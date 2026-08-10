# -*- coding: utf-8 -*-
"""The visual codex: the words the game keeps using, and what they mean.

Item and skill descriptions are written for someone who already plays. They
lean on about sixty recurring terms - "Combo Ready", "Fixed Cast", "Per
Refine", "Perfect Dodge" - and none of them are ever explained. A new player
reading "Enables Combo Ready for 1.5s" learns nothing from it.

This is the one place those words are defined. Every definition is one line,
in plain language, and says what it means *for the player* rather than how it
is implemented. Where a term is measurable the definition avoids the number,
for the same reason the rest of the site does: numbers move with balance
passes and a definition should not.

The terms are grouped, and each group has a colour that is used everywhere the
term appears - the codex page, the skill tables, the database drawer - so the
colour itself starts to carry meaning after a few minutes of reading.

`ALIASES` exists because the game writes the same idea several ways ("Def
Pierce", "Defense Pierce", "Defence Pierce"). All spellings resolve to one
entry so the reader sees one consistent word.
"""

# key: (term, definition). The key is the anchor slug.
GROUPS = [
    ("states", "States you build up", "st",
     "Conditions your own actions put you in. Almost every job has at least "
     "one, and using a skill at the wrong moment usually means wasting it.", [
         ("combo-ready", "Combo Ready",
          "A short window opened by one skill in which the next one hits harder or behaves differently."),
         ("cast-ready", "Cast Ready",
          "A window in which a skill that normally needs channelling goes off instantly."),
         ("finisher-ready", "Finisher Ready",
          "A window in which a job's closing skill gains its full effect."),
         ("duel-counter", "Duel Counter",
          "Charges a Duelist accumulates by fighting; several skills spend them or scale on them."),
         ("rolling-counter", "Rolling Counter",
          "Charges built by an Assassin's spinning attacks, spent by the heavier follow-ups."),
         ("overslash-stack", "Overslash Stack",
          "Charges that build as you keep swinging and raise the damage of the skill that consumes them."),
         ("harvest-mode", "Harvest Mode",
          "A Dark Knight stance that blocks healing from skills in exchange for far heavier hits."),
         ("assault-mode", "Assault Mode",
          "A Peacekeeper stance that trades defence for the ability to cut through armour."),
     ]),

    ("timing", "Timing", "ti",
     "How long things take. Most of what separates a job that feels fast from "
     "one that feels heavy is here, not in its damage.", [
         ("cast-time", "Cast Time",
          "The channel before a skill goes off. Being hit can interrupt it."),
         ("fixed-cast", "Fixed Cast",
          "The part of a cast that stats cannot shorten. Only gear made for it will."),
         ("after-cast-delay", "After Cast Delay",
          "The pause after a skill during which you cannot use another. Often the real limit on a rotation."),
         ("cooldown", "Base Starting Cooldown",
          "The wait before a skill can be used again, before any gear reduces it."),
         ("aspd", "ASPD",
          "Attack speed: how quickly you swing between skills. Capped, and the cap differs per job."),
     ]),

    ("gear", "Words on gear", "ge",
     "The vocabulary of equipment. These appear on almost every piece in the "
     "database.", [
         ("set-bonus", "Set Bonus",
          "An extra effect you only get while wearing every piece of a named set."),
         ("piece-bonus", "Piece Bonus",
          "What a single shadow piece gives you on its own, without the rest of its set."),
         ("per-refine", "Per Refine",
          "A bonus that grows with each successful refine, so the same item improves as you invest in it."),
         ("random-options", "Random Options",
          "Bonuses rolled when an item drops. What it rolled is what it is, and the Refuge has no rerolling."),
         ("boss-relic", "Boss Relic",
          "A piece dropped by an MVP that upgrades a weapon into its relic form."),
         ("card-slot", "Card Slot",
          "A socket for a card. How many an item has is fixed when it drops."),
     ]),

    ("offence", "Attack", "of",
     "How damage is worked out. Worth knowing which of these your build "
     "actually scales with before buying gear for it.", [
         ("defense-pierce", "Defense Pierce",
          "Ignores a share of the target's armour, so heavily armoured enemies stop being immune to you."),
         ("magic-defense-pierce", "Magic Defense Pierce",
          "The same, against magic resistance."),
         ("critical-rate", "Critical Rate",
          "How often you land a critical hit."),
         ("critical-damage", "Critical Damage",
          "How much extra a critical hit does when it lands."),
         ("ranged-damage", "Ranged Damage",
          "A bonus that only applies to attacks made from a distance."),
         ("splash-range", "Splash Range",
          "How far a hit spreads to enemies around the target."),
         ("attack-range", "Attack Range",
          "How far away you can be and still hit. Measured in cells."),
         ("endow", "Endow",
          "Temporarily gives your weapon an element, which changes how much damage it does to what."),
     ]),

    ("defence", "Defence and survival", "de",
     "What keeps you standing. Monsters in the Refuge hit harder than they did "
     "and healing is slower, so these matter more than they used to.", [
         ("perfect-dodge", "Perfect Dodge",
          "A flat chance to avoid a hit outright, no matter how accurate the attacker is."),
         ("flee", "Flee",
          "Ordinary evasion. Works against accuracy, and stops working when you are outnumbered."),
         ("hit", "Hit",
          "Accuracy. Enough of it and the target's evasion stops mattering."),
         ("neutral-resistance", "Neutral Resistance",
          "Reduction against plain physical damage, which is most of what hits you."),
         ("healing-received", "Healing Received",
          "How much good a heal does on you. Some very strong gear cuts it."),
         ("leech", "Leech",
          "Recovers HP from a share of the damage you deal."),
         ("overheal", "Overheal",
          "Healing beyond your maximum, turned into a temporary shield instead of being wasted."),
     ]),

    ("status", "Status effects", "sx",
     "What you inflict, and what gets inflicted on you. In the Refuge several "
     "of these now work on bosses, which they did not before.", [
         ("poison", "Poison",
          "Damage over time that also softens defence. Now applies to bosses."),
         ("burning", "Burning", "Fire damage over time."),
         ("frost", "Frost",
          "Slows the target and sets up the heavier freeze."),
         ("frozen", "Frozen",
          "The target cannot act, and takes more from some skills while it lasts."),
         ("bleeding", "Bleeding",
          "Damage over time that also blocks natural recovery."),
         ("stun", "Stun", "The target cannot act for a moment."),
         ("knockback", "Knockback",
          "Pushes the target away, measured in cells. Useful for control, awkward in a party."),
         ("hiding", "Hiding",
          "Drops you out of sight. Capped at a fixed two seconds in the Refuge, but it now works on bosses, insects and demons."),
         ("cloaking", "Cloaking",
          "Move while unseen. Ordinary monsters lose you; bosses do not."),
     ]),

    ("stats", "The six stats", "sa",
     "What you put your points into. Every skill scales off at least one of "
     "them, and the scaling is listed on the skill.", [
         ("str", "STR", "Physical attack, and how much you can carry."),
         ("agi", "AGI", "Attack speed and evasion."),
         ("vit", "VIT", "Health, defence and resistance to status effects."),
         ("int", "INT", "Magic attack, SP and magic defence."),
         ("dex", "DEX", "Accuracy, ranged damage and shorter casting."),
         ("luk", "LUK", "Criticals, perfect dodge, and a quiet hand in a lot of formulas."),
     ]),
]

