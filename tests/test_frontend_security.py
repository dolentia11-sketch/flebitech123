import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "public" / "index.html"
APP_JS = ROOT / "public" / "assets" / "app.js"
APP_CSS = ROOT / "public" / "assets" / "app.css"
FAVICON = ROOT / "public" / "favicon.svg"

def test_frontend_uses_strict_script_controls_without_inline_handlers():
    html = INDEX_HTML.read_text(encoding="utf-8")
    app_js = APP_JS.read_text(encoding="utf-8")

    assert not re.search(r"\son(?:click|input|submit)=", html, flags=re.IGNORECASE)
    assert "DOMPurify.sanitize" in app_js
    assert "marked@15.0.7/marked.min.js" in html
    assert "dompurify@3.2.6/dist/purify.min.js" in html
    assert html.count('integrity="sha384-') == 3
    assert "script-src 'self'" in html
    assert "'unsafe-inline'" not in re.search(
        r'script-src ([^"]+)', html
    ).group(1)


def test_frontend_uses_local_compiled_css_and_strict_style_policy():
    html = INDEX_HTML.read_text(encoding="utf-8")
    css = APP_CSS.read_text(encoding="utf-8")
    app_js = APP_JS.read_text(encoding="utf-8")

    assert 'href="/assets/app.css"' in html
    assert "cdn.tailwindcss.com" not in html
    assert "tailwind.config.js" not in html
    assert not re.search(r"\sstyle=", html, flags=re.IGNORECASE)
    assert not re.search(r"\sstyle=", app_js, flags=re.IGNORECASE)
    assert "'unsafe-inline'" not in re.search(
        r'style-src ([^"]+)', html
    ).group(1)
    assert len(css) > 10_000
    assert ".bg-brand-700" in css
    assert ".lg\\:block" in css
    assert ".bg-white\\/90" in css
    assert ".border-brand-100" in css
    assert ".h-12" in css
    assert ".max-w-\\[85\\%\\]" in css
    assert ".rounded-3xl" in css
    assert ".shadow-inner" in css
    assert ".w-12" in css
    assert ".no-scrollbar" in css
    assert "@tailwind" not in css
    assert 'href="/favicon.svg"' in html
    assert FAVICON.is_file()


def test_vercel_applies_security_headers_without_breaking_the_widget():
    html = INDEX_HTML.read_text(encoding="utf-8")
    config = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    headers = config["headers"][0]["headers"]
    header_names = {header["key"] for header in headers}
    csp_header = next(
        header["value"] for header in headers if header["key"] == "Content-Security-Policy"
    )
    csp_meta = re.search(
        r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">', html
    ).group(1)

    assert {"Content-Security-Policy", "X-Content-Type-Options", "Referrer-Policy", "Permissions-Policy"} <= header_names
    assert "X-Frame-Options" not in header_names
    assert csp_header == csp_meta
    assert "https://cdn.tailwindcss.com" not in csp_header
    assert "style-src 'self' https://cdnjs.cloudflare.com https://fonts.googleapis.com" in csp_header
    assert "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com" in csp_header
