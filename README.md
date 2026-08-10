# Return to Morroc: Refuge — site

Static site for the Refuge. 56 pages, no framework, no bundler, no build step
on the host. What is committed is exactly what the browser receives.

Live at <https://rtmrefuge.pages.dev>.

```
tools/*.py  →  *.html  →  git push  →  static host serves the file
```

## Running it

```bash
python -m http.server 4410
```

Then open <http://localhost:4410>. There is nothing to install.

## Rebuilding

```bash
python build.py
```

That runs every step in the order they depend on each other and stops on the
first failure. The steps individually, if you need one:

| Step | Produces |
| --- | --- |
| `tools/build.py` | home, server, changes, guides, join, faq, newjobs, 404 |
| `tools/build_docs.py` | start / mechanics / gear / world |
| `tools/build_classes.py` | the tree and 42 class pages |
| `tools/build_database.py` | `database.html` and its two JSON payloads |
| `tools/build_meta.py` | sitemap, robots, llms.txt |
| `tools/build_search.py` | the search index |
| `tools/check.py` | the validator - run before every commit |
| `tools/check_i18n.py` | translation coverage |

`build_meta.py` and `build_search.py` read the pages the earlier steps wrote,
so they cannot move earlier in that list.

Three extraction steps sit outside the normal build because they read things
that are not in this repository. Everything they write is committed, so a
normal build is offline and a re-fetch shows up as a readable diff of what
actually changed upstream.

- `tools/fetch_encyclopedia.py` pulls the team's own internal tool into
  `tools/data/encyclopedia.json`: 2,622 items with the description the game
  itself shows, 719 monsters with their drops, zones and card effects, and 40
  classes with 477 skills. **This is the primary source for the database and
  for every skill table.** The internal tool also carries staff balance notes
  and a user list; neither is read and neither is written out.
- `tools/fetch_sprites.py` vendors the 718 monster sprites into
  `assets/sprites/`, so seven hundred images do not depend on somebody else's
  Pages deployment staying up.
- `tools/extract_gamedata.py` reads the emulator's rAthena tables (the
  checkout next to this one) into `tools/data/game.json`. It is now only a
  *secondary* source: the numbers the encyclopedia does not carry - monster
  experience, attack and defence, and an item's job restrictions. Its `script`
  column is never written to the site. See "Descriptions, not formulas".
- `tools/fetch_wiki.py` downloads the wiki for the world the Refuge inherited
  into `tools/data/raw/` and parses it into `tools/data/wiki.json`. Since the
  encyclopedia landed this is a fallback only - it covers the prose sections
  and the two jobs too new to be in the game's own data. Run
  `python tools/fetch_wiki.py --parse-only` to re-parse without re-downloading.

## Descriptions, not formulas

The database used to print the emulator's `script` column, which reads
`bonus2 bSkillAtk,"LG_RAYOFGENESIS",4*(.@r)`. That is reference material for a
wiki, not a description, and it was on eleven thousand rows.

What the site prints now is the text the game puts in front of a player, and
the extraction splits every description in two:

- **What it does** - the sentences. This is what the pages render.
- **What it scales by** - `Damage is 100+25% per level +2% per LUK`,
  `Duration is 10 seconds per level`. Kept in `encyclopedia.json` under
  `numbers`, printed nowhere. Scaling moves with every balance pass, and a
  static page that quotes it goes stale the day one lands; the wiki can be
  corrected the same afternoon.

`SKILL_NUMBERS` and `SKILL_FORMULA` in `tools/fetch_encyclopedia.py` are the
split. `SCRIPTS` in `tools/check.py` is the guard: the build fails if bonus
script, a `getrefine()` call or an `.@variable` reaches any page again.

## Where things live

