#!/usr/bin/env python3
"""Site generator for Lion Creative Media.

Writes every HTML page, one page per blog post (from content/posts/*.md),
sitemap.xml and robots.txt. Run from anywhere:  python3 tools/build_site.py
A GitHub Action runs it automatically whenever a post is saved in the CMS.
"""
import sys, pathlib, re, html as htmllib, datetime, json, os

import markdown
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT

# The public address of the site, no trailing slash. Used for canonical links,
# social-share previews and the sitemap. CHANGE THIS when a custom domain is connected.
SITE_URL = 'https://hannah-muthoni-hailu.github.io/lion-creative-media'
SITE_NAME = 'Lion Creative Media'
DEFAULT_SHARE_IMAGE = 'images/hero-1.jpg'

NAV = [
    ('index.html', 'Home'),
    ('about.html', 'About Us'),
    ('services.html', 'Our Services'),
    ('bts.html', 'BTS'),
    ('journal.html', 'Insights'),
    ('portfolio.html', 'Our Projects'),
    ('contact.html', 'Contact Us'),
]

PHONE = '0742552019'
TEL = '+254742552019'

# --- portfolio categories: (slug page, title, image, object-position, alt, blurb) ---
CATS = [
    ('weddings.html', 'Weddings', 'images/wedding.jpg', 'center', 'A couple holding hands at a wedding ceremony in front of a white floral arch',
     'The vows, up close.'),
    ('portfolio-portraits.html', 'Portraits', 'images/portrait-bw.jpg', 'center 30%', 'Black and white studio portrait of a woman with braided, curly hair',
     'Quiet light, in black and white. Studio and personal-branding portraits shaped around who you are.'),
    ('portfolio-fashion-editorial.html', 'Fashion &amp; Editorial', 'images/portrait-red.jpg', 'center 25%', 'Woman in a black blazer and red jumpsuit smiling in a studio portrait',
     'Red, black and confident. Styled shoots and editorial work with a clear point of view.'),
    ('portfolio-product-advertising.html', 'Product &amp; Advertising', 'images/lipstick.jpg', 'center', 'Two lipsticks displayed on seashells against a brown backdrop',
     'Beauty on shell. Product photography built on light, texture and styling that help things sell.'),
    ('portfolio-events.html', 'Events', 'images/cat-events.jpg', 'center 60%', 'A banquet hall set with red-clothed round tables facing a stage',
     'Live, loud and lit. Launches, conferences and celebrations, covered from the first guest to the last.'),
    ('portfolio-corporate-commercial.html', 'Corporate &amp; Commercial', 'images/cat-corporate.jpg', 'center', 'Aerial view of a courtyard building surrounded by trees and lawns',
     'Leadership portraits, team headshots and brand campaigns for businesses that want to look the part.'),
]

PHONE_ICON = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M6.62 10.79a15.05 15.05 0 0 0 6.59 6.59l2.2-2.2'
              'a1 1 0 0 1 1.02-.24c1.12.37 2.33.57 3.57.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1C10.61 21 3 13.39 3 4a1 1 0 0 1 1-1h3.5'
              'a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1.02l-2.2 2.2z"/></svg>')

from PIL import Image
LOGO_W, LOGO_H = Image.open(OUT / 'images' / 'logo.png').size


def abs_url(path):
    return f"{SITE_URL}/{path.lstrip('/')}" if path else SITE_URL + '/'


def seo_tags(fname, title, desc, share_image=None, kind='website', extra=''):
    url = abs_url('' if fname == 'index.html' else fname)
    img = abs_url(share_image or DEFAULT_SHARE_IMAGE)
    return f'''<link rel="canonical" href="{url}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:type" content="{kind}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
{extra}'''


