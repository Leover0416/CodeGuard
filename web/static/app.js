const $ = (id) => document.getElementById(id);

const prUrl = $("prUrl");
const submitBtn = $("submitBtn");
const loading = $("loading");
const errorEl = $("error");
const results = $("results");

function severityClass(s) {
  return ["critical", "high", "medium", "low"].includes(s) ? s : "low";
}

function renderRisks(risks) {
  const el = $("risks");
  if (!risks.length) {
    el.innerHTML = "<p class='muted'>未发现明显风险项</p>";
    return;
  }
  el.innerHTML = risks
    .map(
      (r) => `
    <div class="risk-item ${severityClass(r.severity)}">
      <span class="badge">${r.severity}</span>
      <span class="badge">${r.category}</span>
      <strong>${r.file}</strong>
      ${r.line_hint ? `<span class="muted"> · ${r.line_hint}</span>` : ""}
      <p>${r.description}</p>
      <p class="muted">建议：${r.suggestion}</p>
    </div>`
    )
    .join("");
}

function renderSuggestions(suggestions) {
  const el = $("suggestions");
  if (!suggestions.length) {
    el.innerHTML = "<p class='muted'>暂无额外建议</p>";
    return;
  }
  el.innerHTML = suggestions
    .map(
      (s) => `
    <div class="sug-item">
      <span class="badge">${s.priority}</span>
      <strong>${s.file}</strong>
      ${s.line_hint ? `<span class="muted"> · ${s.line_hint}</span>` : ""}
      <p>${s.comment}</p>
    </div>`
    )
    .join("");
}

submitBtn.addEventListener("click", async () => {
  const url = prUrl.value.trim();
  if (!url) return;

  errorEl.classList.add("hidden");
  results.classList.add("hidden");
  loading.classList.remove("hidden");
  submitBtn.disabled = true;

  try {
    const res = await fetch("/api/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pr_url: url }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "请求失败");

    const review = data.review;
    $("prTitle").textContent = data.pr_title;
    $("prMeta").textContent = `${data.author} · ${data.changed_files} files · +${data.additions}/-${data.deletions} · ${data.pr_url}`;

    const verdict = $("verdict");
    verdict.textContent = `结论: ${review.overall_verdict}`;
    verdict.className = `verdict ${review.overall_verdict}`;

    $("summary").textContent = review.summary;
    $("impact").textContent = review.impact_scope;
    $("confidence").textContent = review.confidence_note || "";

    renderRisks(review.risks || []);
    renderSuggestions(review.suggestions || []);

    results.classList.remove("hidden");
  } catch (e) {
    errorEl.textContent = e.message || String(e);
    errorEl.classList.remove("hidden");
  } finally {
    loading.classList.add("hidden");
    submitBtn.disabled = false;
  }
});

prUrl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") submitBtn.click();
});
