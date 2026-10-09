#!/usr/bin/env python3
"""Static site generator for jpenberth.com. Run: python3 build.py  (writes HTML into the repo root)."""
import os, html, json, shutil, hashlib

def ver(*paths):
    h = hashlib.md5()
    for p in paths: h.update(open(p, "rb").read())
    return h.hexdigest()[:8]

V = ver("assets/css/site.css", "assets/js/site.js")

SITE = "https://www.jpenberth.com"   # must match the address Vercel serves (apex redirects to www)
NAME = "J. Penberth Rabold"
TAG = "Director & Storyteller"
MGR = dict(name="Eva Beadle", company="BSA Talent", url="https://www.bsatalent.com/", email="Eva.Beadle@bsatalent.com",
           phone="(424) 394-2003", tel="+14243942003", street="468 N Camden Dr #200", city="Beverly Hills", region="CA", zip="90210")
EMAIL = MGR["email"]   # every public contact point on the site is the manager's
DESC = "J. Penberth Rabold is a Los Angeles and Pittsburgh writer-director: short films, music videos, and Dallas & Allegra, a Rust Belt love story."
NAV = [("/", "Home"), ("/filmography/", "Filmography"), ("/writing/", "Writing"), ("/biography/", "Biography"), ("/contact/", "Contact")]
SEEDSPARK = "https://seedandspark.com/fund/dallasallegra"
SUBSTACK = "https://jpenberth.substack.com"
IMDB = "https://www.imdb.com/name/nm2399602/"
CONTACT_ENDPOINT = "https://formspree.io/f/meaeqzvb"   # paste the Google Apps Script web-app URL here (see tools/google-apps-script/Code.gs)
YT_DIRECTING = "https://www.youtube.com/@j.penberthraboldstorytelle7092"
YT_PODCAST = "https://www.youtube.com/@whatsurwhypodcast"
VIMEO = "https://vimeo.com/lydianpictures"
CATALYSTORY = "https://catalystory.com/"
INSTAGRAM = "https://www.instagram.com/jpenberthstoryteller/"
DA_SITE = "https://dallasandallegra.com"

