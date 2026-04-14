from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)

suppliers = []
rfqs = []


def seed_suppliers():
    return [
        {"supplier_name": "Pacific Ingredients", "material_name": "Vanilla Powder", "material_category": "Ingredients", "country": "USA", "unit_cost": 6.50, "previous_cost": 5.90, "lead_time": 12, "delivery_status": "On Time", "moq": 800, "backup_supplier": "Yes", "backup_supplier_name": "FlavorCore Supply", "quality_issue": "No", "annual_spend": 62000, "affected_skus": 3, "brand": "Frozen Bean RTD", "owner": "Dat Nguyen", "due_date": "2026-04-30", "certifications": "SQF, Organic", "capacity_fit": "High", "qualification_stage": "Approved", "region_risk": "Low"},
        {"supplier_name": "Global Cocoa Partners", "material_name": "Cocoa Blend", "material_category": "Ingredients", "country": "Ghana", "unit_cost": 9.80, "previous_cost": 8.10, "lead_time": 24, "delivery_status": "Delayed", "moq": 1500, "backup_supplier": "No", "backup_supplier_name": "", "quality_issue": "Yes", "annual_spend": 145000, "affected_skus": 5, "brand": "Frozen Bean Mocha Line", "owner": "Procurement Team", "due_date": "2026-04-10", "certifications": "Fair Trade, Rainforest Alliance", "capacity_fit": "Medium", "qualification_stage": "Review", "region_risk": "Medium"},
        {"supplier_name": "Prime Pack Solutions", "material_name": "Single Serve Cup", "material_category": "Packaging", "country": "Mexico", "unit_cost": 3.40, "previous_cost": 3.25, "lead_time": 18, "delivery_status": "On Time", "moq": 5000, "backup_supplier": "Yes", "backup_supplier_name": "PackSphere", "quality_issue": "No", "annual_spend": 98000, "affected_skus": 7, "brand": "Frozen Bean Cups", "owner": "Sourcing Ops", "due_date": "2026-05-15", "certifications": "ISO 9001, BRCGS Packaging", "capacity_fit": "High", "qualification_stage": "Approved", "region_risk": "Low"},
        {"supplier_name": "Nordic Label Works", "material_name": "Retail Label Film", "material_category": "Labels", "country": "Canada", "unit_cost": 2.10, "previous_cost": 1.90, "lead_time": 9, "delivery_status": "On Time", "moq": 3000, "backup_supplier": "No", "backup_supplier_name": "", "quality_issue": "No", "annual_spend": 22000, "affected_skus": 9, "brand": "All Brands", "owner": "Packaging Buyer", "due_date": "2026-04-22", "certifications": "FSC", "capacity_fit": "High", "qualification_stage": "Sampling", "region_risk": "Low"},
        {"supplier_name": "Atlas Corrugate", "material_name": "Master Case Carton", "material_category": "Corrugate", "country": "USA", "unit_cost": 4.75, "previous_cost": 4.20, "lead_time": 22, "delivery_status": "Delayed", "moq": 2200, "backup_supplier": "Yes", "backup_supplier_name": "BoxLine West", "quality_issue": "No", "annual_spend": 78000, "affected_skus": 4, "brand": "Club Packs", "owner": "Packaging Buyer", "due_date": "2026-04-18", "certifications": "SFI", "capacity_fit": "Medium", "qualification_stage": "Approved", "region_risk": "Low"},
        {"supplier_name": "Closure Dynamics", "material_name": "Bottle Cap", "material_category": "Caps / Closures", "country": "USA", "unit_cost": 1.35, "previous_cost": 1.20, "lead_time": 14, "delivery_status": "On Time", "moq": 9000, "backup_supplier": "Yes", "backup_supplier_name": "CapWorks", "quality_issue": "No", "annual_spend": 51000, "affected_skus": 6, "brand": "Frozen Bean RTD", "owner": "Packaging Buyer", "due_date": "2026-05-01", "certifications": "BRCGS Packaging", "capacity_fit": "High", "qualification_stage": "Approved", "region_risk": "Low"},
        {"supplier_name": "Northern Co-Pack", "material_name": "Cold Brew Bottling", "material_category": "Co-Manufacturing", "country": "USA", "unit_cost": 0.95, "previous_cost": 0.92, "lead_time": 16, "delivery_status": "On Time", "moq": 25000, "backup_supplier": "No", "backup_supplier_name": "", "quality_issue": "No", "annual_spend": 185000, "affected_skus": 8, "brand": "Frozen Bean RTD", "owner": "Innovation Ops", "due_date": "2026-04-28", "certifications": "SQF, Kosher, Organic", "capacity_fit": "High", "qualification_stage": "Contacted", "region_risk": "Low"},
    ]


