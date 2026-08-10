# -*- coding: utf-8 -*-
"""Validate the generated site. Run before every commit.

    python tools/check.py

Exits non-zero listing what is wrong. This is what keeps ten pages consistent
without reading ten pages.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chrome as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TITLE_MAX = 65
DESC_MIN, DESC_MAX = 70, 175

# Brand and product names belonging to other people. The project is a fan
# work with no affiliation to anyone, and the copy is written so that it
# cannot be mistaken for an official channel. This check is what stops a
# well-meaning edit from quietly reintroducing one.
FORBIDDEN = [
    "ragnarok",
    "gravity co",
    "gravity interactive",
    "kro ", "iro ",
    "—",  # em dash: house style uses a plain hyphen or a rewrite
]

problems = []


def fail(name, msg):
    problems.append("%s: %s" % (name, msg))


def html_files():
    out = sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))
    sub = os.path.join(ROOT, "classes")
    if os.path.isdir(sub):
        out += ["classes/" + f for f in sorted(os.listdir(sub)) if f.endswith(".html")]
    return out


def main():
    files = html_files()
    if not files:
        fail("*", "no HTML found - run tools/build.py first")

    anchors = {}
    for name in files:
        raw = open(os.path.join(ROOT, name.replace("/", os.sep)), "rb").read()
        if b"\r\n" in raw:
            fail(name, "CRLF line endings")
        src = raw.decode("utf-8")
        low = src.lower()

        for term in FORBIDDEN:
            if term in low:
                fail(name, "contains forbidden term %r" % term)

        h1 = re.findall(r"<h1[ >]", src)
        if len(h1) != 1:
            fail(name, "expected exactly one <h1>, found %d" % len(h1))

        t = re.search(r"<title>(.*?)</title>", src, re.S)
        if not t:
            fail(name, "no <title>")
        elif len(t.group(1)) > TITLE_MAX:
            fail(name, "title is %d chars (max %d)" % (len(t.group(1)), TITLE_MAX))

        d = re.search(r'<meta name="description" content="(.*?)">', src, re.S)
        if not d:
            fail(name, "no meta description")
        else:
            n = len(d.group(1))
            if not (DESC_MIN <= n <= DESC_MAX):
                fail(name, "description is %d chars (want %d-%d)" % (n, DESC_MIN, DESC_MAX))

        if '<link rel="canonical"' not in src:
            fail(name, "no canonical link")

        for tag in re.findall(r"<img\b[^>]*>", src):
            if "alt=" not in tag:
                fail(name, "img without alt: %s" % tag[:70])
            if "width=" not in tag or "height=" not in tag:
                fail(name, "img without explicit size: %s" % tag[:70])

        anchors[name] = set(re.findall(r'\bid="([^"]+)"', src))

    # Internal links: the file has to exist, and #fragments have to exist in it.
    for name in files:
        src = open(os.path.join(ROOT, name.replace("/", os.sep)), encoding="utf-8").read()
        for href in re.findall(r'href="([^"]+)"', src):
            if href.startswith(("http", "mailto:", "#", "//")):
                if href.startswith("#") and href[1:] not in anchors[name]:
                    fail(name, "dead fragment %s" % href)
                continue
            target, _, frag = href.partition("#")
            if not target:
                continue
            base = os.path.dirname(name)
            resolved = os.path.normpath(os.path.join(base, target)).replace(os.sep, "/")
            if not os.path.exists(os.path.join(ROOT, resolved.replace("/", os.sep))):
                fail(name, "link to missing file: %s" % target)
            elif frag and target.endswith(".html") and frag not in anchors.get(resolved, set()):
                fail(name, "link to missing anchor: %s" % href)

    for required in ("sitemap.xml", "robots.txt", "llms.txt", "_headers",
                     "site.webmanifest", "assets/css/style.css", "assets/js/main.js",
                     "assets/social/og-cover.jpg"):
        if not os.path.exists(os.path.join(ROOT, required)):
            fail(required, "missing")

    sm = os.path.join(ROOT, "sitemap.xml")
    if os.path.exists(sm):
        listed = set(re.findall(r"<loc>%s/([^<]*)</loc>" % re.escape(C.SITE),
                                open(sm, encoding="utf-8").read()))
        expected = set("" if f == "index.html" else f
                       for f in files if f != "404.html")
        for miss in sorted(expected - listed):
            fail("sitemap.xml", "page not listed: %s" % (miss or "index.html"))
        for extra in sorted(listed - expected):
            fail("sitemap.xml", "lists a page that does not exist: %s" % extra)

    if problems:
        print("%d problem(s):" % len(problems))
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("ok - %d pages checked, nothing to report" % len(files))


if __name__ == "__main__":
    main()
