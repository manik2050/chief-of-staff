import type { InboxAnswers, InboxItem } from "./types";

export const INBOX_ITEMS: InboxItem[] = [
  {
    id: "board-deck",
    source: "email",
    from: "Priya Shah",
    fromRole: "CFO",
    subject: "Board deck v3 — need your pass before Tuesday pack-out",
    body: "Manik — attached is the Q3 board deck. I need you to confirm the hiring and runway slides before we lock the pack Tuesday 5pm. Legal already flagged the acquisition footnote on slide 14. Can you take a pass tonight?",
    receivedAt: "2026-09-19T16:40:00-07:00",
  },
  {
    id: "vp-interview",
    source: "calendar",
    from: "Jordan Hale",
    fromRole: "Recruiting",
    subject: "Hold: VP Eng final round tomorrow 9:30–10:15",
    body: "The VP Eng candidate (Sam Okonkwo) can only do tomorrow morning. I blocked 9:30–10:15 on your calendar. Please confirm you can take it or I will move it to Priya. Sam is also talking to two other companies this week.",
    receivedAt: "2026-09-19T15:12:00-07:00",
  },
  {
    id: "industry-newsletter",
    source: "email",
    from: "The Batch",
    fromRole: "Newsletter",
    subject: "This week in applied AI: evals, routing, and cheaper inference",
    body: "A roundup of papers and product launches. No action requested. Unsubscribe at any time.",
    receivedAt: "2026-09-19T06:02:00-07:00",
  },
  {
    id: "we-should-talk",
    source: "slack",
    from: "Alex Chen",
    fromRole: "Director of Product",
    subject: "#exec-private",
    body: "Hey — we should talk. Not urgent exactly but I don't want to put it in writing. Ping me when you have 10.",
    receivedAt: "2026-09-19T17:05:00-07:00",
  },
  {
    id: "vendor-renewal",
    source: "email",
    from: "Maya Ortiz",
    fromRole: "Ops",
    subject: "Datadog renewal — auto-renews Friday unless we change seats",
    body: "Our Datadog annual agreement auto-renews this Friday. Current spend is $84k. Engineering wants to drop 40 unused seats which would save about $18k. I can send the change form if you want me to handle it under the standing vendor policy.",
    receivedAt: "2026-09-18T11:20:00-07:00",
  },
  {
    id: "performance-concern",
    source: "email",
    from: "Riley Nguyen",
    fromRole: "Head of People",
    subject: "Confidential: performance concern on a direct report",
    body: "I need 20 minutes with you before I schedule a conversation with a director. There is a complaint from two teammates and a possible PIP. Please do not forward this thread.",
    receivedAt: "2026-09-19T14:03:00-07:00",
  },
];

/**
 * Recorded System One-shaped answers so the desk works without an API key.
 * Replace these by setting TYPESAFE_API_KEY and re-running triage.
 */
export const FIXTURE_ANSWERS: Record<string, InboxAnswers> = {
  "board-deck": {
    lane: {
      type: "choice",
      choice: "money",
      probabilities: {
        calendar: 0.04,
        people: 0.12,
        operations: 0.08,
        money: 0.71,
        fyi: 0.02,
        unclear: 0.03,
      },
      confidence: 0.68,
    },
    priority: {
      type: "score",
      score: 2.2,
      legend: {
        "0": "Later",
        "1": "This week",
        "2": "Today",
        "3": "Interrupt now",
      },
      probabilities: { "0": 0.02, "1": 0.12, "2": 0.5, "3": 0.36 },
      confidence: 0.64,
    },
    needs_human: { type: "noul", noul: 0.83 },
  },
  "vp-interview": {
    lane: {
      type: "choice",
      choice: "calendar",
      probabilities: {
        calendar: 0.62,
        people: 0.28,
        operations: 0.04,
        money: 0.01,
        fyi: 0.02,
        unclear: 0.03,
      },
      confidence: 0.58,
    },
    priority: {
      type: "score",
      score: 2.7,
      legend: {
        "0": "Later",
        "1": "This week",
        "2": "Today",
        "3": "Interrupt now",
      },
      probabilities: { "0": 0.01, "1": 0.06, "2": 0.18, "3": 0.75 },
      confidence: 0.78,
    },
    needs_human: { type: "noul", noul: 0.41 },
  },
  "industry-newsletter": {
    lane: {
      type: "choice",
      choice: "fyi",
      probabilities: {
        calendar: 0.01,
        people: 0.01,
        operations: 0.03,
        money: 0.01,
        fyi: 0.92,
        unclear: 0.02,
      },
      confidence: 0.9,
    },
    priority: {
      type: "score",
      score: 0.15,
      legend: {
        "0": "Later",
        "1": "This week",
        "2": "Today",
        "3": "Interrupt now",
      },
      probabilities: { "0": 0.88, "1": 0.09, "2": 0.02, "3": 0.01 },
      confidence: 0.86,
    },
    needs_human: { type: "noul", noul: 0.04 },
  },
  "we-should-talk": {
    lane: {
      type: "choice",
      choice: "unclear",
      probabilities: {
        calendar: 0.16,
        people: 0.31,
        operations: 0.12,
        money: 0.05,
        fyi: 0.06,
        unclear: 0.3,
      },
      confidence: 0.22,
    },
    priority: {
      type: "score",
      score: 1.4,
      legend: {
        "0": "Later",
        "1": "This week",
        "2": "Today",
        "3": "Interrupt now",
      },
      probabilities: { "0": 0.15, "1": 0.4, "2": 0.3, "3": 0.15 },
      confidence: 0.34,
    },
    needs_human: { type: "noul", noul: 0.72 },
  },
  "vendor-renewal": {
    lane: {
      type: "choice",
      choice: "operations",
      probabilities: {
        calendar: 0.02,
        people: 0.02,
        operations: 0.58,
        money: 0.34,
        fyi: 0.02,
        unclear: 0.02,
      },
      confidence: 0.52,
    },
    priority: {
      type: "score",
      score: 2.1,
      legend: {
        "0": "Later",
        "1": "This week",
        "2": "Today",
        "3": "Interrupt now",
      },
      probabilities: { "0": 0.03, "1": 0.18, "2": 0.48, "3": 0.31 },
      confidence: 0.61,
    },
    needs_human: { type: "noul", noul: 0.28 },
  },
  "performance-concern": {
    lane: {
      type: "choice",
      choice: "people",
      probabilities: {
        calendar: 0.06,
        people: 0.84,
        operations: 0.03,
        money: 0.01,
        fyi: 0.01,
        unclear: 0.05,
      },
      confidence: 0.81,
    },
    priority: {
      type: "score",
      score: 2.05,
      legend: {
        "0": "Later",
        "1": "This week",
        "2": "Today",
        "3": "Interrupt now",
      },
      probabilities: { "0": 0.04, "1": 0.2, "2": 0.43, "3": 0.33 },
      confidence: 0.57,
    },
    needs_human: { type: "noul", noul: 0.96 },
  },
};
