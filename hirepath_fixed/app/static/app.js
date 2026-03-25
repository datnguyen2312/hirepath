const page = document.body.dataset.page || "home";
const bootstrap = document.getElementById("bootstrap-data");
const data = bootstrap ? JSON.parse(bootstrap.textContent) : { roles: [], demo_resumes: [] };

const store = {
  get(key, fallback = null) {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    } catch {
      return fallback;
    }
  },
  set(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  },
};

const state = {
  roles: data.roles || [],
  selectedRoleSlug: store.get("hirepath_selected_role", ""),
  resumeText: store.get("hirepath_resume_text", ""),
  analysis: store.get("hirepath_analysis", null),
  feedback: store.get("hirepath_feedback", null),
};

function setText(el, text) { if (el) el.textContent = text; }
function show(el) { if (el) el.classList.remove("hidden"); }
function hide(el) { if (el) el.classList.add("hidden"); }
function roleTitleFromSlug(slug) {
  const role = state.roles.find((r) => r.slug === slug);
  return role ? role.title : slug;
}
function renderList(container, items, formatter) {
  if (!container) return;
  container.innerHTML = "";
  if (!items || !items.length) {
    const li = document.createElement("li");
    li.textContent = "Nothing to show yet.";
    container.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = formatter(item);
    container.appendChild(li);
  });
}

function markActive(container, selector, value, attr) {
  if (!container) return;
  container.querySelectorAll(selector).forEach((node) => {
    node.classList.toggle("active", node.getAttribute(attr) === value);
  });
}

