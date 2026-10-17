#!/usr/bin/env python3
"""Rebel Elite FC — static site generator (GitHub Pages).

python3 build.py site            -> out/site/   production (CNAME rebelelitefc.com)
python3 build.py site preview    -> out/site/   preview (noindex, robots Disallow, no CNAME)

Facts come from ignitefc.com (Rebel Elite is the girls' side of Ignite FC) and the old rebelelitefc.com.
Anything marked [CONFIRM] is awaiting Chris.
"""
import datetime, hashlib, json, re, shutil, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

MODE = sys.argv[1] if len(sys.argv) > 1 else "site"
PREVIEW = "preview" in sys.argv[2:]
BASE = "/rebelelitefc.com" if PREVIEW else ""   # GitHub project-pages subpath for the preview
HERE = Path(__file__).parent
OUT = HERE / "out" / MODE
CACHE = HERE / ".imgcache"; CACHE.mkdir(exist_ok=True)
IMG = HERE / "img"

# ---------------------------------------------------------------- facts
NAME = "Rebel Elite FC"
DOMAIN = "https://rebelelitefc.com"
CITY, STATE = "St. George", "UT"
PHONE, TEL = "435-680-9777", "+14356809777"
EMAIL = "soccer@rebelelitefc.com"
FACEBOOK = "https://www.facebook.com/ignitefcutah"
INSTAGRAM = "https://www.instagram.com/rebelelitefc/"
YOUTUBE = "https://www.youtube.com/@watchIgniteFC"
IGNITE = "https://ignitefc.com"
TRYOUTS_URL = "https://app.olliesports.com/tryouts/ignite-fc/2026-27-tryouts"
FEES_URL = "https://ignitefc.com/2026-2027-club-fees/"
STORE_KIT = "https://www.soccer.com/club/#/2001546044/required"
STORE_FAN = "https://www.soccer.com/club/#/2001546044/fanwear"
ZCC = "https://www.zionchampionscup.com/"
SPONSOR_URL = f"mailto:{EMAIL}?subject=Sponsoring%20Rebel%20Elite%20FC"   # [CONFIRM] swap for Typeform/Stripe link
FIELDS_TRAIN = "Sullivan Soccer Complex and Little Valley Soccer Complex"
FIELDS_TRYOUT = "Sullivan Soccer Complex"
FIELDS_GAMES = "Shivwits fields (past Ivins)"
YEAR = datetime.date.today().year
SEASON = "2026-27"

STATS = [("2×", "Presidents Cup National Champions"), ("3", "State championships in 2026 alone"), ("24", "girls' teams, U8–U19"), ("2018", "Ignite FC founded in St. George")]

HONORS = [  # (when, what)
    ("Jan 2026", "Rebel Elite 2012, 2010 and 2007 — Presidents Cup State Champions (U14, U16, U19)"),
    ("Jul 2025", "Rebel Elite Black U18 — Presidents Cup National Champions"),
    ("Jun 2025", "Rebel Elite Black U16 — State Cup Regional Champions"),
    ("Jan 2025", "Rebel Elite Black U13 — Presidents Cup State Champions"),
    ("Jun 2024", "Rebel Elite Black U18 — USYS Far West Regional Champions; Presidents Cup National finalists"),
    ("Feb 2024", "Rebel Elite Black U14 and U17 — Presidents Cup State Champions"),
    ("Jul 2023", "Rebel Elite Black U14 — Presidents Cup National Champions"),
    ("Jun 2023", "Rebel Elite Black U17 — Presidents Cup National finalists"),
    ("Mar 2023", "Rebel Elite joins the Ignite FC family as the club's girls' program"),
]

# 2026-27 school-year alignment (Aug 1 cutoff). (birth year, Jan–Jul group, Aug–Dec group)
AGE_CHART = [(2018, "U9", "U8"), (2017, "U10", "U9"), (2016, "U11", "U10"), (2015, "U12", "U11"), (2014, "U13", "U12"), (2013, "U14", "U13"),
             (2012, "U15", "U14"), (2011, "U16", "U15"), (2010, "U17", "U16"), (2009, "U18", "U17"), (2008, "U19", "U18"), (2007, "—", "U19")]

STAGES = [  # (slug, label, birth years, stage, blurb)
    ("u8-u10", "U8 – U10", "2017 – 2018", "Foundation", "Small-sided games, hundreds of touches a session, and falling in love with the ball. First touch, dribbling under pressure, and the confidence to try things are built here."),
    ("u11-u12", "U11 – U12", "2015 – 2016", "Development", "9v9 soccer with real positions and real decisions. Shape, passing patterns, and how to compete the right way — while training stays fun and demanding."),
    ("u13-u14", "U13 – U14", "2013 – 2014", "Competitive", "The jump to 11v11. Players learn a system, pressing triggers, and set pieces, and travel to regional tournaments across Utah, Nevada, and Arizona."),
    ("u15-u16", "U15 – U16", "2011 – 2012", "Elite", "High-school-age training built for the next level: individual development plans, strength and speed work, video, and showcase tournaments."),
    ("u17-u19", "U17 – U19", "2008 – 2010", "College pathway", "Our oldest teams play State Cup, Presidents Cup, and college showcases — the same path our 2023 and 2025 national champions took — with recruiting guidance and film."),
]

