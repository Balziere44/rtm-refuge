# -*- coding: utf-8 -*-
"""Pull the team's internal encyclopedia into tools/data/encyclopedia.json.

    python tools/fetch_encyclopedia.py

The internal tool the staff use to balance the game carries the curated data:
the names players actually see, the in-game item descriptions, the category
each item is filed under, and every drop with its zone and rate. That is a
better source than the emulator's own tables, which carry rAthena bonus
scripts where a description should be.

The tool ships as one HTML file with a bundler manifest - a map of gzipped,
base64'd resources keyed by uuid. Two of those resources are the data files;
the rest is React, fonts, and the staff-only parts of the tool, which are not
wanted here and are not written out.

The output is committed, so building the site never touches the network.
"""

import base64
import gzip
import io
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "https://rtm-internal-e.vercel.app/"
OUT = os.path.join(HERE, "data", "encyclopedia.json")
UA = {"User-Agent": "Mozilla/5.0 (rtm-refuge site build)"}


def resources(html):
    """Every text resource in the bundler manifest, decompressed."""
    start = html.index('<script type="__bundler/manifest">')
    body = html[html.index(">", start) + 1:html.index("</script>", start)]
    for blob in json.loads(body).values():
        if not blob["mime"].endswith(("javascript", "json", "plain")):
            continue
        raw = base64.b64decode(blob["data"])
        if blob.get("compressed"):
            raw = gzip.decompress(raw)
        yield raw.decode("utf-8", "replace")


def literal(text, name):
    """The value assigned to `const NAME = ...` in a resource."""
    head = "const %s=" % name
    if not text.startswith(head):
        return None
    return json.loads(text[len(head):].strip().rstrip(";"))


# The description the game shows opens with the skill's own name and two
# fields that are already columns in the table, then sometimes labels the rest
# "Description:". None of that is worth printing twice.
SKILL_RULE = re.compile(r"^[=_\-~\s]+$")
SKILL_DROP = re.compile(r"^(max level|skill form|skill type|level|type)\s*:",
                        re.I)


# A line that is really a scaling table: "Bonus is 3 Atk and 1% ASPD per
# level", "Duration is 10 seconds per level", "Maximum ASPD is 180". These
# move with every balance pass, so they belong in the wiki where they can be
# corrected the day they change - not baked into a static page that will go
# quietly stale. What stays is the sentence that says what the skill does.
SKILL_NUMBERS = re.compile(
    r"per (?:level|lv|refine)\b|\d+\s*%|\bis \d|\+\d|\d+\s*second|"
    r"\d+\s*sec\b|\bLv\s*\d|\bcooldown\b.*\d|\d+\s*/\s*\d", re.I)

# The same idea without any digits in it: "Recovers (skill level x Base Level)
# x (N) as HP". Still a formula, still belongs in the wiki.
SKILL_FORMULA = re.compile(
    r"\bskill level\b|\(N\)|\(\d+\)|\w\s*x\s*\(|\)\s*x\s*\w", re.I)


# A line that ends on one of these is mid-sentence, whatever the next line
# starts with: "Regenerates HP and" / "SP every 5 seconds while sitting."
DANGLING = re.compile(
    r"(,|\band|\bor|\bof|\bto|\bthe|\ba|\ban|\bin|\bby|\bwith|\bfrom|\bfor|"
    r"\bper|\bthan|\bthat|\bwhile|\bwhen)$", re.I)


