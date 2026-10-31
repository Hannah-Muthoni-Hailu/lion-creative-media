# Lion Creative Media: proof-of-concept website

A plain static site (HTML, one stylesheet, one small script, images). No build step and no dependencies.

Open `index.html` in a browser to view it locally.

## Structure
Layout follows a banded editorial pattern: a white header (logo top left, a gold call button top right, the menu centred beneath), a slim menu bar that pins to the top after scrolling on desktop, a full-width hero on the home page, a 1,200px content column, and full-width bands alternating black and charcoal with serif headings and quiet underlined text links. Palette is black, gold (`#E0A526`) and white.

Menu order: Home, About Us, Our Services, Photography/Videography, Insights, Our Projects, Contact Us.

| Page | Menu item |
| --- | --- |
| `index.html` | Home: hero ("No. 1 Videography & Photography Creative Experts"), welcome line, Our Services, founder, working principles, testimonials, enquiry form |
| `about.html` | About Us |
| `services.html` | Our Services |
| `photography-videography.html` | Photography/Videography |
| `journal.html`, `article.html` | Insights (list and one sample article) |
| `portfolio.html`, `portfolio-*.html`, `weddings.html` | Our Projects (category list and one page per category) |
| `contact.html` | Contact Us |
| `testimonials.html` | Not in the menu; linked from the home page and footer |

Shared files: `styles.css` (all styling, including the tablet and phone layouts), `nav.js` (full-screen mobile menu, pinned menu bar, demo form confirmation) and `images/logo.png` (the site logo, a transparent PNG with black lettering, so it needs the white header).

On tablet and phone the header becomes a sticky bar (logo, call button, hamburger). The hamburger opens a full-screen menu whose links slide in one after another while the icon turns into an X.

## Host it
- **GitHub Pages:** Settings > Pages > Deploy from branch > main / (root).
- **Netlify Drop:** drag this folder onto https://app.netlify.com/drop for an instant link.

## Notes
- Testimonials, Insights articles and the founder illustration are samples/placeholders.
- The call button and every "Call us" link use `tel:+254742552019` (0742552019). WhatsApp links are not set up yet.
- The home-page hero uses `images/wedding.jpg`; swap `src` on the `.hero-img` in `index.html` to change it.
- The "Booking & Payment" and "Delivery & Finishing" wording on the Services page is placeholder text to be replaced with real terms.
- The enquiry forms only show a confirmation message; they do not send anything yet.
- Only four photos exist so far (`wedding`, `portrait-bw`, `portrait-red`, `lipstick`). Category pages and the wedding page reuse them, and the `images/*.svg` illustrations stand in until real photos are supplied.
- Fonts (Cormorant Garamond, Ubuntu, Big Shoulders Display) load from Google Fonts, so the site needs an internet connection to show them correctly.
- `our-stories.html` became `journal.html` (menu label "Insights"); the old Portfolio page is now labelled "Our Projects".

## Home page carousel and service cards

- The hero crossfades through `images/hero-1.jpg` to `hero-5.jpg` every 5 seconds (the first change after 1) (`nav.js`, no buttons). To change the pictures, replace those files or edit the `<img class="hero-img">` list in `index.html`; at least two images are needed.
- The six service cards on the home page link to `services.html#photography`, `#video`, `#weddings-events`, `#editing`, `#branding` and `#production`. Their pictures are `images/svc-*.jpg`.

## Drop-down menus

Our Services (the six services) and Our Projects (the six project categories) open a list on hover or keyboard focus on desktop, and with the small arrow on touch screens and in the phone menu. The lists are generated from `SUBMENUS` in the page generator; to edit them by hand, change the `<ul class="sub">` in each page's header.

## Content structure (from the client's notes)

Services are four divisions: Commercial & Brand Production, Events & Corporate Coverage, People & Professional Photography, and Post-production & Specialised Production (`services.html#commercial-brand`, `#events-corporate`, `#people-photography`, `#post-production`). The Services page also carries the ten-step production workflow (`#workflow`); About carries the five differentiators, the team structure and the three standards. Internal notes in the brief (such as which division drives growth or cash flow) are deliberately not published.

## Behind the Scenes (BTS)

`bts.html` + `bts.js` show Instagram reels listed in a published Google Sheet. See `BTS-GUIDE.md` for how the owner adds reels and how to connect the sheet. `photography-videography.html` now sits under Our Projects.