| Path | What it is |
| --- | --- |
| `tools/chrome.py` | `head()`, `header()`, `footer()`, breadcrumbs, JSON-LD helpers. The nav lives here once. |
| `tools/data.py` | Refuge-specific content: dungeon list, FAQ, timeline, change buckets. |
| `tools/classes_meta.py` | The class tree, and what the Refuge changed about each class. |
| `tools/data/encyclopedia.json` | Items, monsters and skills from the team's own tool. The primary source. Generated - do not hand-edit. |
| `tools/fetch_encyclopedia.py` | Pulls and cleans that file. |
| `tools/fetch_sprites.py` | Vendors the monster sprites into `assets/sprites/` |
| `tools/data/wiki.json` | The inherited world, parsed from the wiki. Fallback only. Generated - do not hand-edit. |
| `tools/fetch_wiki.py` | Downloads and parses that wiki. |
| `tools/build.py` | Home and the short pages. One function each. |
| `tools/build_docs.py` | The four long reference pages, assembled from wiki sections. |
| `tools/build_classes.py` | `classes.html` and `classes/*.html` |
| `tools/build_search.py` | `assets/data/search.json` - the search index. Runs last. |
| `tools/extract_gamedata.py` | Reads the emulator's YAML into `tools/data/game.json`. Secondary - numbers only. |
| `tools/build_database.py` | `database.html` + `assets/data/db-items.json` and `db-mobs.json` |
| `tools/check_i18n.py` | Fails if the markup uses a key no locale defines |
| `assets/i18n/pt.js` | Portuguese table. Add a language by copying this file. |
| `tools/build_meta.py` | sitemap, robots, llms.txt |
| `tools/check.py` | The pre-commit validator |
| `tools/set_domain.py` | Move the site to a different origin in one command |
| `assets/css/style.css` | The whole design system. Section 1 is the tokens; nothing else writes a colour. |
| `assets/js/main.js` | Theme toggle, mobile drawer, scroll reveal, list filters, copy buttons. All of it optional. |

To add a nav link, edit `NAV` in `tools/chrome.py`. To correct something the
Refuge changed, edit `refuge=[...]` for that class in `tools/classes_meta.py`,
or the relevant `callout(...)` in `tools/build_docs.py`. Never edit a generated
`.html` directly, and never hand-edit `tools/data/wiki.json` — the next build or
fetch overwrites both.

### Two sources, never blended

The site carries two kinds of material and the distinction is load-bearing:

- **Inherited.** System pages and prose sections transcribed from the wiki for
  the world the Refuge is rebuilding. Skill tables no longer come from here -
  they come from the game.
- **Refuge.** Everything the current team changed, from their own public posts.

Refuge material is always rendered as a purple *"What the Refuge changed"*
callout placed **above** the inherited text, never merged into it. A reader can
always tell which lines predate the rebuild. Where the other server documented
its own additions rather than the shared world — its experience rates, most
obviously — those sections are dropped by name in `DROP` in
`tools/build_docs.py` instead of being reworded into something that would read
as a claim about this server.

## Deploying

Any static host. Cloudflare Pages, Netlify or GitHub Pages all work with zero
configuration; `_headers` is written for Cloudflare Pages and Netlify.

- Build command: *(none)*
- Output directory: `/`

**Set the real domain before the first deploy**, otherwise every canonical link
and the sitemap point at the placeholder:

```bash
python tools/set_domain.py https://your-domain.example
```

That rewrites `SITE` in `tools/chrome.py` and rebuilds everything so the
canonical tags, Open Graph URLs, sitemap, robots.txt and llms.txt all move
together.

### Cache policy

`_headers` caches `/assets/img/*` for a year (those filenames are never reused)
and everything else for an hour with revalidation. The share card deliberately
lives in `/assets/social/` rather than `/assets/img/` because it gets replaced
under the same filename whenever the branding changes — a year of immutable
caching there means chat clients keep showing last year's card. Cloudflare Pages
also *merges* matching header blocks instead of picking the most specific one,
so no path may be covered by two blocks that both set `Cache-Control`.

## Content and naming policy

This is an unofficial, non-commercial fan project. The site is written to be
unambiguous about that, and the wording is a deliberate choice rather than an
accident:

- The copy describes the world in generic genre terms — *custom fantasy MMO
  world*, *classic MMO* — and never uses another company's brand, product name
  or trademark, in visible text, in metadata, or in the page title.
- No official artwork, logo, font or UI asset is used anywhere. The mark is the
  project's own.
- Every page carries the disclaimer in the footer: no affiliation, no
  sponsorship, no endorsement, no real-money trading, and never selling power.
- Third-party names that do appear (skill names, map names) are there only to
  describe gameplay, which is what the footer says.

`tools/check.py` enforces the first point mechanically — it fails the build if a
forbidden term reappears in any page. The list is `FORBIDDEN` at the top of that
file. If a term genuinely needs to be used, change the list on purpose rather
than deleting the check.

The inherited wiki text does name a trademark in a handful of sentences, so
`SCRUB` in `tools/fetch_wiki.py` rewrites those sentences to say the same thing
generically at parse time. Each phrasing needs its own entry — a blanket
substitution turns *"vanilla RO Paladin"* into gibberish. `TYPOS` in the same
file fixes the wiki's spelling errors there rather than in `data/raw/`, so the
next fetch cannot silently undo them.

The practical effect on search is that the site ranks for what it actually is —
its own name, its own systems, its own dungeon names — and not for someone
else's trademark. That is both the safer position and the more honest one.

