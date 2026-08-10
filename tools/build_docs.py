# -*- coding: utf-8 -*-
"""Generate the long reference pages: Start Here, Mechanics, Gear, World.

    python tools/build_docs.py

Each page is a list of sections. A section is our own heading and lede
followed, optionally, by material rendered straight out of tools/data/wiki.json
- the community wiki for the world the Refuge inherited.

Two rules make that safe to do:

1. Anything the Refuge changed is rendered as a labelled callout ABOVE the
   inherited material, never edited into it. A reader always knows which lines
   are old and which are new.
2. Sections that document the OTHER server's own additions are dropped by
   name in DROP, rather than being quietly reworded. Rates are the obvious
   one: that server picked its own, and stating them here would be wrong.
"""

import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chrome as C
import data as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = json.load(open(os.path.join(ROOT, "tools", "data", "wiki.json"), encoding="utf-8"))

# Headings that belong to the other server rather than to the shared world.
DROP = {
    ("New_Player_Guide", "Echoes of Morroc info"),
    ("Main_Features", "Server Information"),
    ("Main_Features", "Contents"),
    ("Main_Page", ""),

    # The rarity tiers and the reroll orbs are theirs. The Refuge has neither,
    # and the gear page says so in a callout - which used to sit directly on
    # top of six sections explaining how they work.
    ("Random_Options", "Rarity System & Rerolling"),
    ("Random_Options", "Rarity Levels"),
    ("Random_Options", "Important Notes"),
    ("Random_Options", "Reroll System"),
    ("Random_Options", "Normal Monster Orbs"),
    ("Random_Options", "MVP Orbs"),

    # Both of these pages contain no content: two "Click Here" cross-links, a
    # table of contents, and a language model's reply preamble that somebody
    # pasted in and never trimmed. There is nothing here to render.
    ("Shadow_Sets", ""),
    ("Shadow_Sets", "Geffen Cave"),
    ("Shadow_Sets", "Tribes"),
    ("Shadow_Sets", "Thanatos Tower"),
    ("Job_Sets", ""),
    ("Job_Sets", "Contents"),
}

# Any bullet or paragraph naming that server, or a system it has and we do
# not, is theirs. These are whole phrases on purpose: "orb" alone would take
# Draco Orbs, the Bifrost Mirror's blue orbs and shadow orbs with it, and
# "reroll" alone would take the Illusionist's kimi.
DROP_IF = (
    "Echoes of Morroc", "Echoes rates",
    "rarity system", "rarities system", "reroll system",
    "rarity level", "have a rarity", "Orb Types",
    # Wiki markup, embeds and editing debris that should never have survived
    # the parse.
    "__TOC__", "media.tenor.com", "https://", "http://",
    "converted from HTML to MediaWiki", "Click Here",
)


def esc(s):
    return html.escape(s or "", quote=False)


def write(rel, text):
    with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("  wrote", rel, len(text) // 1024, "kb")


def keep(page, sec):
    if (page, sec["title"]) in DROP:
        return False
    return True


def clean(items):
    return [i for i in items if not any(bad in i for bad in DROP_IF)]


def wiki_block(page, only=None, skip=(), heading_level=3, label=None):
    """Render a wiki page (or named sections of it) as collapsed detail.

    The site is meant to read as a table of contents for the server: what to
    expect, and some examples. The inherited reference is worth keeping - it
    is the only surviving transcription of that world - but it is not what
    somebody arriving at the page came for, and twenty thousand words of it
    was burying the four sentences that were.

    So every wiki block is folded away behind one line. Our own writing and
    the Refuge callouts stay in the open; this opens when somebody actually
    wants it. Nothing is lost and the default page is a tenth of the length.
    """
    data = WIKI.get(page)
    if not data:
        return '<p class="dim">Not documented yet.</p>'
    out = []
    for sec in data["sections"]:
        if not keep(page, sec):
            continue
        title = sec["title"]
        if only and title not in only:
            continue
        if title in skip:
            continue
        paras = clean(sec["paras"])
        bullets = clean(sec["bullets"])
        if not paras and not bullets:
            continue
        if title and title.lower() not in ("skills",):
            out.append("<h%d id=\"%s\">%s</h%d>" % (
                heading_level, slug(page + "-" + title), esc(title), heading_level))
        for p in paras:
            out.append("<p>%s</p>" % esc(p))
        if bullets:
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % esc(b) for b in bullets))
    if not out:
        return '<p class="dim">Not documented yet.</p>'
    # Two blocks in one section is common, and two summaries reading "Read the
    # full detail" one under the other tells nobody which is which. Name them
    # after what they actually contain.
    if not label:
        if only and len(only) == 1:
            label = list(only)[0]
        else:
            label = page.replace("_", " ")
    return ('<details class="more">\n'
            '        <summary>%s, in full</summary>\n'
            '        <div class="more-body">\n      %s\n        </div>\n'
            '      </details>' % (esc(label), "\n      ".join(out)))


