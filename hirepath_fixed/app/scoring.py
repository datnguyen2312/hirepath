from __future__ import annotations

import random
import re
from dataclasses import dataclass

from app.extractors import extract_bullet_like_lines
from app.models import DeterministicAnalysis, ResumeImprovement, RewrittenBullet, SkillGap, SkillMatch
from app.role_rubrics import get_role

ACTION_VERBS = ["Built", "Analyzed", "Improved", "Automated", "Designed", "Presented", "Led", "Developed", "Optimized"]


@dataclass(slots=True)
class KeywordEvidence:
    keywords_found: list[str]
    evidence: str
    score: float
    strength: str


SOFT_SKILL_HINTS: dict[str, list[str]] = {
    "Active Listening": ["listened", "gathered feedback", "captured requirements", "met with stakeholders"],
    "Coordination": ["coordinated", "cross-functional", "aligned", "worked with"],
    "Judgment and Decision Making": ["recommended", "decided", "prioritized", "selected"],
    "Monitoring": ["tracked", "monitored", "dashboard", "kpi", "audited"],
    "Reading Comprehension": ["reviewed", "analyzed requirements", "studied specs", "read contracts"],
    "Speaking": ["presented", "explained", "briefed", "communicated"],
    "Time Management": ["managed deadlines", "delivered on time", "prioritized"],
    "Complex Problem Solving": ["solved", "root cause", "optimization", "improved process"],
    "Negotiation": ["negotiated", "pricing", "supplier terms", "vendor discussion"],
    "Writing": ["wrote", "documentation", "report", "proposal"],
    "Active Learning": ["learned", "self-taught", "trained", "new tool"],
    "Critical Thinking": ["analyzed", "evaluated", "assessed", "synthesized"],
    "Systems Analysis": ["process mapping", "workflow", "operations analysis", "requirements analysis"],
    "Systems Evaluation": ["evaluated", "benchmark", "quality review", "tested performance"],
}


def analyze_resume_deterministically(role_slug: str, resume_text: str) -> DeterministicAnalysis:
    role = get_role(role_slug)
    lower_text = resume_text.lower()

    matched_skills: list[SkillMatch] = []
    missing_skills: list[SkillGap] = []
    weighted_points = 0.0
    weighted_total = 0

    role_keyword_evidence = score_role_keywords(role.resume_keywords, resume_text)
    metrics_evidence = score_quantified_impact(resume_text)

    for requirement in role.required_skills:
        if requirement.skill == "Role-specific keywords":
            evidence = role_keyword_evidence
        elif requirement.skill == "Quantified achievement evidence":
            evidence = metrics_evidence
        else:
            evidence = score_requirement(lower_text, resume_text, requirement.skill, requirement.keywords + role.resume_keywords)

        weighted_points += evidence.score * requirement.importance
        weighted_total += requirement.importance

        if evidence.score > 0:
            matched_skills.append(
                SkillMatch(
                    skill=requirement.skill,
                    importance=requirement.importance,
                    score=evidence.score,
                    strength="strong" if evidence.score >= 1 else "partial",
                    keywords_found=evidence.keywords_found,
                    evidence=evidence.evidence,
                )
            )
        else:
            missing_skills.append(
                SkillGap(
                    skill=requirement.skill,
                    importance=requirement.importance,
                    reason=f"The resume does not show clear evidence for {requirement.skill.lower()} using role-aligned bullets, tools, or achievements.",
                    how_to_improve=improvement_tip_for_skill(requirement.skill, role.title, role.resume_keywords),
                )
            )

    fit_score = round((weighted_points / weighted_total) * 100) if weighted_total else 0
    fit_label = label_fit_score(fit_score)

    improvements = generate_resume_improvements(role.title, resume_text, matched_skills, missing_skills, role.resume_keywords)
    rewritten_bullets = rewrite_resume_bullets(resume_text, role.title, missing_skills, role.resume_keywords)

    strengths = [
        f"Lean into {match.skill.lower()} evidence with stronger role-specific phrasing and metrics."
        for match in sorted(matched_skills, key=lambda item: (-item.importance, -item.score))[:3]
    ] or ["Add one role-aligned project or internship bullet with measurable impact."]

    biggest_gap = sorted(missing_skills, key=lambda item: (-item.importance, item.skill))
    target_gap = biggest_gap[0].skill if biggest_gap else role.required_skills[0].skill
    suggested_question = select_mock_question(role.mock_questions, target_gap)
    next_steps = build_next_steps(role.title, matched_skills, missing_skills, role.resume_keywords)

    return DeterministicAnalysis(
        role_slug=role.slug,
        role_title=role.title,
        fit_score=fit_score,
        fit_label=fit_label,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        improvements=improvements,
        rewritten_bullets=rewritten_bullets,
        strengths_to_leverage=strengths,
        suggested_question=suggested_question,
        next_steps=next_steps,
    )


