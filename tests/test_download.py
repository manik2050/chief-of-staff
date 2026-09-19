from unittest.mock import patch

from chief_of_staff.download import download_allowlist


def test_download_skips_duplicate_hash(tmp_path):
    pdf = b"%PDF-1.1 minimal"
    dest = tmp_path / "raw"
    manifest = tmp_path / "manifest.json"
    url = "https://example.com/approved-pitch-deck.pdf"

    class Response:
        content = pdf

        def raise_for_status(self):
            return None

    with patch("chief_of_staff.download.requests.get", return_value=Response()):
        first = download_allowlist([url], dest, manifest)
        second = download_allowlist([url], dest, manifest)

    assert first[0]["skipped"] is False
    assert second[-1]["skipped"] is True
    assert second[-1]["skip_reason"] == "duplicate_content_hash"
    assert (dest / "approved-pitch-deck.pdf").exists()
