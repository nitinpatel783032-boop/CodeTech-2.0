# Code Master AI - Backend (Flask / Python, powered by Gemini)

Secure Python backend for the Code Master AI chatbot. Uses Google's
Gemini API (since you have a Gemini key). Supports both plain text
questions and image (screenshot) analysis. Your API key stays on the
server as an environment variable — never in the browser.

## 1. Get a Gemini API key (if you don't already have one saved)

1. Go to https://aistudio.google.com/apikey
2. Sign in with your Google account.
3. Click **Create API key**, copy it.
4. Treat it like a password — never paste it into chat or commit it to
   GitHub directly. Only put it in Render's Environment Variables field.

## 2. Test it locally

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export GEMINI_API_KEY=your-real-gemini-api-key-here
python3 app.py
```

Runs at `http://localhost:5000`. Test it:

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":[{"type":"text","text":"What is a JavaScript closure?"}]}]}'
```

## 3. Deploy for real (Render — easiest free option)

1. Push this `backend` folder as its own GitHub repo (or update your
   existing one — just replace `app.py`, `.env.example`, and this
   README with these new versions).
2. Go to https://render.com, sign in with GitHub.
3. **New +** → **Web Service** → select your repo.
4. Settings:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Under **Environment**, add:
   - Key: `GEMINI_API_KEY`
   - Value: your real Gemini API key
   - (If you had an old `ANTHROPIC_API_KEY` variable here from before,
     you can delete it — it's no longer used.)
6. **Create Web Service** (or, if updating an existing service, Render
   redeploys automatically once you push the new code).
7. Your chatbot endpoint stays the same shape:
   `https://your-app-name.onrender.com/api/chat`

Render's free tier sleeps after inactivity, so the first request after a
while can take 30-50 seconds to wake up — fine for a learning site's
chatbot.

## 4. Frontend — nothing to change

`assets/js/code-master-ai.js` still points at the same backend URL and
sends messages in the same shape it always did. The conversion to
Gemini's format happens entirely inside `app.py`, so you don't need to
touch the frontend at all when switching AI providers.

## What changed in v3

- Switched from Anthropic's Claude API to Google's Gemini API
  (`generateContent` endpoint).
- Added `anthropic_style_to_gemini()` — converts the frontend's message
  format into what Gemini expects, including image blocks.
- Uses `GEMINI_API_KEY` instead of `ANTHROPIC_API_KEY`.
- Uses the `gemini-flash-latest` model alias, so it automatically stays
  on Google's newest fast Flash model without needing code changes.
