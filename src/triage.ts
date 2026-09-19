import { TypeSafeClient } from "@typesafe-ai/sdk";
import { composeDecision } from "./compose";
import { FIXTURE_ANSWERS } from "./inbox";
import { INBOX_QUESTIONS } from "./judgments";
import type { InboxAnswers, InboxItem, Lane, TriageResult } from "./types";

function toItemState(item: InboxItem) {
  return {
    now: "2026-09-19T18:00:00-07:00",
    item: {
      source: item.source,
      from: item.from,
      from_role: item.fromRole,
      subject: item.subject,
      body: item.body,
      received_at: item.receivedAt,
    },
  };
}

function asInboxAnswers(answers: {
  lane: { choice: string; probabilities: Record<string, number>; confidence: number };
  priority: {
    score: number;
    legend: Record<string, string>;
    probabilities: Record<string, number>;
    confidence: number;
  };
  needs_human: { noul: number };
}): InboxAnswers {
  return {
    lane: {
      type: "choice",
      choice: answers.lane.choice as Lane,
      probabilities: answers.lane.probabilities as InboxAnswers["lane"]["probabilities"],
      confidence: answers.lane.confidence,
    },
    priority: {
      type: "score",
      score: answers.priority.score,
      legend: answers.priority.legend,
      probabilities: answers.priority.probabilities,
      confidence: answers.priority.confidence,
    },
    needs_human: { type: "noul", noul: answers.needs_human.noul },
  };
}

export async function triageItem(item: InboxItem): Promise<TriageResult> {
  const apiKey = process.env.TYPESAFE_API_KEY?.trim();

  if (!apiKey) {
    const fixture = FIXTURE_ANSWERS[item.id];
    if (!fixture) {
      throw new Error(
        "This item has no recorded fixture. Set TYPESAFE_API_KEY to triage new items live.",
      );
    }
    return {
      item,
      answers: fixture,
      decision: composeDecision(fixture),
      mode: "fixture",
    };
  }

  const client = new TypeSafeClient({ apiKey });
  const response = await client.systemOne({
    state: toItemState(item),
    questions: INBOX_QUESTIONS,
  });

  const answers = asInboxAnswers(response.answers);
  return {
    item,
    answers,
    decision: composeDecision(answers),
    mode: "live",
    model: response.model,
  };
}
