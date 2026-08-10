# -*- coding: utf-8 -*-
"""Generate every HTML page.

    python tools/build.py

Deterministic, offline, no dependencies. What lands in the repository is
exactly what the browser receives.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import chrome as C
import data as D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DISCORD = C.DISCORD


def write(name, html):
    path = os.path.join(ROOT, name)
    # LF everywhere. Windows checkouts otherwise produce diffs nobody made.
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    print("  wrote", name, len(html) // 1024, "kb")


def page(name, title, description, active, body, trail=None, extra_ld="", hero=False):
    ld = extra_ld
    if trail:
        ld = C.crumb_ld(trail) + ld
    html = C.head("", title, description, "" if name == "index.html" else name,
                  extra_ld=ld, preload_hero=hero)
    html += C.header("", active)
    html += '<main id="main">\n' + body + "\n</main>\n"
    html += C.footer("")
    return write(name, html)


def crumbs(label, href=None):
    return C.breadcrumbs("", [("index.html", "Home"), (href, label)])


def cta(title, text):
    return f"""<section class="section section--tight">
  <div class="shell">
    <div class="cta-band reveal">
      <h2>{title}</h2>
      <p>{text}</p>
      <div class="cluster">
        <a class="btn btn--primary" href="{DISCORD}" rel="noopener" data-i18n="cta.join">Join the community server</a>
        <a class="btn btn--ghost" href="join.html" data-i18n="cta.howto">How to get in</a>
      </div>
    </div>
  </div>
</section>"""


def ul(items, cls=""):
    if not items:
        return ""
    c = f' class="{cls}"' if cls else ""
    return "<ul%s>\n" % c + "\n".join("  <li>%s</li>" % i for i in items) + "\n</ul>"


def job_blocks(groups):
    out = []
    for name, note, bullets in groups:
        anchor = name.lower().replace(" / ", "-").replace(" ", "-").replace("(", "").replace(")", "")
        note_html = f'<p class="muted">{note}</p>' if note else ""
        body = ul(bullets) if bullets else '<p class="dim">No direct changes.</p>'
        out.append(f"""    <article class="card reveal" id="{anchor}" data-row>
      <h3>{name}</h3>
      {note_html}
      {body}
    </article>""")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

HOME_LD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": "%(site)s/#website",
      "url": "%(site)s/",
      "name": "Return to Morroc: Refuge",
      "description": "A free, non-commercial hobby world rebuilt by the people who played the original.",
      "inLanguage": "en"
    },
    {
      "@type": "VideoGame",
      "@id": "%(site)s/#game",
      "name": "Return to Morroc: Refuge",
      "url": "%(site)s/",
      "genre": ["MMORPG", "Fantasy"],
      "gamePlatform": "PC",
      "playMode": ["SinglePlayer", "MultiPlayer", "CoOp"],
      "isAccessibleForFree": true,
      "description": "A custom, free-to-play fantasy MMO world rebuilt by its own players. Brand new classes, new items and a new progression. Never sells power, and no real-money trading.",
      "author": {"@type": "Organization", "name": "The Refuge team"}
    }
  ]
}
</script>
""" % {"site": C.SITE}


