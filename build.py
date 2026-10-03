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
DA_SITE = "https://dallasandallegra.com"

# kind: yt / vimeo / none. status: released / coming
PROJECTS = [
 dict(slug="way-too-soon", title="Way Too Soon", year="", kind="Music Video", yt="9kDtB5f8ZFA", status="released",
      log="Official music video for Jacob Luttrell's “Way Too Soon.”", runtime="4:36"),
 dict(slug="connected", title="Connected", year="2019", kind="Short Film", yt="T78zgx4-O2k", status="released", runtime="6:19",
      log="A young woman struggles to find an authentic connection with her father in a technologically connected world.",
      awards=["Filmmakers Collaboration Challenge 2019 — Runner-Up, Jury Prize", "Filmmakers Collaboration Challenge 2019 — Runner-Up, Best Visuals"]),
 dict(slug="familiar-faces", title="Familiar Faces", year="2020", kind="Music Video", yt="H98SCB794-o", status="released", runtime="6:11",
      log="Music video for Grammy-winning singer-songwriter Jacob Luttrell's new single. The album experience movie is in pre-production."),
 dict(hidden=True, slug="one-gloved-rider", title="One Gloved Rider", year="2020", kind="Short Film", vimeo="531735478", status="released", runtime="5:18",
      log="Samuel, who considers himself a true biker, attempts to join the Skull Crushers Bike Club."),
 dict(slug="almost-super", title="Almost Super", year="2020", kind="Pilot Proof of Concept", status="released", img="almost-super.jpg",
      log="An action-comedy pilot proof of concept starring French Stewart, Bryan Dodds and Laur Allen, about a group of wannabe superheroes who team up with a former supervillain to join the International League of Superheroes."),
 dict(slug="palm-springs-weekend", title="Palm Springs Weekend", year="", kind="Music Video", yt="feY4qLSIRXA", status="released", runtime="",
      log="Music video for Jacob Luttrell's “Palm Springs Weekend.”"),
 dict(hidden=True, slug="toxic-city", title="Toxic City", year="", kind="Album Film", status="coming",
      log="A groundbreaking album film experience for the new album “The Stupidity of Validity” from Grammy-winning singer-songwriter Jacob Luttrell."),
 dict(hidden=True, slug="devilwood", title="Devilwood", year="", kind="Feature", status="coming",
      log="A psychological thriller about three girlfriends on a weekend getaway to repair their fractured friendships, who get sucked into a time portal inside a once-abandoned theme park. Their freedom can only be bought with one thing... blood."),
 dict(hidden=True, slug="dallas-and-allegra", title="Dallas & Allegra", year="", kind="In Development", status="coming",
      log="TODO(Jason): logline for Dallas & Allegra."),
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

def head(title, desc, path, extra="", og_img=None):
    url = SITE + path
    img = og_img or (SITE + "/assets/img/hero-poster.jpg")
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:site_name" content="{NAME}"><meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/img/logo-white.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@300;400&family=Barlow+Condensed:wght@500;600&family=Playfair+Display:ital@0;1&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={V}">
{extra}</head>"""

def header(path):
    links = "".join(f'<a href="{h}"{" class=on aria-current=page" if (h==path or (h!="/" and path.startswith(h))) else ""}>{t}</a>' for h, t in NAV)
    return f"""<header class="top"><a class="tag" href="/">[ {TAG.upper()} ]</a>
<button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
<nav>{links}</nav>
<div class="social"><a href="https://www.instagram.com/" aria-label="Instagram" rel="me noopener"><svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.3" cy="6.7" r=".6" fill="currentColor"/></svg></a><a href="https://vimeo.com/lydianpictures" aria-label="Vimeo" rel="me noopener"><svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M23.977 6.416c-.105 2.338-1.739 5.543-4.894 9.609-3.268 4.247-6.026 6.37-8.29 6.37-1.409 0-2.578-1.294-3.553-3.881L5.322 11.4C4.603 8.816 3.834 7.522 3.01 7.522c-.179 0-.806.378-1.881 1.132L0 7.197a315.065 315.065 0 0 0 3.501-3.123C5.08 2.701 6.266 1.984 7.055 1.91c1.867-.18 3.016 1.1 3.447 3.838.465 2.953.789 4.789.971 5.507.539 2.45 1.131 3.674 1.776 3.674.502 0 1.256-.796 2.265-2.385 1.004-1.589 1.54-2.797 1.612-3.628.144-1.371-.395-2.061-1.614-2.061-.574 0-1.167.121-1.777.391 1.186-3.868 3.434-5.757 6.762-5.637 2.473.06 3.628 1.664 3.493 4.797z"/></svg></a></div></header>"""

def footer():
    return f"""<footer><p>© {NAME}. <a href="mailto:{EMAIL}">{EMAIL}</a></p></footer><script src="/assets/js/site.js?v={V}" defer></script></body></html>"""

def card(p):
    t = thumb(p)
    img = f'<img src="{t}" alt="{esc(p["title"])} — {esc(p["kind"])}" loading="lazy">' if t else '<div class="ph"></div>'
    badge = '<span class="play" aria-hidden="true"></span>'
    meta = " · ".join(x for x in (p["kind"], p["year"]) if x)
    return f'<a class="card" href="/projects/{p["slug"]}/"><div class="thumb">{img}{badge}</div><h3>{esc(p["title"])}</h3><p>{esc(meta)}</p></a>'

def write(path, content):
    d = os.path.join(".", path.strip("/"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf8").write(ext_links(content))

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"

PERSON = {"@context": "https://schema.org", "@type": "Person", "name": NAME, "jobTitle": "Film Director",
          "url": SITE, "email": EMAIL, "image": SITE + "/assets/img/logo-black.png",
          "sameAs": ["https://vimeo.com/lydianpictures", SUBSTACK, DA_SITE],
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
    lst = "".join(f'<li><a href="/projects/{p["slug"]}/"><strong>{esc(p["title"])}</strong></a> <span>{esc(p["year"])}</span><p>{esc(p["log"])}</p></li>' for p in PROJECTS)
    stats = [("15+", "years as a UPM &amp; 1st AD"), ("2×", "Runner-Up, Filmmakers Collaboration Challenge"), ("2nd round", "Austin Film Festival, <em>Ghosts of War</em>"), ("1,000+", "readers of The Writer's Table")]
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
<h2>Work</h2><ul class="credits">{lst}</ul></main>{footer()}"""

def contact():
    return head(f"Contact | {NAME}", f"Contact director {NAME} for bookings, production and general inquiries.", "/contact/") + f"""<body>{header('/contact/')}
<main class="wrap page narrow"><h1>Contact</h1>
<p>Bookings, production and general inquiries:</p>
<p class="big"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<!-- TODO(Jason): add manager / representation details after signing -->
</main>{footer()}"""

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
    return head(f"{p['title']} ({p['kind']}) | {NAME}", p["log"][:155], path, extra, og_img=(SITE + thumb(p)) if thumb(p) and thumb(p).startswith("/") else None) + f"""<body>{header('/filmography/')}
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

def writing_page():
    ps = writing_posts()
    li = "".join(f'<li><a href="{p["url"]}" rel="noopener"><span class="d">{fmt_date(p["date"])}</span><strong>{esc(p["title"])}</strong><span class="b">{esc(p["blurb"])}</span></a></li>' for p in ps)
    blog = {"@context": "https://schema.org", "@type": "Blog", "name": "The Writer's Table", "url": SUBSTACK, "author": {"@type": "Person", "name": NAME, "url": SITE},
            "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"], "datePublished": p["date"], "author": {"@type": "Person", "name": NAME}} for p in ps]}
    return head(f"Writing | {NAME}", "The Writer's Table: screenwriting craft, stakes, structure and the life of a working writer, by J. Penberth Rabold.", "/writing/", ld(blog)) + f"""<body>{header('/writing/')}
<main class="wrap page narrow"><h1>Writing</h1>
<p class="lede">I'm a writer first. <em>The Writer's Table</em> is my newsletter for screenwriters and storytellers: how stories work, why scripts fail, and what it takes to keep going. More than a thousand people read it.</p>
<p class="btns"><a class="btn" href="{SUBSTACK}/subscribe" rel="noopener">Subscribe, it's free</a></p>
<ul class="posts big">{li}</ul><p><a class="more" href="{SUBSTACK}/archive" rel="noopener">Full archive on Substack →</a></p></main>{footer()}"""

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
    return head("Dallas & Allegra: Love Is Destruction | " + NAME, "She's got a plane ticket to Oxford. He's got a safe full of cash and one last score. A Rust Belt Romeo and Juliet, written and directed by J. Penberth Rabold.", path, ld(schema), og_img=SITE + "/assets/img/da/hero-skyline-wide.jpg") + f"""<body class="dapage">{header('/projects/')}
<section class="dahero"><img src="/assets/img/da/hero-skyline-wide.jpg" alt="Dallas and Allegra silhouetted before a full moon over the Pittsburgh skyline" width="1672" height="941"><div class="shade"></div></section>
<main class="wrap page narrow dabody"><p class="eyebrow">A short film</p><h1 class="serif">Dallas &amp; Allegra</h1><p class="lede">Love is destruction.</p>
<p class="btns"><a class="btn" href="{SEEDSPARK}" rel="noopener">Support the film on Seed&amp;Spark</a><a class="btn ghost" href="{DA_SITE}" rel="noopener">dallasandallegra.com</a></p>
<h2>The story</h2><p>In Bellvue Falls, everyone is addicted to something. Two young star-crossed lovers are about to choose the most dangerous one: each other.</p>
<p>Dallas Dixon, a fallen quarterback turned dealer, is two payments away from walking out of the only life this town ever offered him. Allegra Cunningham, a trust fund baby and heir to the Cunningham steel fortune, was born on the right side of town and is less than a year from a plane to Oxford.</p>
<p>Then she tracks him down at a local diner to return her addict mother's Oxy. One late-night conversation later, two people who were never supposed to meet believe they can outrun everything.</p>
<p class="quote">A Rust Belt Romeo and Juliet about the ones this town lets disappear, and a love that burns hotter than whatever is trying to put it out.</p>
<div class="stills">{stills}</div>
<h2>The team</h2><ul class="team">{t}</ul></main>{footer()}"""

def main():
    open("index.html", "w", encoding="utf8").write(ext_links(home()))
    write("/filmography/", filmography()); write("/biography/", biography()); write("/contact/", contact()); write("/writing/", writing_page()); write("/projects/dallas-and-allegra/", da_page())
    for p in PROJECTS: write(f"/projects/{p['slug']}/", project(p))
    urls = ["/", "/filmography/", "/writing/", "/biography/", "/contact/", "/projects/dallas-and-allegra/"] + [f"/projects/{p['slug']}/" for p in PROJECTS]
    open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    json.dump({"cleanUrls": True, "trailingSlash": True, "headers": [{"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"}]}]}, open("vercel.json", "w"), indent=2)
    print("built", len(urls), "pages")

main()
