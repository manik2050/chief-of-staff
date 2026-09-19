#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from chief_of_staff.config import load_toml
from chief_of_staff.download import download_allowlist


def main() -> None:
    parser = argparse.ArgumentParser(description="Download only allowlisted PDFs.")
    parser.add_argument("--config", default="configs/data.toml")
    args = parser.parse_args()
    config = load_toml(args.config)
    urls = config.get("approved_urls") or []
    if not urls:
        print("No approved_urls in config. Refusing to crawl.")
        return
    download_allowlist(
        urls,
        Path(config["raw_dir"]),
        Path(config["download_manifest"]),
        user_agent=config.get("project_user_agent", "chief-of-staff/0.1"),
    )
    print(f"Wrote {config['download_manifest']}")


if __name__ == "__main__":
    main()