def head(title, desc, fname='index.html', share_image=None, kind='website', extra=''):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#171717">
{seo_tags(fname, title, desc, share_image, kind, extra)}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@800;900&amp;family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400;1,500&amp;family=Ubuntu:wght@300;400;700&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css?v=11">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
'''


CHEVRON = '<svg viewBox="0 0 12 12" width="11" height="11" aria-hidden="true" focusable="false"><path d="M2 4.2l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'

# drop-down lists: parent page -> [(href, label)]
import html as _html

SERVICE_LIST = [
    dict(slug='commercial-photography', title='Commercial Photography', img='images/svc-photography.jpg', pos='center 30%',
         alt='A man in a white and leopard-print cape crouching in the street holding a spear',
         short='Professional images that help your business look its best online and in print.',
         lede='Professional photography that helps your business look its best across your website, social media, brochures and adverts.',
         items=['Business and brand photography', 'Food, hospitality and real-estate visuals', 'Social-media campaign photos', 'Images prepared for web, social and print']),
    dict(slug='product-photography', title='Product Photography', img='images/lipstick.jpg', pos='center',
         alt='Two lipsticks displayed on seashells against a brown backdrop',
         short='Clean, eye-catching product photos that make people want to buy.',
         lede='Clean, eye-catching product photos that make people want to buy, made with careful lighting and styling.',
         items=['Product photography', 'Product commercials', 'Photos for online shops and social media', 'Images prepared for web, social and print']),
    dict(slug='videography-brand-films', title='Videography & Brand Films', img='images/svc-video.jpg', pos='50% 35%',
         alt='A videographer filming with a camera on a handheld gimbal',
         short='Company profiles, brand films and adverts that tell your story.',
         lede='Company profile videos, brand films and adverts that explain who you are and why customers should choose you.',
         items=['Company profile videos', 'Brand films and promotional videos', 'Social-media campaign production', 'Customer testimonials and case studies']),
    dict(slug='event-coverage', title='Event Coverage', img='images/cat-events.jpg', pos='center 60%',
         alt='A banquet hall set with red-clothed round tables facing a stage',
         short='Weddings, birthdays, conferences and launches, covered from start to finish.',
         lede='We cover your event from start to finish, so you can enjoy it and still keep every moment, from weddings and birthdays to conferences and launches.',
         items=['Weddings and private events', 'Birthdays and celebrations', 'Corporate events and conferences', 'Product launches and exhibitions', 'Award ceremonies and graduations', 'Event highlight films', 'Same-day edits and photography']),
    dict(slug='portrait-photography', title='Portrait Photography', img='images/blog-headshots.jpg', pos='center 25%',
         alt='A smiling man in a light blue robe speaking at a microphone',
         short='Confident headshots and portraits for individuals, executives and teams.',
         lede='Confident, natural portraits for individuals, executives and whole teams, made at a location that suits you.',
         items=['Corporate headshots', 'Executive portraits', 'Personal branding', 'Staff and team photography', 'Family and milestone portraits']),
    dict(slug='maternity-photoshoot', title='Maternity Photoshoot', img='images/svc-maternity.jpg', pos='center 40%',
         alt='An expectant mother resting on a cloud of peach tulle in a maternity portrait',
         short='Relaxed, beautiful portraits that celebrate this special time.',
         lede='Relaxed, beautiful portraits that celebrate this special time, planned around your comfort and your style.',
         items=['Maternity photoshoots', 'Family portraits', 'Milestone portraits']),
    dict(slug='video-editing-post-production', title='Video Editing & Post Production', img='images/svc-editing.jpg', pos='center 30%',
         alt='A groom in a white tuxedo holding a bride in a beaded lace gown',
         short='Cutting, colour, sound and motion graphics that polish your footage.',
         lede='We turn raw footage into a polished film, with careful cutting, colour, sound and motion graphics.',
         items=['Professional video editing', 'Colour grading and sound design', 'Motion graphics', 'Animation and visual explainers']),
    dict(slug='drone-podcast-livestream', title='Drone, Podcast & Livestream', img='images/svc-drone.jpg', pos='center',
         alt='An aerial view of a road winding past houses and fields',
         short='Aerial shots, podcast filming and live broadcasts.',
         lede='Aerial photography and video, podcast filming and live broadcasting for events, shows and businesses.',
         items=['Drone photography and videography', 'Podcast filming', 'Livestream production']),
]
esc = _html.escape

SUBMENUS = {
    'services.html': [(f"service-{v['slug']}.html", esc(v['title']), esc(v['short'])) for v in SERVICE_LIST],
    'portfolio.html': [
        ('weddings.html', 'Weddings', 'The vows, up close: ceremonies, portraits and celebrations.'),
        ('portfolio-portraits.html', 'Portraits', 'Quiet light, in black and white. Portraits shaped around who you are.'),
        ('portfolio-fashion-editorial.html', 'Fashion &amp; Editorial', 'Styled shoots and editorial work with a clear point of view.'),
        ('portfolio-product-advertising.html', 'Product &amp; Advertising', 'Product photography built on light, texture and styling.'),
        ('portfolio-events.html', 'Events', 'Launches, conferences and celebrations, from the first guest to the last.'),
        ('portfolio-corporate-commercial.html', 'Corporate &amp; Commercial', 'Leadership portraits, team headshots and brand campaigns.'),
        ('photography-videography.html', 'Photography/Videography', 'Stills and motion from one creative team.'),
    ],
}

SOCIAL = [
    ('Instagram', '<rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.3" cy="6.7" r="1.2" fill="currentColor"/>'),
    ('X', '<path d="M17.8 3h3.1l-6.8 7.7L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.3-8.3L2 3h6.4l4.4 5.8L17.8 3zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5z" fill="currentColor"/>'),
    ('Facebook', '<path d="M13.5 22v-8.2h2.8l.5-3.3h-3.3V8.4c0-.9.4-1.7 1.8-1.7h1.6V3.8c-.3 0-1.3-.2-2.4-.2-2.4 0-4 1.5-4 4.1v2.8H7.6v3.3h2.9V22h3z" fill="currentColor"/>'),
]
# links will be provided later: "#" keeps the icons inert until then
SOCIAL_LINKS = {'Instagram': '#', 'X': '#', 'Facebook': '#'}


def social_icons():
    return ''.join(
        f'<a class="social-link" href="{SOCIAL_LINKS[n]}" aria-label="{n}" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">{p}</svg></a>'
        for n, p in SOCIAL)


def header(active):
    items = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ''
        if href in SUBMENUS:
            subs = ''.join(f'<li><a href="{h}"><span class="sub-title">{l}</span><span class="sub-desc">{d}</span></a></li>' for h, l, d in SUBMENUS[href])
            side = ' sub--left' if href == 'portfolio.html' else ''
            items.append(
                f'<div class="nav-item has-sub"><a href="{href}"{cur}>{label}</a>'
                f'<button type="button" class="sub-toggle" aria-expanded="false" aria-label="Show {label} list">{CHEVRON}</button>'
                f'<ul class="sub{side}">{subs}</ul></div>')
        else:
            items.append(f'<a href="{href}"{cur}>{label}</a>')
    links = '\n'.join(items)
    return f'''<header class="site-header">
<div class="header-top">
<a class="logo" href="index.html" aria-label="Lion Creative Media home"><img src="images/logo.png" alt="Lion Creative Media" width="{LOGO_W}" height="{LOGO_H}"></a>
<div class="header-social" aria-label="Social media">{social_icons()}</div>
<a class="call-btn" href="tel:{TEL}" aria-label="Call {PHONE}">{PHONE_ICON}<span>{PHONE}</span></a>
<button type="button" class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="site-nav"><span class="nav-toggle-icon" aria-hidden="true"><span class="nav-bar nav-bar--top"><i></i></span><span class="nav-bar nav-bar--middle"><i></i></span><span class="nav-bar nav-bar--bottom"><i></i></span></span></button>
</div>
<nav id="site-nav" class="site-nav" aria-label="Main">
{links}
<a class="nav-extra" href="tel:{TEL}">{PHONE_ICON}<span><b class="ne-call">Call </b>{PHONE}</span></a>
<div class="nav-social" aria-label="Social media">{social_icons()}</div>
</nav>
</header>
<main id="main">
'''


def footer():
    return f'''</main>
<footer class="site-footer">
<div class="wrap">
<p class="footer-links"><a href="contact.html">Contact Us</a><a href="services.html">Our Services</a><a href="portfolio.html">Our Projects</a><a href="testimonials.html">Testimonials</a></p>
<p class="copy">Nairobi, Kenya &middot; Available for assignments outside the city &middot; Call <a href="tel:{TEL}">{PHONE}</a></p>
<p class="tagline">ROAR LOUDER.</p>
<p class="copy">&copy; 2026 Lion Creative Media. All rights reserved.</p>
</div>
</footer>
<script src="nav.js?v=11"></script>
</body>
</html>
'''


def enquiry_band(form_id='home', alt=False):
    """Two-column contact band: copy on the left, underline-style form on the right."""
    return f'''<section class="band band--tall{' band--alt' if alt else ''}" id="enquire">
