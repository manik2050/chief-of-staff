# Chief of Staff

An executive "cockpit" dashboard that surfaces the day at a glance: top priorities, today's
schedule, team status, and the latest activity across the organization.

It is a small full-stack TypeScript application:

- **`server/`** — an Express + TypeScript REST API with an in-memory data store.
- **`client/`** — a React + Vite + TypeScript single-page dashboard.

The two packages are wired together as npm workspaces, and the Vite dev server proxies
`/api` requests to the API so everything runs from a single `npm run dev`.

## Prerequisites

- Node.js `>= 20`
- npm `>= 10`

## Getting started

```bash
npm install      # install all workspace dependencies
npm run dev      # start the API (:4000) and the client (:5173) together
```

Then open http://localhost:5173.

## Available scripts (run from the repo root)

| Command             | Description                                                     |
| ------------------- | --------------------------------------------------------------- |
| `npm run dev`       | Run the API and client together with live reload.               |
| `npm run dev:server`| Run only the API (`http://localhost:4000`).                     |
| `npm run dev:client`| Run only the client (`http://localhost:5173`).                 |
| `npm run build`     | Type-check and build both packages for production.              |
| `npm run typecheck` | Type-check both packages without emitting output.               |
| `npm run start`     | Run the compiled API from `server/dist` (after `npm run build`).|

## API

| Method | Route                          | Description                                  |
| ------ | ------------------------------ | -------------------------------------------- |
| GET    | `/api/health`                  | Liveness/health probe.                       |
| GET    | `/api/overview`                | Dashboard payload (stats, priorities, etc.). |
| POST   | `/api/priorities/:id/toggle`   | Toggle a priority between open and done.      |

## Project layout

```
.
├── client/            # React + Vite + TypeScript dashboard
│   ├── src/
│   │   ├── App.tsx     # Dashboard UI
│   │   ├── main.tsx    # App entry point
│   │   ├── types.ts    # Shared client types
│   │   └── index.css   # Styling
│   ├── index.html
│   └── vite.config.ts  # Dev server + /api proxy
├── server/            # Express + TypeScript API
│   └── src/
│       ├── index.ts    # Express app + routes
│       ├── data.ts     # In-memory sample data
│       └── types.ts    # Domain types
└── package.json       # npm workspaces + root scripts
```

## Cloud Agent environment

`.cursor/environment.json` configures the Cursor Cloud Agent environment: it installs
dependencies with `npm install` and boots the app via `npm run dev` in a persistent terminal,
exposing the client (`5173`) and API (`4000`) ports.
