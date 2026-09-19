# Chief of Staff

Fine-tune a small LLM so it turns a startup brief into **grounded funding-pitch copy**.

This repo follows [Rahul (@sairahul1)'s fine-tuning guide](https://x.com/sairahul1/status/2100882424343265527): a 1.5B model, 200–500 good examples, QLoRA, company-level splits, and evaluation against a prompt-only baseline. Fine-tuning is not the first step.

## What it does

Input: a startup brief, plus optional industry, stage, traction, fundraising goal, and evidence.

Output: plain English pitch copy. No JSON. No slide structure. No invented metrics.

The running example:

> We help independent clinics reduce missed appointments with automated reminders and patient follow-up.

becomes copy that restates the problem and the product without fabricating revenue, customers, or market size.

## Layout

```
data/examples/     reviewed synthetic examples (public)
data/splits/       company-level split manifests
data/raw/          private PDFs (gitignored)
data/processed/    private JSONL splits (gitignored)
scripts/           download, OCR clean, dataset, train, eval
src/chief_of_staff/  library + FastAPI app
notebooks/         Colab QLoRA
configs/           data.toml, training.toml
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make test
make serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The v0 generator is a grounded heuristic so the product works without a GPU.

Build the company-level splits (processed files stay local):

```bash
make build-data
make evaluate
```

## Training (GPU)

Base model: `Qwen/Qwen2.5-1.5B-Instruct`. Do not start with 7B.

```bash
pip install -e ".[training]"
python scripts/record_environment.py
accelerate launch scripts/train_qlora.py
```

Or use `notebooks/train_colab.ipynb` on a T4. Save to Drive every 50 steps.

Serve the adapter:

```bash
export CHIEF_OF_STAFF_GENERATOR=adapter
export CHIEF_OF_STAFF_ADAPTER_DIR=artifacts/adapters/v1
make serve
```

High-throughput option: vLLM with `--enable-lora`. Keep this app (or another VPS) in front for HTTPS, auth, and rate limits.

## Rules the code enforces

- Allowlisted downloads only. Duplicates skipped by content hash.
- Empty OCR pages are recorded, not dropped.
- Cleaning does not "fix" numbers.
- Splits are by `company_id`, never by page.
- Evaluation flags invented numbers and structured/slide-shaped output.
- User data is opt-in and stripped of emails, phones, and obvious personal names.

Grow the dataset to 200–500 **human-reviewed** examples before claiming the adapter is better than the prompt-only baseline. The test companies in `data/splits/v1.json` stay frozen once you look at them.