def seed_rfqs():
    return [
        {"supplier_name": "Pacific Ingredients", "material_name": "Vanilla Powder", "quote_status": "Received", "quoted_cost": 6.35, "quoted_lead": 11, "selected": "Yes"},
        {"supplier_name": "FlavorCore Supply", "material_name": "Vanilla Powder", "quote_status": "Requested", "quoted_cost": 6.10, "quoted_lead": 14, "selected": "No"},
        {"supplier_name": "PackSphere", "material_name": "Single Serve Cup", "quote_status": "Received", "quoted_cost": 3.20, "quoted_lead": 17, "selected": "No"},
        {"supplier_name": "Northern Co-Pack", "material_name": "Cold Brew Bottling", "quote_status": "In Review", "quoted_cost": 0.95, "quoted_lead": 16, "selected": "No"},
    ]


def ensure_seeded():
    global suppliers, rfqs
    if not suppliers:
        suppliers = seed_suppliers()
    if not rfqs:
        rfqs = seed_rfqs()


def enrich(item):
    x = dict(item)
    x["cost_change"] = round(x["unit_cost"] - x["previous_cost"], 2)
    risk = 0
    if x["delivery_status"] == "Delayed": risk += 40
    if x["lead_time"] > 20: risk += 25
    elif 11 <= x["lead_time"] <= 20: risk += 12
    if x["unit_cost"] >= 8: risk += 15
    if x["cost_change"] > 0.75: risk += 10
    if x["backup_supplier"] == "No": risk += 15
    if x["quality_issue"] == "Yes": risk += 20
    if x["moq"] >= 4000: risk += 8
    if x["region_risk"] == "Medium": risk += 8
    elif x["region_risk"] == "High": risk += 15

    if risk >= 55: x["risk_level"] = "High"; x["supplier_tier"] = "Critical"
    elif risk >= 28: x["risk_level"] = "Medium"; x["supplier_tier"] = "Watchlist"
    else: x["risk_level"] = "Low"; x["supplier_tier"] = "Preferred"

    fit = 0
    fit += 25 if x["capacity_fit"] == "High" else 15 if x["capacity_fit"] == "Medium" else 8
    fit += 20 if x["lead_time"] <= 14 else 12 if x["lead_time"] <= 20 else 6
    fit += 20 if x["unit_cost"] <= 4 else 12 if x["unit_cost"] <= 8 else 6
    fit += 15 if x["backup_supplier"] == "Yes" else 5
    fit += 10 if x["quality_issue"] == "No" else 0
    fit += 10 if x["qualification_stage"] in {"Approved", "Sampling"} else 5
    x["fit_score"] = fit
    x["landed_cost"] = round(x["unit_cost"] * 1.11, 2)
    x["cert_count"] = len([c for c in x["certifications"].split(",") if c.strip()])
    return x


def get_suppliers():
    ensure_seeded()
    return [enrich(x) for x in suppliers]


def get_rfqs():
    ensure_seeded()
    return list(rfqs)


