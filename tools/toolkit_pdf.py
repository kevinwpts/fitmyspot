"""Bygger PDF:erna i verktygslådan med Playwright. Kör: python3 tools/toolkit_pdf.py"""
import re, html
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "private/files"
CSS = """
@page{size:A4;margin:16mm 16mm 18mm}
*{box-sizing:border-box}body{font:10.5pt/1.45 "Helvetica Neue",Arial,sans-serif;color:#16161A;margin:0}
h1{font-size:24pt;margin:0 0 4pt;letter-spacing:-.01em}h2{font-size:14pt;margin:18pt 0 6pt;break-after:avoid}
h3{font-size:11pt;margin:10pt 0 4pt;break-after:avoid}
.sub{color:#5E6169;margin:0 0 12pt}.brand{color:#FF5B1F;font-weight:700}
.box{border:1.2pt solid #16161A;border-radius:8pt;padding:9pt 11pt;margin:6pt 0 10pt;break-inside:avoid}
.ex{background:#FFF1EA;border-color:#FFD3BF}
.line{border-bottom:1pt solid #B9BAC2;height:18pt}
table{width:100%;border-collapse:collapse;margin:4pt 0 10pt;break-inside:auto}
th,td{text-align:left;padding:5pt 6pt;border-bottom:.8pt solid #E2E2E6;vertical-align:top}
th{background:#16161A;color:#fff;font-weight:600}
tr{break-inside:avoid}
.ck{width:16pt}.ck span{display:inline-block;width:10pt;height:10pt;border:1.2pt solid #16161A;border-radius:2pt}
.n{width:42pt;white-space:nowrap;color:#5E6169}.ch{width:52pt;color:#5E6169}
.tags td{height:20pt}.small{font-size:9pt;color:#5E6169}
.pb{break-before:page}
ul{margin:4pt 0 8pt 14pt;padding:0}li{margin:2pt 0}
"""
def pdf(name, body):
    doc = f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}</body></html>"
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); pg.set_content(doc)
        pg.pdf(path=str(OUT / name), format="A4", print_background=True,
               display_header_footer=True, header_template="<span></span>",
               footer_template='<div style="font:8pt Arial;color:#888;width:100%;text-align:center">boredprinter.com · Print to Profit · page <span class="pageNumber"></span>/<span class="totalPages"></span></div>')
        b.close()
    print(OUT / name)

# 30-dagarschecklista ur kapitlet
md = (ROOT / "content/course/print-to-profit/your-30-day-plan.md").read_text()
weeks = re.findall(r"^## (Week \d+: \w+)\n(.*?)(?=^## )", md, flags=re.M | re.S)
b = ['<h1>Your 30-day checklist</h1><p class="sub">Print to Profit · <span class="brand">boredprinter</span> · 30–60 minutes a day. Tick a box when it\'s done. Missed a day? Just continue tomorrow.</p>',
     '<div class="box"><b>My product:</b><div class="line"></div><b>For whom:</b><div class="line"></div><b>Start date:</b><div class="line" style="width:40%"></div></div>']
for title, body in weeks:
    rows = re.findall(r"^\| (\d+) \| (.*?) \| (.*?) \|$", body, flags=re.M)
    t = "".join(f'<tr><td class="ck"><span></span></td><td class="n">Day {d}</td><td>{re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(task))}</td><td class="ch">{("Ch. " + ch) if ch.strip() else ""}</td></tr>' for d, task, ch in rows)
    b.append(f'<h2>{title}</h2><table><tr><th></th><th>Day</th><th>Task</th><th>Chapter</th></tr>{t}</table>')
b.append('<h2>Day-30 review</h2>' + "".join(f'<h3>{q}</h3><div class="line"></div>' for q in [
    "Which product got the most interest?", "Which channel brought the most buyers?", "What took the most time?",
    "What would I do differently?", "My goal for the next 30 days:"]))
pdf("30-day-checklist.pdf", "".join(b))

# Listing-mallar + skript
L = []
L.append('<h1>Listing templates &amp; scripts</h1><p class="sub">Print to Profit · <span class="brand">boredprinter</span> · Fill in the blanks, copy, paste. The example is the Switch game card holder from the guide.</p>')
L.append('''<h2>1. Search phrases (10–15)</h2><p>Type your product into Etsy, eBay or Google and stop. Write down the suggestions.</p>
<table class="tags">''' + "".join(f"<tr><td style='width:50%'>{i}.</td><td>{i+8}.</td></tr>" for i in range(1, 9)) + '</table>')
L.append('''<h2>2. Title</h2><div class="box"><b>[What it is] for [what it fits / who it's for], [key feature], [option]</b><br><span class="small">Most important words first. Under about 15 words. No "perfect", "beautiful" or "best gift" in the title.</span><div class="line"></div><div class="line"></div></div>
<div class="box ex"><b>Example:</b> Switch Game Card Holder, 12 Slot Desk Stand, Personalized Cartridge Organizer</div>''')
L.append('<h2>3. The 13 tags</h2><p class="small">Up to 20 characters each. Phrases, not single words. Spread: 4 what it is · 3 what it fits / who for · 2 where it\'s used · 2 style or material · 2 occasions (only if real).</p><table class="tags"><tr><th>#</th><th>Tag</th><th>Characters</th><th>Example</th></tr>' +
         "".join(f"<tr><td class='n'>{i}</td><td></td><td style='width:60pt'></td><td class='small'>{x}</td></tr>" for i, x in enumerate(
             ["switch game holder", "game card holder", "cartridge holder", "switch card case", "game card storage", "switch organizer", "gamer desk decor",
              "personalized gamer", "gift for gamer", "game room decor", "cartridge stand", "switch accessories", "desk organizer"], 1)) + "</table>")
