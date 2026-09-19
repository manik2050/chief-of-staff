const form = document.getElementById("brief-form");
const copyEl = document.getElementById("copy");
const metaEl = document.getElementById("meta");
const scoresEl = document.getElementById("scores");
const scorecard = document.getElementById("scorecard");
const statusEl = document.getElementById("status");
const submit = document.getElementById("submit");

const sample = {
  brief:
    "We help independent clinics reduce missed appointments with automated reminders and patient follow-up.",
  industry: "Healthcare",
  stage: "Seed",
  traction: "",
  fundraising_goal: "Expand the product and sales team.",
  evidence: "",
};

async function loadPipeline() {
  try {
    const [health, pipeline] = await Promise.all([
      fetch("/health").then((r) => r.json()),
      fetch("/pipeline").then((r) => r.json()),
    ]);
    const checks = Object.entries(pipeline.checks)
      .map(([key, ok]) => `${ok ? "✓" : "○"} ${key.replaceAll("_", " ")}`)
      .join("<br />");
    statusEl.innerHTML = `
      <p><strong>${health.generator}</strong> generator</p>
      <p>${pipeline.next}</p>
      <p>${checks}</p>
    `;
  } catch (error) {
    statusEl.innerHTML = `<p>Could not reach the API.</p>`;
  }
}

function chip(label, ok, detail) {
  const li = document.createElement("li");
  li.innerHTML = `<span>${label}</span><span class="${ok ? "ok" : "bad"}">${detail}</span>`;
  return li;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  submit.disabled = true;
  metaEl.textContent = "Writing…";
  const payload = {
    brief: document.getElementById("brief").value,
    industry: document.getElementById("industry").value || null,
    stage: document.getElementById("stage").value || null,
    traction: document.getElementById("traction").value || null,
    fundraising_goal: document.getElementById("fundraising_goal").value || null,
    evidence: document.getElementById("evidence").value || null,
    consent_to_improve: document.getElementById("consent").checked,
  };
  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || "Generate failed");
    }
    const data = await response.json();
    copyEl.textContent = data.pitch_copy;
    metaEl.textContent = `${data.generator} · ${data.latency_ms} ms`;
    const evaln = data.evaluation;
    scoresEl.innerHTML = "";
    scoresEl.append(
      chip("Plain text", evaln.plain_text_compliant, evaln.plain_text_compliant ? "pass" : "structured"),
      chip(
        "Invented numbers",
        !evaln.numeric_error,
        evaln.numeric_error ? evaln.unsupported_numbers.join(", ") : "none"
      ),
      chip("Repetition", !evaln.repetition, evaln.repetition ? "flagged" : "ok"),
      chip("Empty", !evaln.empty_output, evaln.empty_output ? "empty" : "ok")
    );
    scorecard.hidden = false;
  } catch (error) {
    copyEl.textContent = error.message;
    metaEl.textContent = "Error";
  } finally {
    submit.disabled = false;
  }
});

document.getElementById("sample").addEventListener("click", () => {
  Object.entries(sample).forEach(([key, value]) => {
    const node = document.getElementById(key);
    if (node) node.value = value;
  });
});

document.getElementById("report").addEventListener("click", async () => {
  await fetch("/feedback?unsupported_claim=true", { method: "POST" });
  metaEl.textContent = `${metaEl.textContent} · claim reported`;
});

loadPipeline();
