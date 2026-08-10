# -*- coding: utf-8 -*-
"""Generate the class tree overview and one page per class.

    python tools/build_classes.py

Reads tools/data/wiki.json (the inherited world, transcribed from the
community wiki) and tools/classes_meta.py (the tree, plus what the Refuge
changed). The two are never merged silently: wiki material is presented as
the world as it stands, and every Refuge change is rendered as a labelled
callout so a reader always knows which is which.
"""

import html
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chrome as C
import classes_meta as M

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = json.load(open(os.path.join(ROOT, "tools", "data", "wiki.json"), encoding="utf-8"))

# The game's own skill windows, by class slug. This is the authority for every
# skill name and description; the wiki is only a fallback for the two jobs
# that are too new to be in it.
ENCY = json.load(open(os.path.join(ROOT, "tools", "data", "encyclopedia.json"),
                      encoding="utf-8"))["classes"]

SKILL_TYPE_CLASS = {
    "passive": "sk-passive", "active": "sk-active",
    "physical": "sk-physical", "magic": "sk-magic", "magical": "sk-magic",
    "buff": "sk-support", "party-buff": "sk-support", "self-buff": "sk-support",
    "support": "sk-support", "supportive": "sk-support",
    "debuff": "sk-debuff", "summon": "sk-summon", "stance": "sk-stance",
    "toggle": "sk-stance",
}


def esc(s):
    return html.escape(s or "", quote=False)


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return rel


def t_(key, english):
    """A translatable label: emit the key alongside the English so the runtime
    can swap it. Returned as a pair, rendered as data-i18n + text."""
    return (key, english)


def name_of(slug):
    return M.NAMES.get(slug, slug)


# ---------------------------------------------------------------------------
# pulling a class out of the wiki data
# ---------------------------------------------------------------------------

def wiki_for(meta):
    """Return (prose_sections, skills) for one class."""
    page = meta.get("page")
    if not page or page not in WIKI:
        return [], []

    data = WIKI[page]
    want = meta.get("section")
    if not want:
        sections = data["sections"]
    else:
        # A class documented inside a shared page: its own heading, plus the
        # "<name> Skills" heading that sometimes follows it.
        sections = [s for s in data["sections"]
                    if s["title"] == want or s["title"].startswith(want + " ")]

    prose, skills = [], []
    for sec in sections:
        skills.extend(sec["skills"])
        if sec["paras"] or sec["bullets"]:
            prose.append(sec)
    return prose, skills


def type_class(kind):
    for key, val in SKILL_TYPE_CLASS.items():
        if key in (kind or "").lower():
            return val
    return "sk-other"


def game_rows(slug):
    """The skill table as the game itself writes it.

    Returns (html, count). Empty when the class is not in the encyclopedia,
    which is only true of the two jobs the Refuge added.
    """
    entry = ENCY.get(slug)
    if not entry or not entry["skills"]:
        return "", 0

    rows = []
    for sk in entry["skills"]:
        lines = [l for l in sk["desc"].split("\n") if l.strip()]
        desc = "".join("<p>%s</p>" % esc(l) for l in lines)
        meta = []
        if sk["target"]:
            meta.append('<span class="chip chip--sm">%s</span>' % esc(sk["target"]))
        if sk["needs"]:
            meta.append('<span class="skill-note">Needs %s</span>' % esc(sk["needs"]))
        rows.append(f"""        <tr data-row>
          <th scope="row">{esc(sk['name'])}<span class="skill-max mono">Lv {sk['max']}</span></th>
          <td>{desc}{('<div class="skill-extra">' + "".join(meta) + '</div>') if meta else ''}</td>
          <td><span class="badge {type_class(sk['type'])}">{esc(sk['type']) or 'Skill'}</span></td>
        </tr>""")
    return "\n".join(rows), len(entry["skills"])


