# Stageshow in this kit

Stageshow is a **product-illustration skill**. It teaches the agent to build a
small React scene that *looks like* a real app: a cropped window, a phone, a
bento tile, or a short cursor walkthrough. It is not a screenshot of this repo
and not a Cursor Canvas. It is fake UI, framed on purpose, with real words only
where the story is.

Upstream: [benjitaylor/skills](https://github.com/benjitaylor/skills),
[benji.org/stageshow](https://benji.org/stageshow). Installed at
`.agents/skills/stageshow/` so agents in this folder, including Cloud Agents,
can load it. It is not a CoS slash command. It does not change `/gm`, triage, or
approval.

## How it fires (you do not type a command)

Cursor keeps a catalog of project skills. Each skill's `description` is what the
agent uses to decide relevance (**Agent Decides**). Stageshow's description
already covers mocked UI, heroes, bentos, and cursor demos.

This repo also always-applies `.cursor/rules/stageshow.mdc`. Every turn, the
agent is told: if the ask matches those triggers, **read the skill now**. It
must not wait for `/stageshow`.

You just talk:

```text
Make a README hero: someone assigns a dispatch to an agent owner.
Light, looping, window cropped off the right edge.
```

That is enough. `/stageshow` still exists as a manual override (or a Custom
Mode if you want the skill pinned for a whole session). It is not the normal
path.

It will **not** fire on `/gm`, inbox triage, or "add a task". Those stay prose.

## What you get

A React component built from the kit in `.agents/skills/stageshow/kit/`,
starting from a gold example, then filmed. Output belongs on a page or in
README assets, not in `briefings/` or `work-log/`.

## What it will not do

- Replace Canvas (data beside chat) or decorate a briefing (CLAUDE.md §14).
- Land in `skills/` or in `~/.claude/chief-of-staff/` (installer must not copy it).
- Paste Linear/Figma chrome onto this OS. Product studies are for motion, not identity.

## Playground (optional, for you to look)

Node 20.19+. From `.agents/skills/stageshow/`: `npm install` then `npm run dev`.
Preview at `http://stageshow.localhost:1355` (or the Vite URL on Windows).

## Dispatch

A still or demo is `implement` / `feature`. `done_when`: the component plus a
filmed still at the shown width. Publishing still needs a yes (CLAUDE.md §4).

## Update

```sh
npx skills add benjitaylor/skills --skill stageshow --agent cursor
```

Review the diff. Keep `LICENSE` and `NOTICE.md`. Do not rewrite the upstream
skill to "fit CoS"; keep kit constraints in this file and in
`.cursor/rules/stageshow.mdc`.
