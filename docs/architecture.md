# Architecture

Chief of Staff is a specialist writing model, not a general assistant.

```
startup brief
      ↓
optional retrieval (market data, evidence)
      ↓
small fine-tuned model  (v0 = heuristic / prompt-only)
      ↓
plain-text output
      ↓
numeric + structure eval
```

## Machines

| Job | Machine |
| --- | --- |
| API gateway, auth, rate limits, health | small CPU VPS |
| QLoRA training, GPU inference | Colab T4 or a rented GPU |

Never train or serve the 1.5B model on the 2-vCPU box.

## Versions

- **v0** — heuristic / prompt-only baseline (what this repo ships)
- **v1** — QLoRA adapter on 200 reviewed examples
- **v2** — 1,000 reviewed examples
- **v3** — larger dataset + retrieval

Each version records a `VersionRecord` and a rollback adapter path.
