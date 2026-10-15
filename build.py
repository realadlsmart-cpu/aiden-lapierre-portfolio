#!/usr/bin/env python3
"""Zero-dependency static portfolio generator. Python 3.10+."""
import json
import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dist"
DATA = json.loads((ROOT / "content/portfolio.json").read_text())
DATA.setdefault("customPages", [])
NAV = [("Home", ""), ("Photography", "photography"), ("Model UN", "model-un"), ("Technology", "technology"), ("Academics", "academics"), ("About", "about"), ("Other interests", "interests"), ("Contact", "contact")]
PAGES = []

def e(value):
    return escape(str(value), quote=True)

def local_asset(path):
    if not isinstance(path, str) or not path or "\\" in path or ".." in Path(path).parts or path.startswith("/") or urlparse(path).scheme:
        raise ValueError(f"Asset must be a relative local path: {path!r}")
    resolved = (ROOT / path).resolve()
    if not resolved.is_relative_to((ROOT / "assets").resolve()) or not resolved.is_file():
        raise ValueError(f"Missing asset: {path}")
    return path

def external_url(url):
    if urlparse(url).scheme != "https" or not urlparse(url).netloc:
        raise ValueError("External links must be absolute HTTPS URLs")
    return url

def validate():
    for collection in ("galleries", "projects", "conferences", "customPages"):
        slugs = set()
        for item in DATA[collection]:
            slug = item["slug"]
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in slugs:
                raise ValueError(f"Invalid or duplicate slug: {slug}")
            slugs.add(slug)
            for photo in item.get("photos", []):
                local_asset(photo["src"])
                if not photo.get("alt") or not photo.get("title") or not isinstance(photo.get("width"), int) or not isinstance(photo.get("height"), int) or min(photo["width"], photo["height"]) < 1:
                    raise ValueError("Photos need title, alt text and positive integer width/height")
                if photo.get("full"): local_asset(photo["full"])
                for variant in photo.get("variants", []):
                    local_asset(variant["src"])
                    if not isinstance(variant.get("width"), int) or variant["width"] < 1:
                        raise ValueError("Photo variants need a positive integer width")
            for doc in item.get("documents", []):
                local_asset(doc["path"])
            if item.get("github"): external_url(item["github"])
    if DATA["contact"]["approved"] and DATA["contact"]["email"]:
        if not re.fullmatch(r"[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+", DATA["contact"]["email"]):
            raise ValueError("Invalid approved contact email")
    for social in DATA["contact"]["socials"]:
        external_url(social["url"])

def link(path):
    return "index.html" if not path else path + "/index.html"

def frame(title, label="Photographs to be added", number="", large=False):
    return f'<div class="frame {"frame-large" if large else ""}"><span class="frame-index">{e(number)}</span><span class="frame-title">{e(title)}</span><span class="label">{e(label)}</span><span class="frame-bottom">Image space</span></div>'

def pending(text):
    return f'<p class="pending"><span>Content to add</span>{e(text)}</p>'

def photo_image(photo, prefix, eager=False):
    variants = photo.get("variants", [])
    srcset = ' srcset="' + e(", ".join(prefix + v["src"] + " " + str(v["width"]) + "w" for v in variants)) + '" sizes="(max-width: 720px) 92vw, 70vw"' if variants else ""
    priority = ' fetchpriority="high"' if eager else ""
    return f'<img src="{e(prefix + photo["src"])}" alt="{e(photo["alt"])}" width="{photo["width"]}" height="{photo["height"]}" loading="{"eager" if eager else "lazy"}" decoding="async"{priority}{srcset}>'