def score_requirement(lower_text: str, original_text: str, skill: str, keywords: list[str]) -> KeywordEvidence:
    hits: list[str] = []
    snippets: list[str] = []

    search_terms = unique_keep_order([skill] + keywords + SOFT_SKILL_HINTS.get(skill, []))
    for keyword in search_terms:
        pattern = re.escape(keyword.lower())
        if re.search(rf"\b{pattern}\b", lower_text):
            hits.append(keyword)
            snippet = extract_snippet(original_text, keyword)
            if snippet and snippet not in snippets:
                snippets.append(snippet)

    if len(hits) >= 2:
        return KeywordEvidence(unique_keep_order(hits), " | ".join(snippets[:2]) or f"Multiple role-aligned mentions found for {skill}.", 1.0, "strong")
    if len(hits) == 1:
        return KeywordEvidence(hits, snippets[0] if snippets else f"One role-aligned mention found for {skill}.", 0.5, "partial")
    return KeywordEvidence([], "", 0.0, "missing")


def score_role_keywords(role_keywords: list[str], original_text: str) -> KeywordEvidence:
    lower_text = original_text.lower()
    hits = [kw for kw in role_keywords if kw.lower() in lower_text]
    if len(hits) >= 4:
        snippet = extract_snippet(original_text, hits[0]) if hits else ""
        return KeywordEvidence(hits[:6], snippet or f"Found several role keywords: {', '.join(hits[:4])}.", 1.0, "strong")
    if len(hits) >= 2:
        snippet = extract_snippet(original_text, hits[0]) if hits else ""
        return KeywordEvidence(hits[:4], snippet or f"Found some role keywords: {', '.join(hits[:2])}.", 0.5, "partial")
    return KeywordEvidence([], "", 0.0, "missing")


def score_quantified_impact(original_text: str) -> KeywordEvidence:
    metrics = re.findall(r"\b\d+(?:\.\d+)?%|\$\d+[\d,]*(?:k|m)?|\b\d+[\d,]*\b", original_text, re.IGNORECASE)
    impact_verbs = re.findall(r"\b(reduced|improved|increased|saved|optimized|cut|grew|boosted)\b", original_text, re.IGNORECASE)
    if len(metrics) >= 2 and impact_verbs:
        return KeywordEvidence(unique_keep_order(metrics[:4]), f"Quantified impact appears with metrics like {', '.join(metrics[:3])}.", 1.0, "strong")
    if metrics:
        return KeywordEvidence(unique_keep_order(metrics[:3]), f"At least one metric appears: {metrics[0]}.", 0.5, "partial")
    return KeywordEvidence([], "", 0.0, "missing")


def extract_snippet(text: str, keyword: str, radius: int = 90) -> str:
    match = re.search(re.escape(keyword), text, re.IGNORECASE)
    if not match:
        return ""
    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    snippet = re.sub(r"\s+", " ", text[start:end].replace("\n", " ")).strip()
    return snippet


def unique_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        lowered = value.lower()
        if lowered not in seen:
            seen.add(lowered)
            ordered.append(value)
    return ordered


def label_fit_score(score: int) -> str:
    if score >= 75:
        return "strong"
    if score >= 50:
        return "moderate"
    return "weak"


def improvement_tip_for_skill(skill: str, role_title: str, role_keywords: list[str]) -> str:
    tips = {
        "Role-specific keywords": f"Add keywords that show direct fit for {role_title.lower()}, such as {', '.join(role_keywords[:4])}.",
        "Quantified achievement evidence": "Add numbers to show scale or impact, such as cost savings, fill rate, lead time, stockouts, or time saved.",
        "Microsoft Excel": "Name the spreadsheet work you completed, such as pivot tables, formulas, dashboarding, or KPI reporting.",
        "Microsoft Office software": "Mention which Office tools you used and what output you created, such as presentations, sourcing reports, or weekly updates.",
        "Negotiation": "Add a bullet showing supplier, pricing, or contract discussions and the business result.",
        "Systems Analysis": "Describe a workflow, process map, or operations review you analyzed and what you improved.",
        "Systems Evaluation": "Explain how you evaluated operational performance, tested a process, or compared options before making a recommendation.",
    }
    return tips.get(skill, f"Add one project or work bullet that shows {skill.lower()} in action for a {role_title} application.")


