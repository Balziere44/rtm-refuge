# -*- coding: utf-8 -*-
"""Content source for the generated pages.

Everything that appears in more than one place on the site lives here once.
The build scripts only turn it into markup.

Provenance: the balance and design entries are transcribed from the developer
posts in the project's own community server (Ornstein / croc / Metta, May to
August 2026). The dungeon list is the community access guide by Necropole
Comercial for the original server, which the Refuge inherits. Nothing here was
invented; where a number is still moving, the entry says so.
"""

# --------------------------------------------------------------------------
# Distortion dungeons. Level and rank are the community guide's; the "where"
# column is a shortened version of its directions, enough to orient someone
# without replacing the guide itself.
# --------------------------------------------------------------------------

DUNGEONS = [
    ("Loki's Palace", "85-90", "S", "Morroc, through the assassin guild. One Enriched Oridecon opens it permanently."),
    ("Nightmare Clock Tower", "85-90", "B", "Aldebaran clock tower, portal to the south-west inside."),
    ("Einbroch Deadlands", "85-100", "B", "Einbroch fields, industrial outskirts."),
    ("Morroc", "90-100", "B", "The ruined city itself. The distortion sits in the open."),
    ("Morroc Castle", "100-105", "A", "Deeper into the ruins, past the outer city."),
    ("Geffenia Antitower", "100-105", "B", "Under Geffen, the mirrored tower."),
    ("Kiel Hyre University", "105-110", "B", "Kiel Hyre grounds, through the academy wing."),
    ("Abyss Lake", "105-115", "A", "Hugel side, down into the lake caverns."),
    ("Ancient Temple", "105-115", "A", "Old temple grounds, deep interior."),
    ("Old Glast Heim", "110-120", "A", "The castle before the fall."),
    ("Abyss Glast Heim", "115-125", "A", "The castle after it. Same walls, worse tenants."),
    ("Prontera", "115-120", "B", "The capital, folded in on itself."),
    ("Horror Toy Factory", "120-125", "B", "Lutie, the factory floor."),
    ("Odin Temple", "120-125", "A", "Odin's shrine, upper terraces."),
    ("Rachel Nightmare", "130", "SS", "Rachel, south-west. The first true wall."),
    ("Ancient Verus Laboratory", "140-145", "S", "Verus city centre, through the Yuno fields."),
    ("Divine Temple of Freya", "145-150", "S", "Rachel's inner sanctum."),
    ("Dimensional Gorge", "145-150", "S", "The rift itself."),
    ("Thanatos Paradise", "145-150", "S", "The tower, all the way up."),
    ("Abandoned Castle", "145-150", "S", "Off the main routes. Bring a party."),
    ("Jormungand's Lair", "150", "S", "End of the line for the original roster."),
]

# --------------------------------------------------------------------------
# Job rebalances, grouped the way the developers posted them.
# Each job is (name, note, [bullet, ...]).
# --------------------------------------------------------------------------