def photos(items, prefix):
    if not items: return ""
    figures = []
    for photo in items:
        technical = photo.get("technical", "")
        caption = " · ".join(filter(None, [photo["title"], photo.get("description", ""), technical]))
        full = prefix + photo.get("full", photo["src"])
        figures.append(f'<figure><button class="photo-button" data-full="{e(full)}" data-caption="{e(caption)}" aria-label="View {e(photo["title"])}">{photo_image(photo,prefix)}</button><figcaption>{e(caption)}</figcaption></figure>')
    return '<div class="photos">' + "".join(figures) + '</div><dialog id="viewer" aria-label="Photograph viewer"><div class="viewer-top"><span class="viewer-counter" role="status" aria-live="polite"></span><button data-close type="button" autofocus>Close</button></div><img class="viewer-image" alt=""><div class="viewer-bottom"><p class="viewer-caption"></p><div class="viewer-controls"><button data-previous type="button" aria-label="Previous photograph">Previous</button><button data-next type="button" aria-label="Next photograph">Next</button></div></div></dialog>'

def docs(items, prefix):
    if not items: return pending("Resolutions, notes or supporting files.")
    return '<ul class="bullet-list">' + "".join(f'<li><a href="{e(prefix + doc["path"])}">{e(doc["title"])}</a></li>' for doc in items) + '</ul>'

def page(path, title, description, body, active=""):
    depth = len(path.split("/")) if path else 0
    prefix = "../" * depth
    # Body uses @/ as a root-relative token, replaced for subdirectory deployment.
    body = body.replace("@/", prefix)
    navigation = "".join(f'<a href="{prefix}{link(slug)}" {"aria-current=page" if slug == active else ""}>{label}</a>' for label, slug in NAV)
    url = DATA.get("siteUrl", "").rstrip("/") + "/" + (path + "/" if path else "")
    canonical = f'<link rel="canonical" href="{e(url)}"><meta property="og:url" content="{e(url)}">' if DATA.get("siteUrl") else ""
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)} | Aiden Lapierre</title><meta name="description" content="{e(description)}">
<meta name="theme-color" content="#f6f5f1"><meta property="og:type" content="website"><meta property="og:title" content="{e(title)} | Aiden Lapierre"><meta property="og:description" content="{e(description)}">{canonical}
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}assets/style.css"><script src="{prefix}assets/gallery.js" defer></script>
</head><body><a class="skip" href="#main">Skip to content</a><header class="wrap"><div class="masthead"><a class="brand" href="{prefix}index.html">Aiden Lapierre</a><span class="location">Student portfolio<br>The Netherlands</span><button class="menu-toggle" aria-expanded="false" aria-controls="navigation" type="button">Menu</button></div><nav class="nav" id="navigation" aria-label="Main navigation">{navigation}</nav></header>
<main class="wrap" id="main">{body}</main><footer class="wrap footer"><span>© 2026 Aiden Lapierre</span><span><a href="{prefix}about/index.html">About</a><a href="{prefix}contact/index.html">Contact</a><a href="{prefix}assets/studio.html">Content studio</a><a href="#main">Back to top ↑</a></span></footer>
<script>document.querySelector('.nav').classList.add('js-ready')</script></body></html>'''
    dest = OUT / path / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
    PAGES.append((path, url))

def head(number, title, description, crumb=""):
    breadcrumb = f'<div class="breadcrumb">{crumb}</div>' if crumb else ""
    return f'<div class="page-head">{breadcrumb}<p class="label">{e(number)}</p><h1>{e(title)}</h1><p>{e(description)}</p></div>'

def section(title, content):
    return f'<section class="detail-section"><h2>{e(title)}</h2>{content}</section>'

def gallery_nav(active=""):
    return '<nav class="gallery-nav" aria-label="Photography categories">' + "".join(f'<a href="@/photography/{g["slug"]}/index.html" {"aria-current=page" if g["slug"]==active else ""}>{e(g["title"])}</a>' for g in DATA["galleries"]) + '</nav>'

def home():
    selected = next(((g, p) for g in DATA["galleries"] for p in g["photos"] if p.get("featured")), None)
    if selected is None:
        selected = next(((g,p) for g in DATA["galleries"] for p in g["photos"]), None)
    visual = photo_image(selected[1], "@/", True) if selected else frame("Selected photography", "Awaiting Aiden’s photographs", "01 / Photography", True)
    photo_path = f'photography/{selected[0]["slug"]}/index.html' if selected else 'photography/index.html'
    caption = selected[1]["title"] if selected else "A place for my photographs"
    rows = "".join(f'<a class="row" href="@/photography/{g["slug"]}/index.html"><span class="number">0{i+1}</span><h3>{e(g["title"])}</h3><p>{e(g["description"])}</p><span aria-hidden="true">↗</span></a>' for i,g in enumerate(DATA["galleries"]))
    mun = "".join(f'<a class="row" href="@/model-un/{c["slug"]}/index.html"><span class="number">0{i+1}</span><div><h3>{e(c["name"])}</h3><p>{e(c["country"])} · {e(c["committee"])}</p></div><span aria-hidden="true">↗</span></a>' for i,c in enumerate(DATA["conferences"][-3:]))
    projects = "".join(f'<a class="row" href="@/technology/{p["slug"]}/index.html"><span class="number">0{i+1}</span><div><h3>{e(p["title"])}</h3><p>{e(p["status"])} · {e(p["category"])}</p></div><span aria-hidden="true">↗</span></a>' for i,p in enumerate([DATA["projects"][0],DATA["projects"][2],DATA["projects"][4]]))
    body = f'''<div class="intro"><div><p class="label">Photography, projects & student life</p><h1 class="home-title">Looking closely.<br><em>Learning by doing.</em></h1></div><p>{e(DATA["intro"])}</p></div>
