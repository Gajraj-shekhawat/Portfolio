// The 'js' class is set inline in <head>, so animated content never flashes before this runs.
(() => {
  const root = document.documentElement;
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Theme toggle: remembers your choice, otherwise follows the system */
  document.getElementById('themeToggle').addEventListener('click', () => {
    const current = root.dataset.theme ||
      (matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
    const next = current === 'light' ? 'dark' : 'light';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) {}
  });

  /* Mobile menu */
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');
  const setMenu = (open) => {
    navLinks.classList.toggle('open', open);
    navToggle.setAttribute('aria-expanded', String(open));
    navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  };
  navToggle.addEventListener('click', () => setMenu(!navLinks.classList.contains('open')));
  navLinks.addEventListener('click', (e) => { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') setMenu(false); });

  /* Scroll progress bar + nav border (one rAF per frame) */
  const nav = document.querySelector('.nav');
  const bar = document.getElementById('progressBar');
  let ticking = false;
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const max = document.documentElement.scrollHeight - innerHeight;
      bar.style.setProperty('--p', max > 0 ? (scrollY / max).toFixed(4) : 0);
      nav.classList.toggle('is-scrolled', scrollY > 8);
      ticking = false;
    });
  };
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* Count-up numbers */
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

  /* Reveal on scroll */
  const revealables = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-in');
        entry.target.querySelectorAll('[data-count]').forEach(countUp);
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
    revealables.forEach((el) => io.observe(el));

    /* Highlight the nav link of the section on screen */
    const links = [...document.querySelectorAll('[data-nav]')];
    const spy = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === '#' + entry.target.id));
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    links.forEach((a) => { const s = document.querySelector(a.getAttribute('href')); if (s) spy.observe(s); });
  } else {
    revealables.forEach((el) => el.classList.add('is-in'));
  }

  /* Spotlight that follows the cursor on cards (mouse only) */
  if (matchMedia('(hover: hover) and (pointer: fine)').matches) {
    document.querySelectorAll('.spot').forEach((card) => {
      card.addEventListener('pointermove', (e) => {
        const r = card.getBoundingClientRect();
        card.style.setProperty('--mx', `${e.clientX - r.left}px`);
        card.style.setProperty('--my', `${e.clientY - r.top}px`);
      }, { passive: true });
    });
  }

  /* Rotating word in the hero */
  const word = document.getElementById('rotator');
  const phrases = ['a backend that scales', 'an Android app', 'an AI feature', 'a fast website', 'payments and invoicing', 'a dashboard'];
  if (word && !reduceMotion) {
    let i = 0;
    setInterval(() => {
      if (document.hidden) return;
      word.classList.add('out');
      setTimeout(() => {
        i = (i + 1) % phrases.length;
        word.textContent = phrases[i];
        word.classList.remove('out');
        word.classList.add('in');
        void word.offsetWidth; // restart transition
        word.classList.remove('in');
      }, 450);
    }, 2600);
  }

  document.getElementById('year').textContent = new Date().getFullYear();
})();