def build_home():
    """Deliberately short.

    The previous version put six cards of prose and a six-number strip above
    the fold. Counts of classes and skills are not what a visitor is deciding
    on - they want to look at something and click. So: one sentence, two
    buttons, then four large targets."""
    body = f"""<div class="aurora" aria-hidden="true"><span class="a1"></span><span class="a2"></span><span class="a3"></span></div>

<section class="hero">
  <div class="shell hero-inner">
    <div>
      <p class="eyebrow"><span class="live-dot" aria-hidden="true"></span> <span data-i18n="home.status">In development &middot; no launch date yet</span></p>
      <h1><span data-i18n="home.h1">The Orphans have their <span class="accent">old home</span> back.</span></h1>
      <p class="hero-lede" data-i18n="home.lede">
        A custom world, rebuilt from the ashes by the people who played it.
        Free to play, and it will never sell you power.
      </p>
      <div class="cluster" style="margin-top:2rem">
        <a class="btn btn--primary btn--lg" href="{DISCORD}" rel="noopener" data-i18n="cta.join">Join the community server</a>
        <a class="btn btn--ghost btn--lg" href="start.html" data-i18n="cta.start">Start playing</a>
      </div>
    </div>
    <div class="hero-art">
      <img src="assets/img/mark-900.png" width="900" height="900"
           alt="The Refuge mark: a shattered star of silver and purple shards"
           fetchpriority="high" decoding="async">
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="shell">
    <div class="quick reveal">
      <a class="q-lead" href="database.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">
          <ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/><path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>
        </svg>
        <span class="q-title" data-i18n="quick.db">Database</span>
        <span class="q-sub" data-i18n="quick.dbSub">Every item, every monster, every drop</span>
      </a>
      <a href="classes.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">
          <path d="M12 3v6M12 9L6 14M12 9l6 5M6 14v7M18 14v7M12 9v12" stroke-linecap="round"/>
        </svg>
        <span class="q-title" data-i18n="quick.classes">Classes</span>
        <span class="q-sub" data-i18n="quick.classesSub">The whole job tree</span>
      </a>
      <a href="start.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">
          <path d="M5 12h14M13 6l6 6-6 6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="q-title" data-i18n="quick.start">Start here</span>
        <span class="q-sub" data-i18n="quick.startSub">Level 1 to 130, in order</span>
      </a>
      <a href="world.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true">
          <circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 2.5 15.4 0 18M12 3c-2.5 2.6-2.5 15.4 0 18"/>
        </svg>
        <span class="q-title" data-i18n="quick.world">World</span>
        <span class="q-sub" data-i18n="quick.worldSub">Dungeons and endgame</span>
      </a>
    </div>
  </div>
</section>

<section class="section section--tight section--alt">
  <div class="shell">
    <div class="grid reveal">
      <div class="card">
        <h3 data-i18n="home.p1t">Never pay to win</h3>
        <p data-i18n="home.p1">
          The server has to pay for itself and for the people building it, and
          that will be discussed openly with the community. Whatever it ends up
          being, it will not sell power, and it will not sell your time.
        </p>
      </div>
      <div class="card">
        <h3 data-i18n="home.p2t">No single correct build</h3>
        <p data-i18n="home.p2">
          The job-locked sets that funnelled everyone into one playstyle past
          level 100 are gone. Fifty-plus new sets replaced them, and none of
          them belong to a job.
        </p>
      </div>
      <div class="card">
        <h3 data-i18n="home.p3t">Built where you can watch</h3>
        <p data-i18n="home.p3">
          Balance lists, skill trees and missed deadlines all get posted before
          launch. Feedback from the community has already changed the design
          more than once.
        </p>
      </div>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="shell">
    <div class="grid reveal">
      <a class="card card--link" href="newjobs.html">
        <span class="card-kicker">New</span>
        <h3>Bouncer and Pit Boss</h3>
        <p>Two jobs that did not exist. Golf clubs, chains, and a Swanton Bomb.</p>
      </a>
      <a class="card card--link" href="world.html#endgame">
        <span class="card-kicker">New</span>
        <h3>Two SS dungeons</h3>
        <p>Custom maps. In one of them there is no minimap and dying costs a level.</p>
      </a>
      <a class="card card--link" href="changes.html">
        <span class="card-kicker">Rebuilt</span>
        <h3>Every job rebalanced</h3>
        <p>The skills nobody pressed got numbers worth pressing.</p>
      </a>
    </div>
  </div>
</section>

{cta("There is no launch date. There is a door.",
     "Every announcement lands in the community server first, and the developers answer questions there directly.")}
"""
    page("index.html",
         "Return to Morroc: Refuge | A free custom fantasy MMO world",
         "A free-to-play custom fantasy MMO world rebuilt by its own players. Brand new classes, new items, a new progression, and it never sells power.",
         "index.html", body, extra_ld=HOME_LD, hero=True)


# ---------------------------------------------------------------------------
# The Server
# ---------------------------------------------------------------------------