CORE_CHANGES = [
    ("Orphan (shared baseline)",
     "The skills every character carries. These four changes touch every build in the game.",
     [
         "<strong>Heal</strong> capped at level 1. The formula was rewritten to scale off base level instead of skill level, so it stays relevant instead of falling off. Cooldown 5s to 7s.",
         "<strong>Hiding</strong> capped at level 1, fixed 2 second duration, 5s cooldown, cannot be cancelled early - but now works on insects, demons and bosses.",
         "<strong>Warp Portal</strong> is now a default skill. Memorise three locations plus your save point and warp yourself and the whole party.",
         "<strong>Teleport level 1</strong> is free for everyone, 60 second cooldown, no SP cost, behaves like a Fly Wing. Level 2 was removed.",
         "<strong>Increase AGI</strong> no longer grants ASPD or AGI. Slightly better move speed instead, 20s + 2s per AGI.",
         "Heal, Hiding and Increase AGI now cost 15 SP + 5% of max SP.",
     ]),
    ("Thief line",
     "",
     [
         "<strong>Envenom</strong> can poison bosses. Better INT scaling, chance and duration rise with skill level.",
         "<strong>Improve Defense</strong> rebuilt: 2 HP per skill level per base level. About 150 HP before, roughly 3,900 at level 130.",
         "<strong>Improve Wisdom</strong> rebuilt: 2 SP per skill level per 3 base levels. About 150 SP before, roughly 1,300 at level 130.",
         "<strong>Double Strafe</strong> 50 + 7%/lv to 50 + 10%/lv.",
         "<strong>Arrow Shower</strong> combo damage 80% to 100%.",
         "Elemental spell bonus per focus stack 6% to 7%.",
         "<strong>Backstab</strong> scaling per Improve Dodge level 3% to 5%.",
         "<strong>Cross Ripper Slasher</strong> damage per counter 20% to 25%.",
     ]),
    ("Assassin",
     "",
     [
         "<strong>Axe Tornado</strong> damage per Rolling Cutter counter 15% to 25%.",
         "<strong>Axe Boomerang</strong> base damage 60% to 100%.",
         "<strong>Sonic Blow</strong> LUK scaling 1% to 2% per LUK.",
         "<strong>Burst Petals</strong> base damage 60% to 100%, hit-count bug fixed.",
         "<strong>Magic Pierce</strong> no longer adds 1% def pierce per active level.",
         "<strong>Cloaking</strong> is not detected by normal monsters, but bosses see you.",
     ]),
    ("Rogue",
     "",
     [
         "<strong>Decoy</strong> cooldown 5s to 8s, works on non-bosses.",
         "<strong>Ricochet Arrow</strong> base 50% to 75%, combo bonus 70% to 75%.",
         "<strong>Shield Mastery</strong> bonus to shield skills 5%/lv to 10%/lv.",
         "<strong>Sneak Attack</strong> bonus 30% to 20%, still halved against bosses.",
     ]),
    ("Jester",
     "",
     [
         "<strong>Gift Card</strong> 70 + 7%/lv to 77 + 7%/lv, cooldown 5s to 3s.",
         "<strong>Stack Deck</strong> proc chance for Joker's Draw is now 5% per 7 LUK instead of a flat 30%.",
         "<strong>Joker's Draw</strong> 70 + 5%/lv to 77 + 7%/lv, and refunds 77 SP on use.",
         "<strong>Double Down</strong> 30 + 10%/lv to 35 + 15%/lv.",
     ]),
    ("Illusionist",
     "",
     ["<strong>Life Strings</strong> now grants 10% to 20% of the player's stats per level, duration and cooldown 10s to 30s."]),
    ("Dark Knight",
     "",
     [
         "<strong>Conflagration</strong> gains 50% base damage, HP scaling adjusted.",
         "<strong>Vengeance</strong> cooldown 1.4s to 2s, less HP-based scaling.",
         "<strong>Fatal Menace</strong> 150 + 10%/lv + 30% per missing HP to 150 + 15%/lv + 10% per missing HP.",
         "<strong>Night Menace</strong> 150 + 10%/lv + 50% per missing HP to 150 + 20%/lv + 25% per missing HP.",
         "<strong>Shatter Cross</strong> damage against frozen targets 3% to 10% per STR.",
         "<strong>Knight Ritual</strong> now boosts STR and VIT instead of AGI and DEX.",
     ]),
    ("Judge",
     "",
     [
         "New revolvers added to the pool.",
         "<strong>Death Sentence</strong> 50 + 10%/lv to 100 + 10%/lv, DEX scaling 1% to 3%, combo bonus 50% to 100%.",
         "<strong>Violent Barrage</strong> base 60% to 75%.",
         "<strong>Gun Swap</strong> DEX bonus from combo 2% to 3% per DEX.",
     ]),
    ("Vagabond and Legend",
     "No direct changes - only what flows down from the shared passives such as Improve Defense and Improve Wisdom.",
     []),
    ("Raider",
     "",
     [
         "Improve Defense and Improve Wisdom follow the thief rework.",
         "<strong>Dragon Thrust</strong> base 120% to 110%.",
         "<strong>Heavy Stab</strong> 50 + 30%/lv + 2%/VIT to 100 + 25%/lv + 3%/VIT.",
         "<strong>Wind Cutter</strong> base 40% to 60%.",
         "<strong>Spear Mastery</strong> one-hand spear HP 30 to 25 per level, two-hand spear 2 to 3 flee per level.",
     ]),
    ("Dracomancer",
     "Dragon Orbs are meant to be a strong extra, not a button you press to always transform and stomp everything.",
     [
         "Orb cooldowns 60-5s per level to a flat 90s.",
         "Orb duration flat 10s to 10 + 2s per level.",
         "<strong>Sky Prophecy</strong> cooldown 15s to 12s, cast time set to 2s.",
         "<strong>Crescent Dive</strong> scaling 15%/lv to 25%/lv.",
         "<strong>Geirskogul</strong> base 80% to 100%; 25% stun chance on dragons became 10% on any enemy.",
         "<strong>Draco Wings</strong> no longer costs 5% max HP.",
         "<strong>Dragon Breath</strong> 25%/lv to 30%/lv, cast time no longer grows with level.",
     ]),
    ("Trickster",
     "",
     [
         "<strong>Hellraiser</strong> base 110% to 150%, the level 10 requirement for Finisher Ready is gone, duration 3s to 5s.",
         "<strong>Sweeping Slash</strong> hits three times during Finisher Ready.",
     ]),
    ("Revenant",
     "",
     [
         "<strong>Ominous Presence</strong> takes on croc's overheal mechanic; its hit and critical damage were removed. 3% per level of the extra leeched damage becomes shield.",
         "<strong>Flaming Wave</strong> loses its cast time, burn 0.5 + 0.5s/lv to 2.5 + 0.5s/lv, cooldown fixed at 5s, damage 25%/lv to 30%/lv.",
         "<strong>Final Orchestra</strong> flat healing became 1% of the caster's max HP per pulse per skill level, and deals half that as damage plus knockback to anything standing in it. Max SP cost 50% to 25%.",
     ]),
    ("Peacekeeper",
     "",
     [
         "<strong>Chain Mastery</strong> ATK per level 3 to 1.",
         "<strong>Assault Mode</strong> DEF/MDEF pierce 5%/lv to 3%/lv.",
         "<strong>Use Trinket</strong> base 50% to 100%, 1% to 3% per DEX, cooldowns 5s to 4s and 15s to 10s for Crash.",
         "<strong>Lashing Andromeda</strong> 50 + 10%/lv + 1%/DEX to 50 + 15%/lv + 2%/DEX, cooldown 10s to 7s.",
         "<strong>Wrecking Andromeda</strong> 50 + 10%/lv + 1%/DEX to 100 + 15%/lv + 2%/DEX, cooldown 10s to 7s.",
     ]),
    ("Ronin",
     "",
     [
         "<strong>Ascending</strong> and <strong>Descending Steel</strong> INT scaling 1% to 2%.",
         "<strong>Ascending Steel</strong> grants Kaupe for 1 second.",
     ]),
    ("Shadowseer",
     "",
     ["Max job level 70 to 50.", "Magic Pierce removed from the tree."]),
    ("Prowler",
     "",
     ["Max job level 70 to 50. Nothing else changed."]),
]

