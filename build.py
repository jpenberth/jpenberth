#!/usr/bin/env python3
"""Static site generator for jpenberth.com. Run: python3 build.py  (writes HTML into the repo root)."""
import os, html, json, shutil, hashlib

def ver(*paths):
    h = hashlib.md5()
    for p in paths: h.update(open(p, "rb").read())
    return h.hexdigest()[:8]

V = ver("assets/css/site.css", "assets/js/site.js")

SITE = "https://jpenberth.com"
NAME = "J. Penberth Rabold"
TAG = "Director & Storyteller"
EMAIL = "jpenberth@jpenberth.com"
DESC = "J. Penberth Rabold is a writer and director with 15+ years in Los Angeles film production. Short films, music videos, and Dallas & Allegra, a Rust Belt love story."
NAV = [("/", "Home"), ("/filmography/", "Filmography"), ("/writing/", "Writing"), ("/biography/", "Biography"), ("/contact/", "Contact")]
SEEDSPARK = "https://seedandspark.com/fund/dallasallegra"
SUBSTACK = "https://jpenberth.substack.com"
IMDB = "https://www.imdb.com/name/nm2399602/"
CONTACT_ENDPOINT = "https://script.google.com/macros/s/AKfycbyFgmWsRTny86lZPNbt339hFsoIrca3PU70LCfMWVuL0vDDFVB7vulFpC5192PY3Bxu/exec"   # paste the Google Apps Script web-app URL here (see tools/google-apps-script/Code.gs)
YT_DIRECTING = "https://www.youtube.com/@j.penberthraboldstorytelle7092"
YT_PODCAST = "https://www.youtube.com/@whatsurwhypodcast"
VIMEO = "https://vimeo.com/lydianpictures"
INSTAGRAM = "https://www.instagram.com/jpenberthstoryteller/"
DA_SITE = "https://dallasandallegra.com"

# kind: yt / vimeo / none. status: released / coming
PROJECTS = [
 dict(slug="way-too-soon", title="Way Too Soon", year="", kind="Music Video", yt="9kDtB5f8ZFA", status="released",
      log="Official music video for Jacob Luttrell's “Way Too Soon.”", runtime="4:36"),
 dict(slug="connected", title="Connected", year="2019", kind="Short Film", yt="T78zgx4-O2k", status="released", runtime="6:19",
      log="A young woman struggles to find an authentic connection with her father in a technologically connected world.",
      awards=["Filmmakers Collaboration Challenge 2019 — Runner-Up, Jury Prize", "Filmmakers Collaboration Challenge 2019 — Runner-Up, Best Visuals"]),
 dict(slug="familiar-faces", title="Familiar Faces", year="2020", kind="Music Video", yt="H98SCB794-o", status="released", runtime="6:11",
      log="Official music video for Jacob Luttrell's “Familiar Faces.”"),
 dict(hidden=True, slug="one-gloved-rider", title="One Gloved Rider", year="2020", kind="Short Film", vimeo="531735478", status="released", runtime="5:18",
      log="Samuel, who considers himself a true biker, attempts to join the Skull Crushers Bike Club."),
 dict(slug="almost-super", title="Almost Super", year="2020", kind="Pilot Proof of Concept", status="released", img="almost-super.jpg",
      log="An action-comedy pilot proof of concept starring French Stewart, Bryan Dodds and Laur Allen, about a group of wannabe superheroes who team up with a former supervillain to join the International League of Superheroes."),
 dict(slug="palm-springs-weekend", title="Palm Springs Weekend", year="", kind="Music Video", yt="feY4qLSIRXA", status="released", runtime="",
      log="Official music video for Jacob Luttrell's “Palm Springs Weekend.”"),
 dict(hidden=True, slug="toxic-city", title="Toxic City", year="", kind="Album Film", status="coming",
      log="A groundbreaking album film experience for the new album “The Stupidity of Validity” from Grammy-winning singer-songwriter Jacob Luttrell."),
 dict(hidden=True, slug="devilwood", title="Devilwood", year="", kind="Feature", status="coming",
      log="A psychological thriller about three girlfriends on a weekend getaway to repair their fractured friendships, who get sucked into a time portal inside a once-abandoned theme park. Their freedom can only be bought with one thing... blood."),
 dict(hidden=True, slug="dallas-and-allegra", title="Dallas & Allegra", year="", kind="In Development", status="coming",
      log="She's got a plane ticket to Oxford. He's got a safe full of cash and one last score. In a steel town built on dead dreams, they fall for each other anyway."),
]