def skill_rows(skills):
    rows = []
    for sk in skills:
        kind = (sk.get("type") or "").strip()
        cls = "sk-other"
        for key, val in SKILL_TYPE_CLASS.items():
            if key in kind.lower():
                cls = val
                break
        extra = " ".join(x for x in (sk.get("details"), sk.get("scaling")) if x and x != "None")
        detail = ""
        if sk.get("details") and sk["details"] != "None":
            detail += '<span class="skill-note">%s</span>' % esc(sk["details"])
        if sk.get("scaling") and sk["scaling"] != "None":
            detail += '<span class="chip chip--sm mono">%s</span>' % esc(sk["scaling"])
        rows.append(f"""        <tr data-row>
          <th scope="row">{esc(sk['name'])}<span class="skill-max mono">{esc(sk['max'])}</span></th>
          <td>{esc(sk['desc'])}{('<div class="skill-extra">' + detail + '</div>') if detail else ''}</td>
          <td><span class="badge {cls}">{esc(kind) or 'Skill'}</span></td>
        </tr>""")
    return "\n".join(rows), rows and extra


def own_html(meta):
    """Classes with no wiki page (Merchant, and the two new jobs) carry their
    own bullets here instead."""
    own = meta.get("own")
    if not own:
        return ""
    return ('<h2 data-i18n="ui.whatItIs">What it is</h2>\n      <ul>'
            + "".join("<li>%s</li>" % o for o in own) + "</ul>")


def prose_html(prose):
    out = []
    for sec in prose:
        title = sec["title"]
        if title.lower() in ("skills", ""):
            # A bare "Skills" heading has nothing under it worth printing.
            body = sec["paras"]
            if not body and not sec["bullets"]:
                continue
            title = ""
        block = []
        if title:
            block.append('<h2 id="%s">%s</h2>' % (slugify(title), esc(title)))
        for p in sec["paras"]:
            block.append("<p>%s</p>" % esc(p))
        if sec["bullets"]:
            block.append("<ul>" + "".join("<li>%s</li>" % esc(b) for b in sec["bullets"]) + "</ul>")
        out.append("\n      ".join(block))
    return "\n      ".join(out)


def slugify(s):
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in s).strip("-")


# ---------------------------------------------------------------------------
# the class page
# ---------------------------------------------------------------------------

