from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


StrengthLabel = Literal["strong", "partial", "missing"]
FitLabel = Literal["strong", "moderate", "weak"]


class SkillRequirement(BaseModel):
    skill: str
    importance: int = Field(ge=1, le=10)
    keywords: list[str]
    signal_type: str = "Core skill"


class RoleRubric(BaseModel):
    slug: str
    title: str
    summary: str
    onet_code: str | None = None
    onet_title: str | None = None
    job_zone: int | None = None
    job_zone_meaning: str | None = None
    job_zone_education_note: str | None = None
    top_education_distribution: str | None = None
    required_skills: list[SkillRequirement]
    preferred_skills: list[str]
    interview_competencies: list[str]
    mock_questions: list[str]
    top_knowledge: list[str] = []
    top_work_activities: list[str] = []
    top_tasks: list[str] = []
    top_tech: list[str] = []
    resume_keywords: list[str] = []
    likely_interview_topics: list[str] = []
    alternate_titles: list[str] = []
    source_urls: dict[str, str] = {}


class ResumeSectionMap(BaseModel):
    education: str = ""
    experience: str = ""
    projects: str = ""
    skills: str = ""
    leadership: str = ""
    certifications: str = ""
    raw_excerpt: str = ""


class ResumeExtractionResult(BaseModel):
    file_name: str
    word_count: int
    resume_text: str
    sections: ResumeSectionMap


class SkillMatch(BaseModel):
    skill: str
    importance: int
    score: float = Field(ge=0, le=1)
    strength: StrengthLabel
    keywords_found: list[str]
    evidence: str


class SkillGap(BaseModel):
    skill: str
    importance: int
    reason: str
    how_to_improve: str


class ResumeImprovement(BaseModel):
    area: Literal["summary", "experience", "projects", "skills", "formatting", "education"]
    issue: str
    suggestion: str


class RewrittenBullet(BaseModel):
    original: str
    improved: str


class GapAnalysisResult(BaseModel):
    fit_score: int = Field(ge=0, le=100)
    fit_label: FitLabel
    summary: str
    matched_skills: list[SkillMatch]
    missing_skills: list[SkillGap]
    resume_improvements: list[ResumeImprovement]
    rewritten_bullets: list[RewrittenBullet]
    strengths_to_leverage: list[str]
    mock_interview_question: str
    next_steps: list[str]
    demo_mode: bool = False


class AnalyzeResumeRequest(BaseModel):
    role_slug: str
    resume_text: str


class InterviewFeedbackRequest(BaseModel):
    role_slug: str
    question: str
    answer_text: str
    analysis: GapAnalysisResult


class FeedbackCategoryScores(BaseModel):
    relevance: int = Field(ge=1, le=10)
    structure: int = Field(ge=1, le=10)
    evidence: int = Field(ge=1, le=10)
    clarity: int = Field(ge=1, le=10)


class InterviewFeedbackResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    strengths: list[str]
    weaknesses: list[str]
    feedback_by_category: FeedbackCategoryScores
    improved_answer_tips: list[str]
    next_steps: list[str]
    sample_better_answer: str
    demo_mode: bool = False


class DeterministicAnalysis(BaseModel):
    role_slug: str
    role_title: str
    fit_score: int
    fit_label: FitLabel
    matched_skills: list[SkillMatch]
    missing_skills: list[SkillGap]
    improvements: list[ResumeImprovement]
    rewritten_bullets: list[RewrittenBullet]
    strengths_to_leverage: list[str]
    suggested_question: str
    next_steps: list[str]


class CandidatePreferences(BaseModel):
    target_role: str
    employment_type: Literal["internship", "full_time"] = "internship"
    location: str = "Any"
    remote_preference: Literal["remote", "hybrid", "onsite", "any"] = "any"
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    visa_required: bool | None = None


class RecruiterContact(BaseModel):
    name: str
    title: str
    team: str
    linkedin_url: HttpUrl
    email: str | None = None
    note: str | None = None


class JobOpportunity(BaseModel):
    source: str
    title: str
    company: str
    location: str
    salary_text: str
    apply_url: HttpUrl
    recruiter_search_url: HttpUrl
    recruiter_action: str
    recruiter_contacts: list[RecruiterContact] = []
    company_blurb: str | None = None
    match_score: int = Field(ge=0, le=100)
    why_match: list[str]
    missing_skills: list[str]
    next_action: str


class OpportunityMatchRequest(BaseModel):
    role_slug: str
    analysis: GapAnalysisResult
    feedback: InterviewFeedbackResult
    preferences: CandidatePreferences


class OpportunityMatchResponse(BaseModel):
    preferences: CandidatePreferences
    jobs: list[JobOpportunity]
    summary: str
