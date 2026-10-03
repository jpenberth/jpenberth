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
DESC = "J. Penberth Rabold is a Los Angeles director and storyteller: short films, music videos and original stories about human connection."
NAV = [("/", "Home"), ("/filmography/", "Filmography"), ("/biography/", "Biography"), ("/contact/", "Contact")]

# kind: yt / vimeo / none. status: released / coming
PROJECTS = [
 dict(slug="way-too-soon", title="Way Too Soon", year="", kind="Music Video", yt="9kDtB5f8ZFA", status="released",
      log="Official music video for Jacob Luttrell's “Way Too Soon.”", runtime="4:36"),
 dict(slug="connected", title="Connected", year="2019", kind="Short Film", yt="T78zgx4-O2k", status="released", runtime="6:19",
      log="A young woman struggles to find an authentic connection with her father in a technologically connected world.",
      awards=["Filmmakers Collaboration Challenge 2019 — Runner-Up, Jury Prize", "Filmmakers Collaboration Challenge 2019 — Runner-Up, Best Visuals"]),
 dict(slug="familiar-faces", title="Familiar Faces", year="2020", kind="Music Video", yt="H98SCB794-o", status="released", runtime="6:11",
      log="Music video for Grammy-winning singer-songwriter Jacob Luttrell's new single. The album experience movie is in pre-production."),
 dict(slug="one-gloved-rider", title="One Gloved Rider", year="2020", kind="Short Film", vimeo="531735478", status="released", runtime="5:18",
      log="Samuel, who considers himself a true biker, attempts to join the Skull Crushers Bike Club."),
 dict(slug="almost-super", title="Almost Super", year="2020", kind="Pilot Proof of Concept", status="released", img="almost-super.jpg",
      log="An action-comedy pilot proof of concept starring French Stewart, Bryan Dodds and Laur Allen, about a group of wannabe superheroes who team up with a former supervillain to join the International League of Superheroes."),
 dict(slug="new-film", title="NEW FILM TITLE", year="", kind="Film", yt="feY4qLSIRXA", status="released", runtime="",
      log="TODO(Jason): title and logline for this film."),
 dict(hidden=True, slug="toxic-city", title="Toxic City", year="", kind="Album Film", status="coming",
      log="A groundbreaking album film experience for the new album “The Stupidity of Validity” from Grammy-winning singer-songwriter Jacob Luttrell."),
 dict(hidden=True, slug="devilwood", title="Devilwood", year="", kind="Feature", status="coming",
      log="A psychological thriller about three girlfriends on a weekend getaway to repair their fractured friendships, who get sucked into a time portal inside a once-abandoned theme park. Their freedom can only be bought with one thing... blood."),
 dict(hidden=True, slug="dallas-and-allegra", title="Dallas & Allegra", year="", kind="In Development", status="coming",
      log="TODO(Jason): logline for Dallas & Allegra."),
]

ALL_PROJECTS = PROJECTS
PROJECTS = [p for p in ALL_PROJECTS if not p.get("hidden")]  # hidden ones keep their data but are not built

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
<div class="social"><a href="https://www.instagram.com/" aria-label="Instagram" rel="me noopener">IG</a><a href="https://vimeo.com/lydianpictures" aria-label="Vimeo" rel="me noopener">VM</a></div></header>"""

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
    open(os.path.join(d, "index.html"), "w", encoding="utf8").write(content)

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + "</script>\n"

PERSON = {"@context": "https://schema.org", "@type": "Person", "name": NAME, "jobTitle": "Film Director",
          "url": SITE, "email": EMAIL, "image": SITE + "/assets/img/logo-black.png",
          "sameAs": ["https://vimeo.com/lydianpictures"]}

def home():
    cards = "".join(card(p) for p in PROJECTS)
    acc = ["Connected — Runner-Up, Jury Prize · Filmmakers Collaboration Challenge 2019", "Connected — Runner-Up, Best Visuals · Filmmakers Collaboration Challenge 2019"]
    return head(f"{NAME} | Film Director & Storyteller", DESC, "/", ld(PERSON)) + f"""<body class="home">{header('/')}
<div class="stage" aria-hidden="false"><video autoplay muted loop playsinline preload="auto" poster="/assets/img/hero-poster.jpg"><source src="/assets/video/hero.mp4" type="video/mp4"></video>
<div class="tint"></div><div class="grain"></div><div class="grain g2"></div></div>
<div class="intro"><h1 class="logo"><img src="/assets/img/logo-white.png" alt="{NAME} — Storyteller" width="1515" height="534"></h1></div>
<main class="sheet"><section class="grid wrap"><h2 class="sr">Selected work</h2>{cards}</section>
<section class="wrap story"><!-- STORY COPY --></section></main>{footer()}"""

def filmography():
    cards = "".join(card(p) for p in PROJECTS)
    return head(f"Filmography | {NAME}", f"Short films, music videos and projects in development by director {NAME}.", "/filmography/") + f"""<body>{header('/filmography/')}
<main class="wrap page"><h1>Filmography</h1><section class="grid">{cards}</section></main>{footer()}"""

def biography():
    lst = "".join(f'<li><a href="/projects/{p["slug"]}/"><strong>{esc(p["title"])}</strong></a> <span>{esc(p["year"])}</span><p>{esc(p["log"])}</p></li>' for p in PROJECTS)
    return head(f"Biography | {NAME}", f"About {NAME}: director and storyteller drawn to stories of human connection and self-empowerment.", "/biography/", ld(PERSON)) + f"""<body>{header('/biography/')}
<main class="wrap page narrow"><h1>Biography</h1><h2 class="name">{NAME}</h2>
<p>I believe storytelling is about human connection. Letting my imagination run wild has become one of the most fulfilling parts of my life. Getting behind the camera as a director isn't something that I ever saw in my journey, but now that I have, it influences every aspect of the way I approach the stories I write and direct.</p>
<p>I'm drawn to stories about the human experience in worlds far beyond our own or the past. Putting characters in situations that require them to discover their own self-empowerment. Stories that create a conversation around the emotions and truth drive us to survive and seek out the love in life.</p>
<p class="quote">Write truth... inspire love.</p>
<h2>Filmography</h2><ul class="credits">{lst}</ul></main>{footer()}"""

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

def main():
    open("index.html", "w", encoding="utf8").write(home())
    write("/filmography/", filmography()); write("/biography/", biography()); write("/contact/", contact())
    for p in PROJECTS: write(f"/projects/{p['slug']}/", project(p))
    urls = ["/", "/filmography/", "/biography/", "/contact/"] + [f"/projects/{p['slug']}/" for p in PROJECTS]
    open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    json.dump({"cleanUrls": True, "trailingSlash": True, "headers": [{"source": "/assets/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"}]}]}, open("vercel.json", "w"), indent=2)
    print("built", len(urls), "pages")

main()
