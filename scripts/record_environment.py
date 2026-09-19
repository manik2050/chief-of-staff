#!/usr/bin/env python3
from __future__ import annotations

import argparse
import platform
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Snapshot the training environment.")
    parser.add_argument("--output", default="configs/training-environment.txt")
    args = parser.parse_args()
    lines = [f"Python: {platform.python_version()}"]
    try:
        import torch
        import transformers
        import trl
        import peft

        lines.append(f"Torch: {torch.__version__}")
        lines.append(f"Transformers: {transformers.__version__}")
        lines.append(f"TRL: {trl.__version__}")
        lines.append(f"PEFT: {peft.__version__}")
        gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none"
        lines.append(f"GPU: {gpu}")
    except ImportError as exc:
        lines.append(f"Training libraries not installed ({exc})")
        lines.append("GPU: none")
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
