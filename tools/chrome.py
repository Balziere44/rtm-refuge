# -*- coding: utf-8 -*-
"""Shared page chrome for the Refuge site.

Every page is generated, so the header, footer and <head> exist exactly once.
That is the whole reason for this file: adding a nav link used to mean editing
nine files and forgetting two of them.

`prefix` is the relative path back to the site root ("" at the root, "../" one
level down). Keeping URLs relative means the site works from a subfolder, from
a file:// preview and from the final domain without a rebuild.
"""

# The canonical origin. tools/set_domain.py rewrites this and every generated
# file, so moving to a real domain later is one command, not a find-replace.
SITE = "https://rtmrefuge.pages.dev"

DISCORD = "https://discord.gg/a5P3PFNMhn"


# House style, applied to every line of text the build re-typesets: our own
# copy, the inherited wiki, and the game's own item and skill descriptions.
#
# All three sources separate a thing from its description with a spaced hyphen
# ("Insect Wings - Movement speed garment", "Fire - Burning chance"). Every
# other page uses a colon for that. The em dash is already banned by check.py;
# this is the same rule applied to the mark that was standing in for it.
# Swapping the glyph changes no meaning: what is on the left is still being
# defined by what is on the right.
import re as _re

_DASH = _re.compile(r"(?<=[^\s-]) - (?=\S)")


def house_style(line):
    return _DASH.sub(": ", line or "")


def _og_version():
    """A short hash of the share card, appended to its URL.

    Chat clients cache a link preview by image URL and hold it for a day or
    more, so redrawing the card under the same name means nobody sees the new
    one until their cache expires. Changing the URL whenever the bytes change
    is what makes a redraw visible the same afternoon.
    """
    import hashlib
    import os
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "assets", "social", "og-cover.jpg")
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as fh:
        return "?v=" + hashlib.sha1(fh.read()).hexdigest()[:8]


OG_V = _og_version()

# Deliberate wording note (see README): the site describes itself with generic
# genre vocabulary and never uses a publisher's brand name, product name or
# artwork. This is a fan project with no affiliation to any company, and the
# copy is written so that it cannot be mistaken for one.
BRAND = "Return to Morroc: Refuge"
SHORT = "RTM: Refuge"

# The top row is a table of contents, not an index of every page.
#
# Eleven flat links needed 1180px before they collapsed, and a reader scanning
# them had to hold eleven options in their head to find one. Three groups do
# not: you decide "the game" first and read five short labels second. The mark
# is the home link, so Home does not need a slot of its own.
#
# (key, label, href, children). A group carries no href of its own - it opens.
NAV = [
    ("nav.start", "Start Here", "start.html", []),
    ("nav.about", "The Server", None, [
        ("nav.server", "What the Refuge is", "server.html"),
        ("nav.changes", "What changed", "changes.html"),
        ("nav.faq", "Questions", "faq.html"),
    ]),
    ("nav.game", "The Game", None, [
        ("nav.classes", "Classes", "classes.html"),
        ("nav.newjobs", "Two new jobs", "newjobs.html"),
        ("nav.mechanics", "Combat and stats", "mechanics.html"),
        ("nav.gear", "Gear", "gear.html"),
        ("nav.world", "World", "world.html"),
    ]),
    ("nav.reference", "Reference", None, [
        ("nav.database", "Database", "database.html"),
        ("nav.codex", "Codex", "codex.html"),
        ("nav.guides", "Guides", "guides.html"),
    ]),
    ("nav.join", "Join", "join.html", []),
]

CARET = ('<svg class="nav-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2.2" aria-hidden="true"><path d="M6 9l6 6 6-6" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')

FOOTER_COLUMNS = [
    ("Start here", [
        ("server.html", "What the Refuge is"),
        ("start.html", "New player guide"),
        ("join.html", "How to join"),
        ("faq.html", "Questions and answers"),
    ]),
    ("The game", [
        ("classes.html", "All 42 classes"),
        ("newjobs.html", "Bouncer and Pit Boss"),
        ("mechanics.html", "Combat and stats"),
        ("gear.html", "Items, refining, shadows"),
        ("world.html", "Regions, dungeons, MVPs"),
    ]),
    ("Reference", [
        ("changes.html", "Changes from the original"),
        ("database.html", "Items and monsters"),
        ("codex.html", "What the words mean"),
        ("guides.html", "Player-written guides"),
        ("llms.txt", "llms.txt"),
        ("sitemap.xml", "Sitemap"),
    ]),
]

