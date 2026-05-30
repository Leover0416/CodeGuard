const $ = (id) => document.getElementById(id);

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s ?? "";
  return d.innerHTML;
}

function scoreRingClass(score) {
  if (score >= 70) return "high";
  if (score >= 40) return "mid";
  return "low";
}

function levelClass(level) {
  return ["critical", "high", "medium", "low"].includes(level) ? level : "low";
}

function renderDashboard(data, review) {
  const radar = review.radar || {};
  $("prTitle").textContent = data.pr_title;
  $("prMeta").textContent = `${data.author} · ${data.changed_files} files · +${data.additions}/-${data.deletions}`;

  const score = radar.risk_score ?? 0;
  const ring = $("scoreRing");
  ring.className = `score-ring ${scoreRingClass(score)}`;
  $("riskScore").textContent = String(score);

  $("statsRow").innerHTML = [
    `<span class="stat-chip">变更规模 <strong>${esc(radar.change_scale)}</strong></span>`,
    `<span class="stat-chip ${radar.blocking_count ? "danger" : ""}">阻塞合并 <strong>${radar.blocking_count ?? 0}</strong></span>`,
    `<span class="stat-chip">结论 <strong>${esc(review.overall_verdict)}</strong></span>`,
  ].join("");

  $("focusHint").textContent = radar.top_focus_hint || "优先查看 Review 路线图前 3 步";
  const verdict = $("verdict");
  verdict.textContent = `合并建议: ${review.overall_verdict}`;
  verdict.className = `verdict ${review.overall_verdict}`;

  $("summary").textContent = review.summary || "";
  $("impact").textContent = review.impact_scope || "";
  const mods = radar.affected_modules || [];
  $("modules").innerHTML = mods.length
    ? mods.map((m) => `<span class="module-tag">${esc(m)}</span>`).join("")
    : "<span class='muted'>—</span>";

  renderRoute(review.review_route || []);
  renderRankings(review.file_rankings || []);
  renderBlocking(review.blocking_issues || []);
  renderFindings(review.risk_findings || []);
  renderOptional(review.optional_comments || []);
  $("confidence").textContent = review.confidence_note || "";
}

function renderRoute(steps) {
  const el = $("reviewRoute");
  if (!steps.length) {
    el.innerHTML = "<p class='muted'>暂无路线建议</p>";
    return;
  }
  el.innerHTML = steps
    .map(
      (s) => `
    <div class="route-step">
      <div class="route-order ${s.order <= 3 ? "top3" : ""}">${s.order}</div>
      <div>
        <div class="route-file">${esc(s.file)} <span class="badge">${esc(s.risk_level)}</span></div>
        <div class="route-reason">${esc(s.reason)}</div>
      </div>
    </div>`
    )
    .join("");
}

function renderRankings(rankings) {
  const el = $("fileRankings");
  if (!rankings.length) {
    el.innerHTML = "<p class='muted'>—</p>";
    return;
  }
  el.innerHTML = rankings
    .slice(0, 8)
    .map(
      (r) => `
    <div class="rank-row">
      <span>${esc(r.file)}</span>
      <span class="badge">${r.risk_score}</span>
    </div>
    <div class="rank-bar"><span style="width:${r.risk_score}%"></span></div>
    <p class="muted" style="margin:0 0 0.5rem">${esc(r.reason)}</p>`
    )
    .join("");
}

function renderBlocking(items) {
  const badge = $("blockingBadge");
  badge.textContent = String(items.length);
  badge.className = `count-badge ${items.length ? "" : "zero"}`;
  const el = $("blockingPanel");
  if (!items.length) {
    el.innerHTML = "<p class='muted'>无阻塞合并问题</p>";
    return;
  }
  el.innerHTML = items
    .map(
      (b) => `
    <div class="item high">
      <strong>${esc(b.title)}</strong> · ${esc(b.file)}
      <p>${esc(b.description)}</p>
      <div class="evidence">${esc(b.evidence)}</div>
      <p class="muted">修复：${esc(b.fix_suggestion)}</p>
    </div>`
    )
    .join("");
}

function renderFindings(items) {
  const el = $("findingsPanel");
  if (!items.length) {
    el.innerHTML = "<p class='muted'>未发现需记录的风险项</p>";
    return;
  }
  el.innerHTML = items
    .map(
      (f) => `
    <div class="item ${levelClass(f.severity)}">
      <span class="badge">${esc(f.severity)}</span>
      <span class="badge">${esc(f.category)}</span>
      <strong>${esc(f.file)}</strong>
      <p>${esc(f.description)}</p>
      <div class="evidence">${esc(f.evidence)}</div>
      <p class="muted">${esc(f.suggestion)}</p>
    </div>`
    )
    .join("");
}

function renderOptional(items) {
  const el = $("optionalPanel");
  if (!items.length) {
    el.innerHTML = "<p class='muted'>无可选 Comment（已控制噪音）</p>";
    return;
  }
  el.innerHTML = items
    .map(
      (c) => `
    <div class="item low">
      <span class="badge">${esc(c.priority)}</span>
      <strong>${esc(c.file)}</strong>
      <p>${esc(c.comment)}</p>
      ${c.evidence ? `<div class="evidence">${esc(c.evidence)}</div>` : ""}
    </div>`
    )
    .join("");
}

document.querySelectorAll(".collapse-head").forEach((btn) => {
  btn.addEventListener("click", () => {
    const card = btn.closest(".collapsible");
    const body = document.getElementById(btn.dataset.target);
    card.classList.toggle("open");
    body.classList.toggle("hidden-body");
  });
});

$("submitBtn").addEventListener("click", async () => {
  const url = $("prUrl").value.trim();
  if (!url) return;

  $("error").classList.add("hidden");
  $("results").classList.add("hidden");
  $("loading").classList.remove("hidden");
  $("submitBtn").disabled = true;

  try {
    const res = await fetch("/api/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pr_url: url }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "请求失败");
    renderDashboard(data, data.review);
    $("results").classList.remove("hidden");
  } catch (e) {
    $("error").textContent = e.message || String(e);
    $("error").classList.remove("hidden");
  } finally {
    $("loading").classList.add("hidden");
    $("submitBtn").disabled = false;
  }
});

$("prUrl").addEventListener("keydown", (e) => {
  if (e.key === "Enter") $("submitBtn").click();
});