def clean_skill(desc, name):
    """Split a skill's in-game text into what it does and what it scales by.

    Returns (prose, numbers, target). The prose is what the site prints.
    """
    target = ""
    prose, numbers, last = [], [], None
    for line in (desc or "").split("\n"):
        line = line.replace("\t", " ").strip()
        if not line or SKILL_RULE.match(line):
            if prose and prose[-1] != "":
                prose.append("")
            last = None
            continue
        if line == name or SKILL_DROP.match(line):
            continue
        line = re.sub(r"^Description\s*:\s*", "", line)

        m = re.match(r"^Target\s*:\s*(.+)$", line, re.I)
        if m and not target:
            target = m.group(1).strip()
            last = None
            continue

        # The game hard-wraps at about forty characters, so a sentence can
        # arrive split. A continuation rejoins whichever bucket the line above
        # it went into, or the split leaves half a sentence in each.
        if last and last[-1] and (re.match(r"[a-z]", line)
                                  or DANGLING.search(last[-1])):
            last[-1] = last[-1] + " " + line
            continue

        scaling = (any(ch.isdigit() for ch in line)
                   and SKILL_NUMBERS.search(line)) or SKILL_FORMULA.search(line)
        last = numbers if scaling else prose
        last.append(line)

    # A label with nothing left under it - "Harvest Mode:" whose three lines
    # all turned out to be scaling - is worse than no label at all. This has
    # to run over the whole list, not just the tail: the orphan is usually in
    # the middle, where the next real sentence follows a blank.
    kept = []
    for i, line in enumerate(prose):
        if line == "":
            continue
        if line.endswith(":") and not any(
                p and not p.endswith(":") for p in prose[i + 1:]):
            continue
        kept.append(line)
    prose = kept

    # A handful of skills - mostly the "+" upgrades - describe themselves in
    # one line that happens to carry a level range, so the whole description
    # lands in the numbers bucket. An empty cell is worse than that one line.
    if not prose and numbers:
        prose = [numbers.pop(0)]

    return "\n".join(prose).strip(), "\n".join(numbers).strip(), target


def main():
    req = urllib.request.Request(SRC, headers=UA)
    html = urllib.request.urlopen(req, timeout=90).read().decode("utf-8", "replace")

    items = mobs = classes = None
    for text in resources(html):
        items = literal(text, "ITEMS") or items
        mobs = literal(text, "MOBS") or mobs
        classes = literal(text, "CLASS_DATA_FULL") or classes

    if not items or not mobs:
        print("could not find ITEMS/MOBS in the bundle - the tool's build "
              "layout probably changed", file=sys.stderr)
        return 1

    # The staff tool stores per-item balance notes and a client-side user list.
    # Neither is game data and neither belongs on a public site; the shapes
    # below are the only fields carried across.
    items = [{
        "name": it["name"],
        "category": it.get("category") or "",
        "description": it.get("description") or "",
        "sources": [{
            "id": s.get("mob_id"),
            "name": s.get("mob_name") or "",
            "level": s.get("mob_level") or 0,
            "zone": s.get("mob_zone") or "",
            "mvp": bool(s.get("mob_is_mvp")),
            "pct": s.get("drop_pct") or 0,
        } for s in it.get("sources") or []],
    } for it in items]

    mobs = [{
        "id": m["id"],
        "name": m["name"],
        "level": m.get("level") or 0,
        "hp": m.get("hp") or 0,
        "size": m.get("size") or "",
        "race": m.get("race") or "",
        "element": m.get("element") or "",
        "element_level": m.get("element_level") or 0,
        "mvp": bool(m.get("is_mvp")),
        "zone": m.get("zone") or "",
        "maps": m.get("maps") or [],
        "card_effect": m.get("cardEffect") or "",
        "card_slot": m.get("cardSlot") or "",
        "drops": [{"name": d.get("name") or "", "pct": d.get("pct") or 0}
                  for d in m.get("drops") or []],
    } for m in mobs]

    # The skill list is keyed by the same slug the site already uses for its
    # class pages, with underscores where the site has hyphens.
    skills = {}
    for key, cls in (classes or {}).items():
        skills[key.replace("_", "-")] = {
            "name": cls.get("name") or key,
            "summary": cls.get("desc") or "",
            "skills": [],
        }
        for sk in cls.get("skills") or []:
            prose, numbers, target = clean_skill(sk.get("desc"),
                                                 sk.get("name") or "")
            skills[key.replace("_", "-")]["skills"].append({
                "name": sk.get("name") or "",
                "max": sk.get("maxLv") or 1,
                "type": sk.get("type") or "",
                "needs": sk.get("prereq") or "",
                "target": target,
                # Kept out of the site's pages on purpose - see SKILL_NUMBERS.
                "numbers": numbers,
                "desc": prose,
            })

    items.sort(key=lambda x: x["name"])
    mobs.sort(key=lambda x: x["id"])

    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"items": items, "mobs": mobs, "classes": skills}, fh,
                  ensure_ascii=False, indent=0, sort_keys=True)
        fh.write("\n")

    print("encyclopedia: %d items, %d monsters, %d drop lines, "
          "%d classes with %d skills - %d kb"
          % (len(items), len(mobs),
             sum(len(m["drops"]) for m in mobs),
             len(skills), sum(len(c["skills"]) for c in skills.values()),
             os.path.getsize(OUT) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
