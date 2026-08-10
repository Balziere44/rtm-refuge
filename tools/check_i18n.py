# -*- coding: utf-8 -*-
"""Compare the keys used in the markup against each locale file.

    python tools/check_i18n.py

A missing key does not break the page - the runtime falls back to the English
snapshot - which is exactly why it needs a checker. Silent fallback means a
half-translated site looks fine to whoever wrote the English.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES = os.path.join(ROOT, "assets", "i18n")

USED = re.compile(r'data-i18n="([^"]+)"')
USED_ATTR = re.compile(r'data-i18n-attr="([^"]+)"')
DEFINED = re.compile(r"^\s*'([^']+)':", re.M)


def html_files():
    out = [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".html")]
    sub = os.path.join(ROOT, "classes")
    if os.path.isdir(sub):
        out += [os.path.join(sub, f) for f in os.listdir(sub) if f.endswith(".html")]
    js = os.path.join(ROOT, "assets", "js")
    out += [os.path.join(js, f) for f in os.listdir(js) if f.endswith(".js")]
    return out


def main():
    used = set()
    for path in html_files():
        src = open(path, encoding="utf-8").read()
        used.update(USED.findall(src))
        for group in USED_ATTR.findall(src):
            for pair in group.split(","):
                bits = pair.split(":")
                if len(bits) > 1 and bits[1].strip():
                    used.add(bits[1].strip())

    if not os.path.isdir(LOCALES):
        print("no locales directory - nothing to check")
        return

    problems = 0
    for name in sorted(os.listdir(LOCALES)):
        if not name.endswith(".js"):
            continue
        code = name[:-3]
        src = open(os.path.join(LOCALES, name), encoding="utf-8").read()
        have = set(DEFINED.findall(src))
        missing = sorted(used - have)
        extra = sorted(have - used)
        print("%s: %d/%d keys" % (code, len(have & used), len(used)))
        for key in missing:
            print("  MISSING", key)
            problems += 1
        for key in extra:
            # Not fatal: a key can be defined ahead of the markup that uses it.
            print("  unused ", key)

    if problems:
        sys.exit(1)
    print("ok - every key used in the markup is translated")


if __name__ == "__main__":
    main()
