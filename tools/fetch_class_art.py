# -*- coding: utf-8 -*-
"""Fetch the job sprites for every class into assets/img/classes/.

    python tools/fetch_class_art.py

Two files per class, because the source publishes two useful things:

    <slug>.png        the standing sprite, an animated PNG - six frames of
                      idle. This is the one on the class page.
    <slug>-still.png  the sitting sprite, a single frame. This is the one in
                      the tree, where 39 of them share a screen and 39
                      simultaneous loops would be a lot to look at, and the
                      one shown to anyone who asked the OS for less motion.

An APNG cannot be paused from CSS, so having the still frame as a separate
file is what makes prefers-reduced-motion possible at all.

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


def candidates(slug, pose):
    """Male first, then female - whichever of the two the source published."""
    s = their_slug(slug)
    for sex in ("m", "f"):
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


def frames(blob):
    """Animated PNGs carry an acTL chunk saying how many frames they have."""
    i = blob.find(b"acTL")
    return int.from_bytes(blob[i + 4:i + 8], "big") if i > 0 else 1


def fetch(slug, pose, suffix):
    dest = os.path.join(OUT, slug + suffix + ".png")
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        with open(dest, "rb") as fh:
            return "cached (%d frames)" % frames(fh.read())

    for url in candidates(slug, pose):
        blob = get(url)
        if blob:
            with open(dest, "wb") as fh:
                fh.write(blob)
            return "%s, %d frames, %d kb" % (
                url.rsplit("/", 1)[-1], frames(blob), len(blob) // 1024)
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    found, missing, still_only = [], [], []

    for meta in M.CLASSES:
        slug = meta["slug"]
        moving = fetch(slug, "", "")
        still = fetch(slug, "_sit", "-still")

        if moving:
            found.append((slug, moving))
            if not still:
                still_only.append(slug)
        elif still:
            # No animation published: the still frame stands in for both, so
            # the page has something rather than a gap.
            os.replace(os.path.join(OUT, slug + "-still.png"),
                       os.path.join(OUT, slug + ".png"))
            found.append((slug, "still only"))
        else:
            missing.append(slug)

    print("class art: %d classes, %d missing" % (len(found), len(missing)))
    for slug, what in found:
        print("  %-20s %s" % (slug, what))
    if still_only:
        print("  no still frame, will animate in the tree too: %s"
              % ", ".join(still_only))
    if missing:
        print("  no sprite published for: %s" % ", ".join(missing))
    return 0


if __name__ == "__main__":
    sys.exit(main())
