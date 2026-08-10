/* The database.

   Two and a half thousand items and seven hundred monsters, filtered in the
   browser with no server and no framework. Four things make that work:

   1. Nothing is fetched until somebody asks for something. The dropdowns and
      their option lists are written into the page at build time, so the whole
      filter bar is usable while the 514 KB payload has not been requested at
      all - and for a reader who only came to look around, never is.
   2. The payload is column arrays with string tables, so the download is a
      third of what objects would cost.
   3. Filtering runs over plain arrays and a pre-folded lowercase string, so a
      keystroke is a linear scan of numbers, not of objects.
   4. A result set is painted forty rows at a time, on request. The old version
      kept painting until the viewport was full, which for a broad filter meant
      hundreds of rows nobody had asked to see.

   What it shows is the description the game itself puts in front of a player.
   The emulator's bonus scripts are deliberately not in the payload. */
(function () {
  'use strict';

  var root = document.getElementById('db');
  if (!root) return;

  var PREFIX = window.RTMR_PREFIX || '';
  var CHUNK = 40;

  var state = {
    tab: 'items',
    q: '',
    facets: {},
    sort: 'name',
    data: { items: null, mobs: null },
    matched: [],
    painted: 0,
    live: false        // has anything been asked for yet
  };

  var els = {
    list: document.getElementById('db-list'),
    count: document.getElementById('db-count'),
    bar: document.getElementById('db-bar'),
    empty: document.getElementById('db-empty'),
    start: document.getElementById('db-start'),
    page: document.getElementById('db-page'),
    facets: document.getElementById('db-facets'),
    extra: root.querySelector('.db-extra'),
    sort: document.getElementById('db-sort'),
    q: document.getElementById('db-q'),
    detail: document.getElementById('db-detail'),
    detailInner: document.getElementById('db-detail-inner')
  };

  function fold(s) {
    return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function num(n) {
    return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  /* Rates arrive as percentages already. A hundred is a guaranteed drop; the
     rarest things in the game sit at three decimal places. */
  function rate(p) {
    if (p >= 100) return '100%';
    if (p >= 1) return (Math.round(p * 100) / 100) + '%';
    return (Math.round(p * 1000) / 1000) + '%';
  }

  /* Anything under a tenth of a percent is worth flagging as a grind. */
  function rateClass(p) {
    if (p >= 50) return 'is-common';
    if (p >= 5) return 'is-uncommon';
    if (p >= 0.5) return 'is-rare';
    return 'is-veryrare';
  }

  /* ---- the codex ---------------------------------------------------------
     The same term table the skill tables are marked up with at build time.
     Item text arrives with the payload, so the marking has to happen here.
     Loaded once, lazily, and the drawer renders fine without it. */

  var codex = null;
  var codexAsked = false;

  /* Only the drawer marks terms up, so this waits for the first drawer rather
     than costing every visitor a request they may never use. */
  function wantCodex() {
    if (codexAsked) return;
    codexAsked = true;
    fetch(PREFIX + 'assets/data/codex.json')
      .then(function (r) { return r.json(); })
      .then(function (d) {
        // Longest spelling first, so "Magic Defense Pierce" wins over
        // "Defense Pierce". The payload is already in that order.
        codex = {
          map: {},
          re: new RegExp('(?<![\\w-])(' + d.terms.map(function (t) {
            return t[0].replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          }).join('|') + ')(?![\\w-])', 'g')
        };
        d.terms.forEach(function (t) { codex.map[t[0]] = t; });
      })
      .catch(function () { codex = null; });
  }

  /* Takes escaped text, returns escaped text with links added. */
  function terms(escaped) {
    if (!codex) return escaped;
    return escaped.replace(codex.re, function (m) {
      var t = codex.map[m];
      return '<a class="term term--' + t[3] + '" href="' + PREFIX + 'codex.html#' +
        t[1] + '" title="' + esc(t[2]) + '">' + m + '</a>';
    });
  }

  function sprite(id, name) {
    // The box is taller than it is wide because the sprites are: a Poring is
    // a ball and a Seyren is a man on a horse. Reserving the tall box for all
    // of them keeps the list from reflowing as they arrive.
    return '<img class="db-sprite" loading="lazy" decoding="async" width="56" height="64" ' +
      'src="' + PREFIX + 'assets/sprites/' + id + '.gif" alt="" ' +
      'onerror="this.style.visibility=\'hidden\'" data-mob="' + esc(name) + '">';
  }

  /* ---- loading ---------------------------------------------------------- */

  function load(tab) {
    if (state.data[tab]) return Promise.resolve(state.data[tab]);
    var file = tab === 'items' ? 'db-items.json' : 'db-mobs.json';
    return fetch(PREFIX + 'assets/data/' + file)
      .then(function (r) { return r.json(); })
      .then(function (raw) {
        var C = {};
        raw.cols.forEach(function (name, i) { C[name] = i; });
        raw.rows.forEach(function (row) {
          // One folded string per row, built once, searched on every keystroke.
          // The description is in it, so "reduces cast time" finds the gear
          // that does it without anybody knowing an item name.
          var extra = tab === 'items'
            ? raw.cats[row[C.cat]] + ' ' + row[C.desc]
            : raw.races[row[C.race]] + ' ' + raw.zones[row[C.zone]] + ' ' +
              row[C.card] + ' ' + row[C.drops].map(function (d) {
                return raw.items[d[0]];
              }).join(' ');
          row.__f = fold(row[C.name] + ' ' + extra);
        });
        raw.C = C;
        state.data[tab] = raw;
        return raw;
      });
  }

  /* ---- facets ----------------------------------------------------------- */

  // Each facet is a column plus how to read it. `multi` means the cell is a
  // list of indices (an item can occupy two slots), `flag` a 0/1 column,
  // `flagLen` a list that should not be empty, and `range` two number inputs.
  //
  // `pick` marks the four or five that are the page's front door. Those are
  // <select> elements written into the HTML at build time, so they are listed
  // here only so that matching knows how to read them; renderFacets skips them
  // and the rest arrive folded behind "More filters".
  var FACETS = {
    items: [
      { key: 'grp', col: 'grp', table: 'grps', pick: true },
      { key: 'loc', col: 'loc', table: 'locs', multi: true, pick: true },
      { key: 'cat', col: 'cat', table: 'cats', pick: true },
      { key: 'slots', label: 'Card slots', col: 'slots', numbers: [0, 1, 2, 3, 4] },
      { key: 'lv', label: 'Required level', col: 'lv', range: true },
      { key: 'jobs', label: 'Usable by', col: 'jobs', table: 'jobs', skipEmpty: true, wide: true },
      { key: 'refine', label: 'Refineable', col: 'refine', flag: true },
      { key: 'src', label: 'Dropped by a monster', col: 'src', flagLen: true },
      { key: 'zones', label: 'Drops in', col: 'zones', table: 'zones', multi: true, wide: true }
    ],
    mobs: [
      { key: 'zone', col: 'zone', table: 'zones', pick: true },
      { key: 'race', col: 'race', table: 'races', pick: true },
      { key: 'element', col: 'element', table: 'elements', pick: true },
      { key: 'size', col: 'size', table: 'sizes', pick: true },
      { key: 'mvp', label: 'MVP only', col: 'mvp', flag: true },
      { key: 'lv', label: 'Level', col: 'lv', range: true },
      { key: 'drops', label: 'Drops something', col: 'drops', flagLen: true },
      { key: 'maps', label: 'Map', col: 'maps', table: 'maps', multi: true, wide: true }
    ]
  };

  var SORTS = {
    items: [['name', 'Name'], ['lv', 'Required level'], ['atk', 'Attack'],
            ['matk', 'Magic attack'], ['def', 'Defense'], ['slots', 'Card slots'],
            ['weight', 'Weight'], ['src', 'Drop sources']],
    mobs: [['name', 'Name'], ['lv', 'Level'], ['hp', 'Health'],
           ['exp', 'Base EXP'], ['jexp', 'Job EXP'], ['drops', 'Number of drops']]
  };

  function facetValues(data, facet) {
    var col = data.C[facet.col];
    var counts = {};
    data.rows.forEach(function (row) {
      var cell = row[col];
      if (facet.multi) {
        (cell || []).forEach(function (v) { counts[v] = (counts[v] || 0) + 1; });
      } else {
        counts[cell] = (counts[cell] || 0) + 1;
      }
    });
    return counts;
  }

  function renderFacets() {
    var data = state.data[state.tab];
    var out = [];
    FACETS[state.tab].forEach(function (facet) {
      if (facet.pick) return;   // it already has a dropdown of its own
      var body = '';
      if (facet.range) {
        var sel = state.facets[facet.key] || {};
        body = '<div class="db-range">' +
          '<label class="visually-hidden" for="f-' + facet.key + '-min">Minimum</label>' +
          '<input class="field" id="f-' + facet.key + '-min" type="number" inputmode="numeric" placeholder="min"' +
          ' data-range="' + facet.key + '" data-edge="min" value="' + (sel.min != null ? sel.min : '') + '">' +
          '<span aria-hidden="true">to</span>' +
          '<label class="visually-hidden" for="f-' + facet.key + '-max">Maximum</label>' +
          '<input class="field" id="f-' + facet.key + '-max" type="number" inputmode="numeric" placeholder="max"' +
          ' data-range="' + facet.key + '" data-edge="max" value="' + (sel.max != null ? sel.max : '') + '">' +
          '</div>';
      } else if (facet.flag || facet.flagLen) {
        var on = state.facets[facet.key] === 1;
        body = '<label class="db-check"><input type="checkbox" data-flag="' + facet.key + '"' +
          (on ? ' checked' : '') + '> <span>Only these</span></label>';
      } else if (facet.numbers) {
        body = facet.numbers.map(function (n) {
          var picked = (state.facets[facet.key] || []).indexOf(n) !== -1;
          var label = facet.numberLabels ? facet.numberLabels[n] : n;
          return '<label class="db-check"><input type="checkbox" data-facet="' + facet.key +
            '" value="' + n + '"' + (picked ? ' checked' : '') + '> <span>' + label + '</span></label>';
        }).join('');
      } else {
        var counts = facetValues(data, facet);
        var table = data[facet.table] || [];
        var entries = Object.keys(counts).map(function (i) {
          return { i: +i, label: table[+i], n: counts[i] };
        }).filter(function (e) {
          return e.label && !(facet.skipEmpty && !e.label.trim());
        }).sort(function (a, b) { return b.n - a.n || a.label.localeCompare(b.label); });

        // A facet with three hundred values is a wall. Show the useful ones
        // and let the rest arrive behind a toggle.
        var limit = facet.wide ? 8 : 12;
        body = entries.map(function (e, idx) {
          var picked = (state.facets[facet.key] || []).indexOf(e.i) !== -1;
          return '<label class="db-check' + (idx >= limit ? ' is-extra' : '') + '">' +
            '<input type="checkbox" data-facet="' + facet.key + '" value="' + e.i + '"' +
            (picked ? ' checked' : '') + '> <span>' + esc(e.label) + '</span>' +
            '<span class="db-n mono">' + num(e.n) + '</span></label>';
        }).join('');
        if (entries.length > limit) {
          body += '<button type="button" class="db-more" data-more>' +
            'Show ' + (entries.length - limit) + ' more</button>';
        }
      }

      out.push('<details class="db-facet"' + (facet.wide ? '' : ' open') + '>' +
        '<summary>' + esc(facet.label) + '</summary>' +
        '<div class="db-facet-body">' + body + '</div></details>');
    });
    els.facets.innerHTML = out.join('');

    els.sort.innerHTML = SORTS[state.tab].map(function (s) {
      return '<option value="' + s[0] + '"' + (s[0] === state.sort ? ' selected' : '') +
        '>' + s[1] + '</option>';
    }).join('');
  }

  /* ---- filtering -------------------------------------------------------- */

  function matches(row, data) {
    var C = data.C;
    if (state.q && row.__f.indexOf(state.q) === -1) return false;

    var ok = true;
    FACETS[state.tab].forEach(function (facet) {
      if (!ok) return;
      var picked = state.facets[facet.key];
      if (picked == null) return;
      var cell = row[C[facet.col]];

      if (facet.range) {
        if (picked.min != null && cell < picked.min) ok = false;
        if (picked.max != null && cell > picked.max) ok = false;
      } else if (facet.flag) {
        if (picked === 1 && !cell) ok = false;
      } else if (facet.flagLen) {
        if (picked === 1 && !(cell && cell.length)) ok = false;
      } else if (picked.length) {
        if (facet.multi) {
          var hit = (cell || []).some(function (v) { return picked.indexOf(v) !== -1; });
          if (!hit) ok = false;
        } else if (picked.indexOf(cell) === -1) {
          ok = false;
        }
      }
    });
    return ok;
  }

  /* Nobody has asked for anything: no query, no filter. That is the page's
     resting state, and it shows six chips rather than two thousand rows. */
  function idle() {
    if (state.q) return false;
    for (var key in state.facets) {
      if (state.facets[key] != null) return false;
    }
    return true;
  }

  function showIdle() {
    state.matched = [];
    state.painted = 0;
    els.list.innerHTML = '';
    els.start.hidden = false;
    els.bar.hidden = true;
    els.empty.hidden = true;
    els.page.hidden = true;
  }

  function apply() {
    if (idle()) { showIdle(); saveUrl(); return; }
    var data = state.data[state.tab];
    if (!data) return;
    els.start.hidden = true;
    els.bar.hidden = false;
    var C = data.C;
    state.matched = data.rows.filter(function (row) { return matches(row, data); });

    var col = C[state.sort];
    var byName = state.sort === 'name';
    var byLength = state.sort === 'src' || state.sort === 'drops';
    state.matched.sort(function (a, b) {
      if (byName) return String(a[C.name]).localeCompare(String(b[C.name]));
      var av = byLength ? (a[col] || []).length : a[col];
      var bv = byLength ? (b[col] || []).length : b[col];
      return (bv - av) || String(a[C.name]).localeCompare(String(b[C.name]));
    });

    els.count.textContent = num(state.matched.length) + ' of ' + num(data.rows.length);
    els.empty.hidden = state.matched.length > 0;
    els.list.innerHTML = '';
    state.painted = 0;
    paint();
    saveUrl();
  }

  /* ---- painting --------------------------------------------------------- */

  /* The first line or two of a description is the part that identifies the
     item. Anything past that is set bonuses and refine tables, which belong
     in the drawer rather than in a list row. */
  function blurb(desc) {
    if (!desc) return '';
    var lines = desc.split('\n').filter(function (l) { return l.trim(); });
    return lines.slice(0, 2).join(' · ');
  }

  function itemCard(row, data) {
    var C = data.C;
    var stats = [];
    if (row[C.atk]) stats.push('ATK ' + row[C.atk]);
    if (row[C.matk]) stats.push('MATK ' + row[C.matk]);
    if (row[C.def]) stats.push('DEF ' + row[C.def]);
    if (row[C.slots]) stats.push(row[C.slots] + '× slot');
    if (row[C.lv]) stats.push('Lv ' + row[C.lv]);
    var loc = (row[C.loc] || []).map(function (i) { return data.locs[i]; }).join(' / ');
    var hue = data.hues[row[C.grp]];

    return '<li class="db-row"><button type="button" class="db-entry" data-open="' + row[C.id] + '">' +
      '<span class="db-chip db-chip--' + hue + '" aria-hidden="true"></span>' +
      '<span class="db-body">' +
        '<span class="db-name">' + esc(row[C.name]) + '</span>' +
        '<span class="db-tags">' +
          '<span class="badge badge--' + hue + '">' + esc(data.cats[row[C.cat]]) + '</span>' +
          (loc ? '<span class="db-sub">' + esc(loc) + '</span>' : '') +
        '</span>' +
        (stats.length ? '<span class="db-stats mono">' + stats.map(function (s) {
          return '<span>' + s + '</span>';
        }).join('') + '</span>' : '') +
        (row[C.desc] ? '<span class="db-fx">' + esc(blurb(row[C.desc])) + '</span>' : '') +
      '</span></button></li>';
  }

  function mobCard(row, data) {
    var C = data.C;
    var drops = row[C.drops].length;
    return '<li class="db-row"><button type="button" class="db-entry db-entry--mob" data-open="' + row[C.id] + '">' +
      sprite(row[C.id], row[C.name]) +
      '<span class="db-body">' +
        '<span class="db-name">' + esc(row[C.name]) +
          (row[C.mvp] ? ' <span class="badge rank-ss">MVP</span>' : '') +
        '</span>' +
        '<span class="db-tags">' +
          '<span class="badge">Lv ' + row[C.lv] + '</span>' +
          '<span class="db-sub">' + esc(data.races[row[C.race]]) + '</span>' +
          '<span class="db-sub">' + esc(data.elements[row[C.element]]) +
            (row[C.elv] ? ' ' + row[C.elv] : '') + '</span>' +
          '<span class="db-sub">' + esc(data.sizes[row[C.size]]) + '</span>' +
        '</span>' +
        '<span class="db-stats mono"><span>HP ' + num(row[C.hp]) + '</span>' +
          (row[C.exp] ? '<span>EXP ' + num(row[C.exp]) + '</span>' : '') +
          '<span>' + esc(data.zones[row[C.zone]]) + '</span></span>' +
        (drops ? '<span class="db-fx">' + drops + (drops === 1 ? ' drop' : ' drops') + '</span>' : '') +
      '</span></button></li>';
  }

  /* Forty rows, then a button. Infinite scroll used to keep painting until the
     viewport was full, which for "every weapon" meant several hundred rows
     nobody had asked for and a page you could not reach the end of. */
  function paint() {
    var data = state.data[state.tab];
    var slice = state.matched.slice(state.painted, state.painted + CHUNK);
    if (slice.length) {
      var render = state.tab === 'items' ? itemCard : mobCard;
      els.list.insertAdjacentHTML('beforeend', slice.map(function (r) {
        return render(r, data);
      }).join(''));
      state.painted += slice.length;
    }
    var left = state.matched.length - state.painted;
    els.page.hidden = left <= 0;
    els.page.textContent = 'Show ' + num(Math.min(left, CHUNK)) + ' more';
  }

  /* ---- detail ----------------------------------------------------------- */

  function findRow(tab, id) {
    var data = state.data[tab];
    if (!data) return null;
    var col = data.C.id;
    for (var i = 0; i < data.rows.length; i++) {
      if (data.rows[i][col] === id) return data.rows[i];
    }
    return null;
  }

  function statList(pairs) {
    var kept = pairs.filter(function (p) {
      return p[1] !== '' && p[1] !== 0 && p[1] != null;
    });
    return '<dl class="db-detail-stats">' + kept.map(function (p) {
      return '<div><dt>' + p[0] + '</dt><dd>' + esc(p[1]) + '</dd></div>';
    }).join('') + '</dl>';
  }

  function itemDetail(row, data) {
    var C = data.C;
    var html = '<p class="db-detail-kind"><span class="badge badge--' +
      data.hues[row[C.grp]] + '">' + esc(data.cats[row[C.cat]]) + '</span></p>' +
      '<h2>' + esc(row[C.name]) + '</h2>';

    if (row[C.desc]) {
      html += '<div class="db-desc">' + row[C.desc].split('\n').map(function (line) {
        return line.trim() ? '<p>' + terms(esc(line)) + '</p>' : '';
      }).join('') + '</div>';
    }

    html += statList([
      ['Slot', (row[C.loc] || []).map(function (i) { return data.locs[i]; }).join(', ')],
      ['Card slots', row[C.slots]],
      ['Attack', row[C.atk]], ['Magic attack', row[C.matk]],
      ['Defense', row[C.def]], ['Magic defense', row[C.mdef]],
      ['Required level', row[C.lv]], ['Weight', row[C.weight]],
      ['Refineable', row[C.refine] ? 'Yes' : ''],
      ['Usable by', data.jobs[row[C.jobs]]]
    ]);

    html += '<h3>Where it drops</h3>';
    var src = row[C.src];
    if (!src.length) {
      html += '<p class="dim">No monster drops this. It comes from a shop, a ' +
        'quest, a craft or an exchange.</p>';
    } else {
      html += '<ul class="db-drops">' + src.map(function (s) {
        return '<li>' +
          '<button type="button" class="db-link" data-jump-mob="' + s[0] + '">' +
            esc(data.mobs[s[1]]) + '</button>' +
          '<span class="dim">Lv ' + s[2] + ' · ' + esc(data.zones[s[3]]) + '</span>' +
          '<span class="mono db-rate ' + rateClass(s[4]) + '">' + rate(s[4]) + '</span>' +
          (s[5] ? '<span class="badge rank-ss">MVP</span>' : '') +
          '</li>';
      }).join('') + '</ul>';
    }
    return html;
  }

  function mobDetail(row, data) {
    var C = data.C;
    var html = '<div class="db-detail-head">' + sprite(row[C.id], row[C.name]) +
      '<div><h2>' + esc(row[C.name]) +
      (row[C.mvp] ? ' <span class="badge rank-ss">MVP</span>' : '') + '</h2>' +
      '<p class="dim">Level ' + row[C.lv] + ' · ' +
      esc(data.races[row[C.race]]) + ' · ' +
      esc(data.elements[row[C.element]]) + (row[C.elv] ? ' ' + row[C.elv] : '') +
      '</p></div></div>';

    html += statList([
      ['Health', num(row[C.hp])],
      ['Size', data.sizes[row[C.size]]],
      ['Zone', data.zones[row[C.zone]]],
      ['Base EXP', row[C.exp] ? num(row[C.exp]) : ''],
      ['Job EXP', row[C.jexp] ? num(row[C.jexp]) : ''],
      ['Attack', row[C.atk]], ['Defense', row[C.def]],
      ['Magic defense', row[C.mdef]]
    ]);

    if (row[C.card]) {
      html += '<h3>Its card</h3><div class="db-desc"><p>' + terms(esc(row[C.card])) + '</p>' +
        (row[C.cslot] ? '<p class="dim">Goes in: ' + esc(row[C.cslot]) + '</p>' : '') +
        '</div>';
    }

    html += '<h3>Drops</h3>';
    if (!row[C.drops].length) {
      html += '<p class="dim">Drops nothing.</p>';
    } else {
      html += '<ul class="db-drops">' + row[C.drops].map(function (d) {
        var name = esc(data.items[d[0]]);
        return '<li>' + (d[2]
            ? '<button type="button" class="db-link" data-jump-item="' + d[2] + '">' + name + '</button>'
            : '<span>' + name + '</span>') +
          '<span class="mono db-rate ' + rateClass(d[1]) + '">' + rate(d[1]) + '</span></li>';
      }).join('') + '</ul>';
    }

    var maps = (row[C.maps] || []).map(function (i) { return data.maps[i]; });
    if (maps.length) {
      html += '<h3>Found on</h3><p class="mono db-maps">' +
        maps.map(esc).join(', ') + '</p>';
    }
    return html;
  }

  function openDetail(id) {
    var data = state.data[state.tab];
    var row = findRow(state.tab, id);
    if (!row) return;

    els.detailInner.innerHTML =
      '<button type="button" class="icon-btn db-close" data-detail-close aria-label="Close">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">' +
      '<path d="M6 6l12 12M18 6L6 18" stroke-linecap="round"/></svg></button>' +
      (state.tab === 'items' ? itemDetail(row, data) : mobDetail(row, data));
    els.detail.hidden = false;
    els.detail.dataset.open = 'true';
    els.detail.scrollTop = 0;
    saveUrl(id);
  }

  function closeDetail() {
    els.detail.dataset.open = 'false';
    els.detail.hidden = true;
    saveUrl();
  }

  /* Following a drop in either direction is the point of the whole page, so a
     name in the drawer switches tab, clears the filters and opens the other
     record. Loading the other payload is the only asynchronous part. */
  function jump(tab, id) {
    switchTab(tab, function () { openDetail(id); });
  }

  /* ---- url state -------------------------------------------------------- */

  function saveUrl(openId) {
    var p = new URLSearchParams();
    if (state.tab !== 'items') p.set('tab', state.tab);
    if (state.q) p.set('q', els.q.value);
    if (state.sort !== 'name') p.set('sort', state.sort);
    // Keep ?kind= in the address for as long as it is still the filter, so
    // reloading or sharing the page keeps the slice somebody arrived at.
    var grp = state.facets.grp;
    if (state.tab === 'items' && grp && grp.length === 1 && state.data.items) {
      p.set('kind', state.data.items.grps[grp[0]]);
    }
    if (openId) p.set('id', openId);
    var qs = p.toString();
    history.replaceState(null, '', qs ? '?' + qs : location.pathname);
  }

  var pendingKind = '';

  function readUrl() {
    var p = new URLSearchParams(location.search);
    if (p.get('tab') === 'mobs') state.tab = 'mobs';
    if (p.get('q')) { state.q = fold(p.get('q')); els.q.value = p.get('q'); }
    if (p.get('sort')) state.sort = p.get('sort');
    pendingKind = p.get('kind') || '';
    return p.get('id') ? +p.get('id') : 0;
  }

  /* ?kind=Shadow+gear preselects the Kind dropdown, so a page elsewhere on the
     site can link straight at one slice of the database. It takes the label
     rather than the index because the index is a build detail and would
     silently point somewhere else the next time the data is rebuilt. */
  function applyUrlFacet() {
    var data = state.data.items;
    if (!pendingKind || state.tab !== 'items' || !data) return;
    var i = data.grps.indexOf(pendingKind);
    if (i !== -1) state.facets.grp = [i];
    pendingKind = '';
  }

  /* ---- the dropdowns -----------------------------------------------------
     Their options are in the HTML already. These two keep the elements and
     `state.facets` saying the same thing in both directions. */

  function picks() {
    return root.querySelectorAll('[data-pick]');
  }

  function syncPicks() {
    picks().forEach(function (sel) {
      if (sel.dataset.tab !== state.tab) { sel.value = ''; return; }
      var v = state.facets[sel.dataset.pick];
      sel.value = (v && v.length === 1) ? String(v[0]) : '';
    });
  }

  function showPicksFor(tab) {
    root.querySelectorAll('[data-picks]').forEach(function (box) {
      box.hidden = box.dataset.picks !== tab;
    });
  }

  /* The payload is fetched here and nowhere else, on the first thing anybody
     asks for. A visitor who reads the page and leaves never downloads it. */
  function ensure(then) {
    if (state.data[state.tab]) { then(); return; }
    // Fired alongside the payload so the first drawer already has it.
    wantCodex();
    els.start.hidden = true;
    els.bar.hidden = false;
    els.count.textContent = 'Loading...';
    load(state.tab).then(function () {
      renderFacets();
      then();
    });
  }

  /* ---- events ----------------------------------------------------------- */

  var timer;
  els.q.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      state.q = fold(els.q.value.trim());
      ensure(apply);
    }, 160);
  });

  els.sort.addEventListener('change', function () {
    state.sort = els.sort.value;
    ensure(apply);
  });

  /* One dropdown is one value. Two of them at once is what "More filters" is
     for, and that is where multi-select lives. */
  root.addEventListener('change', function (e) {
    var sel = e.target.closest('[data-pick]');
    if (!sel) return;
    state.facets[sel.dataset.pick] = sel.value === '' ? null : [+sel.value];
    ensure(apply);
  });

  root.addEventListener('click', function (e) {
    var chip = e.target.closest('[data-quick]');
    if (!chip) return;
    var bits = chip.dataset.quick.split(':');
    switchTab(bits[0], function () {
      // A 0/1 column is matched against the number 1, everything else against
      // a list of indices. Setting the wrong shape silently matches every row.
      var facet = FACETS[bits[0]].filter(function (f) {
        return f.key === bits[1];
      })[0];
      state.facets[bits[1]] =
        (facet && (facet.flag || facet.flagLen)) ? 1 : [+bits[2]];
      syncPicks();
      apply();
    });
  });

  els.page.addEventListener('click', paint);

  els.extra.addEventListener('toggle', function () {
    if (!els.extra.open || state.data[state.tab]) return;
    load(state.tab).then(renderFacets);
  });

  els.facets.addEventListener('change', function (e) {
    var box = e.target;
    if (box.dataset.facet) {
      var key = box.dataset.facet;
      var val = +box.value;
      var list = state.facets[key] || [];
      if (box.checked) list = list.concat([val]);
      else list = list.filter(function (v) { return v !== val; });
      state.facets[key] = list.length ? list : null;
      apply();
    } else if (box.dataset.flag) {
      state.facets[box.dataset.flag] = box.checked ? 1 : null;
      ensure(apply);
    } else if (box.dataset.range) {
      var cur = state.facets[box.dataset.range] || {};
      cur[box.dataset.edge] = box.value === '' ? null : +box.value;
      state.facets[box.dataset.range] =
        (cur.min == null && cur.max == null) ? null : cur;
      ensure(apply);
    }
  });

  els.facets.addEventListener('click', function (e) {
    var more = e.target.closest('[data-more]');
    if (!more) return;
    more.parentNode.classList.add('is-expanded');
    more.remove();
  });

  document.getElementById('db-reset').addEventListener('click', function () {
    state.facets = {};
    state.q = '';
    els.q.value = '';
    syncPicks();
    if (state.data[state.tab]) renderFacets();
    apply();
  });

  els.list.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-open]');
    if (btn) openDetail(+btn.dataset.open);
  });

  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-detail-close]')) { closeDetail(); return; }
    var toMob = e.target.closest('[data-jump-mob]');
    if (toMob) { jump('mobs', +toMob.dataset.jumpMob); return; }
    var toItem = e.target.closest('[data-jump-item]');
    if (toItem) jump('items', +toItem.dataset.jumpItem);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && els.detail.dataset.open === 'true') closeDetail();
  });

  function markTabs() {
    root.querySelectorAll('[data-db-tab]').forEach(function (t) {
      t.setAttribute('aria-selected', String(t.dataset.dbTab === state.tab));
    });
  }

  function switchTab(name, then) {
    if (name !== state.tab) {
      state.tab = name;
      state.facets = {};
      state.sort = 'name';
      // The query has to go with the facets. Leaving "jellopy" in the box
      // while switching to monsters shows an empty list with no visible cause.
      state.q = '';
      els.q.value = '';
      els.extra.open = false;
      els.facets.innerHTML = '';
      syncPicks();
      closeDetail();
    }
    markTabs();
    showPicksFor(name);
    // Switching tab with nothing selected is browsing, not asking. The other
    // payload stays unfetched until it is actually wanted.
    if (!then && idle()) { apply(); return; }
    ensure(function () { apply(); if (then) then(); });
  }

  root.querySelectorAll('[data-db-tab]').forEach(function (tab) {
    tab.addEventListener('click', function () {
      if (tab.dataset.dbTab !== state.tab) switchTab(tab.dataset.dbTab);
    });
  });

  /* ---- boot -------------------------------------------------------------
     A first visit fetches nothing at all. Only a URL that already names
     something - a query, a kind, an open record - opens the payload. */

  var openId = readUrl();
  markTabs();
  showPicksFor(state.tab);

  if (openId || state.q || pendingKind) {
    ensure(function () {
      applyUrlFacet();
      syncPicks();
      apply();
      if (openId) openDetail(openId);
    });
  } else {
    apply();
  }
})();
