/* Site search.

   The whole UI is built at runtime, so none of the 55 pages carries markup
   for it. The index is fetched on first open and warmed on pointerenter of
   the button, which is what makes the first open feel instant.

   Ranking is where the actual work is. Two rules matter more than the rest:
   a page about "fire" has to beat the hundred items named "fire", and no
   single group may bury every other group. */
(function () {
  'use strict';

  var INDEX_URL = (window.RTMR_PREFIX || '') + 'assets/data/search.json';
  var PREFIX = window.RTMR_PREFIX || '';

  var index = null;
  var loading = null;
  var overlay = null;
  var input = null;
  var list = null;
  var cursor = -1;
  var results = [];
  var opener = null;

  // Weight by group, then a hard cap per group. Without the cap, 423 skills
  // bury the one page that actually answers the question.
  var GROUP_WEIGHT = { page: 60, section: 50, class: 40, dungeon: 30, skill: 20 };
  var GROUP_CAP = 7;

  function fold(s) {
    return String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  function load() {
    if (index) return Promise.resolve(index);
    if (loading) return loading;
    loading = fetch(INDEX_URL)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        index = data.rows.map(function (r) {
          return {
            title: r[0], sub: r[1], url: r[2],
            group: data.groups[r[3]], extra: r[4] || '',
            fTitle: fold(r[0]), fSub: fold(r[1]), fExtra: fold(r[4] || '')
          };
        });
        return index;
      })
      .catch(function () { index = []; return index; });
    return loading;
  }

  function score(row, q, words) {
    var t = row.fTitle;
    var s = 0;
    if (t === q) s = 1000;
    else if (t.indexOf(q) === 0) s = 700;
    else if (new RegExp('\\b' + q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).test(t)) s = 520;
    else if (t.indexOf(q) !== -1) s = 340;
    else if (row.fSub.indexOf(q) !== -1) s = 150;
    else if (row.fExtra.indexOf(q) !== -1) s = 90;

    if (!s && words.length > 1) {
      var hay = t + ' ' + row.fSub + ' ' + row.fExtra;
      var all = words.every(function (w) { return hay.indexOf(w) !== -1; });
      if (all) s = 110;
    }
    if (!s) return 0;
    return s + (GROUP_WEIGHT[row.group] || 0) - row.title.length / 6;
  }

  function search(query) {
    var q = fold(query.trim());
    if (!q || !index) return [];
    var words = q.split(/\s+/).filter(Boolean);
    var scored = [];
    for (var i = 0; i < index.length; i++) {
      var s = score(index[i], q, words);
      if (s > 0) scored.push({ row: index[i], s: s });
    }
    scored.sort(function (a, b) { return b.s - a.s; });

    var perGroup = {};
    var out = [];
    for (var j = 0; j < scored.length && out.length < 24; j++) {
      var g = scored[j].row.group;
      perGroup[g] = (perGroup[g] || 0) + 1;
      if (perGroup[g] > GROUP_CAP) continue;
      out.push(scored[j].row);
    }
    return out;
  }

  function build() {
    if (overlay) return;
    overlay = document.createElement('div');
    overlay.className = 'search-overlay';
    overlay.dataset.open = 'false';
    overlay.innerHTML =
      '<div class="search-panel" role="dialog" aria-modal="true" aria-label="Search this site">' +
      '<input type="search" autocomplete="off" spellcheck="false" role="combobox"' +
      ' aria-expanded="true" aria-controls="search-results" aria-autocomplete="list"' +
      ' placeholder="Search classes, skills, dungeons, guides..."' +
      ' data-i18n-attr="placeholder:search.placeholder">' +
      '<ul class="search-results" id="search-results" role="listbox"></ul>' +
      '<p class="search-foot"><span>Enter to open</span><span>Arrows to move</span>' +
      '<span>Esc to close</span></p></div>';
    document.body.appendChild(overlay);
    input = overlay.querySelector('input');
    list = overlay.querySelector('.search-results');

    input.addEventListener('input', function () { render(search(input.value)); });
    overlay.addEventListener('click', function (e) {
      if (e.target === overlay) close();
    });
  }

  function render(rows) {
    results = rows;
    cursor = rows.length ? 0 : -1;
    if (!input.value.trim()) {
      list.innerHTML = '<li class="search-empty" data-i18n="search.hint">' +
        'Type to search 500+ classes, skills, dungeons and sections.</li>';
      return;
    }
    if (!rows.length) {
      list.innerHTML = '<li class="search-empty" data-i18n="search.none">Nothing found.</li>';
      return;
    }
    list.innerHTML = rows.map(function (r, i) {
      return '<li role="option" id="sr-' + i + '" aria-selected="' + (i === 0) + '">' +
        '<a href="' + PREFIX + r.url + '">' +
        '<span class="r-title">' + escape(r.title) + '</span>' +
        '<span class="r-group">' + r.group + '</span>' +
        (r.sub ? '<span class="r-sub">' + escape(r.sub) + '</span>' : '') +
        '</a></li>';
    }).join('');
    input.setAttribute('aria-activedescendant', 'sr-0');
  }

  function escape(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function move(delta) {
    if (!results.length) return;
    var items = list.querySelectorAll('li');
    items[cursor] && items[cursor].setAttribute('aria-selected', 'false');
    cursor = (cursor + delta + results.length) % results.length;
    items[cursor].setAttribute('aria-selected', 'true');
    input.setAttribute('aria-activedescendant', 'sr-' + cursor);
    items[cursor].scrollIntoView({ block: 'nearest' });
  }

  function open() {
    build();
    opener = document.activeElement;
    load().then(function () { render(search(input.value)); });
    overlay.dataset.open = 'true';
    document.body.classList.add('no-scroll');
    input.value = '';
    render([]);
    input.focus();
  }

  function close() {
    if (!overlay) return;
    overlay.dataset.open = 'false';
    document.body.classList.remove('no-scroll');
    if (opener && opener.focus) opener.focus();
  }

  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-search-open]')) { e.preventDefault(); open(); }
  });

  document.addEventListener('pointerenter', function (e) {
    if (e.target.closest && e.target.closest('[data-search-open]')) load();
  }, true);

  document.addEventListener('keydown', function (e) {
    var el = document.activeElement;
    var typing = el && (el.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName));
    var isOpen = overlay && overlay.dataset.open === 'true';

    if ((e.key === '/' && !typing) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) {
      e.preventDefault();
      isOpen ? close() : open();
      return;
    }
    if (!isOpen) return;
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
    else if (e.key === 'Enter' && cursor >= 0) {
      var a = list.querySelectorAll('li')[cursor].querySelector('a');
      if (a) { e.preventDefault(); window.location.href = a.href; }
    }
  });
})();
