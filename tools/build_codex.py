# -*- coding: utf-8 -*-
"""Build codex.html and the shared term table.

    python tools/build_codex.py

Writes:

    codex.html               the glossary page
    assets/data/codex.json   the same terms, for database.js to mark up

Also exposes mark(), which build_classes.py uses to underline the terms in
every skill description at build time. The database does the same thing at
runtime because its text arrives with the payload.
"""

import html
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chrome as C
import codex as K

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def esc(s):
    return html.escape(s or "", quote=False)


def write(rel, text, quiet=False):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path) or ROOT, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    if not quiet:
        print("  wrote %s - %d kb" % (rel, os.path.getsize(path) // 1024))


# ---------------------------------------------------------------------------
# marking terms in a body of text
# ---------------------------------------------------------------------------

def _pattern():
    table = K.lookup()
    # Longest first: "Magic Defense Pierce" must win over "Defense Pierce".
    spellings = sorted(table, key=len, reverse=True)
    return table, re.compile(
        r"(?<![\w-])(%s)(?![\w-])" % "|".join(re.escape(s) for s in spellings))


TABLE, TERM_RE = _pattern()


def mark(text, prefix=""):
    """Wrap every known term in already-escaped text.

    Takes escaped text and returns escaped text with markup added, so it can
    be dropped straight into a template. Nothing here introduces a tag that
    the caller did not already have.
    """
    if not text:
        return text

    def sub(m):
        slug, term, definition, hue = TABLE[m.group(1)]
        return ('<a class="term term--%s" href="%scodex.html#%s" title="%s">%s</a>'
                % (hue, prefix, slug, esc(definition).replace('"', "&quot;"),
                   m.group(1)))

    return TERM_RE.sub(sub, text)


# ---------------------------------------------------------------------------
# the page
# ---------------------------------------------------------------------------

def build_page():
    blocks = []
    for key, title, hue, blurb, terms in K.GROUPS:
        rows = []
        for slug, term, definition in terms:
            rows.append(
                '        <div class="codex-row" id="%s" data-row>\n'
                '          <dt><span class="term term--%s term--static">%s</span></dt>\n'
                '          <dd>%s</dd>\n'
                '        </div>' % (slug, hue, esc(term), esc(definition)))
        blocks.append(
            '    <section class="codex-group codex-group--%s" id="g-%s" data-filter-group>\n'
            '      <h2>%s</h2>\n'
            '      <p class="codex-blurb">%s</p>\n'
            '      <dl class="codex-list">\n%s\n      </dl>\n'
            '    </section>' % (hue, key, esc(title), esc(blurb), "\n".join(rows)))

    jump = "".join(
        '<a class="pill" href="#g-%s">%s</a>' % (key, esc(title))
        for key, title, _h, _b, _t in K.GROUPS)

    trail = [("index.html", "Home"), (None, "Codex")]
    body = """<section class="page-hero page-hero--tight">
  <div class="shell">
    %s
    <h1 data-i18n="codex.h1">Codex</h1>
    <p class="lede" data-i18n="codex.lede">
      Item and skill descriptions are written for people who already play.
      These are the words they lean on, in plain language. Wherever one of them
      turns up on this site it is underlined in its own colour, and it links
      back here.
    </p>
    <div class="pill-row" style="margin-top:1.4rem">%s</div>
  </div>
</section>

<div class="shell codex">
  <div class="codex-tools">
    <label class="visually-hidden" for="codex-q">Filter</label>
    <input id="codex-q" class="field" type="search" autocomplete="off"
           placeholder="Filter the codex..." data-i18n-attr="placeholder:codex.filter"
           data-filter="codex-body" data-filter-empty="codex-empty">
  </div>
  <div id="codex-body">
%s
  </div>
  <p class="codex-empty" id="codex-empty" hidden data-i18n="codex.empty">
    Nothing by that name. Try the database instead.
  </p>
</div>
""" % (C.breadcrumbs("", trail), jump, "\n".join(blocks))

    out = C.head("", "Codex | Return to Morroc: Refuge",
                 "Every recurring word in the game's item and skill text, "
                 "explained in one line: combo windows, cast timing, gear "
                 "bonuses, status effects and the six stats.",
                 "codex.html", extra_ld=C.crumb_ld(trail))
    out += C.header("", "codex.html")
    out += '<main id="main">\n' + body + "\n</main>\n"
    out += C.footer("")
    write("codex.html", out)


def build_data():
    """The same table, for the database to mark up its own text at runtime."""
    terms = []
    for slug, term, definition, _key, hue in K.entries():
        for spelling in [term] + K.ALIASES.get(slug, []):
            terms.append([spelling, slug, definition, hue])
    terms.sort(key=lambda t: len(t[0]), reverse=True)
    write("assets/data/codex.json",
          json.dumps({"terms": terms}, ensure_ascii=False,
                     separators=(",", ":")) + "\n")
    return len(list(K.entries())), len(terms)


if __name__ == "__main__":
    print("building codex")
    n_terms, n_spellings = build_data()
    build_page()
    print("  %d terms, %d spellings, %d groups"
          % (n_terms, n_spellings, len(K.GROUPS)))
