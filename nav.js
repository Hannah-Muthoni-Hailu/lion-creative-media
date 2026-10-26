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

  /* ----- Drop-down lists (Our Services, Our Projects) ----- */
  function closeSubs(except) {
    if (!nav) return;
    Array.prototype.forEach.call(nav.querySelectorAll('.nav-item.open'), function (item) {
      if (item === except) return;
      item.classList.remove('open');
      item.querySelector('.sub-toggle').setAttribute('aria-expanded', 'false');
    });
  }

  function setOpen(open) {
    if (!nav || !toggle) return;
    clearTimers();
    var links = nav.querySelectorAll(':scope > a, :scope > .nav-item');
    if (!open) closeSubs();

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
      var tog = e.target.closest('.sub-toggle');
      if (tog) { // the arrow next to a menu item opens or closes its list
        var item = tog.parentNode;
        var willOpen = !item.classList.contains('open');
        closeSubs(item);
        item.classList.toggle('open', willOpen);
        tog.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
        return;
      }
      if (e.target.closest('a')) setOpen(false);
    });
    // on desktop, clicking elsewhere closes a list that was opened with the arrow
    document.addEventListener('click', function (e) {
      if (!e.target.closest('.nav-item')) closeSubs();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        if (nav.classList.contains('open')) {
          setOpen(false);
          toggle.focus();
        } else if (nav.querySelector('.nav-item.open')) {
          closeSubs();
        } else if (document.activeElement && document.activeElement.closest('.sub') && document.activeElement.blur) {
          document.activeElement.blur(); // hides a list that is showing because of keyboard focus
        }
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
    });
    Array.prototype.forEach.call(bar.querySelectorAll('.sub-toggle'), function (b) { b.setAttribute('tabindex', '-1'); });
    Array.prototype.forEach.call(bar.children, function (el) { el.classList.remove('visible'); });
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
    var current = 0, leaving = null;
    var FIRST_MS = 1000, SLIDE_MS = 5000; // first change comes quickly, then a steady pace
    var advance = function () {
      if (!document.hidden) { // pause while the tab is in the background
        if (leaving) leaving.classList.remove('is-leaving');
        leaving = slides[current];
        leaving.classList.remove('is-active');
        leaving.classList.add('is-leaving');
        current = (current + 1) % slides.length;
        slides[current].classList.add('is-active');
        slides[current].classList.remove('is-leaving');
      }
      setTimeout(advance, SLIDE_MS);
    };
    setTimeout(advance, FIRST_MS);
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
