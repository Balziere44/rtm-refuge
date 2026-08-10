# -*- coding: utf-8 -*-
"""Download the community wiki for the original world and parse it to JSON.

    python tools/fetch_wiki.py

This is the only script that touches the network, and it is not part of a
normal build. It writes tools/data/wiki.json, which is committed, so the site
builds offline and a re-fetch shows up as a readable diff of what the wiki
actually changed.

The wiki documents the world the Refuge inherited. It does not know about
anything the Refuge changed - those corrections live in tools/classes_meta.py
and tools/data.py and are rendered as explicit callouts, never silently merged.
"""

import glob
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "raw")
OUT = os.path.join(HERE, "data", "wiki.json")

WIKI = "https://wiki.echoesofmorroc.org/index.php?title=%s&action=raw"
UA = {"User-Agent": "Mozilla/5.0 (compatible; rtm-refuge-site/1.0)"}

PAGES = """
Accessories Achievements Arcanemaster Armors Assassin Base_Aspd_Limit_Table Bifrost_Mirror
Black_Market Black_Plague Blast_Juggler Card_System Cards_Armor Cards_Headgear Combat_Reworked
Combos/Rotations Costume Darkknight Distortion_Dungeons Dracomancer Dream_Enchantments
Einherjar_Equipment Elemental_Table Garment Gravekeeper Grimoire_of_New-Midgard HATred_Quests
Headgears Illusionist Innate_Fixed_Bonus Instance_List Jester Job_Classes Job_Quests Job_Sets
Judge Judge_Headquarters Kafra_Services Kingslayer Legend MVP_System Main_Features Main_Page
Main_Story_Quest Mimic NPC_Equipment New_Player_Guide Night_Raven Orphan Paradox_seasons
Peacekeeper Prowler Raider Random_Options Ranking_System Refine_System Regions_and_Dungeons
Revenant Rogue Ronin Runes Satsujin Shadow_Sets Shadow_System Shadowseer Shields Sinner
Specializations Stat_Changes Systems_and_Exchanges The_Orphanage Thief Trickster
Unchained_Evolutions Unique_Bonuses Vagabond Weapons World_Changes
""".split()


# ---------------------------------------------------------------------------
# fetch
# ---------------------------------------------------------------------------

def fetch():
    os.makedirs(RAW, exist_ok=True)
    got = 0
    for page in PAGES:
        path = os.path.join(RAW, page.replace("/", "_") + ".txt")
        if os.path.exists(path) and os.path.getsize(path):
            continue
        try:
            req = urllib.request.Request(WIKI % page, headers=UA)
            body = urllib.request.urlopen(req, timeout=30).read()
            open(path, "wb").write(body)
            got += 1
        except Exception as exc:                     # noqa: BLE001 - report and continue
            print("  FAILED", page, exc)
        time.sleep(0.15)
    print("  fetched", got, "new pages into data/raw")


# ---------------------------------------------------------------------------
# parse
# ---------------------------------------------------------------------------

# The wiki is hand-written by players and carries the usual typos. Fixing them
# here rather than in data/raw keeps the next fetch from silently undoing the
# corrections, and keeps the list reviewable.
TYPOS = [
    ("Unqiue", "Unique"), ("unqiue", "unique"), ("Unqique", "Unique"),
    ("excells", "excels"), ("Skill celling", "skill ceiling"), ("celling", "ceiling"),
    ("Ronis ", "Ronin "), ("alot", "a lot"), ("continious", "continuous"),
    ("weilding", "wielding"), ("denstity", "density"), ("effectivnes", "effectiveness"),
    ("Nifflheim", "Niflheim"), ("Protera", "Prontera"), ("Chaning", "Changing"),
    ("procced", "proceed"), ("Depeding", "Depending"), ("recieve", "receive"),
    ("Ressurection", "Resurrection"), ("ressurection", "resurrection"),
    ("possibilites", "possibilities"), ("abilites", "abilities"),
    ("Adventureres", "Adventurers"), ("Improvments", "Improvements"),
    ("no longers", "no longer"), ("sropho", "Sropho"),
]


# The wiki names a publisher's trademark in a handful of sentences. This site
# is an unaffiliated fan project and deliberately does not reproduce it (see
# README, "Content and naming policy"), so those sentences are rewritten to
# say the same thing in generic terms. tools/check.py fails the build if one
# slips through, which is how this list stays honest.
SCRUB = [
    # Table-of-contents markers and bare media embeds are markup, not prose.
    ("__TOC__", ""),
    ("__NOTOC__", ""),
    ("refined Ragnarok Online experience", "refined take on the classic experience"),
    ("familiar with classic Ragnarok Online mechanics", "familiar with classic MMO mechanics"),
    ("for Classic Ragnarok players", "for players of the classic game"),
    ("a core part of the ragnarok experience", "a core part of the classic experience"),
    ("Ragnarok Online", "the original game"),
    ("Ragnarok", "the original game"),
    ("ragnarok", "the original game"),
    # "RO" appears bare in about a dozen sentences. Each phrasing needs its
    # own replacement or the grammar breaks - "vanilla RO Paladin" must not
    # become "vanilla the original game Paladin".
    ("original RO's", "the original game's"),
    ("original RO", "the original game"),
    ("Original Ro", "the original game"),
    ("Vanilla RO", "Classic"),
    ("vanilla RO", "classic"),
    ("classic RO", "the classic game"),
    ("found in RO.", "found in the original game."),
    ("Destruction of Morroc - RO", "Destruction of Morroc"),
    ("from renewal", "from the modern version"),
]


