import { choice, noul, score } from "@typesafe-ai/sdk";
import type { PriorityBand } from "./types";

/**
 * Questions and thresholds for inbox triage.
 *
 * Review this file with a human. TypeSafe is only as good as these
 * definitions; the rest of the app is ordinary code.
 */
export const LANE_CRITERIA = {
  calendar:
    "Time on the calendar: meetings, travel, holds, reschedules, or a request that needs a slot.",
  people:
    "A person decision: hiring, performance, interpersonal conflict, org design, or something HR-sensitive.",
  operations:
    "Execution work: process, vendors, tools, follow-ups the Chief of Staff can drive without a personal exec decision.",
  money:
    "Spend, contracts, legal exposure, fundraising, or anything that commits the company financially or legally.",
  fyi: "Awareness only. No decision, no reply, and no calendar change is required.",
  unclear:
    "The item does not contain enough to assign a lane. Do not guess a lane when the ask is missing or two lanes are equally plausible.",
} as const;

export const PRIORITY_LEVELS = [
  "Can wait more than a week. No meeting, deadline, or relationship is at risk if this sits.",
  "Belongs on this week's list. Someone is waiting, but missing today does not create a real problem.",
  "Needs a decision or reply before end of today. A deadline, visitor, or commitment is already on the clock.",
  "Interrupt the current block. A live fire, a same-day external commitment, or a people/legal issue that gets worse by waiting.",
] as const;

export const INBOX_QUESTIONS = {
  lane: choice(
    {
      task: "Assign this inbox item to exactly one Chief of Staff lane.",
      use: "Read `item.source`, `item.from`, `item.from_role`, `item.subject`, and `item.body`.",
      rule: "Pick `unclear` when two lanes are equally plausible or the ask is missing.",
    },
    LANE_CRITERIA,
  ),
  priority: score(
    {
      task: "How soon does this item need attention from the executive or Chief of Staff?",
      use: "Use stated deadlines in `item.body` and compare `item.received_at` to `now`.",
      ignore:
        "Sender seniority alone does not raise priority. A CEO newsletter is still FYI.",
    },
    PRIORITY_LEVELS,
  ),
  needs_human: noul(
    {
      task: "Should a person review this before any reply, calendar change, or routing email is sent?",
    },
    {
      true: "The item is legally sensitive, people-sensitive, irreversible, politically loaded, or asks the executive to personally commit. A wrong automatic action would be hard to undo.",
      false:
        "Standing policy is enough. The Chief of Staff can file, schedule, or route this without asking first.",
    },
  ),
};

export const THRESHOLDS = {
  /** Below this, do not trust the lane. Hold for a person. */
  laneMinConfidence: 0.55,
  /** Noul at or above this means a person must see it first. */
  needsHumanNoul: 0.6,
  /** Interrupt-now scores at or above this that lack confidence still go to review. */
  interruptScore: 2.5,
  interruptMinConfidence: 0.6,
  /** FYI items below this priority score can be filed. */
  fileMaxPriority: 1.5,
} as const;

export const PRIORITY_BANDS: Record<PriorityBand, string> = {
  later: "Later",
  this_week: "This week",
  today: "Today",
  interrupt: "Interrupt now",
};

export function priorityBand(scoreValue: number): PriorityBand {
  if (scoreValue < 0.75) return "later";
  if (scoreValue < 1.75) return "this_week";
  if (scoreValue < 2.5) return "today";
  return "interrupt";
}