<div class="wrap grid-2">
<div class="contact-copy">
<h2>Let&rsquo;s make something fearless.</h2>
<p>Tell us what you&rsquo;re planning, whether it&rsquo;s a product shoot, brand film, corporate event, headshot session or campaign. We reply within one business day.</p>
<p>We&rsquo;ll help turn the idea into a visual experience worth remembering.</p>
<p>Nairobi, Kenya &middot; Available for assignments outside the city</p>
<p><a class="link" href="tel:+254742552019">Call us</a> &middot; {PHONE}</p>
<p class="tagline" style="margin-top:22px">ROAR LOUDER.</p>
</div>
<div>
<form class="enquiry" id="form-{form_id}" data-demo-form data-sent="sent-{form_id}">
<label class="sr-only" for="{form_id}-name">Your name</label>
<input class="field" id="{form_id}-name" name="name" type="text" placeholder="Your name" autocomplete="name" required>
<label class="sr-only" for="{form_id}-contact">Phone or email</label>
<input class="field" id="{form_id}-contact" name="contact" type="text" placeholder="Phone or email" autocomplete="email" required>
<label class="sr-only" for="{form_id}-msg">Your project</label>
<textarea class="field" id="{form_id}-msg" name="message" placeholder="Tell us your date, location and project idea"></textarea>
<button class="btn" type="submit">Send enquiry</button>
</form>
<div class="form-sent" id="sent-{form_id}" tabindex="-1" hidden>
<h3>Message sent.</h3>
<p>Thank you for reaching out. We will get back to you soon to talk through your idea.</p>
<p class="note">Demo form: nothing is actually sent yet.</p>
</div>
</div>
</div>
</section>
'''


PAGES = []   # every page written, for the sitemap: (file name, last-modified date or None)


def page(fname, title, desc, active, body, share_image=None, kind='website', extra='', lastmod=None, sitemap=True):
    html = head(title, desc, fname, share_image, kind, extra) + header(active) + body + footer()
    (OUT / fname).write_text(html, encoding='utf-8')
    if sitemap:
        PAGES.append((fname, lastmod))


def cta_band(heading, label='Book a shoot', href='contact.html', alt=True):
    return f'''<section class="band band--tall{' band--alt' if alt else ''}">
<div class="wrap">
<h2>{heading}</h2>
<p class="links"><a class="link" href="{href}">{label}</a><a class="link" href="tel:+254742552019">Call us</a></p>
</div>
</section>
'''


# =====================================================================
# HOME
# =====================================================================
ARROW = '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
svc_cards = ''
for v in SERVICE_LIST:
    svc_cards += f'''<a class="svc-card" href="service-{v['slug']}.html">
<span class="svc-media"><img src="{v['img']}" alt="{esc(v['alt'])}" loading="lazy" style="object-position:{v['pos']}"></span>
<span class="svc-body">
<h3>{esc(v['title'])}</h3>
<p>{esc(v['short'])}</p>
<span class="svc-more">Learn more {ARROW}</span>
</span>
</a>
'''

home = '''<section class="hero" aria-label="Featured work">
<div class="hero-slides" aria-hidden="true">
<img class="hero-img is-active" src="images/hero-1.jpg" alt="" fetchpriority="high" style="object-position:50% 40%">
<img class="hero-img" src="images/hero-2.jpg" alt="" style="object-position:60% 30%">
<img class="hero-img" src="images/hero-3.jpg" alt="" style="object-position:50% 40%">
<img class="hero-img" src="images/hero-4.jpg" alt="" style="object-position:50% 50%">
<img class="hero-img" src="images/hero-5.jpg" alt="" style="object-position:50% 45%">
</div>
<div class="wrap hero-inner">
<p class="hero-kicker">Commercial Photography &bull; Film &bull; Creative Production</p>
<h1><span class="gold">No. 1</span> Videography &amp; Photography<br class="hero-br"> Experts</h1>
<a class="btn-fill" href="services.html">Explore Our Services</a>
</div>
</section>

<section class="band welcome">
<div class="wrap">
<div class="welcome-inner">
<span class="rule" aria-hidden="true"></span>
<h2>Welcome to Lion Creative Media</h2>
<p>We help businesses communicate their value through powerful visuals, professional production and purposeful storytelling.</p>
<p>Lion Creative Media is a Nairobi-based commercial photography, film and creative production company. From product shoots and brand films to events, portraits and post-production, we bring creative thinking and professional execution to every project.</p>
<p class="links links--center"><a class="link" href="about.html">About us</a><a class="link" href="portfolio.html">Our projects</a></p>
</div>
</div>
</section>

<section class="band band--services" id="services">
<div class="wrap">
<header class="section-head">
<span class="eyebrow">What we do</span>
<h2 class="band-title">Our Services</h2>
<span class="rule" aria-hidden="true"></span>
<p>Photography, film and creative production, all under one roof. Choose a service to see what is included.</p>
</header>
<div class="svc-grid svc-grid--eight">
{svc_cards}</div>
<p class="links links--center"><a class="link" href="services.html">View all services</a></p>
</div>
</section>

<section class="band band--tall">
<div class="wrap statement statement--center">
<h2>More than a picture. A pride of ideas.</h2>
<p>We make images and films that carry emotion, personality and purpose. Arrive with a full concept or just a spark and we will build the creative direction, lighting, locations and visual language around it. The bolder the idea, the better.</p>
<p class="links links--center"><a class="link" href="about.html">About us</a><a class="link" href="contact.html">Start a project</a></p>
</div>
</section>

