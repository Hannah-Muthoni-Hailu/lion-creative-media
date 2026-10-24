# Lion Creative Media House: proof-of-concept website

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
