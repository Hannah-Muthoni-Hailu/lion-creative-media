# Lion Creative Media House: proof-of-concept website

A plain static site (HTML, one stylesheet, one small script, images). No build step and no dependencies.

Open `index.html` in a browser to view it locally.

## Structure
Layout follows a banded editorial pattern: centred logo header with a centred menu, a slim menu bar that pins to the top after scrolling, a 1,200px content column, full-width bands alternating black and charcoal, serif headings and quiet underlined text links. Palette is black, gold (`#E0A526`) and white.

| Page | Purpose |
| --- | --- |
| `index.html` | Home: intro, image pair, service blocks, philosophy and founder, working principles, testimonials, enquiry form |
| `portfolio.html` | Hero image and a list of portfolio categories |
| `portfolio-*.html`, `weddings.html` | One page per category (weddings has its own page and menu link) |
| `journal.html`, `article.html` | Journal list and one sample article |
| `services.html` | Six service cards, booking and delivery notes |
| `testimonials.html` | Client reviews |
| `contact.html` | Contact details and enquiry form |

Shared files: `styles.css` (all styling, including the tablet and phone layouts) and `nav.js` (hamburger menu, pinned menu bar, demo form confirmation).

## Host it
- **GitHub Pages:** Settings > Pages > Deploy from branch > main / (root).
- **Netlify Drop:** drag this folder onto https://app.netlify.com/drop for an instant link.

## Notes
- Testimonials, Journal articles and the WhatsApp number (+254 XXX XXX XXX) are samples/placeholders.
- The "Booking & Payment" and "Delivery & Finishing" wording on the Services page is placeholder text to be replaced with real terms.
- The enquiry forms only show a confirmation message; they do not send anything yet.
- Only four photos exist so far (`wedding`, `portrait-bw`, `portrait-red`, `lipstick`). Category pages and the wedding page reuse them, and the `images/*.svg` illustrations stand in until real photos are supplied.
- Fonts (Cormorant Garamond, Ubuntu, Big Shoulders Display) load from Google Fonts, so the site needs an internet connection to show them correctly.
- `about.html` was folded into the home page ("Meet Joseph Kyuli") and `our-stories.html` became `journal.html`.
