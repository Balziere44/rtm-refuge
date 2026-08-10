/* Runtime translation.

   English lives in the HTML. There is no en.js, because the text a crawler
   indexes and the text a visitor without JavaScript reads has to be the real
   markup, not a shell that gets filled in later.

   Other languages are small tables loaded on demand. The contract in the
   markup is two attributes and nothing else:

     <span data-i18n="nav.home">Home</span>
     <input data-i18n-attr="placeholder:search.placeholder,title:search.title">

   A missing key falls back to the English snapshot taken at boot, so a
   half-finished translation degrades to English word by word instead of
   printing "undefined". */
(function () {
  'use strict';

  var LANGS = [
    { code: 'en', label: 'English', native: 'English' },
    { code: 'pt', label: 'Portuguese', native: 'Portugues (BR)' }
  ];

  var STORE = 'rtmr-lang';
  var tables = {};      // code -> table
  var snapshot = null;  // element -> original English
  var attrSnap = null;
  var current = 'en';

  window.RTMR_I18N_REGISTER = function (code, table) {
    tables[code] = table;
    if (code === current) apply(code);
  };

  function takeSnapshot() {
    if (snapshot) return;
    snapshot = new Map();
    attrSnap = new Map();
    document.querySelectorAll('[data-i18n]').forEach(function (el) {
      snapshot.set(el, el.innerHTML);
    });
    document.querySelectorAll('[data-i18n-attr]').forEach(function (el) {
      var store = {};
      el.getAttribute('data-i18n-attr').split(',').forEach(function (pair) {
        var attr = pair.split(':')[0].trim();
        store[attr] = el.getAttribute(attr);
      });
      attrSnap.set(el, store);
    });
  }

  function apply(code) {
    takeSnapshot();
    var t = tables[code] || {};
    current = code;

    snapshot.forEach(function (english, el) {
      var key = el.getAttribute('data-i18n');
      el.innerHTML = (code !== 'en' && t[key]) ? t[key] : english;
    });

    attrSnap.forEach(function (store, el) {
      el.getAttribute('data-i18n-attr').split(',').forEach(function (pair) {
        var bits = pair.split(':');
        var attr = bits[0].trim();
        var key = (bits[1] || '').trim();
        var value = (code !== 'en' && t[key]) ? t[key] : store[attr];
        if (value != null) el.setAttribute(attr, value);
      });
    });

    document.documentElement.lang = code === 'pt' ? 'pt-BR' : code;
    window.RTMR_I18N_TABLE = code === 'en' ? {} : t;

    document.querySelectorAll('[data-lang-pick]').forEach(function (b) {
      b.setAttribute('aria-current', String(b.getAttribute('data-lang-pick') === code));
    });
    var label = document.querySelector('[data-lang-label]');
    if (label) label.textContent = code.toUpperCase();

    document.dispatchEvent(new CustomEvent('rtmr:lang', { detail: { lang: code } }));
  }

  function load(code) {
    if (code === 'en' || tables[code]) { apply(code); return; }
    var s = document.createElement('script');
    s.src = (window.RTMR_PREFIX || '') + 'assets/i18n/' + code + '.js';
    // A locale that fails to load leaves the English snapshot in place, which
    // is a worse experience than a translation and a much better one than an
    // empty page.
    s.onerror = function () { apply('en'); };
    document.head.appendChild(s);
    apply(code);
  }

  function pick(code) {
    try { localStorage.setItem(STORE, code); } catch (e) {}
    load(code);
  }

  function initial() {
    try {
      var saved = localStorage.getItem(STORE);
      if (saved) return saved;
    } catch (e) {}
    var known = LANGS.map(function (l) { return l.code; });
    var wanted = navigator.languages || [navigator.language || 'en'];
    for (var i = 0; i < wanted.length; i++) {
      var base = String(wanted[i]).slice(0, 2).toLowerCase();
      if (known.indexOf(base) !== -1) return base;
    }
    return 'en';
  }

  document.addEventListener('click', function (e) {
    var toggle = e.target.closest('[data-lang-open]');
    var wrap = document.querySelector('.lang');
    if (toggle) {
      var open = wrap.dataset.open !== 'true';
      wrap.dataset.open = String(open);
      toggle.setAttribute('aria-expanded', String(open));
      return;
    }
    var choice = e.target.closest('[data-lang-pick]');
    if (choice) {
      pick(choice.getAttribute('data-lang-pick'));
      wrap.dataset.open = 'false';
      wrap.querySelector('[data-lang-open]').setAttribute('aria-expanded', 'false');
      return;
    }
    if (wrap && !e.target.closest('.lang')) wrap.dataset.open = 'false';
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var wrap = document.querySelector('.lang');
    if (wrap && wrap.dataset.open === 'true') {
      wrap.dataset.open = 'false';
      wrap.querySelector('[data-lang-open]').focus();
    }
  });

  load(initial());
})();