<section class="band band--alt band--tall">
<div class="wrap grid-2 promise">
<div>
<span class="eyebrow">Our production promise</span>
<h2>Thinking before the camera rolls. Quality after it.</h2>
<p>Every project follows the same simple promise, so you always know what is being made, when it arrives and what we need from you.</p>
<p class="links"><a class="link" href="about.html">How we work</a><a class="link" href="services.html#workflow">Our workflow</a></p>
</div>
<ol class="promise-list">
<li><strong>Creative thinking</strong> before the camera rolls.</li>
<li><strong>Professional execution</strong> on location and in studio.</li>
<li><strong>Consistent</strong> visual quality.</li>
<li><strong>Multiple useful deliverables</strong> from planned production.</li>
<li><strong>Reliable</strong> communication and delivery.</li>
</ol>
</div>
</section>

<section class="band band--alt band--tall">
<div class="wrap">
<h2 class="band-title">Trusted to capture what matters</h2>
<p class="note" style="margin-top:10px">Sample testimonials for this proof of concept</p>
<div style="margin-top:28px">
<div class="quote"><div class="avatar" aria-hidden="true">A</div><div><h3>Amina Wanjiru</h3><span class="role">Boutique owner</span><p>The team made the whole shoot feel effortless. The photos came back sharper and more striking than we had pictured.</p></div></div>
<div class="quote"><div class="avatar" aria-hidden="true">D</div><div><h3>Daniel Otieno</h3><span class="role">Marketing manager</span><p>Our launch video was delivered on time and looked far beyond what we expected. We have already booked them for the next campaign.</p></div></div>
</div>
<p class="links"><a class="link" href="testimonials.html">More client stories</a></p>
</div>
</section>

''' + enquiry_band('home')

page('index.html', 'Lion Creative Media | Commercial Photography, Film &amp; Creative Production in Nairobi',
     'Lion Creative Media is a Nairobi-based commercial photography, film and creative production company helping businesses communicate their value through powerful visuals.',
     'index.html', home.replace('{svc_cards}', svc_cards))

# =====================================================================
# PORTFOLIO (category index)
# =====================================================================
cat_items = '\n'.join(
    f'<li><a href="{c[0]}">{c[1]}<span>VIEW &rarr;</span></a></li>' for c in CATS
) + '\n<li><a href="photography-videography.html">Photography/Videography<span>VIEW &rarr;</span></a></li>'
portfolio = f'''<section class="band band--top">
<div class="wrap">
<h1>Our Projects</h1>
<p class="lede" style="margin-top:14px;max-width:640px">A look at recent portraits, weddings, product and commercial work from across our company. Choose a category to explore.</p>
</div>
</section>

<section class="band">
<div class="wrap">
<div class="frame ratio-169"><img src="images/wedding.jpg" alt="A couple holding hands at a wedding ceremony in front of a white floral arch" style="object-position:center 40%"></div>
</div>
</section>

<section class="band band--tall">
<div class="wrap">
<ul class="cat-list">
{cat_items}
</ul>
<p class="links"><a class="link" href="contact.html">Book a shoot</a><a class="link" href="tel:+254742552019">Call us</a></p>
</div>
</section>
'''
page('portfolio.html', 'Our Projects | Lion Creative Media',
     'Explore weddings, portraits, fashion, product, event and corporate photography and film by Lion Creative Media, Nairobi.',
     'portfolio.html', portfolio)

# =====================================================================
# PORTFOLIO CATEGORY PAGES (weddings has its own richer page below)
# =====================================================================
for slug, title, img, pos, alt, blurb in CATS:
    if slug == 'weddings.html':
        continue
    plain_title = title.replace('&amp;', '&')
    ratio = 'ratio-32' if ('lipstick' in img or 'cat-' in img) else 'ratio-45'
    body = f'''<section class="band band--top">
<div class="wrap">
<p><a class="back" href="portfolio.html">&larr; Our Projects</a></p>
<h1>{title}</h1>
<p class="lede" style="margin-top:14px;max-width:640px">{blurb}</p>
</div>
</section>

<section class="band">
<div class="wrap gallery single">
<div><div class="frame {ratio}"><img src="{img}" alt="{alt}" style="object-position:{pos}"></div><p class="caption">{title}</p></div>
</div>
</section>

''' + cta_band('Your project could be next.')
    page(slug, f'{plain_title} | Lion Creative Media', f'{plain_title} photography and film by Lion Creative Media, Nairobi.',
         'portfolio.html', body)

# =====================================================================
# WEDDINGS
# =====================================================================
weddings = '''<section class="band band--top">
<div class="wrap">
<div class="frame ratio-169"><img src="images/wedding.jpg" alt="A couple holding hands at a wedding ceremony in front of a white floral arch" style="object-position:center 40%"></div>
</div>
</section>

<section class="band band--tall">
<div class="wrap grid-2">
<div>
<h1>Every vow. Every laugh. Every detail.</h1>
</div>
<div>
<p>From the quiet nerves before the ceremony to the last dance of the night, we cover the big moments and the quiet ones in between. Weddings, engagements and celebrations, photographed and filmed with warmth and care.</p>
<p>Based in Nairobi and available for assignments outside the city, we ask about your date, venue and priorities, then send a tailored photography and film proposal.</p>
<p class="links"><a class="link" href="contact.html">Enquire about your wedding</a><a class="link" href="tel:+254742552019">Call us</a></p>
<p class="note" style="margin-top:18px">Placeholder gallery: more wedding work will be added.</p>
</div>
</div>
</section>

''' + cta_band('Planning your day?', 'Enquire about your wedding')
page('weddings.html', 'Wedding Photography &amp; Film | Lion Creative Media',
     'Wedding, engagement and celebration photography and film in Nairobi and beyond, by Lion Creative Media.',
     'portfolio.html', weddings)
# SERVICES
# =====================================================================
cards = svc_cards
services = f'''<section class="band band--top">
<div class="wrap grid-2">
<div><h1>Our Services</h1></div>
<div><p class="lede">We help businesses communicate their value through powerful visuals, professional production and purposeful storytelling. Choose a service below to see what is included. Every project is quoted from your brief, with deliverables, schedule, crew, location and budget agreed in advance.</p></div>
</div>
</section>

<section class="band band--tall">
<div class="wrap">
<div class="svc-grid svc-grid--eight">
{cards}</div>
</div>
</section>

