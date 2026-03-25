from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from typing import Any

from app.models import (
    DeterministicAnalysis,
    FeedbackCategoryScores,
    GapAnalysisResult,
    InterviewFeedbackResult,
)
from app.role_rubrics import get_role


try:  # Optional dependency during local demo mode.
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore[assignment]


@lru_cache(maxsize=1)
def get_openai_client() -> Any | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None
    return OpenAI(api_key=api_key)



def generate_gap_analysis_with_ai(role_slug: str, resume_text: str, deterministic: DeterministicAnalysis) -> GapAnalysisResult:
    client = get_openai_client()
    role = get_role(role_slug)

    if client is None:
        return build_demo_gap_analysis(role.title, deterministic)

    prompt = f"""
You are an expert career coach for university students applying to entry-level roles.
Stay grounded in the resume and deterministic analysis provided.
Do not invent missing projects, tools, or achievements.
Use concise, specific language.

Target role rubric:
{role.model_dump_json(indent=2)}

Deterministic analysis:
{deterministic.model_dump_json(indent=2)}

Resume text:
{resume_text[:12000]}
""".strip()

    try:
        response = client.responses.parse(
            model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            input=[
                {
                    "role": "system",
                    "content": "Return structured career-coaching analysis for a student resume. Ground every recommendation in the supplied resume and rubric.",
                },
                {"role": "user", "content": prompt},
            ],
            text_format=GapAnalysisResult,
        )
        parsed = response.output_parsed
        if parsed is None:
            return build_demo_gap_analysis(role.title, deterministic)
        parsed.demo_mode = False
        parsed.fit_score = deterministic.fit_score
        parsed.fit_label = deterministic.fit_label
        return parsed
    except Exception:
        return build_demo_gap_analysis(role.title, deterministic)



def generate_interview_feedback_with_ai(
    role_slug: str,
    question: str,
    answer_text: str,
    deterministic_analysis: GapAnalysisResult,
) -> InterviewFeedbackResult:
    client = get_openai_client()
    role = get_role(role_slug)

    if client is None:
        return build_demo_interview_feedback(question, answer_text)

    prompt = f"""
You are coaching a student for a {role.title} interview.
Evaluate the answer with practical, supportive feedback.
Stay honest and specific.

Role rubric:
{role.model_dump_json(indent=2)}

Existing analysis:
{deterministic_analysis.model_dump_json(indent=2)}

Interview question:
{question}

Student answer:
{answer_text}
""".strip()

    try:
        response = client.responses.parse(
            model=os.getenv("OPENAI_MODEL", "gpt-5.4-mini"),
            input=[
                {
                    "role": "system",
                    "content": "Return structured mock interview feedback. Reward relevance, evidence, structure, and clarity.",
                },
                {"role": "user", "content": prompt},
            ],
            text_format=InterviewFeedbackResult,
        )
        parsed = response.output_parsed
        if parsed is None:
            return build_demo_interview_feedback(question, answer_text)
        parsed.demo_mode = False
        return parsed
    except Exception:
        return build_demo_interview_feedback(question, answer_text)



def build_demo_gap_analysis(role_title: str, deterministic: DeterministicAnalysis) -> GapAnalysisResult:
    summary = build_gap_summary(role_title, deterministic)
    return GapAnalysisResult(
        fit_score=deterministic.fit_score,
        fit_label=deterministic.fit_label,
        summary=summary,
        matched_skills=deterministic.matched_skills,
        missing_skills=deterministic.missing_skills,
        resume_improvements=deterministic.improvements,
        rewritten_bullets=deterministic.rewritten_bullets,
        strengths_to_leverage=deterministic.strengths_to_leverage,
        mock_interview_question=deterministic.suggested_question,
        next_steps=deterministic.next_steps,
        demo_mode=True,
    )



