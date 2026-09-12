import { useEffect, useState } from "react";
import type { Overview, Priority, PriorityStatus } from "./types.ts";

const STATUS_LABEL: Record<PriorityStatus, string> = {
  on_track: "On track",
  at_risk: "At risk",
  blocked: "Blocked",
  done: "Done",
};

const AVAILABILITY_LABEL: Record<string, string> = {
  available: "Available",
  focus: "Heads-down",
  ooo: "Out of office",
};

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export default function App() {
  const [data, setData] = useState<Overview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  async function load() {
    try {
      const res = await fetch("/api/overview");
      if (!res.ok) throw new Error(`API responded ${res.status}`);
      setData((await res.json()) as Overview);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function togglePriority(id: string) {
    setBusy(id);
    try {
      const res = await fetch(`/api/priorities/${id}/toggle`, { method: "POST" });
      if (!res.ok) throw new Error(`API responded ${res.status}`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update");
    } finally {
      setBusy(null);
    }
  }

  if (error) {
    return (
      <div className="state">
        <h1>Chief of Staff</h1>
        <p className="error">Could not reach the API: {error}</p>
        <button onClick={() => void load()}>Retry</button>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="state">
        <div className="spinner" />
        <p>Loading your briefing…</p>
      </div>
    );
  }

  const today = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">CoS</div>
          <div>
            <div className="brand-name">Chief of Staff</div>
            <div className="brand-sub">Executive cockpit</div>
          </div>
        </div>
        <nav>
          <a className="active" href="#overview">Overview</a>
          <a href="#priorities">Priorities</a>
          <a href="#schedule">Schedule</a>
          <a href="#team">Team</a>
          <a href="#activity">Activity</a>
        </nav>
        <div className="sidebar-footer">
          <div className="pulse" />
          <span>API connected</span>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">{today}</p>
            <h1>{greeting()}, Manik</h1>
          </div>
          <button className="refresh" onClick={() => void load()}>
            Refresh briefing
          </button>
        </header>

        <section className="stats" id="overview">
          {data.stats.map((stat) => (
            <div className="card stat" key={stat.label}>
              <p className="stat-label">{stat.label}</p>
              <div className="stat-value-row">
                <span className="stat-value">{stat.value}</span>
                <span
                  className={
                    "delta " + (stat.delta > 0 ? "up" : stat.delta < 0 ? "down" : "flat")
                  }
                >
                  {stat.delta > 0 ? "▲" : stat.delta < 0 ? "▼" : "•"} {Math.abs(stat.delta)}
                </span>
              </div>
              <p className="stat-hint">{stat.hint}</p>
            </div>
          ))}
        </section>

        <div className="grid">
          <section className="card" id="priorities">
            <div className="card-head">
              <h2>Top priorities</h2>
              <span className="count">{data.priorities.length}</span>
            </div>
            <ul className="priorities">
              {data.priorities.map((p: Priority) => (
                <li key={p.id} className={p.status === "done" ? "done" : ""}>
                  <button
                    className={"check " + (p.status === "done" ? "checked" : "")}
                    disabled={busy === p.id}
                    onClick={() => void togglePriority(p.id)}
                    aria-label="Toggle complete"
                  >
                    {p.status === "done" ? "✓" : ""}
                  </button>
                  <div className="priority-body">
                    <div className="priority-title">{p.title}</div>
                    <div className="priority-meta">
                      <span className={"badge status-" + p.status}>{STATUS_LABEL[p.status]}</span>
                      <span className={"badge impact-" + p.impact}>{p.impact} impact</span>
                      <span className="owner">{p.owner}</span>
                    </div>
                  </div>
                  <div className="due">{p.due}</div>
                </li>
              ))}
            </ul>
          </section>

          <section className="card" id="schedule">
            <div className="card-head">
              <h2>Today's schedule</h2>
              <span className="count">{data.meetings.length}</span>
            </div>
            <ul className="schedule">
              {data.meetings.map((m) => (
                <li key={m.id}>
                  <div className="time">{m.time}</div>
                  <div className="meeting-body">
                    <div className="meeting-title">{m.title}</div>
                    <div className="meeting-meta">
                      {m.location} · {m.attendees.join(", ")}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </section>

          <section className="card" id="team">
            <div className="card-head">
              <h2>Team status</h2>
              <span className="count">{data.team.length}</span>
            </div>
            <ul className="team">
              {data.team.map((t) => (
                <li key={t.id}>
                  <div className="avatar">{t.name.split(" ").map((n) => n[0]).join("")}</div>
                  <div className="team-body">
                    <div className="team-name">{t.name}</div>
                    <div className="team-role">{t.role}</div>
                    <div className="load-track">
                      <div
                        className={"load-fill " + (t.workload > 80 ? "hot" : "")}
                        style={{ width: `${t.workload}%` }}
                      />
                    </div>
                  </div>
                  <span className={"avail avail-" + t.availability}>
                    {AVAILABILITY_LABEL[t.availability]}
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="card" id="activity">
            <div className="card-head">
              <h2>Latest activity</h2>
            </div>
            <ul className="activity">
              {data.updates.map((u) => (
                <li key={u.id}>
                  <div className="dot" />
                  <div>
                    <div className="activity-text">
                      <strong>{u.author}</strong> {u.text}
                    </div>
                    <div className="activity-time">{u.at}</div>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </main>
    </div>
  );
}
