# Runbook

Follow this order. Do not skip to training.

1. Review `data/examples/source_records.json`.
2. Add only allowlisted URLs to `configs/data.toml`, then `python scripts/download_sources.py`.
3. `python scripts/extract_text.py` — empty pages are kept.
4. `python scripts/clean_ocr.py` — never auto-correct numbers.
5. Human-review briefs and target copy. Add rows to `data/examples/reviewed_examples.jsonl`.
6. `python scripts/build_examples.py && python scripts/split_dataset.py`.
7. Evaluate the v0 baseline: `python scripts/evaluate.py --generator heuristic`.
8. If you have an API key, compare `--generator prompt`.
9. Only then train: GPU machine, `accelerate launch scripts/train_qlora.py`.
10. Save checkpoints every 50 steps (already configured). On Colab, use `notebooks/train_colab.ipynb`.
11. Evaluate on the frozen test companies. If you peeked, the test set is burned.
12. Serve the adapter behind this FastAPI app (`CHIEF_OF_STAFF_GENERATOR=adapter`).
13. Keep the VPS as the TLS / auth / rate-limit gateway.

Retrain only from reviewed, permission-cleared, opt-in examples, with a documented failure pattern and a rollback artifact.
