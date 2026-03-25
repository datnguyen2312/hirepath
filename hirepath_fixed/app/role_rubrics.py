from __future__ import annotations

from app.models import RoleRubric, SkillRequirement
from app.role_matrix_seed import ROLE_MATRIX_SEED


SIGNAL_KEYWORDS: dict[str, list[str]] = {
    "Active Listening": ["active listening", "listened", "gathered requirements", "stakeholder meetings", "customer feedback"],
    "Coordination": ["coordinated", "cross-functional", "aligned teams", "stakeholders", "vendors"],
    "Judgment and Decision Making": ["decision", "tradeoff", "recommended", "prioritized", "evaluated options"],
    "Monitoring": ["monitored", "tracked", "audited", "measured", "kpi", "performance"],
    "Reading Comprehension": ["analyzed documents", "reviewed contracts", "requirements", "specifications", "sops"],
    "Speaking": ["presented", "communicated", "led meetings", "briefed", "explained"],
    "Time Management": ["managed deadlines", "prioritized", "timeline", "on time", "scheduling"],
    "Complex Problem Solving": ["solved", "root cause", "optimization", "scenario analysis", "troubleshooting"],
    "Negotiation": ["negotiated", "vendor negotiation", "supplier negotiation", "pricing", "contract terms"],
    "Writing": ["wrote", "documentation", "reports", "proposal", "rfp", "rfq"],
    "Active Learning": ["learned quickly", "upskilled", "trained", "new process", "self-taught"],
    "Critical Thinking": ["analyzed", "evaluated", "assessed", "synthesized", "investigated"],
    "Systems Analysis": ["systems analysis", "process mapping", "workflow", "requirements analysis", "operations analysis"],
    "Systems Evaluation": ["evaluated systems", "performance review", "tested process", "benchmark", "quality review"],
    "Microsoft Excel": ["excel", "spreadsheets", "pivot table", "xlookup", "vlookup", "formulas"],
    "Microsoft Office software": ["microsoft office", "powerpoint", "word", "outlook", "office suite"],
    "Role-specific keywords": [],
    "Quantified achievement evidence": [],
}


ROLE_RUBRICS: list[RoleRubric] = []
for raw in ROLE_MATRIX_SEED.values():
    required_skills = []
    for signal in raw["signals"]:
        required_skills.append(
            SkillRequirement(
                skill=signal["name"],
                importance=int(signal["weight"]),
                signal_type=signal["signal_type"],
                keywords=SIGNAL_KEYWORDS.get(signal["name"], [signal["name"].lower()]),
            )
        )

    rubric = RoleRubric(
        slug=raw["slug"],
        title=raw["title"],
        summary=raw["summary"],
        onet_code=raw["onet_code"],
        onet_title=raw["onet_title"],
        job_zone=raw["job_zone"],
        job_zone_meaning=raw["job_zone_meaning"],
        job_zone_education_note=raw["job_zone_education_note"],
        top_education_distribution=raw["top_education_distribution"],
        required_skills=required_skills,
        preferred_skills=[item["name"] for item in raw.get("top_tech", [])[:4]],
        interview_competencies=raw.get("likely_interview_topics", [])[:5],
        mock_questions=raw.get("mock_questions", []),
        top_knowledge=[item["name"] for item in raw.get("top_knowledge", [])[:6]],
        top_work_activities=[item["name"] for item in raw.get("top_work_activities", [])[:5]],
        top_tasks=[item["name"] for item in raw.get("top_tasks", [])[:6]],
        top_tech=[item["name"] for item in raw.get("top_tech", [])[:7]],
        resume_keywords=raw.get("resume_keywords", []),
        likely_interview_topics=raw.get("likely_interview_topics", []),
        alternate_titles=raw.get("alternate_titles", []),
        source_urls=raw.get("source_urls", {}),
    )
    ROLE_RUBRICS.append(rubric)

ROLE_BY_SLUG = {role.slug: role for role in ROLE_RUBRICS}


DEMO_RESUMES = {
    "maya-sca": {
        "label": "Maya - Entry-level supply chain analyst",
        "text": """Maya Chen\nChicago, IL\n\nEDUCATION\nB.S. in Supply Chain Management, University of Illinois\n\nSKILLS\nExcel, Pivot Tables, XLOOKUP, PowerPoint, KPI reporting, inventory tracking, SQL basics\n\nPROJECTS\nCampus Inventory Optimization Project\n- Analyzed 18 weeks of dining hall inventory data in Excel and built a weekly KPI dashboard for stockouts and overstock.\n- Cleaned supplier and usage data, created reorder logic, and recommended changes that reduced projected waste by 12%.\n- Presented findings to faculty and student operations leads.\n\nEXPERIENCE\nOperations Student Assistant\n- Maintained logistics records, monitored order status, and prepared weekly performance reports for incoming deliveries.\n- Coordinated with three campus departments to resolve back-order issues and improve communication on delayed shipments.\n- Documented process issues and proposed an updated intake workflow that cut manual follow-up time by 20%.\n""",
    },
    "alex-procurement": {
        "label": "Alex - Procurement analyst",
        "text": """Alex Rivera\nDallas, TX\n\nEDUCATION\nB.B.A. in Operations and Analytics\n\nSKILLS\nExcel, Word, PowerPoint, vendor analysis, spend tracking, SAP basics, report writing\n\nEXPERIENCE\nPurchasing Intern\n- Prepared purchase order requests and reviewed requisitions for office, packaging, and maintenance supplies.\n- Compared supplier quotes in Excel, summarized price differences, and recommended a preferred vendor for a quarterly buy.\n- Wrote a weekly sourcing report for the operations manager and tracked delivery exceptions.\n\nPROJECTS\nSupplier Bid Evaluation Case\n- Built a bid comparison model in Excel to score pricing, delivery terms, and compliance requirements across 5 suppliers.\n- Presented the recommended award rationale and identified 8% potential savings.\n""",
    },
    "sam-manager": {
        "label": "Sam - Supply chain manager",
        "text": """Sam Patel\nAtlanta, GA\n\nSUMMARY\nSupply chain professional with internship and campus operations experience across forecasting, inventory control, warehousing, and cross-functional coordination.\n\nSKILLS\nExcel, SAP, WMS, KPI dashboards, vendor communication, forecasting, inventory planning\n\nEXPERIENCE\nLogistics Coordinator Intern\n- Monitored inbound and outbound shipments across two warehouses and escalated service failures to carriers and internal teams.\n- Built an Excel dashboard for fill rate, lead time, and inventory aging that improved weekly review speed by 30%.\n- Coordinated with purchasing, customer service, and warehouse leads to reduce stockout incidents by 11%.\n\nPROJECTS\nDemand Forecasting Capstone\n- Forecasted demand for 25 SKUs and recommended safety stock adjustments using historical seasonality and supplier lead times.\n- Presented an inventory optimization plan with projected savings and service-level impact to faculty and alumni judges.\n""",
    },
}


def get_role(slug: str) -> RoleRubric:
    if slug not in ROLE_BY_SLUG:
        raise KeyError(f"Unknown role slug: {slug}")
    return ROLE_BY_SLUG[slug]