def build_server():
    body = f"""<section class="page-hero">
  <div class="shell">
    {crumbs("The Server")}
    <h1>What the Refuge actually is</h1>
    <p>
      Who built it, why it exists, how it is paid for, and what it refuses to
      become. Written from the team's own posts rather than a pitch deck.
    </p>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div class="grid grid--wide">
      <div class="prose reveal">
        <h2>The one-paragraph version</h2>
        <p>
          Return to Morroc: Refuge is a special take on Return to Morroc, which was
          itself a heavily customised world that closed some time ago. It is not a
          revival in the nostalgic sense. It is the same design philosophy with the
          mistakes taken out, several hundred new items in, two jobs that never
          existed, and an explicit decision that nothing will ever be for sale.
        </p>
        <p>
          The team is three people plus moderators. They are not a studio. They
          have said in as many words that this is not meant to be a professional
          server - just a good experience for people who want somewhere to play
          that adds content, fixes what was broken, and respects your time.
        </p>
        <h2>Who does what</h2>
      </div>
      <div class="stack">
        <div class="card reveal">
          <span class="card-kicker">Head admin</span>
          <h3>Metta</h3>
          <p>Hosting, costs, planning and server progression. He paid for all of it, and the idea was his - he called Ornstein and spent hours arguing that the old world deserved better than a sequel-in-name.</p>
        </div>
        <div class="card reveal">
          <span class="card-kicker">Co-developer</span>
          <h3>croc</h3>
          <p>Items, code and the day-to-day running of the build. Much of his earlier work on the original is folded straight into the Refuge.</p>
        </div>
        <div class="card reveal">
          <span class="card-kicker">Co-developer</span>
          <h3>Ornstein</h3>
          <p>Design, job adjustments and the gameplay plan. He built the original world's direction and came back for this one. The new jobs, the rebalance passes and the Amatsu dungeon are his.</p>
        </div>
        <div class="card reveal">
          <span class="card-kicker">Community</span>
          <h3>The moderation team</h3>
          <p>Issues, arguments and the human side. Feedback from the community server has already changed the balance lists more than once.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--alt" id="money">
  <div class="shell">
    <div class="section-head reveal">
      <p class="eyebrow">Money</p>
      <h2>How this gets paid for, honestly</h2>
    </div>
    <div class="grid">
      <div class="card reveal">
        <h3>The costs are real</h3>
        <p>Hosting costs money and the people building this are doing real work. The head admin has covered all of it out of pocket so far. That is not a sustainable arrangement and nobody is pretending it is.</p>
      </div>
      <div class="card reveal">
        <h3>So there will be a way to fund it</h3>
        <p>What that looks like has not been decided. It will be discussed with the community before it ships, not announced at it. Cosmetics, conveniences, donations, a founder pack - all of that is on the table.</p>
      </div>
      <div class="card reveal">
        <h3>The line that will not move</h3>
        <p><strong>It will never sell power.</strong> No stats, no gear advantage, no progression you can buy past. And no real-money trading, ever. If a funding idea fails that test it does not ship.</p>
      </div>
    </div>
    <div class="panel reveal" style="margin-top:2rem">
      <p>
        There is no launch date. The team aimed for the end of the World Cup, missed
        it because real life happened to all three of them, said so plainly, and now
        plan on August 2026 at roughly 95% confidence. That is the entire status
        report, and it is more than most projects give you.
      </p>
    </div>
  </div>
</section>

<section class="section">
  <div class="shell shell-narrow">
    <div class="section-head reveal">
      <p class="eyebrow">Design</p>
      <h2>The rules the rebuild follows</h2>
    </div>
    <div class="prose reveal">
      <h3>Expand what was good, fix what was not</h3>
      <p>
        Every change on this site traces back to that sentence. Skills nobody
        pressed got numbers worth pressing. Systems that funnelled everyone into
        the same build got deleted. Nothing was changed because change looks like
        progress.
      </p>
      <h3>A small cozy town, not a live service</h3>
      <p>
        Updates arrive at a reasonable pace. New content keeps coming. There are
        no plans to close, and the stated ambition is to go considerably further
        than the original ever did.
      </p>
      <h3>Simple to read, varied to play</h3>
      <p>
        The jobs are meant to be easy to understand and varied by utility rather
        than by spectacle. If you are expecting a skill tree that reads like a
        light show, this is the wrong world - the interest here is in what a
        skill does for the party, not how big it is.
      </p>
      <h3>Built where you can watch</h3>
      <p>
        Balance lists, skill trees, dungeon reveals and missed deadlines all get
        posted publicly before launch. Suggestions from the community server have
        already changed the design more than once.
      </p>
    </div>
  </div>
</section>

{cta("Questions the team has already answered",
     "Nine of the most common ones are collected on the FAQ. Anything else, ask directly - the developers answer.")}
"""
    page("server.html",
         "The Server | Return to Morroc: Refuge",
         "Who builds the Refuge, why it exists, how it is funded, and the design rules the rebuild follows. Three people, no cash shop, no real-money trading.",
         "server.html", body, trail=[("index.html", "Home"), (None, "The Server")])


