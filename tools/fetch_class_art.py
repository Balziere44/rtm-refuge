# -*- coding: utf-8 -*-
"""Fetch the job sprite for every class into assets/img/classes/.

    python tools/fetch_class_art.py

The source publishes one sprite per class under a predictable path, in four
variants - male and female, standing and sitting - and not every class has all
four. This probes them in a fixed order and keeps the first that exists, so a
class always gets the same sprite on every run.

Nothing here is wired into build.py: the images are committed, and the build
must not depend on a third party being reachable.
"""

import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import classes_meta as M

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "img", "classes")
BASE = "https://echoesofmorroc.org/classes-normalized"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Their slug is ours with the hyphens taken out, except where it is not.
OVERRIDE = {
    "dark-knight": "darkknight",
}


def their_slug(slug):
    return OVERRIDE.get(slug, slug.replace("-", ""))


def candidates(slug):
    """Sitting first: it is the pose the source itself leads with."""
    s = their_slug(slug)
    for sex in ("m", "f"):
        for pose in ("_sit", ""):
            yield "%s/%s/%s_%s%s.png" % (BASE, s, sex, s, pose)


def get(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.status != 200:
                return None
            blob = r.read()
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
        return None
    # A single-page app can answer any path with its HTML shell, so trust the
    # bytes rather than the status code.
    return blob if blob[:8] == b"\x89PNG\r\n\x1a\n" else None


def main():
    os.makedirs(OUT, exist_ok=True)
    found, missing = [], []

    for meta in M.CLASSES:
        slug = meta["slug"]
        dest = os.path.join(OUT, slug + ".png")
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            found.append((slug, "cached"))
            continue

        for url in candidates(slug):
            blob = get(url)
            if blob:
                with open(dest, "wb") as fh:
                    fh.write(blob)
                found.append((slug, url.rsplit("/", 1)[-1]))
                break
        else:
            missing.append(slug)

    print("class art: %d found, %d missing" % (len(found), len(missing)))
    for slug, what in found:
        print("  %-20s %s" % (slug, what))
    if missing:
        print("  no sprite published for: %s" % ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
