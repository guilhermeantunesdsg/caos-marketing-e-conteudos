/* CAOS · idiomas (PT / EN / ES). O português é o texto do próprio HTML; EN e ES vêm de dicionários. */
(function () {
  'use strict';
  var d = document, L = window.__LANG || 'pt', D = window.__I18N || null;
  var collect = /[?&]collect=1/.test(location.search), found = {};
  var norm = function (s) { return s.replace(/\s+/g, ' ').trim(); };
  var own = Object.prototype.hasOwnProperty;

  function look(s) {
    var k = norm(s); if (!k || !/[A-Za-zÀ-ÿ]/.test(k)) return null;
    if (collect) { found[k] = 1; return null; }
    return D && own.call(D, k) ? D[k] : null;
  }
  // traduz um texto qualquer (usado também pelo app.js)
  window.t = function (s) { var r = look(String(s == null ? '' : s)); return r == null ? s : r; };

  var INLINE = { SPAN: 1, B: 1, STRONG: 1, EM: 1, I: 1, BR: 1, SMALL: 1, MARK: 1, SUP: 1, SUB: 1, U: 1, WBR: 1, A: 1, LABEL: 0 };
  var SKIP = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, SVG: 1, TEXTAREA: 1, SELECT: 0 };

  function allInline(el) {
    for (var c = el.firstElementChild; c; c = c.nextElementSibling) {
      if (!INLINE[c.tagName] || c.hasAttribute('data-i18n-skip')) return false;
      if (!allInline(c)) return false;
    }
    return true;
  }
  function hasText(el) {
    for (var n = el.firstChild; n; n = n.nextSibling) if (n.nodeType === 3 && /\S/.test(n.nodeValue)) return true;
    return false;
  }
  function wrap(orig, tr) { var m = orig.match(/^(\s*)[\s\S]*?(\s*)$/); return m[1] + tr + m[2]; }

  function walk(el) {
    if (SKIP[el.tagName] || el.getAttribute('translate') === 'no') return;
    if (hasText(el) && allInline(el)) {
      var h = el.innerHTML, r = look(h);
      if (r != null) el.innerHTML = wrap(h, r);
      return;
    }
    for (var n = el.firstChild; n; n = n.nextSibling) {
      if (n.nodeType === 1) walk(n);
      else if (n.nodeType === 3 && /\S/.test(n.nodeValue)) { var t = look(n.nodeValue); if (t != null) n.nodeValue = wrap(n.nodeValue, t); }
    }
  }

  var ATTRS = ['placeholder', 'aria-label', 'title', 'alt', 'data-cursor'];
  function attrs() {
    Array.prototype.forEach.call(d.querySelectorAll('[placeholder],[aria-label],[title],[alt],[data-cursor]'), function (el) {
      ATTRS.forEach(function (a) { if (el.hasAttribute(a)) { var r = look(el.getAttribute(a)); if (r != null) el.setAttribute(a, r); } });
    });
    Array.prototype.forEach.call(d.querySelectorAll('input[type=checkbox][value],option[value]'), function (el) {
      var r = look(el.getAttribute('value')); if (r != null) el.setAttribute('value', r);
    });
    Array.prototype.forEach.call(d.querySelectorAll('meta[name=description],meta[property="og:title"],meta[property="og:description"]'), function (m) {
      var r = look(m.getAttribute('content')); if (r != null) m.setAttribute('content', r);
    });
    var tt = look(d.title); if (tt != null) d.title = tt;
    // mensagens pré-preenchidas do WhatsApp
    Array.prototype.forEach.call(d.querySelectorAll('a[href*="wa.me"]'), function (a) {
      var h = a.getAttribute('href'), i = h.indexOf('?text='); if (i < 0) return;
      var msg; try { msg = decodeURIComponent(h.slice(i + 6)); } catch (e) { return; }
      var r = look(msg); if (r != null) a.setAttribute('href', h.slice(0, i) + '?text=' + encodeURIComponent(r));
    });
  }

  function run() {
    if (!collect && !D) return;
    walk(d.body); attrs();
    if (collect) {
      var w = {}; try { w = JSON.parse(d.getElementById('works-data').textContent); } catch (e) {}
      Object.keys(w).forEach(function (id) { ['titulo', 'cliente', 'servico', 'descricao'].forEach(function (k) { if (w[id][k]) look(w[id][k]); }); });
      var pre = d.createElement('pre'); pre.id = '__keys'; pre.textContent = JSON.stringify(Object.keys(found)); d.body.appendChild(pre);
    }
  }
  run();

  // bandeiras
  function setLang(l) {
    try { localStorage.setItem('caosLang', l); } catch (e) {}
    location.reload();
  }
  Array.prototype.forEach.call(d.querySelectorAll('[data-l]'), function (b) {
    var on = b.getAttribute('data-l') === L;
    b.classList.toggle('is-on', on); b.setAttribute('aria-pressed', on ? 'true' : 'false');
    b.addEventListener('click', function () { if (b.getAttribute('data-l') !== L) setLang(b.getAttribute('data-l')); });
  });
})();