def apply_filters(data, args):
    search = args.get("search", "").strip().lower()
    category = args.get("category", "")
    risk = args.get("risk", "")
    country = args.get("country", "")
    stage = args.get("stage", "")
    result = data
    if search:
        result = [x for x in result if search in x["supplier_name"].lower() or search in x["material_name"].lower() or search in x["brand"].lower()]
    if category:
        result = [x for x in result if x["material_category"] == category]
    if risk:
        result = [x for x in result if x["risk_level"] == risk]
    if country:
        result = [x for x in result if x["country"] == country]
    if stage:
        result = [x for x in result if x["qualification_stage"] == stage]
    return result


def build_summary(data):
    total = len(data)
    high = sum(1 for x in data if x["risk_level"] == "High")
    backups_needed = sum(1 for x in data if x["backup_supplier"] == "No")
    opportunities = sum(1 for x in data if x["fit_score"] >= 70 and x["risk_level"] != "High")
    savings = round(sum(max(x["cost_change"], 0) * x["moq"] for x in data), 0)
    co_packs = sum(1 for x in data if x["material_category"] == "Co-Manufacturing")
    continuity = max(0, min(100, round(100 - (sum(x["fit_score"] for x in data) / max(total, 1) / 2))))
    return {"total_suppliers": total, "high_risk": high, "backups_needed": backups_needed, "opportunities": opportunities, "potential_savings": savings, "co_packs": co_packs, "continuity": continuity}


def build_exec_story(summary):
    return (
        f"{summary['high_risk']} suppliers are currently high risk, while {summary['backups_needed']} materials still need approved backup coverage. "
        f"The sourcing workspace has identified {summary['opportunities']} strong sourcing opportunities and an estimated ${summary['potential_savings']:,.0f} in cost-improvement potential."
    )


def build_chart_data(data):
    categories = {}
    countries = {}
    for x in data:
        categories.setdefault(x["material_category"], 0)
        categories[x["material_category"]] += x["annual_spend"]
        countries.setdefault(x["country"], 0)
        countries[x["country"]] += 1
    shortlist = sorted(data, key=lambda z: z["fit_score"], reverse=True)[:6]
    return {
        "category_labels": list(categories.keys()),
        "category_spend": list(categories.values()),
        "fit_labels": [x["supplier_name"] for x in shortlist],
        "fit_values": [x["fit_score"] for x in shortlist],
        "country_labels": list(countries.keys()),
        "country_values": list(countries.values()),
    }


def build_sourcing_cards(data):
    rows = []
    for x in sorted(data, key=lambda z: z["fit_score"], reverse=True):
        rec = "Best backup option" if x["backup_supplier"] == "Yes" and x["risk_level"] == "Low" else "Review further" if x["risk_level"] == "Medium" else "Costly / higher risk"
        rows.append({"supplier_name": x["supplier_name"], "material_name": x["material_name"], "category": x["material_category"], "country": x["country"], "fit_score": x["fit_score"], "lead_time": x["lead_time"], "unit_cost": x["unit_cost"], "recommendation": rec, "certifications": x["certifications"]})
    return rows


def build_pipeline(data):
    stages = ["New", "Contacted", "Quoting", "Sampling", "Review", "Approved", "Rejected"]
    out = {stage: [] for stage in stages}
    for x in data:
        out.setdefault(x["qualification_stage"], []).append(x)
    return out