ALL_PROJECTS = PROJECTS
PROJECTS = [p for p in ALL_PROJECTS if not p.get("hidden")]  # hidden ones keep their data but are not built

import re as _re
def ext_links(h):
    """Open every outside http(s) link in a new tab, safely."""
    def fix(m):
        tag = m.group(0)
        if not _re.search(r'href="https?://', tag) or 'target=' in tag: return tag
        if 'rel="' in tag:
            tag = _re.sub(r'rel="([^"]*)"', lambda r: 'rel="' + (r.group(1) if 'noopener' in r.group(1) else r.group(1) + ' noopener') + '"', tag, 1)
        else:
            tag = tag[:-1] + ' rel="noopener"' + '>'
        return tag[:-1] + ' target="_blank">'
    return _re.sub(r'<a\s[^>]*>', fix, h)

def esc(s): return html.escape(s, quote=True)

def thumb(p):
    local = f"assets/img/stills/{p.get('img', p['slug']+'.jpg')}"
    if os.path.exists(local): return "/" + local
    if p.get("yt"): return f"https://i.ytimg.com/vi/{p['yt']}/hqdefault.jpg"
    return None

def OG_FOR(path):
    """pick the share image for a page: its own if one was generated, else the home one"""
    name = {"/": "og-home.jpg", "/filmography/": "og-filmography.jpg", "/writing/": "og-writing.jpg", "/credits/": "og-credits.jpg",
            "/biography/": "og-biography.jpg", "/contact/": "og-contact.jpg", "/projects/dallas-and-allegra/": "og-dallas-and-allegra.jpg"}.get(path)
    if not name and path.startswith("/projects/"):
        name = "og-" + path.strip("/").split("/")[-1] + ".jpg"
    return name if name and os.path.exists("assets/img/" + name) else "og-home.jpg"

def head(title, desc, path, extra="", og_img=None):
    url = SITE + path
    img = og_img or (SITE + "/assets/img/" + OG_FOR(path))
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="{NAME}"><meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{img}">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@300;400&family=Barlow+Condensed:wght@500;600&family=Playfair+Display:ital@0;1&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={V}">
{extra}</head>"""

def header(path):
    links = "".join(f'<a href="{h}"{" class=on aria-current=page" if (h==path or (h!="/" and path.startswith(h))) else ""}>{t}</a>' for h, t in NAV)
    return f"""<header class="top"><a class="tag" href="/">[ {TAG.upper()} ]</a>
<button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
<nav>{links}</nav>
<div class="social"><a href="{INSTAGRAM}" aria-label="Instagram" rel="me noopener"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.3" cy="6.7" r=".6" fill="currentColor"/></svg></a><a href="{YT_DIRECTING}" aria-label="YouTube" rel="me noopener"><svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor" aria-hidden="true"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg></a></div></header>"""

def footer():
    links = [("Credits", "/credits/"), ("IMDb", IMDB), ("Instagram", INSTAGRAM), ("YouTube", YT_DIRECTING), ("Podcast", YT_PODCAST), ("The Writer's Table", SUBSTACK)]
    row = " · ".join(f'<a href="{u}" rel="me noopener">{esc(t)}</a>' for t, u in links)
    return f"""<footer><p class="flinks">{row}</p><p>© {NAME}. <a href="mailto:{EMAIL}">{EMAIL}</a></p></footer><script src="/assets/js/site.js?v={V}" defer></script></body></html>"""

def card(p):
    t = thumb(p)
    img = f'<img src="{t}" alt="{esc(p["title"])} — {esc(p["kind"])}" loading="lazy">' if t else '<div class="ph"></div>'
    badge = '<span class="play" aria-hidden="true"></span>' if (p.get("yt") or p.get("vimeo")) else ''
    meta = " · ".join(x for x in (p["kind"], p["year"]) if x)
    return f'<a class="card" href="/projects/{p["slug"]}/"><div class="thumb">{img}{badge}</div><h3>{esc(p["title"])}</h3><p>{esc(meta)}</p></a>'

def write(path, content):
    d = os.path.join(".", path.strip("/"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf8").write(ext_links(content))

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"

PERSON = {"@context": "https://schema.org", "@type": "Person", "name": NAME, "jobTitle": "Film Director",
          "url": SITE, "email": EMAIL, "image": SITE + "/assets/img/logo-black.png",
          "sameAs": [SUBSTACK, DA_SITE, IMDB, YT_DIRECTING, YT_PODCAST, INSTAGRAM],
          "description": "Writer and director. 15+ years as a unit production manager and first assistant director in Los Angeles; writer of series and features; author of The Writer's Table newsletter.",
          "homeLocation": [{"@type": "Place", "name": "Los Angeles, CA"}, {"@type": "Place", "name": "Pittsburgh, PA"}],
          "knowsAbout": ["Screenwriting", "Film directing", "Short films", "Music videos"]}

def home():
    cards = "".join(card(p) for p in PROJECTS)
    acc = ["Connected — Runner-Up, Jury Prize · Filmmakers Collaboration Challenge 2019", "Connected — Runner-Up, Best Visuals · Filmmakers Collaboration Challenge 2019"]
    return head(f"{NAME} | Film Director & Storyteller", DESC, "/", ld(PERSON)) + f"""<body class="home">{header('/')}