<section class="band band--alt band--tall" id="workflow">
<div class="wrap">
<span class="eyebrow">The production workflow</span>
<h2 class="band-title">From first enquiry to final delivery</h2>
<p class="lede" style="max-width:680px;margin-top:14px">Every project follows the same ten steps, so you know what is happening, what is being delivered, when it will arrive and what we need from you.</p>
<ol class="steps">
<li><span class="step-name">Enquiry</span><span class="step-text">We respond within one business day.</span></li>
<li><span class="step-name">Discovery</span><span class="step-text">We understand your brief and budget.</span></li>
<li><span class="step-name">Quotation</span><span class="step-text">Sent within 24&ndash;48 hours once we have enough information.</span></li>
<li><span class="step-name">Booking</span><span class="step-text">Signed approval and a deposit confirm your date.</span></li>
<li><span class="step-name">Pre-production</span><span class="step-text">An approved concept, schedule and shot list.</span></li>
<li><span class="step-name">Production</span><span class="step-text">We shoot according to the agreed scope.</span></li>
<li><span class="step-name">Editing</span><span class="step-text">Your first draft arrives within the agreed timeline.</span></li>
<li><span class="step-name">Revisions</span><span class="step-text">Feedback is tracked across the agreed revision rounds.</span></li>
<li><span class="step-name">Delivery</span><span class="step-text">Organised files are handed over on the agreed date, with final payment.</span></li>
<li><span class="step-name">Follow-up</span><span class="step-text">We ask for your feedback and talk about what comes next.</span></li>
</ol>
</div>
</section>

''' + cta_band('Plan your shoot.', 'Start a project', alt=False)
page('services.html', 'Services | Lion Creative Media',
     'Commercial and brand production, events and corporate coverage, professional photography and post-production in Nairobi by Lion Creative Media.',
     'services.html', services)

# =====================================================================
# TESTIMONIALS
# =====================================================================
TESTI = [
    ('A', 'Amina Wanjiru', 'Boutique owner', 'The team made the whole shoot feel effortless. The photos came back sharper and more striking than we had pictured.'),
    ('D', 'Daniel Otieno', 'Marketing manager', 'Our launch video was delivered on time and looked far beyond what we expected. We have already booked them for the next campaign.'),
    ('G', 'Grace Mutua', 'Newlywed', 'They caught the loud moments and the quiet ones. Every time we open our album, we feel that day all over again.'),
    ('M', 'Mercy Kamau', 'Caf&eacute; owner', 'The retouching was natural and the colours were spot on. We now use the images across our website and social channels.'),
    ('P', 'Peter Mwangi', 'Operations lead', 'Our conference coverage and highlight film came together beautifully. The whole team was impressed.'),
    ('F', 'Faith Njeri', 'Consultant', 'I was nervous about being photographed, but the session felt easy and fun. I finally have portraits I am proud to share.'),
]
rows = ''.join(
    f'<div class="quote"><div class="avatar" aria-hidden="true">{i}</div><div><h3>{n}</h3><span class="role">{r}</span><p>{t}</p></div></div>\n'
    for i, n, r, t in TESTI
)
testimonials = f'''<section class="band band--top">
<div class="wrap">
<h1>Trusted to capture what matters</h1>
<p class="note" style="margin-top:12px">Sample testimonials for this proof of concept</p>
<p class="links"><a class="link" href="contact.html">Leave a review</a></p>
</div>
</section>

<section class="band band--tall">
<div class="wrap" style="max-width:960px">
{rows}</div>
</section>

''' + cta_band('Be our next story.', 'Start a project')
page('testimonials.html', 'Client Testimonials | Lion Creative Media',
     'Kind words from the people and brands who have worked with Lion Creative Media.',
     'testimonials.html', testimonials)

# =====================================================================
# INSIGHTS (blog): posts are markdown files in content/posts, edited in Pages CMS
# =====================================================================
def warn(msg):
    # shows as a yellow annotation in the GitHub Actions run, plain text elsewhere
    print(f"::warning::{msg}" if os.environ.get('GITHUB_ACTIONS') else f"WARNING: {msg}")


def split_front_matter(text):
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def as_date(v):
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    try:
        return datetime.date.fromisoformat(str(v)[:10])
    except ValueError:
        return datetime.date.today()


def clean_path(p):
    """CMS writes '/images/blog/x.jpg'; the site uses relative paths so it works in any folder."""
    return str(p or '').strip().lstrip('/')


FOCUS = {'top': 'center 15%', 'upper': 'center 30%', 'center': 'center', 'lower': 'center 70%'}
md = markdown.Markdown(extensions=['extra', 'sane_lists', 'smarty'])


def load_posts():
    posts = []
    for f in sorted((OUT / 'content' / 'posts').glob('*.md')):
        meta, body = split_front_matter(f.read_text(encoding='utf-8'))
        slug = f.stem
        title = str(meta.get('title') or slug.replace('-', ' ').title()).strip()
        published = bool(meta.get('published', False))
        d = as_date(meta.get('date'))
        md.reset()
        body_html = md.convert(body)
        body_html = re.sub(r'(<img[^>]*?\ssrc=")/', r'\1', body_html)
        body_html = body_html.replace('<img ', '<img loading="lazy" ')
        words = len(re.findall(r'\w+', body))
        post = dict(
            slug=slug, file=f'insights-{slug}.html', title=title, published=published, date=d,
            category=str(meta.get('category') or 'News'), author=str(meta.get('author') or 'The Lion Creative Media team'),
            excerpt=str(meta.get('excerpt') or '').strip(),
            seo_title=str(meta.get('seo_title') or '').strip(),
            desc=str(meta.get('meta_description') or meta.get('excerpt') or '').strip(),
            keyword=str(meta.get('focus_keyword') or '').strip(),
            cover=clean_path(meta.get('cover')), alt=str(meta.get('cover_alt') or '').strip(),
            pos=FOCUS.get(str(meta.get('cover_focus') or 'upper'), 'center 30%'),
            body_html=body_html, body=body, words=words, minutes=max(1, round(words / 200)),
        )
        if published:
            seo_check(post)
        posts.append(post)
    posts.sort(key=lambda p: p['date'], reverse=True)
    return posts


def seo_check(p):
    """Plain-language SEO checks, reported (never blocking) when the site is built."""
    n = p['slug']
    t = p['seo_title'] or p['title']
    if len(t) > 60:
        warn(f"[{n}] SEO title is {len(t)} characters; Google cuts titles off after about 60.")
    if not p['desc']:
        warn(f"[{n}] has no meta description.")
    elif not 70 <= len(p['desc']) <= 160:
        warn(f"[{n}] meta description is {len(p['desc'])} characters; aim for 70 to 160.")
    if not p['cover']:
        warn(f"[{n}] has no cover image, so social shares will show the default picture.")
    elif not p['alt']:
        warn(f"[{n}] cover image has no description (alt text).")
    for img in re.findall(r'<img[^>]*>', p['body_html']):
        if not re.search(r'\salt="[^"]+"', img):
            warn(f"[{n}] an image in the article has no description (alt text).")
    if p['words'] < 300:
        warn(f"[{n}] is only {p['words']} words; short posts rarely rank. Aim for 300 or more.")
    if not re.search(r'<h[23]', p['body_html']):
        warn(f"[{n}] has no sub-headings (use Heading 2 / Heading 3) to break up the text.")
    k = p['keyword'].lower()
    if k:
        first = ' '.join(re.sub(r'<[^>]+>', ' ', p['body_html']).split()[:100]).lower()
        for label, text in (('title', t.lower()), ('meta description', p['desc'].lower()), ('first 100 words', first)):
            if k not in text:
                warn(f"[{n}] focus keyword \"{p['keyword']}\" is missing from the {label}.")


POSTS = load_posts()
LIVE = [p for p in POSTS if p['published']]

entries = ''
for p in LIVE:
    img = (f'<div class="frame ratio-32"><img src="{p["cover"]}" alt="{htmllib.escape(p["alt"])}" '
           f'style="object-position:{p["pos"]}"></div>') if p['cover'] else '<div></div>'
    entries += f'''<article class="entry">