ASSASSIN_BRANCH = [
    ("Blade Dancer / Night Raven",
     "croc's leech and ranged bonuses on the bird skills are kept.",
     [
         "<strong>Soul Destroyer</strong> applies poison to any target including bosses while Enchant Poison is up. 25 + 5%/lv chance, 5 + 1s/lv duration.",
         "<strong>Counter Slash</strong> starting cooldown 0.5s to 0.6s.",
         "<strong>Night Hunt</strong> hit count doubled (20 at level 10), HP loss per hit 5% to 7%, 1% damage per 1% missing HP, 1.25x at red health.",
         "<strong>Bloody Fangs</strong> range 11 to 3 cells, cooldown 4s to 5s, no more double damage with dual axes (folded into a flat 50%/lv + 5%/INT, still MATK based), triple damage at red health, ends Night Hunt early.",
         "<strong>Cloaking Exceed</strong> move speed 90 + 10%/lv to 40%/lv.",
         "<strong>Typhoon Edge</strong> now boosted by dual axes.",
         "<strong>Definitive Dagger</strong> range increased to 3 cells.",
     ]),
    ("Scoundrel / Black Plague",
     "Most toxins affect bosses, carried over from croc's build.",
     [
         "<strong>Venom Buster</strong> base cooldown 10s to 5s.",
         "<strong>Spiral Blade</strong> slightly faster repeat, damage per level 10% to 15%.",
         "<strong>Mjolnir's Fall</strong> damage per level 10% to 25%.",
         "<strong>Enchant Deadly Poison</strong> now negates the entire flat defence rather than 75% of it.",
     ]),
    ("Executioner / Gravekeeper",
     "Animation lock timers were reweighted toward after-cast delay.",
     [
         "<strong>Meteor Assault</strong> +5% damage per Rolling Counter.",
         "<strong>Exale Rage</strong> area doubled to 11x11.",
         "<strong>Mass Grave</strong> cast time removed.",
         "<strong>Guard Breaker</strong> final damage +25% per defensive buff on the target - Kyrie, Assumptio, Auto Guard, Defender, Reflect and friends.",
         "<strong>Fissure Tooth</strong> DEX scaling 2% to 3%.",
     ]),
    ("Shinobi / Satsujin",
     "Honestly the most balanced job in the game, and one of the hardest to play. It did not need changes.",
     [
         "<strong>Dragon Omamori</strong> DEX scaling 2% to 3%.",
         "<strong>Million Stab</strong> cooldown 15s to 7s, since it lost the gear that supported it.",
     ]),
]