L.append('''<h2 class="pb">4. Description</h2><p class="small">Most buyers only read the first lines. Answers first, specs after.</p>
<div class="box"><b>[One line: what it does for them.]</b><div class="line"></div>
<b>What you get:</b> [item, size in cm and inches, color]<div class="line"></div>
<b>Fits:</b> [exact models / sizes]<div class="line"></div>
<b>Made by me:</b> Designed and 3D printed by me in [city], in [material].<div class="line"></div>
<b>Personalization:</b> [how to add a name / options]<div class="line"></div>
<b>Shipping:</b> Ships in [X] days with [carrier], with tracking.<div class="line"></div>
<b>Care:</b> [e.g. keep away from heat, like a hot car]<div class="line"></div></div>
<div class="box ex"><b>Keeps 12 Switch game cards upright, sorted and easy to grab. The slots are tight: turn it upside down and the cards stay in.</b><br>
<b>What you get:</b> 1 holder, 11 × 3 × 1.8 cm (4.3 × 1.2 × 0.7 in), in the color you choose.<br>
<b>Fits:</b> Switch game cards. 12 slots.<br><b>Made by me:</b> Designed and 3D printed by me in [city], in PLA.<br>
<b>Personalization:</b> Add a name of up to 10 letters on the front, in a second color.<br>
<b>Shipping:</b> Ships in 1–3 days with tracking.<br><b>Care:</b> Keep away from heat, like a hot car.</div>''')
L.append('''<h2>5. FAQ (end of the description)</h2>
<div class="box"><b>Will it fit my [thing]?</b> → exact measurements<div class="line"></div><b>Is it sturdy?</b> → material, wall thickness, what it can hold<div class="line"></div>
<b>Can I choose the color?</b> → yes/no and options<div class="line"></div><b>How long until it arrives?</b> → making time + shipping<div class="line"></div></div>''')
L.append('''<h2>6. Personalization box</h2><div class="box">"[What to write] (max [X] letters). Leave empty for no [name/text]."</div>
<div class="box ex">"Name for the front (max 10 letters). Leave empty for no name."</div>''')
L.append('''<h2>7. Copy-paste scripts</h2>
<h3>Local group post</h3><div class="box">I design and 3D print these [product] myself here in [town]. They [what it does]. $[price], pick-up or shipping. I can also make it in your color or with a name. Comment or send me a message!</div>
<h3>Message to a local shop or café</h3><div class="box">Hi! I'm [name], I design and 3D print [product] locally. I made a few samples that I think would fit your shop/your customers. Could I drop by with them for 5 minutes this week? If they sell, great. If not, no hard feelings.</div>
<p class="small">Bring 3 samples and a simple price sheet. Offer them 30–40% of the price, or a wholesale price of about half your retail price.</p>
<h3>Reddit / community post (no spam)</h3><div class="box">I got tired of [problem], so I designed this [product] for [specific thing]. Took [X] versions to get the fit right. Happy to answer questions about the design!</div>
<p class="small">Read the rules first. Only add a link where allowed, or when someone asks.</p>
<h3>Review request (after delivery)</h3><div class="box">Hi [name]! Your [product] should have arrived. I hope it fits perfectly. If you have a minute, a review would really help my small shop. And if anything isn't right, just reply here and I'll fix it.</div>
<h3>Proof before printing a personalized order</h3><div class="box">Hi [name], thanks for your order! Here's how your [product] will look with "[text]". Is the spelling right? Reply "yes" and I'll start printing today.</div>
<h3>Thank-you card</h3><div class="box">Thanks for your order, [name]! Made by hand in [city]. Tag @[yourshop] when it's in use. I'd love to see it.</div>''')
L.append('''<h2>8. Video hooks (first second)</h2><ul>
<li>"I was tired of [problem]…" → show the problem first, then the product.</li>
<li>"This took [X] hours to print" → timelapse of the print growing.</li>
<li>"It fits perfectly" → the satisfying click when it slides in.</li>
<li>"Making one for my [person]…" → a personal story.</li>
<li>"Version 1 vs version [X]" → shows your design process.</li></ul>''')
L.append('''<h2>9. Photo shot list</h2><table><tr><th></th><th>Photo</th><th>Example</th></tr>''' + "".join(
    f"<tr><td class='ck'><span></span></td><td><b>{a}</b></td><td class='small'>{c}</td></tr>" for a, c in [
        ("Hero", "Holder full of cards on a clean desk, window light from the side"),
        ("In use", "A hand pulling one card out"),
        ("Proof", "Held upside down, cards still in"),
        ("Size", "Next to the console or a hand"),
        ("Personal / options", "Close-up of the name, plus color options")]) + "</table>")
pdf("listing-templates.pdf", "".join(L))
