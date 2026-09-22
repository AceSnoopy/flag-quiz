# Flag Quiz — Implementation Plan

**Stack:** Python Flask + SQLite, server-rendered HTML with light JavaScript. Runs locally at `http://localhost:5050`. Flask is installed into a project-local virtualenv (`.venv`).

## 1. Project structure
```
Flag Website/
├── app.py              # Flask app: routes for auth, quiz, store, collection
├── db.py               # SQLite setup + helpers
├── countries.py        # All ~250 countries/territories (ISO code → name, region)
├── requirements.txt    # flask
├── templates/          # base, login, register, home, quiz, results, store, collection
└── static/             # style.css, quiz.js
```

## 2. Data model (SQLite)
- **users** — id, username (unique), password_hash, coins, created_at
- **owned_flags** — user_id, country_code, purchased_at
- **quiz_results** — user_id, score, stars, played_at (for history / high score)

## 3. Login
- Register / Login forms with **username + password**; passwords hashed with Werkzeug.
- Flask sessions keep users logged in; quiz, store and collection require login.
- New accounts start with **100 coins**.

## 4. Quiz (10 rounds)
- Starting a game: the **server** picks 10 random, non-repeating countries, each with 3 random wrong answers; the 4 options are shuffled.
- Correct answers stay server-side so players can't cheat by inspecting the page.
- Each round: large flag + 4 buttons. On click, correct answer turns green (wrong pick red), then "Next". Progress bar ("Round 3 / 10").
- Flag images from **flagcdn.com** (free CDN by ISO code) — consistent on every device.

## 5. Results & star rating
| Correct | Stars |
|---|---|
| 0–1 | 0★ |
| 2–3 | 1★ |
| 4–5 | 2★ |
| 6–7 | 3★ |
| 8–9 | 4★ |
| 10 | 5★ |

- Results screen: score, animated stars, per-round recap (flag, your answer, correct answer), coins earned.
- **Coins:** 10 per correct answer + 50 bonus for a perfect 10/10.

## 6. Store
- Grid of every country's flag with search box and region filter.
- Flat **50 coins per flag**. Buy disabled if already owned or unaffordable.
- Purchase validated server-side (balance + ownership).
- **My Collection** page shows owned flags and progress ("12 / 250 collected").

## 7. Navigation & design
- Top bar: Play · Store · My Collection · coin balance · Logout.
- Clean, responsive layout that works on phone and desktop.

## 8. Build order
1. Environment, database, auth.
2. Quiz flow + results with star rating.
3. Coins, store and collection.
4. Styling, then end-to-end test in the browser.

## Defaults (easy to change)
- 100 starting coins, 10 coins/correct, 50 perfect bonus, 50 coins/flag.
- Wrong answers are fully random (could switch to same-region for harder mode).
- Territories (e.g. Greenland, Puerto Rico) included alongside sovereign nations.

## Running
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```
Then open http://localhost:5050.

## Hosting (added)
- Code on GitHub: `AceSnoopy/flag-quiz` (public).
- Hosted on **Render** (GitHub Pages can't run a Python server). The `render.yaml` blueprint creates a free web service (gunicorn) and a free Postgres database.
- `db.py` uses Postgres when `DATABASE_URL` is set and SQLite otherwise, so local development is unchanged.