<div class="stage" aria-hidden="false"><video autoplay muted loop playsinline preload="auto" poster="/assets/img/hero-poster.jpg"><source src="/assets/video/hero.mp4" type="video/mp4"></video>
<div class="tint"></div><canvas class="tv" aria-hidden="true"></canvas><div class="scan"></div><div class="roll"></div></div>
<div class="intro"><h1 class="logo"><img src="/assets/img/logo-white.png" alt="{NAME} — Storyteller" width="1515" height="534"></h1></div>
<main class="sheet"><section class="grid wrap"><h2 class="sr">Selected work</h2>{cards}</section>
{story_home()}{da_feature()}{writing_teaser()}</main>{footer()}"""

def filmography():
    cards = "".join(card(p) for p in PROJECTS)
    return head(f"Filmography | {NAME}", f"Short films, music videos and projects in development by director {NAME}.", "/filmography/") + f"""<body>{header('/filmography/')}
<main class="wrap page"><h1>Filmography</h1><section class="grid">{cards}</section></main>{footer()}"""

def biography():
    stats = [("15+", "years as a UPM &amp; 1st AD"), ("2×", "Runner-Up, Filmmakers Collaboration Challenge"), ("Round 2", "Austin Film Festival, <em>Ghosts of War</em>"), ("13K+", "followers on Instagram"), ("1,000+", "readers of The Writer's Table")]
    st = "".join(f'<div><b>{a}</b><span>{c}</span></div>' for a, c in stats)
    return head(f"Biography | {NAME}", f"About {NAME}: a writer and director who spent 15 years running sets in Los Angeles and now makes the stories he writes.", "/biography/", ld(PERSON)) + f"""<body>{header('/biography/')}
