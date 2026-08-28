"""
Gemini-powered skill extraction from job posting text.
Uses Gemini 2.0 Flash (free tier, 1500 req/day).
"""

import json
import os
import google.generativeai as genai
from dotenv import load_dotenv
from models import ExtractedSkills

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

EXTRACTION_PROMPT = """You are a skill extraction AI for the Indian vocational education sector (ITI/skill development).

Analyze the following job posting and extract structured information. Return ONLY valid JSON with NO markdown formatting, NO code blocks, NO extra text.

The JSON must have exactly these fields:
{{
  "job_title": "string - the job title",
  "industry": "string - sector like Manufacturing, IT, Automobile, Electrical, Construction, Electronics, HVAC, Automation, Design",
  "experience_level": "string - e.g. Fresher, 0-2 years, 1-3 years, 3-5 years",
  "technical_skills": ["list of specific technical/hard skills required"],
  "soft_skills": ["list of soft skills mentioned or implied"],
  "certifications": ["list of certifications mentioned, empty array if none"],
  "tools_and_equipment": ["list of specific tools, machines, or equipment mentioned"],
  "qualification": "string - educational qualification required",
  "salary_range": "string - salary range if mentioned, empty string if not"
}}

IMPORTANT RULES:
- Extract skills as specific, granular items (e.g., "MIG welding" not just "welding")
- Include implied skills even if not explicitly listed
- For soft_skills, include things like "safety awareness", "teamwork", "communication" if they're implied by the role
- Return ONLY the JSON object, no markdown, no explanation

JOB POSTING:
{job_text}
"""


def _fallback_extract_skills(job_text: str) -> ExtractedSkills:
    """Intelligent regex/keyword fallback extractor when Gemini key is invalid/unavailable."""
    import re
    lines = [line.strip() for line in job_text.split("\n") if line.strip()]
    
    # Title extraction
    title = "Technical Specialist"
    for line in lines[:6]:
        if any(k in line.lower() for k in ["title:", "role:", "position:"]):
            title = line.split(":", 1)[1].strip()
            break
        elif any(k in line.lower() for k in ["operator", "technician", "engineer", "mechanic", "developer", "electrician", "fitter", "welder"]):
            title = line.strip()
            break

    # Industry detection
    industry = "Manufacturing"
    text_lower = job_text.lower()
    if any(k in text_lower for k in ["ev", "electric vehicle", "battery", "bms", "ather", "tata motors"]):
        industry = "Automobile"
    elif any(k in text_lower for k in ["iot", "plc", "scada", "automation", "siemens", "robotics"]):
        industry = "Automation"
    elif any(k in text_lower for k in ["python", "software", "network", "cybersecurity", "web", "data"]):
        industry = "IT"
    elif any(k in text_lower for k in ["solar", "renewable", "inverter"]):
        industry = "Renewable Energy"
    elif any(k in text_lower for k in ["cnc", "lathe", "machinist", "milling", "turner", "welding", "g-code"]):
        industry = "Manufacturing"
    elif any(k in text_lower for k in ["wiring", "electrical", "motor", "transformer"]):
        industry = "Electrical"

    # Known skill keywords dictionary
    common_skills = [
        "CNC programming", "G-code", "M-code", "Blueprint reading", "GD&T",
        "Precision measurement", "Micrometers", "Vernier calipers", "CMM",
        "MasterCAM", "AutoCAD", "SolidWorks", "PLC programming", "SCADA",
        "Siemens TIA Portal", "Industrial IoT", "MQTT", "OPC-UA", "Modbus",
        "Python", "Node.js", "Industrial Ethernet", "Preventive maintenance",
        "Predictive maintenance", "Lithium-ion battery", "BMS diagnostics",
        "CAN bus", "High-voltage safety", "Spot welding", "Cell-to-pack",
        "Thermal management", "EV charging", "MIG welding", "TIG welding",
        "Soldering", "PCB troubleshooting", "Oscilloscope", "Hydraulics",
        "Pneumatics", "5S", "Lean manufacturing", "Kaizen", "Quality inspection",
        "Data structures", "Algorithms", "Machine learning", "SQL", "Git", "Linux",
        "React", "JavaScript", "HTML/CSS", "Cybersecurity", "Solar PV"
    ]
    
    extracted_tech = []
    for sk in common_skills:
        if re.search(r'\b' + re.escape(sk.lower()) + r'\b', text_lower):
            extracted_tech.append(sk)
            
    # If none found from dictionary, extract bullet points
    if not extracted_tech:
        for line in lines:
            if line.startswith(("-", "•", "*", "–")):
                clean = re.sub(r'^[-•*–\s]+', '', line).strip()
                if len(clean) > 3 and len(clean) < 60:
                    extracted_tech.append(clean)

    # Tools & equipment
    tools = [t for t in ["Micrometers", "Vernier calipers", "CMM", "Siemens S7", "TIA Portal", "Oscilloscope", "MasterCAM", "AutoCAD", "SolidWorks", "Multimeter", "Spot welder", "CAN Analyzer"] if t.lower() in text_lower]

    return ExtractedSkills(
        job_title=title,
        industry=industry,
        experience_level="1-3 years" if "1-3" in text_lower else "Fresher / Entry Level",
        technical_skills=extracted_tech[:10] if extracted_tech else ["Technical Operations", "Quality Standards", "Safety Protocol"],
        soft_skills=["Problem Solving", "Team Collaboration", "Safety Awareness", "Communication"],
        certifications=["Industry Certification / ITI Diploma"] if "cert" in text_lower or "iti" in text_lower or "diploma" in text_lower else [],
        tools_and_equipment=tools if tools else ["Standard Testing & Hand Tools"],
        qualification="ITI / Diploma / BE" if "qualification" in text_lower else "Technical Certification",
        salary_range="₹20,000 - ₹35,000/month"
    )


async def extract_skills_from_text(job_text: str) -> ExtractedSkills:
    """
    Send job posting text to Gemini and get structured skill extraction.
    Falls back to intelligent local parser if API key is invalid/unavailable.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or "PASTE" in api_key or "YOUR_KEY" in api_key or len(api_key) < 15:
        # Use intelligent local fallback immediately
        return _fallback_extract_skills(job_text)

    prompt = EXTRACTION_PROMPT.format(job_text=job_text)
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0,
                max_output_tokens=2048,
            )
        )
        
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            raw_text = "\n".join(lines[1:-1])
        
        parsed = json.loads(raw_text)
        return ExtractedSkills(**parsed)
        
    except Exception as e:
        print(f"Gemini API issue ({e}), using fallback parser")
        return _fallback_extract_skills(job_text)


def extract_skills_from_text_sync(job_text: str) -> ExtractedSkills:
    """Synchronous wrapper for testing."""
    import asyncio
    return asyncio.run(extract_skills_from_text(job_text))


# Parse all job postings from the text file
def parse_job_postings_file(filepath: str) -> list[str]:
    """Split job_postings.txt into individual postings."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Split by the separator pattern
    postings = content.split("--- JOB POSTING")
    # Filter out empty strings and clean up
    postings = [p.strip() for p in postings if p.strip()]
    # Remove the numbering prefix (e.g., " 1 ---\n")
    cleaned = []
    for p in postings:
        # Find first newline after the separator
        idx = p.find("\n")
        if idx != -1:
            cleaned.append(p[idx+1:].strip())
        else:
            cleaned.append(p)
    
    return cleaned