def generate_resume_improvements(role_title: str, resume_text: str, matched_skills: list[SkillMatch], missing_skills: list[SkillGap], role_keywords: list[str]) -> list[ResumeImprovement]:
    improvements: list[ResumeImprovement] = []
    lower_text = resume_text.lower()

    if "skills" not in lower_text:
        improvements.append(ResumeImprovement(area="skills", issue="No clearly labeled skills section.", suggestion=f"Add a skills section tuned to {role_title} signals like {', '.join(role_keywords[:4])}."))
    if "projects" not in lower_text and "experience" not in lower_text:
        improvements.append(ResumeImprovement(area="projects", issue="Role-relevant evidence is hard to find.", suggestion="Separate projects or experience into scannable sections with short, impact-focused bullets."))
    if not re.search(r"\d", resume_text):
        improvements.append(ResumeImprovement(area="experience", issue="The resume lacks quantified results.", suggestion="Add metrics for cost savings, service level, turnaround time, inventory, or supplier performance where possible."))
    if missing_skills:
        gap = sorted(missing_skills, key=lambda item: (-item.importance, item.skill))[0]
        improvements.append(ResumeImprovement(area="projects", issue=f"Top missing signal: {gap.skill.lower()}.", suggestion=gap.how_to_improve))
    if matched_skills:
        best = sorted(matched_skills, key=lambda item: (-item.importance, -item.score))[0]
        improvements.append(ResumeImprovement(area="summary", issue=f"Your strongest fit signal is {best.skill.lower()}, but it is not fully leveraged up top.", suggestion=f"Open with a one-line summary for {role_title} and name {best.skill.lower()} plus one measurable result."))
    return improvements[:4]


def rewrite_resume_bullets(resume_text: str, role_title: str, missing_skills: list[SkillGap], role_keywords: list[str]) -> list[RewrittenBullet]:
    bullet_lines = extract_bullet_like_lines(resume_text, limit=4)
    rewrites: list[RewrittenBullet] = []
    gap_hint = missing_skills[0].skill.lower() if missing_skills else role_keywords[0].lower() if role_keywords else "business impact"
    for line in bullet_lines[:2]:
        rewrites.append(RewrittenBullet(original=line, improved=improve_bullet(line, gap_hint)))
    if not rewrites:
        rewrites = [
            RewrittenBullet(original="Helped with operations and reporting.", improved=f"Built and maintained {gap_hint}-relevant reporting, highlighted the business issue, and summarized a measurable outcome for a {role_title} audience."),
            RewrittenBullet(original="Worked with team members on projects.", improved=f"Coordinated with cross-functional partners, used role-relevant tools, and turned the work into a decision, savings opportunity, or KPI improvement."),
        ]
    return rewrites[:2]


def improve_bullet(line: str, gap_hint: str) -> str:
    cleaned = line.strip().rstrip(".")
    prefix = "" if re.match(r"^[A-Z][a-z]+", cleaned) else random.choice(ACTION_VERBS) + " "
    suffix = " and tied the work to a measurable outcome or recommendation"
    if "using" not in cleaned.lower() and "with" not in cleaned.lower():
        suffix = f" using tools relevant to {gap_hint}{suffix}"
    return f"{prefix}{cleaned}{suffix}."


def select_mock_question(questions: list[str], target_gap: str) -> str:
    for question in questions:
        if target_gap.lower().split("/")[0].strip() in question.lower():
            return question
    return questions[0] if questions else f"Tell me about a time you demonstrated {target_gap.lower()}."


def build_next_steps(role_title: str, matched_skills: list[SkillMatch], missing_skills: list[SkillGap], role_keywords: list[str]) -> list[str]:
    steps: list[str] = []
    if missing_skills:
        top_gap = sorted(missing_skills, key=lambda item: (-item.importance, item.skill))[0]
        steps.append(f"Close the top gap in {top_gap.skill.lower()} with one focused project, internship bullet, or case story this week.")
    steps.append(f"Tailor your resume headline and skills section using keywords such as {', '.join(role_keywords[:3])}.")
    steps.append("Practice the mock answer out loud using situation, action, result, and what changed.")
    steps.append("After editing the resume, re-run the analysis and compare whether the fit score and gap list improve.")
    return steps[:4]