# Amarante is one of Google's Art Nouveau families and carries the decorative
# headings; Atkinson Hyperlegible was designed for low-vision readability and
# does the actual reading. One decorative face, one legible face, one mono for
# labels - nothing else gets loaded.
FONTS = ("https://fonts.googleapis.com/css2?family=Amarante&"
         "family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&"
         "family=JetBrains+Mono:wght@400;500&display=swap")


def head(prefix, title, description, canonical, extra_ld="", preload_hero=False):
    """The <head> plus the opening <body> and skip link.

    `canonical` is a path relative to the site root, e.g. "" or "world.html".
    """
    url = SITE + "/" + canonical
    hero = ('\n<link rel="preload" as="image" href="%sassets/img/mark-900.png" fetchpriority="high">'
            % prefix) if preload_hero else ""
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">

<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">
<meta name="theme-color" content="#06040a">
<meta name="theme-color" content="#06040a" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#f2f0f5" media="(prefers-color-scheme: light)">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="en_US">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{SITE}/assets/social/og-cover.jpg{OG_V}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{BRAND}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{SITE}/assets/social/og-cover.jpg{OG_V}">

<link rel="icon" href="{prefix}assets/img/icon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="{prefix}assets/img/icon-180.png">
<link rel="manifest" href="{prefix}site.webmanifest">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>{hero}
<link rel="stylesheet" href="{prefix}assets/css/style.css">
<link rel="stylesheet" media="print" onload="this.media='all'" href="{FONTS}">
<noscript><link rel="stylesheet" href="{FONTS}"></noscript>

<script>
/* The only blocking script on the site. It has to run before the first paint
   or the wrong theme shows for a frame. */