def class_page(meta):
    slug = meta["slug"]
    name = name_of(slug)
    prose, skills = wiki_for(meta)
    rows, n_skills = game_rows(slug)
    from_game = bool(rows)
    if not rows:
        rows, _ = skill_rows(skills)
        n_skills = len(skills)
    tier = M.TIER_LABEL[meta["tier"]]

    facts = [(t_('ui.tier', 'Tier'), tier)]
    if meta["parents"]:
        facts.append((t_("ui.changesFrom", "Changes from"), " or ".join(
            '<a href="%s.html">%s</a>' % (p, name_of(p)) for p in meta["parents"])))
    if meta["leads_to"]:
        facts.append((t_("ui.leadsTo", "Leads to"), ", ".join(
            '<a href="%s.html">%s</a>' % (p, name_of(p)) for p in meta["leads_to"])))
    if meta.get("weapons") or (meta.get("page") and WIKI.get(meta["page"], {}).get("weapons")):
        w = meta.get("weapons") or WIKI[meta["page"]]["weapons"]
        facts.append((t_("ui.weapons", "Weapons"), esc(w)))

    fact_html = "\n".join(
        '        <div><dt data-i18n="%s">%s</dt><dd>%s</dd></div>' % (k[0], k[1], v) for k, v in facts)

    src = WIKI.get(meta.get("page") or "", {})
    verdict = ""
    if src.get("best") or src.get("worst"):
        verdict = f"""      <div class="verdict">
        <div class="verdict-col verdict-col--good">
          <h3 data-i18n="ui.strengths">Strengths</h3>
          <p>{esc(src.get('best', 'Not documented yet.'))}</p>
        </div>
        <div class="verdict-col verdict-col--bad">
          <h3 data-i18n="ui.weaknesses">Weaknesses</h3>
          <p>{esc(src.get('worst', 'Not documented yet.'))}</p>
        </div>
      </div>"""

    refuge = ""
    if meta["refuge"]:
        items = "".join("<li>%s</li>" % r for r in meta["refuge"])
        refuge = f"""      <aside class="callout callout--refuge" aria-labelledby="refuge-{slug}">
        <h2 id="refuge-{slug}" data-i18n="ui.refugeChanged">What the Refuge changed</h2>
        <ul>{items}</ul>
      </aside>"""

    skills_block = ""
    if rows:
        skills_block = f"""      <section class="section--tight" id="skills">
        <div class="section-head">
          <h2 data-i18n="ui.skills">Skills</h2>
          <p>What each one does, in the words the game itself uses.
             Numbers are deliberately left out - they move with every balance
             pass, and a page that quotes them goes stale the day one lands.</p>
        </div>
        <div class="cluster" style="margin-bottom:1rem">
          <label class="visually-hidden" for="sk">Filter skills</label>
          <input id="sk" type="search" class="field" placeholder="Filter skills..." data-i18n-attr="placeholder:ui.filterSkills"
                 data-filter="skilltable" data-filter-count="skcount">
          <span class="chip mono" id="skcount">-</span>
        </div>
        <div class="table-wrap">
          <table id="skilltable">
            <caption class="visually-hidden">{esc(name)} skills</caption>
            <thead><tr><th scope="col">Skill</th><th scope="col">What it does</th><th scope="col">Type</th></tr></thead>
            <tbody>
{rows}
            </tbody>
          </table>
        </div>
      </section>"""

    if from_game:
        source_note = ("Skill names and descriptions are read straight out of "
                       "the server's own skill windows, so they say exactly "
                       "what a player sees in game. Where the Refuge changed "
                       "something, it is called out above.")
    elif meta.get("page") is None:
        source_note = ("This job is new in the Refuge, so there is no inherited "
                       "documentation for it. Everything here comes from the "
                       "designer's own posts.")
    else:
        source_note = ("This job's skills are still being transcribed. Where "
                       "the Refuge changed something, it is called out above.")

    siblings = [c for c in M.CLASSES if c["tier"] == meta["tier"] and c["slug"] != slug][:6]
    sib_html = "".join(
        '<a class="pill" href="%s.html">%s</a>' % (s["slug"], name_of(s["slug"]))
        for s in siblings)

    trail = [("index.html", "Home"), ("classes.html", "Classes"), (None, name)]
    body = f"""<section class="page-hero page-hero--class">
  <div class="shell">
    {C.breadcrumbs("../", trail)}
    <p class="eyebrow">{tier}</p>
    <h1>{esc(name)}</h1>
    <p class="lede">{esc(meta['tagline'])}</p>
    <div class="cluster" style="margin-top:1.4rem">
      <a class="btn btn--primary" href="{C.DISCORD}" rel="noopener" data-i18n="cta.join">Join the community server</a>
      <a class="btn btn--ghost" href="../classes.html">Full class tree</a>
      {'<a class="btn btn--ghost" href="#skills">Skills</a>' if rows else ''}
    </div>
  </div>
</section>

<div class="shell class-body">
  <article class="prose">
{refuge}
    <dl class="factbar">
{fact_html}
    </dl>
{verdict}
    <div class="prose-flow">
      {prose_html(prose) or own_html(meta)}
    </div>
{skills_block}
    <p class="source-note">{source_note}</p>
    <nav class="pill-row" aria-label="Other {tier.lower()}s">
      <span class="dim">More {tier.lower()}s:</span> {sib_html}
      <a class="pill pill--strong" href="../classes.html">Full tree</a>
    </nav>
  </article>
</div>
"""

    title = "%s | Return to Morroc: Refuge" % name
    desc = ("%s in Return to Morroc: Refuge - %s Skill list, strengths, weaknesses "
            "and what the rebuild changed." % (name, meta["tagline"]))
    desc = desc[:174]
    html_out = C.head("../", title, desc, "classes/%s.html" % slug,
                      extra_ld=C.crumb_ld(trail))
    html_out += C.header("../", "classes.html")
    html_out += '<main id="main">\n' + body + "\n</main>\n"
    html_out += C.footer("../")
    return write("classes/%s.html" % slug, html_out)


