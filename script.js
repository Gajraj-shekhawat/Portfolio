// The 'js' class is set inline in <head>, so animated content never flashes before this runs.
(() => {
  // Google Apps Script web-app URL that saves leads to the Sheet and emails Gajraj.
  // Leave empty to fall back to email (form) / WhatsApp (chat).
  const LEAD_ENDPOINT = 'https://script.google.com/macros/s/AKfycbwvZCRkCqXyEqqIlPJcNyTept1inFr-2pjicCuqlJ4nEh7zoO3AXky9BGc6ZqbVSDqPOQ/exec';
  const WA_NUMBER = '919414584444';
  const root = document.documentElement;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];

  /* ---------- Theme toggle ---------- */
  $('#themeToggle').addEventListener('click', () => {
    const current = root.dataset.theme ||
      (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    const next = current === 'light' ? 'dark' : 'light';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) {}
  });

  /* ---------- Mobile menu ---------- */
  const navToggle = $('#navToggle');
  const navLinks = $('#navLinks');
  const setMenu = (open) => {
    navLinks.classList.toggle('open', open);
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  };
  navToggle.addEventListener('click', () => setMenu(!navLinks.classList.contains('open')));
  navLinks.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });

  /* ---------- Scroll: progress bar, nav border, back-to-top ring ---------- */
  const nav = $('.nav');
  const bar = $('#progressBar');
  const toTop = $('#toTop');
  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const max = root.scrollHeight - innerHeight;
      const p = max > 0 ? Math.min(1, scrollY / max) : 0;
      bar.style.setProperty('--p', p.toFixed(4));
      if (toTop) {
        toTop.style.setProperty('--p', p.toFixed(4));
        toTop.classList.toggle('show', scrollY > innerHeight * 0.8);
      }
      nav.classList.toggle('is-scrolled', scrollY > 8);
      ticking = false;
    });
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Count-up numbers ---------- */
  const countUp = (el) => {
    const target = parseFloat(el.dataset.count);
    const decimals = +(el.dataset.decimals || 0);
    const fmt = (v) => el.hasAttribute('data-comma') ? Math.round(v).toLocaleString('en-IN') : v.toFixed(decimals);
    if (reduceMotion) { el.textContent = fmt(target); return; }
    const t0 = performance.now(), dur = 1400;
    const step = (now) => {
      const k = Math.min(1, (now - t0) / dur);
      el.textContent = fmt(target * (1 - Math.pow(1 - k, 3)));
      if (k < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  /* ---------- Scramble effect for section labels ---------- */
  const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+<>/';
  const scramble = (el) => {
    const node = [...el.childNodes].find((n) => n.nodeType === 3 && n.textContent.trim());
    if (!node || reduceMotion) return;
    const final = node.textContent;
    let frame = 0;
    const total = 22;
    const tick = () => {
      frame++;
      const done = Math.floor((frame / total) * final.length);
      node.textContent = final.split('').map((c, i) =>
        i < done || c === ' ' ? c : GLYPHS[(Math.random() * GLYPHS.length) | 0]).join('');
      if (frame < total) requestAnimationFrame(tick); else node.textContent = final;
    };
    requestAnimationFrame(tick);
  };

  /* ---------- Reveal on scroll + active nav ---------- */
  const revealables = $$('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const el = entry.target;
        el.classList.add('is-in');
        $$('[data-count]', el).forEach(countUp);
        $$('.eyebrow', el).forEach(scramble);
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
    revealables.forEach((el) => io.observe(el));

    const links = $$('[data-nav]');
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === '#' + entry.target.id));
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    links.forEach((a) => { const h = a.getAttribute('href'); const s = h.startsWith('#') ? $(h) : null; if (s) spy.observe(s); });
  } else {
    revealables.forEach((el) => el.classList.add('is-in'));
  }

  /* ---------- Typing terminal line ---------- */
  const typer = $('#typer');
  const phrases = ['a backend that scales', 'an Android app', 'an AI agent', 'a trading dashboard', 'payments & GST invoicing', 'a school ERP', 'a fast website'];
  if (typer && !reduceMotion) {
    let i = 0, j = phrases[0].length, deleting = true;
    const loop = () => {
      if (document.hidden) return setTimeout(loop, 600);
      const word = phrases[i];
      if (deleting) {
        j--;
        typer.textContent = word.slice(0, j);
        if (j === 0) { deleting = false; i = (i + 1) % phrases.length; return setTimeout(loop, 250); }
        return setTimeout(loop, 32);
      }
      const next = phrases[i];
      j++;
      typer.textContent = next.slice(0, j);
      if (j === next.length) { deleting = true; return setTimeout(loop, 1900); }
      setTimeout(loop, 55 + Math.random() * 45);
    };
    setTimeout(loop, 2600);
  }

  /* ---------- Mouse-only effects ---------- */
  if (finePointer && !reduceMotion) {
    // Spotlight + gentle 3D tilt on cards
    $$('.spot').forEach((card) => {
      const tilt = card.matches('.case, .service');
      card.addEventListener('pointermove', (e) => {
        const r = card.getBoundingClientRect();
        const x = e.clientX - r.left, y = e.clientY - r.top;
        card.style.setProperty('--mx', `${x}px`);
        card.style.setProperty('--my', `${y}px`);
        if (tilt && card.classList.contains('is-in')) {
          const rx = ((y / r.height) - 0.5) * -5;
          const ry = ((x / r.width) - 0.5) * 5;
          card.style.transform = `perspective(1000px) rotateX(${rx.toFixed(2)}deg) rotateY(${ry.toFixed(2)}deg) translateY(-4px)`;
        }
      }, { passive: true });
      if (tilt) card.addEventListener('pointerleave', () => { card.style.transform = ''; });
    });

    // Magnetic buttons
    $$('.btn--primary, .btn--ghost, .icon-btn, .badge, .totop').forEach((el) => {
      el.classList.add('magnetic');
      el.addEventListener('pointermove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2);
        const dy = e.clientY - (r.top + r.height / 2);
        el.style.transform = `translate(${(dx * 0.22).toFixed(1)}px, ${(dy * 0.3).toFixed(1)}px)`;
      }, { passive: true });
      el.addEventListener('pointerleave', () => { el.style.transform = ''; });
    });

    // Hero glows follow the mouse
    const heroBg = $('.hero__bg');
    const hero = $('.hero');
    if (hero && heroBg) hero.addEventListener('pointermove', (e) => {
      heroBg.style.setProperty('--px', ((e.clientX / innerWidth) - 0.5).toFixed(3));
      heroBg.style.setProperty('--py', ((e.clientY / innerHeight) - 0.5).toFixed(3));
    }, { passive: true });

    // Custom cursor: dot follows exactly, ring trails smoothly
    const cursor = $('.cursor');
    const dot = $('.cursor__dot');
    const ring = $('.cursor__ring');
    root.classList.add('has-cursor');
    cursor.classList.add('is-hidden');
    let mx = innerWidth / 2, my = innerHeight / 2, rx = mx, ry = my, raf = 0;
    const render = () => {
      rx += (mx - rx) * 0.18;
      ry += (my - ry) * 0.18;
      dot.style.transform = `translate(${mx}px, ${my}px)`;
      ring.style.transform = `translate(${rx}px, ${ry}px)`;
      raf = (Math.abs(mx - rx) > 0.1 || Math.abs(my - ry) > 0.1) ? requestAnimationFrame(render) : 0;
    };
    addEventListener('pointermove', (e) => {
      mx = e.clientX; my = e.clientY;
      cursor.classList.remove('is-hidden');
      const t = e.target;
      cursor.classList.toggle('is-text', !!t.closest('input, textarea'));
      cursor.classList.toggle('is-link', !t.closest('input, textarea') && !!t.closest('a, button, summary, label, .case'));
      if (!raf) raf = requestAnimationFrame(render);
    }, { passive: true });
    addEventListener('pointerdown', () => cursor.classList.add('is-down'));
    addEventListener('pointerup', () => cursor.classList.remove('is-down'));
    document.addEventListener('pointerleave', () => cursor.classList.add('is-hidden'));
  }

  /* ---------- Contact form ---------- */
  const form = $('#contactForm');
  if (form) {
    const status = $('#formStatus');
    const label = $('.form__label', form);
    const setStatus = (msg, cls) => { status.textContent = msg; status.className = 'form__status' + (cls ? ' ' + cls : ''); };
    const emailOk = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(form));
      if (data.website) return; // spam bot filled the hidden field
      const fields = { name: data.name.trim(), email: data.email.trim(), phone: (data.phone || '').trim(), message: data.message.trim() };
      let bad = null;
      $$('.field', form).forEach((f) => f.classList.remove('invalid'));
      if (!fields.name) bad = 'f-name';
      else if (!emailOk(fields.email)) bad = 'f-email';
      else if (fields.message.length < 5) bad = 'f-message';
      if (bad) {
        const input = $('#' + bad);
        input.parentElement.classList.add('invalid');
        input.focus();
        setStatus(bad === 'f-email' ? 'Please enter a valid email address.' : 'Please fill in this field.', 'err');
        return;
      }

      const endpoint = form.dataset.endpoint || LEAD_ENDPOINT;
      const payload = { ...fields, interest: data.interest || '', source: 'Contact form', page: location.href, sent: new Date().toISOString() };

      if (!endpoint) {
        // No sheet connected yet: open the visitor's email app with everything filled in.
        const body = `Hi Gajraj,\n\n${payload.message}\n\nInterested in: ${payload.interest}\n\n${payload.name}\n${payload.email}${payload.phone ? '\n' + payload.phone : ''}`;
        location.href = `mailto:contact@gajrajshekhawat.com?subject=${encodeURIComponent('Project enquiry from ' + payload.name)}&body=${encodeURIComponent(body)}`;
        setStatus('Your email app should open with the message ready. Just press send.', 'ok');
        return;
      }

      form.classList.add('is-sending');
      $('.form__submit', form).disabled = true;
      label.textContent = 'Sending…';
      setStatus('');
      try {
        await fetch(endpoint, { method: 'POST', mode: 'no-cors', body: new URLSearchParams(payload) });
        form.classList.remove('is-sending');
        form.classList.add('is-sent');
        label.textContent = 'Sent ✓';
        setStatus(`Thanks ${payload.name.split(' ')[0]}! Your message is with me, and I'll reply within a day.`, 'ok');
        form.reset();
        setTimeout(() => { form.classList.remove('is-sent'); label.textContent = 'Send message'; $('.form__submit', form).disabled = false; }, 6000);
      } catch (err) {
        form.classList.remove('is-sending');
        $('.form__submit', form).disabled = false;
        label.textContent = 'Send message';
        setStatus('Something went wrong. Please email contact@gajrajshekhawat.com or WhatsApp +91 94145 84444.', 'err');
      }
    });
  }

  /* ---------- "Show all projects" on small screens ---------- */
  const moreBtn = $('.cases__more');
  if (moreBtn) moreBtn.addEventListener('click', () => {
    const cases = $('.cases');
    const open = !cases.classList.contains('cases--all');
    cases.classList.toggle('cases--all', open);
    moreBtn.setAttribute('aria-expanded', String(open));
    moreBtn.firstChild.textContent = open ? 'Show fewer projects ' : moreBtn.dataset.label;
    moreBtn.lastElementChild.textContent = open ? '↑' : '↓';
    if (!open) $('#work').scrollIntoView();
  });
  if (moreBtn) moreBtn.dataset.label = moreBtn.firstChild.textContent;

  /* ---------- Chat assistant (scripted lead capture, on every page) ---------- */
  const initChat = () => {
    const AVATAR = '/images/avatar-96.webp';
    const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text != null) n.textContent = text; return n; };
    const emailOk = (v) => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);

    const launcher = el('button', 'chat-launch');
    launcher.type = 'button';
    launcher.setAttribute('aria-label', 'Chat with Gajraj');
    launcher.setAttribute('aria-expanded', 'false');
    launcher.innerHTML = '<span class="chat-launch__icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 5h16v11H8l-4 4z"/></svg></span><span class="chat-launch__text">Chat with Gajraj</span>';

    const nudge = el('button', 'chat-nudge');
    nudge.type = 'button';
    nudge.innerHTML = '<img src="' + AVATAR + '" alt="" width="28" height="28" /><span>Need a website, app or AI feature? Tell me in 1 minute →</span>';

    const panel = el('section', 'chat');
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', "Chat with Gajraj's assistant");
    panel.hidden = true;
    panel.innerHTML = `
      <header class="chat__head">
        <img src="${AVATAR}" alt="" width="40" height="40" />
        <div><p class="chat__name">Gajraj's assistant</p><p class="chat__status"><span class="dot"></span> Gajraj usually replies within a day</p></div>
        <button class="chat__close" type="button" aria-label="Close chat">×</button>
      </header>
      <div class="chat__log" aria-live="polite"></div>
      <div class="chat__input"></div>`;
    document.body.append(launcher, nudge, panel);
    const log = panel.querySelector('.chat__log');
    const inputArea = panel.querySelector('.chat__input');

    const lead = {};
    const OPTIONS = ['Website', 'Web or mobile app', 'Backend / API', 'AI feature', 'Tech advice', 'Something else'];
    // Always keep the newest message in view (also after the input area or keyboard resizes the panel).
    const scroll = () => requestAnimationFrame(() => { log.scrollTop = log.scrollHeight; });
    if ('ResizeObserver' in window) new ResizeObserver(scroll).observe(log);
    const say = (text, who = 'bot') => { const b = el('div', 'msg msg--' + who); b.textContent = text; log.append(b); scroll(); return b; };
    const typing = (ms = 600) => new Promise((res) => {
      const t = el('div', 'msg msg--bot msg--typing'); t.innerHTML = '<i></i><i></i><i></i>'; log.append(t); scroll();
      setTimeout(() => { t.remove(); res(); }, reduceMotion ? 0 : ms);
    });
    const bot = async (...lines) => { for (const l of lines) { await typing(); say(l); } };

    // Validation rules
    const V = {
      details: (v) => v.length < 10 ? 'Please add a few more words (at least 10 characters).' : '',
      name: (v) => !/^[\p{L}][\p{L} .'-]{1,59}$/u.test(v) ? 'Please enter your name using letters only (2–60 characters).' : '',
      email: (v) => /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)*\.[A-Za-z]{2,}$/.test(v) ? '' : 'Please enter a valid email, e.g. name@company.com',
      phone: (v) => {
        const digits = v.replace(/\D/g, '');
        if (/^[^+\d]/.test(v.trim()) || /[^\d\s()+-]/.test(v)) return 'Use digits only, e.g. +91 98765 43210';
        const indian = digits.replace(/^(91|0)(?=[6-9]\d{9}$)/, '');
        if (/^[6-9]\d{9}$/.test(indian)) return '';
        if (v.trim().startsWith('+') && digits.length >= 8 && digits.length <= 15) return '';
        if (/^\d{10}$/.test(digits)) return 'Indian mobile numbers start with 6, 7, 8 or 9.';
        return 'Enter a 10-digit Indian mobile, or an international number starting with + (8–15 digits).';
      },
      location: (v) => v.length > 80 ? 'Please keep it short, e.g. Dubai, UAE' : '',
    };
    const formatPhone = (v) => {
      const d = v.replace(/\D/g, '');
      const m = d.match(/^(?:91|0)?([6-9]\d{9})$/);
      return m ? `+91 ${m[1].slice(0, 5)} ${m[1].slice(5)}` : '+' + d;
    };

    const ask = ({ type = 'text', placeholder = '', optional = false, validate, multiline = false, inputmode, autocomplete }) => new Promise((resolve) => {
      inputArea.innerHTML = '';
      const form = el('form', 'chat__form');
      form.noValidate = true;
      const input = el(multiline ? 'textarea' : 'input', 'chat__field');
      if (!multiline) input.type = type;
      if (inputmode) input.inputMode = inputmode;
      if (autocomplete) input.autocomplete = autocomplete;
      input.placeholder = placeholder;
      input.setAttribute('aria-label', placeholder);
      if (multiline) input.rows = 2;
      const send = el('button', 'chat__send'); send.type = 'submit'; send.setAttribute('aria-label', 'Send');
      send.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12l16-8-6 16-2-6z"/></svg>';
      form.append(input, send);
      const err = el('p', 'chat__error'); err.setAttribute('role', 'alert');
      inputArea.append(form, err);
      if (optional) { const skip = el('button', 'chat__skip', 'Skip'); skip.type = 'button'; skip.onclick = () => { say('Skipped', 'me'); inputArea.innerHTML = ''; resolve(''); }; inputArea.append(skip); }
      input.addEventListener('input', () => { input.classList.remove('bad'); err.textContent = ''; });
      if (multiline) input.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit(); } });
      form.onsubmit = (e) => {
        e.preventDefault();
        const v = input.value.trim();
        if (!v && optional) { err.textContent = 'Type an answer or tap Skip.'; return; }
        const msg = !v ? 'Please type an answer.' : (validate ? validate(v) : '');
        if (msg) { input.classList.add('bad'); err.textContent = msg; input.focus(); scroll(); return; }
        say(v, 'me'); inputArea.innerHTML = ''; scroll(); resolve(v);
      };
      scroll();
      setTimeout(() => input.focus({ preventScroll: true }), 60);
    });
    const choose = (opts) => new Promise((resolve) => {
      inputArea.innerHTML = '';
      const wrap = el('div', 'chat__opts');
      opts.forEach((o) => { const b = el('button', 'chat__opt', o); b.type = 'button'; b.onclick = () => { say(o, 'me'); inputArea.innerHTML = ''; scroll(); resolve(o); }; wrap.append(b); });
      inputArea.append(wrap);
      scroll();
    });

    const summaryText = () =>
      `New enquiry via website chat\nInterested in: ${lead.interest}\nDetails: ${lead.details}\nName: ${lead.name}\nEmail: ${lead.email}\nPhone: ${lead.phone}` +
      (lead.location ? `\nLocation: ${lead.location}` : '');

    const finish = () => {
      inputArea.innerHTML = '';
      const row = el('div', 'chat__opts');
      const wa = el('a', 'chat__opt chat__opt--primary', 'WhatsApp Gajraj');
      wa.href = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(summaryText())}`; wa.target = '_blank'; wa.rel = 'noopener';
      const again = el('button', 'chat__opt', 'Send another message'); again.type = 'button';
      again.onclick = () => { log.innerHTML = ''; Object.keys(lead).forEach((k) => delete lead[k]); run(); };
      row.append(wa, again); inputArea.append(row); scroll();
    };

    const submit = async () => {
      const payload = { name: lead.name, email: lead.email, phone: lead.phone, location: lead.location || '', interest: lead.interest,
        message: lead.details, source: 'Website chat', page: location.href, sent: new Date().toISOString() };
      let ok = false;
      if (LEAD_ENDPOINT) {
        try { await fetch(LEAD_ENDPOINT, { method: 'POST', mode: 'no-cors', body: new URLSearchParams(payload) }); ok = true; } catch (e) { ok = false; }
      }
      if (ok) {
        await bot(`Thank you, ${lead.name.split(' ')[0]}! ✅ Your message has reached Gajraj.`,
          `He'll get back to you within a day on ${lead.email} or WhatsApp. If it's urgent, you can message him on WhatsApp right now.`);
      } else {
        await bot("Your details are ready, but the connection dropped. Please tap WhatsApp below to send them to Gajraj directly.");
      }
      finish();
    };

    let started = false;
    const run = async () => {
      started = true;
      await bot("Hi 👋 I'm Gajraj's assistant.", 'Gajraj is a full-stack software engineer: websites, web and mobile apps, backends, AI and data, for businesses worldwide. What would you like to build?');
      lead.interest = await choose(OPTIONS);
      await bot('Great choice! Tell me a little about it: what should it do, and is there a deadline?');
      lead.details = await ask({ placeholder: 'e.g. An app for my shop to take orders on WhatsApp…', multiline: true, validate: V.details });
      await bot("Thanks, that's helpful. What's your name?");
      lead.name = await ask({ placeholder: 'Your full name', autocomplete: 'name', validate: V.name });
      const first = lead.name.split(' ')[0];
      await bot(`Nice to meet you, ${first}! What's your email address?`);
      lead.email = await ask({ type: 'email', inputmode: 'email', autocomplete: 'email', placeholder: 'you@company.com', validate: V.email });
      await bot('And your mobile / WhatsApp number, so Gajraj can reach you quickly?');
      lead.phone = formatPhone(await ask({ type: 'tel', inputmode: 'tel', autocomplete: 'tel', placeholder: '+91 98765 43210', validate: V.phone }));
      await bot('Last one: where are you based? City and country is enough.');
      lead.location = await ask({ placeholder: 'e.g. Dubai, UAE', autocomplete: 'address-level2', optional: true, validate: V.location });
      await typing(400);
      const card = el('div', 'msg msg--bot msg--card');
      [['Interested in', lead.interest], ['Details', lead.details], ['Name', lead.name], ['Email', lead.email], ['Phone', lead.phone], ['Location', lead.location || '—']]
        .forEach(([k, v]) => { const r = el('p'); r.append(el('b', '', k + ': '), document.createTextNode(v)); card.append(r); });
      log.append(card); scroll();
      await submit();
    };

    const open = () => {
      panel.hidden = false; requestAnimationFrame(() => panel.classList.add('open')); root.classList.add('chat-open');
      launcher.setAttribute('aria-expanded', 'true'); launcher.classList.add('is-open'); nudge.classList.remove('show');
      try { sessionStorage.setItem('chatSeen', '1'); } catch (e) {}
      if (!started) run();
    };
    const close = () => {
      panel.classList.remove('open'); root.classList.remove('chat-open'); launcher.setAttribute('aria-expanded', 'false'); launcher.classList.remove('is-open');
      setTimeout(() => { panel.hidden = true; }, 250); launcher.focus();
    };
    launcher.onclick = () => (panel.hidden ? open() : close());
    nudge.onclick = open;
    const nudgeShown = () => root.classList.toggle('nudge-open', nudge.classList.contains('show'));
    new MutationObserver(nudgeShown).observe(nudge, { attributes: true, attributeFilter: ['class'] });
    panel.querySelector('.chat__close').onclick = close;
    panel.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    $$('a[href$="#chat"]').forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); open(); }));

    let seen = false;
    try { seen = sessionStorage.getItem('chatSeen') === '1'; } catch (e) {}
    if (!seen && !window.matchMedia('(max-width: 560px)').matches) setTimeout(() => { if (panel.hidden) { nudge.classList.add('show'); setTimeout(() => nudge.classList.remove('show'), 10000); } }, 15000);
  };
  if ('requestIdleCallback' in window) requestIdleCallback(initChat, { timeout: 2500 }); else setTimeout(initChat, 1200);

  const year = $('#year');
  if (year) year.textContent = new Date().getFullYear();
})();
