# -*- coding: utf-8 -*-
"""Build the public database payload and the database page.

    python tools/build_database.py

Reads two sources and prefers the first:

    tools/data/encyclopedia.json   the team's own curated data - the names
                                   players see, the in-game descriptions, the
                                   category each item is filed under, and every
                                   drop with its zone and rate
    tools/data/game.json           the emulator's tables, used only to fill in
                                   numbers the encyclopedia does not carry
                                   (experience, monster attack and defence)

Writes:

    assets/data/db-items.json   every item, as column arrays
    assets/data/db-mobs.json    every monster and what it drops
    database.html               the page shell

Nothing derived from the emulator's `script` column is ever written out. Those
are rAthena bonus expressions - `bonus2 bSkillAtk,"LG_RAYOFGENESIS",4*(.@r)` -
and they are reference material for the wiki, not a description. What a player
reads here is the description the game itself shows them.

Rows are arrays, not objects, and repeated strings (category, slot, zone, job
list, monster name) are indices into small dictionaries. The key names and the
repeated words would otherwise be most of the file.
"""

import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chrome as C

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENCY = os.path.join(HERE, "data", "encyclopedia.json")
GAME = os.path.join(HERE, "data", "game.json")

# ---------------------------------------------------------------------------
# categories
# ---------------------------------------------------------------------------

# The encyclopedia files items under a hundred-odd categories, which is right
# for a person browsing but far too many to put in a filter list. Every one of
# them rolls up into one of these, matched on the first pattern that hits, so
# the coarse filter and the precise label can both be shown.
GROUPS = [
    ("Card", (r"^card$",)),
    ("Shadow gear", (r"shadow",)),
    ("Costume", (r"costume",)),
    ("Shield", (r"shield|buckler",)),
    ("Weapon", (r"sword|dagger|axe|katar|spear|bow|whip|scythe|knuckle|staff|"
                r"revolver|knife|lance|claw|instrument|musical|weapon|"
                r"rapier|mace|gun",)),
    ("Headgear", (r"head",)),
    ("Armor", (r"armor|armour|garment|shoes|robe|mantle",)),
    ("Accessory", (r"accessory|pendant|ring|belt",)),
    # Runes, orbs, decks, codices and cantrips books are all the same kind of
    # thing from a player's side: the piece of kit a particular class carries
    # instead of a second weapon.
    ("Class gear", (r"rune|orb|deck|codex|cantrips|manual|core|book|prowler",)),
    ("Ammunition", (r"^arrow$|^ammo$|bullet|cannonball",)),
    ("Usable", (r"healing|restorative|potion|usable|support|taming|container|"
                r"delayconsume|special",)),
    ("Material", (r"etc|collectible|valuable|material|quest|key|essential|"
                  r"forging|refining",)),
]

# One colour per group, used for the chip on every row. Purely so a list of
# two thousand names has some shape to it at a glance.
GROUP_HUE = {
    "Weapon": "wpn", "Shield": "shd", "Armor": "arm", "Headgear": "hat",
    "Accessory": "acc", "Card": "crd", "Costume": "cos", "Shadow gear": "sha",
    "Class gear": "run", "Ammunition": "amm", "Usable": "use",
    "Material": "mat", "Other": "oth",
}

# The same slot is written four ways across the game's own description text -
# "Mid Headgear", "Middle headgear", "Upper Headgear", "Lower Head". Left
# alone the filter lists each spelling as its own option.
SLOT_ALIAS = {
    "upper head": "Upper headgear", "upper headgear": "Upper headgear",
    "top headgear": "Upper headgear", "head": "Upper headgear",
    "mid head": "Middle headgear", "mid headgear": "Middle headgear",
    "middle head": "Middle headgear", "middle headgear": "Middle headgear",
    "middle": "Middle headgear",
    # "Upper, Mid and Lower Headgear" splits into bare words. In a Location
    # line those only ever mean the headgear rows.
    "upper": "Upper headgear", "mid": "Middle headgear",
    "low": "Lower headgear", "lower": "Lower headgear",
    "acessory": "Accessory",
    "low head": "Lower headgear", "low headgear": "Lower headgear",
    "lower head": "Lower headgear", "lower headgear": "Lower headgear",
    "headgear": "Headgear", "armor": "Armor", "armour": "Armor",
    "garment": "Garment", "shoes": "Shoes", "shield": "Shield",
    "accessory": "Accessory", "left accessory": "Accessory",
    "right accessory": "Accessory", "any slot": "Accessory",
    "weapon": "Weapon", "two-handed": "Weapon (two-handed)",
    "two handed": "Weapon (two-handed)", "off-hand": "Off-hand",
    "offhand": "Off-hand", "ammunition": "Ammunition", "ammo": "Ammunition",
    "shadow weapon": "Shadow weapon", "shadow armor": "Shadow armor",
    "shadow shield": "Shadow shield", "shadow shoes": "Shadow shoes",
    "shadow accessory": "Shadow accessory",
}