(function () {{
  try {{
    var t = localStorage.getItem('rtmr-theme');
    if (!t) t = matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
    document.documentElement.dataset.theme = t;
  }} catch (e) {{}}
}})();
</script>
{extra_ld}</head>
<body>
<a class="skip-link" href="#main" data-i18n="a11y.skip">Skip to content</a>
"""


CURRENT = ' aria-current="page"'


def _sub_links(prefix, active, kids, indent):
    pad = " " * indent
    return "\n".join(
        '%s<a href="%s%s"%s data-i18n="%s">%s</a>'
        % (pad, prefix, href, CURRENT if href == active else "", key, label)
        for key, label, href in kids)


def _nav_bar(prefix, active):
    """The desktop row. A group is a button plus a panel underneath it."""
    out = []
    for key, label, href, kids in NAV:
        if not kids:
            cls = "nav-top nav-cta" if key == "nav.join" else "nav-top"
            out.append('      <a class="%s" href="%s%s"%s data-i18n="%s">%s</a>'
                       % (cls, prefix, href,
                          CURRENT if href == active else "", key, label))
            continue
        here = ' data-here="true"' if any(k[2] == active for k in kids) else ""
        out.append(
            '      <div class="nav-group" data-open="false">\n'
            '        <button class="nav-top" type="button" data-nav-group\n'
            '                aria-expanded="false"%s data-i18n="%s">%s%s</button>\n'
            '        <div class="nav-menu">\n%s\n        </div>\n'
            '      </div>'
            % (here, key, label, CARET, _sub_links(prefix, active, kids, 10)))
    return "\n".join(out)


def _nav_drawer(prefix, active):
    """The phone version. Groups start closed unless you are inside one, which
    is the same bargain the desktop row makes."""
    out = []
    for key, label, href, kids in NAV:
        if not kids:
            out.append('      <a href="%s%s"%s data-i18n="%s">%s</a>'
                       % (prefix, href,
                          CURRENT if href == active else "", key, label))
            continue
        here = " open" if any(k[2] == active for k in kids) else ""
        out.append(
            '      <details class="drawer-group"%s>\n'
            '        <summary data-i18n="%s">%s</summary>\n'
            '        <div class="drawer-group-body">\n%s\n        </div>\n'
            '      </details>'
            % (here, key, label, _sub_links(prefix, active, kids, 10)))
    return "\n".join(out)


def header(prefix, active):
    return f"""<header class="site-header">
  <div class="shell header-inner">
    <a class="brand" href="{prefix}index.html">
      <img class="mark" src="{prefix}assets/img/icon-192.png" width="34" height="34" alt="" aria-hidden="true">
      <span class="brand-text">
        <span class="brand-name">RETURN TO MORROC</span>
        <span class="brand-sub">Refuge</span>
      </span>
    </a>
    <!-- NAV:START -->
    <nav class="nav" aria-label="Main">
{_nav_bar(prefix, active)}
    </nav>
    <!-- NAV:END -->
    <div class="header-actions">
      <button class="icon-btn search-btn" type="button" data-search-open
              aria-label="Search this site" data-i18n-attr="aria-label:search.title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true">
          <circle cx="11" cy="11" r="7"/><path d="M20 20l-3.6-3.6" stroke-linecap="round"/>
        </svg>
        <kbd>Ctrl K</kbd>
      </button>
      <div class="lang" data-open="false">
        <button class="icon-btn" type="button" data-lang-open aria-expanded="false"
                aria-haspopup="true" aria-label="Change language"
                data-i18n-attr="aria-label:lang.change">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">
            <circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 2.5 15.4 0 18M12 3c-2.5 2.6-2.5 15.4 0 18"/>
          </svg>
        </button>
        <div class="lang-menu" role="menu">
          <button type="button" role="menuitem" data-lang-pick="en" aria-current="true">
            English <span class="lang-code">EN</span>
          </button>
          <button type="button" role="menuitem" data-lang-pick="pt" aria-current="false">
            Portugu&ecirc;s <span class="lang-code">PT</span>
          </button>
        </div>
      </div>
      <button class="icon-btn" type="button" data-theme-toggle aria-label="Switch theme"
              data-i18n-attr="aria-label:theme.switch">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" stroke-linejoin="round"/>
        </svg>
      </button>
      <a class="icon-btn" href="{DISCORD}" rel="noopener" aria-label="Community chat server">
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M19.6 5.6A16 16 0 0 0 15.7 4.4l-.2.4a12 12 0 0 1 3.4 1.7 14 14 0 0 0-12-.6 13 13 0 0 0-1.7.6 12 12 0 0 1 3.4-1.7l-.2-.4A16 16 0 0 0 4.4 5.6C2 9.2 1.3 12.7 1.6 16.2a16 16 0 0 0 4.9 2.5l1-1.6a10 10 0 0 1-1.6-.8l.4-.3a11 11 0 0 0 9.4 0l.4.3a10 10 0 0 1-1.6.8l1 1.6a16 16 0 0 0 4.9-2.5c.4-4-.7-7.5-2.8-10.6zM8.6 14.3c-1 0-1.7-.9-1.7-1.9s.8-1.9 1.7-1.9 1.8.9 1.7 1.9c0 1-.7 1.9-1.7 1.9zm6.3 0c-1 0-1.7-.9-1.7-1.9s.8-1.9 1.7-1.9 1.8.9 1.7 1.9c0 1-.7 1.9-1.7 1.9z"/>
        </svg>
      </a>
      <button class="icon-btn nav-toggle" type="button" data-drawer-open aria-expanded="false" aria-controls="drawer" aria-label="Open menu">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path d="M4 7h16M4 12h16M4 17h16" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  </div>
</header>

<div class="drawer" id="drawer" data-open="false" role="dialog" aria-modal="true" aria-label="Menu">
  <div class="shell">
    <div class="drawer-head">
      <span class="eyebrow">Menu</span>
      <button class="icon-btn" type="button" data-drawer-close aria-label="Close menu">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
          <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
    <!-- DRAWER:START -->
    <nav aria-label="Mobile">
{_nav_drawer(prefix, active)}
    </nav>
    <!-- DRAWER:END -->
  </div>
