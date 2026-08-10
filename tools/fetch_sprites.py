# -*- coding: utf-8 -*-
"""Vendor the monster sprites.

    python tools/fetch_sprites.py

The sprites live in the team's own asset repository. They are copied in here
rather than hotlinked for two reasons: a page that renders seven hundred
images should not depend on somebody else's Pages deployment staying up, and
served from our own origin they get our cache headers instead of GitHub's.

Only the monsters that actually appear in the database are fetched. Run it
after fetch_encyclopedia.py; it reads the monster list from there.
"""

import io
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = "https://crosscutunion99-ops.github.io/RTMInternalE/sprites/%s.gif"
OUT = os.path.join(ROOT, "assets", "sprites")
UA = {"User-Agent": "Mozilla/5.0 (rtm-refuge site build)"}


def main():
    data = json.load(io.open(os.path.join(HERE, "data", "encyclopedia.json"),
                             encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)

    ids = sorted({m["id"] for m in data["mobs"]})
    got, skipped, missing = 0, 0, []

    for mob_id in ids:
        dest = os.path.join(OUT, "%d.gif" % mob_id)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            skipped += 1
            continue
        try:
            req = urllib.request.Request(SRC % mob_id, headers=UA)
            blob = urllib.request.urlopen(req, timeout=30).read()
        except urllib.error.HTTPError as err:
            if err.code == 404:
                missing.append(mob_id)
                continue
            raise
        with open(dest, "wb") as fh:
            fh.write(blob)
        got += 1
        if got % 50 == 0:
            print("  %d fetched" % got)
            time.sleep(0.2)

    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print("sprites: %d new, %d already here, %d not published - %d kb total"
          % (got, skipped, len(missing), total // 1024))
    if missing:
        print("  no sprite for: %s" % ", ".join(str(m) for m in missing))


if __name__ == "__main__":
    sys.exit(main())
