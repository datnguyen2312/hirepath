from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.ai_client import generate_gap_analysis_with_ai, generate_interview_feedback_with_ai
from app.extractors import extract_resume_from_upload
from app.models import (
    AnalyzeResumeRequest,
    GapAnalysisResult,
    InterviewFeedbackRequest,
    InterviewFeedbackResult,
    OpportunityMatchRequest,
    OpportunityMatchResponse,
    ResumeExtractionResult,
)
from app.opportunity_matcher import build_opportunity_matches
from app.role_rubrics import DEMO_RESUMES, ROLE_RUBRICS, get_role
from app.scoring import analyze_resume_deterministically

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(
    title="HirePath Student Career Copilot",
    version="0.2.0",
    description="HirePath web experience for resume analysis, skills gap checking, mock interview coaching, and action planning for students targeting entry-level roles.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def template_context(request: Request, page_id: str, title: str) -> dict:
    return {
        "request": request,
        "page_id": page_id,
        "title": title,
        "roles": [role.model_dump() for role in ROLE_RUBRICS],
        "demo_resumes": [{"key": key, "label": value["label"]} for key, value in DEMO_RESUMES.items()],
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "home.html", template_context(request, "home", "HirePath | AI Career Copilot"))


@app.get("/resume-analysis", response_class=HTMLResponse)
async def resume_analysis_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "resume_analysis.html", template_context(request, "resume", "HirePath | Resume Analysis"))


@app.get("/skills-gap-check", response_class=HTMLResponse)
async def skills_gap_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "skills_gap_check.html", template_context(request, "skills", "HirePath | Skills Gap Check"))


@app.get("/mock-interview", response_class=HTMLResponse)
async def mock_interview_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "mock_interview.html", template_context(request, "interview", "HirePath | Mock Interview"))


@app.get("/next-step-plan", response_class=HTMLResponse)
async def next_step_plan_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "next_step_plan.html", template_context(request, "next", "HirePath | Action Plan"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/roles")
async def list_roles() -> list[dict[str, str]]:
    return [{"slug": role.slug, "title": role.title, "summary": role.summary} for role in ROLE_RUBRICS]


@app.get("/api/demo-resumes")
async def list_demo_resumes() -> list[dict[str, str]]:
    return [{"key": key, "label": value["label"]} for key, value in DEMO_RESUMES.items()]


@app.get("/api/demo-resume/{resume_key}")
async def get_demo_resume(resume_key: str) -> dict[str, str | int]:
    if resume_key not in DEMO_RESUMES:
        raise HTTPException(status_code=404, detail="Demo resume not found.")
    payload = DEMO_RESUMES[resume_key]
    return {"label": payload["label"], "resume_text": payload["text"], "word_count": len(payload["text"].split())}


@app.post("/api/extract-resume", response_model=ResumeExtractionResult)
async def extract_resume(file: UploadFile = File(...)) -> ResumeExtractionResult:
    return await extract_resume_from_upload(file)


@app.post("/api/analyze", response_model=GapAnalysisResult)
async def analyze_resume(payload: AnalyzeResumeRequest) -> GapAnalysisResult:
    if len(payload.resume_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="Resume text is too short to analyze.")
    try:
        get_role(payload.role_slug)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Target role was not found.") from exc
    deterministic = analyze_resume_deterministically(payload.role_slug, payload.resume_text)
    return generate_gap_analysis_with_ai(payload.role_slug, payload.resume_text, deterministic)


@app.post("/api/interview-feedback", response_model=InterviewFeedbackResult)
async def score_interview_answer(payload: InterviewFeedbackRequest) -> InterviewFeedbackResult:
    if len(payload.answer_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Please write a longer interview answer before scoring it.")
    return generate_interview_feedback_with_ai(
        role_slug=payload.role_slug,
        question=payload.question,
        answer_text=payload.answer_text,
        deterministic_analysis=payload.analysis,
    )


@app.post("/api/opportunity-match", response_model=OpportunityMatchResponse)
async def opportunity_match(payload: OpportunityMatchRequest) -> OpportunityMatchResponse:
    try:
        get_role(payload.role_slug)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Target role was not found.") from exc
    return build_opportunity_matches(
        role_slug=payload.role_slug,
        analysis=payload.analysis,
        feedback=payload.feedback,
        preferences=payload.preferences,
    )
