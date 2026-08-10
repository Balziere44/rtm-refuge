# -*- coding: utf-8 -*-
"""Build the public database payload and the database page.

    python tools/build_database.py

Reads tools/data/game.json (produced by extract_gamedata.py from the server's
own emulator) and writes:

    assets/data/db-items.json   every item, as column arrays
    assets/data/db-mobs.json    every monster and what it drops
    database.html               the page shell

Rows are arrays, not objects, and repeated strings (type, subtype, slot, job
list) are indices into small dictionaries. With eleven thousand items the key
names and the repeated words are most of the file, so this is the difference
between a payload a phone will download and one it will not.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chrome as C

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAME = os.path.join(HERE, "data", "game.json")

# The emulator's internal type names are not what a player calls things.
TYPE_LABEL = {
    "Weapon": "Weapon", "Armor": "Armor", "Card": "Card",
    "Shadowgear": "Shadow gear", "Ammo": "Ammunition",
    "Usable": "Usable", "Healing": "Usable", "DelayConsume": "Usable",
    "Delayconsume": "Usable", "Petarmor": "Pet armor", "Etc": "Material",
}

SUB_LABEL = {
    "1hSword": "One-handed sword", "2hSword": "Two-handed sword",
    "1hSpear": "One-handed spear", "2hSpear": "Two-handed spear",
    "1hAxe": "One-handed axe", "2hAxe": "Two-handed axe",
    "Mace": "Mace", "2hMace": "Two-handed mace", "Staff": "Staff",
    "2hStaff": "Two-handed staff", "Bow": "Bow", "Knuckle": "Knuckle",
    "Musical": "Instrument", "Whip": "Whip", "Book": "Book",
    "Katar": "Katar", "Revolver": "Revolver", "Rifle": "Rifle",
    "Gatling": "Gatling gun", "Shotgun": "Shotgun", "Grenade": "Grenade launcher",
    "Huuma": "Huuma shuriken", "Dagger": "Dagger", "Shield": "Shield",
    "Arrow": "Arrow", "Bullet": "Bullet", "Kunai": "Kunai",
    "Cannonball": "Cannonball", "ThrowWeapon": "Throwing weapon",
    "Normal": "", "None": "",
}


def write(rel, text, quiet=False):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
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


def build_payload():
    game = json.load(open(GAME, encoding="utf-8"))
    items, mobs = game["items"], game["mobs"]

    types, subs, locs, jobs = Dict(), Dict(), Dict(), Dict()

    # item id -> [[mob index, rate], ...]. Built first so the item rows can
    # carry a "is this obtainable from a monster" flag for free.
    drops_by_item = {}
    for mi, mob in enumerate(mobs):
        for drop in mob["drops"]:
            if drop["id"]:
                drops_by_item.setdefault(drop["id"], []).append(
                    [mi, drop["rate"], 1 if drop["mvp"] else 0])

    rows = []
    for it in items:
        label = TYPE_LABEL.get(it["type"], it["type"])
        sub = SUB_LABEL.get(it["sub"], it["sub"] or "")
        rows.append([
            it["id"],
            it["name"],
            types.id(label),
            subs.id(sub),
            it["slots"],
            it["atk"],
            it["matk"],
            it["def"],
            it["lv"],
            it["weight"],
            1 if it["refine"] else 0,
            [locs.id(x) for x in it["loc"]],
            jobs.id(", ".join(it["jobs"]) if it["jobs"] else ""),
            # Scripts are the single biggest thing in the payload. The long
            # ones are combo text that repeats the same lines; 320 characters
            # keeps every ordinary bonus list whole.
            it["script"][:320],
            len(drops_by_item.get(it["id"], [])),
        ])

    payload = {
        "cols": ["id", "name", "type", "sub", "slots", "atk", "matk", "def",
                 "lv", "weight", "refine", "loc", "jobs", "fx", "drops"],
        "types": types.values,
        "subs": subs.values,
        "locs": locs.values,
        "jobs": jobs.values,
        "rows": rows,
    }
    write("assets/data/db-items.json",
          json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")

    races, elements, sizes = Dict(), Dict(), Dict()
    mrows = []
    for mob in mobs:
        mrows.append([
            mob["id"], mob["name"], mob["lv"], mob["hp"],
            mob["atk"], mob["def"], mob["mdef"], mob["exp"], mob["jexp"],
            sizes.id(mob["size"]), races.id(mob["race"]),
            elements.id(mob["element"]), mob["elv"],
            1 if mob["mvp"] else (2 if mob["boss"] else 0),
            [[d["id"], d["rate"], 1 if d["mvp"] else 0] for d in mob["drops"]],
        ])

    write("assets/data/db-mobs.json", json.dumps({
        "cols": ["id", "name", "lv", "hp", "atk", "def", "mdef", "exp", "jexp",
                 "size", "race", "element", "elv", "rank", "drops"],
        "sizes": sizes.values, "races": races.values, "elements": elements.values,
        "rows": mrows,
    }, ensure_ascii=False, separators=(",", ":")) + "\n")

    return len(rows), len(mrows), sum(len(m["drops"]) for m in mobs)


# ---------------------------------------------------------------------------
# the page
# ---------------------------------------------------------------------------

def build_page(n_items, n_mobs, n_drops):
    trail = [("index.html", "Home"), (None, "Database")]
    body = f"""<section class="page-hero page-hero--tight">
  <div class="shell">
    {C.breadcrumbs("", trail)}
    <h1 data-i18n="db.h1">Database</h1>
    <p class="lede" data-i18n="db.lede">
      Every item and every monster, straight out of the server's own files.
      Filter it, sort it, and follow a drop in either direction.
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

  <div class="db-shell">
    <form class="db-filters" id="db-filters" aria-label="Filters">
      <div class="db-search">
        <label class="visually-hidden" for="db-q">Search</label>
        <input id="db-q" class="field" type="search" autocomplete="off"
               placeholder="Search by name or effect..."
               data-i18n-attr="placeholder:db.search">
      </div>
      <div id="db-facets"></div>
      <button type="button" class="btn btn--ghost btn--block" id="db-reset"
              data-i18n="db.reset">Clear filters</button>
    </form>

    <div class="db-main">
      <div class="db-bar">
        <p class="db-count mono" id="db-count" aria-live="polite">Loading...</p>
        <label class="visually-hidden" for="db-sort">Sort</label>
        <select id="db-sort" class="field field--select"></select>
      </div>
      <div id="panel-items" role="tabpanel" aria-labelledby="tab-items">
        <ul class="db-list" id="db-list"></ul>
        <div id="db-sentinel" aria-hidden="true"></div>
        <p class="db-empty" id="db-empty" hidden data-i18n="db.empty">
          Nothing matches those filters.
        </p>
      </div>
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
      <p>
        <strong>These are the original world's numbers.</strong> They are read
        directly from the server files the project inherited, which makes them
        the most accurate reference that exists today - and it also means the
        Refuge's rebalance passes are not in them yet. Where a page on this
        site says something different, that page wins.
        <a href="changes.html">See what changed</a>.
      </p>
    </div>
  </div>
