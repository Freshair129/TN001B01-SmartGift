"""Assemble the upload folder for the SmartGift back office.

The back office is `public/internal.html` — the same static page as the public
catalog plus the Landed Cost Engine, BOM cascade and governance views. It is
shipped as its own docroot (not a folder inside the public site) so the two can
never leak into each other, and it carries an .htaccess that refuses to serve
anything until a password file exists.

    python scripts/build_backend.py            # -> dist/backend/
    python scripts/build_backend.py --out X    # somewhere else
"""
import argparse
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "public"

# internal.html becomes the docroot index; the public catalog is NOT included
FILES = {
    "internal.html": "index.html",
    "customer-catalog.css": "customer-catalog.css",
    "customer-catalog.js": "customer-catalog.js",
    "gift-anatomy-25d.js": "gift-anatomy-25d.js",
    "gift-anatomy-3d.js": "gift-anatomy-3d.js",
}
DIRS = ["data", "assets"]

HTACCESS = """# SmartGift back office — private.
# This page exposes the landed-cost formula and the corporate markup, so it is
# refused outright until a password file is in place.

Options -Indexes
DirectoryIndex index.html

AuthType Basic
AuthName "SmartGift Back Office"
# Point this at the .htpasswd that DirectAdmin writes for you:
#   DirectAdmin -> Advanced -> Password Protected Directories
# then replace the path below with the one it reports. Never keep the password
# file inside public_html.
AuthUserFile /home/CHANGE_ME/.htpasswds/backoffice/.htpasswd
Require valid-user

<IfModule mod_mime.c>
  AddType image/webp        .webp
  AddType model/gltf-binary .glb
  AddType application/json  .json
</IfModule>

<IfModule mod_headers.c>
  Header set X-Robots-Tag "noindex, nofollow, noarchive"
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "no-referrer"
</IfModule>
"""

ROBOTS = "User-agent: *\nDisallow: /\n"


def build(out: pathlib.Path) -> pathlib.Path:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for src_name, dst_name in FILES.items():
        src = SRC / src_name
        if src.exists():
            shutil.copy2(src, out / dst_name)

    for d in DIRS:
        src = SRC / d
        if src.exists():
            shutil.copytree(src, out / d)

    (out / ".htaccess").write_text(HTACCESS, encoding="utf-8")
    (out / "robots.txt").write_text(ROBOTS, encoding="utf-8")

    files = [p for p in out.rglob("*") if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    print(f"{out}  {len(files)} files  {size / 1024 / 1024:.1f} MB")
    print("upload the CONTENTS of this folder to the back-office docroot,")
    print("then set the password in DirectAdmin -> Password Protected Directories")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "dist" / "backend"))
    build(pathlib.Path(ap.parse_args().out))