def slug(s):
    return "".join(c.lower() if c.isalnum() else "-" for c in s).strip("-")


CALLOUT_KEYS = {
    "What the Refuge changed": "ui.refugeChanged",
    "Not in the Refuge": "ui.notInRefuge",
    "New in the Refuge": "ui.newInRefuge",
}


def _ck(title):
    return CALLOUT_KEYS.get(title, "")


def callout(title, items, kind="refuge"):
    body = "".join("<li>%s</li>" % i for i in items)
    key = _ck(title)
    attr = f' data-i18n="{key}"' if key else ""
    return (f'<aside class="callout callout--{kind}">\n'
            f'        <h3{attr}>{title}</h3>\n        <ul>{body}</ul>\n      </aside>')


def section(sid, title, lede, body):
    return f"""    <section id="{sid}">
      <h2>{title}</h2>
      <p>{lede}</p>
      {body}
    </section>"""


def doc_page(name, title, description, active, hero_title, hero_lede, sections,
             trail_label, intro="", hero_cta=""):
    toc = "\n".join(
        '        <li><a href="#%s">%s</a></li>' % (sid, t)
        for sid, t, _l, _b in sections)
    body_html = "\n".join(section(sid, t, l, b) for sid, t, l, b in sections)

    trail = [("index.html", "Home"), (None, trail_label)]
    body = f"""<section class="page-hero">
  <div class="shell">
    {C.breadcrumbs("", trail)}
    <h1>{hero_title}</h1>
    <p class="lede">{hero_lede}</p>
    <div class="cluster" style="margin-top:1.6rem">
      <a class="btn btn--primary" href="{C.DISCORD}" rel="noopener" data-i18n="cta.join">Join the community server</a>
      {hero_cta}
    </div>
  </div>
</section>
{intro}
<div class="shell doc">
  <nav class="doc-toc" aria-label="On this page">
    <h2 data-i18n="ui.onThisPage">On this page</h2>
    <ol>
{toc}
    </ol>
  </nav>
  <div class="doc-body">
{body_html}
    <p class="source-note">
      Material on this page is transcribed from the community wiki for the world
      the Refuge inherited, and from the development team's own posts. Where the
      two disagree, the posts win and the difference is called out in a purple
      box. Numbers may still move before launch.
    </p>
  </div>
</div>
"""
    out = C.head("", title, description, name, extra_ld=C.crumb_ld(trail))
    out += C.header("", active)
    out += '<main id="main">\n' + body + "\n</main>\n"
    out += C.footer("")
    write(name, out)


# ---------------------------------------------------------------------------
# Start here
# ---------------------------------------------------------------------------