# Rebel Elite teams as listed on ignitefc.com/teams (birth year, color)
TEAMS = [
    (2007, "Black"), (2007, "White"), (2008, "Black"),
    (2009, "Black"), (2009, "White"), (2009, "Pink"),
    (2010, "Black"), (2010, "White"), (2011, "Black"),
    (2012, "Black"), (2012, "White"), (2012, "Pink"),
    (2013, "Black"), (2013, "White"), (2014, "Black"),
    (2015, "Black"), (2015, "White"),
    (2016, "Black"), (2016, "White"), (2016, "Pink"),
    (2017, "Black"), ("2017/18", "White"),
]
ALUMNI_TEAMS = [(2006, "Black"), (2006, "White"), (2005, "Black")]




FAQ_TRYOUTS = [
    ("When are Rebel Elite tryouts?", "Every club in Utah holds tryouts in the same window set by UYSA — the first week of June. Registration opens in the spring on Ollie Sports, and the schedule by age group is posted here and on ignitefc.com. Players can be evaluated year-round if a roster has room."),
    ("Where are tryouts held?", f"At {FIELDS_TRYOUT} in St. George. Arrive 15–20 minutes before your first session for check-in."),
    ("Who can try out?", "Girls U8 through U19. No prior club experience is required for our younger age groups. U8 players may play up with U9."),
    ("What should my player bring?", "Water, a ball, cleats, and shin guards. Attend every session you can — more time in front of the coaches is better, but one night is welcome."),
    ("What does it cost to play?", "Club fees are set each season and kept as low as possible; UYSA registration and the adidas Rebel kit are paid separately, and each team chooses and funds its own tournaments. The current fee sheet is posted on ignitefc.com before tryouts."),
    ("Which age group is my daughter in?", "Starting with the 2026-27 season, UYSA uses a school-year alignment with an August 1 cutoff: players born January–July are in one age group and players born August–December in the next younger group. See the chart on our Teams page."),
    ("Where do teams train and play?", f"Practices are usually two nights a week at {FIELDS_TRAIN}. League games run in a fall season and a spring season (8–15 games each), usually one night a week, mostly at the {FIELDS_GAMES}."),
    ("We're from out of town. Can we still try out?", "Yes. Email us your player's name and birthdate and we'll connect you with the right coach or arrange another option."),
]

NAV = [("/teams/", "Teams"), ("/tryouts/", "Tryouts"), ("/about/", "About"), (ZCC, "Tournament"), ("/contact/", "Contact")]

# ---------------------------------------------------------------- helpers
def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
def asset(rel): return "/" + rel
IMG_OUT = set()

def _variant(name, w, crop=None, top=0.3):
    stem = re.sub(r"[^a-z0-9]+", "-", Path(name).stem.lower()).strip("-")
    tag = f"-{crop[0]}x{crop[1]}" if crop else ""
    rel = f"img/{stem}{tag}-{w}.webp"; dst = CACHE / Path(rel).name
    if not dst.exists():
        im = ImageOps.exif_transpose(Image.open(IMG / name))
        im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
        if crop:
            r = crop[0] / crop[1]
            if im.width / im.height > r:
                nw = int(im.height * r); x = (im.width - nw) // 2; im = im.crop((x, 0, x + nw, im.height))
            else:
                nh = int(im.width / r); y = int((im.height - nh) * top); im = im.crop((0, y, im.width, y + nh))
        if im.width > w: im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        im.save(dst, "WEBP", quality=82, method=5)
    IMG_OUT.add(rel); return rel, Image.open(dst).size

def pic(name, alt, sizes="100vw", cls="", eager=False, crop=None, maxw=1920, top=0.3):
    full = min(Image.open(IMG / name).width, maxw)
    vs = [_variant(name, w, crop, top) for w in sorted({w for w in (480, 960, full) if w <= full})]
    srcset = ", ".join(f"{asset(rel)} {sz[0]}w" for rel, sz in vs); rel, (w, h) = vs[-1]
    load = 'fetchpriority="high" loading="eager"' if eager else 'loading="lazy"'
    return f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="{asset(rel)}" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" alt="{esc(alt)}" decoding="async" {load}>'

I = {k: f'<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{v}</svg>' for k, v in {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 7 10-7"/>',
    "pin": '<path d="M12 22s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    "play": '<path d="M6 4l14 8-14 8z" fill="currentColor" stroke="none"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "trophy": '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 5h3a2 2 0 0 1-2 4h-1M7 5H4a2 2 0 0 0 2 4h1"/>',
    "ig": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>',
    "fb": '<path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H7v4h3v6h4v-6h3l1-4h-4V8z"/>',
    "yt": '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="m10 9 5 3-5 3z" fill="currentColor" stroke="none"/>',
}.items()}

def header(current):
    links = "".join(f'<a href="{k}"{" aria-current=page" if k == current else ""}{" rel=noopener target=_blank" if k.startswith("http") else ""}>{l}</a>' for k, l in NAV)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap top-in">