<a class="entry-img" href="{p['file']}" tabindex="-1" aria-hidden="true">{img}</a>
<div>
<p class="entry-date">{p['date'].strftime('%d %b %Y')} &middot; {htmllib.escape(p['category'])}</p>
<h2><a href="{p['file']}">{htmllib.escape(p['title'])}</a></h2>
<p>{htmllib.escape(p['excerpt'])}</p>
<p><a class="link" href="{p['file']}">Read article</a></p></div>
</article>
'''
if not entries:
    entries = '<p class="reel-empty">New articles are on the way. Check back soon.</p>'
journal = f'''<section class="band band--top">
<div class="wrap">
<h1>Insights</h1>
<p class="lede" style="margin-top:14px;max-width:640px">Stories, tips and behind the scenes: advice for getting the most from your shoot, plus a look at how we work.</p>
</div>
</section>

<section class="band band--tall">
<div class="wrap">
{entries}</div>
</section>
'''
page('journal.html', 'Insights | Lion Creative Media',
     'Stories, tips and behind-the-scenes notes on photography and film from Lion Creative Media, Nairobi.',
     'journal.html', journal, lastmod=LIVE[0]['date'] if LIVE else None)

for p in LIVE:
    e = htmllib.escape
    title_tag = e(f"{p['seo_title'] or p['title']} | {SITE_NAME}") if '|' not in (p['seo_title'] or '') else e(p['seo_title'])
    desc = e(p['desc'])
    cover_html = (f'''<section class="band">
<div class="wrap post">
<div class="frame ratio-32"><img src="{p['cover']}" alt="{e(p['alt'])}" style="object-position:{p['pos']}"></div>
</div>
</section>
''') if p['cover'] else ''
    ld = {
        '@context': 'https://schema.org', '@type': 'Article', 'headline': p['title'],
        'description': p['desc'], 'datePublished': p['date'].isoformat(), 'dateModified': p['date'].isoformat(),
        'author': {'@type': 'Organization', 'name': SITE_NAME}, 'publisher': {'@type': 'Organization', 'name': SITE_NAME,
        'logo': {'@type': 'ImageObject', 'url': abs_url('images/logo.png')}},
        'mainEntityOfPage': abs_url(p['file']),
    }
    if p['cover']:
        ld['image'] = abs_url(p['cover'])
    extra = (f'<meta property="article:published_time" content="{p["date"].isoformat()}">\n'
             f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>\n')
    body = f'''<section class="band band--top">
<div class="wrap post">
<p><a class="back" href="journal.html">&larr; Back to Insights</a></p>
<p class="meta">{e(p['category'])} &middot; {p['date'].strftime('%d %b %Y')} &middot; {p['minutes']} min read</p>
<h1>{e(p['title'])}</h1>
<p class="lede">{e(p['excerpt'])}</p>
<p class="note">By {e(p['author'])}</p>
</div>
</section>

{cover_html}<section class="band band--tall">
<div class="wrap post post-body">
{p['body_html']}
</div>
</section>

''' + cta_band('Ready to plan your own shoot?')
    page(p['file'], title_tag, desc, 'journal.html', body, share_image=p['cover'] or None,
         kind='article', extra=extra, lastmod=p['date'])

# the old sample address now points visitors to the live article
(OUT / 'article.html').write_text(
    '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved | Lion Creative Media</title>'
    '<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url=journal.html">'
    '<link rel="canonical" href="' + abs_url('journal.html') + '"></head>'
    '<body><p><a href="journal.html">Go to Insights</a></p></body></html>', encoding='utf-8')

# =====================================================================
# CONTACT
# =====================================================================
SERVICE_OPTIONS = '\n'.join(f'<option value="{v["slug"]}">{esc(v["title"])}</option>' for v in SERVICE_LIST)
contact = f'''<section class="band band--top">
<div class="wrap pair" style="grid-template-columns:repeat(3,1fr);gap:32px">
<div class="frame ratio-34"><img src="images/portrait-red.jpg" alt="Woman in a black blazer and red jumpsuit smiling in a studio portrait" style="object-position:center 25%"></div>
<div class="frame ratio-34"><img src="images/wedding.jpg" alt="A couple holding hands at a wedding ceremony" style="object-position:35% center"></div>
<div class="frame ratio-34"><img src="images/lipstick.jpg" alt="Two lipsticks displayed on seashells against a brown backdrop" style="object-position:55% center"></div>
</div>
</section>

