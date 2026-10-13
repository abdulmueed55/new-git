/* ===== FreelanceFigures — shared site script ===== */
(function () {
  'use strict';

  /* ---------- AdSense ----------
     Apna AdSense publisher ID yahan paste karein, e.g. 'ca-pub-1234567890123456'
     Jab tak ye khali hai, ad slots hide rahenge (approval se pehle khali boxes nahi dikhenge). */
  var ADSENSE_CLIENT = '';

  function initAds() {
    var slots = document.querySelectorAll('.ad-slot');
    if (!ADSENSE_CLIENT) {
      for (var i = 0; i < slots.length; i++) slots[i].setAttribute('data-empty', '1');
      return;
    }
    var s = document.createElement('script');
    s.async = true;
    s.crossOrigin = 'anonymous';
    s.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + ADSENSE_CLIENT;
    document.head.appendChild(s);

    for (var j = 0; j < slots.length; j++) {
      var slot = slots[j];
      var id = slot.getAttribute('data-slot') || '';
      var ins = document.createElement('ins');
      ins.className = 'adsbygoogle';
      ins.style.display = 'block';
      ins.setAttribute('data-ad-client', ADSENSE_CLIENT);
      if (id) ins.setAttribute('data-ad-slot', id);
      ins.setAttribute('data-ad-format', slot.getAttribute('data-format') || 'auto');
      ins.setAttribute('data-full-width-responsive', 'true');
      slot.appendChild(ins);
      try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) { /* blocked */ }
    }
  }

  /* ---------- theme ---------- */
  function initTheme() {
    var btn = document.querySelector('.theme-btn');
    if (!btn) return;
    function paint() {
      var explicit = document.documentElement.getAttribute('data-theme');
      var dark = explicit
        ? explicit === 'dark'
        : window.matchMedia('(prefers-color-scheme: dark)').matches;
      btn.textContent = dark ? '☀' : '☾';
      btn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    }
    btn.addEventListener('click', function () {
      var explicit = document.documentElement.getAttribute('data-theme');
      var dark = explicit
        ? explicit === 'dark'
        : window.matchMedia('(prefers-color-scheme: dark)').matches;
      var next = dark ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem('ff-theme', next); } catch (e) { /* private mode */ }
      paint();
    });
    paint();
  }

  /* ---------- mobile menu ---------- */
  function initMenu() {
    var btn = document.querySelector('.menu-btn');
    var nav = document.querySelector('.nav');
    if (!btn || !nav) return;
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------- shared helpers (used by calculator pages) ---------- */
  var FF = {
    /** Read a numeric input; returns fallback when blank or not a number. */
    num: function (id, fallback) {
      var el = document.getElementById(id);
      if (!el) return fallback || 0;
      var v = parseFloat(String(el.value).replace(/,/g, '').trim());
      return isFinite(v) ? v : (fallback || 0);
    },
    val: function (id) {
      var el = document.getElementById(id);
      return el ? el.value : '';
    },
    money: function (n, currency) {
      var cur = currency || FF.currency();
      try {
        return new Intl.NumberFormat('en-US', {
          style: 'currency', currency: cur,
          minimumFractionDigits: 2, maximumFractionDigits: 2
        }).format(n);
      } catch (e) {
        return cur + ' ' + n.toFixed(2);
      }
    },
    money0: function (n, currency) {
      var cur = currency || FF.currency();
      try {
        return new Intl.NumberFormat('en-US', {
          style: 'currency', currency: cur,
          minimumFractionDigits: 0, maximumFractionDigits: 0
        }).format(n);
      } catch (e) {
        return cur + ' ' + Math.round(n);
      }
    },
    currency: function () {
      var el = document.getElementById('currency');
      return el ? el.value : 'USD';
    },
    /** Recalculate on any input change inside a form. */
    live: function (formId, fn) {
      var form = document.getElementById(formId);
      if (!form) return;
      form.addEventListener('input', fn);
      form.addEventListener('change', fn);
      form.addEventListener('submit', function (e) { e.preventDefault(); fn(); });
      fn();
    },
    show: function (id) {
      var el = document.getElementById(id);
      if (el) el.hidden = false;
    },
    set: function (id, text) {
      var el = document.getElementById(id);
      if (el) el.textContent = text;
    },
    /** Copy the rendered result block to the clipboard as plain text. */
    initCopy: function (btnId, resultId) {
      var btn = document.getElementById(btnId);
      var res = document.getElementById(resultId);
      if (!btn || !res) return;
      btn.addEventListener('click', function () {
        var text = res.innerText.replace(/\n{3,}/g, '\n\n').trim();
        var done = function () {
          var old = btn.textContent;
          btn.textContent = 'Copied';
          setTimeout(function () { btn.textContent = old; }, 1600);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(text).then(done, function () {});
        } else {
          var ta = document.createElement('textarea');
          ta.value = text;
          document.body.appendChild(ta);
          ta.select();
          try { document.execCommand('copy'); done(); } catch (e) { /* ignore */ }
          document.body.removeChild(ta);
        }
      });
    },
    /** Reset a form back to its HTML defaults and recalculate. */
    initReset: function (btnId, formId, fn) {
      var btn = document.getElementById(btnId);
      var form = document.getElementById(formId);
      if (!btn || !form) return;
      btn.addEventListener('click', function () {
        form.reset();
        if (fn) fn();
      });
    }
  };
  window.FF = FF;

  function boot() {
    initTheme();
    initMenu();
    initAds();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