def build_gap_summary(role_title: str, deterministic: DeterministicAnalysis) -> str:
    if deterministic.fit_label == "strong":
        opener = f"Your resume already shows a solid baseline for a {role_title} application."
    elif deterministic.fit_label == "moderate":
        opener = f"Your resume shows partial fit for a {role_title} role, but the story is not complete yet."
    else:
        opener = f"Right now your resume does not strongly signal readiness for a {role_title} role."

    matched = ", ".join(item.skill for item in deterministic.matched_skills[:3]) or "a few transferable experiences"
    missing = ", ".join(item.skill for item in deterministic.missing_skills[:2]) or "deeper proof of role-specific experience"
    return f"{opener} Your strongest evidence today is in {matched}. The biggest gaps to close next are {missing}. Prioritize adding one project or bullet that turns those missing skills into visible proof."



def build_demo_interview_feedback(question: str, answer_text: str) -> InterviewFeedbackResult:
    stripped = answer_text.strip()
    word_count = len(stripped.split())
    has_numbers = bool(re.search(r"\d", stripped))
    has_action = bool(re.search(r"\b(I|we)\s+(built|created|analyzed|led|improved|designed|implemented|fixed|presented|launched)\b", stripped, re.IGNORECASE))
    has_result = bool(re.search(r"\b(result|impact|outcome|improved|increased|reduced|learned)\b", stripped, re.IGNORECASE)) or has_numbers
    has_structure = len(re.split(r"[.!?]", stripped)) >= 2

    relevance = 8 if word_count >= 40 else 5 if word_count >= 20 else 3
    structure = 8 if has_structure and word_count >= 50 else 6 if has_structure else 4
    evidence = 8 if has_action and has_result else 6 if has_action else 3
    clarity = 8 if word_count >= 35 else 6 if word_count >= 20 else 4

    overall = round((relevance + structure + evidence + clarity) / 40 * 100)

    strengths: list[str] = []
    weaknesses: list[str] = []

    if word_count >= 30:
        strengths.append("You gave enough context for the interviewer to understand the situation.")
    else:
        weaknesses.append("Your answer is too short to fully show your thinking and impact.")

    if has_action:
        strengths.append("You described actions you personally took, which helps ownership come through.")
    else:
        weaknesses.append("It is not yet clear what you specifically did versus what the team did.")

    if has_result:
        strengths.append("You included an outcome or signal of impact.")
    else:
        weaknesses.append("Add a result, metric, or lesson learned so the answer feels complete.")

    if has_structure:
        strengths.append("The answer has a reasonable flow instead of sounding random.")
    else:
        weaknesses.append("Use a clearer beginning, middle, and end to make the answer easier to follow.")

    tips = [
        "Answer with STAR: situation, task, action, result.",
        "Name one concrete tool, decision, or tradeoff you handled yourself.",
        "End with the measurable outcome or what changed because of your work.",
    ]

    next_steps = [
        "Rewrite the answer into 4 short STAR bullets before speaking it aloud.",
        "Add one metric, scale indicator, or concrete result.",
        "Practice a second version that is under 90 seconds.",
    ]

    sample_better_answer = build_sample_better_answer(question, answer_text)

    return InterviewFeedbackResult(
        overall_score=overall,
        strengths=strengths[:3],
        weaknesses=weaknesses[:3],
        feedback_by_category=FeedbackCategoryScores(
            relevance=relevance,
            structure=structure,
            evidence=evidence,
            clarity=clarity,
        ),
        improved_answer_tips=tips,
        next_steps=next_steps,
        sample_better_answer=sample_better_answer,
        demo_mode=True,
    )



def build_sample_better_answer(question: str, answer_text: str) -> str:
    if not answer_text.strip():
        return (
            "In one class project, our data was messy and the first analysis was unreliable. "
            "I took ownership of cleaning the dataset, standardizing categories, and rebuilding the dashboard. "
            "After that, our team could explain the trend clearly and give one recommendation with confidence. "
            "That experience taught me to slow down, validate assumptions, and communicate the result in simple language."
        )

    condensed = re.sub(r"\s+", " ", answer_text.strip())
    first_sentence = condensed.split(".")[0].strip()
    return (
        f"A stronger version of your answer could start like this: {first_sentence}. "
        "Then add the specific task you owned, the key action you took, and a measurable result or lesson learned."
    )