async function loadDemoResume(key, statusEl, textarea) {
  try {
    setText(statusEl, "Loading demo resume...");
    const response = await fetch(`/api/demo-resume/${key}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Could not load demo resume.");
    state.resumeText = payload.resume_text;
    store.set("hirepath_resume_text", state.resumeText);
    if (textarea) textarea.value = payload.resume_text;
    setText(statusEl, `Loaded demo resume: ${payload.label} (${payload.word_count} words)`);
  } catch (err) {
    setText(statusEl, err.message || "Could not load demo resume.");
  }
}

async function extractResume(fileInput, statusEl, textarea, button) {
  const file = fileInput.files?.[0];
  if (!file) {
    setText(statusEl, "Choose a file first.");
    return;
  }
  const formData = new FormData();
  formData.append("file", file);
  button.disabled = true;
  try {
    setText(statusEl, "Extracting resume text...");
    const response = await fetch("/api/extract-resume", { method: "POST", body: formData });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Resume extraction failed.");
    state.resumeText = payload.resume_text;
    store.set("hirepath_resume_text", state.resumeText);
    textarea.value = payload.resume_text;
    setText(statusEl, `Extracted ${payload.word_count} words from ${payload.file_name}.`);
  } catch (err) {
    setText(statusEl, err.message || "Resume extraction failed.");
  } finally {
    button.disabled = false;
  }
}

function renderAnalysis(data) {
  setText(document.getElementById("fit-score"), `${data.fit_score}%`);
  setText(document.getElementById("fit-label"), `${data.fit_label} fit`);
  setText(document.getElementById("analysis-summary"), data.summary);
  setText(document.getElementById("mode-badge"), data.demo_mode ? "mode: demo fallback" : "mode: live AI");
  renderList(document.getElementById("matched-skills"), data.matched_skills, (item) => `${item.skill} (${item.strength}) — ${item.evidence || "Evidence captured"}`);
  renderList(document.getElementById("missing-skills"), data.missing_skills, (item) => `${item.skill}: ${item.how_to_improve}`);
  renderList(document.getElementById("resume-improvements"), data.resume_improvements, (item) => `${item.area}: ${item.suggestion}`);
  renderList(document.getElementById("next-steps"), data.next_steps, (item) => item);
  setText(document.getElementById("mock-question-box"), data.mock_interview_question);

  const rewrites = document.getElementById("rewritten-bullets");
  if (rewrites) {
    rewrites.innerHTML = "";
    (data.rewritten_bullets || []).forEach((rewrite) => {
      const card = document.createElement("div");
      card.className = "rewrite-card";
      card.innerHTML = `<div class="rewrite-original">Original: ${rewrite.original}</div><div class="rewrite-improved">Improved: ${rewrite.improved}</div>`;
      rewrites.appendChild(card);
    });
  }
  show(document.getElementById("analysis-section"));
}

async function analyzeResume() {
  const textarea = document.getElementById("resume-text");
  const resumeText = textarea.value.trim();
  if (resumeText.length < 50 || !state.selectedRoleSlug) return;
  state.resumeText = resumeText;
  store.set("hirepath_resume_text", resumeText);
  const btn = document.getElementById("analyze-btn");
  btn.disabled = true;
  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role_slug: state.selectedRoleSlug, resume_text: resumeText }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Analysis failed.");
    state.analysis = payload;
    store.set("hirepath_analysis", payload);
    renderAnalysis(payload);
  } catch (err) {
    setText(document.getElementById("analysis-summary"), err.message || "Analysis failed.");
    show(document.getElementById("analysis-section"));
  } finally {
    btn.disabled = false;
  }
}

function renderFeedback(data) {
  setText(document.getElementById("interview-score"), `${data.overall_score}%`);
  setText(document.getElementById("interview-status"), data.demo_mode ? "Demo feedback shown." : "Live AI feedback shown.");
  setText(document.getElementById("sample-better-answer"), data.sample_better_answer);
  renderList(document.getElementById("feedback-strengths"), data.strengths, (item) => item);
  renderList(document.getElementById("feedback-weaknesses"), data.weaknesses, (item) => item);
  renderList(document.getElementById("answer-tips"), data.improved_answer_tips, (item) => item);
  renderList(document.getElementById("feedback-next-steps"), data.next_steps, (item) => item);

  const categoryWrap = document.getElementById("feedback-categories");
  if (categoryWrap) {
    categoryWrap.innerHTML = "";
    Object.entries(data.feedback_by_category).forEach(([label, value]) => {
      const row = document.createElement("div");
      row.className = "score-item";
      row.innerHTML = `<span>${label}</span><span class="score-value">${value}/10</span>`;
      categoryWrap.appendChild(row);
    });
  }
  show(document.getElementById("feedback-grid"));
  show(document.getElementById("feedback-detail-grid"));
}

async function scoreInterview() {
  if (!state.analysis || !state.selectedRoleSlug) return;
  const answerText = document.getElementById("interview-answer").value.trim();
  if (answerText.length < 10) {
    setText(document.getElementById("interview-status"), "Write a longer answer first.");
    return;
  }
  const btn = document.getElementById("score-answer-btn");
  btn.disabled = true;
  try {
    const response = await fetch("/api/interview-feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ role_slug: state.selectedRoleSlug, question: state.analysis.mock_interview_question, answer_text: answerText, analysis: state.analysis }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Interview feedback failed.");
    state.feedback = payload;
    store.set("hirepath_feedback", payload);
    renderFeedback(payload);
  } catch (err) {
    setText(document.getElementById("interview-status"), err.message || "Interview feedback failed.");
  } finally { btn.disabled = false; }
}

function renderActionPlan() {
  const summary = document.getElementById("opportunity-summary");
  const grid = document.getElementById("opportunity-grid");
  if (!summary || !grid) return;

  const matched = (state.analysis?.matched_skills || []).slice(0, 4);
  const missing = (state.analysis?.missing_skills || []).slice(0, 4);
  const improvements = (state.analysis?.resume_improvements || []).slice(0, 4);
  const strengths = (state.analysis?.strengths_to_leverage || []).slice(0, 3);
  const interviewTips = (state.feedback?.improved_answer_tips || []).slice(0, 3);
  const actions = [...(state.analysis?.next_steps || []), ...(state.feedback?.next_steps || [])].filter(Boolean);
  const uniqueActions = [...new Set(actions)].slice(0, 3);

  const roleTitle = roleTitleFromSlug(state.selectedRoleSlug || "") || "your target role";
  setText(summary, `This action plan is built for the ${roleTitle} path. It highlights your strongest evidence, the skills still missing, the resume fixes to prioritize, and one interview coaching takeaway you can act on next.`);
  show(document.getElementById("opportunity-summary-card"));
  show(document.getElementById("opportunity-section"));

  grid.innerHTML = "";
  const cards = [
    {
      title: "Role-fit summary",
      subtitle: `Current result: ${state.analysis.fit_label} fit for ${roleTitle}.`,
      extra: `<div class="plan-score">${state.analysis.fit_score}% fit score</div>`,
      list: strengths.length ? strengths : [state.analysis.summary],
    },
    {
      title: "Strong matches",
      subtitle: "Skills and evidence already working in your favor.",
      list: matched.length ? matched.map((item) => `${item.skill} (${item.strength}) — ${item.evidence || "Evidence captured"}`) : ["Run the Skills Gap Check to see your strongest matches."],
    },
    {
      title: "Missing skills",
      subtitle: "The main gaps to close before applying with confidence.",
      list: missing.length ? missing.map((item) => `${item.skill}: ${item.how_to_improve}`) : ["No major missing skills surfaced in the current analysis."],
    },
    {
      title: "Resume priorities",
      subtitle: "The edits most likely to strengthen the resume quickly.",
      list: improvements.length ? improvements.map((item) => `${item.area}: ${item.suggestion}`) : ["No resume priorities available yet."],
    },
    {
      title: "Interview coaching takeaway",
      subtitle: state.feedback ? `Current interview score: ${state.feedback.overall_score}%.` : "Complete the mock interview to unlock coaching feedback.",
      list: interviewTips.length ? interviewTips : ["Complete the mock interview step to receive structured coaching tips."],
    },
    {
      title: "3 next actions",
      subtitle: "A practical short plan for what to do next.",
      list: uniqueActions.length ? uniqueActions : ["Run the earlier steps to generate a personalized action plan."],
    },
  ];

  cards.forEach((card) => {
    const article = document.createElement("article");
    article.className = "plan-card";
    const list = (card.list || []).map((item) => `<li>${item}</li>`).join("");
    article.innerHTML = `
      <h3>${card.title}</h3>
      <p class="plan-subtext">${card.subtitle}</p>
      ${card.extra || ""}
      <ul class="bullet-list top-gap">${list}</ul>
    `;
    grid.appendChild(article);
  });
}

function buildActionPlan() {
  if (!state.analysis || !state.feedback || !state.selectedRoleSlug) {
    setText(document.getElementById("opportunity-status"), "Complete Skills Gap Check and Mock Interview first.");
    return;
  }
  setText(document.getElementById("opportunity-status"), "Building your personalized action plan...");
  renderActionPlan();
  setText(document.getElementById("opportunity-status"), "Your action plan is ready.");
}

function initResumePage() {
  const textarea = document.getElementById("resume-text");
  const status = document.getElementById("upload-status");
  if (textarea && state.resumeText) textarea.value = state.resumeText;
  document.querySelectorAll("[data-demo-resume]").forEach((btn) => btn.addEventListener("click", () => {
    markActive(document.getElementById("demo-resume-list"), ".chip-button", btn.dataset.demoResume, "data-demo-resume");
    loadDemoResume(btn.dataset.demoResume, status, textarea);
  }));
  const extractBtn = document.getElementById("extract-btn");
  if (extractBtn) extractBtn.addEventListener("click", () => extractResume(document.getElementById("resume-file"), status, textarea, extractBtn));
  textarea?.addEventListener("input", () => store.set("hirepath_resume_text", textarea.value.trim()));
}

function initSkillsPage() {
  const textarea = document.getElementById("resume-text");
  if (textarea) textarea.value = state.resumeText || "";
  const selectedPill = document.getElementById("selected-role-pill");
  if (state.selectedRoleSlug) setText(selectedPill, `Selected role: ${roleTitleFromSlug(state.selectedRoleSlug)}`);
  if (state.analysis) renderAnalysis(state.analysis);
  document.querySelectorAll("[data-role-slug]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.selectedRoleSlug = btn.dataset.roleSlug;
      store.set("hirepath_selected_role", state.selectedRoleSlug);
      setText(selectedPill, `Selected role: ${roleTitleFromSlug(state.selectedRoleSlug)}`);
      markActive(document.getElementById("role-grid"), ".role-card", state.selectedRoleSlug, "data-role-slug");
      document.getElementById("analyze-btn").disabled = !(textarea.value.trim().length >= 50 && state.selectedRoleSlug);
    });
  });
  if (state.selectedRoleSlug) markActive(document.getElementById("role-grid"), ".role-card", state.selectedRoleSlug, "data-role-slug");
  textarea?.addEventListener("input", () => {
    state.resumeText = textarea.value.trim();
    store.set("hirepath_resume_text", state.resumeText);
    document.getElementById("analyze-btn").disabled = !(state.resumeText.length >= 50 && state.selectedRoleSlug);
  });
  document.getElementById("analyze-btn")?.addEventListener("click", analyzeResume);
  document.getElementById("analyze-btn").disabled = !(state.resumeText.length >= 50 && state.selectedRoleSlug);
}

function initInterviewPage() {
  if (state.analysis) {
    setText(document.getElementById("mock-question-box"), state.analysis.mock_interview_question);
    setText(document.getElementById("interview-status"), "Question ready. Write your answer below.");
  }
  if (state.feedback) renderFeedback(state.feedback);
  document.getElementById("score-answer-btn")?.addEventListener("click", scoreInterview);
}

function initNextStepPage() {
  if (state.analysis && state.feedback) {
    setText(document.getElementById("opportunity-status"), "Complete the final step to build your action plan.");
  }
  document.getElementById("build-action-plan-btn")?.addEventListener("click", buildActionPlan);
}

if (page === "resume") initResumePage();
if (page === "skills") initSkillsPage();
if (page === "interview") initInterviewPage();
if (page === "next") initNextStepPage();
