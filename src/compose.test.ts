import { describe, expect, it } from "vitest";
import { composeDecision } from "./compose";
import { FIXTURE_ANSWERS } from "./inbox";
import type { InboxAnswers, Lane } from "./types";

function answers(overrides: {
  lane?: Partial<InboxAnswers["lane"]> & { choice?: Lane };
  priority?: Partial<InboxAnswers["priority"]>;
  needs_human?: Partial<InboxAnswers["needs_human"]>;
}): InboxAnswers {
  const base = FIXTURE_ANSWERS["industry-newsletter"];
  return {
    lane: { ...base.lane, ...overrides.lane },
    priority: { ...base.priority, ...overrides.priority },
    needs_human: { ...base.needs_human, ...overrides.needs_human },
  };
}

describe("composeDecision", () => {
  it("files a confident low-priority FYI", () => {
    const decision = composeDecision(FIXTURE_ANSWERS["industry-newsletter"]);
    expect(decision).toMatchObject({
      action: "file",
      reason: "awareness",
      lane: "fyi",
    });
  });

  it("holds an unclear or low-confidence lane", () => {
    expect(composeDecision(FIXTURE_ANSWERS["we-should-talk"]).reason).toBe(
      "uncertain_lane",
    );
    expect(
      composeDecision(
        answers({
          lane: { choice: "operations", confidence: 0.4 },
        }),
      ).reason,
    ).toBe("uncertain_lane");
  });

  it("holds sensitive items even when the lane is clear", () => {
    const decision = composeDecision(FIXTURE_ANSWERS["performance-concern"]);
    expect(decision).toMatchObject({
      action: "review",
      reason: "sensitive",
      lane: "people",
    });
  });

  it("holds interrupt-now scores that lack confidence", () => {
    const decision = composeDecision(
      answers({
        lane: { choice: "calendar", confidence: 0.8 },
        priority: { score: 2.8, confidence: 0.4 },
        needs_human: { noul: 0.2 },
      }),
    );
    expect(decision).toMatchObject({
      action: "review",
      reason: "uncertain_urgency",
    });
  });

  it("routes a confident calendar hold", () => {
    const decision = composeDecision(FIXTURE_ANSWERS["vp-interview"]);
    expect(decision).toMatchObject({
      action: "route",
      reason: "confident",
      lane: "calendar",
      priorityBand: "interrupt",
    });
  });

  it("does not file a high-priority FYI", () => {
    const decision = composeDecision(
      answers({
        lane: { choice: "fyi", confidence: 0.9 },
        priority: { score: 2.2, confidence: 0.8 },
        needs_human: { noul: 0.1 },
      }),
    );
    expect(decision.action).toBe("route");
    expect(decision.lane).toBe("fyi");
  });

  it("uses recorded fixtures for the rest of the sample inbox", () => {
    expect(composeDecision(FIXTURE_ANSWERS["board-deck"]).reason).toBe("sensitive");
    expect(composeDecision(FIXTURE_ANSWERS["vendor-renewal"]).reason).toBe(
      "uncertain_lane",
    );
  });
});