# ---------------------------------------------------------------------------
# What changed
# ---------------------------------------------------------------------------

def build_changes():
    body = f"""<section class="page-hero">
  <div class="shell">
    {crumbs("What Changed")}
    <h1>Everything the Refuge changed</h1>
    <p>
      The developers keep this in three buckets: transformed, added, removed.
      So does this page. If you played the original, start here.
    </p>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div class="grid grid--wide">
      <div class="card reveal">
        <span class="card-kicker tag-changed">Transformed</span>
        <h3>Rebuilt rather than tuned</h3>
        {ul(D.TRANSFORMED)}
      </div>
      <div class="card reveal">
        <span class="card-kicker tag-added">Added</span>
        <h3>New in the Refuge</h3>
        {ul(D.ADDED)}
      </div>
      <div class="card reveal">
        <span class="card-kicker tag-removed">Removed</span>
        <h3>Gone, on purpose</h3>
        {ul(D.REMOVED)}
      </div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="shell shell-narrow">
    <div class="section-head reveal">
      <p class="eyebrow">The reasoning</p>
      <h2>Why the shadow sets had to go</h2>
    </div>
    <div class="prose reveal">
      <p>
        This is the change people ask about most, so it deserves the space. In the
        original, every job had its own shadow set past level 100. They were strong,
        they were mandatory, and they were built around whichever skill the set
        assumed you would press. The result was that reaching 100 narrowed your
        character instead of opening it up.
      </p>
      <p>
        The Refuge deletes them and replaces them with more than fifty new sets tied
        to dungeons rather than to jobs. They are not job-locked. Several of them
        exist specifically to make an unloved skill worth building around - and one
        that is still in testing puts you at 1 HP in exchange for chaining a lot of
        skills in a row, which tells you roughly how far the team is willing to go.
      </p>
      <p class="muted">
        This is also why the power curve overall sits lower than the original's.
        Nothing is missing; the ceiling simply is not propped up by a mandatory set
        any more.
      </p>
      <h2>And why drop-rate gear went with them</h2>
      <p>
        Drop-rate bonuses on equipment create a tax: before you farm the thing you
        want, you farm the thing that lets you farm. Removing them means the drop
        tables can be tuned once, honestly, for everyone.
      </p>
      <h2>Difficulty moved, it did not vanish</h2>
      <p>
        Monsters deal more damage and healing is slower. In exchange, a large share
        of the skill changes on the <a href="classes.html">classes page</a> are
        straight damage increases - they exist to pay for the increased monster
        power and density, not to make you stronger than you were.
      </p>
      <p>
        Hiding now works on bosses, insects and demons. That is a genuine new tool,
        and the bosses had their skills rebalanced in response, so it is a
        conversation rather than an exploit.
      </p>
    </div>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div class="section-head reveal">
      <p class="eyebrow">Related</p>
      <h2>Keep reading</h2>
    </div>
    <div class="grid">
      <a class="card card--link reveal" href="classes.html"><h3>Every job change, line by line</h3><p>All three rebalance passes in one place.</p></a>
      <a class="card card--link reveal" href="newjobs.html"><h3>The two new jobs</h3><p>Bouncer and Pit Boss, including the full skill list.</p></a>
      <a class="card card--link reveal" href="world.html"><h3>Where the new content lives</h3><p>Distortions, Amatsu SS and the two unannounced dungeons.</p></a>
    </div>
  </div>
</section>
"""
    page("changes.html",
         "What Changed | Return to Morroc: Refuge",
         "Every difference between the original world and the Refuge: what was transformed, what was added, what was removed, and the reasoning behind each decision.",
         "changes.html", body, trail=[("index.html", "Home"), (None, "What Changed")])


# ---------------------------------------------------------------------------
# New jobs
# ---------------------------------------------------------------------------

