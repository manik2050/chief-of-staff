import type { Meeting, Priority, TeamMember, Update } from "./types.js";

export const priorities: Priority[] = [
  {
    id: "p1",
    title: "Finalize Q3 board deck",
    owner: "Manik",
    status: "on_track",
    due: "Today, 4:00 PM",
    impact: "high",
  },
  {
    id: "p2",
    title: "Close staff engineer offer",
    owner: "Talent",
    status: "at_risk",
    due: "Tomorrow",
    impact: "high",
  },
  {
    id: "p3",
    title: "Unblock data pipeline migration",
    owner: "Platform",
    status: "blocked",
    due: "Sep 15",
    impact: "medium",
  },
  {
    id: "p4",
    title: "Publish weekly leadership update",
    owner: "Manik",
    status: "on_track",
    due: "Fri",
    impact: "medium",
  },
  {
    id: "p5",
    title: "Review annual vendor renewals",
    owner: "Finance",
    status: "done",
    due: "Sep 10",
    impact: "low",
  },
];

export const meetings: Meeting[] = [
  {
    id: "m1",
    time: "09:30",
    title: "Exec staff sync",
    attendees: ["CEO", "CFO", "CTO"],
    location: "Boardroom",
  },
  {
    id: "m2",
    time: "11:00",
    title: "Product roadmap review",
    attendees: ["Product", "Design", "Eng"],
    location: "Zoom",
  },
  {
    id: "m3",
    time: "14:00",
    title: "1:1 with Head of Sales",
    attendees: ["Sales Lead"],
    location: "Office 4B",
  },
  {
    id: "m4",
    time: "16:00",
    title: "Board deck dry run",
    attendees: ["CEO", "Comms"],
    location: "Boardroom",
  },
];

export const team: TeamMember[] = [
  { id: "t1", name: "Priya Shah", role: "Chief of Staff, Ops", availability: "available", workload: 62 },
  { id: "t2", name: "Diego Alvarez", role: "Program Manager", availability: "focus", workload: 88 },
  { id: "t3", name: "Wei Chen", role: "Business Analyst", availability: "available", workload: 45 },
  { id: "t4", name: "Sara Osei", role: "Exec Assistant", availability: "ooo", workload: 0 },
];

export const updates: Update[] = [
  { id: "u1", author: "Platform", text: "Migration blocker escalated to infra on-call.", at: "12m ago" },
  { id: "u2", author: "Talent", text: "Candidate verbally accepted; awaiting signed offer.", at: "48m ago" },
  { id: "u3", author: "Finance", text: "Vendor renewals approved and archived.", at: "2h ago" },
  { id: "u4", author: "Comms", text: "Board deck narrative draft shared for review.", at: "3h ago" },
];