<main class="wrap page narrow"><p class="eyebrow">Biography</p><h1 class="serif">{NAME}</h1>
<p class="lede">Writer. Director. Storyteller.</p>
<p>I moved to Los Angeles in 2000 because I wanted to make movies. That was the whole plan. The problem was, I had nothing to say yet. No real voice, no story that was mine. So I learned how movies get made. For fifteen years I worked as a unit production manager and first assistant director, with some editing along the way, on music videos, shorts and features. I learned what a story actually costs once it has to stand up on a set.</p>
<p>Writing never went away. In 2015 I stopped doing it on the side and made it the job. Since then I've written series bibles, pilots and features that have landed on desks at Netflix, Apple, Starz and HBO. I've come close, and I've come close a lot: a show that went down to the wire, a film that stalled at the finish line. I know exactly what &ldquo;almost&rdquo; feels like. I also know it isn't the end of the story.</p>
<div class="stats">{st}</div>
<p>Along the way I directed <a href="/projects/connected/">Connected</a>, a short about a young woman struggling to find an authentic connection with her father in a technologically connected world. It was a Runner-Up for both the Jury Prize and Best Visuals at the 2019 Filmmakers Collaboration Challenge. I developed the series <em>Ghosts of War</em>, a second-round selection at the Austin Film Festival, and I've directed music videos for my friend Jacob Luttrell, including <a href="/projects/way-too-soon/">Way Too Soon</a> and <a href="/projects/familiar-faces/">Familiar Faces</a>.</p>
<p>I believe storytelling is about human connection. I'm drawn to stories about the human experience, in worlds far beyond our own or the past, where characters are put in situations that force them to discover their own self-empowerment. Stories that start a conversation about emotion and truth, and the love that makes us want to survive.</p>
<p>Right now that story is <a href="/projects/dallas-and-allegra/">Dallas &amp; Allegra</a>, a Rust Belt Romeo and Juliet, and the first film I'm making by asking the people who believe in it to help get it made. No gatekeeper, no executive across the table. I'm also studying Film &amp; TV Writing at LA Film School and writing <a href="/writing/">The Writer's Table</a>, a newsletter for screenwriters who are trying to finish what they start.</p>
<p class="quote">Write truth... inspire love.</p>
<p class="verify"><a href="/filmography/">See the films →</a> &nbsp;·&nbsp; <a href="/credits/">All credits →</a> &nbsp;·&nbsp; <a href="{IMDB}" rel="me noopener">IMDb</a></p></main>{footer()}"""

def contact():
    topics = ["Bookings / directing", "Writing / scripts", "Production", "Press", "Something else"]
    opts = "".join(f"<option>{t}</option>" for t in topics)
    return head(f"Contact | {NAME}", f"Contact director {NAME} for bookings, production and general inquiries.", "/contact/") + f"""<body>{header('/contact/')}
<main class="wrap page narrow"><p class="eyebrow">Contact</p><h1 class="serif">Let's talk.</h1>
<p>Bookings, production and general inquiries:</p>
<p class="big"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<!-- TODO(Jason): add manager / representation details after signing -->
<h2 class="formh">Or send a message</h2>
<form id="contact-form" class="cform" data-endpoint="{CONTACT_ENDPOINT}" data-email="{EMAIL}" novalidate>
<label>Name<input name="name" autocomplete="name" required maxlength="120"></label>
<label>Email<input name="email" type="email" autocomplete="email" required maxlength="200"></label>
<label>What's it about?<select name="topic">{opts}</select></label>
<label>Message<textarea name="message" rows="6" required maxlength="4000"></textarea></label>
<input class="hp" name="company" tabindex="-1" autocomplete="off" aria-hidden="true">
<input type="hidden" name="page" value="{SITE}/contact/">
<button class="btn" type="submit">Send message</button>
<p class="fmsg" role="status" aria-live="polite"></p>
</form></main>{footer()}"""

def project(p):
    path = f"/projects/{p['slug']}/"
    if p.get("yt"):
        player = f'<div class="player"><iframe src="https://www.youtube-nocookie.com/embed/{p["yt"]}" title="{esc(p["title"])}" allow="accelerometer; encrypted-media; picture-in-picture; fullscreen" allowfullscreen loading="lazy"></iframe></div>'
    elif p.get("vimeo"):
        player = f'<div class="player"><iframe src="https://player.vimeo.com/video/{p["vimeo"]}?dnt=1" title="{esc(p["title"])}" allow="fullscreen; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>'
    else:
        t = thumb(p)
        player = f'<div class="player still">{"<img src=%s alt=%s>" % (chr(34)+t+chr(34), chr(34)+esc(p["title"])+chr(34)) if t else ""}</div>'
    awards = "".join(f"<li>{esc(a)}</li>" for a in p.get("awards", []))
    schema = {"@context": "https://schema.org", "@type": "Movie" if p["kind"] in ("Short Film", "Feature", "Pilot Proof of Concept") else "CreativeWork",
              "name": p["title"], "description": p["log"], "director": {"@type": "Person", "name": NAME, "url": SITE}, "url": SITE + path}
    if p["year"]: schema["dateCreated"] = p["year"]
    extra = ld(schema)
    if p.get("yt"):
        extra += ld({"@context": "https://schema.org", "@type": "VideoObject", "name": f"{p['title']} — {NAME}", "description": p["log"],
                     "thumbnailUrl": f"https://i.ytimg.com/vi/{p['yt']}/hqdefault.jpg", "embedUrl": f"https://www.youtube.com/embed/{p['yt']}",
                     "uploadDate": (p["year"] or "2020") + "-01-01"})
    meta = " · ".join(x for x in (p["kind"], p["year"], p.get("runtime")) if x)
    return head(f"{p['title']} ({p['kind']}) | {NAME}", p["log"][:155], path, extra, og_img=None) + f"""<body>{header('/filmography/')}
