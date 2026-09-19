from __future__ import annotations

import json
import time
from pathlib import Path

import requests

from chief_of_staff.dataset import sha256_bytes, sha256_file, write_json
from chief_of_staff.rights import DownloadManifestEntry


class DownloadError(RuntimeError):
    pass


def download_allowlist(
    urls: list[str],
    dest_dir: Path,
    manifest_path: Path,
    *,
    user_agent: str = "chief-of-staff/0.1",
    timeout: int = 60,
) -> list[dict]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    seen_hashes: set[str] = set()
    existing = []
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        seen_hashes = {row["sha256"] for row in existing if row.get("sha256")}

    manifest = list(existing)
    for url in urls:
        filename = url.rstrip("/").split("/")[-1] or "download.pdf"
        destination = dest_dir / filename
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": user_agent},
        )
        response.raise_for_status()
        if not response.content.startswith(b"%PDF-"):
            raise DownloadError(f"Not a PDF: {url}")

        digest = sha256_bytes(response.content)
        if digest in seen_hashes:
            manifest.append(
                DownloadManifestEntry(
                    url=url,
                    filename=filename,
                    sha256=digest,
                    bytes=len(response.content),
                    downloaded_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    skipped=True,
                    skip_reason="duplicate_content_hash",
                ).model_dump()
            )
            continue

        destination.write_bytes(response.content)
        seen_hashes.add(digest)
        manifest.append(
            DownloadManifestEntry(
                url=url,
                filename=filename,
                sha256=sha256_file(destination),
                bytes=destination.stat().st_size,
                downloaded_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            ).model_dump()
        )

    write_json(manifest_path, manifest)
    return manifest