def build_start():
    sections = [
        ("waking", "You wake up as an Orphan",
         "No memories, no name, and a reflection that will not stop talking to you. "
         "That is the whole of your character creation.",
         callout("What the Refuge changed", [
             "Every character starts with <strong>Warp Portal</strong> and <strong>Teleport level 1</strong> as core skills. You do not have to earn mobility.",
             "<strong>Heal</strong> and <strong>Hiding</strong> are capped at level 1 and rebuilt. Heal scales off your base level; Hiding is a fixed 2 seconds that works on bosses.",
             "Manuals that granted those skills were reworked or removed, so guides written for the original world will point you at items that no longer do what they say.",
         ]) + "\n      " + wiki_block("Orphan", skip=("Skills",)) +
         "\n      " + wiki_block("New_Player_Guide", only=("Orphan Dream",))),

        ("orphanage", "The Orphanage",
         "The hub. Every service you need before level 50 is in one building, and "
         "the Refuge gave the whole place a visual pass.",
         wiki_block("The_Orphanage")),

        ("first-job", "Your first job change",
         "Ten job levels for a normal job, fifteen for an Expert one, twenty-five "
         "if you want to be a Mimic. The basement under the pyramids is where you "
         "get them.",
         wiki_block("New_Player_Guide", only=("First Job Change", "Getting Started"))),

        ("levelling", "Where to level, all the way to 130",
         "The single most useful thing the community ever wrote down: which map, "
         "at which level, and what to take away from it.",
         callout("Read this before you follow a level range", [
             "Monsters deal more damage than they used to and healing is slower, so a spot that was comfortable in the original may not be.",
             "Experience is slightly slower than the original's, but the curve is more rewarding.",
             "Drop-rate gear no longer exists, so there is nothing to farm before you farm.",
         ], kind="warn") + "\n      " +
         wiki_block("New_Player_Guide", only=(
             "Getting Started", "Journey Continues", "Leveling? I Love it!",
             "We're So Back!", "It's so over"))),

        ("second-job", "Second job, specialisation, final job",
         "The main road forks twice. Here is what each fork means and when you "
         "reach it.",
         wiki_block("New_Player_Guide", only=(
             "Second Job Change", "Choosing Specialization", "Final job change?")) +
         '\n      <p><a class="btn btn--ghost" href="classes.html">See the full class tree</a></p>'),

        ("distortions", "Level 100 and the Bifrost Mirror",
         "Distortion dungeons are the first content gate that asks you to prepare "
         "rather than just arrive.",
         wiki_block("New_Player_Guide", only=("What the Orb?",)) +
         "\n      " + wiki_block("Bifrost_Mirror") +
         '\n      <p><a class="btn btn--ghost" href="guides.html#bifrost">Step-by-step mirror walkthrough</a></p>'),

        ("endcap", "130, 150, and what comes after",
         "One hundred and thirty is the soft cap. One hundred and fifty is a "
         "challenge rather than a goal.",
         wiki_block("New_Player_Guide", only=("Is this the End?",)) +
         "\n      " + callout("What the Refuge added past this point", [
             "<strong>Nightmare in Amatsu</strong>, an SS dungeon where level 150 is recommended, there is no minimap, and dying costs a base level.",
             "A second SS dungeon, finished, on a fully custom map. It will not be described before launch.",
             "<strong>Einherjar Challenge Mode</strong>: your level cap only rises when you beat a boss of your own level. It awards costumes, not relics.",
             "More than fifty new shadow sets, none of them job-locked.",
         ])),
    ]
    doc_page("start.html",
             "Start Here | Return to Morroc: Refuge",
             "A new player guide for the Refuge: your first job change, every levelling "
             "spot from 1 to 130, when to specialise, and what the rebuild changed.",
             "start.html",
             "Start here",
             "Everything between waking up with no name and hitting the soft cap, in "
             "the order you will need it.",
             sections, "Start Here",
             hero_cta='<a class="btn btn--ghost" href="classes.html">Pick a class</a>')


# ---------------------------------------------------------------------------
# Mechanics
# ---------------------------------------------------------------------------

