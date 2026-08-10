# -*- coding: utf-8 -*-
"""The class roster: the tree, and how each class maps onto the wiki data.

`tools/data/wiki.json` holds the raw material (descriptions, skill tables)
transcribed from the community wiki for the original world. This file says
which page belongs to which class, where that class sits in the tree, and -
importantly - what the Refuge changed about it, which the wiki cannot know.

Fields per class:
  slug      URL under classes/
  page      key in wiki.json, or None if the class has no wiki page
  section   for classes documented inside a shared page, the heading to pull
  tier      orphan | first | second | spec | final | expert | alt
  parents   what you change from
  leads_to  what you can change into
  tagline   one line, ours
  refuge    list of Refuge-specific notes, or []
"""

# The eight specialisations live inside one wiki page; their skills are pulled
# by heading rather than by page.
CLASSES = [
    # --- the shared start -------------------------------------------------
    dict(slug="orphan", page="Orphan", tier="orphan", parents=[], leads_to=[
        "thief", "trickster", "jester", "ronin", "mimic", "vagabond", "raider",
        "judge", "peacekeeper", "illusionist", "dark-knight", "bouncer"],
        tagline="Cursed by fate. The starter, and the only one.",
        refuge=[
            "Warp Portal is now a core Orphan skill: three memo points plus your save point, and it moves the whole party.",
            "Teleport level 1 is free for every character, 60 second cooldown, no SP cost. Level 2 was removed.",
            "Heal is capped at level 1 and rebuilt to scale with base level rather than skill level.",
            "Hiding is capped at level 1, fixed 2 seconds, and now works on bosses, insects and demons.",
            "Increase AGI no longer grants ASPD or AGI, only move speed.",
        ]),

    # --- first jobs off the Orphan ---------------------------------------
    dict(slug="thief", page="Thief", tier="first", parents=["orphan"],
         leads_to=["assassin", "rogue", "prowler", "shadowseer", "unchained-thief"],
         tagline="Path of the hero. Endless skills and spells.",
         refuge=[
             "Improve Defense rebuilt: 2 HP per skill level per base level. Roughly 3,900 HP at level 130, where it used to be a flat 150.",
             "Improve Wisdom rebuilt: 2 SP per skill level per 3 base levels, roughly 1,300 SP at level 130.",
             "Envenom can poison bosses.",
             "Double Strafe, Arrow Shower, Backstab and Cross Ripper Slasher all hit harder.",
         ]),
    dict(slug="trickster", page="Trickster", tier="first", parents=["orphan"],
         leads_to=["revenant"],
         tagline="Niflheim's eyes in Midgard. Lifesteal, criticals and fire.",
         refuge=["Hellraiser base damage 110% to 150%, and Finisher Ready no longer needs level 10.",
                 "Sweeping Slash hits three times during Finisher Ready."]),
    dict(slug="jester", page="Jester", tier="first", parents=["orphan"], leads_to=[],
         tagline="Plays with destiny. A barrage of skills.",
         refuge=["Gift Card and Joker's Draw both hit harder; Joker's Draw refunds 77 SP on use.",
                 "Stack Deck's proc chance is now 5% per 7 LUK instead of a flat 30%."]),
    dict(slug="ronin", page="Ronin", tier="first", parents=["orphan"], leads_to=[],
         tagline="Perfect play. Every skill can crit, every hit taken costs you.",
         refuge=["Ascending and Descending Steel INT scaling doubled to 2%.",
                 "Ascending Steel now grants Kaupe for one second.",
                 "New gear was added specifically for this job, which was short of it."]),
    dict(slug="mimic", page="Mimic", tier="first", parents=["orphan"], leads_to=[],
         tagline="Every skill in the game, if the dice agree.",
         refuge=[]),
    dict(slug="vagabond", page="Vagabond", tier="first", parents=["orphan"],
         leads_to=["legend"],
         tagline="Forging your destiny. Auto attack specialist.",
         refuge=["Only touched indirectly, through the shared passives."]),
    dict(slug="raider", page="Raider", tier="first", parents=["orphan"],
         leads_to=["dracomancer"],
         tagline="The forgotten myth. Heart of weapons.",
         refuge=["Heavy Stab and Wind Cutter hit harder; Dragon Thrust slightly less.",
                 "Spear Mastery retuned: less HP on one-hand, more flee on two-hand."]),
    dict(slug="bouncer", page=None, tier="first", parents=["orphan"], leads_to=["pit-boss"],
         tagline="Fists, punch combos, and the first casting skills in the tree.",
         weapons="Fists",
         refuge=["Brand new in the Refuge. Commissioned by the head admin, designed by Ornstein.",
                 "Tanky, versatile, flexible, and an enormous SP sink.",
                 "Progression to Pit Boss is fast, on the same timing as Raider to Dracomancer."],
         own=["Quick punch combos that build stacks, and the first casting skills in the tree.",
              "Tanky and flexible in how you build it, with real survivability for a first job.",
              "The cost is an enormous SP sink. You can make it move fast, but speed eats your bar.",
              "Designed by Ornstein, themed by Metta, commissioned specifically for this server."]),

    dict(slug="merchant", page=None, tier="alt", parents=["orphan"], leads_to=[],
         tagline="A life of peace and profits. Cannot fight, can sell.",
         refuge=[],
         weapons="None",
         own=["Available from the very start. Change at base level 1, at the Merchant Envoy near the backroom in the Orphanage.",
              "Cannot level up at all. That is the trade.",
              "Three skills, all learned at job change.",
              "Free travel between the Orphanage and Alberta, and a cart anywhere, any time, from an exclusive item."]),

    # --- expert jobs ------------------------------------------------------
    dict(slug="judge", page="Judge", tier="expert", parents=["orphan"], leads_to=[],
         tagline="Power from the royalty. High preparation for high burst.",
         refuge=["New revolvers added to the pool.",
                 "Death Sentence base damage doubled, DEX scaling tripled, combo bonus doubled.",
                 "Violent Barrage and Gun Swap both improved."]),
    dict(slug="peacekeeper", page="Peacekeeper", tier="expert", parents=["orphan"], leads_to=[],
         tagline="Whips and trinkets, in one continuous combo.",
         refuge=["Use Trinket base damage doubled and DEX scaling tripled.",
                 "Both Andromeda skills hit harder on shorter cooldowns.",
                 "New gear was added specifically for this job, which was short of it.",
                 "Chain Mastery and Assault Mode were pulled back to pay for it."]),
    dict(slug="illusionist", page="Illusionist", tier="expert", parents=["orphan"], leads_to=[],
         tagline="Memories given life. Summons and illusion spells.",
         refuge=["Life Strings now grants 10% to 20% of your stats per level, on a 30 second cycle."]),
    dict(slug="dark-knight", page="Darkknight", tier="expert", parents=["orphan"], leads_to=[],
         tagline="Vengeance incarnate. Life energy into power.",
         refuge=["Fatal Menace and Night Menace rebalanced: more base damage, less missing-HP scaling.",
                 "Knight Ritual now boosts STR and VIT instead of AGI and DEX.",
                 "Conflagration gains 50% base damage; Shatter Cross triples its bonus against frozen targets."]),

    # --- thief second jobs -------------------------------------------------
    dict(slug="assassin", page="Assassin", tier="second", parents=["thief"],
         leads_to=["blade-dancer", "shinobi", "executioner", "scoundrel", "unchained-assassin"],
         tagline="Power of tradition. Master of weapon arts.",
         refuge=["Axe Tornado, Axe Boomerang, Sonic Blow and Burst Petals all improved.",
                 "Cloaking is no longer detected by normal monsters, but bosses see you.",
                 "Magic Pierce no longer adds defence pierce per active level."]),
    dict(slug="rogue", page="Rogue", tier="second", parents=["thief"],
         leads_to=["mystic", "duelist", "saboteur", "deadeye", "unchained-rogue"],
         tagline="Power of change. Jack of all trades.",
         refuge=["Shield Mastery bonus doubled to 10% per level.",
                 "Ricochet Arrow improved; Decoy and Sneak Attack pulled back."]),
    dict(slug="prowler", page="Prowler", tier="alt", parents=["thief"], leads_to=[],
         tagline="Evasive backstabber. Close in and slaughter.",
         refuge=["Max job level reduced from 70 to 50. Nothing else changed."]),
    dict(slug="shadowseer", page="Shadowseer", tier="alt", parents=["thief"], leads_to=[],
         tagline="Duality of reality. A rain of autospells.",
         refuge=["Max job level reduced from 70 to 50.",
                 "Magic Pierce removed from the tree."]),

    # --- raider / trickster / vagabond finals -----------------------------
    dict(slug="dracomancer", page="Dracomancer", tier="final", parents=["raider"], leads_to=[],
         tagline="The storm walker. Bound to dragons.",
         refuge=["Orbs are an extra, not a rotation. Cooldown is a flat 90s and duration scales with level.",
                 "Crescent Dive, Geirskogul and Dragon Breath all improved.",
                 "Draco Wings no longer costs 5% of your max HP."]),
    dict(slug="revenant", page="Revenant", tier="final", parents=["trickster"], leads_to=[],
         tagline="Master of life and death. Engagement and explosive damage.",
         refuge=["Ominous Presence takes on the overheal mechanic; 3% per level of the extra leech becomes shield.",
                 "Flaming Wave loses its cast time and burns five times longer.",
                 "Final Orchestra heals 1% of your max HP per pulse per level, and deals half that as damage plus knockback."]),
    dict(slug="legend", page="Legend", tier="final", parents=["vagabond"], leads_to=[],
         tagline="Master of your destiny. Battlefield dominance with power.",
         refuge=["Only touched indirectly, through the shared passives."]),
    dict(slug="pit-boss", page=None, tier="final", parents=["bouncer"], leads_to=[],
         tagline="Big setup for big hits.",
         weapons="Golf Clubs and Chains",
         refuge=["Brand new in the Refuge.",
                 "Most skills have fixed cast time, so gear that reduces it is the build.",
                 "Golf clubs cut fixed cast; chains raise your current defence by percentage.",
                 "Roughly a Dracomancer's HP, slightly more SP."],
         own=["Doubles down on the tree's identity: prepare big swings, land big strikes.",
              "Most skills have fixed cast time, so gear that reduces it is not optional. It is the build.",
              "<strong>Golf clubs</strong> carry an innate reduction to fixed cast time.",
              "<strong>Chains</strong> raise the job's defensive properties directly, as a percentage of your current defence.",
              "Roughly a Dracomancer's HP and slightly more SP.",
              "Very flexible, but pulled toward one of two poles: quick, with combos feeding a finisher, or slow, with fixed-cast skills that hurt a great deal when they land.",
              "Full skill list on the <a href=\"../newjobs.html\">new jobs page</a>."]),

    # --- specialisations (documented inside one wiki page) ----------------
    dict(slug="blade-dancer", page="Specializations", section="Blade Dancer",
         tier="spec", parents=["assassin"], leads_to=["night-raven"],
         tagline="Master of blades. Dual wielding, properly.", refuge=[]),
    dict(slug="shinobi", page="Specializations", section="Shinobi",
         tier="spec", parents=["assassin"], leads_to=["satsujin"],
         tagline="Master of elements. Change the element, change the fight.", refuge=[]),
    dict(slug="executioner", page="Specializations", section="Executioner",
         tier="spec", parents=["assassin"], leads_to=["gravekeeper"],
         tagline="Master of katars. Chain the skills, land the damage.", refuge=[]),
    dict(slug="scoundrel", page="Specializations", section="Scoundrel",
         tier="spec", parents=["assassin"], leads_to=["black-plague"],
         tagline="Master of poisons. Debuff everything, including yourself.", refuge=[]),
    dict(slug="mystic", page="Specializations", section="Mystic",
         tier="spec", parents=["rogue"], leads_to=["arcane-master"],
         tagline="Spellcasting, unlocked.", refuge=[]),
    dict(slug="duelist", page="Specializations", section="Duelist",
         tier="spec", parents=["rogue"], leads_to=["kingslayer"],
         tagline="A stance, counter charges, and skills that read them.", refuge=[]),
    dict(slug="saboteur", page="Specializations", section="Saboteur",
         tier="spec", parents=["rogue"], leads_to=["blast-juggler"],
         tagline="Traps, explosions, and a pitcher for the party.", refuge=[]),
    dict(slug="deadeye", page="Specializations", section="Deadeye",
         tier="spec", parents=["rogue"], leads_to=["sinner"],
         tagline="The bow, the nest, and one very heavy finisher.", refuge=[]),

    # --- assassin finals ---------------------------------------------------
    dict(slug="night-raven", page="Night_Raven", tier="final", parents=["blade-dancer"], leads_to=[],
         tagline="Unseen blade from the skies. Speed, mobility, precision.",
         refuge=["Night Hunt hit count doubled, and deals 1.25x at red health.",
                 "Bloody Fangs traded its range for triple damage at red health.",
                 "Soul Destroyer poisons anything, bosses included, under Enchant Poison.",
                 "Cloaking Exceed move speed rebuilt to scale purely per level."]),
    dict(slug="satsujin", page="Satsujin", tier="final", parents=["shinobi"], leads_to=[],
         tagline="Master of shadows and magic. Attacks from shadows and spells.",
         refuge=["Barely touched, because it did not need it. Dragon Omamori DEX scaling 2% to 3%.",
                 "Million Stab cooldown 15s to 7s, since it lost the gear that supported it."]),
    dict(slug="gravekeeper", page="Gravekeeper", tier="final", parents=["executioner"], leads_to=[],
         tagline="Loki's legacy for Midgard. Critical attacks and combos.",
         refuge=["Guard Breaker gains 25% final damage per defensive buff on the target.",
                 "Exale Rage area doubled to 11x11; Mass Grave lost its cast time.",
                 "Meteor Assault gains 5% per Rolling Counter."]),
    dict(slug="black-plague", page="Black_Plague", tier="final", parents=["scoundrel"], leads_to=[],
         tagline="Unseen death from inside. Poisons, toxins, curses and death.",
         refuge=["Enchant Deadly Poison now negates the whole flat defence, not 75% of it.",
                 "Venom Buster cooldown halved; Spiral Blade and Mjolnir's Fall both hit harder."]),

    # --- rogue finals ------------------------------------------------------
    dict(slug="arcane-master", page="Arcanemaster", tier="final", parents=["mystic"], leads_to=[],
         tagline="Unrestricted forbidden magic. Spellcasting, autospells, elements.",
         refuge=["Unlimited Power rebuilt: no cooldowns on anything, but every skill gains an irreducible 1s cast and costs double SP.",
                 "Comet cooldown halved."]),
    dict(slug="kingslayer", page="Kingslayer", tier="final", parents=["duelist"], leads_to=[],
         tagline="Master of strategy and war. Versatility, control, protection.",
         refuge=["Check Mate rebuilt from a fixed 400 ATK into a normal formula that reads your current HP and SP.",
                 "King's Chains adds your soft and hard defence as extra final damage.",
                 "Both gambits now hand you five duel counters."]),
    dict(slug="blast-juggler", page="Blast_Juggler", tier="final", parents=["saboteur"], leads_to=[],
         tagline="No restrictions or rules. Bombs, traps and explosions.",
         refuge=["Hot, Cold and Claymore traps now ignore defence, with a rebuilt formula.",
                 "Claymore triples against full-health targets; Cluster Bomb triples under 10%.",
                 "Rolling Flames halved in area but doubled in hit detection, and no longer clears ground effects."]),
    dict(slug="sinner", page="Sinner", tier="final", parents=["deadeye"], leads_to=[],
         tagline="Repent through cleansing. Smiting arrows and turrets.",
         refuge=["Sniper Nest fully reworked: -150 flee, +150 hit, guaranteed crits on Headshot and Aimed Bolt, +25% SP costs.",
                 "Cannon Turret now walks with you, attacks your target and inherits 7% of your ATK per level.",
                 "Headshot always deals full damage, and halves its cooldown from the nest."]),

    # --- unchained --------------------------------------------------------
    dict(slug="unchained-thief", page="Unchained_Evolutions", section="Unchained Thief",
         tier="alt", parents=["thief"], leads_to=["phantom-thief"],
         tagline="Power of tradition and change. User of multiple schools.",
         refuge=[]),
    dict(slug="unchained-assassin", page="Unchained_Evolutions", section="Unchained Assassin",
         tier="alt", parents=["assassin"], leads_to=[],
         tagline="Break the limit and lock the job. Master of the basic arts.", refuge=[]),
    dict(slug="unchained-rogue", page="Unchained_Evolutions", section="Unchained Rogue",
         tier="alt", parents=["rogue"], leads_to=[],
         tagline="Break the limit and lock the job. Master of the basic arts.", refuge=[]),
    dict(slug="phantom-thief", page="Unchained_Evolutions", section="Phantom Thief",
         tier="final", parents=["unchained-thief"], leads_to=[],
         tagline="Master of tradition and change. Infinite possibilities.",
         refuge=["Job shadow sets no longer exist, so the part of this job that borrowed them borrows the new dungeon sets instead."]),
]

