import json
import io
from PyPDF2 import PdfReader
from groq import Groq
from app.core.config import GROQ_API_KEY


EXTRACTION_PROMPT = """You are a resume parser. Extract structured data from the following resume text.

Return ONLY valid JSON with this exact structure (no markdown, no explanation, no extra text):
{
  "skills": ["skill1", "skill2", ...],
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
- Return ONLY the JSON object, nothing else.

Resume text:
"""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text content from a PDF file."""
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def extract_resume_data(raw_text: str) -> dict:
    """Send resume text to Groq LLM and get structured JSON back."""
    client = Groq(api_key=GROQ_API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a precise resume parser. You only return valid JSON. No markdown, no explanation.",
            },
            {
                "role": "user",
                "content": EXTRACTION_PROMPT + raw_text,
            },
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=4096,
    )

    response_text = chat_completion.choices[0].message.content.strip()

    # Clean up response if it has markdown code fences
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()

    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        raise ValueError(f"AI returned invalid JSON. Raw response: {response_text[:500]}")

    # Ensure all expected keys exist
    result = {
        "skills": parsed.get("skills", []),
        "education": parsed.get("education", []),
        "projects": parsed.get("projects", []),
        "experience": parsed.get("experience", []),
        "certifications": parsed.get("certifications", []),
        "summary": parsed.get("summary", None),
    }

    return result