def build_mechanics():
    sections = [
        ("combat", "Combat was rebuilt, not tuned",
         "Skills matter more than gear checks. You dodge, you rotate, you move.",
         wiki_block("Combat_Reworked") + "\n      " +
         wiki_block("Main_Features", only=("Combat Mechanics",))),

        ("stats", "Stats and the cost curve",
         "Points get more expensive as they climb, breakpoints survived from "
         "pre-renewal, and almost every skill now scales off a stat.",
         '<p>What each of the six actually does is one line each in the '
         '<a href="codex.html#g-stats">codex</a>, along with Hit, Flee, '
         'Perfect Dodge and the rest of the vocabulary. What follows is the '
         'part that is specific to this world.</p>\n      ' +
         wiki_block("Main_Features", only=("Character Stats",)) + "\n      " +
         # Everything skipped here is a one-line definition that the codex now
         # owns. Printing both means maintaining both, and they would drift.
         wiki_block("Stat_Changes", skip=(
             "Strength (STR)", "Agility (AGI)", "Vitality (VIT)",
             "Intelligence (INT)", "Dexterity (DEX)", "Luck (LUK)",
             "Attack (ATK)", "Magic Attack (MATK)", "Critical Rate and Damage",
             "Hit Rate (Hit)", "Flee Rate (Flee)", "Perfect Dodge",
             "Attack Speed (ASPD)", "Cast Time",
             "Stun", "Silence", "Poison", "Burning", "Freeze",
             "All Status Effects",
         ))),

        ("aspd", "Attack speed",
         "Each job has its own base attack speed limit, and the Refuge went back "
         "through the ones that were simply strange.",
         callout("What the Refuge changed", [
             "Base attack speed was re-adjusted on several jobs where the original value made no sense.",
             "Increase AGI no longer grants attack speed at all - it is a movement skill now.",
         ]) + "\n      " + wiki_block("Base_Aspd_Limit_Table")),

        ("elements", "Elements",
         "The element table is the difference between a comfortable dungeon and a "
         "wall. Endows are cheap; ignoring them is not.",
         wiki_block("Elemental_Table")),

        ("combos", "Combos and rotations",
         "Some skills read what you cast before them. This is the layer most "
         "players discover late and wish they had known about at level 30.",
         wiki_block("Combos_Rotations", skip=("Combo Ready", "Cast Ready", "Stance")) +
         '\n      <p>The three states a skill can leave you in - '
         '<a href="codex.html#combo-ready">Combo Ready</a>, '
         '<a href="codex.html#cast-ready">Cast Ready</a> and the job stances - '
         'are defined in the codex, and underlined wherever they appear.</p>'),

        ("bonuses", "Innate and unique bonuses",
         "Equipment does more than add numbers. Bouncing skills, repeating "
         "skills, autocasts and leech all live here.",
         wiki_block("Innate_Fixed_Bonus") + "\n      " + wiki_block("Unique_Bonuses")),

        ("death", "Dying, and the Shadow you leave behind",
         "Death is not a loading screen. It puts something hostile in the room "
         "with your party.",
         wiki_block("Shadow_System") + "\n      " +
         callout("What the Refuge changed", [
             "Hiding now works on bosses, insects and demons - so boss skills were rebalanced in response.",
             "In <strong>Nightmare in Amatsu</strong>, dying costs a base level outright.",
         ])),

        ("ranking", "Dungeon ranks",
         "Every dungeon carries a difficulty tier. Anything can be done solo with "
         "enough preparation - the rank tells you how much.",
         wiki_block("Ranking_System", skip=(
             "RANK E", "RANK D", "RANK C", "RANK B", "RANK A", "RANK S",
         )) +
         '\n      <p>Every dungeon and the rank it carries is in the table on '
         'the <a href="world.html#distortions">world page</a>, which is '
         'sortable and searchable. Six paragraphs describing six ranks were '
         'the same information, arranged worse.</p>'),
    ]
    doc_page("mechanics.html",
             "Mechanics | Return to Morroc: Refuge",
             "How combat, stats, elements, attack speed, combos and death actually work "
             "in the Refuge, and what the rebuild changed about each of them.",
             "mechanics.html",
             "How the game actually works",
             "Combat, stats, elements, rotations and death. The systems layer, with "
             "the Refuge's changes marked where they land.",
             sections, "Mechanics",
             hero_cta='<a class="btn btn--ghost" href="gear.html">Gear systems</a>')


# ---------------------------------------------------------------------------
# Gear
# ---------------------------------------------------------------------------

