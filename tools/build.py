#!/usr/bin/env python3
"""Bygger hela boredprinter.com till public/ från content/ och site/.
Kör: python3 tools/build.py"""
from html import escape as html_escape
import json, re, html, datetime, shutil, hashlib
from pathlib import Path
import yaml, markdown, sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blocks import preprocess

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"
SITE = json.loads((ROOT / "site/site.json").read_text())
URL = SITE["url"]
TODAY = datetime.date.today().isoformat()
e = html.escape

# ---------- innehåll ----------
def load(p):
    raw = p.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    meta = yaml.safe_load(m.group(1)); body = m.group(2)
    meta["slug"] = p.stem; meta["body"] = body
    return meta

GUIDES = sorted([load(p) for p in (ROOT / "content/guides").glob("*.md")], key=lambda g: g["order"])
FREE = [g for g in GUIDES if g["type"] == "free"]
PREM = [g for g in GUIDES if g["type"] == "premium"]
PROD = SITE["products"]

# ---------- assets (cache-bustade) ----------
(OUT / "assets").mkdir(parents=True, exist_ok=True)
css = (ROOT / "site/site.css").read_text()
js = (ROOT / "site/site.js").read_text().replace("__SB_URL__", SITE["supabase_url"]).replace("__SB_ANON__", SITE["supabase_anon"])
ver = hashlib.sha1((css + js + (ROOT / "site/reader.js").read_text()).encode()).hexdigest()[:8]
(OUT / "assets/site.css").write_text(css)
(OUT / "assets/site.js").write_text(js)
(OUT / "assets/reader.js").write_text((ROOT / "site/reader.js").read_text())

LOGO = '<svg viewBox="0 0 64 64" aria-hidden="true"><rect x="15" y="54" width="9" height="6" rx="2" fill="#1A1918"/><rect x="40" y="54" width="9" height="6" rx="2" fill="#1A1918"/><rect x="8" y="7" width="48" height="50" rx="11" fill="#1A1918"/><rect x="14" y="18" width="36" height="30" rx="6" fill="#FFF8F1"/><path d="M27 13h10v7l-5 5-5-5z" fill="#FF5B1F"/><path d="M19 33.5h10a5 5 0 0 1-10 0z" fill="#1A1918"/><path d="M35 33.5h10a5 5 0 0 1-10 0z" fill="#1A1918"/><path d="M28.5 43h7" stroke="#1A1918" stroke-width="2.6" stroke-linecap="round"/></svg>'
LOGO_W = LOGO.replace('fill="#1A1918"', 'fill="#FFFFFF"').replace('stroke="#1A1918"', 'stroke="#FFFFFF"').replace('#FFF8F1', '#1A1918')
IG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>'

