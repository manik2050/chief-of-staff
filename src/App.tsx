import { useEffect, useMemo, useState } from "react";
import { PRIORITY_BANDS, THRESHOLDS } from "./judgments";
import type {
  DecisionAction,
  InboxItem,
  Lane,
  TriageResult,
} from "./types";

type Status = { mode: "live" | "demo"; hasKey: boolean };

const LANE_LABELS: Record<Lane, string> = {
  calendar: "Calendar",
  people: "People",
  operations: "Operations",
  money: "Money",
  fyi: "FYI",
  unclear: "Unclear",
};

const ACTION_LABELS: Record<DecisionAction, string> = {
  review: "Hold for review",
  route: "Route",
  file: "File",
};

function formatPercent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function formatWhen(iso: string) {
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(iso));
}

async function readJson<T>(res: Response): Promise<T> {
  const data = (await res.json()) as T & { error?: string };
  if (!res.ok) {
    throw new Error(data.error ?? `Request failed (${res.status})`);
  }
  return data;
}

export function App() {
  const [status, setStatus] = useState<Status | null>(null);
  const [items, setItems] = useState<InboxItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, TriageResult>>({});
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [draftOpen, setDraftOpen] = useState(false);
  const [draft, setDraft] = useState({
    from: "",
    fromRole: "",
    subject: "",
    body: "",
    source: "email" as InboxItem["source"],
  });

  useEffect(() => {
    Promise.all([
      fetch("/api/status").then((res) => readJson<Status>(res)),
      fetch("/api/inbox").then((res) => readJson<{ items: InboxItem[] }>(res)),
    ])
      .then(([nextStatus, inbox]) => {
        setStatus(nextStatus);
        setItems(inbox.items);
        setSelectedId(inbox.items[0]?.id ?? null);
      })
      .catch((nextError: unknown) => {
        setError(nextError instanceof Error ? nextError.message : "Failed to load desk.");
      });
  }, []);

  const selected = items.find((item) => item.id === selectedId) ?? null;
  const result = selected ? results[selected.id] : undefined;
  const reviewCount = useMemo(
    () => Object.values(results).filter((entry) => entry.decision.action === "review").length,
    [results],
  );

  async function triage(item: InboxItem) {
    setPendingId(item.id);
    setError(null);
    try {
      const next = await readJson<TriageResult>(
        await fetch("/api/triage", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ item }),
        }),
      );
      setResults((current) => ({ ...current, [item.id]: next }));
      setSelectedId(item.id);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Triage failed.");
    } finally {
      setPendingId(null);
    }
  }

  async function triageAll() {
    for (const item of items) {
      await triage(item);
    }
  }

  function addDraft() {
    if (!draft.subject.trim() || !draft.body.trim()) {
      setError("A new item needs a subject and a body.");
      return;
    }
    const item: InboxItem = {
      id: `draft-${crypto.randomUUID()}`,
      source: draft.source,
      from: draft.from.trim() || "Unknown",
      fromRole: draft.fromRole.trim() || "Unknown",
      subject: draft.subject.trim(),
      body: draft.body.trim(),
      receivedAt: new Date().toISOString(),
    };
    setItems((current) => [item, ...current]);
    setSelectedId(item.id);
    setDraftOpen(false);
    setDraft({ from: "", fromRole: "", subject: "", body: "", source: "email" });
    void triage(item);
  }

  return (
    <div className="desk">
      <header className="masthead">
        <div>
          <p className="eyebrow">Chief of Staff</p>
          <h1>Inbox triage</h1>
        </div>
        <div className="masthead-meta">
          <p className={`mode mode-${status?.mode ?? "demo"}`}>
            {status?.hasKey ? "Live TypeSafe" : "Demo fixtures"}
          </p>
          <p className="counts">
            {Object.keys(results).length} judged
            {reviewCount ? ` · ${reviewCount} held` : ""}
          </p>
        </div>
      </header>

      {error ? <p className="banner">{error}</p> : null}

      <div className="workspace">
        <aside className="stack">
          <div className="stack-head">
            <h2>Incoming</h2>
            <div className="stack-actions">
              <button type="button" className="text-btn" onClick={() => setDraftOpen(true)}>
                New item
              </button>
              <button type="button" className="text-btn" onClick={() => void triageAll()}>
                Triage all
              </button>
            </div>
          </div>
          <ul>
            {items.map((item) => {
              const judged = results[item.id];
              return (
                <li key={item.id}>
                  <button
                    type="button"
                    className={item.id === selectedId ? "item active" : "item"}
                    onClick={() => setSelectedId(item.id)}
                  >
                    <span className="item-source">{item.source}</span>
                    <strong>{item.subject}</strong>
                    <span className="item-from">
                      {item.from} · {formatWhen(item.receivedAt)}
                    </span>
                    {judged ? (
                      <span className={`pill pill-${judged.decision.action}`}>
                        {ACTION_LABELS[judged.decision.action]}
                      </span>
                    ) : null}
                  </button>
                </li>
              );
            })}
          </ul>
        </aside>

        <main className="sheet">
          {selected ? (
            <>
              <p className="source-line">
                {selected.source} · {selected.fromRole}
              </p>
              <h2>{selected.subject}</h2>
              <p className="from-line">
                {selected.from}
                <span> · {formatWhen(selected.receivedAt)}</span>
              </p>
              <p className="body">{selected.body}</p>
              <button
                type="button"
                className="primary"
                disabled={pendingId === selected.id}
                onClick={() => void triage(selected)}
              >
                {pendingId === selected.id ? "Judging…" : "Triage this"}
              </button>

              {result ? <DecisionCard result={result} /> : (
                <p className="hint">
                  TypeSafe answers three questions in one call: lane, priority, and
                  whether a person should see it first. Code decides what to do.
                </p>
              )}
            </>
          ) : (
            <p className="hint">Nothing in the stack yet.</p>
          )}
        </main>
      </div>

      {draftOpen ? (
        <div className="modal" role="dialog" aria-labelledby="draft-title">
          <div className="modal-card">
            <h2 id="draft-title">New inbox item</h2>
            <p>
              Live TypeSafe is required for items that are not in the sample
              fixtures. Add <code>TYPESAFE_API_KEY</code> to run those.
            </p>
            <label>
              Source
              <select
                value={draft.source}
                onChange={(event) =>
                  setDraft((current) => ({
                    ...current,
                    source: event.target.value as InboxItem["source"],
                  }))
                }
              >
                <option value="email">Email</option>
                <option value="slack">Slack</option>
                <option value="calendar">Calendar</option>
              </select>
            </label>
            <label>
              From
              <input
                value={draft.from}
                onChange={(event) =>
                  setDraft((current) => ({ ...current, from: event.target.value }))
                }
              />
            </label>
            <label>
              Role
              <input
                value={draft.fromRole}
                onChange={(event) =>
                  setDraft((current) => ({ ...current, fromRole: event.target.value }))
                }
              />
            </label>
            <label>
              Subject
              <input
                value={draft.subject}
                onChange={(event) =>
                  setDraft((current) => ({ ...current, subject: event.target.value }))
                }
              />
            </label>
            <label>
              Body
              <textarea
                rows={5}
                value={draft.body}
                onChange={(event) =>
                  setDraft((current) => ({ ...current, body: event.target.value }))
                }
              />
            </label>
            <div className="modal-actions">
              <button type="button" className="text-btn" onClick={() => setDraftOpen(false)}>
                Cancel
              </button>
              <button type="button" className="primary" onClick={addDraft}>
                Add and triage
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

function DecisionCard({ result }: { result: TriageResult }) {
  const { decision, answers, mode } = result;
  const laneEntries = Object.entries(answers.lane.probabilities) as [Lane, number][];

  return (
    <section className="decision">
      <p className={`verdict verdict-${decision.action}`}>
        {ACTION_LABELS[decision.action]}
      </p>
      <p className="summary">{decision.summary}</p>
      <p className="mode-note">
        {mode === "live" ? `Live ${result.model ?? "TypeSafe"}` : "Recorded fixture"}
      </p>

      <div className="judgments">
        <article>
          <h3>Lane</h3>
          <p className="value">
            {decision.lane ? LANE_LABELS[decision.lane] : "—"}
          </p>
          <p className="metric">confidence {formatPercent(answers.lane.confidence)}</p>
          <ul className="dist">
            {laneEntries
              .sort((a, b) => b[1] - a[1])
              .map(([lane, probability]) => (
                <li key={lane}>
                  <span>{LANE_LABELS[lane]}</span>
                  <span>{formatPercent(probability)}</span>
                </li>
              ))}
          </ul>
        </article>
        <article>
          <h3>Priority</h3>
          <p className="value">{PRIORITY_BANDS[decision.priorityBand]}</p>
          <p className="metric">
            score {decision.priorityScore.toFixed(2)} · confidence{" "}
            {formatPercent(answers.priority.confidence)}
          </p>
        </article>
        <article>
          <h3>Human review</h3>
          <p className="value">{decision.needsHuman ? "Yes" : "No"}</p>
          <p className="metric">
            yes {formatPercent(answers.needs_human.noul)} · gate ≥{" "}
            {formatPercent(THRESHOLDS.needsHumanNoul)}
          </p>
        </article>
      </div>
    </section>
  );
}