# kind: yt / vimeo / none. status: released / coming
PROJECTS = [
 dict(slug="way-too-soon", title="Way Too Soon", year="2022", kind="Music Video", yt="9kDtB5f8ZFA", status="released",
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
 dict(slug="palm-springs-weekend", title="Palm Springs Weekend", year="2022", kind="Music Video", yt="feY4qLSIRXA", status="released", runtime="",
      log="Official music video for Jacob Luttrell's “Palm Springs Weekend.”"),
 dict(hidden=True, slug="toxic-city", title="Toxic City", year="", kind="Album Film", status="coming",
      log="A groundbreaking album film experience for the new album “The Stupidity of Validity” from Grammy-winning singer-songwriter Jacob Luttrell."),
 dict(hidden=True, slug="devilwood", title="Devilwood", year="", kind="Feature", status="coming",
      log="A psychological thriller about three girlfriends on a weekend getaway to repair their fractured friendships, who get sucked into a time portal inside a once-abandoned theme park. Their freedom can only be bought with one thing... blood."),
 dict(hidden=True, slug="dallas-and-allegra", title="Dallas & Allegra", year="", kind="In Development", status="coming",
      log="She's got a plane ticket to Oxford. He's got a safe full of cash and one last score. In a steel town built on dead dreams, they fall for each other anyway."),
]

ALL_PROJECTS = PROJECTS
FILM_ORDER = ["connected", "almost-super", "way-too-soon", "familiar-faces", "palm-springs-weekend"]   # strongest directing work first
PROJECTS = sorted([p for p in ALL_PROJECTS if not p.get("hidden")], key=lambda p: FILM_ORDER.index(p["slug"]) if p["slug"] in FILM_ORDER else 99)  # hidden ones keep their data but are not built

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

def crumbs(*items):
    """items: (name, path) pairs after Home"""
    el = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
    for i, (n, pth) in enumerate(items, 2): el.append({"@type": "ListItem", "position": i, "name": n, "item": SITE + pth})
    return ld({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": el})

WEBSITE = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": NAME,
           "description": "Official website of writer and director J. Penberth Rabold.", "inLanguage": "en", "publisher": {"@id": SITE + "/#person"}}

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
    return f"""<footer><p class="flinks">{row}</p><p>© {NAME}. Represented by {MGR["name"]}, <a href="{MGR["url"]}" rel="noopener">{MGR["company"]}</a> · <a href="mailto:{MGR["email"]}">{MGR["email"]}</a></p></footer><script src="/assets/js/site.js?v={V}" defer></script></body></html>"""

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

PERSON = {"@context": "https://schema.org", "@type": "Person", "@id": SITE + "/#person", "name": NAME,
          "alternateName": ["Jason Penberth Rabold", "Jason Rabold", "J. Penberth"], "jobTitle": ["Film Director", "Screenwriter"],
          "url": SITE, "image": SITE + "/assets/img/headshot.jpg",
          "sameAs": [SUBSTACK, DA_SITE, IMDB, YT_DIRECTING, YT_PODCAST, INSTAGRAM, CATALYSTORY],
          "worksFor": {"@type": "Organization", "name": "Catalystory", "url": CATALYSTORY},
          "description": "Writer and director. 15+ years as a unit production manager and first assistant director in Los Angeles; writer of series and features; author of The Writer's Table newsletter.",
          "homeLocation": [{"@type": "Place", "name": "Los Angeles, CA"}, {"@type": "Place", "name": "Pittsburgh, PA"}],
          "contactPoint": {"@type": "ContactPoint", "contactType": "talent management", "name": MGR["name"], "email": MGR["email"], "telephone": MGR["tel"], "url": MGR["url"],
                           "areaServed": "US", "availableLanguage": "English"},
          "knowsAbout": ["Screenwriting", "Film directing", "Short films", "Music videos"]}

def bio_paras():
    """Eva's full bio, the single source used by BOTH the home page and the Biography page."""
    n_aw = sum(len(v) for v in AWARDS.values())
    return [
        f"""<p>{NAME} is a writer and director whose work explores the complexities of human connection, identity, love, and survival. Drawn to emotionally charged, character-driven storytelling, he creates worlds where ordinary people confront extraordinary circumstances, and where the most compelling conflicts are often the ones unfolding within.</p>""",
        f"""<p>His approach to filmmaking is rooted in more than two decades of experience in the entertainment industry. After moving to Los Angeles in 2000, Penberth spent 15 years working as a unit production manager and first assistant director across feature films, short films, and music videos. That experience gave him an understanding of filmmaking from the ground up, shaping a creative philosophy that balances ambitious storytelling with the realities of bringing a vision to the screen.</p>""",
        f"""<p>In 2015, he shifted his focus to writing and directing, developing original feature films, television pilots, and series. His work has earned {n_aw} festival placements and awards across writing and directing, including two second-round selections at the Austin Film Festival for <em>Bathory</em> and <em>Ghosts of War</em>. His screenplays and television projects have also attracted consideration from major entertainment companies, including Netflix, Apple, Starz, and HBO.</p>""",
        f"""<p>As a director, Penberth brings a visually grounded, emotionally intimate approach to storytelling. His short film <em>Connected</em>, which explores the fragile relationship between a daughter and her father in an increasingly digital world, received runner-up recognition for both the Jury Prize and Best Visuals at the 2019 Filmmakers Collaboration Challenge. His directing work also includes the music videos <em>Way Too Soon</em> and <em>Familiar Faces</em>.</p>""",
        f"""<p>His current slate spans romantic drama, psychological horror, survival thrillers, and character-driven television, united by a fascination with human vulnerability, moral complexity, and the pursuit of connection. He is currently developing <a href="/projects/dallas-and-allegra/">Dallas &amp; Allegra</a>, a contemporary Rust Belt reimagining of Romeo and Juliet, which he wrote and will direct. Set against a landscape of economic hardship, addiction, and divided social worlds, the film explores the collision of love, loyalty, and circumstance.</p>""",
        f"""<p>For Penberth, storytelling is ultimately an exploration of what it means to be human, what breaks us, what connects us, and what we're willing to risk for something worth believing in.</p>""",
    ]

def bio_short():
    """Home-page version: Eva's opening paragraph verbatim, plus one paragraph assembled from sentences/facts in the full bio."""
    n_aw = sum(len(v) for v in AWARDS.values())
    full = bio_paras()
    return [
        full[0],
        f"""<p>After moving to Los Angeles in 2000, Penberth spent 15 years as a unit production manager and first assistant director before shifting to writing and directing in 2015. His work has earned {n_aw} festival placements and awards, including two second-round selections at the Austin Film Festival for <em>Bathory</em> and <em>Ghosts of War</em>. He is currently developing <a href="/projects/dallas-and-allegra/">Dallas &amp; Allegra</a>, a contemporary Rust Belt reimagining of Romeo and Juliet, which he wrote and will direct.</p>""",
    ]

import os as _os
HERO_STYLE = _os.environ.get("HERO", "portrait")   # "portrait" (Eva) or "brand" (logo title card)
TAGLINE = "Stories about the choices that define us, the connections that shape us, and the lengths we'll go to for the things we love."
KICKER = "Writer &nbsp;|&nbsp; Director &nbsp;|&nbsp; Filmmaker"

def hero_portrait():
    """Option A: the first thing anyone sees is the portrait, with the name, titles and a short intro."""
    return f"""<section class="phero"><figure class="pfig"><img src="/assets/img/headshot.jpg" alt="Black-and-white portrait of {NAME}, writer and director" width="900" height="1266" fetchpriority="high"></figure>
<div class="ptxt"><p class="eyebrow">{KICKER}</p>
<h1 class="plogo"><img src="/assets/img/logo-white.png" alt="{NAME}, film director, screenwriter and storyteller" width="1515" height="534"></h1>
<p class="lede">{TAGLINE}</p>
{"".join(bio_short())}
<p class="btns"><a class="btn" href="/biography/">Read my story</a></p></div></section>"""

def hero_brand():
    """Option B: no photo or video up top, just the signature as a title card with film grain; the portrait follows below."""
    return f"""<section class="bhero"><canvas class="tv" data-interval="10000" data-fade="4000" aria-hidden="true"></canvas><div class="scan"></div>
<div class="bin"><h1 class="blogo"><img src="/assets/img/logo-white.png" alt="{NAME}, film director, screenwriter and storyteller" width="1515" height="534" fetchpriority="high"></h1>
<p class="eyebrow">{KICKER}</p><p class="blede">{TAGLINE}</p></div><a class="cue" href="#about" aria-label="Scroll to the introduction">&darr;</a></section>
<section class="about" id="about"><div class="wrap ab">
<figure class="shot"><img src="/assets/img/headshot.jpg" alt="Black-and-white portrait of {NAME}, writer and director" width="900" height="1266" loading="lazy"></figure>
<div class="abt"><h2 class="serif nm">{NAME}</h2>
{"".join(bio_short())}
<p class="btns"><a class="btn" href="/biography/">Read my story</a></p></div></div></section>"""

def about_home():
    return f"""<section class="about"><div class="wrap ab">
<figure class="shot"><img src="/assets/img/headshot.jpg" alt="Black-and-white portrait of {NAME}, writer and director" width="900" height="1266" loading="lazy"></figure>
<div class="abt"><p class="eyebrow">Writer &nbsp;|&nbsp; Director &nbsp;|&nbsp; Filmmaker</p><h2 class="serif nm">{NAME}</h2>
<p class="lede">Stories about the choices that define us, the connections that shape us, and the lengths we'll go to for the things we love.</p>
{"".join(bio_short())}
<p class="btns"><a class="btn" href="/biography/">Read my story</a></p></div></div></section>"""

def broken_band():
    """The Catalystory idea, in its own words (from catalystory.com)."""
    return """<section class="broken"><div class="wrap"><h2 class="serif">Broken is beautiful.</h2>
<p class="bl">Every one of us has been broken, and that's the one thread we all share.</p>
<p class="bq">What if broken is where the story begins?</p></div></section>"""

def slate_teaser():
    li = "".join(f'<li><a href="/writing/"><span class="g">{esc(s["format"])} &middot; {esc(s["genre"])}</span><strong>{esc(s["title"])}</strong></a></li>' for s in SLATE)
    return f"""<section class="wrap slt"><p class="eyebrow">The Writing</p><h2 class="serif">Original film and television.</h2><ul class="tiles">{li}</ul><p><a class="more" href="/writing/">See the slate →</a></p></section>"""

def home():
    acc = []
    hero = hero_portrait() if HERO_STYLE == "portrait" else hero_brand()
    pre = '<link rel="preload" as="image" href="/assets/img/headshot.jpg" fetchpriority="high">\n' if HERO_STYLE == "portrait" else ""
    return head(f"{NAME} | Los Angeles Film Director & Writer", DESC, "/", ld(PERSON) + ld(WEBSITE) + pre) + f"""<body class="home nohero">{header('/')}
<main class="sheet plain">{hero}{broken_band()}{da_feature()}{slate_teaser()}{signup()}</main>{footer()}"""

def filmography():
    cards = "".join(card(p) for p in PROJECTS)
    return head(f"Films & Music Videos | {NAME}, Director", f"Short films and music videos directed by {NAME}: Connected, Almost Super, Familiar Faces, Way Too Soon and Palm Springs Weekend.", "/filmography/", crumbs(("Filmography", "/filmography/"))) + f"""<body>{header('/filmography/')}
<main class="wrap page"><h1>Filmography</h1><section class="grid">{cards}</section></main>{footer()}"""

def biography():
    stats = [("15+", "years as a UPM &amp; 1st AD"), (str(sum(len(v) for v in AWARDS.values())), "festival placements &amp; awards, writing and directing"), ("2×", "Austin Film Festival second round, <em>Bathory</em> &amp; <em>Ghosts of War</em>"), ("13K+", "followers on Instagram"), ("1,000+", "readers of The Writer's Table")]
    st = "".join(f'<div><b>{a}</b><span>{c}</span></div>' for a, c in stats)
    _bio = bio_paras()
    return head(f"Biography | {NAME}, Writer & Director", f"About {NAME}: a Los Angeles and Pittsburgh writer and director who spent 15 years running film sets and now makes the stories he writes.", "/biography/", ld(PERSON) + crumbs(("Biography", "/biography/"))) + f"""<body>{header('/biography/')}
<main class="wrap page narrow"><p class="eyebrow">Biography</p><h1 class="serif">{NAME}</h1>
<p class="lede">Stories about the choices that define us, the connections that shape us, and the lengths we'll go to for the things we love.</p>
{_bio[0]}{_bio[1]}{_bio[2]}
<div class="stats">{st}</div>
{_bio[3]}{_bio[4]}{_bio[5]}
<p class="quote">Write truth... inspire love.</p>
<p class="verify"><a href="/filmography/">See the films →</a> &nbsp;·&nbsp; <a href="/credits/">All credits →</a> &nbsp;·&nbsp; <a href="{IMDB}" rel="me noopener">IMDb</a> &nbsp;·&nbsp; <a href="{CATALYSTORY}" rel="noopener">Catalystory</a></p>
</main>{footer()}"""

def contact():
    topics = ["Bookings / directing", "Writing / scripts", "Production", "Press", "Something else"]
    opts = "".join(f"<option>{t}</option>" for t in topics)
    return head(f"Contact {NAME} | Bookings & Production", f"Contact the management of writer and director {NAME}: Eva Beadle at BSA Talent, Beverly Hills. Or send a message through the form.", "/contact/", crumbs(("Contact", "/contact/"))) + f"""<body>{header('/contact/')}
<main class="wrap page narrow"><p class="eyebrow">Contact</p><h1 class="serif">Let's talk.</h1>
<p>For bookings, production, writing and press inquiries, please contact my manager:</p>
<div class="mgr"><p class="mname">{MGR["name"]}</p><p class="mco"><a href="{MGR["url"]}" rel="noopener">{MGR["company"]}</a></p>
<p><a href="mailto:{MGR["email"]}">{MGR["email"]}</a><br><a href="tel:{MGR["tel"]}">{MGR["phone"]}</a></p>
<p class="addr">{MGR["street"]}<br>{MGR["city"]}, {MGR["region"]} {MGR["zip"]}</p></div>
<p class="prod">My production company: <a href="{CATALYSTORY}" rel="noopener">Catalystory</a></p>
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
    extra += crumbs(("Filmography", "/filmography/"), (p["title"], path))
    meta = " · ".join(x for x in (p["kind"], p["year"], p.get("runtime")) if x)
    desc_ = p["log"] if len(p["log"]) >= 110 else (p["log"] + f" Directed by {NAME}, Los Angeles film director.")
    return head(f"{p['title']} ({p['kind']}) | {NAME}", desc_[:155], path, extra, og_img=None) + f"""<body>{header('/filmography/')}
<main class="wrap page"><p class="crumb"><a href="/filmography/">← Filmography</a></p><h1>{esc(p["title"])}</h1><p class="meta">{esc(meta)}</p>
{player}<div class="narrow"><p>{esc(p["log"])}</p><p class="by">Directed by {NAME}</p>{f'<h2>Awards</h2><ul>{awards}</ul>' if awards else ''}</div></main>{footer()}"""


import json as _json
def writing_posts():
    try: return _json.load(open("data/writing.json", encoding="utf8"))
    except Exception: return []

def fmt_date(d):
    import datetime
    return datetime.date.fromisoformat(d).strftime("%b %-d, %Y")

def signup():
    return f"""<section class="signup"><div class="wrap sin"><div><p class="eyebrow">Stay in the loop</p><h2 class="serif">Get the newsletter and Dallas &amp; Allegra updates.</h2>
<p class="sub">Craft notes from The Writer's Table and news as the film comes together. Free. Unsubscribe any time.</p></div>
<form class="sform" action="{SUBSTACK}/api/v1/free?nojs=true" method="post" target="_blank">
<input type="hidden" name="source" value="embed"><input type="hidden" name="first_url" value="{SITE}/"><input type="hidden" name="current_url" value="{SITE}/">
<label class="sr" for="sub-email">Email address</label><input id="sub-email" name="email" type="email" placeholder="Your email" autocomplete="email" required>
<button class="btn" type="submit">Subscribe</button></form></div></section>"""

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
    eps_li = "".join(f'<li><a href="https://www.youtube.com/watch?v={i}" rel="noopener"><strong>{esc(t)}</strong><span class="b">Guest: {esc(g)}</span></a></li>' for i, t, g in PODCAST_EPS[:3])
    ps = writing_posts()
    li = "".join(f'<li><a href="{p["url"]}" rel="noopener"><span class="d">{fmt_date(p["date"])}</span><strong>{esc(p["title"])}</strong><span class="b">{esc(p["blurb"])}</span></a></li>' for p in ps[:5])
    def _card(s):
        return f'<article class="scard"><p class="g">{esc(s["format"])} &middot; {esc(s["genre"])}</p><h3 class="serif">{esc(s["title"])}</h3><p class="log">{esc(s["logline"])}</p></article>'
    cards = "".join(f'<h2 class="sgroup">{g}</h2><section class="sgrid">{"".join(_card(s) for s in SLATE if s["group"] == g)}</section>' for g in ("Film", "Television"))
    items = [{"@type": "ListItem", "position": i, "item": {"@type": "CreativeWork", "name": s["title"], "genre": s["genre"], "description": s["logline"], "author": {"@type": "Person", "name": NAME, "@id": SITE + "/#person"}}} for i, s in enumerate(SLATE, 1)]
    slate_ld = ld({"@context": "https://schema.org", "@type": "ItemList", "name": "Screenwriting slate", "itemListElement": items})
    blog = {"@context": "https://schema.org", "@type": "Blog", "name": "The Writer's Table", "url": SUBSTACK, "author": {"@type": "Person", "name": NAME, "url": SITE},
            "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"], "datePublished": p["date"], "author": {"@type": "Person", "name": NAME}} for p in ps]}
    return head(f"Screenwriting & Writing | {NAME}", f"The screenwriting slate of {NAME}: original features and series including Caketown, Winter in Budapest, Bathory, The Awakening and Erasing Chayse.", "/writing/", slate_ld + ld(blog) + crumbs(("Writing", "/writing/"))) + f"""<body>{header('/writing/')}
<main class="wrap page"><p class="eyebrow">Writing</p><h1 class="serif">The Slate</h1>
<p class="lede wlede">Original feature films and television series about love, loss and the lengths we go to. Scripts and materials are available to industry on request through my manager, <a href="/contact/">{MGR["name"]} at {MGR["company"]}</a>.</p>
{cards}
<div class="narrow notes"><p class="eyebrow">Also</p><h2 class="serif">The Writer's Table</h2>
<p class="lede">My newsletter for screenwriters and storytellers: how stories work, why scripts fail, and what it takes to keep going.</p>
<p class="btns"><a class="btn ghost" href="{SUBSTACK}/subscribe" rel="noopener">Subscribe, it's free</a></p>
<ul class="posts">{li}</ul><p><a class="more" href="{SUBSTACK}/archive" rel="noopener">Full archive on Substack →</a></p>
<div class="pod"><p class="eyebrow">Podcast</p><h2 class="serif">What's Your Why</h2>
<p class="lede">What broke you made you beautiful.</p>
<p>Real conversations with writers, musicians, directors, actors and creators about the fire that drives us, the fear that shapes us, and how both evolve.</p>
<ul class="posts">{eps_li}</ul>
<p><a class="more" href="{YT_PODCAST}" rel="noopener">All episodes on YouTube →</a></p></div></div></main>{signup()}{footer()}"""

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

# --- Awards & selections: positive results only. (year, competition, result, project)
AWARDS = {
 "Films & Music Videos": [
  ("2019", "Filmmakers Collaboration Challenge", "Runner-Up, Jury Prize", "Connected"),
  ("2019", "Filmmakers Collaboration Challenge", "Runner-Up, Best Visuals", "Connected"),
  ("2022", "LWIFF | Lonely Wolf", "Nominee", "Way Too Soon"),
  ("2022", "Toronto Short Film Festival", "Official Selection", "Way Too Soon"),
  ("2022", "FlickFair Film Festival", "Official Selection", "Way Too Soon"),
  ("2022", "FlickFair Film Festival", "Official Selection", "Connected"),
  ("2022", "Breckenridge Film Festival", "Selected", "Way Too Soon"),
 ],
 "Screenplays": [
  ("2022", "Festigious Los Angeles, Monthly Competition", "Winner", "Caketown"),
  ("2022", "Festigious Los Angeles, Monthly Competition", "Winner", "Bathory"),
  ("2022", "RED Movie Awards", "Finalist", "Caketown"),
  ("2022", "Big Apple Film Festival & Screenplay Competition", "Honorable Mention", "Caketown"),
  ("2026", "Outstanding Screenplays Feature Competition", "Semi-Finalist", "Winter in Budapest"),
  ("2026", "3rd Annual Fade In Screenwriting Fellowship", "Semi-Finalist", "Winter in Budapest"),
  ("2026", "StoryPros Awards Screenplay Contest", "Semi-Finalist", "Winter in Budapest"),
  ("2022", "Santa Barbara International Screenplay Awards", "Semi-Finalist", "Caketown"),
  ("2022", "LWIFF | Lonely Wolf", "Semi-Finalist", "Bathory"),
  ("", "Austin Film Festival Screenwriting Competition", "Second Round", "Bathory"),
  ("", "Austin Film Festival Screenwriting Competition", "Second Round", "Ghosts of War"),
  ("2022", "Emerging Creatives", "Selected", "Bathory"),
  ("2026", "Nashville Film Festival Screenwriting Competition", "Quarter-Finalist", "Winter in Budapest"),
  ("2022", "Santa Barbara International Screenplay Awards", "Quarter-Finalist", "Bathory"),
  ("2022", "5th Annual Female Driven Screenwriting Contest", "Quarter-Finalist", "Bathory"),
 ],
}

# --- Writing slate: public-safe fields only (title, format, genre, logline). No deal status, reps or company names from the private one-sheet.
SLATE = [
 dict(group="Film", title="Caketown", format="Feature Film", genre="Romantic Crime Drama",
      logline="A modern-day Rust Belt Romeo and Juliet centered on Dallas Dixon, a fallen athlete-turned-dealer, who meets Allegra Cunningham, a high school senior with the right zip code, searching for something real. Together, they learn that love destroys all."),
 dict(group="Film", title="Winter in Budapest", format="Feature Film", genre="Romantic Drama",
      logline="After the death of his sister, a man long committed to emotional distance is drawn into the trail of letters she has left behind, a journey through Budapest that becomes both a family reckoning and a reckoning with the life he has spent avoiding. Along the way, he discovers an estranged grandfather, an unexpected love, and the possibility that to remain present with another person is its own kind of courage."),
 dict(group="Film", title="Chasing Sky", format="Feature Film", genre="Survival Drama",
      logline="Reeling from the tragic death of his daughter, and secluded in a firewatch cabin deep in a most beautiful Montana setting, a former hotshot firefighter gets caught in a massive storm that destroys his cabin, forcing him to journey across the Montana wilderness to return to the one place he doesn't want to go."),
 dict(group="Television", title="Bathory", format="TV Series", genre="Elevated Drama / Thriller",
      logline="History's deadliest serial killer was a woman. The extraordinary true story of Erzebet Bathory, a brilliant and beautiful Hungarian Countess and one of the most powerful figures in 16th-century Europe, whose legacy became that of history's deadliest serial killer. Sexy, bold and transgressive: was she a monster, or a maligned figure?"),
 dict(group="Television", title="The Awakening", format="TV Series", genre="Elevated Sci-Fi Drama",
      logline="Haunted by violent sleepwalking and recurring dreams of a mysterious woman, astrophysicist Aidan Tellman discovers a terrifying anomaly spreading across Los Angeles, one that may signal the collapse of reality itself. As ancient supernatural forces gather around him, Aidan is drawn into a hidden war in this modern reimagining of Dante's Divine Comedy."),
 dict(group="Television", title="Erasing Chayse", format="TV Pilot", genre="Action / Thriller",
      logline="Chayse Anderson has the perfect life: a beautiful home in the Hollywood Hills, two teenage daughters, a devoted husband, and a standing yoga class with the other soccer moms. She's also a world-class assassin, and as her past starts closing in on the life she's built, she'll have to decide how far she'll go to protect the family who has no idea who she really is."),
 dict(group="Television", title="Ghosts of War: Operation Fortitude", format="TV Anthology Series", genre="Historical Drama",
      logline="The untold story of how the CIA was born during World War II: the U.S.-trained French Resistance men and women who bled and died to turn the tide of the war, and gave birth to the modern CIA."),
]

def awards_section():
    n = sum(len(v) for v in AWARDS.values())
    out = f'<details class="cred"><summary>Awards &amp; Selections <em>{n}</em></summary>'
    for g, rows in AWARDS.items():
        li = "".join(f'<li><span class="y">{esc(y)}</span><span class="t">{esc(c)}</span><span class="r">{esc(r)}</span><span class="k">{esc(p)}</span></li>' for y, c, r, p in rows)
        out += f'<p class="agroup">{esc(g)}</p><ul>{li}</ul>'
    return out + "</details>"

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
    return head(f"Credits & Awards | {NAME}, Director", f"Full credits and awards for {NAME}: directing, writing and editing, unit production management, 1st AD work and festival placements.", "/credits/", ld(PERSON) + crumbs(("Credits", "/credits/"))) + f"""<body>{header('/credits/')}
<main class="wrap page narrow"><p class="eyebrow">Credits</p><h1 class="serif">The work behind the work.</h1>
<p class="lede">Fifteen years of running sets and cutting footage before and between the films I direct.</p>
<div class="stats">{st}</div>{secs}{awards_section()}
<p class="verify">Verified on <a href="{IMDB}" rel="me noopener">IMDb</a>, where some credits appear under the name Jason Rabold. Titles with an IMDb page link straight to it.</p></main>{footer()}"""

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
    open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{__import__('datetime').date.today().isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    json.dump({"cleanUrls": True, "trailingSlash": True, "headers": [{"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"}]}]}, open("vercel.json", "w"), indent=2)
    print("built", len(urls), "pages")

main()
