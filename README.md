# Return to Morroc: Refuge — site

Static site for the Refuge. Ten pages, no framework, no bundler, no build step
on the host. What is committed is exactly what the browser receives.

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
python tools/build.py        # every HTML page
python tools/build_meta.py   # sitemap.xml, robots.txt, llms.txt (run second)
python tools/check.py        # validate before committing
```

`build_meta.py` reads the pages the first script produced, so the order matters.
`check.py` exits non-zero and lists what is wrong; run it before every commit.

## Where things live

| Path | What it is |
| --- | --- |
| `tools/chrome.py` | `head()`, `header()`, `footer()`, breadcrumbs, JSON-LD helpers. The nav lives here once. |
| `tools/data.py` | All content that appears more than once: job changes, dungeon list, FAQ, timeline. |
| `tools/build.py` | Page bodies. One function per page. |
| `tools/build_meta.py` | sitemap, robots, llms.txt |
| `tools/check.py` | The pre-commit validator |
| `tools/set_domain.py` | Move the site to a different origin in one command |
| `assets/css/style.css` | The whole design system. Section 1 is the tokens; nothing else writes a colour. |
| `assets/js/main.js` | Theme toggle, mobile drawer, scroll reveal, list filters, copy buttons. All of it optional. |

To add a nav link, edit `NAV` in `tools/chrome.py` and rebuild. To fix a skill
number, edit `tools/data.py` and rebuild. Never edit the generated `.html`
directly — the next build overwrites it.

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

The practical effect on search is that the site ranks for what it actually is —
its own name, its own systems, its own dungeon names — and not for someone
else's trademark. That is both the safer position and the more honest one.

## Sources

Everything on the site is transcribed from public posts by the development team
(Ornstein, croc and Metta, May–August 2026) in the project's community server,
plus two community-written guides which are credited and linked on the guides
page. Where a number was posted as work-in-progress, the page says so. Nothing
was invented to fill a gap.

## House style

- LF line endings everywhere (`.gitattributes` enforces it).
- No em dashes in generated copy; `check.py` fails on them.
- One `<h1>` per page, `<title>` under 65 characters, `description` between 70
  and 175.
- Every `<img>` carries `alt`, `width` and `height`.
- Contrast is checked with numbers, not by eye. The floor is 4.5:1 in both
  themes.
- Comments explain *why*, not *what*.
