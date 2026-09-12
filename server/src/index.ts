import cors from "cors";
import express from "express";
import { meetings, priorities, team, updates } from "./data.js";
import type { Overview, Stat } from "./types.js";

const app = express();
app.use(cors());
app.use(express.json());

const PORT = Number(process.env.PORT ?? 4000);

function buildStats(): Stat[] {
  const open = priorities.filter((p) => p.status !== "done").length;
  const atRisk = priorities.filter((p) => p.status === "at_risk" || p.status === "blocked").length;
  const avgWorkload = Math.round(team.reduce((sum, t) => sum + t.workload, 0) / team.length);
  return [
    { label: "Open priorities", value: String(open), delta: -1, hint: "vs. yesterday" },
    { label: "Needs attention", value: String(atRisk), delta: 1, hint: "at risk or blocked" },
    { label: "Meetings today", value: String(meetings.length), delta: 0, hint: "on the calendar" },
    { label: "Avg. team load", value: `${avgWorkload}%`, delta: -4, hint: "capacity used" },
  ];
}

app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", service: "chief-of-staff", time: new Date().toISOString() });
});

app.get("/api/overview", (_req, res) => {
  const overview: Overview = {
    stats: buildStats(),
    priorities,
    meetings,
    team,
    updates,
  };
  res.json(overview);
});

app.post("/api/priorities/:id/toggle", (req, res) => {
  const priority = priorities.find((p) => p.id === req.params.id);
  if (!priority) {
    return res.status(404).json({ error: "priority not found" });
  }
  priority.status = priority.status === "done" ? "on_track" : "done";
  return res.json(priority);
});

app.listen(PORT, () => {
  console.log(`[chief-of-staff] API listening on http://localhost:${PORT}`);
});