def build_newjobs():
    skills = "\n".join(
        '      <div class="skill-block" data-row><h4>%s</h4><p class="muted" style="margin:0">%s</p></div>' % s
        for s in D.PITBOSS_SKILLS)
    body = f"""<section class="page-hero">
  <div class="shell">
    {C.breadcrumbs("", [("index.html", "Home"), ("classes.html", "Classes"), (None, "New jobs")])}
    <h1>Bouncer and Pit Boss</h1>
    <p>
      Two jobs that did not exist before. Commissioned by the head admin,
      designed by Ornstein, themed by Metta. An ultra-aggressive melee caster
      built on one idea: big setup for big hits.
    </p>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div class="grid grid--wide">
      <div class="card reveal">
        <span class="card-kicker">First job</span>
        <h3><a href="classes/bouncer.html">Bouncer</a></h3>
        <p>
          Fists. Quick punch combos that build stacks, and the first casting
          skills in the tree. Tanky, versatile, flexible in how you build it.
        </p>
        <p><strong>The cost:</strong> an enormous SP sink. You can make it move
        fast, but speed eats your bar.</p>
        <p class="muted">Progression to the second job is quick - the same timing as the raider line.</p>
      </div>
      <div class="card reveal">
        <span class="card-kicker">Final job</span>
        <h3><a href="classes/pit-boss.html">Pit Boss</a></h3>
        <p>
          Doubles down on the identity: prepare big swings, land big strikes.
          Most of its skills have fixed cast time, so gear that reduces it is not
          optional - it is the build.
        </p>
        <p>Roughly the HP of a dracomancer, and a little more SP.</p>
      </div>
      <div class="card reveal">
        <span class="card-kicker">New weapons</span>
        <h3>Two types, two answers</h3>
        <p><strong>Golf clubs</strong> carry an innate reduction to fixed cast time, which is how you make the slow skills fast.</p>
        <p><strong>Chains</strong> boost the job's defensive properties directly, with percentage bonuses to your current defence.</p>
        <p class="muted">Pit Boss uses a weapon type that did not exist in the game before, with its own visuals and sounds.</p>
      </div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="shell">
    <div class="section-head reveal">
      <p class="eyebrow">Pit Boss</p>
      <h2>The full skill tree</h2>
      <p>
        As posted by the designer in June 2026. Minor changes were still being
        made at the time, and the job has since been finished and approved.
      </p>
    </div>
    <div class="grid grid--wide">
      <div class="card reveal">
{skills}
      </div>
      <div class="stack">
        <div class="panel reveal">
          <h3 style="font-size:var(--step-1)">How it feels to play</h3>
          <p>
            Very flexible, but pulled toward one of two poles: quick, with combos
            feeding stacks into a finisher, or slow, with fixed-cast skills that
            hurt a great deal when they land. Durable throughout.
          </p>
        </div>
        <div class="panel reveal">
          <h3 style="font-size:var(--step-1)">Where the stacks come from</h3>
          <p>
            Bouncer's punch combos build them. <strong>Cross Punch</strong> is the
            slow shortcut that takes you straight to five.
            <strong>Diplomacy</strong> is what you spend them on.
          </p>
        </div>
        <div class="panel reveal">
          <h3 style="font-size:var(--step-1)">Party value</h3>
          <p>
            <strong>Retreat Order</strong> raises the whole party's defensive
            power, <strong>Soul Guard</strong> buys a mitigation window, and
            <strong>Merry-Go-Round</strong> can be pointed at a boss's adds
            rather than the boss.
          </p>
        </div>
        <div class="panel panel--warn reveal">
          <h3 style="font-size:var(--step-1)">Expectations</h3>
          <p>
            The designer has been blunt about this: the job follows the world's
            existing design language - simple, readable, varied by utility. It is
            not trying to be flashy, and it is not borrowed from anywhere else.
          </p>
        </div>
      </div>
    </div>
  </div>
</section>

{cta("Everything else got rebalanced too",
     "Sixteen existing jobs, three rebalance passes, transcribed skill by skill.")}
"""
    page("newjobs.html",
         "Bouncer and Pit Boss | Return to Morroc: Refuge",
         "The Refuge's two brand new jobs: Bouncer, a combo-building melee first job, and Pit Boss, a fixed-cast heavy hitter with two new weapon types. Full skill list.",
         "classes.html", body,
         trail=[("index.html", "Home"), ("classes.html", "Classes"), (None, "New jobs")])


# ---------------------------------------------------------------------------
# Guides
# ---------------------------------------------------------------------------