BY_SLUG = {c["slug"]: c for c in CLASSES}

NAMES = {
    "orphan": "Orphan", "merchant": "Merchant", "thief": "Thief", "trickster": "Trickster", "jester": "Jester",
    "ronin": "Ronin", "mimic": "Mimic", "vagabond": "Vagabond", "raider": "Raider",
    "bouncer": "Bouncer", "pit-boss": "Pit Boss", "judge": "Judge",
    "peacekeeper": "Peacekeeper", "illusionist": "Illusionist", "dark-knight": "Dark Knight",
    "assassin": "Assassin", "rogue": "Rogue", "prowler": "Prowler", "shadowseer": "Shadowseer",
    "dracomancer": "Dracomancer", "revenant": "Revenant", "legend": "Legend",
    "blade-dancer": "Blade Dancer", "shinobi": "Shinobi", "executioner": "Executioner",
    "scoundrel": "Scoundrel", "mystic": "Mystic", "duelist": "Duelist",
    "saboteur": "Saboteur", "deadeye": "Deadeye",
    "night-raven": "Night Raven", "satsujin": "Satsujin", "gravekeeper": "Gravekeeper",
    "black-plague": "Black Plague", "arcane-master": "Arcane Master", "kingslayer": "Kingslayer",
    "blast-juggler": "Blast Juggler", "sinner": "Sinner",
    "unchained-thief": "Unchained Thief", "unchained-assassin": "Unchained Assassin",
    "unchained-rogue": "Unchained Rogue", "phantom-thief": "Phantom Thief",
}

