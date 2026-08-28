# SkillBridge — Final MVP Status

SIH 2026 · PS #26134 · Maharashtra-focused prototype

## Core features
1. Market Demand Radar
2. Course–Market Gap Analyzer
3. Resume–Market Alignment (PDF/DOCX)

## Architecture
- React + Vite frontend
- FastAPI backend
- JSON + Pydantic data layer
- Gemini for structured resume extraction only
- Deterministic Python matching/scoring
- One shared canonical skill system

## Security
- API key is backend-only
- `.env` is ignored and not included
- `backend/.env.example` is provided
- Resume files are processed temporarily

## Validation
- Python compile check: PASS
- Course-gap tests: PASS
- Catalog validation: 0 errors
- Catalog validation warnings remain for legacy course-only skills not needed by the market catalog
- Frontend production build could not be executed in this environment because npm dependency installation timed out; run `npm install` locally before `npm run build`.

## Local run

Backend:
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# edit .env and add GEMINI_API_KEY
uvicorn main:app --reload
```

Frontend (new terminal):
```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, normally http://localhost:5173.
