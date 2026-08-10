/* The database.

   Eleven thousand items and two thousand monsters, filtered in the browser
   with no server and no framework. Three things make that work:

   1. The payload is column arrays with string tables, so the download is a
      third of what objects would cost.
   2. Filtering runs over plain arrays and a pre-folded lowercase name, so a
      keystroke is a linear scan of numbers, not of objects.
   3. Nothing is painted until it is near the viewport. A filter that matches
      five thousand rows renders sixty of them. */
(function () {
  'use strict';

  var root = document.getElementById('db');
  if (!root) return;

  var PREFIX = window.RTMR_PREFIX || '';
  var CHUNK = 60;

  var state = {
    tab: 'items',
    q: '',
    facets: {},
    sort: 'name',
    dir: 1,
    data: { items: null, mobs: null },
    matched: [],
    painted: 0
  };

  var els = {
    list: document.getElementById('db-list'),
    count: document.getElementById('db-count'),
    empty: document.getElementById('db-empty'),
    sentinel: document.getElementById('db-sentinel'),
    facets: document.getElementById('db-facets'),
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

  /* Drop rates are stored the way the server stores them: out of 10000. */
  function rate(r) {
    if (r >= 100) return (r / 100).toFixed(r % 100 ? 2 : 0) + '%';
    if (r >= 10) return (r / 100).toFixed(2) + '%';
    return (r / 100).toFixed(3).replace(/0+$/, '') + '%';
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
          row.__f = fold(row[C.name] + ' ' + (row[C.fx] != null ? row[C.fx] : ''));
        });
        raw.C = C;
        state.data[tab] = raw;
        return raw;
      });
  }

  /* ---- facets ----------------------------------------------------------- */

  // Each facet is a column plus how to read it. `multi` means the cell is a
  // list of indices (an item can occupy two slots), `flag` a 0/1 column, and
  // `range` a pair of number inputs.
  var FACETS = {
    items: [
      { key: 'type', label: 'Type', col: 'type', table: 'types' },
      { key: 'sub', label: 'Weapon / shield type', col: 'sub', table: 'subs', skipEmpty: true },
      { key: 'loc', label: 'Equipment slot', col: 'loc', table: 'locs', multi: true },
      { key: 'slots', label: 'Card slots', col: 'slots', numbers: [0, 1, 2, 3, 4] },
      { key: 'lv', label: 'Required level', col: 'lv', range: true },
      { key: 'jobs', label: 'Usable by', col: 'jobs', table: 'jobs', skipEmpty: true, wide: true },
      { key: 'refine', label: 'Refineable', col: 'refine', flag: true },
      { key: 'drops', label: 'Dropped by a monster', col: 'drops', flagGt: true }
    ],
    mobs: [
      { key: 'race', label: 'Race', col: 'race', table: 'races' },
      { key: 'element', label: 'Element', col: 'element', table: 'elements' },
      { key: 'size', label: 'Size', col: 'size', table: 'sizes' },
      { key: 'rank', label: 'Rank', col: 'rank', numbers: [0, 1, 2],
        numberLabels: { 0: 'Normal', 1: 'MVP', 2: 'Mini-boss' } },
      { key: 'lv', label: 'Level', col: 'lv', range: true }
    ]
  };

  var SORTS = {
    items: [['name', 'Name'], ['lv', 'Required level'], ['atk', 'Attack'],
            ['matk', 'Magic attack'], ['def', 'Defense'], ['slots', 'Slots'],
            ['weight', 'Weight'], ['drops', 'Drop sources']],
    mobs: [['name', 'Name'], ['lv', 'Level'], ['hp', 'Health'], ['exp', 'Base EXP'],
           ['jexp', 'Job EXP'], ['atk', 'Attack'], ['def', 'Defense']]
  };

  function facetValues(data, facet) {
    var C = data.C, col = C[facet.col];
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
      } else if (facet.flag || facet.flagGt) {
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

        // A facet with sixty values is a wall. Show the useful ones and let
        // the rest arrive behind a toggle.
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

      out.push('<details class="db-facet" open>' +
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
      } else if (facet.flagGt) {
        if (picked === 1 && !(cell > 0)) ok = false;
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

  function apply() {
    var data = state.data[state.tab];
    if (!data) return;
    var C = data.C;
    state.matched = data.rows.filter(function (row) { return matches(row, data); });

    var col = C[state.sort];
    var byName = state.sort === 'name';
    state.matched.sort(function (a, b) {
      if (byName) return String(a[C.name]).localeCompare(String(b[C.name]));
      return (b[col] - a[col]) || String(a[C.name]).localeCompare(String(b[C.name]));
    });

    els.count.textContent = num(state.matched.length) + ' of ' + num(data.rows.length);
    els.empty.hidden = state.matched.length > 0;
    els.list.innerHTML = '';
    state.painted = 0;
    paint();
    saveUrl();
  }

  /* ---- painting --------------------------------------------------------- */

  function itemCard(row, data) {
    var C = data.C;
    var stats = [];
    if (row[C.atk]) stats.push(['ATK', row[C.atk]]);
    if (row[C.matk]) stats.push(['MATK', row[C.matk]]);
    if (row[C.def]) stats.push(['DEF', row[C.def]]);
    if (row[C.slots]) stats.push(['Slots', row[C.slots]]);
    if (row[C.lv]) stats.push(['Lv', row[C.lv]]);
    var sub = data.subs[row[C.sub]];
    var loc = (row[C.loc] || []).map(function (i) { return data.locs[i]; }).join(' / ');
    return '<li class="db-row"><button type="button" class="db-entry" data-open="' + row[C.id] + '">' +
      '<span class="db-name">' + esc(row[C.name]) + '</span>' +
      '<span class="db-tags">' +
        '<span class="badge">' + esc(data.types[row[C.type]]) + '</span>' +
        (sub ? '<span class="db-sub">' + esc(sub) + '</span>' : '') +
        (loc ? '<span class="db-sub">' + esc(loc) + '</span>' : '') +
      '</span>' +
      (stats.length ? '<span class="db-stats mono">' + stats.map(function (s) {
        return '<span>' + s[0] + ' ' + s[1] + '</span>';
      }).join('') + '</span>' : '') +
      (row[C.fx] ? '<span class="db-fx">' + esc(row[C.fx].slice(0, 120)) + '</span>' : '') +
      '</button></li>';
  }

  function mobCard(row, data) {
    var C = data.C;
    var rank = row[C.rank];
    return '<li class="db-row"><button type="button" class="db-entry" data-open="' + row[C.id] + '">' +
      '<span class="db-name">' + esc(row[C.name]) +
        (rank === 1 ? ' <span class="badge rank-ss">MVP</span>' :
         rank === 2 ? ' <span class="badge rank-a">Boss</span>' : '') +
      '</span>' +
      '<span class="db-tags">' +
        '<span class="badge">Lv ' + row[C.lv] + '</span>' +
        '<span class="db-sub">' + esc(data.races[row[C.race]]) + '</span>' +
        '<span class="db-sub">' + esc(data.elements[row[C.element]]) + ' ' + row[C.elv] + '</span>' +
        '<span class="db-sub">' + esc(data.sizes[row[C.size]]) + '</span>' +
      '</span>' +
      '<span class="db-stats mono"><span>HP ' + num(row[C.hp]) + '</span>' +
      '<span>ATK ' + row[C.atk] + '</span><span>DEF ' + row[C.def] + '</span>' +
      '<span>EXP ' + num(row[C.exp]) + '</span></span>' +
      (row[C.drops].length ? '<span class="db-fx">' + row[C.drops].length + ' drops</span>' : '') +
      '</button></li>';
  }

  function paint() {
    var data = state.data[state.tab];
    var slice = state.matched.slice(state.painted, state.painted + CHUNK);
    if (!slice.length) return;
    var render = state.tab === 'items' ? itemCard : mobCard;
    els.list.insertAdjacentHTML('beforeend', slice.map(function (r) {
      return render(r, data);
    }).join(''));
    state.painted += slice.length;

    // After painting a block the sentinel is often still on screen and no
    // second intersection ever fires. Keep going until it is out of reach.
    requestAnimationFrame(function () {
      var box = els.sentinel.getBoundingClientRect();
      if (box.top < window.innerHeight + 600) paint();
    });
  }

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) paint();
    }, { rootMargin: '600px' }).observe(els.sentinel);
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

  function dropSources(itemId) {
    var mobs = state.data.mobs;
    if (!mobs) return null;
    var C = mobs.C, out = [];
    mobs.rows.forEach(function (row) {
      row[C.drops].forEach(function (d) {
        if (d[0] === itemId) out.push({ name: row[C.name], lv: row[C.lv], rate: d[1], mvp: d[2] });
      });
    });
    return out.sort(function (a, b) { return b.rate - a.rate; });
  }

  function openDetail(id) {
    var data = state.data[state.tab];
    var row = findRow(state.tab, id);
    if (!row) return;
    var C = data.C;
    var html;

    if (state.tab === 'items') {
      var rows = [
        ['Type', data.types[row[C.type]]],
        ['Subtype', data.subs[row[C.sub]]],
        ['Slot', (row[C.loc] || []).map(function (i) { return data.locs[i]; }).join(', ')],
        ['Card slots', row[C.slots]],
        ['Attack', row[C.atk]], ['Magic attack', row[C.matk]], ['Defense', row[C.def]],
        ['Required level', row[C.lv]], ['Weight', row[C.weight] / 10],
        ['Refineable', row[C.refine] ? 'Yes' : 'No'],
        ['Usable by', data.jobs[row[C.jobs]]],
        ['Item ID', row[C.id]]
      ].filter(function (r) { return r[1] !== '' && r[1] !== 0 && r[1] != null; });

      html = '<h2>' + esc(row[C.name]) + '</h2>' +
        '<dl class="db-detail-stats">' + rows.map(function (r) {
          return '<div><dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd></div>';
        }).join('') + '</dl>';

      if (row[C.fx]) {
        html += '<h3>Effect</h3><pre class="db-script">' +
          esc(row[C.fx]).split(' | ').join('\n') + '</pre>';
      }

      html += '<h3>Where it drops</h3>';
      var sources = dropSources(row[C.id]);
      if (sources === null) {
        html += '<p class="dim">Loading monster data...</p>';
        load('mobs').then(function () { openDetail(id); });
      } else if (!sources.length) {
        html += '<p class="dim">No monster drops this. It comes from a shop, a quest or an exchange.</p>';
      } else {
        html += '<ul class="db-drops">' + sources.map(function (s) {
          return '<li><span>' + esc(s.name) + '</span><span class="dim">Lv ' + s.lv + '</span>' +
            '<span class="mono">' + rate(s.rate) + '</span>' +
            (s.mvp ? '<span class="badge rank-ss">MVP</span>' : '') + '</li>';
        }).join('') + '</ul>';
      }
    } else {
      var mrows = [
        ['Level', row[C.lv]], ['Health', num(row[C.hp])],
        ['Attack', row[C.atk]], ['Defense', row[C.def]], ['Magic defense', row[C.mdef]],
        ['Base EXP', num(row[C.exp])], ['Job EXP', num(row[C.jexp])],
        ['Race', data.races[row[C.race]]],
        ['Element', data.elements[row[C.element]] + ' ' + row[C.elv]],
        ['Size', data.sizes[row[C.size]]],
        ['Monster ID', row[C.id]]
      ];
      html = '<h2>' + esc(row[C.name]) + '</h2>' +
        '<dl class="db-detail-stats">' + mrows.map(function (r) {
          return '<div><dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd></div>';
        }).join('') + '</dl><h3>Drops</h3>';

      var itemsData = state.data.items;
      if (!row[C.drops].length) {
        html += '<p class="dim">Drops nothing.</p>';
      } else if (!itemsData) {
        html += '<p class="dim">Loading item data...</p>';
        load('items').then(function () { openDetail(id); });
      } else {
        var ic = itemsData.C, byId = {};
        itemsData.rows.forEach(function (r) { byId[r[ic.id]] = r[ic.name]; });
        html += '<ul class="db-drops">' + row[C.drops].map(function (d) {
          return '<li><span>' + esc(byId[d[0]] || ('Item ' + d[0])) + '</span>' +
            '<span class="mono">' + rate(d[1]) + '</span>' +
            (d[2] ? '<span class="badge rank-ss">MVP reward</span>' : '') + '</li>';
        }).join('') + '</ul>';
      }
    }

    els.detailInner.innerHTML =
      '<button type="button" class="icon-btn db-close" data-detail-close aria-label="Close">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">' +
      '<path d="M6 6l12 12M18 6L6 18" stroke-linecap="round"/></svg></button>' + html;
    els.detail.hidden = false;
    els.detail.dataset.open = 'true';
    saveUrl(id);
  }

  function closeDetail() {
    els.detail.dataset.open = 'false';
    els.detail.hidden = true;
    saveUrl();
  }

  /* ---- url state -------------------------------------------------------- */

  function saveUrl(openId) {
    var p = new URLSearchParams();
    if (state.tab !== 'items') p.set('tab', state.tab);
    if (state.q) p.set('q', els.q.value);
    if (state.sort !== 'name') p.set('sort', state.sort);
    if (openId) p.set('id', openId);
    var qs = p.toString();
    history.replaceState(null, '', qs ? '?' + qs : location.pathname);
  }

  function readUrl() {
    var p = new URLSearchParams(location.search);
    if (p.get('tab') === 'mobs') state.tab = 'mobs';
    if (p.get('q')) { state.q = fold(p.get('q')); els.q.value = p.get('q'); }
    if (p.get('sort')) state.sort = p.get('sort');
    return p.get('id') ? +p.get('id') : 0;
  }

  /* ---- events ----------------------------------------------------------- */

  var timer;
  els.q.addEventListener('input', function () {
    clearTimeout(timer);
    timer = setTimeout(function () {
      state.q = fold(els.q.value.trim());
      apply();
    }, 120);
  });

  els.sort.addEventListener('change', function () {
    state.sort = els.sort.value;
    apply();
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
      apply();
    } else if (box.dataset.range) {
      var cur = state.facets[box.dataset.range] || {};
      cur[box.dataset.edge] = box.value === '' ? null : +box.value;
      state.facets[box.dataset.range] =
        (cur.min == null && cur.max == null) ? null : cur;
      apply();
    }
  });

  els.facets.addEventListener('click', function (e) {
    var more = e.target.closest('[data-more]');
    if (!more) return;
    var body = more.parentNode;
    body.classList.add('is-expanded');
    more.remove();
  });

  document.getElementById('db-reset').addEventListener('click', function () {
    state.facets = {};
    state.q = '';
    els.q.value = '';
    renderFacets();
    apply();
  });

  els.list.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-open]');
    if (btn) openDetail(+btn.dataset.open);
  });

  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-detail-close]')) closeDetail();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && els.detail.dataset.open === 'true') closeDetail();
  });

  root.querySelectorAll('[data-db-tab]').forEach(function (tab) {
    tab.addEventListener('click', function () {
      var name = tab.dataset.dbTab;
      if (name === state.tab) return;
      state.tab = name;
      state.facets = {};
      state.sort = 'name';
      // The query has to go with the facets. Leaving "jellopy" in the box
      // while switching to monsters shows an empty list with no visible cause.
      state.q = '';
      els.q.value = '';
      closeDetail();
      root.querySelectorAll('[data-db-tab]').forEach(function (t) {
        t.setAttribute('aria-selected', String(t.dataset.dbTab === name));
      });
      els.count.textContent = 'Loading...';
      load(name).then(function () { renderFacets(); apply(); });
    });
  });

  /* ---- boot ------------------------------------------------------------- */

  var openId = readUrl();
  root.querySelectorAll('[data-db-tab]').forEach(function (t) {
    t.setAttribute('aria-selected', String(t.dataset.dbTab === state.tab));
  });
  load(state.tab).then(function () {
    renderFacets();
    apply();
    if (openId) openDetail(openId);
  });
})();
