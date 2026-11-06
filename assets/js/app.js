/* CAOS · comportamento do site (otimizado) */
(function () {
  'use strict';
  var d = document, w = window, root = d.documentElement;
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var reduce = w.matchMedia && w.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = w.matchMedia && w.matchMedia('(pointer: fine)').matches;
  var clamp = function (v, a, b) { return Math.max(a, Math.min(b, v)); };
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var hasIO = 'IntersectionObserver' in w;
  var WA_NUM = '5538998280485';
  var MSG = {
    geral: 'Olá, CAOS! Vim pelo site e gostaria de conversar sobre um projeto.',
    eventos: 'Olá, CAOS! Vim pelo site e gostaria de um orçamento de audiovisual para o meu evento.',
    casamentos: 'Olá, CAOS! Vim pelo site e gostaria de consultar a disponibilidade da minha data de casamento.',
    marketing: 'Olá, CAOS! Vim pelo site e gostaria de uma proposta de marketing para a minha empresa.'
  };
  var lenis = null;
  function scrollLock(on) { d.body.style.overflow = on ? 'hidden' : ''; if (lenis) on ? lenis.stop() : lenis.start(); }

  /* ---------- métricas (só carrega com consentimento) ---------- */
  w.dataLayer = w.dataLayer || [];
  function track(name, params) {
    try {
      if (typeof w.gtag === 'function') w.gtag('event', name, params || {});
      else w.dataLayer.push(Object.assign({ event: name }, params || {}));
      if (typeof w.fbq === 'function' && /^(wa_|form_)/.test(name)) w.fbq('track', 'Lead', { fonte: name });
    } catch (e) {}
  }
  d.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('[data-track]');
    if (a && a.tagName !== 'FORM') track(a.getAttribute('data-track'), { destino: a.getAttribute('href') || '', pagina: location.pathname });
  });
  (function consent() {
    var cfg = w.__CAOS_ANALYTICS; if (!cfg || (!cfg.ga4 && !cfg.pixel)) return;
    var KEY = 'caos-consent';
    var get = function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
    var set = function (v) { try { localStorage.setItem(KEY, v); } catch (e) {} };
    function load() {
      if (cfg.ga4) {
        var s = d.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + cfg.ga4; d.head.appendChild(s);
        w.gtag = function () { w.dataLayer.push(arguments); }; w.gtag('js', new Date()); w.gtag('config', cfg.ga4);
      }
      if (cfg.pixel) {
        !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(w, d, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
        w.fbq('init', cfg.pixel); w.fbq('track', 'PageView');
      }
    }
    var c = get(); if (c === 'sim') return load(); if (c === 'nao') return;
    var bar = d.createElement('div'); bar.className = 'consent'; bar.setAttribute('role', 'dialog');
    bar.innerHTML = '<p>Usamos cookies de métricas para entender como o site é usado. Você pode recusar.</p><div><button data-c="sim">Aceitar</button><button data-c="nao">Recusar</button></div>';
    d.body.appendChild(bar);
    bar.addEventListener('click', function (e) { var b = e.target.closest('[data-c]'); if (!b) return; set(b.dataset.c); bar.remove(); if (b.dataset.c === 'sim') load(); });
  })();

  /* ---------- rolagem suave (Lenis) ---------- */
  if (!reduce && typeof w.Lenis === 'function') {
    lenis = new w.Lenis({ lerp: .09, wheelMultiplier: .95, smoothWheel: true });
    (function raf(t) { lenis.raf(t); requestAnimationFrame(raf); })(performance.now());
    root.classList.add('lenis');
  }

  /* ---------- transição de página ---------- */
  function entered() { root.classList.add('is-entered'); setTimeout(function () { root.classList.remove('is-entering', 'is-entered'); }, 900); try { sessionStorage.removeItem('caosNav'); } catch (e) {} }
  if (root.classList.contains('is-entering')) requestAnimationFrame(function () { requestAnimationFrame(entered); });
  w.addEventListener('pageshow', function (e) { if (e.persisted) root.classList.remove('is-leaving'); });
  d.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    if (a.target && a.target !== '_self') return;
    var u; try { u = new URL(a.href, location.href); } catch (er) { return; }
    if (u.origin !== location.origin) return;
    if (u.pathname === location.pathname && u.search === location.search) return;
    if (reduce) return;
    e.preventDefault();
    try { sessionStorage.setItem('caosNav', '1'); } catch (er) {}
    root.classList.add('is-leaving'); closeMenu();
    setTimeout(function () { location.href = u.href; }, 720);
  });

  /* ---------- menu ---------- */
  var burger = $('[data-burger]'), menu = $('[data-menu]');
  function closeMenu() { if (!menu || !menu.classList.contains('is-open')) return; menu.classList.remove('is-open'); menu.setAttribute('aria-hidden', 'true'); burger.setAttribute('aria-expanded', 'false'); scrollLock(false); }
  if (burger) burger.addEventListener('click', function () {
    var open = !menu.classList.contains('is-open');
    menu.classList.toggle('is-open', open); menu.setAttribute('aria-hidden', String(!open)); burger.setAttribute('aria-expanded', String(open)); scrollLock(open);
  });
  d.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });
  w.addEventListener('resize', function () { if (w.innerWidth > 1180) closeMenu(); });

  /* ---------- cronômetro (REC) ---------- */
  var tcs = $$('[data-timecode]'), t0 = performance.now();
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  if (tcs.length && !reduce) setInterval(function () {
    if (d.hidden) return;
    var ms = performance.now() - t0, s = Math.floor(ms / 1000), f = Math.floor((ms % 1000) / 41.666);
    var txt = pad(Math.floor(s / 3600)) + ':' + pad(Math.floor(s / 60) % 60) + ':' + pad(s % 60) + ':' + pad(f);
    for (var i = 0; i < tcs.length; i++) tcs[i].textContent = txt;
  }, 83);

  /* ---------- cursor (só roda enquanto o mouse se mexe) ---------- */
  (function cursor() {
    var c = $('.cursor'); if (!c || !fine) return;
    var lab = $('em', c), x = -100, y = -100, tx = x, ty = y, on = false, run = false;
    function loop() {
      x = lerp(x, tx, .24); y = lerp(y, ty, .24);
      c.style.transform = 'translate3d(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px,0)';
      if (Math.abs(tx - x) + Math.abs(ty - y) > .3) requestAnimationFrame(loop); else run = false;
    }
    w.addEventListener('pointermove', function (e) { tx = e.clientX; ty = e.clientY; if (!on) { on = true; x = tx; y = ty; } if (!run) { run = true; requestAnimationFrame(loop); } }, { passive: true });
    w.addEventListener('pointerdown', function () { c.classList.add('is-down'); });
    w.addEventListener('pointerup', function () { c.classList.remove('is-down'); });
    d.addEventListener('pointerover', function (e) {
      var t = e.target.closest && e.target.closest('[data-cursor]');
      if (t) { lab.textContent = t.getAttribute('data-cursor'); c.classList.add('is-link'); } else c.classList.remove('is-link');
    }, { passive: true });
  })();

  /* ---------- quebra de texto em palavras ---------- */
  function splitWords(el) {
    var n = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (ch) {
        if (ch.nodeType === 3) {
          var frag = d.createDocumentFragment();
          ch.textContent.split(/(\s+)/).forEach(function (tok) {
            if (!tok) return;
            if (/^\s+$/.test(tok)) { frag.appendChild(d.createTextNode(' ')); return; }
            var m = d.createElement('span'); m.className = 'wm';
            var i = d.createElement('span'); i.className = 'wi'; i.style.setProperty('--i', n++); i.textContent = tok;
            m.appendChild(i); frag.appendChild(m);
          });
          node.replaceChild(frag, ch);
        } else if (ch.nodeType === 1) walk(ch);
      });
    })(el);
  }
  $$('[data-split]').forEach(function (el) { el.setAttribute('aria-label', el.textContent.trim()); splitWords(el); });

  /* ---------- revelações ---------- */
  var io = hasIO ? new IntersectionObserver(function (es) {
    var k = 0;
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.style.setProperty('--d', (k++ * .07) + 's'); e.target.classList.add('is-in'); io.unobserve(e.target);
    });
  }, { threshold: .1, rootMargin: '0px 0px -5% 0px' }) : null;
  $$('[data-reveal],[data-split],[data-fade]').forEach(function (el) { if (io) io.observe(el); else el.classList.add('is-in'); });
  setTimeout(function () { $$('[data-reveal]:not(.is-in),[data-split]:not(.is-in),[data-fade]:not(.is-in)').forEach(function (el) { var r = el.getBoundingClientRect(); if (r.top < w.innerHeight) el.classList.add('is-in'); }); }, 1200);

  /* ---------- pausa animações CSS de seções fora da tela ---------- */
  if (hasIO) {
    var secIO = new IntersectionObserver(function (es) { es.forEach(function (e) { e.target.classList.toggle('is-off', !e.isIntersecting); }); }, { rootMargin: '150px 0px' });
    $$('[data-sec]').forEach(function (s) { secIO.observe(s); });
  }

  /* ---------- itens que só trabalham quando visíveis ---------- */
  function watch(list) {
    if (!hasIO) { list.forEach(function (o) { o.vis = true; }); return list; }
    var obs = new IntersectionObserver(function (es) { es.forEach(function (e) { e.target._o.vis = e.isIntersecting; }); }, { rootMargin: '120px 0px' });
    list.forEach(function (o) { o.vis = false; o.watchEl.__o = o; o.watchEl._o = o; obs.observe(o.watchEl); });
    return list;
  }
  var scrubs = watch($$('[data-scrub]').map(function (el) {
    var words = el.textContent.trim().split(/\s+/); el.setAttribute('aria-label', words.join(' ')); el.innerHTML = '';
    var spans = words.map(function (t) { var s = d.createElement('span'); s.className = 'w'; s.textContent = t; el.appendChild(s); el.appendChild(d.createTextNode(' ')); return s; });
    return { el: el, watchEl: el, spans: spans, n: -1 };
  }));
  var stepLists = watch($$('[data-steps]').map(function (el) { return { el: el, watchEl: el, items: $$('[data-step]', el), line: $('.steps__line', el), done: false }; }));
  var rulers = watch($$('[data-ruler]').map(function (el) { return { el: el, watchEl: el, ticks: $$('i', el), n: -1 }; }));
  var para = watch($$('[data-speed]').map(function (el) { return { el: el, watchEl: el.parentNode, speed: parseFloat(el.dataset.speed) || 0 }; }));

  function stepsFrame() {
    var vh = w.innerHeight, vert = w.innerWidth <= 980;
    stepLists.forEach(function (s) {
      if (!s.vis && !(s.done && !vert)) return;
      var r = s.el.getBoundingClientRect(), n = s.items.length, p;
      if (vert) p = clamp((vh * .72 - r.top) / (r.height * .92 + 1), 0, 1);
      else {
        if (!s.done) { if (r.top > vh * .78) return; s.done = true; s.t0 = performance.now(); stepsTimer(); }
        p = clamp((performance.now() - s.t0) / (n * 520), 0, 1);
        if (p >= 1) s.finished = true;
      }
      s.el.style.setProperty('--p', p);
      s.items.forEach(function (it, i) { it.classList.toggle('on', p >= (i + .15) / n); });
    });
  }
  var stepsRun = false;
  function stepsTimer() {
    if (stepsRun) return; stepsRun = true;
    (function loop() { stepsFrame(); var more = stepLists.some(function (s) { return s.done && !s.finished && w.innerWidth > 980; }); if (more) requestAnimationFrame(loop); else stepsRun = false; })();
  }

  /* ---------- hero: do caos à ordem ---------- */
  var chaosEl = $('[data-chaos]'), chars = [];
  if (chaosEl) {
    var label = chaosEl.getAttribute('aria-label');
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (ch) {
        if (ch.nodeType === 3) {
          var frag = d.createDocumentFragment();
          ch.textContent.split(/(\s+)/).forEach(function (tok) {
            if (!tok) return;
            if (/^\s+$/.test(tok)) { frag.appendChild(d.createTextNode(' ')); return; }
            var cw = d.createElement('span'); cw.className = 'cw';
            tok.split('').forEach(function (c) { var s = d.createElement('span'); s.className = 'ch'; s.textContent = c; cw.appendChild(s); chars.push({ el: s, x: 0, y: 0, vx: 0, vy: 0, r: 0, vr: 0, cx: 0, cy: 0 }); });
            frag.appendChild(cw);
          });
          node.replaceChild(frag, ch);
        } else if (ch.nodeType === 1) walk(ch);
      });
    })(chaosEl);
    chaosEl.setAttribute('aria-label', label);
    var W = w.innerWidth, H = w.innerHeight;
    chars.forEach(function (c) {
      c.x = (Math.random() - .5) * W * .9; c.y = (Math.random() - .5) * H * .8; c.r = (Math.random() - .5) * 360; var s = .3 + Math.random() * 1.6;
      c.el.style.transform = 'translate(' + c.x.toFixed(0) + 'px,' + c.y.toFixed(0) + 'px) rotate(' + c.r.toFixed(0) + 'deg) scale(' + s.toFixed(2) + ')';
    });
    var heroSec = chaosEl.closest('section'), heroVis = true, mx = -999, my = -999, looping = false, ready = false;
    var measure = function () { var sy = w.scrollY; chars.forEach(function (c) { var r = c.el.getBoundingClientRect(); c.cx = r.left + r.width / 2 - c.x; c.cy = r.top + sy + r.height / 2 - c.y; }); };
    var startOrder = function () {
      chaosEl.classList.add('is-ready');
      if (reduce) { chars.forEach(function (c) { c.el.style.transform = ''; }); return; }
      chars.forEach(function (c, i) {
        c.el.style.transition = 'transform 1.6s cubic-bezier(.22,1,.36,1) ' + (i * 38 + 150) + 'ms, opacity .4s';
        c.el.style.transform = 'translate(0,0) rotate(0) scale(1)';
      });
      setTimeout(function () {
        chars.forEach(function (c) { c.el.style.transition = 'none'; c.x = c.y = c.vx = c.vy = c.r = c.vr = 0; });
        measure(); ready = true;
      }, chars.length * 38 + 1900);
    };
    (d.fonts && d.fonts.ready ? d.fonts.ready : Promise.resolve()).then(function () { requestAnimationFrame(startOrder); });
    if (fine && !reduce) {
      w.addEventListener('pointermove', function (e) { mx = e.clientX; my = e.clientY; if (ready && heroVis && !looping) { looping = true; requestAnimationFrame(spring); } }, { passive: true });
      var rz; w.addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(function () { if (ready) { chars.forEach(function (c) { c.el.style.transform = ''; }); measure(); } }, 250); });
      if (hasIO && heroSec) new IntersectionObserver(function (e) { heroVis = e[0].isIntersecting; }).observe(heroSec);
    }
    function spring() {
      var sy = w.scrollY, moving = false, rad = 150;
      for (var j = 0; j < chars.length; j++) {
        var c = chars[j], dx = c.cx - mx, dy = c.cy - sy - my, dist2 = dx * dx + dy * dy;
        if (dist2 < rad * rad && dist2 > 0) { var dist = Math.sqrt(dist2), f = (1 - dist / rad) * 16; c.vx += dx / dist * f; c.vy += dy / dist * f; c.vr += (dx > 0 ? 1 : -1) * f * .6; }
        if (c.x === 0 && c.y === 0 && c.r === 0 && !c.vx && !c.vy && !c.vr) continue;
        c.vx += -c.x * .07; c.vy += -c.y * .07; c.vr += -c.r * .07;
        c.vx *= .84; c.vy *= .84; c.vr *= .84;
        c.x += c.vx; c.y += c.vy; c.r += c.vr;
        if (Math.abs(c.x) + Math.abs(c.y) + Math.abs(c.r) + Math.abs(c.vx) + Math.abs(c.vy) < .08) { c.x = c.y = c.r = c.vx = c.vy = c.vr = 0; c.el.style.transform = ''; continue; }
        moving = true; c.el.style.transform = 'translate3d(' + c.x.toFixed(1) + 'px,' + c.y.toFixed(1) + 'px,0) rotate(' + c.r.toFixed(1) + 'deg)';
      }
      var near = mx > -900 && my < (heroSec ? heroSec.getBoundingClientRect().bottom : 0);
      if (moving || near) requestAnimationFrame(spring); else looping = false;
    }
  }

  /* ---------- fragmentos flutuando (canvas) ---------- */
  $$('[data-chaos-canvas]').forEach(function (cv) {
    if (reduce) return;
    var ctx = cv.getContext('2d'), dpr = Math.min(1.5, w.devicePixelRatio || 1), W, H, parts = [], vis = true, running = false, mx = -999, my = -999, last = 0;
    function size() { var r = cv.getBoundingClientRect(); W = r.width; H = r.height; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    function make() {
      parts = []; var n = Math.round(clamp(W / 60, 10, 26));
      for (var i = 0; i < n; i++) {
        var t = Math.random();
        parts.push({ x: Math.random() * W, y: Math.random() * H, s: 8 + Math.random() * 34, vx: (Math.random() - .5) * .35, vy: (Math.random() - .5) * .35,
          r: Math.random() * 6.28, vr: (Math.random() - .5) * .008, type: t < .3 ? 'tri' : t < .65 ? 'sq' : t < .85 ? 'fill' : 'cross', ox: 0, oy: 0 });
      }
    }
    function draw(t) {
      if (!vis) { running = false; return; }
      requestAnimationFrame(draw);
      if (t - last < 33) return; last = t; // ~30 fps
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        p.x += p.vx * 2; p.y += p.vy * 2; p.r += p.vr * 2;
        if (p.x < -50) p.x = W + 50; else if (p.x > W + 50) p.x = -50; if (p.y < -50) p.y = H + 50; else if (p.y > H + 50) p.y = -50;
        var dx = p.x + p.ox - mx, dy = p.y + p.oy - my, d2 = dx * dx + dy * dy;
        if (d2 < 28900 && d2 > 0) { var dist = Math.sqrt(d2), f = (1 - dist / 170) * 4; p.ox += dx / dist * f; p.oy += dy / dist * f; }
        p.ox *= .93; p.oy *= .93;
        ctx.save(); ctx.translate(p.x + p.ox, p.y + p.oy); ctx.rotate(p.r);
        if (p.type === 'tri') { ctx.fillStyle = '#EA671E'; ctx.beginPath(); ctx.moveTo(-p.s / 2, -p.s / 2); ctx.lineTo(p.s / 2, -p.s / 2); ctx.lineTo(p.s / 2, p.s / 2); ctx.closePath(); ctx.fill(); }
        else if (p.type === 'sq') { ctx.strokeStyle = 'rgba(236,236,237,.28)'; ctx.lineWidth = 1.5; ctx.strokeRect(-p.s / 2, -p.s / 2, p.s, p.s); }
        else if (p.type === 'fill') { ctx.fillStyle = 'rgba(236,236,237,.1)'; ctx.fillRect(-p.s / 3, -p.s / 3, p.s / 1.5, p.s / 1.5); }
        else { ctx.strokeStyle = 'rgba(234,103,30,.7)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(-8, 0); ctx.lineTo(8, 0); ctx.moveTo(0, -8); ctx.lineTo(0, 8); ctx.stroke(); }
        ctx.restore();
      }
    }
    function go() { if (!running && vis && !d.hidden) { running = true; requestAnimationFrame(draw); } }
    size(); make(); go();
    var rz; w.addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(function () { size(); make(); }, 200); });
    if (fine) w.addEventListener('pointermove', function (e) { var r = cv.getBoundingClientRect(); mx = e.clientX - r.left; my = e.clientY - r.top; }, { passive: true });
    d.addEventListener('visibilitychange', go);
    if (hasIO) new IntersectionObserver(function (e) { vis = e[0].isIntersecting; go(); }).observe(cv);
  });

  /* ---------- faixas: aceleram com a rolagem ---------- */
  var marqs = $$('[data-marq]'), marqRun = false, vel = 0;
  function marqLoop() {
    var rate = 1 + Math.min(6, Math.abs(vel) * .35), dir = vel < -.5 ? -1 : 1, settled = true;
    vel *= .92;
    marqs.forEach(function (m) {
      var a = m._a || (m._a = m.getAnimations && m.getAnimations()[0]); if (!a) return;
      var tgt = dir * rate; a.playbackRate = lerp(a.playbackRate, tgt, .12);
      if (Math.abs(a.playbackRate - 1) > .04) settled = false;
    });
    if (!settled || Math.abs(vel) > .05) requestAnimationFrame(marqLoop); else { marqRun = false; marqs.forEach(function (m) { if (m._a) m._a.playbackRate = 1; }); }
  }

  /* ---------- scroll horizontal do portfólio ---------- */
  var hs = $('[data-hs]'), hsTrack = $('[data-hs-track]'), hsBar = $('[data-hs-bar]'), hsDist = 0;
  function hsOn() { return w.innerWidth > 1000 && w.innerHeight >= 620; }
  function hsSize() {
    if (!hs) return;
    var on = hsOn(); root.classList.toggle('hs-off', !on);
    if (!on) { hs.style.height = ''; hsTrack.style.transform = ''; return; }
    hsDist = Math.max(0, hsTrack.scrollWidth - w.innerWidth + 40);
    hs.style.height = (w.innerHeight + hsDist) + 'px';
  }
  function hsFrame(y) {
    if (!hs || !hsOn()) return;
    var top = hs.offsetTop, p = clamp((y - top) / Math.max(1, hsDist), 0, 1);
    hsTrack.style.transform = 'translate3d(' + (-p * hsDist).toFixed(1) + 'px,0,0)';
    if (hsBar) hsBar.style.setProperty('--p', p.toFixed(4));
  }

  /* ---------- painéis empilhados ---------- */
  var panels = $$('[data-panel]');
  function panelsFrame() {
    if (!panels.length) return;
    if (w.innerWidth <= 820) { panels.forEach(function (p) { p.style.transform = ''; p.style.setProperty('--dim', 0); }); return; }
    var vh = w.innerHeight;
    panels.forEach(function (p, i) {
      var nx = panels[i + 1]; if (!nx) return;
      var t = clamp(1 - nx.getBoundingClientRect().top / vh, 0, 1);
      if (p._t === t) return; p._t = t;
      p.style.transform = 'scale(' + (1 - t * .06).toFixed(4) + ')'; p.style.setProperty('--dim', (t * .55).toFixed(3));
    });
  }

  /* ---------- loop de rolagem ---------- */
  var lastY = w.scrollY, hdr = $('[data-hdr]'), prog = $('.progress i'), fab = $('.fab'), ticking = false, hdrHidden = false, heroIn = $('.hero__in'), heroOn = !!$('.hero');
  function onScroll() {
    ticking = false;
    var y = w.scrollY, vh = w.innerHeight, dh = root.scrollHeight - vh, dy = y - lastY; lastY = y;
    vel = lerp(vel, dy, .25); if (!marqRun && marqs.length && Math.abs(vel) > .6) { marqRun = true; requestAnimationFrame(marqLoop); }
    if (hdr) {
      hdr.classList.toggle('is-stuck', y > 40);
      var hide = y > 420 && dy > 4 && !(menu && menu.classList.contains('is-open')), show = dy < -4 || y < 420;
      if (hide && !hdrHidden) { hdrHidden = true; hdr.classList.add('is-hidden'); } else if (show && hdrHidden) { hdrHidden = false; hdr.classList.remove('is-hidden'); }
    }
    if (prog) prog.style.transform = 'scaleX(' + (dh > 0 ? y / dh : 0).toFixed(4) + ')';
    if (fab) fab.classList.toggle('is-on', y > 520);
    hsFrame(y); panelsFrame(); stepsFrame();
    scrubs.forEach(function (s) {
      if (!s.vis) return;
      var r = s.el.getBoundingClientRect(), p = clamp((vh * .85 - r.top) / (vh * .45 + r.height * .7), 0, 1), n = Math.round(p * s.spans.length);
      if (n === s.n) return; var prev = s.n; s.n = n;
      var a = Math.max(0, Math.min(prev, n)), b = Math.max(prev, n); if (prev < 0) { a = 0; b = s.spans.length; }
      for (var i = a; i < b && i < s.spans.length; i++) s.spans[i].classList.toggle('on', i < n);
    });
    rulers.forEach(function (r) {
      if (!r.vis) return;
      var b = r.el.getBoundingClientRect(), p = clamp((vh * .95 - b.top) / (vh * .6), 0, 1), n = Math.round(p * r.ticks.length);
      if (n === r.n) return; r.n = n; r.ticks.forEach(function (t, i) { t.classList.toggle('on', i === n - 1 || i === n - 2); });
    });
    para.forEach(function (o) {
      if (!o.vis) return;
      var r = o.watchEl.getBoundingClientRect();
      o.el.style.transform = 'translate3d(0,' + ((r.top + r.height / 2 - vh / 2) * o.speed).toFixed(1) + 'px,0)';
    });
    if (heroOn && heroIn && !reduce && y < vh * 1.1) { heroIn.style.transform = 'translate3d(0,' + (y * .1).toFixed(1) + 'px,0)'; heroIn.style.opacity = clamp(1 - y / (vh * .9), 0, 1).toFixed(2); }
  }
  var sched = function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } };
  w.addEventListener('scroll', sched, { passive: true });
  var rzT; w.addEventListener('resize', function () { clearTimeout(rzT); rzT = setTimeout(function () { hsSize(); sched(); }, 120); });
  (d.fonts && d.fonts.ready ? d.fonts.ready : Promise.resolve()).then(function () { hsSize(); onScroll(); });
  w.addEventListener('load', function () { hsSize(); onScroll(); });
  hsSize(); onScroll();

  /* ---------- inclinação e ímã (só mouse) ---------- */
  if (fine && !reduce) {
    $$('[data-tilt]').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect(), px = (e.clientX - r.left) / r.width - .5, py = (e.clientY - r.top) / r.height - .5;
        el.style.transform = 'perspective(900px) rotateX(' + (-py * 7).toFixed(2) + 'deg) rotateY(' + (px * 9).toFixed(2) + 'deg)';
      }, { passive: true });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
    $$('[data-magnetic]').forEach(function (el) {
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect(); el.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * .2).toFixed(1) + 'px,' + ((e.clientY - r.top - r.height / 2) * .28).toFixed(1) + 'px)';
      }, { passive: true });
      el.addEventListener('pointerleave', function () { el.style.transform = ''; });
    });
  }

  /* ---------- filtros do portfólio ---------- */
  $$('[data-chips]').forEach(function (box) {
    box.addEventListener('click', function (e) {
      var b = e.target.closest('[data-filter]'); if (!b) return;
      $$('.chip', box).forEach(function (c) { c.classList.toggle('is-on', c === b); });
      var f = b.dataset.filter, grid = $('[data-grid]', box.closest('section'));
      $$('.work', grid).forEach(function (wk) { wk.classList.toggle('is-off', f !== '*' && wk.dataset.tipo !== f); });
    });
  });

  /* ---------- lightbox ---------- */
  (function lightbox() {
    var lb = $('[data-lightbox]'), stage = $('[data-stage]'), cap = $('[data-cap]'); if (!lb) return;
    var data = {}; try { data = JSON.parse($('#works-data').textContent); } catch (e) {}
    var order = [], cur = -1, lastFocus = null;
    function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    function collect(scope) { var seen = {}; order = []; $$('[data-open]', scope || d).forEach(function (b) { var id = b.dataset.open; if (!seen[id] && data[id]) { seen[id] = 1; order.push(id); } }); }
    function show(i) {
      cur = (i + order.length) % order.length; var wk = data[order[cur]], html = '';
      if (wk.youtube) html = '<iframe src="https://www.youtube-nocookie.com/embed/' + esc(wk.youtube) + '?autoplay=1&rel=0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen title="' + esc(wk.titulo) + '"></iframe>';
      else if (wk.vimeo) html = '<iframe src="https://player.vimeo.com/video/' + esc(wk.vimeo) + '?autoplay=1" allow="autoplay; fullscreen" allowfullscreen title="' + esc(wk.titulo) + '"></iframe>';
      else if (wk.mp4) html = '<video src="' + esc(wk.mp4) + '" controls autoplay playsinline></video>';
      else if (wk.capa) html = '<img src="' + esc(wk.capa) + '" alt="' + esc(wk.titulo) + '">';
      else html = '<div class="frame" data-v="1"><span class="frame__ph"><img class="sym" src="/assets/img/brand/simbolo.svg" alt="" width="100" height="100"></span><i class="fc tl"></i><i class="fc tr"></i><i class="fc bl"></i><i class="fc br"></i></div>';
      stage.innerHTML = html;
      cap.innerHTML = '<span>' + esc(wk.cliente) + ' · ' + esc(wk.servico) + '</span><strong>' + esc(wk.titulo) + '</strong><p>' + esc(wk.descricao) + '</p>';
    }
    function open(id, scope) {
      collect(scope); var i = order.indexOf(id); if (i < 0) return;
      lastFocus = d.activeElement; lb.hidden = false; scrollLock(true); show(i);
      requestAnimationFrame(function () { lb.classList.add('is-open'); $('[data-close]', lb).focus(); });
      track('portfolio_abrir', { id: id });
    }
    function close() { lb.classList.remove('is-open'); stage.innerHTML = ''; scrollLock(false); setTimeout(function () { lb.hidden = true; }, 350); if (lastFocus) lastFocus.focus(); }
    d.addEventListener('click', function (e) {
      var b = e.target.closest('[data-open]'); if (b) { open(b.dataset.open, b.closest('section')); return; }
      if (e.target.closest('[data-close]')) close();
      else if (e.target.closest('[data-prev]')) show(cur - 1); else if (e.target.closest('[data-next]')) show(cur + 1);
      else if (e.target === lb || e.target === stage) close();
    });
    d.addEventListener('keydown', function (e) {
      if (lb.hidden) return; if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(cur - 1); if (e.key === 'ArrowRight') show(cur + 1);
    });
  })();

  /* ---------- casamentos: monte a cobertura ---------- */
  var opts = $('[data-opts]');
  function selectedOpts() { return opts ? $$('input:checked', opts).map(function (i) { return i.value; }) : []; }
  if (opts) {
    var cta = $('[data-opt-cta]'), cnt = $('[data-opt-count]');
    var upd = function () {
      var sel = selectedOpts(); cnt.textContent = sel.length;
      cta.href = 'https://wa.me/' + WA_NUM + '?text=' + encodeURIComponent(MSG.casamentos + (sel.length ? ' Tenho interesse em: ' + sel.join(', ') + '.' : ''));
    };
    opts.addEventListener('change', upd); upd();
  }

  /* ---------- formulários → WhatsApp + registro no Netlify ---------- */
  var svc = $('[data-service]'), extra = $('[data-extra]');
  if (svc && extra) svc.addEventListener('change', function () { extra.hidden = !/Eventos|Casamentos/.test(svc.value); });
  $$('.js-form').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault(); if (!f.checkValidity()) { f.reportValidity(); return; }
      var fd = new FormData(f), g = function (k) { return (fd.get(k) || '').toString().trim(); };
      var lines = [MSG[f.dataset.wa] || MSG.geral, ''];
      [['nome', 'Nome'], ['telefone', 'Telefone'], ['email', 'E-mail'], ['servico', 'Serviço de interesse'], ['data', 'Data'], ['local', 'Local'], ['mensagem', 'Mensagem']].forEach(function (m) { if (g(m[0])) lines.push(m[1] + ': ' + g(m[0])); });
      var sel = selectedOpts(); if (sel.length && f.dataset.wa === 'casamentos') lines.push('Interesse em: ' + sel.join(', '));
      w.open('https://wa.me/' + WA_NUM + '?text=' + encodeURIComponent(lines.join('\n')), '_blank', 'noopener');
      track(f.dataset.track || 'form', { pagina: location.pathname });
      if (!/^(localhost|127\.|0\.0\.0\.0)/.test(location.hostname)) {
        try { fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(fd).toString(), keepalive: true }); } catch (er) {}
      }
      var b = $('button[type=submit] .btn__t', f);
      if (b) { var old = b.textContent; b.textContent = 'Abrindo o WhatsApp…'; setTimeout(function () { b.textContent = old; }, 4500); }
      if (f.name === 'contato') setTimeout(function () { location.href = '/contato/obrigado/'; }, 900);
    });
  });

  /* ---------- âncoras suaves ---------- */
  d.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]'); if (!a || a.getAttribute('href') === '#') return;
    var t = $(a.getAttribute('href')); if (!t) return;
    e.preventDefault(); closeMenu();
    if (lenis) lenis.scrollTo(t, { offset: -40, duration: 1.3 });
    else w.scrollTo({ top: t.getBoundingClientRect().top + w.scrollY - 40, behavior: reduce ? 'auto' : 'smooth' });
  });
})();