def slot_name(raw):
    key = re.sub(r"\s+", " ", raw.strip().lower())
    return SLOT_ALIAS.get(key, raw.strip()[:1].upper() + raw.strip()[1:])


# A zone name is derived from a map file, and map files are numbered by floor:
# Abbey01, Abbey03, Mjolnir 01, Mjolnir 04, Tha para01 through Tha para08. That
# is a hundred and seventeen entries in a filter that is meant to be a list of
# places. The floor is not lost by merging them - every monster's record still
# carries the exact map names it walks on.
ZONE_FLOOR = re.compile(r"[\s_-]*\d+$")

# A handful of prefixes that survive the merge as something nobody would
# recognise. Only the ones the maps themselves make unambiguous.
ZONE_ALIAS = {
    "In sphinx": "Sphinx",
    "C tower": "Clock Tower",
    "Anthell": "Ant Hell",
    "Tha t": "Thanatos Tower",
    "Tha para": "Thanatos Tower",
    "Thana boss": "Thanatos Tower",
    "Jupe core": "Juperos",
    "Juperos": "Juperos",
    "Treasure": "Treasure Room",
    "Treasure Room": "Treasure Room",
}


def zone_name(raw):
    name = (raw or "").strip()
    if not name:
        return "Unknown"
    stem = ZONE_FLOOR.sub("", name) or name
    return ZONE_ALIAS.get(stem, stem)


def clean_label(raw):
    """The encyclopedia has a few categories typed by hand, and one of them is
    "\\Shuffling Deck?". Strip what is clearly a slip of the keyboard."""
    return re.sub(r"^[^\w]+|[^\w)]+$", "", (raw or "").strip()) or "Other"


def group_of(category):
    low = (category or "").lower()
    for name, patterns in GROUPS:
        for pattern in patterns:
            if re.search(pattern, low):
                return name
    return "Other"


# ---------------------------------------------------------------------------
# descriptions
# ---------------------------------------------------------------------------

# Lines the game uses as a stat header or footer rather than as prose. They are
# lifted out into their own fields so the description left over is only the
# part worth reading, and so the same number is not printed twice on one card.
LIFTED = {
    "type": None,
    "weight": "weight",
    "required level": "lv",
    "level required": "lv",
    "location": "slot",
    "position": "slot",
    "defense": "def",
    "magicdef": "mdef",
    "attack": "atk",
    "magicatk": "matk",
    "attack range": "range",
    "weapon level": "wlv",
}

RULE = re.compile(r"^[_\-=~.\s]+$")
FIELD = re.compile(r"^([A-Za-z][A-Za-z ]*?)\s*:\s*(.*)$")


def to_int(text):
    """`045` and `+22%` and `Lv 3` all have a number in them somewhere."""
    m = re.search(r"-?\d+", str(text))
    return int(m.group(0)) if m else 0


def read_description(text):
    """Split an in-game description into stat fields and readable prose."""
    fields, body = {}, []
    for line in (text or "").split("\n"):
        line = line.replace("\t", " ").strip()
        if not line or RULE.match(line):
            # A row of underscores is the game's separator. Keep it as a blank
            # so the paragraph breaks survive, but never as a run of glyphs.
            if body and body[-1] != "":
                body.append("")
            continue
        m = FIELD.match(line)
        if m and m.group(1).lower() in LIFTED and m.group(2).strip():
            key = LIFTED[m.group(1).lower()]
            if key and key not in fields:
                fields[key] = m.group(2).strip()
            continue
        body.append(C.house_style(line))

    while body and body[-1] == "":
        body.pop()
    return fields, "\n".join(body).strip()


# ---------------------------------------------------------------------------
# plumbing
# ---------------------------------------------------------------------------