<section class="band band--tall">
<div class="wrap grid-2">
<div class="contact-copy">
<h1>Let&rsquo;s make something fearless.</h1>
<p style="margin-top:18px">Tell us what you are planning: a product shoot, brand film, corporate event, headshot session or campaign. We respond within one business day, and send a quotation within 24&ndash;48 hours once we have enough information.</p>
<p class="big-phone"><a href="tel:+254742552019">{PHONE}</a></p>
<p>Based in Nairobi, Kenya &middot; Available for assignments outside Nairobi too.</p>
<p class="links"><a class="link" href="tel:+254742552019">Call us</a></p>
</div>
<div>
<form class="enquiry" id="form-contact" data-demo-form data-sent="sent-contact">
<label class="field-label" for="c-name">Name</label>
<input class="field" id="c-name" name="name" type="text" autocomplete="name" required>
<label class="field-label" for="c-email">Email</label>
<input class="field" id="c-email" name="email" type="email" autocomplete="email" required>
<label class="field-label" for="c-type">What are you planning?</label>
<select class="field" id="c-type" name="type">
<option value="">Choose a service</option>
{SERVICE_OPTIONS}
<option value="other">Something else</option>
</select>
<label class="field-label" for="c-date">Preferred date (optional)</label>
<input class="field" id="c-date" name="date" type="date">
<label class="field-label" for="c-msg">Tell us more</label>
<textarea class="field" id="c-msg" name="message"></textarea>
<button class="btn" type="submit">Send enquiry</button>
</form>
<div class="form-sent" id="sent-contact" tabindex="-1" hidden>
<h3>Message sent.</h3>
<p>Thank you for reaching out. We will get back to you soon to talk through your idea.</p>
<p class="note">Demo form: nothing is actually sent yet.</p>
<p><a class="link" href="index.html">Back to home</a></p>
</div>
</div>
</div>
</section>
'''
page('contact.html', 'Book a Shoot | Lion Creative Media',
     'Contact Lion Creative Media in Nairobi to plan a product shoot, brand film, corporate event, headshot session or campaign.',
     'contact.html', contact)

# =====================================================================
# ABOUT US
# =====================================================================
about = f'''<section class="band band--top">
<div class="wrap about-intro">
<span class="eyebrow">About Us</span>
<h1>Every Story Deserves to Be Seen. Every Moment Deserves to Be Remembered.</h1>
</div>
</section>

<section class="band band--tall">
<div class="wrap grid-2">
<div><p class="lede lede--big">Welcome to Lion Creative Media, where creativity meets storytelling.</p></div>
<div>
<p>We are a Nairobi-based creative production company passionate about capturing life&rsquo;s special moments and bringing ideas to life through professional photography, videography and creative production.</p>
<p>From weddings, birthdays and corporate events to brand campaigns, product shoots and commercial films, we approach every project with creativity, passion and attention to detail.</p>
<p>We believe every moment has a story worth telling and every brand has a vision worth sharing. Our mission is to turn those stories into beautiful, lasting visual experiences.</p>
<p class="links"><a class="link" href="services.html">Our services</a><a class="link" href="contact.html">Work with us</a></p>
</div>
</div>
</section>

<section class="band">
<div class="wrap">
<div class="frame ratio-169"><img src="images/hero-3.jpg" alt="A camera operator filming an event with several cameras" style="object-position:center 40%"></div>
</div>
</section>

<section class="band band--alt band--tall">
<div class="wrap">
<span class="eyebrow">What sets us apart</span>
<h2 class="band-title">How we work</h2>
<dl class="defs">
<div><dt>Creative direction</dt><dd>We develop concepts, scripts, shot lists and visual references before we film.</dd></div>
<div><dt>Business understanding</dt><dd>We learn your audience, your product and the message you want to send.</dd></div>
<div><dt>Production planning</dt><dd>Deliverables, schedule, crew, location and budget are agreed in advance.</dd></div>
<div><dt>Multi-format delivery</dt><dd>We plan the formats and aspect ratios you need before the camera rolls.</dd></div>
<div><dt>Professional handover</dt><dd>You receive organised, high-quality assets on the agreed date.</dd></div>
</dl>
</div>
</section>

<section class="band band--tall">
<div class="wrap">
<span class="eyebrow">Our team</span>
<h2 class="band-title">One team behind every project</h2>
<dl class="defs">
<div><dt>Founder &amp; Creative Director</dt><dd>Client relationships, creative direction and quality control.</dd></div>
<div><dt>Production</dt><dd>Camera operators, photographers, drone operators and lighting assistants.</dd></div>
<div><dt>Post-production</dt><dd>Video editors, retouchers, motion designers and sound specialists.</dd></div>
<div><dt>Production support</dt><dd>Makeup artists, models, stylists and set assistants.</dd></div>
<div><dt>Administration</dt><dd>Bookings, quotations, contracts, invoicing and delivery.</dd></div>
</dl>
</div>
</section>

<section class="band band--alt band--tall">
<div class="wrap">
<span class="eyebrow">Our standards</span>
<h2 class="band-title">What you can expect</h2>
<div class="grid-3 block" style="margin-top:34px">
<div><h3>Every project has a creative brief</h3><p>We never start filming until we understand your intended message and have agreed the deliverables.</p></div>
<div><h3>A professional production experience</h3><p>You know what is happening, what is being delivered, when it will arrive and what we need from you.</p></div>
<div><h3>Work worth sharing</h3><p>With your permission, we turn the project into a case study, behind-the-scenes content and a genuine testimonial.</p></div>
</div>
</div>
</section>

''' + cta_band('Have an idea? We&rsquo;d love to hear it.', 'Get in touch', alt=False)
page('about.html', 'About Us | Lion Creative Media',
     'Lion Creative Media is a Nairobi-based creative production company capturing life\'s special moments through professional photography, videography and creative production.',
     'about.html', about)

# =====================================================================
# PHOTOGRAPHY / VIDEOGRAPHY
# =====================================================================
pv = f'''<section class="band band--top">
<div class="wrap">
<p><a class="back" href="portfolio.html">&larr; Our Projects</a></p>
</div>
<div class="wrap grid-2" style="margin-top:18px">
<div><h1>Photography &amp; Videography</h1></div>
<div><p class="lede">Stills and motion from one creative team. We plan the formats and aspect ratios before filming, so a single shoot gives you multiple useful deliverables that look and feel like your business.</p></div>
</div>
</section>