def head(title, desc, path, extra_ld=None, og_type="website", noindex=False, image=None):
    can = URL + path
    ld = [{"@context": "https://schema.org", "@type": "Organization", "name": "boredprinter", "url": URL, "logo": URL + "/icon-512.png", "sameAs": [SITE["instagram"]]}]
    if extra_ld: ld += extra_ld
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{can}">
{'<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'}
<meta name="google-site-verification" content="k2pg0YUW4uSaR17aU-OOrcagvWNx2prDQFDTYDuasYI">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="boredprinter">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{can}">
<meta property="og:image" content="{URL}{image or "/og.png"}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBFAF7">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700..800&family=Geist:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={ver}">
<script type="application/ld+json">{json.dumps(ld if len(ld) > 1 else ld[0], ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""

def header(active=""):
    def a(href, label, key, cls=""):
        cur = ' aria-current="page"' if key == active else ""
        return f'<a href="{href}" class="{cls}"{cur}>{label}</a>'
    return f"""<header class="top"><div class="wrap">
<a class="logo" href="/" aria-label="boredprinter home">{LOGO}boredprinter</a>
<nav class="nav" aria-label="Main">{a('/guides', 'Guides', 'guides')}{a('/tools/3d-print-price-calculator', 'Calculator', 'calc', 'hm')}{a('/library', 'My guides', 'lib', 'hm')}<a class="btn or" href="/guides/print-to-profit">Get the guide</a></nav>
</div></header>"""

def footer():
    free = "".join(f'<a href="/guides/{g["slug"]}">{e(g.get("nav", g["h1"]))}</a>' for g in FREE)
    prem = "".join(f'<a href="/guides/{g["slug"]}">{e(g["h1"])}</a>' for g in PREM)
    return f"""<footer class="foot"><div class="wrap">
<div><a class="logo" href="/">{LOGO}boredprinter</a><p style="margin:0;max-width:34ch">Honest guides to making money with your 3D printer. Made by <a href="{SITE['instagram']}" rel="noopener" style="display:inline;color:var(--ink);font-weight:600">@boredprinter</a>.</p></div>
<div><b>Free guides</b>{free}<a href="/tools/3d-print-price-calculator">Price calculator</a></div>
<div><b>Premium</b>{prem}<a href="/library">My guides</a></div>
<div><b>About</b><a href="/about">About</a><a href="{SITE['instagram']}" rel="noopener" class="igl">{ico('ig', 16)} Instagram</a><a href="/privacy">Privacy</a><a href="/terms">Terms &amp; refunds</a></div>
<p class="fine">© {datetime.date.today().year} boredprinter. Not legal or tax advice. Rules and fees change, always check the source.</p>
</div></footer>
<script src="/assets/site.js?v={ver}" defer></script>
</body></html>"""

def cover(prod_key, cls=""):
    g = next(x for x in PREM if x["product"] == prod_key)
    alt = e(g["h1"]) + " guide cover"
    if cls == "book" or cls == "":
        w, h = (857, 1200) if prod_key == "playbook" else (826, 1200)
        return f'<img class="bookimg" src="/img/book-{prod_key}.webp" alt="{alt}" width="{w}" height="{h}" fetchpriority="high">'
    return f'<img class="coverimg" src="/img/cover-{prod_key}.webp" alt="{alt}" width="600" height="800">'

def buy_btn(key, cls="btn or big wide"):
    p = PROD[key]
    if p.get("link"):
        return f'<a class="{cls}" href="{e(p["link"])}">Buy now · ${p["price"]}</a>'
    return f'<a class="{cls}" href="#waitlist">Get notified at launch</a>'

def signup(src="home", title="Free: The First Sale Checklist", text="A one-page checklist that takes you from idea to your first sale, plus new guides when they come out.", bullets=("The 12 steps to your first sale", "The license check, in 30 seconds", "Pricing cheat sheet"), light=False, anchor=""):
    ok = e('<p class="ok"><b>Done! 🎉</b> Your checklist: <a href="/free/first-sale-checklist.pdf" target="_blank" rel="noopener">open the PDF</a>. New guides will come to your inbox.</p>')
    lis = "".join(f"<li>{e(b)}</li>" for b in bullets)
    return f"""<div class="signup{' light' if light else ''}"{f' id="{anchor}"' if anchor else ''}>
<div><h2>{e(title)}</h2><p>{e(text)}</p><ul>{lis}</ul></div>
<form class="sform" data-src="{src}" data-btn="Send me the checklist" data-ok="{ok}" novalidate>
<label for="em-{src}" class="skip">Email</label>
<input id="em-{src}" type="email" name="email" placeholder="you@email.com" autocomplete="email" required>
<button class="btn or big" type="submit">Send me the checklist</button>
<p class="err" role="alert" hidden></p>
<small>Free. No spam. Unsubscribe any time.</small>
</form></div>"""

def stack_tables(html):
    """Ger varje cell en etikett från rubrikraden, så tabeller kan staplas på mobil."""
    def one(m):
        t = m.group(0)
        heads = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<th[^>]*>(.*?)</th>", t, flags=re.S)]
        if not heads: return t
        if heads[:3] == ["Day", "Task", "Chapter"]:
            rows = re.findall(r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>", t, flags=re.S)
            li = "".join(f'<li><span class="dn">Day {d.strip()}</span><span class="dt">{task}</span>{f"<span class=dc>Ch. {ch.strip()}</span>" if ch.strip() else ""}</li>' for d, task, ch in rows)
            return f'<ol class="days">{li}</ol>'
        def row(r):
            i = [0]
            def cell(c):
                lab = heads[i[0]] if i[0] < len(heads) else ""; i[0] += 1
                return f'<td data-label="{html_escape(lab)}"' + c.group(1) + ">"
            r2 = re.sub(r"<td([^>]*)>", cell, r.group(0))
            # Första cellen är bara en siffra (t.ex. dag 1) → visa "Day 1"
            return re.sub(r'<td data-label="([^"]*)"([^>]*)>(\s*\d+\s*)</td>', lambda x: f'<td data-label="{x.group(1)}" class="num"{x.group(2)}>{x.group(3)}</td>', r2, count=1)
        return '<table class="stack">' + re.sub(r"<tr>.*?</tr>", row, t[len("<table>"):], flags=re.S)
    return re.sub(r"<table>.*?</table>", one, html, flags=re.S)

def card(g):
    meta = f'{e(g.get("kicker") or "Guide")} · {g["read"]} min read' if g["type"] == "free" else f'Online guide · ${g["price"]}'
    th = OUT / "img/guides" / f'{g["slug"]}.webp'
    img = f'<img class="cthumb" src="/img/guides/{g["slug"]}.webp" alt="" width="1600" height="900" loading="lazy">' if g["type"] == "free" and th.exists() else ""
    return f'<a class="card{" hasimg" if img else ""}" href="/guides/{g["slug"]}">{img}<h3>{e(g["h1"])}</h3><p>{e(g["summary"])}</p><span class="meta">{meta} →</span></a>'

CALC_CARD = '<a class="card tool" href="/tools/3d-print-price-calculator"><h3>3D print price calculator</h3><p>Filament, power, machine wear, your time and fees. Get a price that is worth it.</p><span class="meta">Free tool · Use it →</span></a>'

def prod_cards(only=None):
    out = []
    for g in PREM:
        if only and g["product"] not in only: continue
        k = g["product"]; p = PROD[k]
        out.append(f"""<div class="prod">{cover(k, "flat")}<div><h3><a href="/guides/{g['slug']}" style="text-decoration:none">{e(g['h1'])}</a></h3><p>{e(g['summary'])}</p><div class="row"><span class="price">${p['price']}</span><a class="btn" href="/guides/{g['slug']}">See what's inside</a></div></div></div>""")
    one = " one" if len(out) == 1 else ""
    if "bundle" not in PROD or len(PREM) < 2:
        return f'<div class="prods{one}">{"".join(out)}</div>'
    b = PROD["bundle"]; full = sum(PROD[g["product"]]["price"] for g in PREM)
    bl = f'<a class="btn or" href="{e(b["link"])}">Get both · ${b["price"]}</a>' if b.get("link") else '<a class="btn or" href="/guides/print-to-profit#waitlist">Get notified</a>'
    return f'<div class="prods{one}">{"".join(out)}</div><div class="bundle"><div><b>Get both guides · ${b["price"]}</b><br><span>Save ${full - b["price"]} compared to buying them separately.</span></div>{bl}</div>'

def faq_html(items):
    return '<div class="faq">' + "".join(f"<details><summary>{e(f['q'])}</summary><p>{e(f['a'])}</p></details>" for f in items) + "</div>"

def faq_ld(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in items]}

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": URL + u} for i, (n, u) in enumerate(items)]}

def write(path, html_):
    p = OUT / (path.strip("/") or "index")
    p = p.with_suffix(".html") if path != "/" else OUT / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(html_)

AUTHOR = {"@type": "Person", "name": "Kevin", "url": URL + "/about", "image": URL + "/img/kevin.webp", "sameAs": [SITE["instagram"]], "jobTitle": "Creator of @boredprinter"}
def ico(name, size=20):
    P = {
      "ig": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>',
      "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
      "refresh": '<path d="M20 11a8 8 0 0 0-14.5-4.5L4 8"/><path d="M4 3v5h5"/><path d="M4 13a8 8 0 0 0 14.5 4.5L20 16"/><path d="M20 21v-5h-5"/>',
      "shield": '<path d="M12 3l7 3v6c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
      "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18.5h2"/>',
      "book": '<path d="M4 4.5A1.5 1.5 0 0 1 5.5 3H20v15H5.5A1.5 1.5 0 0 0 4 19.5z"/><path d="M4 19.5A1.5 1.5 0 0 0 5.5 21H20"/>',
      "sheet": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 10h18M3 15h18M9 4v16"/>',
      "file": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',
      "box": '<path d="M3 7l9-4 9 4v10l-9 4-9-4z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
      "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
      "store": '<path d="M3 9l1.5-5h15L21 9"/><path d="M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/><path d="M5 12v8h14v-8"/>',
      "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
      "coins": '<ellipse cx="9" cy="6" rx="6" ry="2.5"/><path d="M3 6v4c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5V6"/><path d="M9 15.5c-3.3 0-6-1.1-6-2.5v4c0 1.4 2.7 2.5 6 2.5 1.2 0 2.3-.1 3.2-.4"/><ellipse cx="17" cy="15" rx="4.5" ry="2"/><path d="M12.5 15v3c0 1.1 2 2 4.5 2s4.5-.9 4.5-2v-3"/>',
      "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
      "spool": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/><path d="M12 3v6M12 15v6"/>',
      "printer": '<path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M7 14h10v7H7z"/>',
      "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
      "percent": '<path d="M19 5L5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/>',
      "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
      "scale": '<path d="M12 3v18M7 21h10M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/>',
      "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
      "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
    }[name]
    return f'<svg class="i" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P}</svg>'

def trust_row(items=(("bolt", "Instant access"), ("shield", "30-day money-back guarantee"), ("lock", "Secure checkout by Stripe"))):
    return '<ul class="trow">' + "".join(f"<li>{ico(i, 16)}<span>{t}</span></li>" for i, t in items) + "</ul>"

def icons_md(html):
    return re.sub(r"\{\{ico:([a-z]+)\}\}", lambda m: ico(m.group(1), 18), html)

def inc_icon(x):
    t = x.lower()
    for k, n in (("spreadsheet", "sheet"), ("toolkit", "sheet"), ("template", "file"), ("script", "file"), ("example", "box"), ("checklist", "calendar"), ("sprint", "calendar"), ("update", "refresh"), ("online", "book"), ("phone", "phone"), ("device", "phone"), ("instant", "bolt")):
        if k in t: return ico(n)
    return ico("book")

AUTHOR_BOX = f'<aside class="author"><img src="/img/kevin.webp" alt="Kevin, the creator of boredprinter" width="480" height="480" loading="lazy"><div><b>Written by Kevin</b><p>I run <a href="{SITE["instagram"]}" rel="noopener">@boredprinter</a> on Instagram, where {SITE["followers"]} people follow my 3D printing. I write these guides to show what actually works when you sell your prints, without the hype.</p><div class="ctas" style="margin-top:10px"><a class="btn" href="{SITE["instagram"]}" rel="noopener">{ico("ig", 16)} Follow</a><a class="more" href="/about">More about me →</a></div></div></aside>'

PAGES = []  # för sitemap: (path, lastmod, prio)

# ---------- startsida ----------
HOME_FAQ = [
    {"q": "Can you really make money with a 3D printer?", "a": "Yes, but for most people it's a side income, not a salary. The people who do best sell their own designs to a specific group of buyers and price in their time. That's exactly what Print to Profit teaches."},
    {"q": "I'm a complete beginner at selling. Is this for me?", "a": "Yes. You need to know how to print. Everything about selling, from picking a product to getting paid, is explained step by step."},
    {"q": "What is Print to Profit, exactly?", "a": "A complete online guide you read on this site, on your phone or computer. It comes with pricing worksheets, listing templates and a 30-day plan, and you get free updates when rules or fees change."},
    {"q": "Do I need to know CAD or 3D design?", "a": "No. Print to Profit works without it, and shows you simple ways to make products that are your own design."},
    {"q": "What if it's not for me?", "a": "You have a 30-day money-back guarantee. Read it, try the plan. If it's not worth it to you, message me within 30 days and you get all your money back. No questions."},
    {"q": "Do I need an account to buy?", "a": "No. You pay with your email and get access right away. To come back later, log in with a link we email you. No password."},
]
INSIDE = f"""<div class="sech"><div><h2>Look inside</h2><p>Short chapters, made for your phone. Every one ends with a task you can do the same day.</p></div><a class="more" href="/guides/print-to-profit/pick-your-lane">Read chapter 1 free →</a></div>
<div class="inside">
<figure><div class="phone"><img src="/img/inside/quiz.webp" alt="A quiz in chapter 1 that picks your way to make money" width="780" height="1560" loading="lazy"></div><figcaption><b>Quizzes that decide for you</b>Find the way to earn that fits you.</figcaption></figure>
<figure><div class="phone"><img src="/img/inside/steps.webp" alt="Step-by-step pricing worksheet in chapter 6" width="780" height="1560" loading="lazy"></div><figcaption><b>Fill-in worksheets</b>Work out your real price, step by step.</figcaption></figure>
<figure><div class="phone"><img src="/img/inside/yesno.webp" alt="Clear do and don't lists in chapter 4" width="780" height="1560" loading="lazy"></div><figcaption><b>Clear yes and no</b>Know exactly what you can sell.</figcaption></figure>
</div>
"""
IGCHIP = f"""<a class="igchip" href="{SITE['instagram']}" rel="noopener"><img src="/img/kevin-sm.webp" alt="" width="40" height="40"><span><b>{SITE['followers']} followers</b><small>{ico('ig', 15)} @boredprinter on Instagram</small></span></a>"""
P = PROD["playbook"]
def launch_note(p):
    if not p.get("later_price"): return ""
    when = f' on {p["price_until"]}' if p.get("price_until") else " after launch"
    return f'Launch price. Goes up to ${p["later_price"]}{when}.'
main_cta = (f'<a class="btn or big" href="{e(P["link"])}">Get Print to Profit · ${P["price"]}</a>' if P.get("link")
            else '<a class="btn or big" href="/guides/print-to-profit#waitlist">Get early access</a>')
CHECK = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
CROSS = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><path d="M7 7l10 10M17 7L7 17"/></svg>'
pains = ["Your printer mostly sits there doing nothing", "You have no idea what would actually sell", "You're not sure what you're even allowed to sell", "Your prices barely cover the filament", "Etsy's new rules confuse you"]
learn = [
    ("What to make", "A simple method to find products people already want to buy, so you don't waste weeks on things that don't sell."),
    ("How to design it yourself", "Your own product in Tinkercad (free) in about an hour, plus names and text in Bambu Studio. No design skills needed."),
    ("What you're allowed to sell", "Licenses and Etsy's 2025 rules in plain English, so your shop doesn't get shut down."),
    ("What to charge", "A spreadsheet that includes filament, power, your time and fees, so every sale is actually worth it."),
    ("Where to sell", "Etsy, eBay, Facebook Marketplace, TikTok Shop, your own link or local shops. What each one costs, and which fits your product."),
    ("How to get your first 10 sales", "Photos, listings and posts that sell, without paying for ads."),
    ("A 30-day plan", "What to do each day, from today until your first sales come in. With one worked example product followed through every step."),
]
steps = [("Pick one product", "Use the research method to find something a specific group of people wants."),
         ("Price it right", "Run the numbers once with the worksheet. Never sell at a loss again."),
         ("Make your first sales", "Follow the 30-day plan: photos, listing, and getting it in front of buyers.")]
home = head("Make Money With Your 3D Printer | boredprinter",
            "Learn what to print, what to charge and where to sell it. Simple step-by-step guides to making money with your 3D printer, plus a free price calculator.",
            "/", [faq_ld(HOME_FAQ), {"@context": "https://schema.org", "@type": "WebSite", "name": "boredprinter", "url": URL}])
home += header() + f"""
<main id="main">
<section class="hero"><div class="wrap">
<div>
<h1>Turn your 3D printer into a <em>side income.</em></h1>
<p class="lead">Learn exactly what to print, what to charge and where to sell it. Step by step, and without breaking Etsy's new rules.</p>
<div class="ctas">{main_cta}<a class="btn ghost big" href="/guides/print-to-profit/pick-your-lane">Read chapter 1 free</a></div>
{IGCHIP}
<ul class="trust"><li>{ico('shield')}<span>30-day money-back guarantee</span></li><li>{ico('coins')}<span>{launch_note(P) or 'One-time payment, free updates'}</span></li></ul>
</div>
{cover('playbook')}
</div></section>

<section class="sec alt"><div class="wrap pain">
<div><h2>Bought a 3D printer to make money, but…</h2></div>
<ul class="xlist">{"".join(f"<li>{e(x)}</li>" for x in pains)}</ul>
<p class="pain-end">I see it in my comments all the time. People buy a printer to make money, try a few random prints, sell nothing and stop. They guessed what to make, what to charge and where to sell. <b>Print to Profit is the plan I wish they'd had.</b></p>
</div></section>

<section class="sec"><div class="wrap">
<div class="sech"><div><h2>What you'll learn in Print to Profit</h2><p>Everything you need to go from "I have a printer" to "people pay me for my prints".</p></div></div>
<ol class="learn">{"".join(f'<li><b>{e(t)}</b><p>{e(d)}</p></li>' for t, d in learn)}</ol>
</div></section>

<section class="sec"><div class="wrap">
{INSIDE}</div></section>



<section class="sec alt"><div class="wrap"><div class="me"><img src="/img/kevin.webp" alt="Kevin, the creator of boredprinter" width="480" height="480" loading="lazy"><div><h2>Hi, I'm Kevin</h2><p class="lead" style="margin-top:12px">I run <a href="{SITE['instagram']}" rel="noopener">@boredprinter</a>, where {SITE['followers']} people follow my 3D printing. The question I get most is: "Can you actually make money with this thing?"</p><p>These guides are my honest answer. No "$10k a month" promises. Just researched, up-to-date steps, checked against the current rules and written so anyone can follow them.</p><div class="ctas" style="margin-top:8px"><a class="btn" href="{SITE['instagram']}" rel="noopener">{ico('ig', 18)} Follow @boredprinter</a><a class="btn ghost" href="/about">More about me</a></div></div></div></div></section>

<section class="sec"><div class="wrap"><div class="offer">
<div class="offer-img">{cover('playbook')}</div>
<div>
<h2>Print to Profit</h2>
<p class="lead" style="margin-top:12px">A step-by-step 30-day plan to your first 10 sales.</p>
<ul class="inc">{"".join(f"<li>{inc_icon(x)}<span>{e(x)}</span></li>" for x in next(g for g in PREM if g['product']=='playbook')['includes'])}<li>{ico('phone')}<span>Instant access on any device</span></li></ul>
<p class="vstack">12 chapters · about 80 minutes · spreadsheet toolkit, templates, a worked example and a 30-day plan</p>
<div class="offer-buy"><span class="price big">${P['price']}</span><span class="once">{launch_note(P) or 'one-time payment'}</span></div><p class="valline vbox">{ico('spool', 18)}<span>About the price of 1.5 spools of filament. Sell 3 of the example product and it has paid for itself.</span></p>
<div class="ctas" style="margin-top:16px">{main_cta}<a class="btn ghost big" href="/guides/print-to-profit/pick-your-lane">Read chapter 1 free</a></div>
{trust_row()}
</div>
</div></div></section>



<section class="sec alt"><div class="wrap"><h2 style="margin-bottom:18px">Questions</h2>{faq_html(HOME_FAQ)}</div></section>

<section class="sec"><div class="wrap">
<div class="sech"><div><h2>Not ready to buy? Start free</h2><p>Our free guides answer the questions every beginner has.</p></div><a class="more" href="/guides">All guides →</a></div>
<div class="cards">{"".join(card(g) for g in FREE[:3])}{CALC_CARD}</div>
</div></section>



<section class="sec"><div class="wrap">{signup('home', anchor='waitlist')}</div></section>

<section class="sec"><div class="wrap final">
<h2>Your printer could be paying for itself.</h2>
<p class="lead" style="margin:14px auto 26px">Start today with Print to Profit, or read the free guide first.</p>
<div class="ctas" style="justify-content:center">{main_cta}<a class="btn ghost big" href="/guides/how-to-make-money-with-a-3d-printer">Read the free guide</a></div>
</div></section>
<div class="mcta" id="mcta" hidden><span><b>Print to Profit</b><small>30-day plan to your first 10 sales</small></span>{main_cta.replace('btn or big', 'btn or')}</div>
<script>(()=>{{const b=document.getElementById("mcta"),h=document.querySelector(".hero");if(!b||!h||!("IntersectionObserver" in window))return;new IntersectionObserver(es=>{{b.hidden=es[0].isIntersecting}}).observe(h)}})();</script>
</main>""" + footer()
write("/", home); PAGES.append(("/", TODAY, "1.0"))

# ---------- guideindex ----------
gi = head("3D Printing Business Guides: Free & Premium | boredprinter",
          "All boredprinter guides on making money with 3D printing: what sells, licenses, Etsy, pricing, and in-depth premium guides.",
          "/guides", [crumbs_ld([("Home", "/"), ("Guides", "/guides")])])
gi += header("guides") + f"""
<main id="main" class="art"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Guides</span></nav>
<div class="ahead"><h1>Guides to making money with 3D printing</h1><p class="lead">Start with the free guides. When you want the complete plan, the premium guides go deeper.</p></div>
<h2 style="font-size:26px;margin:10px 0 16px">Free</h2>
<div class="cards">{"".join(card(g) for g in FREE)}{CALC_CARD}</div>
<h2 style="font-size:26px;margin:44px 0 16px">Premium</h2>
{prod_cards()}
<div style="margin-top:48px">{signup('guides', light=True, anchor='waitlist')}</div>
</div></main>""" + footer()
write("/guides", gi); PAGES.append(("/guides", TODAY, "0.9"))

# ---------- gratisguider ----------
MD = lambda: markdown.Markdown(extensions=["tables", "toc", "attr_list", "sane_lists", "md_in_html"], extension_configs={"toc": {"permalink": False}})
for g in FREE:
    md = MD(); body = icons_md(md.convert(preprocess(g["body"])))
    body = stack_tables(body)
    body = re.sub(r"<table( class=\"stack\")?>", r'<div class="tbl"><table\1>', body).replace("</table>", "</table></div>")
    body = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener" target="_blank"', body)
    # upsell före "Sources" (eller sist)
    up = f"""<aside class="upsell">{cover('playbook', 'flat')}<div><b>Want the complete plan?</b><p>Print to Profit takes you step by step from idea to steady sales, with worksheets and templates.</p><a class="btn or" href="/guides/print-to-profit">See what's inside</a><p class="upg">{ico('shield', 15)} 30-day money-back guarantee</p></div></aside>"""
    if '<h2 id="sources">' in body: body = body.replace('<h2 id="sources">', up + '<h2 id="sources">', 1)
    else: body += up
    toc = "".join(f'<a href="#{t["id"]}">{e(t["name"])}</a>' for t in md.toc_tokens if t["id"] not in ("sources",))
    path = f"/guides/{g['slug']}"
    ld = [crumbs_ld([("Home", "/"), ("Guides", "/guides"), (g["h1"], path)]),
          {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "description": g["description"], "datePublished": str(g["updated"]), "dateModified": str(g["updated"]),
           "author": AUTHOR, "publisher": {"@type": "Organization", "name": "boredprinter", "logo": {"@type": "ImageObject", "url": URL + "/icon-512.png"}},
           "mainEntityOfPage": URL + path, "image": URL + "/og.png"}]
    if g.get("faq"): ld.append(faq_ld(g["faq"]))
    rel = [x for x in FREE if x["slug"] != g["slug"]][:3]
    upd = datetime.date.fromisoformat(str(g["updated"])).strftime("%B %-d, %Y")
    hero_f = OUT / "img/guides" / f"{g['slug']}.webp"
    hero = f'<img class="ahero" src="/img/guides/{g["slug"]}.webp" alt="{e(g.get("image_alt", g["h1"]))}" width="1600" height="900" fetchpriority="high">' if hero_f.exists() else ""
    if hero: ld[1]["image"] = URL + f"/img/guides/{g['slug']}.webp"
    page = head(g["title"], g["description"], path, ld, "article", image=(f"/img/guides/{g['slug']}.webp" if hero else None)) + header("guides") + f"""
<main id="main" class="art"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/guides">Guides</a> / <span>{e(g['kicker'])}</span></nav>
<header class="ahead"><h1>{e(g['h1'])}</h1><p class="lead">{e(g['summary'])}</p>
<div class="ameta"><span class="by"><img src="/img/kevin-sm.webp" alt="" width="26" height="26">By Kevin</span><span>Updated <time datetime="{g['updated']}">{upd}</time></span><span>{g['read']} min read</span></div></header>
{hero}<div class="agrid"><article class="prose">{body}
{('<h2 id="faq">Frequently asked questions</h2>' + faq_html(g['faq'])) if g.get('faq') else ''}
</article>
<aside class="toc" aria-label="On this page"><b>On this page</b>{toc}{'<a href="#faq">FAQ</a>' if g.get('faq') else ''}<div class="tbox"><b style="text-transform:none;letter-spacing:0;color:var(--ink);font-size:15px;margin:0">Free checklist</b><p>The 12 steps to your first sale.</p><a class="btn or wide" href="#waitlist">Get it free</a></div></aside>
</div>
<div style="margin-top:56px">{signup(g['slug'][:40], light=True, anchor='waitlist')}</div>
{AUTHOR_BOX}
<section class="related" style="margin-top:56px"><h2 style="font-size:28px;margin-bottom:16px">Keep reading</h2><div class="cards">{"".join(card(x) for x in rel)}</div></section>
</div></main>""" + footer()
    write(path, page); PAGES.append((path, str(g["updated"]), "0.8"))

# ---------- kurser (läsläge) ----------
COURSES = {}
LOCK = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'
for cy in sorted((ROOT / "content/course").glob("*/course.yaml")):
    c = yaml.safe_load(cy.read_text()); COURSES[c["guide"]] = c
    gdir = cy.parent; n = len(c["chapters"])
    (ROOT / "private/course" / c["guide"]).mkdir(parents=True, exist_ok=True)
    prod_k = c["product"]; P_ = PROD[prod_k]
    buy_url = P_["link"] or f"/guides/{c['guide']}#waitlist"
    buy_lbl = f"Get {c['title']} · ${P_['price']}" if P_["link"] else "Get early access"
    for i, ch in enumerate(c["chapters"]):
        src = gdir / f"{ch['slug']}.md"
        ch["ready"] = src.exists()
        if ch["ready"]:
            md = MD(); body = md.convert(preprocess(src.read_text().replace("{{BUY}}", e(buy_url)).replace("{{PRICE}}", str(P_["price"]))))
            heads = [re.sub(r"\s*\{#.*\}$", "", h).strip() for h in re.findall(r"^## (.+)$", src.read_text(), flags=re.M)]
            parts = [t for t in md.toc_tokens if t["name"] in heads and t["name"] not in ("Next chapter",)]
            if len(parts) >= 3:
                body = (f'<details class="otp"><summary>{ico("book", 16)}In this chapter · {len(parts)} parts</summary><ol>'
                        + "".join(f'<li><a href="#{t["id"]}">{e(t["name"])}</a></li>' for t in parts) + '</ol></details>') + body
            body = stack_tables(body)
            body = re.sub(r"<table( class=\"stack\")?>", r'<div class="tbl"><table\1>', body).replace("</table>", "</table></div>")
            body = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" rel="noopener" target="_blank"', body)
        else:
            body = f'<div class="call note"><span class="calli"></span><div><p><b>This chapter is being written.</b></p><p>You\'ll get an email when it\'s ready. It\'s included in what you bought, no extra cost.</p></div></div>'
        ch["html"] = body
        if not ch.get("free"):
            (ROOT / "private/course" / c["guide"] / f"{ch['slug']}.html").write_text(body)
    for i, ch in enumerate(c["chapters"]):
        path = f"/guides/{c['guide']}/{ch['slug']}"
        side = "".join(
            f'<a href="/guides/{c["guide"]}/{x["slug"]}" data-ch="{x["slug"]}"{" aria-current=page" if j == i else ""}><span class="chn">{j+1}</span><span class="cht">{e(x["title"])}</span>{"" if x.get("free") else "<span class=\"lk\">" + LOCK + "</span>"}</a>'
            for j, x in enumerate(c["chapters"]))
        prev_ = c["chapters"][i - 1] if i > 0 else None; next_ = c["chapters"][i + 1] if i < n - 1 else None
        nav = '<nav class="rnav">' + (f'<a class="btn ghost" href="/guides/{c["guide"]}/{prev_["slug"]}">← {e(prev_["title"])}</a>' if prev_ else '<span></span>') + (f'<a class="btn" href="/guides/{c["guide"]}/{next_["slug"]}">Next: {e(next_["title"])} →</a>' if next_ else '') + '</nav>'
        unlock = f"""<aside class="unlock"><img src="/img/cover-{prod_k}.webp" alt="" width="600" height="800"><div><b>Unlock all {n} chapters</b><p>{e(c['title'])} takes you from your first idea to your first 10 sales and beyond. Read it here, on any device.</p><a class="btn or" href="{e(buy_url)}">{e(buy_lbl)}</a>{trust_row()}<p class="small">Already bought? <a href="/library">Log in</a></p></div></aside>"""
        if ch.get("free"):
            content = f'<div class="prose">{ch["html"]}</div>{unlock}'
        else:
            content = f"""<div id="chBody" class="prose" data-g="{c['guide']}" data-c="{ch['slug']}" hidden></div>
<div id="chLock" class="lockbox"><div class="lki">{LOCK}</div><h2>This chapter is part of {e(c['title'])}</h2><p>{e(ch['summary'])}</p><a class="btn or big" href="{e(buy_url)}">{e(buy_lbl)}</a>{trust_row()}<p class="small">Already bought it? <a href="/library">Log in with your email</a> · <a href="/guides/{c['guide']}/{c['chapters'][0]['slug']}">Read chapter 1 free</a></p></div>
<p id="chLoad" class="small" hidden>Loading chapter…</p>"""
        title = f"{ch['title']} | {c['title']}, chapter {i+1}" + (" (free)" if ch.get("free") else "")
        ld = [crumbs_ld([("Home", "/"), ("Guides", "/guides"), (c["title"], f"/guides/{c['guide']}"), (ch["title"], path)])]
        if ch.get("free"):
            ld.append({"@context": "https://schema.org", "@type": "Article", "headline": f"{ch['title']}: {c['title']} chapter {i+1}", "description": ch["summary"], "author": AUTHOR, "mainEntityOfPage": URL + path, "image": URL + "/og.png", "datePublished": TODAY, "dateModified": TODAY})
        page = head(title, ch["summary"], path, ld, "article", noindex=not ch.get("free")) + header("guides") + f"""
<main id="main" class="art"><div class="wrap reader">
<aside class="rside" aria-label="Chapters"><details class="rtoc" open><summary><img src="/img/cover-{prod_k}.webp" alt="" width="600" height="800"><span><b>{e(c['title'])}</b><small>{n} chapters</small></span></summary><nav>{side}</nav></details></aside>
<div class="rmain">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/guides/{c['guide']}">{e(c['title'])}</a> / <span>Chapter {i+1}</span></nav>
<header class="ahead" style="margin:18px 0 26px"><p class="chk2">Chapter {i+1} of {n} · {ch['minutes']} min{' · Free to read' if ch.get('free') else ''}</p><div class="cprog" aria-hidden="true"><span style="width:{round((i+1)/n*100)}%"></span></div><h1 style="font-size:clamp(32px,4.6vw,48px)">{e(ch['title'])}</h1><p class="lead">{e(ch['summary'])}</p></header>
{content}
{nav}
</div></div></main>
<script src="/assets/reader.js?v={ver}" defer></script>""" + footer()
        write(path, page)
        if ch.get("free"): PAGES.append((path, TODAY, "0.8"))

# ---------- premiumsidor ----------
PREM_FAQ = [
    {"q": "What format is it?", "a": "An online guide you read on this site, on your phone, tablet or computer. You log in with your email, no password. Plus the worksheets and templates listed above."},
    {"q": "How do I get it after paying?", "a": "Right after checkout. You can come back any time via My guides by logging in with your email (no password)."},
    {"q": "Do I get updates?", "a": "Yes. When rules, fees or methods change, the guide is updated, and you see the new version right away. Free."},
    {"q": "Can I get a refund?", "a": "Yes. 30-day money-back guarantee. Read it, try the plan. If it's not worth it to you, message me within 30 days and you get all your money back. No questions."},
    {"q": "Is it only about Etsy?", "a": "No. Etsy gets a lot of detail because it's where most buyers of 3D printed items search. Chapter 5 compares Etsy, eBay, Facebook Marketplace, TikTok Shop, your own payment link, local shops and fairs, with real fees, and helps you pick the two that fit your product."},
    {"q": "Who handles payment and tax?", "a": "Payment is handled securely by Stripe, which also takes care of VAT and sales tax in your country."},
]
for g in PREM:
    k = g["product"]; p = PROD[k]; path = f"/guides/{g['slug']}"
    crs = COURSES.get(g["slug"])
    if crs:
        outline = "".join(f'<li><span>{i+1:02d}</span><a href="/guides/{g["slug"]}/{x["slug"]}" style="text-decoration:none;color:inherit"><b>{e(x["title"])}</b>{" <small class=\"freeto\">· Free to read</small>" if x.get("free") else ""}<br><small style="color:var(--muted)">{e(x["summary"])}</small></a></li>' for i, x in enumerate(crs["chapters"]))
    else:
        outline = "".join(f'<li><span>{i+1:02d}</span>{e(x)}</li>' for i, x in enumerate(g["outline"]))
    inc = "".join(f"<li>{inc_icon(x)}<span>{e(x)}</span></li>" for x in g["includes"])
    intro = markdown.markdown(g["body"], extensions=["attr_list", "md_in_html"])
    avail = "https://schema.org/InStock" if p.get("link") else "https://schema.org/PreOrder"
    ld = [crumbs_ld([("Home", "/"), ("Guides", "/guides"), (g["h1"], path)]), faq_ld(PREM_FAQ),
          {"@context": "https://schema.org", "@type": "Product", "name": g["h1"], "description": g["description"], "brand": {"@type": "Brand", "name": "boredprinter"}, "image": URL + "/og.png",
           "offers": {"@type": "Offer", "price": str(p["price"]), "priceCurrency": "USD", "availability": avail, "url": URL + path}}]
    soon = "" if p.get("link") else '<p class="note">Coming soon. Join the list and get it first, at the launch price.</p>'
    other = next((x for x in PREM if x["product"] != k), None)
    page = head(g["title"], g["description"], path, ld) + header("guides") + f"""
<main id="main">
<section class="phero"><div class="wrap">
{cover(k)}
<div>
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/guides">Guides</a> / <span>Premium</span></nav>
<h1 style="margin-top:18px;font-size:clamp(34px,5vw,54px)">{e(g['h1'])}</h1>
<p class="lead" style="margin-top:16px">{e(g['summary'])}</p>
<div class="buy"><div class="price">${p['price']} <span style="font:500 15px var(--body);color:var(--muted);letter-spacing:0">· Online guide · lifetime access</span></div>{f'<p class="launch">{launch_note(p)}</p>' if launch_note(p) else ''}{buy_btn(k)}{(f'<a class="btn ghost big wide" href="/guides/{g["slug"]}/{crs["chapters"][0]["slug"]}">Read chapter 1 free</a>') if crs else ''}{soon}{trust_row()}<p class="valline vbox">{ico('spool', 18)}<span>About the price of 1.5 spools of filament. Sell 3 of the example product and it has paid for itself.</span></p></div>
</div></div></section>
<section class="sec alt"><div class="wrap cols">
<div class="prose" style="font-size:17px">{intro}</div>
<div><h2 style="font-size:28px;margin-bottom:16px">What's inside</h2><ol class="list2">{outline}</ol></div>
</div></section>
<section class="sec"><div class="wrap cols">
<div><h2 style="font-size:28px;margin-bottom:16px">You get</h2><ul class="inc">{inc}<li>{ico('phone')}<span>Instant access on any device</span></li></ul>{trust_row()}</div>
<div><h2 style="font-size:28px;margin-bottom:16px">Questions</h2>{faq_html(PREM_FAQ)}</div>
</div></section>
<section class="sec"><div class="wrap">{signup('wait-' + k, title='Get it first', text='Join the list and you\'ll get an email the day it launches, at the launch price. Plus the free First Sale Checklist right away.', bullets=('Launch day email', 'Launch price', 'Free checklist now'), anchor='waitlist') if not p.get('link') else ''}
{INSIDE}
<div class="mini">{IGCHIP}<p>Written by Kevin. I research every rule, fee and step so you don't have to guess.</p></div>
<div style="margin-top:40px"><h2 style="font-size:28px;margin-bottom:16px">Also available</h2><div class="cards">{card(other) if other else ""}{card(FREE[0])}{card(FREE[1])}{CALC_CARD}</div></div>
</div></section>
</main>""" + footer()
    write(path, page); PAGES.append((path, str(g["updated"]), "0.9"))

# ---------- kalkylator ----------
CALC_FAQ = [
    {"q": "How do I calculate the cost of a 3D print?", "a": "Add the filament cost (spool price ÷ grams × grams used), electricity (watts × hours × price per kWh), machine wear per hour, your hands-on time, packaging and selling fees."},
    {"q": "What markup should I use for 3D prints?", "a": "Most sellers multiply their total cost by 2 to 3. Personalized or unique designs can go higher."},
    {"q": "How much electricity does a 3D printer use?", "a": "A typical home FDM printer averages roughly 100–150 W while printing. A heated chamber or a large bed can use more."},
]
calc_html = (ROOT / "site/calculator.html").read_text()
for lab, n in (("Material", "spool"), ("Printer", "printer"), ("Your time and packing", "clock"), ("Price and fees", "percent")):
    calc_html = calc_html.replace(f'<p style="margin:0 0 12px;font-weight:600">{lab}</p>', f'<p class="cgh">{ico(n, 18)}{lab}</p>')
path = "/tools/3d-print-price-calculator"
page = head("3D Print Price Calculator (Free): What to Charge for 3D Prints", "Free 3D printing price calculator: filament, electricity, machine wear, labour, packaging and Etsy-style fees. Get a selling price and profit per print.", path,
            [crumbs_ld([("Home", "/"), ("Tools", path), ("Price calculator", path)]), faq_ld(CALC_FAQ),
             {"@context": "https://schema.org", "@type": "WebApplication", "name": "3D Print Price Calculator", "applicationCategory": "BusinessApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "url": URL + path}]) + header("calc") + f"""
<main id="main" class="art"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <span>Price calculator</span></nav>
<div class="ahead"><h1>3D print price calculator</h1><p class="lead">Fill in your numbers and see what a print really costs you, and what to charge. Everything stays in your browser.</p></div>
{calc_html}
<div class="agrid" style="margin-top:56px"><div class="prose"><h2>How the calculator works</h2><p>It adds up every cost of one item: filament (with a buffer for failed prints), electricity, machine wear, your hands-on time and packaging. Then it applies your markup and adds marketplace fees on top, so the profit you see is what you actually keep.</p><p>Not sure about the numbers? Read <a href="/guides/how-to-price-3d-prints">how to price 3D prints</a> for a full walkthrough.</p><h2>Frequently asked questions</h2>{faq_html(CALC_FAQ)}</div></div>
<div style="margin-top:56px">{signup('calc', light=True, anchor='waitlist')}</div>
</div></main>""" + footer()
write(path, page); PAGES.append((path, TODAY, "0.9"))

# ---------- My guides ----------
lib_html = (ROOT / "site/library.html").read_text().replace('<label for="libEmail" style="font-weight:600">', f'<label for="libEmail" style="font-weight:600;display:flex;align-items:center;gap:8px">{ico("mail", 18)}')
page = head("My guides | boredprinter", "Read the boredprinter guides you have bought.", "/library", noindex=True) + header("lib") + f"""
<main id="main" class="art"><div class="wrap lib">
<div class="ahead"><h1 style="font-size:clamp(34px,5vw,48px)">Your guides</h1><p class="lead">Log in with the email you used at checkout. We'll email you a link, no password needed.</p></div>
{lib_html}
</div></main>""" + footer()
write("/library", page)

thanks_html = (ROOT / "site/thanks.html").read_text()
page = head("Thank you! | boredprinter", "Your guide is ready to download.", "/thanks", noindex=True) + header() + f"""
<main id="main" class="art"><div class="wrap lib">{thanks_html}</div></main>""" + footer()
write("/thanks", page)

# ---------- om / juridik / 404 ----------
def simple(path, title, desc, h1, body_md, noindex=False):
    page = head(title, desc, path, noindex=noindex) + header() + f"""
<main id="main" class="art"><div class="wrap"><div class="ahead"><h1 style="font-size:clamp(34px,5vw,50px)">{e(h1)}</h1></div><div class="prose">{icons_md(markdown.markdown(body_md, extensions=['tables', 'attr_list', 'md_in_html']))}</div></div></main>""" + footer()
    write(path, page)
    if not noindex: PAGES.append((path, TODAY, "0.4"))

for name in ("about", "privacy", "terms"):
    m = load(ROOT / f"content/pages/{name}.md")
    simple("/" + name, m["title"], m["description"], m["h1"], m["body"])

page = head("Page not found | boredprinter", "This page doesn't exist.", "/404", noindex=True) + header() + f"""
<main id="main" class="art"><div class="wrap"><div class="ahead"><h1>This page doesn't exist</h1><p class="lead">It may have moved. Try one of these instead.</p></div><div class="cards">{"".join(card(g) for g in FREE[:3])}{CALC_CARD}</div></div></main>""" + footer()
(OUT / "404.html").write_text(page)

# ---------- sitemap / robots / llms ----------
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{URL}{p if p != '/' else '/'}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>\n" for p, d, pr in PAGES) + "</urlset>\n"
(OUT / "sitemap.xml").write_text(sm)
(OUT / "robots.txt").write_text(f"""User-agent: *
Allow: /
Disallow: /api/
Disallow: /library
Disallow: /thanks

Sitemap: {URL}/sitemap.xml
""")
llms = f"""# boredprinter

> boredprinter ({URL}) publishes honest, practical guides on making money with a home 3D printer, by the creator behind @boredprinter on Instagram ({SITE['followers']} followers). Free guides cover what sells, licenses, Etsy's 2025+ rules for 3D prints and pricing, plus a free price calculator. Premium online guides go deeper.

## Free guides
""" + "".join(f"- [{g['h1']}]({URL}/guides/{g['slug']}): {g['summary']}\n" for g in FREE) + f"""- [3D print price calculator]({URL}/tools/3d-print-price-calculator): free tool to price a 3D print including filament, electricity, machine wear, labour, packaging and fees.

## Premium guides
""" + "".join(f"- [{g['h1']}]({URL}/guides/{g['slug']}): {g['summary']} (${PROD[g['product']]['price']}, online guide)\n" for g in PREM)
(OUT / "llms.txt").write_text(llms)
# säkerhet: om både x.html och mappen x/ finns, lägg en kopia som x/index.html
for f in list(OUT.rglob("*.html")):
    d = f.with_suffix("")
    if d.is_dir() and f.name != "index.html": (d / "index.html").write_text(f.read_text())
print("built", len(PAGES), "indexed pages")
