# Flag Quiz

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/AceSnoopy/flag-quiz)

Guess the country from its flag: 10 rounds with 4 choices each, and a 0–5 star rating at the end. Correct answers earn coins, which you can spend in a store that sells every country's flag for your collection.

Built with Flask. It uses SQLite locally and Postgres in production.

## Run locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Open http://localhost:5050.

## Deploy to Render

The repo includes a [`render.yaml`](render.yaml) blueprint that creates a free web service and a free Postgres database.

1. Sign in at [render.com](https://render.com) with GitHub.
2. **New → Blueprint**, then pick this repo and click **Apply**.
3. When the deploy finishes, the site is live at `https://flag-quiz-XXXX.onrender.com`. Every push to `main` redeploys it.

Notes on Render's free tier:
- The web service sleeps after 15 minutes without traffic. The first visit after that takes about 30–60 seconds to wake it.
- The free Postgres database expires after 30 days unless you upgrade it.

## Configuration

| Env var | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string. If unset, a local `flags.db` SQLite file is used. |
| `SECRET_KEY` | Session signing key. If unset, a random key is generated and saved to `.secret_key`. |