<section class="band band--tall">
<div class="wrap cards two">
<article class="card">
<div class="frame ratio-32"><img src="images/pv-photography.jpg" alt="A bride in a pearl-beaded veil as her groom places the ring on her finger" style="object-position:center 35%"></div>
<h3>Photography</h3>
<p class="blurb">Considered photography for businesses, teams and occasions.</p>
<ul><li>Product photography</li><li>Corporate headshots and executive portraits</li><li>Personal branding and team photography</li><li>Food, hospitality and real-estate visuals</li><li>Weddings, private events and corporate events</li><li>Family, maternity and milestone portraits</li></ul>
<a class="link" href="portfolio.html">See our projects</a>
</article>
<article class="card">
<div class="frame ratio-32"><img src="images/pv-videography.jpg" alt="A camera operator filming an event under purple and orange stage lighting" style="object-position:center 40%"></div>
<h3>Videography</h3>
<p class="blurb">Films that communicate your value, built from concept through to the final cut.</p>
<ul><li>Company profile videos</li><li>Brand films and promotional videos</li><li>Social-media campaign production</li><li>Customer testimonials and case studies</li><li>Event highlight films and same-day edits</li><li>Drone, podcast and livestream production</li></ul>
<a class="link" href="contact.html">Enquire about video</a>
</article>
</div>
</section>

<section class="band band--alt band--tall">
<div class="wrap">
<h2 class="band-title">One team, start to finish</h2>
<div class="grid-4 values" style="margin-top:32px">
<div><h3>Creative Direction</h3><p>We shape the idea, styling, locations and mood before the camera rolls.</p></div>
<div><h3>Professional Production</h3><p>Dependable planning, pro gear and a smooth workflow from shoot day to final files.</p></div>
<div><h3>Premium Retouching</h3><p>Natural retouching, refined colour and a clean, editorial finish on every frame.</p></div>
<div><h3>Private Delivery</h3><p>Photos and films delivered through a private online gallery, easy to view and share.</p></div>
</div>
</div>
</section>

''' + cta_band('Tell us what you&rsquo;re planning.', 'Book a shoot', alt=False)
page('photography-videography.html', 'Photography &amp; Videography | Lion Creative Media',
     'Portrait, product, corporate and fashion photography plus brand films, event highlights and social reels from Lion Creative Media in Nairobi.',
     'portfolio.html', pv)

# =====================================================================
# SERVICE DETAIL PAGES (one per card on the Our Services page)
# =====================================================================
for v in SERVICE_LIST:
    lis = ''.join(f'<li>{esc(i)}</li>' for i in v['items'])
    others = ''.join(f'<a href="service-{o["slug"]}.html">{esc(o["title"])}</a>' for o in SERVICE_LIST if o is not v)
    body = f'''<section class="band band--top">
<div class="wrap">
<p><a class="back" href="services.html">&larr; Our Services</a></p>
</div>
<div class="wrap grid-2" style="margin-top:18px">
<div><h1>{esc(v['title'])}</h1></div>
<div><p class="lede">{esc(v['lede'])}</p></div>
</div>
</section>

<section class="band band--tall">
<div class="wrap grid-2 service-detail">
<div class="frame ratio-32"><img src="{v['img']}" alt="{esc(v['alt'])}" style="object-position:{v['pos']}"></div>
<div>
<h2>What&rsquo;s included</h2>
<ul class="included">{lis}</ul>
<p class="note">Every project starts with a short chat about your brief and budget, then a quotation. <a class="link" href="services.html#workflow">See how it works</a></p>
<p class="links"><a class="link" href="contact.html?service={v['slug']}">Enquire about {esc(v['title'])}</a><a class="link" href="tel:{TEL}">Call us</a></p>
</div>
</div>
</section>

<section class="band band--alt band--tall">
<div class="wrap">
<span class="eyebrow">More services</span>
<div class="more-services">{others}</div>
</div>
</section>
'''
    page(f"service-{v['slug']}.html", f"{esc(v['title'])} | Lion Creative Media",
         f"{esc(v['title'])} in Nairobi by Lion Creative Media. {esc(v['lede'])}", 'services.html', body)


# =====================================================================
# BTS (behind the scenes): reels listed in a Google Sheet, see BTS-GUIDE.md
# =====================================================================
BTS_SHEET_URL = ''   # paste the sheet's "Publish to web" CSV link here (see BTS-GUIDE.md)
bts = f'''<section class="band band--top">
<div class="wrap grid-2">
<div><h1>Behind the Scenes</h1></div>
<div><p class="lede">A look at how we plan, shoot and finish our work, straight from our Instagram. Tap a reel to play it.</p></div>
</div>
</section>

<section class="band band--tall">
<div class="wrap">
<div class="reel-grid" id="reel-grid" data-sheet="{BTS_SHEET_URL}" aria-live="polite"></div>
<p class="reel-empty" id="reel-empty" hidden>New reels are on the way. Check back soon.</p>
<noscript><p class="reel-empty">Please turn on JavaScript to watch our reels.</p></noscript>
</div>
</section>

<script src="bts.js?v=1" defer></script>

''' + cta_band('Want your own story told this way?', 'Start a project', alt=True)
page('bts.html', 'Behind the Scenes | Lion Creative Media',
     'Behind-the-scenes reels from Lion Creative Media: how we plan, shoot and finish commercial photography and film in Nairobi.',
     'bts.html', bts)

# =====================================================================
# SITEMAP + ROBOTS
# =====================================================================
urls = ''
for fname, mod in sorted(PAGES, key=lambda x: (x[0] != 'index.html', x[0])):
    loc = abs_url('' if fname == 'index.html' else fname)
    urls += f"  <url><loc>{loc}</loc>" + (f"<lastmod>{mod.isoformat()}</lastmod>" if mod else '') + "</url>\n"
(OUT / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n',
    encoding='utf-8')
(OUT / 'robots.txt').write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding='utf-8')

print(f'wrote {len(PAGES)} pages, {len(LIVE)} published posts, sitemap.xml and robots.txt to', OUT)
