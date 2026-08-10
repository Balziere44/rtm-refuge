# -*- coding: utf-8 -*-
"""Point the whole site at a different origin.

    python tools/set_domain.py https://refuge.example.com

Rewrites tools/chrome.py and then rebuilds everything, so canonical links,
Open Graph URLs, the sitemap, robots.txt and llms.txt all move together.
Moving domain by hand is how a site ends up telling search engines it lives
somewhere it does not.
"""

import os
import re
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    new = sys.argv[1].rstrip("/")
    if not new.startswith("https://"):
        print("refusing: the origin must start with https://")
        sys.exit(2)

    path = os.path.join(HERE, "chrome.py")
    src = open(path, encoding="utf-8").read()
    src, n = re.subn(r'^SITE = ".*"$', 'SITE = "%s"' % new, src, count=1, flags=re.M)
    if not n:
        print("could not find the SITE line in tools/chrome.py")
        sys.exit(1)
    open(path, "w", encoding="utf-8", newline="\n").write(src)
    print("SITE =", new)

    for script in ("build.py", "build_meta.py"):
        subprocess.check_call([sys.executable, os.path.join(HERE, script)])


if __name__ == "__main__":
    main()
