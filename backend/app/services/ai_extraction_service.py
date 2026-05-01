import json
import io
import logging
import urllib.request
from typing import Dict, Any
from PyPDF2 import PdfReader
from groq import Groq
from app.core.config import GROQ_API_KEY

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are an expert resume parser. Extract structured data from the following resume text.

Return ONLY a valid JSON object matching the exact structure below. Do not include any explanations, markdown formatting, or code blocks.

{
  "skills": ["skill1", "skill2"],
  "education": [
    {
      "degree": "B.Tech in Computer Science",
      "institution": "XYZ University",
      "year": "2024",
      "cgpa": "8.5"
    }
  ],
  "projects": [
    {
      "title": "Project Name",
      "description": "Brief description of the project",
      "tech_stack": ["React", "Node.js"]
    }
  ],
  "experience": [
    {
      "company": "Company Name",
      "role": "Software Engineer Intern",
      "duration": "Jun 2023 - Aug 2023",
      "description": "Brief description of work done"
    }
  ],
  "certifications": [
    {
      "name": "AWS Cloud Practitioner",
      "issuer": "Amazon",
      "year": "2023"
    }
  ],
  "summary": "A 2-3 line professional summary of the candidate based on their resume."
}

Rules:
- If a section has no data, return an empty array [] for lists or null for summary.
- Do NOT invent data. Only extract what is explicitly mentioned.
- Ensure the response is a valid JSON object.

Resume text:
"""

def extract_text_from_pdf_url(pdf_url: str) -> str:
    """Download PDF from URL and extract text."""
    try:
        req = urllib.request.Request(pdf_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            file_bytes = response.read()
            
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        
        if not reader.pages:
            raise ValueError("PDF has no pages")
            
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                logger.warning(f"Error extracting page {page_num}: {str(e)}")
                continue
                
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to fetch or extract PDF from URL: {str(e)}")
        raise ValueError(f"Failed to extract text from resume PDF: {str(e)}")

def parse_resume_from_url(resume_url: str) -> Dict[str, Any]:
    """Fetch PDF, extract text, and send to Groq LLM to get structured JSON."""
    if not resume_url:
        return {}
        
    try:
        raw_text = extract_text_from_pdf_url(resume_url)
    except Exception as e:
        logger.error(f"Error getting raw text: {e}")
        return {"error": str(e)}

    if not raw_text or len(raw_text.strip()) < 50:
        return {"error": "Resume text is empty or too short"}

    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        logger.info("Sending resume text to Groq for extraction...")
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise JSON-only resume parser. You must output valid JSON.",
                },
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT + raw_text,
                },
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        logger.debug(f"Groq response: {response_text[:500]}")
        
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            return {"error": "AI returned invalid JSON"}
            
        # Ensure standard keys exist
        result = {
            "skills": parsed.get("skills") or [],
            "education": parsed.get("education") or [],
            "projects": parsed.get("projects") or [],
            "experience": parsed.get("experience") or [],
            "certifications": parsed.get("certifications") or [],
            "summary": parsed.get("summary") or None,
        }
        
        logger.info("Resume extraction successful")
        return result
        
    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
        return {"error": f"Failed to extract resume data: {str(e)}"}