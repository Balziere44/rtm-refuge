# Return to Morroc: Refuge — site

Static site for the Refuge. 54 pages, no framework, no bundler, no build step
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
python tools/build.py          # home and the short pages
python tools/build_docs.py     # start / mechanics / gear / world
python tools/build_classes.py  # the tree, plus 41 class pages
python tools/build_meta.py     # sitemap.xml, robots.txt, llms.txt (run last)
python tools/check.py          # validate before committing
```

`build_meta.py` reads the pages the other scripts produced, so it goes last.
`check.py` exits non-zero and lists what is wrong; run it before every commit.

`tools/fetch_wiki.py` is separate and touches the network. It downloads the
community wiki for the world the Refuge inherited into `tools/data/raw/` and
parses it into `tools/data/wiki.json`. Both are committed, so a normal build is
offline and a re-fetch shows up as a readable diff of what the wiki changed.
Run `python tools/fetch_wiki.py --parse-only` to re-parse without re-downloading.

## Where things live

| Path | What it is |
| --- | --- |
| `tools/chrome.py` | `head()`, `header()`, `footer()`, breadcrumbs, JSON-LD helpers. The nav lives here once. |
| `tools/data.py` | Refuge-specific content: dungeon list, FAQ, timeline, change buckets. |
| `tools/classes_meta.py` | The class tree, and what the Refuge changed about each class. |
| `tools/data/wiki.json` | The inherited world, parsed from the community wiki. Generated - do not hand-edit. |
| `tools/fetch_wiki.py` | Downloads and parses that wiki. The only networked script. |
| `tools/build.py` | Home and the short pages. One function each. |
| `tools/build_docs.py` | The four long reference pages, assembled from wiki sections. |
| `tools/build_classes.py` | `classes.html` and `classes/*.html` |
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

- **Inherited.** Descriptions, skill tables and system pages transcribed from
  the community wiki for the world the Refuge is rebuilding.
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
  sponsorship, no endorsement, nothing sold, no real-money trading.
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
- **The community wiki** for the world the Refuge is rebuilding, for the
  inherited systems, regions and skill tables. 77 pages, 424 skill rows.
- **Two community-written guides**, credited and linked on the guides page.

Where a number was posted as work-in-progress, the page says so. Nothing was
invented to fill a gap, and where the wiki and the posts disagree, the posts
win and the difference is shown rather than resolved silently.

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