</section>
"""

    out = C.head("", "Database | Return to Morroc: Refuge",
                 "Searchable database of %s items and %s monsters with %s drops - "
                 "filter by type, slot, level, job, race and element."
                 % (f"{n_items:,}", f"{n_mobs:,}", f"{n_drops:,}"),
                 "database.html", extra_ld=C.crumb_ld(trail))
    out = out.replace("</head>",
                      '<script>window.RTMR_DB = {items: %d, mobs: %d, drops: %d};</script>\n</head>'
                      % (n_items, n_mobs, n_drops))
    out += C.header("", "database.html")
    out += '<main id="main">\n' + body + "\n</main>\n"
    out = out.replace('<script src="assets/js/i18n.js" defer></script>',
                      '<script src="assets/js/database.js" defer></script>\n'
                      '<script src="assets/js/i18n.js" defer></script>')
    out += C.footer("")
    # The footer is appended after the head replacement, so wire the script in
    # here instead - it has to come before i18n.js so its markup exists when
    # the translation snapshot is taken.
    out = out.replace('<script src="assets/js/main.js" defer></script>',
                      '<script src="assets/js/main.js" defer></script>\n'
                      '<script src="assets/js/database.js" defer></script>')
    write("database.html", out)


if __name__ == "__main__":
    print("building database")
    counts = build_payload()
    build_page(*counts)
    print("  %d items, %d monsters, %d drop entries" % counts)