def build_guides():
    body = f"""<section class="page-hero">
  <div class="shell">
    {crumbs("Guides")}
    <h1>Guides written by players</h1>
    <p>
      Collected so nobody has to scroll three years of chat history to find the
      one message that explains where the portal is.
    </p>
  </div>
</section>

<section class="section">
  <div class="shell" id="bifrost">
    <div class="section-head reveal">
      <p class="eyebrow">Walkthrough</p>
      <h2>The Bifrost Mirror Shard</h2>
      <p>
        A hidden quest with no NPC pointing at it. Four gems, four tombs, one
        study at the top of a city, and a costume at the end.
      </p>
    </div>
    <div class="grid grid--wide">
      <div class="card reveal">
        <h3>1. Find the shard</h3>
        <p>Use the Orphan Badge and take Kafra Allysia to the free Morroc field. Work right through the portals until <span class="mono">moc_fild14</span>, then head right to the tomb. Interact with the <strong>Bifrost Stone Shard</strong> and choose to dig it out.</p>
      </div>
      <div class="card reveal">
        <h3>2. Eye of Vidar &middot; 25,000z</h3>
        <p>Kafra to Alberta. Through the north-west portal, then the lower one, then left to the tomb.</p>
      </div>
      <div class="card reveal">
        <h3>3. Eye of Vali &middot; 50,000z</h3>
        <p>Kafra to Hugel, through the lower portal. The tomb hides behind a house near the centre of the map.</p>
      </div>
      <div class="card reveal">
        <h3>4. Eye of Thor &middot; 100,000z</h3>
        <p>Prontera, then Kafra to Rachel (3,000z). Portals: right, up, up, left. Tomb at the map centre.</p>
      </div>
      <div class="card reveal">
        <h3>5. Eye of Balder &middot; 300,000z</h3>
        <p>Prontera to Umbala to Niflheim, 3,000z each hop. Then north-east to the tomb.</p>
      </div>
      <div class="card reveal">
        <h3>6. Assemble it</h3>
        <p>From Hugel take the ferry (1,500z) and follow the portals to Dicastes Diel. Inside the city building, past reception, Main Elevator to the Main Corridor, then Study Elevator to the Sage's Study. Add the gems <strong>in order</strong>: Vidar, Vali, Thor, Balder.</p>
      </div>
    </div>
    <div class="panel reveal" style="margin-top:2rem">
      <p><strong>Reward:</strong> the <em>Complete Mirror</em> achievement and Costume Cold Angel Wings. Total cost in fees: 475,000z plus travel.</p>
    </div>
  </div>
</section>

<section class="section section--alt" id="external">
  <div class="shell">
    <div class="section-head reveal">
      <p class="eyebrow">Elsewhere</p>
      <h2>The originals, in full</h2>
      <p>
        These are other people's work and they deserve the traffic. Everything
        above is a condensed version of the first one.
      </p>
    </div>
    <div class="grid">
      <a class="card card--link reveal" href="https://necropolecomercial.com/nc/guia-de-acesso-para-as-distortion-dungeons/" rel="noopener">
        <span class="card-kicker">Necropole Comercial</span>
        <h3>Distortion dungeon access</h3>
        <p>Turn-by-turn routing to all 21 distortions, with minimap screenshots. Portuguese.</p>
      </a>
      <a class="card card--link reveal" href="https://necropolecomercial.com/nc/guia-da-hide-quest-bifrost-mirror-shard/" rel="noopener">
        <span class="card-kicker">Necropole Comercial</span>
        <h3>Bifrost Mirror Shard hidden quest</h3>
        <p>The full version of the walkthrough above, with screenshots at every tomb. Portuguese.</p>
      </a>
      <a class="card card--link reveal" href="https://docs.google.com/spreadsheets/d/1RJ_aT-3F3K8f3Q6gjNiOebnsKmBMF6t87sVa95RUz5Y/edit?usp=sharing" rel="noopener">
        <span class="card-kicker">ElPato / Duck</span>
        <h3>Dungeon and distortion locations</h3>
        <p>A low-resolution visual location sheet for anyone who gets lost on the field maps. Community spreadsheet.</p>
      </a>
      <a class="card card--link reveal" href="https://docs.google.com/spreadsheets/d/1VXeW7JAKgn26ljPFa8ygWujwqXlkexOBUYtUk2s_Fg8/edit?gid=2052741816#gid=2052741816" rel="noopener">
        <span class="card-kicker">Pitaya</span>
        <h3>Hatred, costumes, Sun Hat and Celestial Tome</h3>
        <p>The reference sheet for the collection hunts. Community spreadsheet.</p>
      </a>
    </div>
    <div class="panel reveal" style="margin-top:2rem">
      <p>
        Written something useful? Post it in the community server and it goes on
        this page with your name on it. That is the whole editorial process.
      </p>
    </div>
  </div>
</section>

<section class="section">
  <div class="shell shell-narrow">
    <div class="section-head reveal">
      <p class="eyebrow">Before you go</p>
      <h2>Things worth knowing early</h2>
    </div>
    <div class="prose reveal">
      <h3>You already have Warp Portal and Teleport</h3>
      <p>
        Both are default skills for every character. Warp Portal memorises three
        locations plus your save point and takes your whole party. Teleport is
        free with a 60 second cooldown. Nobody needs to buy mobility.
      </p>
      <h3>Hiding is a two-second tool, not a hiding place</h3>
      <p>
        Fixed duration, five second cooldown, cannot be cancelled early - and it
        works on bosses, insects and demons. It is an interrupt, not an escape.
      </p>
      <h3>Improve Defense and Improve Wisdom are worth points now</h3>
      <p>
        They scale with base level rather than being a flat lump. At level 130
        that is roughly 3,900 HP and 1,300 SP instead of 150 of each. Do not skip
        them because you remember them being bad.
      </p>
      <h3>The Orphan Badge is your key to almost everything</h3>
      <p>
        Kafra teleport services, and by extension most distortion access routes,
        run through it. Get it early.
      </p>
    </div>
  </div>
</section>

{cta("Nothing here is final",
     "The world is still in development, which means guides written now will need corrections later. The community server is where those corrections happen.")}
"""
    page("guides.html",
         "Guides | Return to Morroc: Refuge",
         "Player-written guides for the Refuge: the Bifrost Mirror Shard hidden quest step by step, distortion dungeon access, community spreadsheets and early-game advice.",
         "guides.html", body, trail=[("index.html", "Home"), (None, "Guides")])


