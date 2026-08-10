/* Return to Morroc: Refuge - shared behaviour.
   Deliberately small and dependency free. Everything here is an enhancement:
   the pages are fully readable with this file blocked. */
(function () {
  'use strict';

  document.documentElement.classList.add('js');

  /* ---- theme -------------------------------------------------------------
     The initial value is set by the inline script in <head>, before paint.
     This only handles the toggle and persistence. */
  var root = document.documentElement;

  function setTheme(t) {
    root.dataset.theme = t;
    try { localStorage.setItem('rtmr-theme', t); } catch (e) {}
    var meta = document.querySelector('meta[name="theme-color"]:not([media])');
    if (meta) meta.content = t === 'light' ? '#f2f0f5' : '#06040a';
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      b.setAttribute('aria-label', t === 'light' ? 'Switch to dark theme' : 'Switch to light theme');
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-theme-toggle]');
    if (!btn) return;
    setTheme(root.dataset.theme === 'light' ? 'dark' : 'light');
  });

  setTheme(root.dataset.theme || 'dark');

  /* ---- mobile drawer ----------------------------------------------------- */
  var drawer = document.getElementById('drawer');

  function closeDrawer() {
    if (!drawer) return;
    drawer.dataset.open = 'false';
    document.body.classList.remove('no-scroll');
    var t = document.querySelector('[data-drawer-open]');
    if (t) { t.setAttribute('aria-expanded', 'false'); t.focus(); }
  }

  function openDrawer() {
    if (!drawer) return;
    drawer.dataset.open = 'true';
    document.body.classList.add('no-scroll');
    var t = document.querySelector('[data-drawer-open]');
    if (t) t.setAttribute('aria-expanded', 'true');
    var first = drawer.querySelector('a, button');
    if (first) first.focus();
  }

  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-drawer-open]')) { openDrawer(); return; }
    if (e.target.closest('[data-drawer-close]')) { closeDrawer(); return; }
    if (drawer && drawer.dataset.open === 'true' && e.target.closest('#drawer a')) closeDrawer();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && drawer && drawer.dataset.open === 'true') closeDrawer();
  });

  /* ---- header menus ------------------------------------------------------
     Hover and :focus-within already open a group in CSS, so this file only
     adds what those two cannot do: a tap on a touch screen, and a way out. */
  function closeMenus(except) {
    document.querySelectorAll('.nav-group[data-open="true"]').forEach(function (g) {
      if (g === except) return;
      g.dataset.open = 'false';
      var b = g.querySelector('[data-nav-group]');
      if (b) b.setAttribute('aria-expanded', 'false');
    });
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-nav-group]');
    if (!btn) { closeMenus(null); return; }
    var group = btn.parentNode;
    var open = group.dataset.open !== 'true';
    closeMenus(group);
    group.dataset.open = String(open);
    btn.setAttribute('aria-expanded', String(open));
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    var open = document.querySelector('.nav-group[data-open="true"]');
    if (!open) return;
    closeMenus(null);
    var b = open.querySelector('[data-nav-group]');
    if (b) b.focus();
  });

  /* ---- scroll reveal -----------------------------------------------------
     Without IntersectionObserver nothing is hidden in the first place, so the
     absence of this feature costs nothing. */
  var targets = document.querySelectorAll('.reveal');
  if (targets.length && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.classList.add('is-in');
        io.unobserve(en.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    targets.forEach(function (el) { io.observe(el); });
    // Safety net. A background tab, a print job or a paused compositor can
    // stop the observer from ever firing, and hidden content is worse than
    // unanimated content.
    setTimeout(function () {
      targets.forEach(function (el) { el.classList.add('is-in'); });
    }, 2500);
  } else {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---- table / list filter ----------------------------------------------
     Used by the dungeon table and the job change lists. Any input carrying
     data-filter="<id>" filters the rows of that container by text content.
     Accents are stripped on both sides so "distorcao" finds "distorção". */
  function fold(s) {
    return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  }

  document.querySelectorAll('[data-filter]').forEach(function (input) {
    var scope = document.getElementById(input.getAttribute('data-filter'));
    if (!scope) return;
    var rows = Array.prototype.slice.call(scope.querySelectorAll('[data-row]'));
    var count = document.getElementById(input.getAttribute('data-filter-count') || '');
    var empty = document.getElementById(input.getAttribute('data-filter-empty') || '');
    // A filtered list that leaves five headings with nothing under them reads
    // as broken, so a group with no surviving rows goes too.
    var groups = Array.prototype.slice.call(scope.querySelectorAll('[data-filter-group]'));

    function apply() {
      var q = fold(input.value.trim());
      var shown = 0;
      rows.forEach(function (r) {
        var hit = !q || fold(r.textContent).indexOf(q) !== -1;
        r.hidden = !hit;
        if (hit) shown++;
      });
      groups.forEach(function (g) {
        g.hidden = !g.querySelector('[data-row]:not([hidden])');
      });
      if (count) count.textContent = shown + ' / ' + rows.length;
      if (empty) empty.hidden = shown > 0;
    }

    input.addEventListener('input', apply);
    apply();
  });

  /* ---- copy buttons ------------------------------------------------------ */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-copy]');
    if (!btn) return;
    var text = btn.getAttribute('data-copy');
    var done = function () {
      var old = btn.textContent;
      btn.textContent = 'Copied';
      setTimeout(function () { btn.textContent = old; }, 1600);
    };
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(done, done);
    } else {
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); } catch (err) {}
      document.body.removeChild(ta);
      done();
    }
  });
})();
