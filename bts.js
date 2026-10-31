// Lion Creative Media: Behind the Scenes page.
// Reads the list of Instagram reels from a Google Sheet published as CSV
// (the link sits in data-sheet on #reel-grid; see BTS-GUIDE.md) and shows each one as a card.
// A reel only loads from Instagram when a visitor taps it, which keeps the page fast.
(function () {
  var grid = document.getElementById('reel-grid');
  var empty = document.getElementById('reel-empty');
  if (!grid) return;

  var PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>';

  /* ----- CSV: handles quoted cells, commas and line breaks inside quotes ----- */
  function parseCSV(text) {
    var rows = [], row = [], cell = '', quoted = false, i, ch;
    text = text.replace(/^﻿/, '');
    for (i = 0; i < text.length; i++) {
      ch = text.charAt(i);
      if (quoted) {
        if (ch === '"' && text.charAt(i + 1) === '"') { cell += '"'; i++; }
        else if (ch === '"') quoted = false;
        else cell += ch;
      } else if (ch === '"') quoted = true;
      else if (ch === ',') { row.push(cell); cell = ''; }
      else if (ch === '\n' || ch === '\r') {
        if (ch === '\r' && text.charAt(i + 1) === '\n') i++;
        row.push(cell); cell = ''; rows.push(row); row = [];
      } else cell += ch;
    }
    if (cell !== '' || row.length) { row.push(cell); rows.push(row); }
    return rows.filter(function (r) { return r.some(function (c) { return c.trim() !== ''; }); });
  }

  /* ----- Turn the rows into reels: columns "url", "caption" (optional), "thumbnail" (optional) ----- */
  function toReels(rows) {
    if (!rows.length) return [];
    var head = rows[0].map(function (h) { return h.trim().toLowerCase(); });
    var hasHeader = head.some(function (h) { return h === 'url' || h === 'link' || h === 'reel' || h === 'caption'; });
    var col = function (names, fallback) {
      for (var k = 0; k < names.length; k++) { var ix = head.indexOf(names[k]); if (hasHeader && ix > -1) return ix; }
      return hasHeader ? -1 : fallback;
    };
    var u = col(['url', 'link', 'reel', 'reel link', 'instagram link'], 0);
    var c = col(['caption', 'title', 'description'], 1);
    var t = col(['thumbnail', 'image', 'cover'], 2);
    var out = [];
    rows.slice(hasHeader ? 1 : 0).forEach(function (r) {
      var url = (r[u] || '').trim();
      var m = url.match(/instagram\.com\/(?:[A-Za-z0-9_.]+\/)?(reel|reels|p|tv)\/([A-Za-z0-9_-]+)/i);
      if (!m) return;
      var kind = m[1].toLowerCase() === 'p' ? 'p' : 'reel';
      var thumb = c > -1 || t > -1 ? (t > -1 ? (r[t] || '').trim() : '') : '';
      out.push({
        embed: 'https://www.instagram.com/' + kind + '/' + m[2] + '/embed',
        link: 'https://www.instagram.com/' + kind + '/' + m[2] + '/',
        caption: c > -1 ? (r[c] || '').trim() : '',
        thumb: /^https:\/\//i.test(thumb) ? thumb : ''
      });
    });
    return out.reverse(); // new reels are added at the bottom of the sheet; show the newest first
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }

  function card(reel, index) {
    var art = el('article', 'reel');
    var frame = el('div', 'reel-frame');
    var label = reel.caption ? 'Play reel: ' + reel.caption : 'Play reel ' + (index + 1);

    var btn = el('button', 'reel-play');
    btn.type = 'button';
    btn.setAttribute('aria-label', label);
    if (reel.thumb) {
      var img = el('img');
      img.src = reel.thumb; img.alt = ''; img.loading = 'lazy';
      btn.appendChild(img);
    }
    var badge = el('span', 'reel-badge');
    badge.innerHTML = PLAY;
    btn.appendChild(badge);
    btn.appendChild(el('span', 'reel-hint', 'Tap to play'));
    btn.addEventListener('click', function () {
      var f = el('iframe');
      f.src = reel.embed;
      f.title = reel.caption || 'Instagram reel';
      f.setAttribute('allowfullscreen', '');
      f.setAttribute('allow', 'autoplay; encrypted-media; fullscreen; picture-in-picture');
      f.setAttribute('scrolling', 'no');
      frame.replaceChild(f, btn);
    });
    frame.appendChild(btn);
    art.appendChild(frame);

    var meta = el('div', 'reel-meta');
    if (reel.caption) meta.appendChild(el('p', 'reel-caption', reel.caption));
    var a = el('a', 'link', 'Watch on Instagram');
    a.href = reel.link; a.target = '_blank'; a.rel = 'noopener';
    meta.appendChild(a);
    art.appendChild(meta);
    return art;
  }

  function show(reels) {
    grid.innerHTML = '';
    if (!reels.length) { if (empty) empty.hidden = false; return; }
    if (empty) empty.hidden = true;
    reels.forEach(function (r, i) { grid.appendChild(card(r, i)); });
  }

  // Instagram tells the embedded player how tall it needs to be; match it so nothing is cut off
  window.addEventListener('message', function (e) {
    if (e.origin !== 'https://www.instagram.com') return;
    var data;
    try { data = typeof e.data === 'string' ? JSON.parse(e.data) : e.data; } catch (err) { return; }
    if (!data || data.type !== 'MEASURE' || !data.details || !data.details.height) return;
    Array.prototype.forEach.call(grid.querySelectorAll('iframe'), function (f) {
      if (f.contentWindow === e.source) {
        f.parentNode.classList.add('is-sized');
        f.style.height = data.details.height + 'px';
      }
    });
  });

  var sheet = (grid.getAttribute('data-sheet') || '').trim();
  if (!sheet) { show([]); return; }
  fetch(sheet, { cache: 'no-cache' })
    .then(function (res) { if (!res.ok) throw new Error('sheet ' + res.status); return res.text(); })
    .then(function (text) { show(toReels(parseCSV(text))); })
    .catch(function () { show([]); });
})();