def write(rel, text, quiet=False):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    if not quiet:
        print("  wrote %s - %d kb" % (rel, os.path.getsize(path) // 1024))


class Dict:
    """A string table. Repeated values become one small integer."""

    def __init__(self):
        self.values = []
        self.index = {}

    def id(self, value):
        if value not in self.index:
            self.index[value] = len(self.values)
            self.values.append(value)
        return self.index[value]


def dumps(payload):
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"


def options(table, cells):
    """(index, label, count) for one column, ready to become <option> tags.

    These are written into the page itself rather than derived in the browser,
    which is the whole point of the rewrite: the filters are usable, and show
    how much of everything there is, before a single byte of the payload has
    been asked for.
    """
    counts = {}
    for cell in cells:
        for v in (cell if isinstance(cell, list) else [cell]):
            counts[v] = counts.get(v, 0) + 1
    out = [(i, table[i], n) for i, n in counts.items()
           if table[i] and table[i].strip()]
    # A short list is most useful biggest-first; a long one is only findable
    # in alphabetical order.
    if len(out) > 20:
        out.sort(key=lambda o: o[1].lower())
    else:
        out.sort(key=lambda o: (-o[2], o[1].lower()))
    return out


# ---------------------------------------------------------------------------
# the payloads
# ---------------------------------------------------------------------------

def build_payload():
    ency = json.load(io.open(ENCY, encoding="utf-8"))
    game = json.load(io.open(GAME, encoding="utf-8"))

    by_name = {}
    for row in game["items"]:
        by_name.setdefault(row["name"], row)
    mob_stats = {}
    for row in game["mobs"]:
        mob_stats.setdefault(row["name"], row)

    # ---- items ----
    cats, groups, slots, jobs, zones, mobnames = (
        Dict(), Dict(), Dict(), Dict(), Dict(), Dict())
    item_ids = {}
    rows = []

    for n, it in enumerate(ency["items"]):
        fields, desc = read_description(it["description"])
        stat = by_name.get(it["name"], {})

        # The emulator's id is what a staff member would look up, so use it
        # when the item is in both. The forty-odd items added since that
        # snapshot get a synthetic id, which only ever has to be stable enough
        # to put in a link.
        item_id = stat.get("id") or (900000 + n)
        item_ids[it["name"]] = item_id

        raw_slots = [s for s in re.split(r"[,/]| and ", fields.get("slot", ""))
                     if s.strip()] or list(stat.get("loc") or [])
        slot_names = []
        for raw in raw_slots:
            name = slot_name(raw)
            if name and name not in slot_names:
                slot_names.append(name)

        sources = []
        for src in it["sources"]:
            sources.append([
                src["id"] or 0,
                mobnames.id(src["name"]),
                src["level"],
                zones.id(zone_name(src["zone"])),
                src["pct"],
                1 if src["mvp"] else 0,
            ])
        sources.sort(key=lambda s: -s[4])

        rows.append([
            item_id,
            it["name"],
            cats.id(clean_label(it["category"])),
            groups.id(group_of(it["category"])),
            [slots.id(s) for s in slot_names],
            to_int(fields.get("lv") or stat.get("lv") or 0),
            to_int(fields.get("weight") or 0) or (stat.get("weight") or 0) // 10,
            to_int(fields.get("atk") or stat.get("atk") or 0),
            to_int(fields.get("matk") or stat.get("matk") or 0),
            to_int(fields.get("def") or stat.get("def") or 0),
            to_int(fields.get("mdef") or 0),
            stat.get("slots") or 0,
            1 if stat.get("refine") else 0,
            jobs.id(", ".join(stat.get("jobs") or [])),
            desc,
            sources,
            # The zones the item drops in, flattened, so "show me everything
            # that drops in Payon" is one column read rather than a walk of
            # every source on every row.
            sorted({s[3] for s in sources}),
        ])

    write("assets/data/db-items.json", dumps({
        "cols": ["id", "name", "cat", "grp", "loc", "lv", "weight", "atk",
                 "matk", "def", "mdef", "slots", "refine", "jobs", "desc",
                 "src", "zones"],
        "cats": cats.values, "grps": groups.values, "locs": slots.values,
        "jobs": jobs.values, "zones": zones.values, "mobs": mobnames.values,
        "hues": [GROUP_HUE.get(g, "oth") for g in groups.values],
        "rows": rows,
    }))

    # ---- monsters ----
    races, elements, sizes, mzones, maps, itemnames = (
        Dict(), Dict(), Dict(), Dict(), Dict(), Dict())
    mrows = []
    for mob in ency["mobs"]:
        stat = mob_stats.get(mob["name"], {})
        mrows.append([
            mob["id"],
            mob["name"],
            mob["level"],
            mob["hp"],
            sizes.id(mob["size"] or "Unknown"),
            races.id(mob["race"] or "Unknown"),
            elements.id(mob["element"] or "Unknown"),
            mob["element_level"],
            1 if mob["mvp"] else 0,
            mzones.id(zone_name(mob["zone"])),
            [maps.id(m) for m in mob["maps"]],
            mob["card_effect"],
            mob["card_slot"],
            stat.get("exp") or 0,
            stat.get("jexp") or 0,
            stat.get("atk") or 0,
            stat.get("def") or 0,
            stat.get("mdef") or 0,
            [[itemnames.id(d["name"]), d["pct"], item_ids.get(d["name"], 0)]
             for d in mob["drops"]],
        ])

    write("assets/data/db-mobs.json", dumps({
        "cols": ["id", "name", "lv", "hp", "size", "race", "element", "elv",
                 "mvp", "zone", "maps", "card", "cslot", "exp", "jexp", "atk",
                 "def", "mdef", "drops"],
        "sizes": sizes.values, "races": races.values,
        "elements": elements.values, "zones": mzones.values,
        "maps": maps.values, "items": itemnames.values,
        "rows": mrows,
    }))

    picks = {
        "items": [
            ("grp", "Any kind", options(groups.values, [r[3] for r in rows])),
            ("loc", "Any slot", options(slots.values, [r[4] for r in rows])),
            ("cat", "Any category", options(cats.values, [r[2] for r in rows])),
        ],
        "mobs": [
            ("zone", "Anywhere", options(mzones.values, [r[9] for r in mrows])),
            ("race", "Any race", options(races.values, [r[5] for r in mrows])),
            ("element", "Any element", options(elements.values, [r[6] for r in mrows])),
            ("size", "Any size", options(sizes.values, [r[4] for r in mrows])),
        ],
    }

    return ((len(rows), len(mrows),
             sum(len(m["drops"]) for m in ency["mobs"]),
             len(mzones.values)), picks)


# ---------------------------------------------------------------------------
# the page
# ---------------------------------------------------------------------------

def select(tab, key, blank, entries):
    """One dropdown, options and all, written at build time."""
    opts = ['      <option value="">%s</option>' % C_esc(blank)]
    for index, label, n in entries:
        opts.append('      <option value="%d">%s (%s)</option>'
                    % (index, C_esc(label), f"{n:,}"))
    return ('    <label class="visually-hidden" for="pick-%s-%s">%s</label>\n'
            '    <select class="field field--select" id="pick-%s-%s"\n'
            '            data-pick="%s" data-tab="%s">\n%s\n    </select>'
            % (tab, key, C_esc(blank), tab, key, key, tab, "\n".join(opts)))


def C_esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


# The chips on the empty state: the six kinds people actually come looking for,
# labelled the way a player would say it rather than the way the data files it.
QUICK = [
    ("Weapon", "Weapons"),
    ("Armor", "Armor"),
    ("Headgear", "Headgear"),
    ("Card", "Cards"),
    ("Shadow gear", "Shadow gear"),
    ("Class gear", "Class gear"),
]


def quick_chips(picks):
    kinds = dict((key, entries) for key, _, entries in picks["items"])["grp"]
    index_of = dict((label, i) for i, label, _ in kinds)
    out = []
    for label, shown in QUICK:
        if label in index_of:
            out.append('          <button type="button" class="chip" '
                       'data-quick="items:grp:%d">%s</button>'
                       % (index_of[label], C_esc(shown)))
    # One monster chip, so the second tab is discoverable from the first.
    out.append('          <button type="button" class="chip" '
               'data-quick="mobs:mvp:1">MVPs</button>')
    return "\n".join(out)


def build_page(n_items, n_mobs, n_drops, n_zones, picks):
    trail = [("index.html", "Home"), (None, "Database")]
    item_picks = "\n".join(select("items", k, blank, entries)
                           for k, blank, entries in picks["items"])
    mob_picks = "\n".join(select("mobs", k, blank, entries)
                          for k, blank, entries in picks["mobs"])

    body = """<section class="page-hero page-hero--tight">
  <div class="shell">
    %(crumbs)s
    <h1 data-i18n="db.h1">Database</h1>
    <p class="lede" data-i18n="db.lede">
      Every item and every monster, with the description the game itself shows
      you. Search a name, or pick a category to browse.
    </p>
  </div>
</section>

<div class="shell db" id="db">
  <div class="db-tabs" role="tablist" aria-label="Database">
    <button class="db-tab" role="tab" id="tab-items" aria-controls="panel-items"
            aria-selected="true" data-db-tab="items" data-i18n="db.items">Items</button>
    <button class="db-tab" role="tab" id="tab-mobs" aria-controls="panel-mobs"
            aria-selected="false" data-db-tab="mobs" data-i18n="db.monsters">Monsters</button>
  </div>

  <form class="db-hunt" id="db-hunt" aria-label="Search and filter">
    <div class="db-search">
      <label class="visually-hidden" for="db-q">Search</label>
      <input id="db-q" class="field" type="search" autocomplete="off"
             placeholder="Search by name or effect..."
             data-i18n-attr="placeholder:db.search">
    </div>
    <div class="db-picks" data-picks="items">
%(item_picks)s
    </div>
    <div class="db-picks" data-picks="mobs" hidden>
%(mob_picks)s
    </div>
    <details class="db-extra">
      <summary data-i18n="db.more">More filters</summary>
      <div class="db-extra-body" id="db-facets">
        <p class="dim" data-i18n="db.extraWait">Opening this loads the data.</p>
      </div>
    </details>
  </form>

  <div class="db-main">
    <div class="db-bar" id="db-bar" hidden>
      <p class="db-count mono" id="db-count" aria-live="polite"></p>
      <div class="cluster">
        <label class="visually-hidden" for="db-sort">Sort</label>
        <select id="db-sort" class="field field--select"></select>
        <button type="button" class="btn btn--ghost btn--sm" id="db-reset"
                data-i18n="db.reset">Clear</button>
      </div>
    </div>
    <div id="panel-items" role="tabpanel" aria-labelledby="tab-items">
      <div class="db-start" id="db-start">
        <p data-i18n="db.startText">
          Nothing is loaded until you ask for something. Type a name or an
          effect above, or start from one of these.
        </p>
        <div class="cluster">
%(chips)s
        </div>
      </div>
      <ul class="db-list" id="db-list"></ul>
      <p class="db-empty" id="db-empty" hidden data-i18n="db.empty">
        Nothing matches those filters.
      </p>
      <button type="button" class="btn btn--ghost btn--block" id="db-page" hidden>
        Show more
      </button>
    </div>
  </div>
</div>

<aside class="db-detail" id="db-detail" data-open="false" role="dialog"
       aria-modal="false" aria-label="Entry details" hidden>
  <div class="db-detail-inner" id="db-detail-inner"></div>
</aside>

<section class="section section--tight">
  <div class="shell">
    <div class="panel">
      <p data-i18n="db.note">
        <strong>This is the live game data.</strong> Names, descriptions and
        drop rates come straight from the server the team is building on, so
        they are the most accurate reference that exists. Balance passes land
        here as they land in game. Where a page on this site says something
        different, that page wins.
        <a href="changes.html" data-i18n="db.note.link">See what changed</a>.
      </p>
    </div>
  </div>
</section>
""" % {"crumbs": C.breadcrumbs("", trail), "item_picks": item_picks,
       "mob_picks": mob_picks, "chips": quick_chips(picks)}

    out = C.head("", "Database | Return to Morroc: Refuge",
                 "Search %s items and %s monsters across %s zones. Filter by "
                 "category, slot, level, job, race, element and where it drops."
                 % (f"{n_items:,}", f"{n_mobs:,}", n_zones),
                 "database.html", extra_ld=C.crumb_ld(trail))
    out = out.replace("</head>",
                      '<script>window.RTMR_DB = {items: %d, mobs: %d, drops: %d};</script>\n</head>'
                      % (n_items, n_mobs, n_drops))
    out += C.header("", "database.html")
    out += '<main id="main">\n' + body + "\n</main>\n"
    out += C.footer("")
    # database.js has to run before i18n.js so the markup it owns exists when
    # the English snapshot is taken.
    out = out.replace('<script src="assets/js/main.js" defer></script>',
                      '<script src="assets/js/main.js" defer></script>\n'
                      '<script src="assets/js/database.js" defer></script>')
    write("database.html", out)


if __name__ == "__main__":
    print("building database")
    counts, picks = build_payload()
    build_page(*counts, picks=picks)
    print("  %d items, %d monsters, %d drop entries, %d zones" % counts)