ROGUE_BRANCH = [
    ("Mystic / Arcane Master",
     "Still one of the hardest jobs to play at full capacity.",
     [
         "<strong>Dual Cast</strong> duration and cooldown 15s to 30s.",
         "<strong>Unlimited Power</strong> duration 30s, cooldown 60s, magic defence pierce 3%/lv to 1%/lv, MATK bonus 3%/lv to 5%/lv. While it is up: every skill in the game loses its cooldown, every skill gains an irreducible 1s cast time, and every skill costs double SP.",
         "<strong>Comet</strong> cooldown 20s to 10s, INT scaling 6% to 7%.",
     ]),
    ("Saboteur / Blast Juggler",
     "Carry weight now scales off base level rather than STR, so hauling materials is easier.",
     [
         "<strong>Burning Field</strong> scaling 1%/lv to 2%/lv, cooldown 5s to 4s, fire bottle cost 3 to 2.",
         "<strong>Greater Explosion</strong> cooldown 10s to 8s, acid bottle cost 3 to 2.",
         "<strong>Hot Trap</strong> and <strong>Cold Trap</strong> now ignore defence; formula 150 + 5 x lv x INT becomes 100 + 10 x lv x INT.",
         "<strong>Claymore Trap</strong> ignores defence and triples damage against enemies at full HP.",
         "<strong>Cluster Bomb</strong> triples damage against enemies below 10% HP - this one does not ignore defence.",
         "<strong>Rolling Flames</strong> area halved to 3x3, hit detection twice as fast, no longer clears ground effects, scaling 15%/lv to 10%/lv.",
         "<strong>Fire Expansion</strong> passive bonus to Rolling Flames 20%/lv to 15%/lv.",
         "<strong>Mr. Bombastic</strong> INT scaling 3% to 2% per INT, and it remains the ground-clearing tool.",
     ]),
    ("Duelist / Kingslayer",
     "",
     [
         "<strong>Duel Stance</strong>: Riposte and Delta Skyfall gain 1% per VIT for every 2 duel counters (5% per VIT at cap).",
         "<strong>Retribution</strong> damage per counter doubled, SP cost 50 to 10.",
         "<strong>King's Chains</strong> weight influence up about 8%, and adds your soft and hard defence as extra final damage. Cooldown 5s to 8s.",
         "<strong>Queen's Gambit</strong> grants 5 duel counters on hit.",
         "<strong>King's Gambit</strong> grants 5 duel counters when it clears anything from the ground.",
         "<strong>Check Mate</strong> rebuilt: was a fixed 400 ATK multiplied by twice your total SP. Now a normal formula - 100 + 3 x current SP + current HP/10 as a percentage of attack.",
         "<strong>Bishop's Tax</strong> 30% (20% on bosses) against afflicted targets became a flat 15% against everything.",
     ]),
    ("Deadeye / Sinner",
     "The Godhand arrow combo window is more forgiving.",
     [
         "<strong>Sniper Nest</strong> fully reworked. It used to trade move speed and flee for damage. Now: -150 flee, +150 hit, Headshot and Aimed Bolt always crit while active, and all SP costs rise 25%.",
         "<strong>Headshot</strong> always deals full damage regardless of Sniper Nest, and its cooldown is halved when cast from the nest. Bonus per DEX during combo 15% to 10%.",
         "<strong>Aimed Bolt</strong> always critical inside Sniper Nest.",
         "<strong>Cannon Turret</strong> receives 7% per level of its owner's ATK, walks with them and attacks the same target.",
         "<strong>Arrow Storm</strong> cooldown 7s to 10s, damage 20%/lv to 25%/lv, DEX scaling 4% to 5%.",
     ]),
]