# Spellings the game uses that should resolve to one entry. Longest first
# matters at match time, not here.
ALIASES = {
    "defense-pierce": ["Def Pierce", "Defence Pierce", "DEF Pierce"],
    "magic-defense-pierce": ["MagicDef Pierce", "MDef Pierce", "Magic Def Pierce"],
    "cooldown": ["Cooldown", "Starting Cooldown"],
    "aspd": ["Attack Speed"],
    "duel-counter": ["Duel Counters"],
    "rolling-counter": ["Rolling Counters", "Rolling Cutter Counter"],
    "overslash-stack": ["Overslash Stacks"],
    "leech": ["Leeching", "Leech Power", "lifesteal"],
    "endow": ["Endows", "Endowed"],
    "critical-rate": ["Crit Rate"],
    "critical-damage": ["Crit Damage", "Critical Damage Bonus"],
    "cast-time": ["Casting Time"],
    "fixed-cast": ["Fixed Cast Time", "Fixed Casting"],
    "random-options": ["Random Option"],
    "perfect-dodge": ["Perfect Dodge"],
}


def entries():
    """Every term as (slug, term, definition, group_key, hue)."""
    for key, _title, hue, _blurb, terms in GROUPS:
        for slug, term, definition in terms:
            yield slug, term, definition, key, hue


def lookup():
    """Every spelling mapped to (slug, term, definition, hue).

    Sorted longest-first by the caller: "Magic Defense Pierce" has to be tried
    before "Defense Pierce" or the longer term is never matched.
    """
    out = {}
    for slug, term, definition, _key, hue in entries():
        for spelling in [term] + ALIASES.get(slug, []):
            out[spelling] = (slug, term, definition, hue)
    return out
