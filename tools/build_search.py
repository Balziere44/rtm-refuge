# -*- coding: utf-8 -*-
"""Build the site search index.

    python tools/build_search.py

Runs after everything else, because it reads the pages the other scripts
produced as well as the source data. Rows are arrays rather than objects
because there are thousands of them and the key names would be most of the
file.

    {"groups": ["page", "class", "section", "skill", "dungeon"],
     "rows": [["Title", "Subtitle", "url.html#anchor", groupIndex, "extra words"]]}
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import classes_meta as M
import data as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = json.load(open(os.path.join(ROOT, "tools", "data", "wiki.json"), encoding="utf-8"))
ENCY = json.load(open(os.path.join(ROOT, "tools", "data", "encyclopedia.json"),
                      encoding="utf-8"))["classes"]

GROUPS = ["page", "class", "section", "skill", "dungeon"]
G = {name: i for i, name in enumerate(GROUPS)}

TITLE = re.compile(r"<title>(.*?)</title>", re.S)
DESC = re.compile(r'<meta name="description" content="(.*?)">', re.S)
# Section headings on the reference pages carry the id the TOC links to.
SECTION = re.compile(r'<section id="([^"]+)">\s*<h2>(.*?)</h2>\s*<p>(.*?)</p>', re.S)


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def root_pages():
    for name in sorted(os.listdir(ROOT)):
        if name.endswith(".html") and name != "404.html":
            yield name


def main():
    rows = []
    seen = set()

    def add(title, sub, url, group, extra=""):
        key = (title, url)
        if key in seen:
            return
        seen.add(key)
        rows.append([title, sub, url, G[group], extra])

    # 1. Every page, by its own title and description.
    for name in root_pages():
        src = open(os.path.join(ROOT, name), encoding="utf-8").read()
        t = TITLE.search(src)
        d = DESC.search(src)
        title = strip(t.group(1)).split(" | ")[0] if t else name
        add(title, strip(d.group(1)) if d else "", name, "page")

        # 2. Every numbered section of a reference page.
        for sid, head, lede in SECTION.findall(src):
            add(strip(head), strip(lede)[:120], "%s#%s" % (name, sid), "section", title)

    # 3. Every class.
    for meta in M.CLASSES:
        name = M.NAMES.get(meta["slug"], meta["slug"])
        add(name, meta["tagline"], "classes/%s.html" % meta["slug"], "class",
            M.TIER_LABEL[meta["tier"]])

    # 4. Every skill, pointing at the class page that documents it. A skill
    #    name is the single most likely thing somebody types into this box,
    #    so this has to index the names the pages actually print - the game's
    #    own - and fall back to the wiki only where the pages do.
    for meta in M.CLASSES:
        slug = meta["slug"]
        entry = ENCY.get(slug)
        if entry and entry["skills"]:
            for sk in entry["skills"]:
                add(sk["name"], sk["desc"].split("\n")[0],
                    "classes/%s.html#skills" % slug, "skill",
                    M.NAMES.get(slug, "") + " " + (sk.get("type") or ""))
            continue

        page = meta.get("page")
        if not page or page not in WIKI:
            continue
        want = meta.get("section")
        for sec in WIKI[page]["sections"]:
            if want and not (sec["title"] == want or sec["title"].startswith(want + " ")):
                continue
            for sk in sec["skills"]:
                add(sk["name"], sk["desc"],
                    "classes/%s.html#skills" % slug, "skill",
                    M.NAMES.get(slug, "") + " " + (sk.get("type") or ""))

    # 5. Every dungeon.
    for name, lv, rank, where in D.DUNGEONS:
        add(name, "Level %s, rank %s. %s" % (lv, rank, where),
            "world.html#distortions", "dungeon", "distortion dungeon")

    out = {"groups": GROUPS, "rows": rows}
    path = os.path.join(ROOT, "assets", "data", "search.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")

    counts = {}
    for r in rows:
        counts[GROUPS[r[3]]] = counts.get(GROUPS[r[3]], 0) + 1
    print("  wrote assets/data/search.json - %d rows (%s), %d kb" % (
        len(rows), ", ".join("%s %d" % kv for kv in sorted(counts.items())),
        os.path.getsize(path) // 1024))


if __name__ == "__main__":
    print("building search index")
    main()