# ---------------------------------------------------------------------------
# Join
# ---------------------------------------------------------------------------

def build_join():
    body = f"""<section class="page-hero">
  <div class="shell">
    {crumbs("Join")}
    <h1>How to get in</h1>
    <p>
      There is no launch date and no client download yet. Here is exactly where
      things stand and what to do in the meantime.
    </p>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div class="grid grid--wide">
      <div class="card reveal">
        <span class="card-kicker"><span class="live-dot" aria-hidden="true"></span> Status</span>
        <h3>In development</h3>
        <p>
          The endgame dungeons are finished. The two new jobs are finished. What
          remains is boss changes, items for the new jobs, cleanup, and the
          outside-the-game work: registration, security, patcher checks.
        </p>
        <p class="muted">Last public status: August 2026, described as roughly 95% likely.</p>
      </div>
      <div class="card reveal">
        <span class="card-kicker">Step one</span>
        <h3>Join the community server</h3>
        <p>
          Every announcement lands there first, including the launch. The
          developers answer questions directly and read the suggestion channels.
        </p>
        <p class="cluster">
          <a class="btn btn--primary" href="{DISCORD}" rel="noopener">Open the invite</a>
        </p>
        <p class="mono dim" style="font-size:var(--step--1);margin-top:0.8rem">
          {DISCORD}
          <button class="chip" type="button" data-copy="{DISCORD}" style="cursor:pointer;margin-left:0.4rem">Copy</button>
        </p>
      </div>
      <div class="card reveal">
        <span class="card-kicker">Step two</span>
        <h3>Read what changed</h3>
        <p>
          If you played the original, the <a href="changes.html">changes page</a>
          and the <a href="classes.html">rebalance lists</a> will save you a
          respec. If you did not, the <a href="server.html">server page</a> is
          the shorter introduction.
        </p>
      </div>
      <div class="card reveal">
        <span class="card-kicker">Step three</span>
        <h3>Accounts</h3>
        <p>
          Not decided yet. There may be a web control panel, or registration may
          happen through the in-game command. The team has said this is still
          pending confirmation.
        </p>
      </div>
    </div>
  </div>
</section>

<section class="section section--alt">
  <div class="shell shell-narrow">
    <div class="section-head reveal">
      <p class="eyebrow">Expectations</p>
      <h2>What you are signing up for</h2>
    </div>
    <div class="prose reveal">
      <p>
        This is a hobby project run by three people with day jobs. They missed
        their first estimate because real life happened to all three of them at
        once, and they said so publicly rather than going quiet. That is the
        texture of the thing.
      </p>
      <p>
        In exchange you get a world that will never sell you power, where the
        balance decisions are posted before they ship, and where the person
        paying for the hardware is in the same chat channel as you.
      </p>
      <p class="muted">
        If you are looking for a polished commercial operation with a roadmap and
        a support desk, this is honestly not it. If you want a small, well-made
        place that respects your time, pull up a chair.
      </p>
    </div>
  </div>
</section>

<section class="section">
  <div class="shell">
    <div class="cta-band reveal">
      <h2>See you in the Refuge</h2>
      <p>Soon, in the sense that people who have missed one deadline use the word.</p>
      <div class="cluster">
        <a class="btn btn--primary" href="{DISCORD}" rel="noopener">Join the community server</a>
        <a class="btn btn--ghost" href="faq.html">Read the FAQ</a>
      </div>
    </div>
  </div>
</section>
"""
    page("join.html",
         "How to Join | Return to Morroc: Refuge",
         "Current development status of the Refuge, how to follow the launch announcement, and what to expect from a free hobby world run by three people.",
         "join.html", body, trail=[("index.html", "Home"), (None, "Join")])