def build_planning_data(data):
    if not data:
        return {"kpis": {"forecast_accuracy": 0, "forecast_bias": 0, "service_risk": "Low", "constrained_months": 0}, "months": [], "forecast": [], "consensus": [], "capacity": [], "plans": [], "actions": []}

    total_spend = sum(x["annual_spend"] for x in data)
    base_monthly = max(120, round(total_spend / 12 / 1000))
    seasonal = [0.92, 0.97, 1.01, 1.06, 1.12, 1.18]
    months = ["May", "Jun", "Jul", "Aug", "Sep", "Oct"]
    forecast = [round(base_monthly * m) for m in seasonal]
    delay_penalty = sum(1 for x in data if x["delivery_status"] == "Delayed")
    exposure_penalty = sum(1 for x in data if x["backup_supplier"] == "No")
    consensus = [round(v * (1 + (0.01 if i < 2 else 0.025) + (delay_penalty * 0.003))) for i, v in enumerate(forecast)]
    capacity = [round(v * (0.98 - exposure_penalty * 0.01 + (0.01 if i >= 3 else 0))) for i, v in enumerate(consensus)]
    constrained_months = sum(1 for d, c in zip(consensus, capacity) if c < d)
    forecast_accuracy = max(72, min(96, round(90 - delay_penalty * 2 - exposure_penalty * 1.5)))
    forecast_bias = round(((sum(consensus) - sum(forecast)) / max(sum(forecast), 1)) * 100, 1)
    service_gap = max((d - c) for d, c in zip(consensus, capacity))
    service_risk = "High" if constrained_months >= 3 or service_gap >= 25 else "Medium" if constrained_months >= 1 else "Low"
    ranked = sorted(data, key=lambda x: (x["affected_skus"], x["annual_spend"], x["risk_level"] == "High"), reverse=True)[:4]
    plans = []
    for x in ranked:
        demand = max(150, round(x["annual_spend"] / 1000 * 1.35))
        supply = round(demand * (0.88 if x["risk_level"] == "High" else 0.95 if x["risk_level"] == "Medium" else 1.02))
        gap = demand - supply
        plans.append({"material": x["material_name"], "brand": x["brand"], "owner": x["owner"], "demand": demand, "supply": supply, "gap": gap, "status": "Expedite / rebalance" if gap > 20 else "Monitor" if gap > 0 else "Covered"})
    actions = [
        f"Lock a consensus demand plan for the next 8 weeks around {max(consensus):,}k equivalent units at peak.",
        f"Trigger supply review for {constrained_months} constrained month(s) where supply trails demand.",
        f"Prioritize backup qualification for {exposure_penalty} single-source material lane(s) before promo lift hits.",
        f"Use the S&OP forum to reconcile commercial upside vs. current service-risk posture of {service_risk.lower()}.",
    ]
    return {"kpis": {"forecast_accuracy": forecast_accuracy, "forecast_bias": forecast_bias, "service_risk": service_risk, "constrained_months": constrained_months}, "months": months, "forecast": forecast, "consensus": consensus, "capacity": capacity, "plans": plans, "actions": actions}


def build_insights(data):
    if not data:
        return {"cert_ready": 0, "qa_flags": 0, "retailer_risk": [], "single_source": 0, "avg_fit": 0, "co_pack_ready": 0, "rfq_ready": 0}
    cert_ready = sum(1 for x in data if x["cert_count"] >= 2)
    retailer_risk = sorted(data, key=lambda x: (x["affected_skus"], x["risk_level"] == "High"), reverse=True)[:3]
    qa_flags = sum(1 for x in data if x["quality_issue"] == "Yes")
    single_source = sum(1 for x in data if x["backup_supplier"] == "No")
    avg_fit = round(sum(x["fit_score"] for x in data) / max(len(data), 1))
    co_pack_ready = sum(1 for x in data if x["material_category"] == "Co-Manufacturing" and x["qualification_stage"] in {"Sampling", "Approved", "Review"})
    rfq_ready = sum(1 for x in data if x["qualification_stage"] in {"Contacted", "Quoting", "Sampling", "Review"})
    return {"cert_ready": cert_ready, "qa_flags": qa_flags, "retailer_risk": retailer_risk, "single_source": single_source, "avg_fit": avg_fit, "co_pack_ready": co_pack_ready, "rfq_ready": rfq_ready}


