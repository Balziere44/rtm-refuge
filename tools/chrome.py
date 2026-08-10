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
DATABASE = "https://rtm-internal-e.vercel.app/"

# Deliberate wording note (see README): the site describes itself with generic
# genre vocabulary and never uses a publisher's brand name, product name or
# artwork. This is a fan project with no affiliation to any company, and the
# copy is written so that it cannot be mistaken for one.
BRAND = "Return to Morroc: Refuge"
SHORT = "RTM: Refuge"

NAV = [
    ("index.html", "Home"),
    ("server.html", "The Server"),
    ("start.html", "Start Here"),
    ("classes.html", "Classes"),
    ("mechanics.html", "Mechanics"),
    ("gear.html", "Gear"),
    ("world.html", "World"),
    ("guides.html", "Guides"),
    ("join.html", "Join"),
]

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
        ("database.html", "Community database"),
        ("guides.html", "Player-written guides"),
        ("llms.txt", "llms.txt"),
        ("sitemap.xml", "Sitemap"),
    ]),
]

# Viaoda Libre is one of Google's seven Art Nouveau families and carries the
# decorative headings; Atkinson Hyperlegible was designed for low-vision
# readability and does the actual reading. One decorative face, one legible
# face, one mono for labels - nothing else gets loaded.
FONTS = ("https://fonts.googleapis.com/css2?family=Viaoda+Libre&"
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
<meta property="og:image" content="{SITE}/assets/social/og-cover.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{BRAND}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{SITE}/assets/social/og-cover.jpg">

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


def nav_key(href):
    """Stable i18n key for a nav entry, derived from its filename."""
    return "nav." + href.replace(".html", "").replace("index", "home")


def _nav_links(prefix, active, cls=""):
    out = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        out.append(f'      <a href="{prefix}{href}"{cur} '
                   f'data-i18n="{nav_key(href)}">{label}</a>')
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
{_nav_links(prefix, active)}
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
{_nav_links(prefix, active)}
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
      {BRAND} is an unofficial, non-commercial fan project with no affiliation to,
      sponsorship by or endorsement from any game publisher, developer or rights
      holder. It hosts no commercial storefront, sells nothing, and accepts no
      real-money trading. All third-party names that appear anywhere on this site
      belong to their respective owners and are used only to describe gameplay.
      Nothing here is distributed for profit.
      <br><br>
      Built by the community, in the open. Site content is free to copy.
    </p>
  </div>
</footer>
<!-- FOOTER:END -->

<script>window.RTMR_PREFIX = "{prefix}";</script>
<script src="{prefix}assets/js/main.js" defer></script>
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