<main class="wrap page"><p class="crumb"><a href="/filmography/">← Filmography</a></p><h1>{esc(p["title"])}</h1><p class="meta">{esc(meta)}</p>
{player}<div class="narrow"><p>{esc(p["log"])}</p><p class="by">Directed by {NAME}</p>{f'<h2>Awards</h2><ul>{awards}</ul>' if awards else ''}</div></main>{footer()}"""


import json as _json
def writing_posts():
    try: return _json.load(open("data/writing.json", encoding="utf8"))
    except Exception: return []

def fmt_date(d):
    import datetime
    return datetime.date.fromisoformat(d).strftime("%b %-d, %Y")

def story_home():
    return f"""<section class="wrap story"><p class="eyebrow">Writer · Director</p>
<h2 class="serif">I tell stories about people trying to find a way to each other.</h2>
<p>Fifteen years on set as a unit production manager and first AD taught me how movies get made. Writing taught me why. Now I make my own, from short films and music videos to a Rust Belt love story called <a href="/projects/dallas-and-allegra/">Dallas &amp; Allegra</a>.</p>
<p><a class="more" href="/biography/">Read my story →</a></p></section>"""

def da_feature():
    return f"""<section class="da"><div class="wrap da-in">
<a class="da-poster" href="/projects/dallas-and-allegra/"><img src="/assets/img/da/poster-vertical.jpg" alt="Dallas &amp; Allegra — a short film, Love Is Destruction" loading="lazy" width="1087" height="1446"></a>
<div><p class="eyebrow">Now / Next</p><h2 class="serif">Dallas &amp; Allegra</h2><p class="lede">Love is destruction.</p>
<p>She's got a plane ticket to Oxford. He's got a safe full of cash and one last score. In a steel town built on dead dreams, they fall for each other anyway, and discover the fastest way out of hell is straight through it, together.</p>
<p class="btns"><a class="btn" href="/projects/dallas-and-allegra/">The film</a><a class="btn ghost" href="{SEEDSPARK}" rel="noopener">Support it on Seed&amp;Spark</a></p></div></div></section>"""

def writing_teaser():
    ps = writing_posts()[:3]
    if not ps: return ""
    li = "".join(f'<li><a href="{p["url"]}" rel="noopener"><span class="d">{fmt_date(p["date"])}</span><strong>{esc(p["title"])}</strong><span class="b">{esc(p["blurb"])}</span></a></li>' for p in ps)
    return f"""<section class="wrap wt"><p class="eyebrow">The Writer's Table</p><h2 class="serif">Notes on craft, from the page and the set.</h2><ul class="posts">{li}</ul><p><a class="more" href="/writing/">All writing →</a></p></section>"""

PODCAST_EPS = [('WwXxVy-aCIQ', 'Writing What You See: Pittsburgh Novelist on Craft & Persistence', 'Patrick McGinty'), ('NxiY7GW6ylU', 'All Your F*cks Disappear at 40 (And Other Truths): Screenwriter Lauren Greenwood on Rejection', 'Lauren Greenwood'), ('o1eX88hF5Gk', 'When Church Breaks You: Pastor JP Robles on Creativity, Faith, and Why God Looks Up From the Bottom', 'JP Robles'), ('L6sN8k8ncDk', 'The Story That Drives Him: Donavan Clark on Passion, Perseverance, and Purpose', 'Donavan Clark'), ('CiraxMcO6k4', 'The Song That Saved His Life: Jacob Luttrell on Pain, Purpose, and Being a Superhero', 'Jacob Luttrell')]