</div>
"""


def foot_key(href):
    """Stable i18n key for a footer link, derived from its target."""
    stem = href.split("/")[-1].split("#")[0]
    for ext in (".html", ".txt", ".xml"):
        stem = stem.replace(ext, "")
    return "foot." + (stem or "external")


def footer(prefix):
    cols = []
    for col, (title, links) in enumerate(FOOTER_COLUMNS):
        items = []
        for href, label in links:
            full = href if href.startswith("http") else prefix + href
            ext = ' rel="noopener"' if href.startswith("http") else ""
            key = foot_key(href)
            items.append(
                f'        <li><a href="{full}"{ext} data-i18n="{key}">{label}</a></li>')
        items = "\n".join(items)
        cols.append(f'      <div>\n        <h4 data-i18n="foot.col{col}">{title}</h4>\n'
                    f"        <ul>\n{items}\n        </ul>\n      </div>")
    cols = "\n".join(cols)
    return f"""<!-- FOOTER:START -->
<footer class="site-footer">
  <div class="shell">
    <div class="footer-grid">
      <div>
        <a class="brand" href="{prefix}index.html">
          <img class="mark" src="{prefix}assets/img/icon-192.png" width="34" height="34" alt="" aria-hidden="true">
          <span class="brand-text">
            <span class="brand-name">RETURN TO MORROC</span>
            <span class="brand-sub">Refuge</span>
          </span>
        </a>
        <p class="muted" data-i18n="foot.blurb" style="margin-top:1rem;font-size:0.92rem;max-width:34ch">
          A free, non-commercial hobby world built and run by a handful of players
          for anyone who wants somewhere unhurried to play.
        </p>
        <p class="cluster" style="margin-top:1rem">
          <a class="btn btn--ghost" href="{DISCORD}" rel="noopener" data-i18n="cta.chat">Community chat</a>
        </p>
      </div>
{cols}
    </div>
    <p class="footer-legal" data-i18n="foot.legal">
      {BRAND} is an unofficial fan project with no affiliation to, sponsorship by
      or endorsement from any game publisher, developer or rights holder. It is
      free to play, it accepts no real-money trading, and it will never sell
      in-game power. All third-party names that appear anywhere on this site
      belong to their respective owners and are used only to describe gameplay.
      <br><br>
      Built by the community, in the open. Site content is free to copy.
    </p>
  </div>
</footer>
<!-- FOOTER:END -->

<script>window.RTMR_PREFIX = "{prefix}";</script>
<script src="{prefix}assets/js/main.js" defer></script>
<script src="{prefix}assets/js/fx.js" defer></script>
<script src="{prefix}assets/js/search.js" defer></script>
<script src="{prefix}assets/js/i18n.js" defer></script>
</body>
</html>
"""


def breadcrumbs(prefix, trail):
    """Visible crumbs. The JSON-LD version is built from the same list so the
    two can never drift apart."""
    parts = []
    for i, (href, label) in enumerate(trail):
        if i:
            parts.append("<span>/</span>")
        if href is None:
            parts.append(f"<span>{label}</span>")
        else:
            key = ' data-i18n="ui.home"' if label == "Home" else ""
            parts.append(f'<a href="{prefix}{href}"{key}>{label}</a>')
    return '<p class="crumbs">' + "".join(parts) + "</p>"


def crumb_ld(trail):
    items = []
    for i, (href, label) in enumerate(trail, start=1):
        entry = {"pos": i, "name": label}
        target = f'"item": "{SITE}/{href}",' if href is not None else ""
        items.append('    {"@type": "ListItem", "position": %d, %s "name": "%s"}'
                     % (i, target, label))
    body = ",\n".join(items)
    return ('<script type="application/ld+json">\n'
            '{\n  "@context": "https://schema.org",\n  "@type": "BreadcrumbList",\n'
            '  "itemListElement": [\n' + body + '\n  ]\n}\n</script>\n')


def faq_ld(pairs):
    items = []
    for q, a in pairs:
        plain = a.replace('"', "'").replace("\n", " ")
        items.append('    {"@type": "Question", "name": "%s", "acceptedAnswer": '
                     '{"@type": "Answer", "text": "%s"}}' % (q.replace('"', "'"), plain))
    return ('<script type="application/ld+json">\n'
            '{\n  "@context": "https://schema.org",\n  "@type": "FAQPage",\n'
            '  "mainEntity": [\n' + ",\n".join(items) + '\n  ]\n}\n</script>\n')
