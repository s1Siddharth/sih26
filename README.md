# SkillBridge — ITI Skill Gap Analyzer

A full-stack prototype for analyzing skill gaps between ITI/skill development courses and real job market demands. Built for SIH26.

## 🚀 Features

- **AI-Powered Skill Extraction**: Uses Google Gemini 2.0 Flash to instantly parse unstructured job postings into structured JSON (technical skills, soft skills, tools).
- **Skill Gap Matching**: Rule-based matching engine comparing job market demands against ITI course curricula.
- **Employer Feedback Loop**: Allows industry partners to approve/reject recommended curriculum updates.
- **Interactive Dashboard**: Real-time visualization of high-demand skills, emerging technologies, and coverage gaps.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Pydantic, Google Generative AI (Gemini)
- **Frontend**: React (Vite), Recharts, Axios
- **Styling**: Premium Dark Theme CSS with Glassmorphism (Vanilla CSS)

## 📊 How it Works (Mocked vs Real)

For this prototype, we used representative sample data to ensure a smooth, reliable demonstration:
- **Job Postings (`backend/data/job_postings.txt`)**: 18 realistic job descriptions spanning various trades. *In production, this connects to job portal APIs (NCS, LinkedIn).*
- **Course Catalog (`backend/data/courses.json`)**: 15 ITI trades with their respective skills taught. *In production, this syncs with the AICTE/DGT course database.*
- **Placement Data (`backend/data/placements.json`)**: Dummy placement records to demonstrate placement-rate tracking. *In production, this integrates with state employment exchanges.*

**What is 100% REAL:** The AI extraction engine (Gemini) is fully functional and processes text live during the demo. The matching logic dynamically computes gaps based on the AI output.

## ⚙️ Setup Instructions

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```
**Important**: Open `backend/.env` and paste your actual Gemini API key:
`GEMINI_API_KEY=your_key_here`

### 2. Frontend Setup
```bash
cd frontend
npm install
```

## ▶️ Running the Demo

1. **Start Backend**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```
   (Runs on `http://localhost:8000`)

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   (Runs on `http://localhost:5173`)

## 💡 Pitch Talking Points
- *"We used representative sample data for the prototype to ensure reliability, but the AI extraction engine is fully live."*
- *"For speed, we used rule-based matching. In production, we would add a Vector Database (like ChromaDB) to match skills by semantic meaning (e.g., 'EV battery repair' matching 'Automotive Electrical Systems')."*
