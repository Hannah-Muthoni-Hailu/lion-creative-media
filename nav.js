// Lion Creative Media House: header behaviour and the demo enquiry form.
(function () {
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');

  /* ----- Hamburger menu (tablet and phone) ----- */
  function setOpen(open) {
    if (!nav || !toggle) return;
    nav.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
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
      if (window.innerWidth > 960) setOpen(false);
    });
  }

  /* ----- Slim menu bar that pins to the top after the header scrolls away ----- */
  if (header && nav) {
    var bar = document.createElement('div');
    bar.className = 'menu-fixed';
    bar.setAttribute('aria-hidden', 'true');
    bar.innerHTML = nav.innerHTML;
    Array.prototype.forEach.call(bar.querySelectorAll('a'), function (a) {
      a.setAttribute('tabindex', '-1');
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
