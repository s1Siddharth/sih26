# SkillBridge — ITI Skill Gap Analyzer

A full-stack prototype for analyzing skill gaps between ITI/skill development courses and real job-market demands. Built for SIH26.

## 🚀 Features

- **AI-Powered Skill Extraction** — Uses Google Gemini to extract technical skills, soft skills, tools, and technologies from unstructured job postings.
- **Skill Gap Matching** — Compares market-demanded skills with skills taught in ITI courses.
- **Course–Market Alignment** — Identifies suitable market roles for each course and calculates skill coverage.
- **Resume Alignment** — Upload a resume in PDF or DOCX format to extract skills, calculate alignment, identify skill gaps, and generate recommendations.
- **Multi-Sector Market Data** — Uses representative job-market data across multiple sectors instead of relying on a single industry.
- **Interactive Dashboard** — Visualizes demand, skill coverage, emerging skills, and course-market gaps.
- **Employer Feedback** — Provides a foundation for industry feedback on recommended curriculum improvements.

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- Pydantic
- Google Gemini
- Rule-based skill matching

### Frontend
- React
- Vite
- Axios
- Recharts
- Vanilla CSS

## 🧠 How It Works

```text
                    SkillBridge
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
   Course Data      Market Data       Resume
        │               │                │
        │               ▼                ▼
        │         Skill Extraction   Resume Parser
        │               │                │
        └───────────────┴────────────────┘
                        │
                        ▼
                 Skill Matching
                        │
                        ▼
                  Gap Analysis
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      Match Score    Skill Gaps   Recommendations
📊 Prototype Data

The current prototype uses representative datasets stored under:

backend/data/

The data covers multiple sectors and includes:

ITI/skill-development courses
Skills and competencies
Job-market roles
Job postings
Market-demand signals
Placement information
Recommendations
District-level planning data

These datasets are intended for demonstration and validation of the prototype.

Production Data Sources

In a production deployment, the platform can integrate with authoritative sources such as:

Government skill-development databases
National Career Service (NCS)
DGT/ITI curriculum data
State employment data
Employer/job-posting APIs
Industry and employer feedback
🤖 AI Component

The prototype uses Gemini for structured extraction from unstructured job-market text.

The AI extraction pipeline converts text such as:

Looking for an EV Technician with experience
in battery diagnostics, electrical systems,
CAN bus and EV maintenance.

into structured skills such as:

Technical Skills:
- Battery diagnostics
- Electrical systems
- EV maintenance

Tools / Technologies:
- CAN bus

The extracted skills are then passed to the matching engine for gap analysis.

📄 Resume Analysis

Users can upload a resume in:

PDF
DOCX

The system extracts relevant resume information and compares the candidate's skills against market requirements.

The result includes:

Extracted skills
Market alignment score
Matched skills
Missing skills
Skill-gap recommendations
Suggested areas for upskilling
🔍 Skill Gap Analysis

The matching engine compares:

Course Skills
      +
Market Role Requirements
      ↓
Skill Matching
      ↓
Coverage / Alignment
      ↓
Skill Gaps
      ↓
Recommendation

For example:

Course: Fitter

Course Skills:
- Precision measurement
- Drilling
- Grinding
- Engineering drawing

Target Role:
CNC Machine Operator

Required Skills:
- CNC operation
- G-code
- CAD/CAM
- Precision measurement

Matched:
✓ Precision measurement

Skill Gaps:
• CNC operation
• G-code
• CAD/CAM
⚙️ Local Setup
Requirements
Python 3.11+
Node.js
npm
uv (recommended for Python environment management)
1. Backend
cd backend
uv sync

If the project is being run from an existing virtual environment:

uv run uvicorn main:app --reload

The API runs at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
2. Environment Variables

Create:

backend/.env

Add your API key:

GEMINI_API_KEY=your_key_here

Never commit .env to GitHub.

3. Frontend

Open a second terminal:

cd frontend
npm install
npm run dev

The frontend runs at:

http://localhost:5173
▶️ Running the Full Stack
Terminal 1 — Backend
cd backend
uv run uvicorn main:app --reload
Terminal 2 — Frontend
cd frontend
npm run dev

Then open:

http://localhost:5173
📁 Project Structure
sih26/
│
├── backend/
│   ├── data/
│   │   ├── courses.json
│   │   ├── demand_signals.json
│   │   ├── district_plans.json
│   │   ├── feedback.json
│   │   ├── job_postings.txt
│   │   ├── market_data.json
│   │   ├── placements.json
│   │   ├── recommendations.json
│   │   ├── roles.json
│   │   ├── skills_catalog.json
│   │   └── student_programs.json
│   │
│   ├── analysis.py
│   ├── catalog_models.py
│   ├── course_gap.py
│   ├── data_store.py
│   ├── main.py
│   ├── matching.py
│   ├── models.py
│   ├── resume_market.py
│   ├── resume_parser.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CourseGapAnalyzer.jsx
│   │   │   ├── MarketDemandRadar.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── ResumeAlignment.jsx
│   │   │
│   │   ├── api/
│   │   │   └── client.js
│   │   │
│   │   ├── App.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .gitignore
🔐 Security

API keys and local environment files must not be committed.

The following files/directories are intentionally ignored:

.env
backend/.env
.venv/
backend/.venv/
node_modules/
dist/
🎯 SIH26 Prototype Scope

The prototype focuses on one core problem:

Identify the gap between skills being taught and skills demanded by the job market, then provide actionable recommendations.

The system demonstrates this through:

Market-demand analysis
Course-to-role matching
Skill-gap analysis
Resume-to-market alignment
Recommendations for upskilling
🚀 Future Enhancements

Possible production extensions include:

Live job-market APIs
Government curriculum integrations
Vector-based semantic skill matching
Larger employer feedback networks
Continuous market-demand monitoring
Regional skill-demand forecasting
Personalized learning-path recommendations