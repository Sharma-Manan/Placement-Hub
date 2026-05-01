import json
import io
import logging
import urllib.request
from typing import Dict, Any
from PyPDF2 import PdfReader
from groq import Groq
from app.core.config import GROQ_API_KEY

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 🔥 IMPORTANT

EXTRACTION_PROMPT = """
Extract structured resume data in JSON.

Fields:
skills (list),
projects (list),
experience (list),
certifications (list),
education (list),
summary (string)

Return ONLY JSON.
Resume:
"""

def extract_text_from_pdf_url(pdf_url: str) -> str:
    """Download PDF from URL and extract text."""
    logger.info(f"[STEP 1] Fetching PDF from URL: {pdf_url}")

    try:
        req = urllib.request.Request(
            pdf_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        with urllib.request.urlopen(req) as response:
            file_bytes = response.read()

        logger.info(f"[STEP 2] PDF downloaded, size: {len(file_bytes)} bytes")

        reader = PdfReader(io.BytesIO(file_bytes))

        if not reader.pages:
            raise ValueError("PDF has no pages")

        logger.info(f"[STEP 3] Total pages in PDF: {len(reader.pages)}")

        text = ""

        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()

                if page_text:
                    logger.debug(f"[PAGE {page_num}] Extracted {len(page_text)} chars")
                    text += page_text + "\n"
                else:
                    logger.warning(f"[PAGE {page_num}] No text extracted")

            except Exception as e:
                logger.warning(f"[PAGE {page_num}] Error: {str(e)}")
                continue

        final_text = text.strip()

        logger.info(f"[STEP 4] Total extracted text length: {len(final_text)}")

        # Preview first 300 chars
        logger.debug(f"[TEXT PREVIEW]: {final_text[:300]}")

        return final_text

    except Exception as e:
        logger.error(f"[ERROR] Failed to fetch/extract PDF: {str(e)}")
        raise ValueError(f"Failed to extract text from resume PDF: {str(e)}")


def parse_resume_from_url(resume_url: str) -> Dict[str, Any]:
    """Fetch PDF, extract text, and send to Groq LLM to get structured JSON."""

    logger.info(f"[START] Resume parsing started")

    if not resume_url:
        logger.error("[ERROR] No resume URL provided")
        return {"error": "No resume URL provided"}

    try:
        raw_text = extract_text_from_pdf_url(resume_url)
    except Exception as e:
        logger.error(f"[ERROR] Raw text extraction failed: {e}")
        return {"error": str(e)}

    if not raw_text or len(raw_text.strip()) < 50:
        logger.error(f"[ERROR] Extracted text too short: length={len(raw_text)}")
        return {"error": "Resume text is empty or too short"}

    logger.info(f"[STEP 5] Sending text to Groq (length={len(raw_text)})")

    try:
        client = Groq(api_key=GROQ_API_KEY)

        if not GROQ_API_KEY:
            logger.error("[ERROR] GROQ_API_KEY is missing!")

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise JSON-only resume parser. You must output valid JSON.",
                },
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT + raw_text[:12000],  # 🔥 prevent overflow
                },
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )

        response_text = chat_completion.choices[0].message.content.strip()

        logger.info(f"[STEP 6] Groq response received")
        logger.debug(f"[GROQ RAW]: {response_text[:500]}")

        try:
            parsed = json.loads(response_text)
            logger.info("[STEP 7] JSON parsed successfully")
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] JSON parsing failed: {str(e)}")
            logger.error(f"[BAD RESPONSE]: {response_text[:500]}")
            return {"error": "AI returned invalid JSON"}

        result = {
            "skills": parsed.get("skills") or [],
            "education": parsed.get("education") or [],
            "projects": parsed.get("projects") or [],
            "experience": parsed.get("experience") or [],
            "certifications": parsed.get("certifications") or [],
            "summary": parsed.get("summary") or None,
        }

        logger.info(f"[SUCCESS] Extraction completed. Skills: {len(result['skills'])}, Projects: {len(result['projects'])}")

        return result

    except Exception as e:
        logger.error(f"[ERROR] Groq API failed: {str(e)}")
        return {"error": f"Failed to extract resume data: {str(e)}"}