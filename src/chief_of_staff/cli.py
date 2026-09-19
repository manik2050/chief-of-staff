from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Chief of Staff CLI")
    parser.add_argument("command", choices=["serve", "version"])
    args = parser.parse_args()
    if args.command == "version":
        from chief_of_staff import __version__

        print(__version__)
        return
    import uvicorn

    uvicorn.run("chief_of_staff.app:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
