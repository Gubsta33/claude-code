/* =============================================================
   VANUSA OLIVEIRA ADVOCACIA
   Movimento: discreto, reversivel, e sempre respeitando
   a preferencia de movimento reduzido, ao vivo, nos dois sentidos.
   ============================================================= */
(function () {
  'use strict';

  var qs = function (s, c) { return (c || document).querySelector(s); };
  var qsa = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var rmq = window.matchMedia('(prefers-reduced-motion: reduce)');
  var reduced = function () { return rmq.matches; };

  /* ---------- Cabecalho ---------- */
  var hdr = qs('#hdr');
  var hdrSolid = null;
  function paintHeader() {
    var want = window.scrollY > 48;
    if (want === hdrSolid) return;          // so escreve no DOM quando muda
    hdrSolid = want;
    hdr.classList.toggle('solid', want);
  }

  /* ---------- Menu mobile ---------- */
  var burger = qs('#burger');
  var mnav = qs('#mnav');
  if (burger && mnav) {
    qsa('a', mnav).forEach(function (a, i) { a.style.setProperty('--d', (0.06 + i * 0.055).toFixed(3) + 's'); });
    var setNav = function (open) {
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      mnav.classList.toggle('open', open);
      mnav.setAttribute('aria-hidden', open ? 'false' : 'true');
      document.documentElement.style.overflow = open ? 'hidden' : '';
      document.body.classList.toggle('nav-open', open);   // esconde o botao flutuante
    };
    burger.addEventListener('click', function () {
      setNav(burger.getAttribute('aria-expanded') !== 'true');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') { setNav(false); burger.focus(); }
    });
    setNav(false);
  }

  /* ---------- Revelacao no scroll ---------- */
  var revealed = [];
  function markDone(el) {
    if (!el.classList.contains('stag')) return;
    window.setTimeout(function () { el.classList.add('done'); }, 1600);   // aposenta os atrasos do escalonamento
  }
  var io = ('IntersectionObserver' in window) ? new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      en.target.classList.add('in');
      markDone(en.target);
      io.unobserve(en.target);
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 }) : null;

  function armReveals() {
    qsa('.rv, .stag, .ln, .draw, .steps, .strip').forEach(function (el) {
      if (revealed.indexOf(el) > -1) return;
      revealed.push(el);
      if (!io || reduced()) { el.classList.add('in'); el.classList.add('done'); return; }
      io.observe(el);
    });
  }

  /* atraso em cascata, declarado no proprio elemento */
  qsa('.stag').forEach(function (g) {
    var step = parseFloat(g.getAttribute('data-step') || '0.08');
    qsa(':scope > *', g).forEach(function (c, i) { c.style.setProperty('--d', (i * step).toFixed(3) + 's'); });
  });
  qsa('.ln').forEach(function (l, i) {
    if (!l.style.getPropertyValue('--d')) l.style.setProperty('--d', (0.06 + i * 0.10).toFixed(3) + 's');
  });
  qsa('.steps .step').forEach(function (s, i) { s.style.setProperty('--d', (0.1 + i * 0.16).toFixed(3) + 's'); });

  /* ---------- Linhas SVG que se desenham ---------- */
  qsa('.draw').forEach(function (svg) {
    qsa('path, line, circle, rect', svg).forEach(function (p, i) {
      var len = 1000;
      try { len = Math.ceil(p.getTotalLength ? p.getTotalLength() : 1000); } catch (e) { len = 1000; }
      if (!len || !isFinite(len)) len = 1000;
      p.style.setProperty('--len', len);
      p.style.setProperty('--d', (i * 0.09).toFixed(3) + 's');
    });
  });

  /* ---------- A assinatura: os tracos da linha do tempo ---------- */
  var ticks = qsa('#spineTicks i');
  var tickOn = -1;
  function paintTicks() {
    if (!ticks.length) return;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var p = h > 0 ? Math.min(1, Math.max(0, window.scrollY / h)) : 0;
    var n = Math.round(p * ticks.length);
    if (n === tickOn) return;               // so escreve no DOM quando muda
    tickOn = n;
    for (var i = 0; i < ticks.length; i++) ticks[i].classList.toggle('on', i < n);
  }

  /* ---------- Parallax do hero (o laco descansa) ---------- */
  var pars = qsa('[data-par]');
  var heroEl = qs('.hero, .phero');
  var heroVisible = true;
  var parTarget = 0, parShown = 0, rafId = null, lastTick = 0;

  function heroProgress() {
    if (!heroEl) return 0;
    var r = heroEl.getBoundingClientRect();
    var span = r.height + window.innerHeight;
    return Math.min(1, Math.max(0, (window.innerHeight - r.top) / span));
  }
  function applyPar(v) {
    for (var i = 0; i < pars.length; i++) {
      var amt = parseFloat(pars[i].getAttribute('data-par')) || 0;
      pars[i].style.transform = 'translate3d(0,' + (v * amt).toFixed(2) + 'px,0)';
    }
  }
  function tick(now) {
    var dt = Math.min(100, now - (lastTick || now));
    lastTick = now;
    var k = 0.14;
    parShown += (parTarget - parShown) * (1 - Math.pow(1 - k, dt / 16.667));
    if (Math.abs(parTarget - parShown) < 0.05) {
      parShown = parTarget; rafId = null; lastTick = 0;   // convergiu: descansa
    } else {
      rafId = window.requestAnimationFrame(tick);
    }
    applyPar(parShown);
  }
  function driveParallax() {
    if (!pars.length || reduced() || !heroVisible) return;
    parTarget = (heroProgress() - 0.5) * 100;
    if (rafId === null) rafId = window.requestAnimationFrame(tick);
  }
  if (heroEl && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; }, { threshold: 0 }).observe(heroEl);
  }

  /* ---------- Um unico ouvinte de scroll ---------- */
  var queued = false;
  function onScroll() {
    if (queued) return;
    queued = true;
    window.requestAnimationFrame(function () {
      queued = false;
      paintHeader();
      paintTicks();
      paintProgress();
      paintWa();
      paintShero();
      driveParallax();
    });
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });

  /* ---------- Contadores ---------- */
  function runCounter(el) {
    var end = parseFloat(el.getAttribute('data-count'));
    var dec = parseInt(el.getAttribute('data-dec') || '0', 10);
    var fmt = function (v) { return dec ? v.toFixed(dec).replace('.', ',') : String(Math.round(v)); };
    if (reduced()) { el.textContent = fmt(end); return; }
    var t0 = null, dur = 1500, last = '';
    (function step(ts) {
      if (t0 === null) t0 = ts;
      var p = Math.min(1, (ts - t0) / dur);
      var e = 1 - Math.pow(1 - p, 3);
      var s = fmt(end * e);
      if (s !== last) { last = s; el.textContent = s; }   // so escreve quando muda
      if (p < 1) window.requestAnimationFrame(step);
    })(performance.now());
  }
  qsa('[data-count]').forEach(function (el) {
    if (!('IntersectionObserver' in window)) { runCounter(el); return; }
    var o = new IntersectionObserver(function (e) {
      if (e[0].isIntersecting) { runCounter(el); o.disconnect(); }
    }, { threshold: 0.6 });
    o.observe(el);
  });

  /* ---------- Perguntas frequentes ---------- */
  qsa('.faq__q').forEach(function (btn) {
    var panel = document.getElementById(btn.getAttribute('aria-controls'));
    if (!panel) return;
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      if (open) {
        panel.style.height = panel.scrollHeight + 'px';
        window.requestAnimationFrame(function () { panel.style.height = '0px'; });
      } else {
        panel.style.height = panel.scrollHeight + 'px';
        var end = function () { panel.style.height = 'auto'; panel.removeEventListener('transitionend', end); };
        panel.addEventListener('transitionend', end);
        if (reduced()) end();
      }
    });
  });

  /* ---------- O momento interativo: a linha do tempo ---------- */
  (function () {
    var track = qs('#tlTrack');
    if (!track) return;
    var btns = qsa('.tl__b', track);
    var panels = qsa('.tl__p');
    function select(i, focus) {
      btns.forEach(function (b, n) { b.setAttribute('aria-selected', n === i ? 'true' : 'false'); b.tabIndex = n === i ? 0 : -1; });
      panels.forEach(function (p, n) { p.classList.toggle('on', n === i); p.hidden = n !== i; });
      if (focus) btns[i].focus();
    }
    btns.forEach(function (b, i) {
      b.addEventListener('click', function () { select(i); });
      b.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        select((i + d + btns.length) % btns.length, true);
      });
    });
    select(0);
  })();

  /* ---------- Formulario: monta a mensagem e abre o WhatsApp ---------- */
  var form = qs('#contatoForm');
  if (form) {
    var showErr = function (id, on) {
      var e = document.getElementById(id);
      if (e) e.classList.toggle('on', on);
      return on;
    };
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var nome = qs('#nome'), fone = qs('#fone'), msg = qs('#msg'), lgpd = qs('#lgpd');
      var bad = false;
      bad = showErr('errNome', !nome.value.trim()) || bad;
      bad = showErr('errFone', !fone.value.trim()) || bad;
      bad = showErr('errMsg', !msg.value.trim()) || bad;
      bad = showErr('errLgpd', !lgpd.checked) || bad;
      if (bad) {
        var first = qs('.f__err.on');
        if (first) {
          var field = first.previousElementSibling || first.parentElement;
          if (field && field.focus) field.focus();
        }
        return;
      }
      var cidade = qs('#cidade'), assunto = qs('#assunto');
      var linhas = ['Olá, vim pelo site.', '', 'Nome: ' + nome.value.trim(),
                    'Telefone: ' + fone.value.trim()];
      if (cidade && cidade.value.trim()) linhas.push('Cidade: ' + cidade.value.trim());
      if (assunto && assunto.value.trim()) linhas.push('Assunto: ' + assunto.value.trim());
      linhas.push('', msg.value.trim());
      window.open('https://wa.me/5551996881523?text=' + encodeURIComponent(linhas.join('\n')),
                  '_blank', 'noopener');
      var ok = qs('#formOk');
      form.querySelectorAll('.f, .form__foot, .consent').forEach(function (n) { n.style.display = 'none'; });
      ok.classList.add('on');
      ok.setAttribute('tabindex', '-1');
      ok.focus();
    });
  }

  /* ---------- Transicao entre paginas ---------- */
  (function () {
    var pt = qs('#pt');
    if (!pt) return;
    window.addEventListener('pageshow', function () { pt.classList.remove('on'); });
    document.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a') : null;
      if (!a || reduced()) return;
      var href = a.getAttribute('href') || '';
      if (a.target === '_blank' || href.charAt(0) === '#' || /^(https?:|mailto:|tel:)/.test(href)) return;
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
      if (a.pathname === window.location.pathname) return;
      e.preventDefault();
      pt.classList.add('on');
      window.setTimeout(function () { window.location.href = href; }, 480);
    });
  })();

  /* ---------- Pausar quando a aba sai de foco ---------- */
  document.addEventListener('visibilitychange', function () {
    document.body.classList.toggle('paused', document.hidden);
  });

  /* ---------- Movimento reduzido, ao vivo, nos dois sentidos ---------- */
  function pinFinalStates() {
    document.body.classList.add('rm');
    qsa('.rv, .stag, .ln, .draw, .steps, .strip').forEach(function (el) { el.classList.add('in'); el.classList.add('done'); });
    qsa('[data-count]').forEach(function (el) {
      var dec = parseInt(el.getAttribute('data-dec') || '0', 10);
      var v = parseFloat(el.getAttribute('data-count'));
      el.textContent = dec ? v.toFixed(dec).replace('.', ',') : String(v);
    });
    if (rafId !== null) { window.cancelAnimationFrame(rafId); rafId = null; }
    applyPar(0);
    sheroOn = false;
    pinShero();
  }
  function unpinFinalStates() {
    document.body.classList.remove('rm');
    parShown = 0; parTarget = 0; lastTick = 0;
    onScroll();
  }
  rmq.addEventListener('change', function (e) {
    if (e.matches) pinFinalStates();
    else { unpinFinalStates(); armReveals(); applyHeroMode(); }
  });


  /* ---------- Hero cinematografico: os cinco portoes, decididos ao vivo ---------- */
  var GATES = [
    '(max-width: 720px)',
    '(orientation: portrait) and (max-width: 1024px)',
    '(orientation: portrait) and (pointer: coarse)',
    '(orientation: landscape) and (pointer: coarse) and (max-height: 560px)',
    '(prefers-reduced-motion: reduce)'
  ];
  var shero = qs('#shero');
  var sheroOn = false;
  var bands = qsa('.shero .band').map(function (el) {
    var r = (el.getAttribute('data-band') || '0,1').split(',');
    return { el: el, a: parseFloat(r[0]), b: parseFloat(r[1]), op: -1, live: null };
  });
  var pathLine = qs('#pathLine'), pathGlow = qs('#pathGlow'), sky = qs('.shero__sky');
  var pathLen = 0;
  if (pathLine && pathLine.getTotalLength) {
    try { pathLen = pathLine.getTotalLength(); } catch (e) { pathLen = 0; }
    if (pathLen) {
      [pathLine, pathGlow].forEach(function (el) {
        el.style.strokeDasharray = pathLen;
        el.style.strokeDashoffset = pathLen;
      });
    }
  }
  var smoothstep = function (p, e0, e1) {
    var x = Math.min(1, Math.max(0, (p - e0) / (e1 - e0)));
    return x * x * (3 - 2 * x);
  };
  var lastP = -1, lastDash = -1;
  function sheroProgress() {
    if (!shero) return 0;
    var r = shero.getBoundingClientRect();
    var span = shero.offsetHeight - window.innerHeight;
    return span > 0 ? Math.min(1, Math.max(0, -r.top / span)) : 0;
  }
  function paintShero() {
    if (!sheroOn || !shero) return;
    var p = sheroProgress();
    if (Math.abs(p - lastP) > 0.0015) {           // so escreve quando muda de verdade
      lastP = p;
      sky.style.setProperty('--p', p.toFixed(4));
      shero.style.setProperty('--p', p.toFixed(4));
    }
    if (pathLen) {
      var dash = Math.round(pathLen * (1 - Math.min(1, p * 1.06)));
      if (dash !== lastDash) {
        lastDash = dash;
        pathLine.style.strokeDashoffset = dash;
        pathGlow.style.strokeDashoffset = dash;
      }
    }
    for (var i = 0; i < bands.length; i++) {
      var b = bands[i];
      var f = Math.min(0.02, (b.b - b.a) / 3);
      var inEdge = (i === 0) ? 1 : smoothstep(p, b.a, b.a + f);
      var outEdge = (i === bands.length - 1) ? 0 : smoothstep(p, b.b - f, b.b);
      var op = inEdge * (1 - outEdge);
      if (Math.abs(op - b.op) > 0.004) {
        b.op = op;
        b.el.style.opacity = op.toFixed(3);
        b.el.style.transform = 'translateY(calc(-50% + ' + ((1 - op) * 16).toFixed(1) + 'px))';
      }
      var live = op > 0.55;
      if (live !== b.live) {
        b.live = live;
        b.el.classList.toggle('live', live);
        b.el.setAttribute('aria-hidden', live ? 'false' : 'true');
      }
    }
  }
  function pinShero() {                            // estado final, sem movimento
    if (!shero) return;
    if (pathLen) { pathLine.style.strokeDashoffset = 0; pathGlow.style.strokeDashoffset = 0; }
    bands.forEach(function (b, i) {
      b.op = -1; b.live = null;
      b.el.style.opacity = i === 0 ? '1' : '0';
      b.el.style.transform = 'translateY(-50%)';
      b.el.setAttribute('aria-hidden', i === 0 ? 'false' : 'true');
    });
  }
  function applyHeroMode() {
    var off = GATES.some(function (q) { return window.matchMedia(q).matches; });
    if (off) { sheroOn = false; return; }
    if (sheroOn) return;
    sheroOn = true;
    lastP = -1; lastDash = -1;
    bands.forEach(function (b) { b.op = -1; b.live = null; });
    paintShero();
  }
  var MQLS = GATES.map(function (q) { return window.matchMedia(q); });
  MQLS.forEach(function (m) { m.addEventListener('change', applyHeroMode); });

  /* ---------- Barra de progresso de leitura ---------- */
  var progBar = qs('#prog i');
  var lastProg = -1;
  function paintProgress() {
    if (!progBar) return;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var p = h > 0 ? Math.min(1, Math.max(0, window.scrollY / h)) : 0;
    if (Math.abs(p - lastProg) < 0.004) return;
    lastProg = p;
    progBar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
  }

  /* ---------- WhatsApp flutuante ---------- */
  var waf = qs('#wafloat');
  var wafOn = null;
  function paintWa() {
    if (!waf) return;
    var want = window.scrollY > window.innerHeight * 0.7;
    if (want === wafOn) return;
    wafOn = want;
    waf.classList.toggle('on', want);
  }

  /* ---------- Aviso de cookies ---------- */
  (function () {
    var ck = qs('#ck');
    if (!ck) return;
    var KEY = 'vo-cookies';
    var saved = null;
    try { saved = window.localStorage.getItem(KEY); } catch (e) { saved = 'skip'; }
    if (!saved) window.setTimeout(function () { ck.classList.add('on'); }, 1200);
    qsa('[data-ck]', ck).forEach(function (b) {
      b.addEventListener('click', function () {
        try { window.localStorage.setItem(KEY, b.getAttribute('data-ck')); } catch (e) { /* sem storage */ }
        ck.classList.remove('on');
      });
    });
  })();

  /* ---------- Filtro dos conteudos ---------- */
  (function () {
    var btnsIniciais = qsa('.filters button');
    if (!btnsIniciais.length) return;
    // A grade so existe quando ha mais de um texto publicado. Sem ela o filtro
    // segue valendo: comanda o destaque e o painel da area.
    var grid = qs('#artGrid');
    var arts = grid ? qsa('.art', grid) : [];
    var empty = qs('#artEmpty');
    var feat = qs('#featBlock');                 // o destaque tambem obedece ao filtro
    var areas = qsa('.area');
    var btns = qsa('.filters button');
    var live = qs('#artLive');
    var now = qs('#artNow');
    var nowCat = qs('[data-now-cat]'), nowCount = qs('[data-now-count]');
    var rotulo = {};
    btns.forEach(function (b) { rotulo[b.getAttribute('data-cat')] = b.textContent.trim(); });

    function apply(cat, mover) {
      btns.forEach(function (o) {
        o.setAttribute('aria-pressed', o.getAttribute('data-cat') === cat ? 'true' : 'false');
      });
      var shown = 0;
      arts.forEach(function (a) {
        var on = (cat === 'todos' || a.getAttribute('data-cat') === cat);
        a.hidden = !on;
        if (on) shown++;
      });
      var featOn = !feat || cat === 'todos' || feat.getAttribute('data-cat') === cat;
      if (feat) feat.hidden = !featOn;
      // o painel da area aparece junto com o filtro dela: filtrar reduz a lista
      // a um card e a pagina ficava vazia demais sem essa explicacao
      areas.forEach(function (s) { s.hidden = (cat === 'todos' || s.getAttribute('data-cat') !== cat); });
      if (empty) empty.hidden = shown > 0;

      var texto = shown === 0 ? 'nenhum conteúdo'
                : (shown === 1 ? '1 conteúdo' : shown + ' conteúdos');
      if (live) live.textContent = rotulo[cat] + ': ' + texto + '.';
      if (now) {                                  // retorno visivel, junto do resultado
        now.hidden = (cat === 'todos');
        if (nowCat) nowCat.textContent = rotulo[cat] || cat;
        if (nowCount) nowCount.textContent = texto;
      }
      if (mover) {                                // leva os olhos ate o resultado
        var painel = areas.filter(function (s) { return !s.hidden; })[0];
        var alvo = painel || (featOn && feat ? feat : qs('#gridBlock'));
        if (alvo) alvo.scrollIntoView({ behavior: reduced() ? 'auto' : 'smooth', block: 'start' });
      }
    }

    btns.forEach(function (b) {
      b.addEventListener('click', function () { apply(b.getAttribute('data-cat'), true); });
    });
    if (now) {                                    // o "ver todos" limpa o filtro sem rolar de novo
      qsa('button', now).forEach(function (b) {
        b.addEventListener('click', function () { apply('todos', false); });
      });
    }
  })();

  /* ---------- Mapa sob demanda ---------- */
  (function () {
    var btn = qs('#mapLoad');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = btn.getAttribute('data-src');
      f.title = 'Mapa com a localização do escritório em Taquara';
      f.loading = 'lazy';
      f.referrerPolicy = 'no-referrer-when-downgrade';
      f.setAttribute('allowfullscreen', '');
      btn.parentNode.appendChild(f);
      btn.remove();
    });
  })();

  /* ---------- Partida ---------- */
  armReveals();
  paintHeader();
  paintTicks();
  paintProgress();
  paintWa();
  applyHeroMode();
  if (!sheroOn) pinShero();
  if (reduced()) pinFinalStates();
  else window.requestAnimationFrame(function () { driveParallax(); });
})();