# ---------------------------------------------------------------------------
# FAQ
# ---------------------------------------------------------------------------

def build_faq():
    items = "\n".join(
        f"      <details class=\"faq reveal\">\n        <summary>{q}</summary>\n        <p>{a}</p>\n      </details>"
        for q, a in D.FAQS)
    body = f"""<section class="page-hero">
  <div class="shell">
    {crumbs("FAQ")}
    <h1>Questions and answers</h1>
    <p>
      The nine things people ask most, answered from the team's own posts rather
      than paraphrased into marketing.
    </p>
  </div>
</section>

<section class="section">
  <div class="shell shell-narrow">
{items}
  </div>
</section>

{cta("Not on the list?",
     "Ask in the community server. The developers answer questions there directly, and the good ones end up on this page.")}
"""
    page("faq.html",
         "FAQ | Return to Morroc: Refuge",
         "Launch date, cost, cash shop, shadow sets, Einherjar Challenge Mode and who runs the Refuge - the nine most common questions, answered from the team's own posts.",
         "join.html", body,
         trail=[("index.html", "Home"), (None, "FAQ")],
         extra_ld=C.faq_ld(D.FAQS))


def build_404():
    """Cloudflare Pages and Netlify both serve /404.html for an unknown path.

    It is generated like every other page so it carries the same header,
    footer and search - a dead end that still lets you get somewhere is worth
    more than a pretty apology."""
    body = f"""<div class="aurora" aria-hidden="true"><span class="a1"></span><span class="a2"></span><span class="a3"></span></div>

<div class="shell lost">
  <div>
    <p class="code" data-i18n="lost.code">Error 404</p>
    <h1 data-i18n="lost.h1">This page wandered off.</h1>
    <p data-i18n="lost.body">
      The address does not exist, or it did and it moved. It happens to orphans
      with no memory. Try the search, or pick up one of the threads below.
    </p>
    <div class="cluster lost-links" style="justify-content:center">
      <button class="btn btn--primary" type="button" data-search-open data-i18n="lost.search">Search the site</button>
      <a class="btn btn--ghost" href="index.html" data-i18n="nav.home">Home</a>
      <a class="btn btn--ghost" href="start.html" data-i18n="nav.start">Start Here</a>
      <a class="btn btn--ghost" href="classes.html" data-i18n="nav.classes">Classes</a>
    </div>
  </div>
</div>
"""
    html = C.head("", "Page not found | Return to Morroc: Refuge",
                  "That page does not exist on the Refuge site. Search the site, or "
                  "start again from the class tree, the new player guide or the home page.",
                  "404.html")
    html += C.header("", "")
    html += '<main id="main">\n' + body + "\n</main>\n"
    html += C.footer("")
    return write("404.html", html)


def main():
    print("building", ROOT)
    build_home()
    build_server()
    build_changes()
    build_newjobs()
    build_guides()
    build_join()
    build_faq()
    build_404()
    print("done")


if __name__ == "__main__":
    main()