def plain(s):
    """Wikitext to readable text. Images go, links keep their label."""
    for wrong, right in TYPOS:
        s = s.replace(wrong, right)
    for term, replacement in SCRUB:
        s = s.replace(term, replacement)
    # External wiki links point at the other successor server. Keep the label,
    # drop the destination: this site does not link to a competitor, and the
    # words themselves describe the shared world.
    s = re.sub(r"\[https?://[^\s\]]+\s+([^\]]+)\]", r"\1", s)
    s = re.sub(r"\[https?://[^\s\]]+\]", "", s)
    s = re.sub(r"https?://\S*echoesofmorroc\S*", "", s)
    s = re.sub(r"\[\[File:[^\]]*\]\]", "", s)
    s = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]+)\]\]", r"\1", s)
    s = re.sub(r"'''(.+?)'''", r"\1", s)
    s = re.sub(r"''(.+?)''", r"\1", s)
    s = re.sub(r"</?[a-z][^>]*>", " ", s, flags=re.I)
    s = s.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()


def parse_table(table):
    """Six-column skill tables. Anything else returns nothing."""
    rows = []
    if "Max Level" not in table:
        return rows
    for row in table.split("\n|-")[1:]:
        cells = []
        for cell in re.split(r"\n\|(?!\})", row):
            cell = cell.strip()
            if not cell or cell[0] in "!}":
                continue
            cell = re.sub(r'^[^|\n]*style="[^"]*"\s*\|', "", cell)
            cell = plain(cell)
            if cell:
                cells.append(cell)
        if len(cells) >= 3 and re.match(r"^Lv\s*\d+$", cells[1], re.I):
            rows.append({
                "name": cells[0], "max": cells[1], "desc": cells[2],
                "type": cells[3] if len(cells) > 3 else "",
                "details": cells[4] if len(cells) > 4 else "",
                "scaling": cells[5] if len(cells) > 5 else "",
            })
    return rows


# Some pages simply run off the end without closing their table, so
# end-of-page counts as a terminator.
TABLE = re.compile(r"\{\|.*?(?:\n\|\}|\Z)", re.S)
HEADING = re.compile(r"^(=+)\s*(.+?)\s*=+\s*$")


def parse_page(path):
    raw = open(path, encoding="utf-8", errors="ignore").read()
    name = os.path.basename(path)[:-4]

    # Walk the page top to bottom so prose, bullets and skill tables all end
    # up attributed to the heading they appear under. A flat list of skills is
    # useless for pages that document eight classes at once.
    sections = [{"title": "", "level": 1, "paras": [], "bullets": [], "skills": []}]
    pos = 0
    for m in TABLE.finditer(raw):
        _text_run(raw[pos:m.start()], sections)
        sections[-1]["skills"].extend(parse_table(m.group(0)))
        pos = m.end()
    _text_run(raw[pos:], sections)

    out = {"page": name,
           "sections": [s for s in sections if s["paras"] or s["bullets"] or s["skills"]]}
    for key, label in (("best", "Best"), ("worst", "Worst"),
                       ("weapons", "Weapons"), ("note", "Note")):
        m = re.search(r"'''%s:'''\s*(.+)" % label, raw)
        if m:
            out[key] = plain(m.group(1))
    return out


def _text_run(chunk, sections):
    for line in chunk.split("\n"):
        line = line.rstrip()
        if not line.strip():
            continue
        h = HEADING.match(line.strip())
        if h:
            sections.append({"title": plain(h.group(2)), "level": len(h.group(1)),
                             "paras": [], "bullets": [], "skills": []})
            continue
        if line.lstrip()[0] in "|!{":
            continue
        if line.lstrip()[0] in "*#:":
            t = plain(line.lstrip("*#: "))
            if t:
                sections[-1]["bullets"].append(t)
        else:
            t = plain(line)
            if t and not re.match(r"^(Best|Worst|Weapons|Note):", t):
                sections[-1]["paras"].append(t)


def parse_all():
    data = {}
    for path in sorted(glob.glob(os.path.join(RAW, "*.txt"))):
        page = parse_page(path)
        data[page["page"]] = page
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    skills = sum(len(s["skills"]) for p in data.values() for s in p["sections"])
    print("  parsed %d pages, %d skill rows -> data/wiki.json" % (len(data), skills))
    return data


if __name__ == "__main__":
    if "--parse-only" not in sys.argv:
        fetch()
    parse_all()