def build_ai_context(data, summary, page="dashboard"):
    high_risk = [x for x in data if x["risk_level"] == "High"]
    no_backup = [x for x in data if x["backup_supplier"] == "No"]
    delayed = [x for x in data if x["delivery_status"] == "Delayed"]
    top_spend = sorted(data, key=lambda x: x["annual_spend"], reverse=True)[:3]
    medium_risk = [x for x in data if x["risk_level"] == "Medium"]
    return {
        "page": page,
        "summary": summary,
        "total_annual_spend": sum(x["annual_spend"] for x in data),
        "high_risk_suppliers": [{"name": x["supplier_name"], "material": x["material_name"], "delivery": x["delivery_status"], "quality": x["quality_issue"], "spend": x["annual_spend"], "lead_time": x["lead_time"]} for x in high_risk],
        "medium_risk_suppliers": [{"name": x["supplier_name"], "material": x["material_name"], "spend": x["annual_spend"]} for x in medium_risk],
        "no_backup_suppliers": [{"name": x["supplier_name"], "material": x["material_name"], "spend": x["annual_spend"]} for x in no_backup],
        "delayed_suppliers": [{"name": x["supplier_name"], "material": x["material_name"], "spend": x["annual_spend"]} for x in delayed],
        "top_spend_suppliers": [{"name": x["supplier_name"], "material": x["material_name"], "spend": x["annual_spend"], "risk": x["risk_level"]} for x in top_spend],
        "categories": list({x["material_category"] for x in data}),
        "countries": list({x["country"] for x in data}),
    }


# ── AI insight proxy ─────────────────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "exec_summary": (
        "You are a senior CPG supply chain strategist. "
        "Given the supplier portfolio data, write a concise executive summary (3-4 sentences, no bullet points) "
        "that a VP of Supply Chain would read in 15 seconds. "
        "Focus on the biggest risks, most urgent actions, and one positive signal. "
        "Be direct and specific — use supplier names, numbers, and dollar values from the data. "
        "Plain sentences only. No headers, no markdown."
    ),
    "risk_analysis": (
        "You are a CPG procurement risk analyst. "
        "Given the supplier portfolio data, provide a sharp 4-6 bullet risk analysis. "
        "Each bullet must be one sentence. Lead each with the risk type in bold (e.g. **Supply continuity:**). "
        "Use supplier names, spend amounts, and lead times from the data. "
        "End with one 'Immediate action:' bullet. Output only the bullets."
    ),
    "sourcing_recommendations": (
        "You are a CPG strategic sourcing advisor. "
        "Given the supplier data and RFQ pipeline, produce 3 specific sourcing recommendations. "
        "Each must be one actionable sentence. Number them 1, 2, 3. "
        "Reference actual suppliers, materials, or spend figures. "
        "Focus on backup qualification, cost savings, and pipeline velocity. No headers."
    ),
    "sop_actions": (
        "You are a CPG S&OP planning director. "
        "Given the supply/demand data and supplier risk posture, write 3 S&OP action statements. "
        "Each is one crisp sentence. Number them 1, 2, 3. "
        "Reference specific materials, months, or demand figures. "
        "Focus on supply continuity, demand alignment, and escalation triggers. No markdown."
    ),
    "supplier_intake": (
        "You are a CPG procurement analyst reviewing a new supplier intake form. "
        "Given the supplier details, write a 2-sentence intake assessment: "
        "first sentence on fit and risk, second on recommended next step. "
        "Be direct and specific using the submitted values. Plain text only."
    ),
}


