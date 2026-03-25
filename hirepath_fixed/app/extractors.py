from __future__ import annotations

import io
import re
from pathlib import Path

from docx import Document
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

from app.models import ResumeExtractionResult, ResumeSectionMap

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


SECTION_PATTERNS = {
    "education": ["education", "academic background"],
    "experience": ["experience", "work experience", "professional experience", "employment"],
    "projects": ["projects", "academic projects", "selected projects"],
    "skills": ["skills", "technical skills", "toolbox"],
    "leadership": ["leadership", "activities", "extracurriculars"],
    "certifications": ["certifications", "certificates"],
}


async def extract_resume_from_upload(file: UploadFile) -> ResumeExtractionResult:
    file_name = file.filename or "resume"
    extension = Path(file_name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF, DOCX, or TXT file.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(data) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File is too large. Please upload a file smaller than 5MB.")

    try:
        if extension == ".pdf":
            raw_text = _extract_pdf_text(data)
        elif extension == ".docx":
            raw_text = _extract_docx_text(data)
        else:
            raw_text = data.decode("utf-8", errors="ignore")
    except Exception as exc:  # pragma: no cover - defensive parsing
        raise HTTPException(status_code=400, detail=f"Could not parse the uploaded file: {exc}") from exc

    normalized = normalize_text(raw_text)
    if len(normalized) < 50:
        raise HTTPException(status_code=400, detail="We could not extract enough text from the file. Try another resume file.")

    sections = split_resume_sections(normalized)
    return ResumeExtractionResult(
        file_name=file_name,
        word_count=len(normalized.split()),
        resume_text=normalized,
        sections=sections,
    )



def _extract_pdf_text(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)



def _extract_docx_text(data: bytes) -> str:
    document = Document(io.BytesIO(data))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs)



def normalize_text(text: str) -> str:
    text = text.replace("\r", "\n")
    text = re.sub(r"\u2022", "-", text)
    text = re.sub(r"\t+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ ]{2,}", " ", text)
    return text.strip()



def split_resume_sections(text: str) -> ResumeSectionMap:
    lower = text.lower()
    sections: dict[str, str] = {key: "" for key in SECTION_PATTERNS}

    heading_hits: list[tuple[int, str, str]] = []
    for key, aliases in SECTION_PATTERNS.items():
        for alias in aliases:
            match = re.search(rf"(^|\n)\s*{re.escape(alias)}\s*(\n|:)", lower)
            if match:
                heading_hits.append((match.start(), key, alias))
                break

    heading_hits.sort(key=lambda item: item[0])

    if heading_hits:
        for index, (start, key, _alias) in enumerate(heading_hits):
            end = heading_hits[index + 1][0] if index + 1 < len(heading_hits) else len(text)
            sections[key] = text[start:end].strip()
    else:
        sections["raw_excerpt"] = text[:2000]
        return ResumeSectionMap(**sections)

    sections["raw_excerpt"] = text[:2000]
    return ResumeSectionMap(**sections)



def extract_bullet_like_lines(text: str, limit: int = 6) -> list[str]:
    lines = [line.strip() for line in text.splitlines()]
    bullet_lines: list[str] = []
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        if cleaned.startswith(("-", "•", "*")):
            bullet_lines.append(cleaned.lstrip("-•* ").strip())
        elif re.match(r"^[A-Z][a-z]+ed\b", cleaned):
            bullet_lines.append(cleaned)
        if len(bullet_lines) >= limit:
            break
    return bullet_lines