def build_gear():
    sections = [
        ("items", "Over 1,500 pieces of equipment",
         "Every item is custom. NPC gear is worth wearing, field monsters drop it "
         "with extra slots, and almost everything rolls random options.",
         wiki_block("Main_Features", only=("New Items",)) + "\n      " +
         wiki_block("NPC_Equipment")),

        ("random-options", "Random options",
         "Rebuilt from the ground up so that a roll is interesting on its own "
         "terms, rather than a lottery you have to keep playing.",
         callout("Not in the Refuge", [
             "There are <strong>no orbs for rerolling random options</strong>. What a piece rolls is what it rolled - the roll is the item, not a starting position you buy your way out of.",
             "There is <strong>no weapon rarity system</strong> either. A weapon is judged on what it does, not on a tier printed above its name.",
             "Both are a deliberate difference, not an omission.",
         ], kind="warn") + "\n      " + wiki_block("Random_Options")),

        ("refine", "Refining that respects your time",
         "Maximum +10, and failure never breaks the item.",
         wiki_block("Main_Features", only=("Refining",)) + "\n      " +
         wiki_block("Refine_System")),

        ("cards", "Cards",
         "Every single card was reworked. One percent from a normal monster, two "
         "from a mini-boss, three from an MVP.",
         wiki_block("Card_System")),

        ("shadows", "Shadow equipment",
         "At least one shadow set per dungeon, occupying four slots instead of "
         "ten. This is the part of the game the Refuge changed most.",
         callout("What the Refuge changed", [
             "<strong>Job shadow sets are gone.</strong> The level 100+ sets that locked each job into one playstyle were removed outright.",
             "<strong>More than fifty new sets</strong> replace them, one or more per dungeon past level 100, none of them job-locked.",
             "They exist to make the neglected half of each skill tree worth building around. One still in testing puts you at 1 HP in exchange for chaining a lot of skills in a row.",
             "Because the mandatory set is gone, the overall power curve sits lower than the original's. That is deliberate.",
         ]) + """
      <h3>Every shadow piece, with what it does</h3>
      <p>There are 206 of them and each one carries the description the game
         itself shows, so they live in the database rather than in a list here
         that would go stale the first time one is retuned. Filter by set
         bonus, by slot, or by the monster that drops it.</p>
      <p><a class="btn btn--primary" href="database.html?kind=Shadow+gear">Browse the shadow gear</a></p>"""),

        ("runes", "Runes and manuals",
         "Two slots that do not exist in the original game. One changes how you "
         "look, the other changes what you can do.",
         wiki_block("Runes") + "\n      " +
         callout("What the Refuge changed", [
             "Many manuals were transformed into something else entirely, orphan skill manuals most of all.",
             "Manuals that granted Heal, Hiding, Warp Portal or Teleport were reworked or removed, because those skills are now core and capped.",
             "Dracomancers equip Draco Orbs in place of runes, and orbs are now a strong extra rather than a rotation button.",
         ])),

        ("enchants", "Dream enchantments",
         "A second layer on top of refining and options.",
         wiki_block("Dream_Enchantments")),

        ("economy", "Shops, exchanges and the Black Market",
         "Where the zeny goes, and the several systems that will take it from you.",
         wiki_block("Black_Market") + "\n      " + wiki_block("Systems_and_Exchanges") +
         "\n      " + wiki_block("Kafra_Services") +
         "\n      " + callout("What the Refuge changed", [
             "<strong>There is no cash shop.</strong> It was removed outright, and there is no real-money trading of any kind.",
             "<strong>Drop-rate bonuses from gear no longer exist.</strong> Drop tables are tuned once, honestly, for everyone.",
         ])),
    ]
    doc_page("gear.html",
             "Gear and Items | Return to Morroc: Refuge",
             "Equipment, random options, refining, cards, shadow sets, runes and manuals "
             "in the Refuge - including the job sets that were removed and what replaced them.",
             "gear.html",
             "Gear, and what to do with it",
             "Fifteen hundred items, refining that cannot break them, and the shadow "
             "system the Refuge rebuilt from scratch.",
             sections, "Gear",
             hero_cta='<a class="btn btn--ghost" href="world.html">Where it drops</a>')


# ---------------------------------------------------------------------------
# World
# ---------------------------------------------------------------------------

