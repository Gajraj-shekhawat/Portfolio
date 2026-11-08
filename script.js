// The 'js' class is set inline in <head>, so animated content never flashes before this runs.
(() => {
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
      toTop.style.setProperty('--p', p.toFixed(4));
      toTop.classList.toggle('show', scrollY > innerHeight * 0.8);
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
    links.forEach((a) => { const s = $(a.getAttribute('href')); if (s) spy.observe(s); });
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
    hero.addEventListener('pointermove', (e) => {
      heroBg.style.setProperty('--px', ((e.clientX / innerWidth) - 0.5).toFixed(3));
      heroBg.style.setProperty('--py', ((e.clientY / innerHeight) - 0.5).toFixed(3));
    }, { passive: true });

    // Custom cursor: dot follows exactly, ring trails smoothly
    const cursor = $('.cursor');
    const dot = $('.cursor__dot');
    const ring = $('.cursor__ring');
    root.classList.add('has-cursor');
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
      const fields = { name: data.name.trim(), email: data.email.trim(), message: data.message.trim() };
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

      const endpoint = form.dataset.endpoint;
      const payload = { ...fields, interest: data.interest || '', page: location.href, sent: new Date().toISOString() };

      if (!endpoint) {
        // No sheet connected yet: open the visitor's email app with everything filled in.
        const body = `Hi Gajraj,\n\n${payload.message}\n\nInterested in: ${payload.interest}\n\n${payload.name}\n${payload.email}`;
        location.href = `mailto:gaju2gajraj@gmail.com?subject=${encodeURIComponent('Project enquiry from ' + payload.name)}&body=${encodeURIComponent(body)}`;
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
        setStatus('Something went wrong. Please email gaju2gajraj@gmail.com or WhatsApp +91 94145 84444.', 'err');
      }
    });
  }

  $('#year').textContent = new Date().getFullYear();
})();