def writing_page():
    eps_li = "".join(f'<li><a href="https://www.youtube.com/watch?v={i}" rel="noopener"><strong>{esc(t)}</strong><span class="b">Guest: {esc(g)}</span></a></li>' for i, t, g in PODCAST_EPS)
    ps = writing_posts()
    li = "".join(f'<li><a href="{p["url"]}" rel="noopener"><span class="d">{fmt_date(p["date"])}</span><strong>{esc(p["title"])}</strong><span class="b">{esc(p["blurb"])}</span></a></li>' for p in ps)
    blog = {"@context": "https://schema.org", "@type": "Blog", "name": "The Writer's Table", "url": SUBSTACK, "author": {"@type": "Person", "name": NAME, "url": SITE},
            "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"], "datePublished": p["date"], "author": {"@type": "Person", "name": NAME}} for p in ps]}
    return head(f"Writing | {NAME}", "The Writer's Table: screenwriting craft, stakes, structure and the life of a working writer, by J. Penberth Rabold.", "/writing/", ld(blog)) + f"""<body>{header('/writing/')}
<main class="wrap page narrow"><h1>Writing</h1>
<p class="lede">I'm a writer first. <em>The Writer's Table</em> is my newsletter for screenwriters and storytellers: how stories work, why scripts fail, and what it takes to keep going. More than a thousand people read it.</p>
<p class="btns"><a class="btn" href="{SUBSTACK}/subscribe" rel="noopener">Subscribe, it's free</a></p>
<ul class="posts big">{li}</ul><p><a class="more" href="{SUBSTACK}/archive" rel="noopener">Full archive on Substack →</a></p>
<div class="pod"><p class="eyebrow">Podcast</p><h2 class="serif">What's Your Why</h2>
<p class="lede">What broke you made you beautiful.</p>
<p>Real conversations with writers, musicians, directors, actors and creators about the fire that drives us, the fear that shapes us, and how both evolve.</p>
<ul class="posts">{eps_li}</ul>
<p><a class="more" href="{YT_PODCAST}" rel="noopener">All episodes on YouTube →</a></p></div></main>{footer()}"""

def da_page():
    path = "/projects/dallas-and-allegra/"
    stills = "".join(f'<img src="/assets/img/da/{n}.jpg" alt="Dallas &amp; Allegra still: {a}" loading="lazy">' for n, a in (("mill-handoff", "the mill handoff"), ("still-here-street", "Bellvue Falls main street"), ("dallas-mirror", "Dallas in the mirror"), ("lit-window", "a lit window")))
    team = [("J. Penberth Rabold", "Writer &amp; Director", "Los Angeles and Pittsburgh-based writer/director with 15+ years as a director, first assistant director and unit production manager across music videos, shorts and features in Los Angeles. Directed the award-winning short <em>Connected</em>; developed the series <em>Ghosts of War</em>, a second-round selection at the Austin Film Festival."),
            ("Shannon Geary", "Producer", "Pittsburgh-area producer and set photographer with 21 years as a music educator and theater director before moving into film production."),
            ("Daniel J. Lennox", "Director of Photography", "Writer/director whose debut feature <em>Jackson's Run</em> won Best Feature at the 2012 CMM Film Festival in New York."),
            ("Jacob Luttrell", "Music Supervisor", "Grammy-credited songwriter performing as <a href='https://jacobisdead.com/' rel='noopener'>JACOBISDEAD</a>. Composes original music for the film.")]
    t = "".join(f"<li><strong>{n}</strong><span>{r}</span><p>{d}</p></li>" for n, r, d in team)
    schema = {"@context": "https://schema.org", "@type": "Movie", "name": "Dallas & Allegra", "alternateName": "Love Is Destruction",
              "description": "A Rust Belt Romeo and Juliet: a fallen quarterback turned dealer and a steel heiress with a plane ticket to Oxford fall for each other in a dying steel town.",
              "director": {"@type": "Person", "name": NAME, "url": SITE}, "author": {"@type": "Person", "name": NAME}, "genre": ["Drama", "Romance", "Crime"],
              "image": SITE + "/assets/img/da/poster-vertical.jpg", "url": SITE + path, "sameAs": [DA_SITE, SEEDSPARK]}
    return head("Dallas & Allegra: Love Is Destruction | " + NAME, "She's got a plane ticket to Oxford. He's got a safe full of cash and one last score. A Rust Belt Romeo and Juliet, written and directed by J. Penberth Rabold.", path, ld(schema)) + f"""<body class="dapage">{header('/projects/')}
<section class="dahero"><img src="/assets/img/da/hero-skyline-wide.jpg" alt="Dallas and Allegra silhouetted before a full moon over the Pittsburgh skyline" width="1672" height="941"><div class="shade"></div></section>
<main class="wrap page narrow dabody"><p class="eyebrow">A short film</p><h1 class="serif">Dallas &amp; Allegra</h1><p class="lede">Love is destruction.</p>
<p class="btns"><a class="btn" href="{SEEDSPARK}" rel="noopener">Support the film on Seed&amp;Spark</a><a class="btn ghost" href="{DA_SITE}" rel="noopener">dallasandallegra.com</a></p>
<h2>The story</h2><p>In Bellvue Falls, everyone is addicted to something. Two young star-crossed lovers are about to choose the most dangerous one: each other.</p>
<p>Dallas Dixon, a fallen quarterback turned dealer, is two payments away from walking out of the only life this town ever offered him. Allegra Cunningham, a trust fund baby and heir to the Cunningham steel fortune, was born on the right side of town and is less than a year from a plane to Oxford.</p>
<p>Then she tracks him down at a local diner to return her addict mother's Oxy. One late-night conversation later, two people who were never supposed to meet believe they can outrun everything.</p>
<p class="quote">A Rust Belt Romeo and Juliet about the ones this town lets disappear, and a love that burns hotter than whatever is trying to put it out.</p>
<div class="stills">{stills}</div>
<h2>The team</h2><ul class="team">{t}</ul></main>{footer()}"""