<div class="photo-lead"><figure><a href="@/{photo_path}" aria-label="Explore photography">{visual}</a><figcaption><span>{e(caption)}</span><span>Photography / 01</span></figcaption></figure><div class="side-note"><p class="label">The portfolio</p><h2>Places, people<br>& things I make.</h2><p>Landscapes, streets, wildlife, aircraft and film. Photography is the starting point, with the rest of my work alongside.</p><a class="text-link" href="@/photography/index.html">Explore photography ↗</a></div></div>
<section class="section"><div class="section-heading"><div><p class="label">01 / Photography</p><h2>Five ways of looking</h2></div><a class="text-link" href="@/photography/index.html">All galleries ↗</a></div><div class="split"><div><p>Digital and film work, organised by subject. Each collection has space for photographs and notes about how they were made.</p></div><div class="list">{rows}</div></div></section>
<div class="home-columns"><section class="section"><div class="section-heading"><div><p class="label">02 / International affairs</p><h2>Model United Nations</h2></div><a class="text-link" href="@/model-un/index.html">All conferences ↗</a></div><div class="list">{mun}</div></section><section class="section"><div class="section-heading"><div><p class="label">03 / Technical work</p><h2>On the workbench</h2></div><a class="text-link" href="@/technology/index.html">All projects ↗</a></div><div class="list">{projects}</div></section></div>
<section class="statement"><div><p class="label">04 / About me</p><a class="text-link" href="@/about/index.html">Read my introduction ↗</a></div><p>I study at the International School of The Hague. This is a record of what I make, what I photograph and what I learn along the way.</p></section>'''
    page("", "Photography & projects", DATA["intro"], body)

def photography():
    cards = []
    for i,g in enumerate(DATA["galleries"]):
        cover = photo_image(g["photos"][0],"@/") if g["photos"] else frame(g["title"],number=f"0{i+1}")
        cards.append(f'<article><a class="cover" href="@/photography/{g["slug"]}/index.html" aria-label="Explore {e(g["title"])} photography">{cover}</a><div><p class="label">0{i+1} / {len(g["photos"])} photographs</p><h2><a href="@/photography/{g["slug"]}/index.html">{e(g["title"])}</a></h2><p>{e(g["description"])}</p></div></article>')
    body = head("01 / Visual work","Photography","Landscapes, everyday life and moving subjects. Photographs made with digital cameras and on film.") + '<div class="gallery-index">' + "".join(cards) + '</div>'
    page("photography", "Photography", "Aiden Lapierre’s landscape, street, wildlife, aviation and film photography.", body, "photography")
    for i,g in enumerate(DATA["galleries"]):
        body = head(f"01.{i+1:02} / Photography",g["title"],g["description"],'<a href="@/photography/index.html">Photography</a> / '+e(g["title"]))
        body += photos(g["photos"],"@/") if g["photos"] else '<div class="gallery-blank">'+frame(g["title"],"Photographs to be added",large=True)+'</div><p class="empty-note">This collection is waiting for my photographs. No sample images are presented as my work.</p>'
        body += gallery_nav(g["slug"])
        page("photography/"+g["slug"],g["title"]+" photography",g["description"],body,"photography")

def model_un():
    records = []
    for i,c in enumerate(DATA["conferences"]):
        award = f'<span class="award">{e(c["award"])}</span>' if c["award"] else '<span class="small">Conference participation</span>'
        records.append(f'<article class="record"><span class="number">0{i+1}</span><div><h2><a href="@/model-un/{c["slug"]}/index.html">{e(c["name"])}</a></h2><p>{e(c["country"])}</p></div><div><span class="label">Committee</span><p>{e(c["committee"])}</p></div>{award}</article>')
    body = head("02 / Debate & diplomacy","Model United Nations","Researching international issues, representing a country’s position and working with other delegates.") + '<div>'+"".join(records)+'</div>'
    page("model-un","Model United Nations","Aiden Lapierre’s Model UN conference experience and delegate awards.",body,"model-un")
    for c in DATA["conferences"]:
        facts = f'<dl class="facts"><div><dt>Country</dt><dd>{e(c["country"])}</dd></div><div><dt>Committee</dt><dd>{e(c["committee"])}</dd></div><div><dt>Date</dt><dd>{e(c["date"] or "To be added")}</dd></div>'
        if c["award"]: facts += f'<div><dt>Recognition</dt><dd>{e(c["award"])}</dd></div>'
        facts += '</dl>'
        topics = '<ul class="bullet-list">'+"".join(f'<li>{e(t)}</li>' for t in c["topics"])+'</ul>' if c["topics"] else pending("Conference agenda and issues debated.")
        reflection = '<p>'+e(c["reflection"])+'</p>' if c["reflection"] else pending("My experience, contributions and what I learned.")
        body = head("02 / Conference record",c["name"],c["description"],'<a href="@/model-un/index.html">Model UN</a> / '+e(c["name"]))
        body += '<div class="detail"><aside>'+facts+'</aside><div class="detail-body">'+section("Agenda",topics)+section("Reflection",reflection)+section("Resolutions & documents",docs(c["documents"],"@/"))+section("Photographs",photos(c["photos"],"@/") or pending("Conference photographs with captions."))+'</div></div>'
        page("model-un/"+c["slug"],c["name"],c["description"],body,"model-un")

def technology():
    rows = "".join(f'<a class="row" href="@/technology/{p["slug"]}/index.html"><span class="number">0{i+1}</span><div><span class="label">{e(p["category"])}</span><h2>{e(p["title"])}</h2></div><p>{e(p["summary"])}</p><span class="status">{e(p["status"])}</span><span aria-hidden="true">↗</span></a>' for i,p in enumerate(DATA["projects"]))
    body = head("03 / Electronics & technology","Projects & experiments","Building, testing and learning how systems work. A record of technical work at different stages of development.")+'<div class="project-index">'+rows+'</div>'
    page("technology","Electronics & technology","FPV drones, CAD, soldering, Raspberry Pi, servers, radio and programming projects.",body,"technology")
    for p in DATA["projects"]:
        facts = '<dl class="facts"><div><dt>Area</dt><dd>'+e(p["category"])+'</dd></div><div><dt>Stage</dt><dd>'+e(p["status"])+'</dd></div></dl>'
        specs = '<table class="table"><caption class="label">Technical specifications</caption><tbody>'+"".join(f'<tr><th scope="row">{e(s["label"])}</th><td>{e(s["value"])}</td></tr>' for s in p["specs"])+'</tbody></table>' if p["specs"] else pending("Components, dimensions, software and technical specifications.")
        challenges = '<ul class="bullet-list">'+"".join(f'<li>{e(t)}</li>' for t in p["challenges"])+'</ul>' if p["challenges"] else pending("Problems encountered, attempted solutions and lessons learned.")
        progress = '<ol class="bullet-list">'+"".join(f'<li><strong>{e(t["date"])}</strong><p>{e(t["text"])}</p></li>' for t in p["progress"])+'</ol>' if p["progress"] else pending("Dated development notes and evidence of completed steps.")
        github = f'<p><a href="{e(p["github"])}">View source on GitHub ↗</a></p>' if p["github"] else ""
        body = head("03 / Project record",p["title"],p["summary"],'<a href="@/technology/index.html">Technology</a> / '+e(p["title"]))
        body += '<div class="detail"><aside>'+facts+github+'</aside><div class="detail-body">'+section("Overview",'<p>'+e(p["description"])+'</p>')+section("Project photographs",photos(p["photos"],"@/") or pending("Build photographs, CAD renders or screenshots."))+section("Technical details",specs)+section("Challenges & learning",challenges)+section("Development record",progress)+section("Documentation",docs(p["documents"],"@/"))+'</div></div>'
        page("technology/"+p["slug"],p["title"],p["summary"],body,"technology")

def remaining():
    a = DATA["academics"]
    subjects = '<div class="subjects">'+"".join('<span>'+e(s)+'</span>' for s in a["subjects"])+'</div>'
    academic_projects = "".join('<article class="detail-section"><h3>'+e(p["title"])+'</h3><p>'+e(p["text"])+'</p></article>' for p in a["projects"]) or pending("Selected coursework, investigations and research, with dates and supporting work.")
    achievements = '<ul class="bullet-list">'+"".join('<li>'+e(t)+'</li>' for t in a["achievements"])+'</ul>' if a["achievements"] else pending("Confirmed academic achievements. No grades or qualifications have been added.")
    body = head("04 / Education","Academics","My education, academic interests and independent learning.")
    body += '<div class="detail"><aside><dl class="facts"><div><dt>School</dt><dd>'+e(DATA["school"])+'</dd></div><div><dt>Curriculum</dt><dd>International Baccalaureate</dd></div><div><dt>Programme</dt><dd>Middle Years Programme</dd></div></dl></aside><div class="detail-body">'+section("Areas of interest",'<p>My interests connect sciences, design, technology and the study of people and society.</p>'+subjects)+section("Academic work",academic_projects)+section("DP planning",'<p>'+e(a["dpPlanning"])+'</p>')+section("Achievements",achievements)+section("Looking ahead",'<p>'+e(a["aspirations"])+'</p>' if a["aspirations"] else pending("University interests, possible courses and future plans."))+'</div></div>'
    page("academics","Academics","Education and academic interests at the International School of The Hague.",body,"academics")
    body = head("05 / Introduction","About me","A student with interests across photography, technology, international affairs and music.")
    body += '<div class="about"><div>'+frame("Aiden Lapierre","Portrait to be added")+'<p class="small" style="margin-top:12px">Based in the Netherlands</p></div><div class="prose"><p>I’m Aiden Lapierre. I study the IB curriculum at the International School of The Hague.</p><p>I enjoy photographing landscapes, streets, wildlife and aircraft, and working with both digital cameras and film. I’m interested in how a photograph records a place or a moment.</p><p>Outside photography, I build and explore electronics and computing systems. My projects include drones, aircraft CAD, Raspberry Pi experiments and a home lab.</p><p>Model United Nations gives me another way to learn about international affairs through research and debate. I also play piano and explore composition.</p><h2>Why this website</h2><p>I wanted one place to bring these interests together and keep a record as my work develops.</p><a class="text-link" href="@/interests/index.html">Other interests ↗</a></div></div>'
    page("about","About","About Aiden Lapierre, a student interested in photography, technology, aviation, international relations and music.",body,"about")
    body = head("06 / Beyond the main subjects","Other interests","Music, writing and a space for activities that develop over time.")
    custom_links = "".join(f'<article class="interest"><span class="label">Page</span><h2><a href="@/pages/{p["slug"]}/index.html">{e(p["title"])}</a></h2><p>{e(p["description"])}</p></article>' for p in DATA["customPages"])
    body += '<div class="interests">'+"".join(f'<article class="interest"><span class="label">0{i+1}</span><h2>{e(t["title"])}</h2><p>{e(t["text"])}</p></article>' for i,t in enumerate(DATA["interests"]))+custom_links+'</div>'
    page("interests","Other interests","Music, piano composition, writing and future activities.",body,"interests")
    contact = DATA["contact"]
    if contact["approved"] and contact["email"]:
        direct = '<h2>Email</h2><p><a href="mailto:'+e(contact["email"])+'">'+e(contact["email"])+'</a></p>'
    else:
        direct = '<h2>Contact details</h2><p>A contact address has not been published yet.</p>'
    if contact["approved"] and contact["socials"]:
        direct += '<ul class="bullet-list">'+"".join('<li><a href="'+e(s["url"])+'">'+e(s["label"])+'</a></li>' for s in contact["socials"])+'</ul>'
    body = head("07 / Get in touch","Contact","For photography, student projects and Model UN.")
    body += '<div class="contact-box"><div><h2>Start a conversation</h2><p>I’m interested in hearing about photography opportunities, student collaborations and shared projects.</p></div><div>'+direct+'</div></div>'
    page("contact","Contact","Contact information for Aiden Lapierre’s portfolio.",body,"contact")


def custom_pages():
    for item in DATA["customPages"]:
        section_html = "".join(section(part.get("heading", "Notes"), '<p>'+e(part.get("body", ""))+'</p>') for part in item.get("sections", []))
        if not section_html:
            section_html = pending("Add sections and text in the Content Studio.")
        body = head("08 / Additional page", item["title"], item["description"], '<a href="@/interests/index.html">Other interests</a> / '+e(item["title"]))
        body += '<div class="detail"><aside><p class="label">Personal page</p></aside><div class="detail-body">'+section_html+'</div></div>'
        page("pages/"+item["slug"], item["title"], item["description"], body, "interests")

def main():
    validate()
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    shutil.copy2(ROOT / "content/portfolio.json", OUT / "assets/portfolio.json")
    home(); photography(); model_un(); technology(); remaining(); custom_pages()
    page("404","Page not found","This page could not be found.",head("404","Page not found","The page may have moved.")+'<p><a href="../index.html">Return home</a></p>',"")
    # Hosts use dist/404.html at arbitrary paths, so its asset and nav references need an absolute base.
    absolute = DATA.get("siteUrl", "").rstrip("/") + "/" if DATA.get("siteUrl") else "/"
    (OUT / "404.html").write_text((OUT / "404/index.html").read_text().replace("../", absolute))
    if DATA.get("siteUrl"):
        urls = "".join('<url><loc>'+e(url)+'</loc></url>' for path,url in PAGES if path != "404")
        (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>')
    (OUT / "robots.txt").write_text("User-agent: *\nAllow: /\n"+("Sitemap: "+DATA["siteUrl"].rstrip("/")+"/sitemap.xml\n" if DATA.get("siteUrl") else ""))
    print(f"Built {len(PAGES)} pages in {OUT}")

if __name__ == "__main__":
    main()
