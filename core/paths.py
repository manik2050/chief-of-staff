#!/usr/bin/env python3
"""Path contract for the Chief of Staff OS.

Every path the OS depends on is resolved in exactly one place: here. Nothing else — no
command, no script, no future MCP server — should build a path out of string concatenation
or assume a home directory.

`install.sh` runs this at install time and writes the resolved map to `paths.json` inside the
install root, so agents and non-Python tooling can read the same contract without importing
anything.

Usage:
    python3 core/paths.py --json                 # print the resolved contract
    python3 core/paths.py --write ~/.claude/chief-of-staff/paths.json --ensure
    COS_HOME=/tmp/cos python3 core/paths.py --json

Resolution order for the install root:
    1. --root argument
    2. $COS_HOME
    3. $CLAUDE_HOME/chief-of-staff
    4. ~/.claude/chief-of-staff
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCHEMA_VERSION = 1


class Paths:
    """Resolved locations for every file the OS reads or writes.

    All members are static: there is one contract per process, parameterised by root, and
    nothing here should carry state.
    """

    DEFAULT_CLAUDE_DIRNAME = ".claude"
    DEFAULT_COS_DIRNAME = "chief-of-staff"

    # Directories install.sh and the agent may create. Everything else must already exist.
    MANAGED_DIRS = ("contacts", "briefings", "drafts", "work-log")

    # Reserved for later phases (PARA vault, Python MCP servers, shared skills). Declared now
    # so the contract is stable. Not created by install.sh.
    RESERVED = ("vault", "mcp", "skills")

    @staticmethod
    def canonical(path: str | os.PathLike[str]) -> Path:
        """Absolute, `~`-expanded, symlinks resolved.

        Resolving symlinks is what makes the contract comparable. On macOS `/tmp` is a symlink
        to `/private/tmp` and `$TMPDIR` sits under `/var` -> `/private/var`, so two spellings of
        the same directory are common. `install.sh` canonicalizes the same way before it
        substitutes paths into the installed files, so every recorded path matches this one.
        """
        return Path(path).expanduser().resolve()

    @staticmethod
    def claude_home() -> Path:
        """The Claude Code configuration directory (`~/.claude` unless overridden)."""
        override = os.environ.get("CLAUDE_HOME")
        if override:
            return Paths.canonical(override)
        return Paths.canonical(Path.home() / Paths.DEFAULT_CLAUDE_DIRNAME)

    @staticmethod
    def root(explicit: str | os.PathLike[str] | None = None) -> Path:
        """The Chief of Staff install root, holding all state for one operator."""
        if explicit:
            return Paths.canonical(explicit)
        override = os.environ.get("COS_HOME")
        if override:
            return Paths.canonical(override)
        return Paths.canonical(Paths.claude_home() / Paths.DEFAULT_COS_DIRNAME)

    @staticmethod
    def commands_dir() -> Path:
        """Where Claude Code looks for personal slash commands."""
        return Paths.claude_home() / "commands"

    @staticmethod
    def os_file(root: Path | None = None) -> Path:
        """The canonical copy of the OS definition (CLAUDE.md)."""
        return (root or Paths.root()) / "CLAUDE.md"

    @staticmethod
    def goals(root: Path | None = None) -> Path:
        return (root or Paths.root()) / "goals.yaml"

    @staticmethod
    def tasks(root: Path | None = None) -> Path:
        return (root or Paths.root()) / "my-tasks.yaml"

    @staticmethod
    def schedules(root: Path | None = None) -> Path:
        return (root or Paths.root()) / "schedules.yaml"

    @staticmethod
    def contacts_dir(root: Path | None = None) -> Path:
        return (root or Paths.root()) / "contacts"

    @staticmethod
    def briefings_dir(root: Path | None = None) -> Path:
        return (root or Paths.root()) / "briefings"

    @staticmethod
    def drafts_dir(root: Path | None = None) -> Path:
        return (root or Paths.root()) / "drafts"

    @staticmethod
    def work_log_dir(root: Path | None = None) -> Path:
        """Assignment files written by /dispatch. One markdown file per piece of work."""
        return (root or Paths.root()) / "work-log"

    @staticmethod
    def manifest(root: Path | None = None) -> Path:
        """Where the generated contract is written."""
        return (root or Paths.root()) / "paths.json"

    @staticmethod
    def reserved(root: Path | None = None) -> dict[str, str]:
        """Locations claimed for later phases but not created yet."""
        base = root or Paths.root()
        return {name: str(base / name) for name in Paths.RESERVED}

    @staticmethod
    def as_dict(root: Path | None = None) -> dict[str, object]:
        base = root or Paths.root()
        return {
            "schema_version": SCHEMA_VERSION,
            "generated_by": "core/paths.py",
            "root": str(base),
            "claude_home": str(Paths.claude_home()),
            "commands_dir": str(Paths.commands_dir()),
            "files": {
                "os": str(Paths.os_file(base)),
                "goals": str(Paths.goals(base)),
                "tasks": str(Paths.tasks(base)),
                "schedules": str(Paths.schedules(base)),
                "manifest": str(Paths.manifest(base)),
            },
            "dirs": {
                "contacts": str(Paths.contacts_dir(base)),
                "briefings": str(Paths.briefings_dir(base)),
                "drafts": str(Paths.drafts_dir(base)),
                "work_log": str(Paths.work_log_dir(base)),
            },
            "reserved": Paths.reserved(base),
        }

    @staticmethod
    def ensure(root: Path | None = None) -> Path:
        """Create the managed directories. Never touches files, never removes anything."""
        base = root or Paths.root()
        base.mkdir(parents=True, exist_ok=True)
        for name in Paths.MANAGED_DIRS:
            (base / name).mkdir(parents=True, exist_ok=True)
        return base

    @staticmethod
    def missing(root: Path | None = None) -> list[str]:
        """State files the OS expects but cannot find. Used by doctor checks."""
        base = root or Paths.root()
        expected = [
            Paths.os_file(base),
            Paths.goals(base),
            Paths.tasks(base),
            Paths.schedules(base),
            Paths.contacts_dir(base),
        ]
        return [str(p) for p in expected if not p.exists()]

    @staticmethod
    def write_manifest(root: Path | None = None, destination: Path | None = None) -> Path:
        """Write the contract as JSON. Overwrites only the generated manifest."""
        base = root or Paths.root()
        target = Path(destination).expanduser() if destination else Paths.manifest(base)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(Paths.as_dict(base), indent=2) + "\n", encoding="utf-8")
        return target


class Cli:
    """Command line entry point for the path contract."""

    @staticmethod
    def parser() -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="paths.py", description="Resolve the Chief of Staff path contract."
        )
        parser.add_argument("--root", help="Install root (defaults to $COS_HOME or ~/.claude/chief-of-staff)")
        parser.add_argument("--json", action="store_true", help="Print the contract as JSON")
        parser.add_argument("--write", nargs="?", const="", metavar="FILE",
                            help="Write paths.json (optionally to FILE)")
        parser.add_argument("--ensure", action="store_true", help="Create managed directories")
        parser.add_argument("--check", action="store_true",
                            help="Exit non-zero if expected state files are missing")
        return parser

    @staticmethod
    def run(argv: list[str] | None = None) -> int:
        args = Cli.parser().parse_args(argv)
        root = Paths.root(args.root)

        if args.ensure:
            Paths.ensure(root)

        if args.write is not None:
            destination = Path(args.write) if args.write else None
            written = Paths.write_manifest(root, destination)
            print(f"wrote {written}")

        if args.json or not (args.write is not None or args.ensure or args.check):
            print(json.dumps(Paths.as_dict(root), indent=2))

        if args.check:
            missing = Paths.missing(root)
            if missing:
                for path in missing:
                    print(f"missing: {path}", file=sys.stderr)
                return 1
            print("ok")

        return 0


if __name__ == "__main__":
    raise SystemExit(Cli.run())
