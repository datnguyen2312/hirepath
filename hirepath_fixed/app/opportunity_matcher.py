from __future__ import annotations

from app.jobs_data import JOBS
from app.models import (
    CandidatePreferences,
    GapAnalysisResult,
    InterviewFeedbackResult,
    JobOpportunity,
    OpportunityMatchResponse,
    RecruiterContact,
)
from app.role_rubrics import get_role


MAX_RESULTS = 15


def normalize(text: str) -> str:
    return text.strip().lower()


def score_salary(job: dict[str, object], preferences: CandidatePreferences) -> tuple[float, str]:
    salary_min = int(job.get("salary_min") or 0)
    salary_max = int(job.get("salary_max") or salary_min)
    requested_min = preferences.salary_min
    requested_max = preferences.salary_max

    if requested_min is None and requested_max is None:
        return 1.0, "Salary expectation is flexible, so this role stays in play."
    if requested_max is not None and salary_min > requested_max:
        return 0.6, "Comp may run above your current upper bound, but it can still be worth reviewing."
    if requested_min is not None and salary_max < requested_min:
        return 0.25, "Comp is below your stated target range."
    return 1.0, "Salary sits inside or close to your stated range."


def score_location(job: dict[str, object], preferences: CandidatePreferences) -> tuple[float, str]:
    preferred_location = normalize(preferences.location or "any")
    job_location = normalize(str(job.get("location") or ""))
    if preferred_location in {"", "any"}:
        return 1.0, "You are open on location."
    if preferred_location in job_location:
        return 1.0, "Location lines up with your preferred market."
    if "remote" in job_location:
        return 0.8, "Remote format keeps this opportunity flexible."
    return 0.35, "Location is weaker than your stated preference."


def score_work_mode(job: dict[str, object], preferences: CandidatePreferences) -> tuple[float, str]:
    preferred = normalize(preferences.remote_preference or "any")
    job_mode = normalize(str(job.get("work_mode") or ""))
    if preferred == "any":
        return 1.0, "You are open to any work mode."
    if preferred == job_mode:
        return 1.0, "Work mode matches your preference."
    if preferred == "remote" and job_mode == "hybrid":
        return 0.55, "Hybrid could still work, but it is not fully remote."
    return 0.35, "Work mode is weaker than your preferred setup."


def score_employment_type(job: dict[str, object], preferences: CandidatePreferences) -> tuple[float, str]:
    desired = normalize(preferences.employment_type or "internship")
    actual = normalize(str(job.get("employment_type") or ""))
    if desired == actual:
        return 1.0, "Employment type matches what you want now."
    return 0.2, "Employment type does not match your current target."


def score_role_alignment(job: dict[str, object], preferences: CandidatePreferences) -> tuple[float, str]:
    target = normalize(preferences.target_role)
    title = normalize(str(job.get("title") or ""))
    if target == title:
        return 1.0, "Role title is an exact match."
    if target in title or any(token in title for token in target.split()):
        return 0.8, "Role title is closely aligned to your target."
    return 0.35, "Role title is adjacent but not exact."


def build_opportunity_matches(
    role_slug: str,
    analysis: GapAnalysisResult,
    feedback: InterviewFeedbackResult,
    preferences: CandidatePreferences,
) -> OpportunityMatchResponse:
    role = get_role(role_slug)
    matched_skill_names = {item.skill for item in analysis.matched_skills}
    missing_skill_names = {item.skill for item in analysis.missing_skills}
    opportunities: list[JobOpportunity] = []

    for job in JOBS:
        if str(job.get("role_slug")) != role_slug:
            continue
        job_skills = [str(skill) for skill in job.get("skills", [])]
        if not job_skills:
            continue

        skill_hits = [skill for skill in job_skills if skill in matched_skill_names]
        skill_gaps = [skill for skill in job_skills if skill in missing_skill_names or skill not in matched_skill_names]
        skill_score = len(skill_hits) / len(job_skills)

        role_score, role_reason = score_role_alignment(job, preferences)
        location_score, location_reason = score_location(job, preferences)
        work_mode_score, mode_reason = score_work_mode(job, preferences)
        employment_score, employment_reason = score_employment_type(job, preferences)
        salary_score, salary_reason = score_salary(job, preferences)

        interview_bonus = 0.10 if feedback.overall_score >= 75 else 0.05 if feedback.overall_score >= 55 else 0.0
        weighted = (
            role_score * 0.28
            + skill_score * 0.30
            + location_score * 0.10
            + salary_score * 0.09
            + work_mode_score * 0.06
            + employment_score * 0.07
            + interview_bonus
            + (analysis.fit_score / 100) * 0.10
        )
        match_score = max(1, min(100, round(weighted * 100)))

        why_match = [
            role_reason,
            (
                f"You already show evidence for {', '.join(skill_hits[:3])}."
                if skill_hits
                else f"This opening stretches you toward {role.title.lower()} signals."
            ),
            location_reason,
            mode_reason,
            salary_reason,
            employment_reason,
        ]

        recruiter_action = (
            f"Use the recruiting / HR team list below to reach out after tailoring your resume to {job['company']}. "
            "Mention one or two of your strongest matched skills and ask for advice on how to stand out."
        )
        next_action = (
            f"Tailor your resume for {', '.join(skill_gaps[:2])} and reuse your strongest interview story before applying."
            if skill_gaps
            else "Resume fit is already strong. Customize your top bullets and apply this week."
        )

        contacts = [RecruiterContact(**contact) for contact in job.get("recruiter_contacts", [])]

        opportunities.append(
            JobOpportunity(
                source=str(job["source"]),
                title=str(job["title"]),
                company=str(job["company"]),
                location=str(job["location"]),
                salary_text=str(job.get("salary_text") or "Not listed"),
                apply_url=str(job["apply_url"]),
                recruiter_search_url=str(job["recruiter_search_url"]),
                recruiter_action=recruiter_action,
                recruiter_contacts=contacts,
                company_blurb=str(job.get("company_blurb") or ""),
                match_score=match_score,
                why_match=why_match[:6],
                missing_skills=skill_gaps[:4],
                next_action=next_action,
            )
        )

    opportunities.sort(key=lambda item: item.match_score, reverse=True)
    ranked_jobs = opportunities[:MAX_RESULTS]
    high_count = sum(1 for item in ranked_jobs if item.match_score >= 85)
    mid_count = sum(1 for item in ranked_jobs if 70 <= item.match_score < 85)

    summary = (
        f"Showing {len(ranked_jobs)} ranked opportunities for the {role.title} path. "
        f"Highest-likelihood matches appear first, followed by stretch options. "
        f"{high_count} roles are in the strongest tier and {mid_count} roles are in the medium-fit tier. "
        "Each card also includes the recruiting / HR contacts available in this demo so the candidate has clear next outreach options."
        if ranked_jobs
        else "No strong matches yet. Broaden location or salary preferences and try again."
    )
    return OpportunityMatchResponse(preferences=preferences, jobs=ranked_jobs, summary=summary)