# --------------------------------------------------------------------------
# What the Refuge did to the original build, in the developers' own three
# buckets.
# --------------------------------------------------------------------------

TRANSFORMED = [
    "Many manuals became something else entirely, orphan skill manuals most of all.",
    "Heal and Hiding are capped at level 1. Heal scales properly with your stats and level; Hiding is a fixed 2 seconds that works on bosses, insects and demons, so it stops being dead weight late.",
    "Warp Portal became a default orphan skill that moves the caster and the whole party to a memorised point.",
    "Every player has Teleport level 1 by default, on a 60 second cooldown.",
    "Major rebalances across every job, aimed squarely at the skills nobody used.",
    "Monsters hit harder across the board, and healing is slower. The damage on a lot of skills went up to match.",
    "Shadowseer and Prowler top out at job level 50 instead of 70.",
    "Experience rate is slightly lower than the original, but the curve is more rewarding.",
    "Some debuffs land on bosses now - a thief's Envenom can poison one.",
    "Base attack speed re-adjusted on the jobs where it was simply strange.",
    "The orphanage got a visual pass, plus quality-of-life NPCs.",
    "All of croc's earlier work on the original build is folded in.",
]

ADDED = [
    "Over 300 new items.",
    "Over 50 new shadow sets covering every dungeon past level 100.",
    "Two SS dungeons, both finished, both on fully custom maps. One is Nightmare in Amatsu, for level 145 and up; the second has not been described.",
    "Bosses had their skills rebalanced, because Hiding now works against them.",
    "New locations, including new dungeons.",
    "New endgame content.",
    "Gear for the jobs that were short of it - Ronin and Peacekeeper in particular.",
    "The job rebalances that never arrived with the original 1.4.",
    "Two entirely new jobs: Bouncer and Pit Boss.",
    "Einherjar Challenge Mode, an optional locked-level run.",
    "Most of the original's known bugs, fixed.",
]

REMOVED = [
    "Weapon rarity. There is no rarity tier on weapons in the Refuge.",
    "Orbs for rerolling random options. What a piece rolls is what it rolled.",
    "Level 100+ job shadow sets. They locked players into one playstyle past 100; the replacement sets are built for variety and for the skills nobody was using.",
    "Manuals that no longer made sense after the Heal, Hiding and Warp Portal rework.",
    "Drop rate bonuses from gear.",
    "The old cash shop, in the form it had. How the server funds itself is being rethought from scratch, in the open - see <a href=\"server.html#money\">the funding note</a>.",
]

# --------------------------------------------------------------------------
# Pit Boss skill list, from the design post.
# --------------------------------------------------------------------------

