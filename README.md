# Chief of Staff

Inbox triage for an executive desk. TypeSafe answers three questions; ordinary code decides whether to **route**, **file**, or **hold for a person**.

## How this uses TypeSafe

The [TypeSafe skill](https://github.com/typesafe-ai/skills) is installed for Cursor at `.agents/skills/typesafe-ai` (linked from `.cursor/skills/typesafe-ai`). Ask the agent to “use the TypeSafe skill” on later work.

The judgments themselves live in one file so they are easy to review:

- [`src/judgments.ts`](src/judgments.ts) — questions and thresholds
- [`src/compose.ts`](src/compose.ts) — what the desk does with those answers

| Judgment | Primitive | What it decides |
| --- | --- | --- |
| `lane` | Choice | Calendar, people, operations, money, FYI, or unclear |
| `priority` | Score | Later / this week / today / interrupt now |
| `needs_human` | Noul | Whether a person must see it before any action |

Composition rules, in order:

1. Unclear lane, or lane confidence below `0.55` → hold
2. `needs_human` at or above `0.60` → hold
3. Interrupt-now score without confidence → hold
4. FYI below the file threshold → file
5. Otherwise route to the lane

## Run the desk

```bash
npm install
npm test
npm run dev
```

Open the Vite URL. Sample items use recorded fixtures so the desk works without an API key.

To triage new items live:

```bash
cp .env.example .env
# add TYPESAFE_API_KEY from https://console.typesafe.ai
npm run dev
```

Vite reads `.env`. Restart after changing the key.

## Update the skill

```bash
npx skills add typesafe-ai/skills --skill typesafe-ai --agent cursor --yes --copy
```
