.PHONY: install test serve build-data evaluate freeze

install:
	python3 -m pip install -e ".[dev]"

test:
	python3 -m pytest

serve:
	python3 -m uvicorn chief_of_staff.app:app --reload --host 0.0.0.0 --port 8000

build-data:
	python3 scripts/build_examples.py
	python3 scripts/split_dataset.py

evaluate:
	python3 scripts/evaluate.py --generator heuristic

freeze:
	python3 scripts/record_environment.py