PITBOSS_SKILLS = [
    ("Diplomacy", "A huge hit with a stun chance, scaled by how many punch-combo stacks you are holding."),
    ("Rebound Bash", "Chance to re-cast several times, boosted by DEX."),
    ("Thug Might", "A wave of pure rage down a long line, hitting everything before and after the target."),
    ("Stalemate", "Root, adapted to this job."),
    ("Soul Guard", "A brief damage reduction window."),
    ("Retreat Order", "Raises the defensive power of the whole party."),
    ("Merry-Go-Round", "An area effect centred on a nearby enemy that spins it and hits everything around it for partial damage."),
    ("Intimidating Glare", "Instantly breaks defences and debuffs a target at range. Mild damage."),
    ("Cross Punch", "A slow hit that takes you straight to 5 combo stacks."),
    ("Ruthless Mastery", "Passive. Raises the power of the job's skills."),
    ("Rough Skin", "Passive. Defence and damage mitigation."),
    ("Swanton Bomb", "Go up, come down, explode. Damage to yourself and everything nearby, based on HP."),
]

TIMELINE = [
    ("19 April 2026", "The call",
     "Metta reaches out after a poll on another project's server. Instead of a new server, he wants the old one back - and better. The project starts that day."),
    ("4 May 2026", "Doors open",
     "The community server goes public. No launch date, an open invitation to ask anything, and a promise: this is not a professional operation, it is a good place to play."),
    ("7-14 May 2026", "The rebalance posts",
     "Job-by-job change lists go up for the early game, the assassin branch and the rogue branch. Job shadow sets are confirmed gone."),
    ("14 May 2026", "Two new jobs",
     "Bouncer and Pit Boss are announced. A first job and a final job, fast progression between them, and a weapon type that did not exist before."),
    ("7 June 2026", "Bouncer plays",
     "Gameplay footage. Tanky, versatile, flexible - and it will drink your SP."),
    ("27 June 2026", "Pit Boss design",
     "The full skill tree, the golf clubs, the chains, and the reasoning behind fixed cast times."),
    ("5 July 2026", "Nightmare in Amatsu",
     "The SS dungeon is revealed. Level 150 recommended, no minimap, and a random spawn point."),
    ("1 August 2026", "Two more SS dungeons",
     "Both finished, both on fully custom maps. One of them stays secret."),
]

FAQS = [
    ("Is there a launch date?",
     "No fixed date. The team has said the current plan is August 2026 and called it roughly 95% likely, but they have missed one estimate already and would rather be honest than pin a day to a calendar. Watch the community server."),
    ("Is it free? Will there be a cash shop?",
     "It is free to play. Whether there is a shop, and what would be in it, has not been decided - and it would be dishonest to promise there will never be one. Hosting costs money and the people building this are doing real work that deserves to be paid for. What can be promised, and is: it will never sell power. No stats, no gear advantage, no progression you can buy past, and no real-money trading. Whatever the funding ends up being, it gets discussed with the community before it ships."),
    ("How is this different from the original?",
     "Hundreds of changes, but they all follow one idea: expand what worked, fix what did not. Over 300 new items, 50+ new shadow sets, two new jobs, new dungeons, a full job rebalance pass, and the removal of the systems that funnelled everyone into the same build."),
    ("Do job shadow sets still exist?",
     "No. This is the single most-asked question in the community server. The level 100+ job-locked shadow sets are gone. The new sets croc has been showing work for every job."),
    ("What is Einherjar Challenge Mode?",
     "An optional way to play. Your maximum level is locked and only rises when you defeat a boss of your own level. It removes the competition for boss spawns from your progression entirely. It awards costumes, not relics - the team decided free relics would turn it into a min-maxing farm."),
    ("Will the server close when something else launches?",
     "The team describes it as a small cozy town: updates at a reasonable pace, new content over time, no plans to close. The stated ambition is to go considerably further than the original ever did."),
    ("Is this related to any other project?",
     "No. It is its own thing, run by its own people, and the developers have said so repeatedly and unprompted."),
    ("Who runs it?",
     "Metta is head admin - hosting, costs, planning and progression. croc handles items, code and development. Ornstein handles design, job adjustments and the gameplay plan. There is a moderation team for the community side."),
    ("Will there be a control panel?",
     "Undecided. There will definitely be a database of information. Registration may go through the in-game command instead of a web panel."),
]
