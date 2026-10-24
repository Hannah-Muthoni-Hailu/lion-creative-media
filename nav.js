// Lion Creative Media House: header behaviour and the demo enquiry form.
(function () {
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ----- Full-screen menu (tablet and phone) -----
     Opening fades in the overlay, then the links slide in one after another
     while the hamburger lines merge and rotate into an X (all in styles.css). */
  var STAGGER_MS = 90;
  var timers = [];
  var behind = [document.getElementById('main'), document.querySelector('.site-footer')];

  function clearTimers() {
    timers.forEach(clearTimeout);
    timers = [];
  }

  function setOpen(open) {
    if (!nav || !toggle) return;
    clearTimers();
    var links = nav.querySelectorAll('a');

    nav.classList.toggle('open', open);
    document.body.classList.toggle('menu-open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');

    // keep keyboard and screen-reader focus inside the menu while it covers the page
    behind.forEach(function (el) { if (el) el.inert = open; });

    Array.prototype.forEach.call(links, function (a, i) {
      if (!open) {
        a.classList.remove('visible');
      } else if (reduceMotion) {
        a.classList.add('visible');
      } else {
        timers.push(setTimeout(function () { a.classList.add('visible'); }, 80 + i * STAGGER_MS));
      }
    });
  }

  if (nav && toggle) {
    toggle.addEventListener('click', function () {
      setOpen(!nav.classList.contains('open'));
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) {
        setOpen(false);
        toggle.focus();
      }
    });
    window.addEventListener('resize', function () {
      if (window.innerWidth > 960 && nav.classList.contains('open')) setOpen(false);
    });
    // returning via the browser's back button can restore a page with the menu open
    window.addEventListener('pageshow', function () {
      if (nav.classList.contains('open')) setOpen(false);
    });
  }

  /* ----- Slim menu bar that pins to the top after the header scrolls away (desktop) ----- */
  if (header && nav) {
    var bar = document.createElement('div');
    bar.className = 'menu-fixed';
    bar.setAttribute('aria-hidden', 'true');
    bar.innerHTML = nav.innerHTML;
    Array.prototype.forEach.call(bar.querySelectorAll('a'), function (a) {
      a.setAttribute('tabindex', '-1');
      a.classList.remove('visible');
    });
    document.body.appendChild(bar);

    var ticking = false;
    function update() {
      ticking = false;
      bar.classList.toggle('visible', window.scrollY > header.offsetHeight);
    }
    window.addEventListener('scroll', function () {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(update);
      }
    }, { passive: true });
    update();
  }

  /* ----- Home hero: pictures crossfade automatically (no buttons) ----- */
  var slides = document.querySelectorAll('.hero-slides .hero-img');
  if (slides.length > 1) {
    var current = 0, leaving = null, SLIDE_MS = 6500;
    setInterval(function () {
      if (document.hidden) return; // pause while the tab is in the background
      if (leaving) leaving.classList.remove('is-leaving');
      leaving = slides[current];
      leaving.classList.remove('is-active');
      leaving.classList.add('is-leaving');
      current = (current + 1) % slides.length;
      slides[current].classList.add('is-active');
      slides[current].classList.remove('is-leaving');
    }, SLIDE_MS);
  }

  /* ----- Demo enquiry forms: confirm on screen, send nothing ----- */
  Array.prototype.forEach.call(document.querySelectorAll('form[data-demo-form]'), function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var sent = document.getElementById(form.getAttribute('data-sent'));
      form.hidden = true;
      if (sent) {
        sent.hidden = false;
        sent.focus();
      }
    });
  });
})();