TIER_LABEL = {
    "orphan": "Starter", "first": "First job", "second": "Second job",
    "spec": "Specialisation", "final": "Final job", "expert": "Expert job",
    "alt": "Alternate path",
}

# The tree, laid out as columns for the overview page. Each entry is
# (heading, blurb, [[row], [row], ...]) where a row is a list of slugs.
TREE = [
    ("Straight from the Orphan",
     "Ten job levels and you are one of these. None of them changes again. "
     "What you pick here is what you play for a hundred and forty levels.",
     [["jester", "ronin", "mimic", "merchant"]]),
    ("One more step",
     "Four roads with exactly two stations. The first job comes at job level "
     "10, the second at 70 for Trickster and Vagabond, sooner for Raider and "
     "Bouncer.",
     [["raider", "trickster", "vagabond", "bouncer"],
      ["dracomancer", "revenant", "legend", "pit-boss"]]),
    ("The Expert jobs",
     "Unique systems, steeper learning curves, and explicitly not recommended "
     "for a first character. Base level 15 and job level 10 to enter.",
     [["judge", "peacekeeper", "illusionist", "dark-knight"]]),
    ("The Thief road",
     "The main progression, and the widest. Fifty job levels as a Thief, then "
     "a choice that eventually forks eight ways.",
     [["thief"], ["assassin", "unchained-thief", "rogue"]]),
    ("Leaving the road",
     "A Thief can abandon the path outright. An Assassin or a Rogue can lock "
     "the job forever instead of specialising.",
     [["shadowseer", "prowler"], ["unchained-assassin", "unchained-rogue", "phantom-thief"]]),
    ("Path of Tradition",
     "Assassin specialisations lift the job level cap from 50 to 70 and are "
     "required for a final job.",
     [["blade-dancer", "shinobi", "scoundrel", "executioner"],
      ["night-raven", "satsujin", "black-plague", "gravekeeper"]]),
    ("Path of Change",
     "Rogue specialisations, same rules. Four of the most different final jobs "
     "in the game come out of this row.",
     [["duelist", "mystic", "saboteur", "deadeye"],
      ["kingslayer", "arcane-master", "blast-juggler", "sinner"]]),
]
