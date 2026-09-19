import react from "@vitejs/plugin-react";
import type { IncomingMessage, ServerResponse } from "node:http";
import { defineConfig, loadEnv } from "vite";
import { INBOX_ITEMS } from "./src/inbox";
import { INBOX_QUESTIONS, THRESHOLDS } from "./src/judgments";
import { triageItem } from "./src/triage";
import type { InboxItem } from "./src/types";

function readJson(req: IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (chunk) => chunks.push(chunk as Buffer));
    req.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf8");
      if (!raw) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch (error) {
        reject(error);
      }
    });
    req.on("error", reject);
  });
}

function sendJson(res: ServerResponse, status: number, body: unknown) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(body));
}

function questionsForReview() {
  return {
    thresholds: THRESHOLDS,
    questions: INBOX_QUESTIONS,
  };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  if (env.TYPESAFE_API_KEY) {
    process.env.TYPESAFE_API_KEY = env.TYPESAFE_API_KEY;
  }

  return {
  plugins: [
    react(),
    {
      name: "chief-of-staff-api",
      configureServer(server) {
        server.middlewares.use(async (req, res, next) => {
          const url = req.url?.split("?")[0] ?? "";

          if (req.method === "GET" && url === "/api/status") {
            sendJson(res, 200, {
              mode: process.env.TYPESAFE_API_KEY ? "live" : "demo",
              hasKey: Boolean(process.env.TYPESAFE_API_KEY),
            });
            return;
          }

          if (req.method === "GET" && url === "/api/inbox") {
            sendJson(res, 200, { items: INBOX_ITEMS });
            return;
          }

          if (req.method === "GET" && url === "/api/judgments") {
            sendJson(res, 200, questionsForReview());
            return;
          }

          if (req.method === "POST" && url === "/api/triage") {
            try {
              const body = (await readJson(req)) as {
                itemId?: string;
                item?: InboxItem;
              };
              const item =
                body.item ?? INBOX_ITEMS.find((entry) => entry.id === body.itemId);
              if (!item) {
                sendJson(res, 400, { error: "Pass itemId or a full item." });
                return;
              }
              const result = await triageItem(item);
              sendJson(res, 200, result);
            } catch (error) {
              const message =
                error instanceof Error ? error.message : "Triage failed.";
              sendJson(res, 500, { error: message });
            }
            return;
          }

          next();
        });
      },
    },
  ],
  };
});
