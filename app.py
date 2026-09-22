import json
import os
import random
import secrets
import ssl
import urllib.request
from functools import wraps
from pathlib import Path

import certifi
from flask import (Flask, Response, abort, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from countries import COUNTRIES, QUIZ_CODES, REGIONS, flag_url
from db import close_db, get_db, init_db

ROUNDS = 10
OPTIONS_PER_ROUND = 4
STARTING_COINS = 100
COINS_PER_CORRECT = 10
PERFECT_BONUS = 50
FLAG_PRICE = 50


def _secret_key():
    if os.environ.get("SECRET_KEY"):
        return os.environ["SECRET_KEY"]
    path = Path(__file__).parent / ".secret_key"
    if not path.exists():
        path.write_text(secrets.token_hex(32))
    return path.read_text().strip()


app = Flask(__name__)
app.secret_key = _secret_key()
# Behind HTTPS in production (Render sets RENDER=true).
app.config["SESSION_COOKIE_SECURE"] = bool(os.environ.get("RENDER"))
app.teardown_appcontext(close_db)
init_db()


def stars_for(score):
    """0-1 -> 0, 2-3 -> 1, 4-5 -> 2, 6-7 -> 3, 8-9 -> 4, 10 -> 5."""
    return 5 if score >= ROUNDS else score // 2


# ---------- request helpers ----------

@app.before_request
def load_user():
    g.user = None
    if "user_id" in session:
        g.user = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
        if g.user is None:
            session.clear()


@app.before_request
def check_csrf():
    if request.method == "POST":
        token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
        if not token or token != session.get("csrf_token"):
            abort(400, "Invalid or missing CSRF token")


@app.context_processor
def inject_globals():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return {"csrf_token": session["csrf_token"], "flag_url": flag_url,
            "COUNTRIES": COUNTRIES, "FLAG_PRICE": FLAG_PRICE}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


# ---------- auth ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")
        error = None
        if not (3 <= len(username) <= 20) or not username.replace("_", "").isalnum():
            error = "Username must be 3–20 characters: letters, numbers or underscores."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm:
            error = "Passwords don't match."
        else:
            db = get_db()
            if db.execute("SELECT 1 FROM users WHERE lower(username) = lower(?)", (username,)).fetchone():
                error = "That username is taken."
            else:
                cur = db.execute(
                    "INSERT INTO users (username, password_hash, coins) VALUES (?, ?, ?) RETURNING id",
                    (username, generate_password_hash(password), STARTING_COINS))
                user_id = cur.fetchone()[0]
                db.commit()
                session.clear()
                session["user_id"] = user_id
                flash(f"Welcome, {username}! You start with {STARTING_COINS} coins.", "success")
                return redirect(url_for("home"))
        flash(error, "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE lower(username) = lower(?)", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            nxt = request.args.get("next", "")
            return redirect(nxt if nxt.startswith("/") and not nxt.startswith("//") else url_for("home"))
        flash("Incorrect username or password.", "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- home ----------

@app.route("/")
@login_required
def home():
    db = get_db()
    uid = g.user["id"]
    stats = db.execute(
        "SELECT COUNT(*) AS games, MAX(score) AS best, SUM(stars) AS total_stars "
        "FROM quiz_results WHERE user_id = ?", (uid,)).fetchone()
    recent = db.execute(
        "SELECT * FROM quiz_results WHERE user_id = ? ORDER BY id DESC LIMIT 5", (uid,)).fetchall()
    owned = db.execute(
        "SELECT COUNT(*) FROM owned_flags WHERE user_id = ?", (uid,)).fetchone()[0]
    return render_template("home.html", stats=stats, recent=recent, owned=owned,
                           total=len(COUNTRIES), rounds=ROUNDS)


# ---------- quiz ----------

def _active_quiz():
    return get_db().execute(
        "SELECT * FROM quizzes WHERE user_id = ? AND finished = 0 ORDER BY id DESC LIMIT 1",
        (g.user["id"],)).fetchone()


@app.route("/quiz/start", methods=["POST"])
@login_required
def quiz_start():
    db = get_db()
    # Abandon any unfinished game.
    db.execute("UPDATE quizzes SET finished = 1 WHERE user_id = ? AND finished = 0", (g.user["id"],))
    answers = random.sample(QUIZ_CODES, ROUNDS)
    questions = []
    for answer in answers:
        wrong = random.sample([c for c in QUIZ_CODES if c != answer], OPTIONS_PER_ROUND - 1)
        options = wrong + [answer]
        random.shuffle(options)
        questions.append({"answer": answer, "options": options})
    db.execute("INSERT INTO quizzes (user_id, questions) VALUES (?, ?)",
               (g.user["id"], json.dumps(questions)))
    db.commit()
    return redirect(url_for("quiz"))


@app.route("/quiz")
@login_required
def quiz():
    q = _active_quiz()
    if q is None:
        return redirect(url_for("home"))
    questions = json.loads(q["questions"])
    picks = json.loads(q["picks"])
    rnd = len(picks)
    current = questions[rnd]
    score = sum(p == qq["answer"] for p, qq in zip(picks, questions))
    options = [{"code": c, "name": COUNTRIES[c]["name"]} for c in current["options"]]
    return render_template("quiz.html", round_num=rnd + 1, rounds=ROUNDS, score=score,
                           options=options, quiz_id=q["id"])


_flag_cache = {}
_ssl_ctx = ssl.create_default_context(cafile=certifi.where())


@app.route("/quiz/flag")
@login_required
def quiz_flag():
    """Serve the current round's flag without revealing its country code in the URL."""
    q = _active_quiz()
    if q is None:
        abort(404)
    code = json.loads(q["questions"])[len(json.loads(q["picks"]))]["answer"]
    if code not in _flag_cache:
        with urllib.request.urlopen(flag_url(code, 640), timeout=10, context=_ssl_ctx) as resp:
            _flag_cache[code] = resp.read()
    return Response(_flag_cache[code], mimetype="image/png",
                    headers={"Cache-Control": "no-store"})


@app.route("/quiz/answer", methods=["POST"])
@login_required
def quiz_answer():
    db = get_db()
    q = _active_quiz()
    if q is None:
        return jsonify(error="No active game"), 400
    questions = json.loads(q["questions"])
    picks = json.loads(q["picks"])
    pick = (request.get_json(silent=True) or {}).get("choice")
    current = questions[len(picks)]
    if pick not in current["options"]:
        return jsonify(error="Invalid choice"), 400

    picks.append(pick)
    correct = pick == current["answer"]
    finished = len(picks) == ROUNDS
    db.execute("UPDATE quizzes SET picks = ?, finished = ? WHERE id = ?",
               (json.dumps(picks), int(finished), q["id"]))

    result = {"correct": correct, "answer": current["answer"], "finished": finished}
    if finished:
        score = sum(p == qq["answer"] for p, qq in zip(picks, questions))
        coins = score * COINS_PER_CORRECT + (PERFECT_BONUS if score == ROUNDS else 0)
        db.execute(
            "INSERT INTO quiz_results (quiz_id, user_id, score, stars, coins_earned) VALUES (?, ?, ?, ?, ?)",
            (q["id"], g.user["id"], score, stars_for(score), coins))
        db.execute("UPDATE users SET coins = coins + ? WHERE id = ?", (coins, g.user["id"]))
        result["next"] = url_for("results", quiz_id=q["id"])
    else:
        result["next"] = url_for("quiz")
    db.commit()
    return jsonify(result)


@app.route("/results/<int:quiz_id>")
@login_required
def results(quiz_id):
    db = get_db()
    res = db.execute("SELECT * FROM quiz_results WHERE quiz_id = ? AND user_id = ?",
                     (quiz_id, g.user["id"])).fetchone()
    if res is None:
        abort(404)
    q = db.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,)).fetchone()
    recap = [{"answer": qq["answer"], "pick": p}
             for qq, p in zip(json.loads(q["questions"]), json.loads(q["picks"]))]
    return render_template("results.html", res=res, recap=recap, rounds=ROUNDS)


# ---------- store & collection ----------

def _owned_codes():
    rows = get_db().execute(
        "SELECT country_code FROM owned_flags WHERE user_id = ?", (g.user["id"],)).fetchall()
    return {r["country_code"] for r in rows}


@app.route("/store")
@login_required
def store():
    countries = sorted(COUNTRIES.values(), key=lambda c: c["name"])
    return render_template("store.html", countries=countries, regions=REGIONS, owned=_owned_codes())


@app.route("/store/buy/<code>", methods=["POST"])
@login_required
def buy(code):
    if code not in COUNTRIES:
        abort(404)
    db = get_db()
    name = COUNTRIES[code]["name"]
    if code in _owned_codes():
        flash(f"You already own the flag of {name}.", "error")
    else:
        # Conditional update makes the balance check and deduction atomic.
        cur = db.execute("UPDATE users SET coins = coins - ? WHERE id = ? AND coins >= ?",
                         (FLAG_PRICE, g.user["id"], FLAG_PRICE))
        if cur.rowcount == 0:
            flash(f"Not enough coins — {name} costs {FLAG_PRICE}. Play a quiz to earn more!", "error")
        else:
            db.execute("INSERT INTO owned_flags (user_id, country_code) VALUES (?, ?)",
                       (g.user["id"], code))
            db.commit()
            flash(f"You bought the flag of {name}!", "success")
    return redirect(url_for("store", _anchor=code))


@app.route("/collection")
@login_required
def collection():
    rows = get_db().execute(
        "SELECT country_code, purchased_at FROM owned_flags WHERE user_id = ? ORDER BY purchased_at DESC",
        (g.user["id"],)).fetchall()
    flags = [COUNTRIES[r["country_code"]] for r in rows if r["country_code"] in COUNTRIES]
    return render_template("collection.html", flags=flags, total=len(COUNTRIES))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