# ---------------------------------------------------------------------------
# the overview
# ---------------------------------------------------------------------------

def node(slug):
    meta = M.BY_SLUG[slug]
    new = ' <span class="badge tag-added">New</span>' if meta.get("page") is None else ""
    return (f'      <a class="node node--{meta["tier"]}" href="classes/{slug}.html">'
            f'<span class="node-name">{esc(name_of(slug))}{new}</span>'
            f'<span class="node-tag">{esc(meta["tagline"])}</span></a>')


def overview():
    blocks = []
    for title, blurb, rows in M.TREE:
        row_html = []
        for i, row in enumerate(rows):
            if i:
                row_html.append('    <div class="tree-link" aria-hidden="true"></div>')
            row_html.append('    <div class="tree-row">\n' + "\n".join(node(s) for s in row) + "\n    </div>")
        blocks.append(f"""  <section class="tree-group reveal">
    <div class="tree-head">
      <h2>{title}</h2>
      <p>{blurb}</p>
    </div>
{chr(10).join(row_html)}
  </section>""")

    counts = {}
    for c in M.CLASSES:
        counts[c["tier"]] = counts.get(c["tier"], 0) + 1

    body = f"""<section class="page-hero">
  <div class="shell">
    {C.breadcrumbs("", [("index.html", "Home"), (None, "Classes")])}
    <h1>{len(M.CLASSES)} classes, seven roads</h1>
    <p class="lede">
      Everyone starts as an Orphan. Where you go after job level 10 decides how
      the next hundred and forty levels feel - and two of these roads did not
      exist before the Refuge.
    </p>
  </div>
</section>

<section class="section section--tight">
  <div class="shell">
    <div class="panel reveal">
      <p>
        <strong>Job shadow sets are gone.</strong> In the original, every job had
        its own mandatory set past level 100 and it decided your build for you.
        The Refuge removed them and replaced them with more than fifty
        dungeon-based sets that any job can wear. Every page below is written
        with that already true.
      </p>
    </div>
  </div>
</section>

<div class="shell tree">
  <section class="tree-group tree-group--root reveal">
    <div class="tree-head">
      <h2>Everyone starts here</h2>
      <p>Ten job levels as an Orphan and the whole tree opens. The Orphan's own
      skills stay with you for all one hundred and fifty levels, which is why the
      Refuge rebuilt four of them before touching anything else.</p>
    </div>
    <div class="tree-row tree-row--single">
{node("orphan")}
    </div>
  </section>
{chr(10).join(blocks)}
</div>

<section class="section section--tight">
  <div class="shell">
    <div class="cta-band reveal">
      <h2>Not sure where to start?</h2>
      <p>Thief is the main road and the most forgiving. Ronin, Jester and the Expert jobs are explicitly not recommended for a first character.</p>
      <div class="cluster">
        <a class="btn btn--primary" href="start.html">Read the new player guide</a>
        <a class="btn btn--ghost" href="newjobs.html">See the two new jobs</a>
      </div>
    </div>
  </div>
</section>
"""
    trail = [("index.html", "Home"), (None, "Classes")]
    out = C.head("", "Classes | Return to Morroc: Refuge",
                 "All %d classes in the Refuge laid out as a tree: seven roads from Orphan, "
                 "eight final jobs on the main line, and two jobs that are new." % len(M.CLASSES),
                 "classes.html", extra_ld=C.crumb_ld(trail))
    out += C.header("", "classes.html")
    out += '<main id="main">\n' + body + "\n</main>\n"
    out += C.footer("")
    return write("classes.html", out)


def main():
    print("building classes")
    print("  wrote", overview())
    for meta in M.CLASSES:
        class_page(meta)
    print("  wrote %d class pages" % len(M.CLASSES))


if __name__ == "__main__":
    main()