<a class="brand" href="/" aria-label="{NAME} home">{pic('re-logo-light.png', NAME + ' logo', '220px', eager=True, maxw=660)}</a>
<nav class="nav" aria-label="Main">{links}</nav>
<a class="btn btn-pink top-cta" href="/tryouts/">Tryouts{I['arrow']}</a>
<button class="burger" aria-label="Menu" aria-expanded="false" aria-controls="menu"><span></span><span></span><span></span></button>
</div></header>
<div class="menu-panel" id="menu" hidden><nav aria-label="Mobile">{links}<a href="{TRYOUTS_URL}" rel="noopener" class="btn btn-pink">Register for Tryouts</a><a href="tel:{TEL}" class="btn btn-line">{PHONE}</a></nav></div>"""

def footer():
    return f"""<footer class="foot"><div class="wrap foot-grid">
<div class="foot-brand">{pic('re-logo-light.png', NAME, '200px', maxw=600)}<p>Rebel Elite FC is the girls' program of <a href="{IGNITE}" rel="noopener">Ignite FC</a> — competitive club soccer in St. George, Utah for ages U8–U19.</p>
<p class="soc"><a href="{INSTAGRAM}" rel="noopener" aria-label="Instagram">{I['ig']}</a><a href="{FACEBOOK}" rel="noopener" aria-label="Facebook">{I['fb']}</a><a href="{YOUTUBE}" rel="noopener" aria-label="YouTube">{I['yt']}</a></p></div>
<div><h3>Club</h3>{"".join(f'<a href="{k}">{l}</a>' for k, l in NAV if not k.startswith("http"))}<a href="{IGNITE}" rel="noopener">Ignite FC (boys)</a></div>
<div><h3>Players</h3><a href="{TRYOUTS_URL}" rel="noopener">Tryout registration</a><a href="/tryouts/#faq">Tryout FAQ</a><a href="/teams/#age-chart">Age group chart</a><a href="{STORE_KIT}" rel="noopener">Rebel kit (soccer.com)</a><a href="{STORE_FAN}" rel="noopener">Fan store</a><a href="{ZCC}" rel="noopener">Zion Champions Cup</a></div>
<div><h3>Contact</h3><a href="tel:{TEL}">{PHONE}</a><a href="mailto:{EMAIL}">{EMAIL}</a><span>{FIELDS_TRYOUT}<br>{CITY}, {STATE}</span></div>
</div><div class="wrap foot-base"><span>© {YEAR} Ignite FC LLC, DBA Rebel Elite. All rights reserved.</span><span><a href="/privacy-policy/">Privacy</a><a href="/sitemap/">Sitemap</a></span></div></footer>"""

LD_ORG = {"@context": "https://schema.org", "@type": "SportsOrganization", "@id": DOMAIN + "/#org", "name": NAME, "alternateName": ["Rebel Elite", "Ignite FC Rebel Elite"], "sport": "Soccer", "url": DOMAIN,
          "logo": DOMAIN + "/assets/logo.png", "telephone": TEL, "email": EMAIL, "sameAs": [FACEBOOK, INSTAGRAM, YOUTUBE, IGNITE], "parentOrganization": {"@type": "SportsOrganization", "name": "Ignite FC", "url": IGNITE},
          "foundingDate": "2018", "memberOf": [{"@type": "Organization", "name": "Utah Youth Soccer Association"}, {"@type": "Organization", "name": "US Club Soccer"}],
          "address": {"@type": "PostalAddress", "addressLocality": CITY, "addressRegion": STATE, "addressCountry": "US"},
          "areaServed": ["St. George, UT", "Washington County, UT", "Southern Utah", "Mesquite, NV"],
          "description": "Girls' competitive club soccer (U8–U19) in St. George, Utah — the girls' program of Ignite FC. Two-time Presidents Cup national champions."}

SITE_JS = """(function(){var b=document.querySelector('.burger'),m=document.getElementById('menu');if(b&&m){b.addEventListener('click',function(){var o=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',!o);m.hidden=o;document.body.classList.toggle('menu-open',!o)})}
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -10% 0px'});document.querySelectorAll('.rv').forEach(function(el){io.observe(el)})}else{document.querySelectorAll('.rv').forEach(function(el){el.classList.add('in')})}})();"""

CSS_V = hashlib.md5((HERE / "site.css").read_bytes()).hexdigest()[:8]
REGISTRY = []
def page(key, title, desc, body, current=None, ld=None, robots="index,follow"):
    canon = DOMAIN + key
    if PREVIEW: robots = "noindex,nofollow"
    lds = [LD_ORG] + (ld or [])
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}"><meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}/assets/og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0b0f">
<link rel="icon" href="/assets/icon.png" type="image/png"><link rel="apple-touch-icon" href="/assets/icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/site.css?v={CSS_V}">
{''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)}
</head>
<body>
{header(current)}
<main id="main">
{body}
</main>
{footer()}
<script>{SITE_JS}</script>
</body>
</html>"""
    REGISTRY.append((key, rebase(doc)))

def rebase(html):
    if not BASE: return html
    html = re.sub(r'((?:href|src)=")/(?!/)', r'\1' + BASE + '/', html)
    html = re.sub(r'(srcset="[^"]*)', lambda m: m.group(1).replace(' /img/', ' ' + BASE + '/img/').replace('="/img/', '="' + BASE + '/img/'), html)
    return html

def crumbs(items):
    li = "".join(f'<li><a href="{k}">{esc(l)}</a></li>' if n < len(items) - 1 else f'<li aria-current="page">{esc(l)}</li>' for n, (k, l) in enumerate(items))
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": n + 1, "name": l, "item": DOMAIN + k} for n, (k, l) in enumerate(items)]}
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{li}</ol></nav>', ld

def pagehead(items, kicker, h1, sub="", photo=None, alt="", top=0.3):
    c, ld = crumbs(items)
    bg = f'<div class="ph-bg">{pic(photo, alt, "100vw", eager=True, crop=(16, 7), top=top)}</div>' if photo else ""
    return f"""<section class="phead{' has-bg' if photo else ''}">{bg}<div class="wrap phead-in">{c}<p class="kicker">{esc(kicker)}</p><h1>{esc(h1)}</h1>{f'<p class="lead">{esc(sub)}</p>' if sub else ''}</div></section>""", ld

def cta_band(h="Ready to play for Rebel Elite?", p="Girls U8–U19 in St. George. Tryouts every June — evaluations year-round.", btn="Register for Tryouts", href=TRYOUTS_URL):
    return f"""<section class="band rv"><div class="wrap band-in"><div><h2>{esc(h)}</h2><p>{esc(p)}</p></div><div class="band-acts"><a class="btn btn-pink btn-lg" href="{href}" rel="noopener">{esc(btn)}{I['arrow']}</a><a class="btn btn-ghost" href="tel:{TEL}">{I['phone']}{PHONE}</a></div></div></section>"""

def faq_block(items, idp="faq", kicker="Questions", h="Frequently asked"):
    html = "".join(f'<details class="faq"{" open" if n == 0 else ""}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for n, (q, a) in enumerate(items))
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}
    return f'<section class="sec" id="{idp}"><div class="wrap narrow"><p class="kicker">{esc(kicker)}</p><h2>{esc(h)}</h2>{html}</div></section>', ld

def honors_list(n=None):
    items = HONORS if n is None else HONORS[:n]
    return '<ol class="honors">' + "".join(f'<li class="rv"><span class="h-when">{esc(w)}</span><span class="h-what">{esc(t)}</span></li>' for w, t in items) + "</ol>"

def age_chart():
    rows = "".join(f"<tr><td>{y}</td><td>{a}</td><td>{b}</td></tr>" for y, a, b in AGE_CHART)
    return f"""<div class="chart-wrap"><table class="chart"><caption>2026-27 age groups — UYSA school-year alignment (August 1 cutoff)</caption><thead><tr><th>Birth year</th><th>Born Jan–Jul</th><th>Born Aug–Dec</th></tr></thead><tbody>{rows}</tbody></table></div>"""

# ---------------------------------------------------------------- pages
def home():
    stats = "".join(f'<div class="stat rv"><strong>{esc(n)}</strong><span>{esc(l)}</span></div>' for n, l in STATS)
    teams = "".join(f'<a class="team-card rv" href="/teams/#{s}"><span class="tc-stage">{esc(st)}</span><strong>{esc(lbl)}</strong><span class="tc-years">Born {esc(yrs)}</span><span class="tc-go">View teams{I["arrow"]}</span></a>' for s, lbl, yrs, st, _ in STAGES)
    body = f"""
<section class="hero"><div class="hero-bg">{pic('hero-2025-pc-champs.jpg', 'Rebel Elite 2012 Black — 2025 Presidents Cup U13 state champions, St. George, Utah', '100vw', eager=True, crop=(16, 9), top=0.45)}</div>
<div class="wrap hero-in"><p class="kicker">Girls' competitive club soccer · St. George, Utah</p>
<h1>Building individual <em>character</em> through girls' soccer in Southern Utah.</h1>
<p class="lead">Rebel Elite FC is the girls' program of Ignite FC — two-time Presidents Cup national champions, 24 teams from U8 to U19, and a pathway from Little Valley to college soccer.</p>
<div class="hero-acts"><a class="btn btn-pink btn-lg" href="/tryouts/">Tryouts{I['arrow']}</a><a class="btn btn-ghost btn-lg" href="/teams/">Find your age group</a></div></div></section>

<section class="stats"><div class="wrap stats-in">{stats}</div></section>

<section class="sec"><div class="wrap split">
<div class="rv"><p class="kicker">Why Rebel Elite</p><h2>Hometown club. National standard.</h2>
<p>Rebel Elite started so St. George girls didn't have to drive to Las Vegas or Salt Lake for elite soccer. Today our teams win state titles every January and have brought two national championships home to Southern Utah — with coaches who know every player by name and push each one to get better every week.</p>
<ul class="checks"><li>{I['check']}24 girls' teams, U8 through U19 — a team for every level</li><li>{I['check']}Licensed, background-checked coaches at every session</li><li>{I['check']}Goalkeeper-specific training included</li><li>{I['check']}State Cup, Presidents Cup &amp; showcase tournaments</li><li>{I['check']}Volunteer-run club — low fees, tournaments chosen by each team</li></ul>
<a class="btn btn-line" href="/about/">Our story{I['arrow']}</a></div>
<figure class="rv">{pic('re-rebel.jpg', 'Rebel Elite FC team with Presidents Cup medals', '(max-width:900px) 100vw, 560px', crop=(4, 3), maxw=1200)}</figure>
</div></section>

<section class="sec dark" id="teams"><div class="wrap"><p class="kicker">Age groups</p><h2>Girls' teams, U8 to U19.</h2><p class="lead">Find your player's age group for the {SEASON} season — now aligned to school year (August 1 cutoff).</p><div class="team-grid">{teams}</div></div></section>

<section class="sec nat" id="honors"><div class="wrap split rev">
<figure class="rv">{pic('re-nationals.jpeg', 'Rebel Elite FC girls celebrating the USYS Far West Presidents Cup championship', '(max-width:900px) 100vw, 560px', crop=(4, 3), maxw=1200)}</figure>
<div class="rv"><p class="kicker">Proven on the national stage</p><h2>Two national titles. Three years.</h2>
<p>Rebel Elite Black won the Presidents Cup National Championship at U14 in 2023 and again at U18 in 2025, with a Far West Regional title and two more national-final appearances in between. In January 2026 three Rebel teams won state championships in the same weekend.</p>
{honors_list(4)}
<a class="btn btn-line" href="/about/#honors">Full honors list{I['arrow']}</a></div></div></section>


{cta_band()}"""
    page("/", "Rebel Elite FC | Girls' Club Soccer in St. George, Utah (U8–U19)",
         "Rebel Elite FC is the girls' program of Ignite FC: competitive club soccer in St. George, Utah for ages U8–U19. Two-time Presidents Cup national champions. Tryouts, fees, teams, and coaches.",
         body, "/", [{"@context": "https://schema.org", "@type": "WebSite", "url": DOMAIN, "name": NAME, "publisher": {"@id": DOMAIN + "/#org"}}])

def teams_page():
    head, ld = pagehead([("/", "Home"), ("/teams/", "Teams")], "Age groups & teams", "Girls' soccer teams, U8 to U19.", f"Twenty-four Rebel Elite teams train in St. George and compete in UYSA leagues, cups, and regional tournaments. Here's what to expect at each stage in {SEASON}.", "ig-hero.jpg", "Rebel Elite FC teams", 0.5)
    def teams_for(yrs):
        lo, hi = yrs
        rows = [(y, c) for y, c in TEAMS if lo <= int(str(y)[:4]) <= hi]
        if not rows: return ""
        return '<ul class="roster">' + "".join(f'<li><strong>Rebel Elite {y} {c}</strong></li>' for y, c in rows) + "</ul>"
    ranges = {"u8-u10": (2017, 2018), "u11-u12": (2015, 2016), "u13-u14": (2013, 2014), "u15-u16": (2011, 2012), "u17-u19": (2007, 2010)}
    secs = "".join(f"""<article class="team-sec rv" id="{s}"><div class="ts-head"><span class="tc-stage">{esc(st)}</span><h2>{esc(lbl)} Girls</h2><p class="ts-years">Birth years {esc(yrs)}</p></div><div class="ts-body"><p>{esc(b)}</p>
<h3 class="h-small">{SEASON} teams</h3>{teams_for(ranges[s])}
<p class="small">Coaches for each team are announced after tryouts. Contact the club for your team's coach.</p>
<dl class="meta"><div><dt>Training</dt><dd>Usually two nights a week · {FIELDS_TRAIN}</dd></div><div><dt>Games</dt><dd>Fall &amp; spring UYSA seasons, 8–15 games each · mostly at the {FIELDS_GAMES}</dd></div></dl>
<a class="btn btn-pink" href="/tryouts/">Tryouts{I['arrow']}</a></div></article>""" for s, lbl, yrs, st, b in STAGES)
    alumni = '<ul class="roster">' + "".join(f'<li><strong>Rebel Elite {y} {c}</strong></li>' for y, c in ALUMNI_TEAMS) + "</ul>"
    faq, fld = faq_block([("Which team will my daughter be placed on?", "Placement is by age group first, then by tryout evaluation. Black is typically the top team in an age group, followed by White and Pink. Players may be invited to play up when it is right for their development."),
                          ("Can teams play across age groups?", "Under the new school-year alignment, teams are not forced to split, but most players will play in the older of two possible groups. Play-down exceptions are reviewed case by case and granted for one year only."),
                          ("Do you have boys' teams?", "Boys play for Ignite FC, our parent club, under the same coaching philosophy. Visit ignitefc.com."),
                          ("How many tournaments do teams play?", "Each team chooses and funds its own tournaments. Younger teams typically play 2–4 a year; older teams 5–8, including State Cup, Presidents Cup, and college showcases like our own Zion Champions Cup.")], "teams-faq")
    body = head + f'<section class="sec"><div class="wrap narrow">{secs}<article class="team-sec rv" id="alumni"><div class="ts-head"><span class="tc-stage">Alumni</span><h2>Graduated teams</h2></div><div class="ts-body"><p>The teams that put Rebel Elite on the map — including the 2025 national champions.</p>{alumni}</div></article></div></section>'
    body += f'<section class="sec dark" id="age-chart"><div class="wrap narrow rv"><p class="kicker">Which age group?</p><h2>{SEASON} age group chart.</h2><p>UYSA moved to a school-year alignment for 2026-27. Find your player\'s birth year and birth month.</p>{age_chart()}<p class="small">Example: a player born March 2018 plays U9; a player born September 2018 plays U8. U8 players may play up with U9.</p></div></section>' + faq + cta_band()
    page("/teams/", "Girls' Soccer Teams U8–U19 & Age Group Chart | Rebel Elite FC, St. George UT", f"Rebel Elite FC fields 24 competitive girls' soccer teams from U8 to U19 in St. George, Utah. See teams, coaches, the {SEASON} age group chart, training and how to try out.",
         body, "/teams/", [ld, fld])

def tryouts_page():
    head, ld = pagehead([("/", "Home"), ("/tryouts/", "Tryouts")], f"{SEASON} season", "Girls' soccer tryouts in St. George, Utah.", "Girls U8–U19. Register online, show up ready to play, and let the coaches see what you've got.", "re-nationals.jpeg", "Rebel Elite FC players", 0.35)
    faq, fld = faq_block(FAQ_TRYOUTS)
    body = head + f"""
<section class="sec"><div class="wrap split">
<div class="rv"><p class="kicker">How it works</p><h2>Three steps to a Rebel jersey.</h2>
<ol class="steps"><li><strong>Register online.</strong> Registration runs through Ollie Sports and takes about three minutes. It opens each spring; UYSA rules keep every Utah club's tryouts in the same early-June window.</li><li><strong>Come to tryouts.</strong> Bring water, a ball, cleats, and shin guards. Sessions run by age group at {FIELDS_TRYOUT} — arrive 15–20 minutes early for check-in.</li><li><strong>Get your offer.</strong> Coaches contact families within a few days of the final session with team placement and next steps.</li></ol>
<a class="btn btn-pink btn-lg" href="{TRYOUTS_URL}" rel="noopener">Register on Ollie{I['arrow']}</a></div>
<aside class="card rv"><h3>Tryout details</h3><dl class="meta"><div><dt>Who</dt><dd>Girls U8–U19 (born 2007–2018)</dd></div><div><dt>Where</dt><dd>{FIELDS_TRYOUT}, St. George, UT</dd></div><div><dt>When</dt><dd>First week of June each year; times by age group posted each spring</dd></div><div><dt>Cost</dt><dd>Tryouts are free</dd></div><div><dt>Missed it?</dt><dd>Year-round evaluations when rosters have room</dd></div><div><dt>Questions</dt><dd><a href="tel:{TEL}">{PHONE}</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></dd></div></dl></aside>
</div></section>
<section class="sec dark" id="fees"><div class="wrap split"><div class="rv"><p class="kicker">What it costs</p><h2>Straightforward fees. No surprises.</h2><p>Rebel Elite is run by volunteer board members and coaches, so the club fee stays low and every team controls its own tournament budget. The current season's fee sheet is published on ignitefc.com before tryouts.</p><a class="btn btn-ghost" href="{FEES_URL}" rel="noopener">Current fee sheet{I['arrow']}</a></div>
<div class="fees rv"><div><strong>Club fee</strong><span>Per player, per season<br><small>Covers coaching, club administration and fields, plus a team equipment fund</small></span></div><div><strong>UYSA</strong><span>League registration<br><small>Paid directly to Utah Youth Soccer; varies by age</small></span></div><div><strong>Kit</strong><span>adidas Rebel uniform<br><small>Home &amp; away jerseys, socks and training top · ordered on <a href="{STORE_KIT}" rel="noopener">soccer.com</a></small></span></div><div><strong>Tournaments</strong><span>Chosen by each team<br><small>Funded by the team and often offset by local sponsors</small></span></div></div></div></section>
<section class="sec"><div class="wrap narrow rv"><p class="kicker">Missed tryouts?</p><h2>We evaluate players year-round.</h2><p>Rosters have room more often than you'd think, especially in younger age groups. Email us your player's birth year and experience and we'll set up a training evaluation with the right team. Out of town? Send a name and birthdate and we'll connect you with a coach.</p><a class="btn btn-pink" href="mailto:{EMAIL}?subject=Player%20evaluation">Request an evaluation{I['arrow']}</a></div></section>""" + faq + cta_band()
    page("/tryouts/", f"Girls' Soccer Tryouts, St. George Utah | Rebel Elite FC {SEASON}", f"Rebel Elite FC girls' soccer tryouts in St. George, Utah: ages U8–U19, held each June at Sullivan Soccer Complex, free to attend. What to bring, what it covers, and year-round evaluations.",
         body, "/tryouts/", [ld, fld])


def about_page():
    head, ld = pagehead([("/", "Home"), ("/about/", "About")], "Our story", "Southern Utah's rebel club.", "Started so St. George girls didn't have to drive to Las Vegas or Salt Lake for elite soccer. Now a two-time national champion.", "re-rebel.jpg", "Rebel Elite FC team", 0.3)
    body = head + f"""
<section class="sec"><div class="wrap narrow prose rv">
<h2>Why we exist</h2>
<p>For years the best young players in Washington County had two choices: settle for recreational soccer, or spend weekends on I-15 chasing clubs in Las Vegas and the Wasatch Front. Ignite FC was founded around a St. George kitchen table in May 2018 to give local kids a third option — real coaching, real competition, and a real club family, at home.</p>
<p>Rebel Elite grew up alongside it as a girls' program and joined the Ignite FC family in March 2023. Within four months a Rebel team had won a national championship. We stayed close-knit on purpose: our coaches know every player's name, strengths, and goals, and we measure success by how much each girl improves — and by who she becomes along the way.</p>
<h2 id="values">What we stand for</h2>
<div class="values"><div><strong>Character first</strong><p>Effort, respect, and accountability are coached as deliberately as a first touch.</p></div><div><strong>Development over trophies</strong><p>We play to win, but we never trade a player's long-term growth for a short-term result.</p></div><div><strong>Club family</strong><p>Parents, siblings, and sponsors are part of the team. Nobody travels to Nationals alone.</p></div><div><strong>Southern Utah proud</strong><p>We represent St. George everywhere we go — and we go far.</p></div></div>
</div></section>
<section class="sec dark" id="honors"><div class="wrap split rev"><figure class="rv">{pic('re-nationals.jpeg', 'Rebel Elite FC girls, USYS Far West Presidents Cup champions', '(max-width:900px) 100vw, 560px', crop=(3, 2), maxw=1200)}</figure>
<div class="rv"><p class="kicker">Honors</p><h2>From Mesquite to Wichita — and back with the trophy.</h2>
<p>Rebel Elite teams have won state titles every year since joining Ignite FC, and twice gone all the way at the Presidents Cup National Championship.</p>{honors_list()}</div></div></section>
<section class="sec" id="college"><div class="wrap narrow prose rv"><p class="kicker">College pathway</p><h2>From Rebel Elite to the next level.</h2>
<p>Our U15–U19 program is built around what college coaches actually look for: technical quality, game intelligence, athleticism, and character. Players get help building highlight film, a recruiting profile, a target-school list, and introductions at showcase events — plus honest guidance from coaches who have played at the college level.</p>
<p>Rebel alumni have gone on to play NCAA and NJCAA soccer. <em>[CONFIRM: college placements to list]</em></p></div></section>
<section class="sec dark"><div class="wrap narrow rv"><p class="kicker">Part of Ignite FC</p><h2>One club, two crests.</h2><p>Rebel Elite is the girls' side of Ignite FC — Southern Utah's elite soccer experience. Boys play as Ignite in orange; girls play as Rebel Elite in pink and black. Same board, same registrar, same standards, and the same home at the Sullivan and Little Valley fields. Ignite FC is a member of the Utah Youth Soccer Association and, since 2026, US Club Soccer, and hosts the Zion Champions Cup every fall.</p><p class="acts"><a class="btn btn-ghost" href="{IGNITE}" rel="noopener">Visit ignitefc.com{I['arrow']}</a> <a class="btn btn-ghost" href="{ZCC}" rel="noopener">Zion Champions Cup{I['arrow']}</a></p></div></section>""" + cta_band()
    page("/about/", "About Rebel Elite FC | Girls' Soccer Club in St. George, Utah", "The story of Rebel Elite FC, the girls' program of Ignite FC in St. George, Utah: founded 2018, two Presidents Cup national championships, state titles every year, and a college pathway.",
         body, "/about/", [ld])


def contact_page():
    head, ld = pagehead([("/", "Home"), ("/contact/", "Contact")], "Contact", "Get in touch.", "Tryouts, evaluations, sponsorships, or just a question — we answer every message.")
    body = head + f"""
<section class="sec"><div class="wrap split">
<div class="rv"><div class="contact-list"><a href="tel:{TEL}">{I['phone']}<span><strong>Call or text</strong>{PHONE}</span></a><a href="mailto:{EMAIL}">{I['mail']}<span><strong>Email</strong>{EMAIL}</span></a><a href="https://www.google.com/maps/search/?api=1&query=Sullivan+Soccer+Complex+St+George+UT" rel="noopener">{I['pin']}<span><strong>Tryouts &amp; training</strong>{FIELDS_TRYOUT} · Little Valley, {CITY}, {STATE}</span></a><a href="{INSTAGRAM}" rel="noopener">{I['ig']}<span><strong>Instagram</strong>@rebelelitefc</span></a></div></div>
<aside class="card rv"><h3>Quick links</h3><a class="btn btn-pink" href="{TRYOUTS_URL}" rel="noopener">Register for Tryouts{I['arrow']}</a><a class="btn btn-line" href="mailto:{EMAIL}?subject=Player%20evaluation">Request an evaluation</a><a class="btn btn-line" href="mailto:{EMAIL}?subject=Sponsoring%20Rebel%20Elite%20FC">Sponsor a team</a><a class="btn btn-line" href="{STORE_KIT}" rel="noopener">Order the Rebel kit</a></aside></div></section>
<section class="map"><iframe title="Sullivan Soccer Complex map" src="https://www.google.com/maps?q=Sullivan+Soccer+Complex,+St.+George,+UT&output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></section>"""
    page("/contact/", "Contact Rebel Elite FC | St. George, Utah Girls' Soccer Club", f"Contact Rebel Elite FC girls' soccer club in St. George, Utah: call or text {PHONE}, email {EMAIL}, or find us at {FIELDS_TRYOUT}.", body, "/contact/", [ld])

def legal_pages():
    head, ld = pagehead([("/", "Home"), ("/privacy-policy/", "Privacy Policy")], "Legal", "Privacy policy")
    body = head + f"""<section class="sec"><div class="wrap narrow prose"><p>Effective {datetime.date.today():%B %d, %Y}.</p>
<p>Rebel Elite FC (Ignite FC LLC, "we") operates rebelelitefc.com. This website does not collect personal information directly. Tryout registration is handled by Ollie Sports and kit orders by soccer.com under their own privacy policies, and email you send us is used only to respond to you.</p>
<p>We do not sell personal information. Embedded content (Google Maps) may set cookies governed by those providers. Questions: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div></section>"""
    page("/privacy-policy/", "Privacy Policy | Rebel Elite FC", "Rebel Elite FC privacy policy.", body, None, [ld], robots="noindex,follow")

def sitemap_page():
    links = "".join(f'<li><a href="{k}">{esc(l)}</a></li>' for k, l in [("/", "Home")] + [n for n in NAV if not n[0].startswith("http")] + [("/privacy-policy/", "Privacy Policy")])
    head, ld = pagehead([("/", "Home"), ("/sitemap/", "Sitemap")], "Sitemap", "Every page on our site.")
    page("/sitemap/", "Sitemap | Rebel Elite FC", "All pages on rebelelitefc.com.", head + f'<section class="sec"><div class="wrap narrow prose"><ul>{links}</ul></div></section>', None, [ld])

home(); teams_page(); tryouts_page(); about_page(); contact_page(); legal_pages(); sitemap_page()

# ---------------------------------------------------------------- redirects (old WordPress URLs)
REDIRECTS = {
    "/tournaments/": "/teams/", "/rebels-at-nationals/": "/about/#honors", "/rebel-elite-fc-2006-presidents-cup/": "/about/#honors",
    "/2024-2025-sponsorships/": "/contact/", "/raffle/": "/contact/", "/sponsors/": "/contact/", "/coaches/": "/about/", "/shop/": STORE_FAN, "/product/rebel-elite-fc-unisex-hoodie/": STORE_FAN,
    "/cart/": "/", "/checkout/": "/", "/my-account/": "/", "/payment-confirmation/": "/", "/payment-failed/": "/", "/hello-world/": "/", "/coaches-2/": "/about/",
}
def redirect(to):
    canon = to if to.startswith("http") else DOMAIN + to.split("#")[0]
    if not to.startswith("http"): to = BASE + to
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{NAME}</title><meta name="robots" content="noindex"><link rel="canonical" href="{canon}"><meta http-equiv="refresh" content="0; url={to}"><script>location.replace({json.dumps(to)})</script></head><body><a href="{to}">Continue</a></body></html>'

# ---------------------------------------------------------------- write
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
for key, doc in REGISTRY:
    p = OUT / key.strip("/") / "index.html"; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(doc)
for old, new in REDIRECTS.items():
    p = OUT / old.strip("/") / "index.html"; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(redirect(new))
(OUT / "img").mkdir(exist_ok=True)
for rel in IMG_OUT: shutil.copy(CACHE / Path(rel).name, OUT / rel)
shutil.copy(HERE / "site.css", OUT / "site.css")
(OUT / "assets").mkdir(exist_ok=True)
Image.open(IMG / "re-ball-icon.png").convert("RGBA").resize((192, 192), Image.LANCZOS).save(OUT / "assets/icon.png")
lg = Image.open(IMG / "re-logo-darkpink.png").convert("RGBA"); lg.thumbnail((1200, 1200)); lg.save(OUT / "assets/logo.png")
og = ImageOps.fit(Image.open(IMG / "hero-2025-pc-champs.jpg").convert("RGB"), (1200, 630), Image.LANCZOS, centering=(0.5, 0.5))
d = ImageDraw.Draw(og, "RGBA"); d.rectangle((0, 0, 1200, 630), fill=(11, 11, 15, 120))
logo = Image.open(IMG / "re-logo-light.png").convert("RGBA"); logo = logo.resize((720, round(logo.height * 720 / logo.width)), Image.LANCZOS)
og.paste(logo, ((1200 - logo.width) // 2, (630 - logo.height) // 2), logo); og.save(OUT / "assets/og.jpg", quality=86)
nf = [d for k, d in REGISTRY if k == "/"][0]
(OUT / "404.html").write_text(rebase(re.sub(r'(?s)<main id="main">.*</main>', '<main id="main"><section class="phead"><div class="wrap phead-in"><p class="kicker">404</p><h1>That page went out of bounds.</h1><p class="lead">It may have moved when we rebuilt the site.</p><p><a class="btn btn-pink" href="/">Home</a> <a class="btn btn-line" href="/tryouts/">Tryouts</a></p></div></section></main>', nf).replace('<meta name="robots" content="index,follow">', '<meta name="robots" content="noindex">')))
today = datetime.date.today().isoformat()
urls = [k for k, _ in REGISTRY if k not in ("/privacy-policy/",)]
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{DOMAIN}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls) + "</urlset>\n")
for old in ("wp-sitemap.xml", "sitemap_index.xml", "page-sitemap.xml"): (OUT / old).write_text((OUT / "sitemap.xml").read_text())
if PREVIEW:
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
else:
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /cart/\nDisallow: /checkout/\nDisallow: /my-account/\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    (OUT / "CNAME").write_text("rebelelitefc.com\n")
(OUT / ".nojekyll").write_text("")
print(f"built {len(REGISTRY)} pages, {len(REDIRECTS)} redirects, {len(IMG_OUT)} images -> {OUT}")
