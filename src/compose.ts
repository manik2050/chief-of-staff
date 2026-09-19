import { PRIORITY_BANDS, THRESHOLDS, priorityBand } from "./judgments";
import type { Decision, InboxAnswers, Lane } from "./types";

const LANE_LABELS: Record<Lane, string> = {
  calendar: "Calendar",
  people: "People",
  operations: "Operations",
  money: "Money",
  fyi: "FYI",
  unclear: "Unclear",
};

export function composeDecision(answers: InboxAnswers): Decision {
  const { lane, priority, needs_human } = answers;
  const band = priorityBand(priority.score);
  const needsHuman = needs_human.noul >= THRESHOLDS.needsHumanNoul;

  if (lane.choice === "unclear" || lane.confidence < THRESHOLDS.laneMinConfidence) {
    return {
      action: "review",
      reason: "uncertain_lane",
      lane: lane.choice === "unclear" ? "unclear" : lane.choice,
      priorityBand: band,
      priorityScore: priority.score,
      needsHuman,
      summary: "Lane is unclear. Hold this for a person instead of guessing.",
    };
  }

  if (needsHuman) {
    return {
      action: "review",
      reason: "sensitive",
      lane: lane.choice,
      priorityBand: band,
      priorityScore: priority.score,
      needsHuman: true,
      summary:
        "This looks sensitive. A person should see it before any reply or calendar change.",
    };
  }

  if (
    priority.score >= THRESHOLDS.interruptScore &&
    priority.confidence < THRESHOLDS.interruptMinConfidence
  ) {
    return {
      action: "review",
      reason: "uncertain_urgency",
      lane: lane.choice,
      priorityBand: band,
      priorityScore: priority.score,
      needsHuman,
      summary:
        "Urgency looks high but uncertain. Confirm before interrupting the day.",
    };
  }

  if (lane.choice === "fyi" && priority.score < THRESHOLDS.fileMaxPriority) {
    return {
      action: "file",
      reason: "awareness",
      lane: "fyi",
      priorityBand: band,
      priorityScore: priority.score,
      needsHuman: false,
      summary: "File as FYI. No action is required this week.",
    };
  }

  return {
    action: "route",
    reason: "confident",
    lane: lane.choice,
    priorityBand: band,
    priorityScore: priority.score,
    needsHuman: false,
    summary: `Route to ${LANE_LABELS[lane.choice]} at ${PRIORITY_BANDS[band]} priority.`,
  };
}