# --- Credits (from IMDb + production resume). (title, year, role, kind, imdb title id or "")
CREDITS = {
 "Directing, Writing & Editing": [
  ("Letter", "2025", "Director, Editor", "Music Video", ""),
  ("Gone", "2025", "Director, Editor", "Music Video", ""),
  ("Dallas & Allegra", "Now", "Writer, Director", "Short Film", ""),
  ("Way Too Soon", "2022", "Director, Editor", "Music Video", ""),
  ("Palm Springs Weekend", "2022", "Director, Editor", "Music Video", ""),
  ("Toxic City", "2022", "Director, Writer, Executive Producer", "Feature", "tt13918222"),
  ("Almost Super", "2020", "Director, Writer, Editor", "Short Film", "tt11851406"),
  ("Familiar Faces", "2020", "Director, Editor", "Music Video", ""),
  ("Connected", "2019", "Director, Writer, Editor", "Short Film", "tt44702216"),
  ("Second Chances", "2015", "Writer", "Short Film", "tt5212564"),
  ("Dig", "2014", "Writer", "Short Film", "tt4295478"),
  ("“Baby, Know I Love You” (Solaris)", "2013", "Director, Editor", "Music Video", ""),
  ("Candy Apple", "2011", "Writer, Co-Producer", "Short Film", "tt2071472"),
 ],
 "Production: Unit Production Manager & 1st AD": [
  ("Room 627", "2026", "Unit Production Manager, 1st AD", "Short Film", ""),
  ("The Elsewhere", "2021", "1st Assistant Director", "Short Film", "tt13059238"),
  ("Breaker, Breaker", "2014", "Unit Production Manager", "Short Film", ""),
  ("Open 24 Hours", "2014", "Unit Production Manager", "Short Film", ""),
  ("Daytona", "2015", "Unit Production Manager", "Short Film", "tt4048782"),
  ("The Anniversary", "2015", "Unit Production Manager", "Short Film", "tt4048784"),
  ("Theodora", "2015", "Assistant Director, Unit Production Manager", "Short Film", "tt4048780"),
  ("Dig", "2014", "1st AD, Production Manager", "Short Film", "tt4295478"),
  ("The Toy Soldiers", "2014", "Unit Production Manager", "Feature", "tt2219214"),
  ("Bamidbar (AFI)", "2014", "Production Manager, Unit Production Manager", "Short Film", "tt3188530"),
  ("The Hoarder", "2014", "Producer, 1st AD, Unit Production Manager", "Short Film", "tt3530650"),
  ("Jackson's Run", "2013", "Unit Production Manager, 1st AD", "Feature", "tt2290423"),
  ("Superficial", "2013", "1st AD, Unit Production Manager", "Short Film", "tt3147278"),
  ("Billy's 7th Birthday", "2013", "Unit Production Manager, 1st AD", "Short Film", ""),
  ("Snooze, Charlie", "2011", "Producer, Unit Production Manager, 1st AD", "Short Film", "tt2066971"),
  ("H1N1", "2011", "Producer, Unit Production Manager, 1st AD", "Short Film", "tt1801510"),
 ],
 "Editing & Post-Production": [
  ("Two Tales of a City", "2014", "Field Producer, Editor", "Television", ""),
  ("Flipping America (Pilot)", "2014", "Editor", "Television", ""),
  ("The Evolution of Stem Cell Research", "2012", "Assistant Editor", "Documentary", "tt1713545"),
  ("Bullproof, Season One", "2011", "Post-Production Supervisor", "Television", "tt1868312"),
  ("3D Safari: Africa", "2011", "Editor", "Television", "tt1869235"),
  ("Elena Undone", "2010", "Assistant Editor", "Feature", "tt1575539"),
 ],
}