def build_world():
    rows = "\n".join(
        f"""        <tr data-row>
          <th scope="row">{esc(n)}</th>
          <td class="num">{lv}</td>
          <td class="num"><span class="badge rank-{r.lower()}">{r}</span></td>
          <td>{esc(w)}</td>
        </tr>""" for n, lv, r, w in D.DUNGEONS)

    table = f"""<div class="cluster" style="margin:1.4rem 0 1rem">
        <label class="visually-hidden" for="dsearch">Filter dungeons</label>
        <input id="dsearch" type="search" class="field" placeholder="Filter by name, level or rank..." data-i18n-attr="placeholder:ui.filterDungeons"
               data-filter="dtable" data-filter-count="dcount">
        <span class="chip mono" id="dcount">-</span>
      </div>
      <div class="table-wrap">
        <table id="dtable">
          <caption class="visually-hidden">Distortion dungeons with level range, rank and location</caption>
          <thead><tr><th scope="col">Dungeon</th><th scope="col">Level</th><th scope="col">Rank</th><th scope="col">Where</th></tr></thead>
          <tbody>
{rows}
          </tbody>
        </table>
      </div>
      <p class="dim">Directions are condensed from the community access guide.
      <a href="guides.html#external">The original, with screenshots, is here.</a></p>"""

    sections = [
        ("world", "New-Midgard",
         "The world was expanded rather than replaced. No access quests, no "
         "instanced dungeons in the levelling loop, and a great many places that "
         "are not where you remember them.",
         wiki_block("Main_Features", only=("A New World to explore",)) + "\n      " +
         wiki_block("World_Changes")),

        ("regions", "Regions and dungeons",
         "Where to go, at what level, and how hard it will be when you get there.",
         wiki_block("Regions_and_Dungeons")),

        ("distortions", "Distortion dungeons",
         "Twenty-one instanced endgame dungeons from level 85 to 150, ranked B "
         "through SS. Each one bends a rule: draining experience on death, "
         "disabling resurrection, enabling free PvP, buffing the monsters.",
         wiki_block("Distortion_Dungeons") + "\n      " + table),

        ("mvps", "MVPs and relics",
         "You no longer have to hope the spawn timer likes you.",
         wiki_block("MVP_System")),

        ("instances", "Instances",
         "Deliberately rare. They exist for the story and a few job quests, and "
         "nowhere else.",
         wiki_block("Instance_List")),

        ("endgame", "The Refuge's own endgame",
         "Two SS-rank dungeons that did not exist before, and an optional mode "
         "that changes what levelling means.",
         callout("New in the Refuge", [
             "<strong>Nightmare in Amatsu.</strong> Level 150 recommended. A heavily customised version of the classic first floor - no hidden doors, real openings, and no minimap. You spawn semi-randomly and orient yourself by the map shadows, because the light source is at the centre. Or you pay zeny to spawn somewhere safe.",
             "<strong>The Amatsu penalty.</strong> Dying there costs you a base level.",
             "<strong>A second SS dungeon</strong>, finished, on a fully custom map. It will not be described before launch.",
             "<strong>Bosses were rebalanced</strong> because Hiding now works against them.",
         ]) + """
      <h3>Nightmare in Amatsu, in the designer's words</h3>
      <p>The priestess has been slain hundreds of times. That was the prophecy, and
      it has been fulfilled. The samurai specter is no longer a single ghost - it is
      an army that came back to fight again after death. You will find the familiar
      boss there, with a twist. Not quite a ghost. Not quite summoned, either. And a
      second boss the team will not talk about.</p>
      <h3>Einherjar Challenge Mode</h3>
      <p>Your maximum level is locked. It only rises when you defeat a boss of the
      same level as you. Nobody can contest a spawn out from under your progression,
      because your progression <em>is</em> the fight.</p>
      <p>It awards costumes, not relics. The team considered handing out one of each
      relic per level and decided it would turn the mode into a min-maxing farm.
      Both modes have access to the entire game.</p>"""),

        ("story", "The story, and the lore underneath it",
         "Completely optional, and the only place instances still live.",
         wiki_block("Main_Story_Quest") + "\n      " +
         wiki_block("Grimoire_of_New-Midgard") + "\n      " +
         wiki_block("Main_Features", only=("A New Tale to read",))),
    ]
    doc_page("world.html",
             "World and Dungeons | Return to Morroc: Refuge",
             "New-Midgard region by region: all 21 distortion dungeons with levels and "
             "ranks, the MVP relic system, and the two SS dungeons built for the Refuge.",
             "world.html",
             "New-Midgard",
             "Regions, dungeons, distortions and MVPs - plus the endgame the Refuge "
             "built on top of them.",
             sections, "World",
             hero_cta='<a class="btn btn--ghost" href="guides.html">Access guides</a>')


def main():
    print("building reference pages")
    build_start()
    build_mechanics()
    build_gear()
    build_world()


if __name__ == "__main__":
    main()
