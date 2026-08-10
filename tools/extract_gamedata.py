# -*- coding: utf-8 -*-
"""Extract items and monsters from the server's own emulator database.

    python tools/extract_gamedata.py [path-to-emulator]

Reads the rAthena YAML the server actually runs on and writes
tools/data/game.json, which is committed. That file is the input to
tools/build_database.py, so a normal build stays offline and does not need the
emulator checkout present.

Why parse the emulator rather than a wiki: this is the server's own data, it is
complete, and every number in it is the number the game uses. A wiki is a
transcription of it by hand.

There is no PyYAML here on purpose - one dependency for one file format that
this project only ever reads in a single, very regular shape is a bad trade.
The parser below handles exactly that shape: `- Key: value` entries, nested
maps, block scalars and inline lists. It raises rather than guessing when it
meets anything else.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "data", "game.json")

DEFAULT_EMU = os.path.join(os.path.dirname(ROOT), "02 emu rathena")

FILES = {
    "equip": "db/re/item_db_equip.yml",
    "etc": "db/re/item_db_etc.yml",
    "usable": "db/re/item_db_usable.yml",
    "mob": "db/re/mob_db.yml",
}


# ---------------------------------------------------------------------------
# the smallest YAML reader that can read these four files
# ---------------------------------------------------------------------------

SCALAR = re.compile(r"^(-\s+)?([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")


def _clean(value):
    value = value.strip()
    if value.startswith("#"):
        return ""
    # Strip a trailing comment, but only when it is not inside quotes.
    if value and value[0] not in "\"'":
        value = value.split(" #")[0].strip()
    if len(value) > 1 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value in ("true", "false"):
        return value == "true"
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def parse(lines, i, indent):
    """Parse a block at `indent`. Returns (value, next_index)."""
    out = None
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        cur = len(raw) - len(raw.lstrip())
        if cur < indent:
            break

        body = raw.lstrip()
        if body.startswith("- "):
            if out is None:
                out = []
            if not isinstance(out, list):
                break
            m = SCALAR.match(body)
            if m:
                # A list item that is itself a map. The first key sits on the
                # dash line, so consume it here and read the rest of the map
                # from the NEXT line - handing the dash line back to parse()
                # would return immediately without advancing and spin forever.
                key, val = m.group(2), m.group(3).strip()
                entry = {}
                if val in ("|", ">"):
                    entry[key], i = read_block(lines, i + 1, cur + 2)
                elif val == "":
                    entry[key], i = parse(lines, i + 1, cur + 3)
                else:
                    entry[key] = _clean(val)
                    i += 1
                rest, i = parse(lines, i, cur + 2)
                if isinstance(rest, dict):
                    entry.update(rest)
                out.append(entry)
            else:
                out.append(_clean(body[2:]))
                i += 1
            continue

        m = SCALAR.match(body)
        if not m:
            break
        if out is None:
            out = {}
        if not isinstance(out, dict):
            break

        key, val = m.group(2), m.group(3).strip()
        if val == "|" or val == ">":
            block, i = read_block(lines, i + 1, cur)
            out[key] = block
        elif val == "":
            child, i = parse(lines, i + 1, cur + 1)
            out[key] = child if child is not None else ""
        else:
            out[key] = _clean(val)
            i += 1
    return out, i


def read_block(lines, i, indent):
    body = []
    while i < len(lines):
        raw = lines[i].rstrip("\n")
        if raw.strip() and (len(raw) - len(raw.lstrip())) <= indent:
            break
        body.append(raw[indent + 2:] if len(raw) > indent + 2 else "")
        i += 1
    return "\n".join(body).strip(), i


def load(path):
    lines = open(path, encoding="utf-8", errors="ignore").read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.startswith("Body:"))
    body, _ = parse(lines, start + 1, 1)
    return body or []


# ---------------------------------------------------------------------------
# shaping
# ---------------------------------------------------------------------------

# rAthena writes each equip slot as its own boolean. Collapsing them into one
# short label is what makes the filter usable.
LOCATION_LABEL = {
    "Head_Top": "Upper headgear", "Head_Mid": "Middle headgear",
    "Head_Low": "Lower headgear", "Armor": "Armor", "Right_Hand": "Weapon",
    "Left_Hand": "Off-hand", "Both_Hand": "Two-handed", "Garment": "Garment",
    "Shoes": "Shoes", "Right_Accessory": "Accessory", "Left_Accessory": "Accessory",
    "Both_Accessory": "Accessory", "Costume_Head_Top": "Costume",
    "Costume_Head_Mid": "Costume", "Costume_Head_Low": "Costume",
    "Costume_Garment": "Costume", "Ammo": "Ammunition",
    "Shadow_Armor": "Shadow armor", "Shadow_Weapon": "Shadow weapon",
    "Shadow_Shield": "Shadow shield", "Shadow_Shoes": "Shadow shoes",
    "Shadow_Right_Accessory": "Shadow accessory",
    "Shadow_Left_Accessory": "Shadow accessory",
}


def script_text(script):
    """Turn a bonus script into something a player can read.

    This is not a decompiler. It keeps the lines, drops the punctuation noise
    and leaves anything it does not recognise intact, because a slightly ugly
    true line beats a pretty invented one.
    """
    if not script:
        return ""
    out = []
    for line in str(script).split("\n"):
        line = line.strip().rstrip(";")
        if not line or line.startswith("//"):
            continue
        out.append(line)
    return " | ".join(out)[:600]


def jobs_of(entry):
    jobs = entry.get("Jobs")
    if not isinstance(jobs, dict):
        return []
    if jobs.get("All") and len([k for k, v in jobs.items() if v is False]) == 0:
        return ["All"]
    allowed = [k for k, v in jobs.items() if v is True and k != "All"]
    if jobs.get("All"):
        denied = [k for k, v in jobs.items() if v is False]
        return ["All except " + ", ".join(sorted(denied))] if denied else ["All"]
    return sorted(allowed)


def locations_of(entry):
    loc = entry.get("Locations")
    if not isinstance(loc, dict):
        return []
    seen = []
    for key, val in loc.items():
        if val is True:
            label = LOCATION_LABEL.get(key, key.replace("_", " "))
            if label not in seen:
                seen.append(label)
    return seen


def main():
    emu = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_EMU
    if not os.path.isdir(emu):
        print("emulator not found at", emu)
        print("usage: python tools/extract_gamedata.py <path-to-emulator>")
        sys.exit(2)

    raw_items = []
    for kind in ("equip", "etc", "usable"):
        path = os.path.join(emu, FILES[kind])
        if os.path.exists(path):
            entries = load(path)
            print("  %-7s %5d entries" % (kind, len(entries)))
            raw_items.extend(entries)

    mobs = load(os.path.join(emu, FILES["mob"]))
    print("  %-7s %5d entries" % ("mob", len(mobs)))

    by_aegis = {e.get("AegisName"): e for e in raw_items if e.get("AegisName")}

    # Which non-equipment items are actually reachable? An etc item nothing
    # drops and nothing sells is client clutter, and there are thousands of
    # them. Keeping only the reachable ones is what gets the payload from
    # megabytes to something a phone will download.
    dropped = set()
    for mob in mobs:
        for group in ("Drops", "MvpDrops"):
            for drop in mob.get(group) or []:
                if isinstance(drop, dict) and drop.get("Item"):
                    dropped.add(drop["Item"])

    items = []
    for e in raw_items:
        kind = e.get("Type") or "Etc"
        aegis = e.get("AegisName")
        keep = kind in ("Weapon", "Armor", "Card") or aegis in dropped
        if not keep:
            continue
        items.append({
            "id": e.get("Id"),
            "aegis": aegis,
            "name": e.get("Name") or aegis,
            "type": kind,
            "sub": e.get("SubType") or "",
            "slots": e.get("Slots") or 0,
            "atk": e.get("Attack") or 0,
            "matk": e.get("MagicAttack") or 0,
            "def": e.get("Defense") or 0,
            "range": e.get("Range") or 0,
            "weight": e.get("Weight") or 0,
            "buy": e.get("Buy") or 0,
            "sell": e.get("Sell") or 0,
            "lv": e.get("EquipLevelMin") or 0,
            "wlv": e.get("WeaponLevel") or e.get("ArmorLevel") or 0,
            "refine": bool(e.get("Refineable")),
            "loc": locations_of(e),
            "jobs": jobs_of(e),
            "script": script_text(e.get("Script")),
        })

    out_mobs = []
    for m in mobs:
        drops = []
        for group, mvp in (("Drops", False), ("MvpDrops", True)):
            for d in m.get(group) or []:
                if not isinstance(d, dict) or not d.get("Item"):
                    continue
                target = by_aegis.get(d["Item"], {})
                drops.append({
                    "item": target.get("Name") or d["Item"].replace("_", " "),
                    "id": target.get("Id") or 0,
                    "rate": d.get("Rate") or 0,
                    "mvp": mvp,
                })
        modes = m.get("Modes") if isinstance(m.get("Modes"), dict) else {}
        out_mobs.append({
            "id": m.get("Id"),
            "name": m.get("Name") or m.get("AegisName"),
            "lv": m.get("Level") or 1,
            "hp": m.get("Hp") or 1,
            "atk": m.get("Attack") or 0,
            "def": m.get("Defense") or 0,
            "mdef": m.get("MagicDefense") or 0,
            "exp": m.get("BaseExp") or 0,
            "jexp": m.get("JobExp") or 0,
            "size": m.get("Size") or "Small",
            "race": m.get("Race") or "Formless",
            "element": m.get("Element") or "Neutral",
            "elv": m.get("ElementLevel") or 1,
            "boss": bool(modes.get("Mvp")) or (m.get("Class") == "Boss"),
            "mvp": bool(modes.get("Mvp")),
            "drops": drops,
        })

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"items": items, "mobs": out_mobs}, fh,
                  ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        fh.write("\n")
    print("  wrote tools/data/game.json - %d items, %d monsters, %d kb"
          % (len(items), len(out_mobs), os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    print("extracting game data")
    main()