@app.route("/api/ai-insight", methods=["POST"])
def ai_insight():
    import urllib.request
    body = request.get_json(force=True)
    context = body.get("context", {})
    mode = body.get("mode", "exec_summary")
    extra_prompt = body.get("prompt", "")

    system = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["exec_summary"])
    user_msg = f"Data:\n{json.dumps(context, indent=2)}"
    if extra_prompt:
        user_msg += f"\n\n{extra_prompt}"

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 450,
        "system": system,
        "messages": [{"role": "user", "content": user_msg}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = "".join(b.get("text", "") for b in result.get("content", []) if b.get("type") == "text")
            return jsonify({"insight": text, "ok": True})
    except Exception as e:
        return jsonify({"insight": "", "ok": False, "error": str(e)}), 500


# ── Page routes ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    data = apply_filters(get_suppliers(), request.args)
    summary = build_summary(data)
    filters = {k: request.args.get(k, "") for k in ["search", "category", "risk", "country", "stage"]}
    all_data = get_suppliers()
    return render_template(
        "dashboard.html",
        summary=summary,
        suppliers=data,
        story=build_exec_story(summary),
        chart_data=build_chart_data(data),
        filters=filters,
        countries=sorted({x["country"] for x in all_data}),
        categories=sorted({x["material_category"] for x in all_data}),
        stages=["New", "Contacted", "Quoting", "Sampling", "Review", "Approved", "Rejected"],
        insights=build_insights(data),
        ai_context=build_ai_context(data, summary, "dashboard"),
    )


@app.route("/sourcing")
def sourcing():
    data = apply_filters(get_suppliers(), request.args)
    summary = build_summary(data)
    filters = {k: request.args.get(k, "") for k in ["search", "category", "risk", "country", "stage"]}
    all_data = get_suppliers()
    pipeline = build_pipeline(data)
    planning = build_planning_data(data)
    return render_template(
        "sourcing.html",
        summary=summary,
        sourcing_cards=build_sourcing_cards(data),
        pipeline=pipeline,
        pipeline_counts={k: len(v) for k, v in pipeline.items()},
        rfqs=get_rfqs(),
        chart_data=build_chart_data(data),
        planning=planning,
        filters=filters,
        countries=sorted({x["country"] for x in all_data}),
        categories=sorted({x["material_category"] for x in all_data}),
        stages=["New", "Contacted", "Quoting", "Sampling", "Review", "Approved", "Rejected"],
        insights=build_insights(data),
        ai_context=build_ai_context(data, summary, "sourcing"),
    )


@app.route("/add_supplier", methods=["POST"])
def add_supplier():
    new_supplier = {
        "supplier_name": request.form.get("supplier_name", "").strip(),
        "material_name": request.form.get("material_name", "").strip(),
        "material_category": request.form.get("material_category", "").strip(),
        "country": request.form.get("country", "").strip(),
        "unit_cost": float(request.form.get("unit_cost", 0)),
        "previous_cost": float(request.form.get("previous_cost", 0)),
        "lead_time": int(request.form.get("lead_time", 0)),
        "delivery_status": request.form.get("delivery_status", "On Time"),
        "moq": int(request.form.get("moq", 0)),
        "backup_supplier": request.form.get("backup_supplier", "Yes"),
        "backup_supplier_name": request.form.get("backup_supplier_name", "").strip(),
        "quality_issue": request.form.get("quality_issue", "No"),
        "annual_spend": int(request.form.get("annual_spend", 0)),
        "affected_skus": int(request.form.get("affected_skus", 0)),
        "brand": request.form.get("brand", "").strip(),
        "owner": request.form.get("owner", "").strip(),
        "due_date": request.form.get("due_date", "").strip(),
        "certifications": request.form.get("certifications", "").strip(),
        "capacity_fit": request.form.get("capacity_fit", "Medium"),
        "qualification_stage": request.form.get("qualification_stage", "New"),
        "region_risk": request.form.get("region_risk", "Low"),
    }
    suppliers.append(new_supplier)
    # Return JSON with intake data so index.html can show AI assessment
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        enriched = enrich(new_supplier)
        return jsonify({"ok": True, "supplier": enriched})
    return redirect(url_for("dashboard"))


@app.route("/add_rfq", methods=["POST"])
def add_rfq():
    rfqs.append({
        "supplier_name": request.form.get("supplier_name", "").strip(),
        "material_name": request.form.get("material_name", "").strip(),
        "quote_status": request.form.get("quote_status", "Requested"),
        "quoted_cost": float(request.form.get("quoted_cost", 0)),
        "quoted_lead": int(request.form.get("quoted_lead", 0)),
        "selected": request.form.get("selected", "No"),
    })
    return redirect(url_for("sourcing"))


@app.route("/seed", methods=["POST"])
def seed():
    global suppliers, rfqs
    suppliers = seed_suppliers()
    rfqs = seed_rfqs()
    return redirect(request.referrer or url_for("dashboard"))


@app.route("/reset", methods=["POST"])
def reset():
    suppliers.clear()
    rfqs.clear()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
