import base64
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "public" / "index.html"


def _inline_script_hashes(html: str) -> list[str]:
    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    return [
        "sha256-"
        + base64.b64encode(hashlib.sha256(script.replace("\r\n", "\n").encode()).digest()).decode()
        for script in scripts
    ]


def test_frontend_uses_strict_script_controls_without_inline_handlers():
    html = INDEX_HTML.read_text(encoding="utf-8")

    assert not re.search(r"\son(?:click|input|submit)=", html, flags=re.IGNORECASE)
    assert "DOMPurify.sanitize" in html
    assert "marked@15.0.7/marked.min.js" in html
    assert html.count('integrity="sha384-') == 4
    assert "script-src 'self'" in html
    assert "'unsafe-inline'" not in re.search(
        r'script-src ([^"]+)', html
    ).group(1)


def test_csp_authorizes_only_the_two_known_inline_scripts():
    html = INDEX_HTML.read_text(encoding="utf-8")
    expected_hashes = _inline_script_hashes(html)
    csp = re.search(r'Content-Security-Policy" content="([^"]+)"', html).group(1)

    assert len(expected_hashes) == 2
    for script_hash in expected_hashes:
        assert script_hash in csp


def test_vercel_applies_security_headers_without_breaking_the_widget():
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    headers = config["headers"][0]["headers"]
    header_names = {header["key"] for header in headers}

    assert {"Content-Security-Policy", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy"} <= header_names
    assert "X-Frame-Options" not in header_names
