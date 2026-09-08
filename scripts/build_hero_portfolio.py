"""Render the client-portfolio hero from its template.

Two outputs from one source:
  public/hero-portfolio.html  - images by relative path, for the real site
  <scratch>/hero_artifact.html - images inlined as data URIs, for an Artifact
"""
import base64, mimetypes, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TPL = ROOT / "src/web/hero-portfolio.template.html"
ASSETS = ROOT / "public/assets/portfolio/web"
REL = "assets/portfolio/web"


def find(name: str) -> pathlib.Path:
    for ext in (".jpg", ".png"):
        p = ASSETS / f"{name}{ext}"
        if p.exists():
            return p
    raise SystemExit(f"missing asset: {name}")


def render(inline: bool) -> str:
    html = TPL.read_text(encoding="utf-8")

    def sub(m):
        name = m.group(1)
        p = find(name)
        if not inline:
            return f"{REL}/{p.name}"
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"

    return re.sub(r"\{\{IMG:([a-z0-9_]+)\}\}", sub, html)


if __name__ == "__main__":
    out_site = ROOT / "public/hero-portfolio.html"
    out_site.write_text(render(False), encoding="utf-8")
    print(out_site, out_site.stat().st_size)
    if len(sys.argv) > 1:
        out_art = pathlib.Path(sys.argv[1])
        out_art.write_text(render(True), encoding="utf-8")
        print(out_art, out_art.stat().st_size)
