# 🌊 LocalFlow — Deployment Guide

## Overview
LocalFlow has 3 parts that need deploying:

| Part | Tech | Location | 
|------|------|----------|
| **Marketing Website** | Static HTML + CSS | `/home/team/shared/localflow/website/` |
| **Dashboard App** | React + Vite | `/home/team/shared/localflow/frontend/` |
| **Backend API** | Python FastAPI | `/home/team/shared/localflow/backend/` |

---

## 1️⃣ Marketing Website — Deploy to Netlify (Free)

Easiest option — drag and drop.

### Steps:
1. Go to [netlify.com](https://netlify.com) and sign up
2. Drag the **`/home/team/shared/localflow/website/`** folder onto the deploy area
3. Netlify gives you a URL like `https://localflow.netlify.app`
4. (Optional) Add your own domain in Settings → Domain Management

### Files to upload:
```
website/
├── index.html
└── style.css
```

**That's it — 2 files, zero build step.**

---

## 2️⃣ Dashboard App — Deploy to Vercel (Free)

### Steps:
1. Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. Install the **Vercel CLI** or connect your GitHub repo
3. Deploy the `/home/team/shared/localflow/frontend/` folder

### Or via CLI:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from the frontend directory
cd /home/team/shared/localflow/frontend
vercel --prod
```

### Environment Variables (in Vercel dashboard):
| Variable | Value |
|----------|-------|
| `VITE_API_URL` | `https://your-backend-url.up.railway.app` |

### Important — update API URL:
In `src/api.js`, change:
```js
const API_BASE = 'http://localhost:8200';
```
to your deployed backend URL:
```js
const API_BASE = 'https://your-app.up.railway.app';
```

---

## 3️⃣ Backend API — Deploy to Railway (Free tier)

### Steps:
1. Go to [railway.com](https://railway.com) and sign up with GitHub
2. Create a **New Project** → **Deploy from GitHub**
3. Push the `/home/team/shared/localflow/backend/` folder to a GitHub repo
4. Railway auto-detects Python + FastAPI

### Railway Configuration:
**Start Command:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
| Variable | Value |
|----------|-------|
| `PORT` | Railway sets this automatically |
| `PYTHON_VERSION` | `3.12` |

### Requirements:
A `requirements.txt` is already included with:
```
fastapi
uvicorn
pydantic
```

### Database Note:
The app uses **team-db** (Turso) which runs in the sandbox. For production, you'd swap to a real database:

**Option A: SQLite (simplest)**
Replace `database.py` to use standard `sqlite3` module instead of `team-db` CLI.

**Option B: PostgreSQL (Railway provides this)**
Railway offers free PostgreSQL. Update `database.py` to use `psycopg2` or SQLAlchemy.

**Option C: Keep Turso** (has a free tier)
Sign up at [turso.tech](https://turso.tech) and create a database, then update the team-db connection.

---

## Quick Deploy Checklist

- [ ] Marketing site uploaded to Netlify
- [ ] Dashboard deployed to Vercel (with API URL updated)
- [ ] Backend deployed to Railway
- [ ] CORS updated in `main.py` to allow your domain
- [ ] Custom domain connected (if desired)
- [ ] Database sorted (SQLite / PostgreSQL / Turso)

---

## Updating CORS (important!)
In `/home/team/shared/localflow/backend/main.py`, change:
```python
allow_origins=["*"]
```
to your actual domains:
```python
allow_origins=[
    "https://localflow.netlify.app",
    "https://your-dashboard.vercel.app",
    "https://your-custom-domain.com.au",
]
```

---

## 💰 Cost Summary
| Service | Cost |
|---------|------|
| Netlify (marketing site) | **Free** |
| Vercel (dashboard) | **Free** |
| Railway (backend API) | **Free** (up to $5/mo after trial) |
| Domain (e.g. .com.au) | ~$15/year |
| **Total** | **$0 to start** |

---

## Files at a Glance
```bash
/home/team/shared/localflow/
├── website/          ← Marketing site (upload to Netlify)
│   ├── index.html
│   └── style.css
├── frontend/         ← Dashboard app (deploy to Vercel)
│   └── src/
│       ├── App.jsx
│       └── components/  (7 panels)
└── backend/          ← API server (deploy to Railway)
    ├── main.py
    ├── routes/
    └── services/
```