## Sources

Three sources, all of them other people's work:

- **The development team's own public posts** (Ornstein, croc and Metta,
  May–August 2026) in the project's community server. Everything marked as a
  Refuge change comes from here.
- **The team's own internal encyclopedia**, for every item, monster, drop and
  skill. This is the most accurate source that exists, because it is not a
  transcription of anything - it is the text the game itself displays, kept by
  the people changing it.
- **The server's own emulator tables**, for the numbers the encyclopedia does
  not carry.
- **The wiki** for the world the Refuge is rebuilding, for the inherited
  system pages and the prose sections. That wiki belongs to another server
  built from the same origin; it is credited here and nowhere on the site,
  which links to no competitor and names none. `tools/check.py` fails the
  build if a link to it reappears.
- **Two community-written guides**, credited and linked on the guides page.

Where a number was posted as work-in-progress, the page says so. Nothing was
invented to fill a gap, and where the wiki and the posts disagree, the posts
win and the difference is shown rather than resolved silently.

## Saying the right thing about money

The site used to promise there would never be a cash shop. That promise cannot
be kept: hosting costs money and the people building this are doing real work.
The copy now says the thing that *can* be held, everywhere it comes up:

- **Free to play.** True today and intended to stay true.
- **Never sells power.** No stats, no gear advantage, no buyable progression.
  This is the load-bearing promise and it is stated in absolute terms.
- **No real-money trading.** Also absolute.
- **Funding is undecided and will be discussed with the community before it
  ships**, not announced at them.

If you edit this, keep those four apart. "No cash shop" is not one of them, and
`llms.txt` explicitly tells language models not to claim it.

## House style

- LF line endings everywhere (`.gitattributes` enforces it).
- No em dashes in generated copy; `check.py` fails on them.
- One `<h1>` per page, `<title>` under 65 characters, `description` between 70
  and 175.
- Every `<img>` carries `alt`, `width` and `height`.
- Contrast is checked with numbers, not by eye. The floor is 4.5:1 in both
  themes, and it has caught three colours so far.
- The logo is never recoloured per theme. It is artwork on a black field, cut
  to a circle; on the light theme it simply reads as a black medallion.
- Headings above `h3` use the Art Nouveau display face. `h3` and below use
  Atkinson Hyperlegible, because a decorative face stops helping at that size.
- Comments explain *why*, not *what*.

## Interface notes

**Glass.** Every raised surface composes one set of tokens (`--glass-fill`,
`--glass-edge`, `--glass-shine`, `--glass-blur`) in section 15 of the
stylesheet. Change those four and the whole site changes together. Nested
glass reads as mud, so a pane inside a pane drops its blur and keeps only its
edge, and `@supports not (backdrop-filter)` falls back to an opaque surface
rather than an unreadable transparent one.

**Aurora.** The home page and the 404 carry a fixed CSS backdrop: three broad
colour fields drifting behind a heavy blur. No canvas, no WebGL, no library.
Only `transform` and `opacity` animate — animating a gradient's colour stops
repaints the whole layer every frame — and `prefers-reduced-motion` keeps the
colour while dropping the drift.

**Search.** `assets/data/search.json` is 529 rows: every page, every reference
section, every class, all 423 skills and all 21 dungeons. The UI is built at
runtime so no page ships markup for it, and the index is warmed on
`pointerenter` of the button so the first open feels instant. Ranking weights
by group and then caps each group at 7 results — without the cap, 423 skills
bury the one page that answers the question. `/` and `Ctrl/Cmd+K` both open it.

**The database.** Eleven thousand items and two thousand monsters, filtered
in the browser with no server. Three things make that work: the payload is
column arrays with string tables rather than objects (a third of the bytes);
each row carries one pre-folded lowercase string so a keystroke scans numbers
rather than objects; and nothing is painted until it is near the viewport, so
a filter matching five thousand rows renders sixty. Drops resolve in both
directions - an item lists what drops it, a monster lists what it drops - and
the open entry is in the URL, so any row is linkable without being a file.

**Translations.** English lives in the HTML; there is no `en.js`, because what
a crawler indexes has to be the real markup. Other languages are tables loaded
on demand, and a missing key falls back to the English snapshot taken at boot,
so a half-finished translation degrades word by word instead of printing
`undefined`. Scope is deliberate and worth defending: navigation, footer,
interface labels, the home page and the shared callout headings are
translated; skill descriptions, levelling spots and the wiki-derived system
pages are not, because those are the exact strings people search for and the
exact strings the game itself shows.
