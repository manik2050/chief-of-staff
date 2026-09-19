export const LANES = [
  "calendar",
  "people",
  "operations",
  "money",
  "fyi",
  "unclear",
] as const;

export type Lane = (typeof LANES)[number];

export type InboxSource = "email" | "slack" | "calendar";

export type InboxItem = {
  id: string;
  source: InboxSource;
  from: string;
  fromRole: string;
  subject: string;
  body: string;
  receivedAt: string;
};

export type ChoiceAnswer<T extends string> = {
  type: "choice";
  choice: T;
  probabilities: Record<T, number>;
  confidence: number;
};

export type ScoreAnswer = {
  type: "score";
  score: number;
  legend: Record<string, string>;
  probabilities: Record<string, number>;
  confidence: number;
};

export type NoulAnswer = {
  type: "noul";
  noul: number;
};

export type InboxAnswers = {
  lane: ChoiceAnswer<Lane>;
  priority: ScoreAnswer;
  needs_human: NoulAnswer;
};

export type DecisionAction = "review" | "route" | "file";

export type DecisionReason =
  | "uncertain_lane"
  | "sensitive"
  | "uncertain_urgency"
  | "awareness"
  | "confident";

export type PriorityBand = "later" | "this_week" | "today" | "interrupt";

export type Decision = {
  action: DecisionAction;
  reason: DecisionReason;
  lane: Lane | null;
  priorityBand: PriorityBand;
  priorityScore: number;
  needsHuman: boolean;
  summary: string;
};

export type TriageMode = "live" | "fixture";

export type TriageResult = {
  item: InboxItem;
  answers: InboxAnswers;
  decision: Decision;
  mode: TriageMode;
  model?: string;
};