def credits_page():
    allc = [c for g in CREDITS.values() for c in g]
    n_total = len({c[0] for c in allc})
    n_dir = len([c for c in CREDITS["Directing, Writing & Editing"] if "Director" in c[2]])
    n_prod = len(CREDITS["Production: Unit Production Manager & 1st AD"])
    stats = [(str(n_total), "credits listed"), (str(n_dir), "directing credits"), (str(n_prod), "UPM / 1st AD credits"), ("2000", "in Los Angeles since")]
    st = "".join(f'<div><b>{a}</b><span>{c}</span></div>' for a, c in stats)
    secs = ""
    for i, (g, rows) in enumerate(CREDITS.items()):
        li = ""
        for t, y, r, k, imdb in rows:
            name = f'<a href="https://www.imdb.com/title/{imdb}/" rel="noopener">{esc(t)}</a>' if imdb else esc(t)
            li += f'<li><span class="y">{esc(y)}</span><span class="t">{name}</span><span class="r">{esc(r)}</span><span class="k">{esc(k)}</span></li>'
        secs += f'<details class="cred"{" open" if i == 0 else ""}><summary>{esc(g)} <em>{len(rows)}</em></summary><ul>{li}</ul></details>'
    return head(f"Credits | {NAME}", f"Complete credits for {NAME}: directing, writing and editing; unit production management and 1st AD; post-production.", "/credits/", ld(PERSON)) + f"""<body>{header('/credits/')}
<main class="wrap page narrow"><p class="eyebrow">Credits</p><h1 class="serif">The work behind the work.</h1>
<p class="lede">Fifteen years of running sets and cutting footage before and between the films I direct.</p>
<div class="stats">{st}</div>{secs}
<p class="verify">Verified on <a href="{IMDB}" rel="me noopener">IMDb</a>. Titles with an IMDb page link straight to it.</p></main>{footer()}"""

def not_found():
    html_ = head("Page not found | " + NAME, "That page isn't here.", "/404") + f"""<body>{header('/404')}
<main class="wrap page narrow nf"><p class="eyebrow">404</p><h1 class="serif">This scene didn't make the final cut.</h1>
<p class="lede">The page you're looking for isn't here. Let's get you back to the work.</p>
<p class="btns"><a class="btn" href="/">Home</a><a class="btn ghost" href="/filmography/">Filmography</a><a class="btn ghost" href="/credits/">Credits</a></p></main>{footer()}"""
    # never index the error page
    html_ = html_.replace('<link rel="canonical" href="' + SITE + '/404">', '<meta name="robots" content="noindex">')
    open("404.html", "w", encoding="utf8").write(ext_links(html_))

def main():
    open("index.html", "w", encoding="utf8").write(ext_links(home()))
    write("/filmography/", filmography()); write("/biography/", biography()); write("/contact/", contact()); write("/writing/", writing_page()); write("/credits/", credits_page()); write("/projects/dallas-and-allegra/", da_page())
    for p in PROJECTS: write(f"/projects/{p['slug']}/", project(p))
    not_found()
    urls = ["/", "/filmography/", "/writing/", "/credits/", "/biography/", "/contact/", "/projects/dallas-and-allegra/"] + [f"/projects/{p['slug']}/" for p in PROJECTS]
    open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    json.dump({"cleanUrls": True, "trailingSlash": True, "headers": [{"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"}]}]}, open("vercel.json", "w"), indent=2)
    print("built", len(urls), "pages")

main()
