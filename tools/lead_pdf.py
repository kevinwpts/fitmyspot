"""Gratis-PDF: The 7-Day First Sale Plan. Kör: python3 tools/lead_pdf.py"""
import re, base64
from pathlib import Path
from playwright.sync_api import sync_playwright
R = Path(__file__).resolve().parent.parent
OUT = R / "public/free/7-day-first-sale-plan.pdf"
def svg(n): return (R / f"site/ill/{n}.svg").read_text()
cover = base64.b64encode((R / "public/img/book-playbook.webp").read_bytes()).decode()
CSS = """@page{size:148mm 210mm;margin:10mm 11mm 12mm}
*{box-sizing:border-box}body{font:9.6pt/1.42 'Helvetica Neue',Arial,sans-serif;color:#16161A;margin:0}
h1{font-size:30pt;line-height:1.02;margin:0;letter-spacing:-.02em}h2{font-size:17pt;line-height:1.1;margin:0 0 6pt;letter-spacing:-.01em}
h3{font-size:10.8pt;margin:8pt 0 3pt}p{margin:0 0 7pt}.o{color:#FF5B1F}.m{color:#5E6169}
.pb{break-before:page}.day{display:inline-block;background:#FF5B1F;color:#fff;font-weight:700;font-size:9pt;padding:3pt 9pt;border-radius:20pt;margin-bottom:8pt;letter-spacing:.04em}
.box{border:1.2pt solid #E2E0DA;border-radius:9pt;padding:7pt 10pt;margin:6pt 0;break-inside:avoid;background:#fff}
.ex{background:#FFF1EA;border-color:#FFD3BF}.dk{background:#16161A;color:#fff;border-color:#16161A}.dk b{color:#7BE0A6}
ul,ol{margin:3pt 0 8pt 14pt;padding:0}li{margin:2.5pt 0}
.task{border:1.5pt solid #16161A;border-radius:9pt;padding:6pt 10pt;margin-top:8pt;break-inside:avoid}.task b{display:block;font-size:9pt;letter-spacing:.06em;color:#FF5B1F;margin-bottom:4pt}
.task li{list-style:none;margin-left:-14pt}.task li::before{content:"☐  ";font-size:12pt}
.more{break-inside:avoid;font-size:9pt;color:#5E6169;border-top:1pt solid #E2E0DA;padding-top:5pt;margin-top:7pt}.more b{color:#16161A}
svg{width:100%;height:auto;max-height:52mm;display:block;margin:4pt 0;border-radius:8pt}
table{width:100%;border-collapse:collapse;font-size:9.5pt;margin:4pt 0 8pt}td,th{padding:3pt 5pt;border-bottom:.8pt solid #E2E0DA;text-align:left}th{font-size:8.5pt;color:#5E6169}
.cov{height:184mm;display:flex;flex-direction:column;background:#16161A;color:#fff;border-radius:12pt;padding:16mm 12mm;margin:-1mm}
.tag{font-family:Courier,monospace;background:#F4F2EE;padding:1pt 4pt;border-radius:3pt;font-size:9.5pt}
"""
P = []
P.append(f"""<div class="cov"><p style="font-weight:700;letter-spacing:.08em;font-size:9pt;color:#FF8A57">FREE · BOREDPRINTER</p>
<h1 style="color:#fff;font-size:36pt;margin-top:8mm">The 7-Day<br><span class="o">First Sale</span><br>Plan</h1>
<p style="font-size:13pt;color:#C9C6BF;margin-top:8mm">From "I have a 3D printer" to "someone paid me". One step a day, about 45 minutes each.</p>
<div style="margin-top:auto;font-size:10pt;color:#C9C6BF">Day 1 · Pick who you sell to<br>Day 2 · Prove people buy it<br>Day 3 · Check you're allowed to sell it<br>Day 4 · Set a price that pays<br>Day 5 · Take photos that sell<br>Day 6 · Write a listing that gets found<br>Day 7 · Get your first buyer</div></div>""")
P.append("""<div class="pb"><h2>Before you start</h2>
<p>Most people who buy a 3D printer to make money quit within a few weeks. Not because it doesn't work, but because they <b>guess</b>: what to make, what to charge, where to sell.</p>
<p>This plan replaces guessing with 7 small steps. Do one a day. Don't skip ahead, don't "perfect" anything.</p>
<div class="box ex"><b>Be realistic.</b> A first sale in 7 days is possible but not guaranteed. What you <i>will</i> have after 7 days: a product people want, a fair price, good photos and a live listing. That's what every seller who makes money has.</div>
<h3>What you need</h3><ul><li>Your printer and some filament</li><li>Your phone (for photos)</li><li>45 minutes a day</li><li>A free account where you'll sell (Etsy is the easiest start)</li></ul>
<div class="box"><b>How to use this:</b> read the day, do the task box at the bottom, tick it. Each day also tells you where the full guide goes deeper, in case you get stuck.</div></div>""")
P.append("""<div class="pb"><span class="day">DAY 1</span><h2>Pick one buyer, not "everyone"</h2>
<p>Sellers who try a bit of everything (a keychain here, a random model there) rarely get traction. Sellers who pick <b>one type of buyer</b> become "the shop with the great board game inserts", and buyers remember them.</p>
<h3>Good buyer groups for 3D prints</h3>
<table><tr><th>Buyer</th><th>What they buy</th></tr><tr><td>Board gamers</td><td>Inserts, organizers, token trays</td></tr><tr><td>Pet owners</td><td>Name tags, feeder stands, toy holders</td></tr><tr><td>People in small flats</td><td>Wall hooks, drawer organizers, cable clips</td></tr><tr><td>Gamers</td><td>Controller stands, game card holders</td></tr><tr><td>Plant lovers</td><td>Pots, self-watering inserts, labels</td></tr></table>
<div class="box ex"><b>The rule:</b> pick a group you <b>belong to</b> or know well. You'll spot problems others miss, and you'll know where they hang out online.</div>
<div class="task"><b>YOUR TASK TODAY</b><ul><li>Pick one buyer group</li><li>Write one sentence: "I make ___ for ___."</li><li>Write down 3 places they hang out online (subreddits, groups, hashtags)</li></ul></div>
<p class="more"><b>Print to Profit, chapter 1</b>: the 7 ways to make money with a printer and a quiz to pick the one that fits you.</p></div>""")
P.append(f"""<div class="pb"><span class="day">DAY 2</span><h2>Prove people already buy it</h2>
<p>The fastest way to fail is to print something nobody searches for. Check demand in 20 minutes, <b>before</b> you design anything.</p>
<h3>1. Etsy autocomplete</h3><p>Type the first word of your idea on Etsy and stop. Every suggestion is a real search people make.</p>
<h3>2. The review trick most sellers don't know</h3><p>Only about <b>3–8% of buyers leave a review</b>. So a listing with 40 reviews has probably sold <b>600–1,200 times</b>. Find 3 listings for your idea with 30+ reviews and you know there's demand.</p>
<h3>3. Read the 2–3 star reviews on Amazon</h3><p>Search the mass-market version. The complaints are your product ideas: "too shallow", "doesn't fit my X", "falls over".</p>
<div class="box ex"><b>The +1 rule:</b> take something that already sells and add one thing: a size for a specific brand, a lid, a name, a set of 3. That difference is your marketing.</div>
<div class="task"><b>YOUR TASK TODAY</b><ul><li>Find 3 listings with 30+ reviews for your idea</li><li>Write down 3 complaints from bad reviews</li><li>Decide your "+1"</li></ul></div>
<p class="more"><b>Print to Profit, chapters 2–3</b>: a 20-minute research routine, an idea scoring sheet, and how to design your own version in Tinkercad (free), step by step.</p></div>""")
P.append(f"""<div class="pb"><span class="day">DAY 3</span><h2>Check you're allowed to sell it</h2>
<p>This is where many new sellers lose their shop. Run every product through this in 30 seconds:</p>{svg('license')}
<ul><li><b>Etsy:</b> since 2025, physical items must be made from <b>your own design</b>. Downloaded files can get your listing removed, even with a commercial license.</li>
<li><b>Fonts count too.</b> Many "free" fonts are personal use only. Google Fonts are fine to sell with.</li>
<li><b>No logos, characters or brand names</b> on the product. "Fits Nintendo Switch cards" describes what it works with. A Mario on it doesn't.</li></ul>
<div class="task"><b>YOUR TASK TODAY</b><ul><li>Run your product through the check</li><li>If it's not your design: make your own simple version</li></ul></div>
<p class="more"><b>Print to Profit, chapter 4</b>: licenses, trademarks, EU product safety rules (GPSR) and the tax basics, in plain English.</p></div>""")
P.append(f"""<div class="pb"><span class="day">DAY 4</span><h2>Set a price that actually pays</h2>
<p>The #1 mistake: pricing by the filament. A "$1 print" sold for $5 feels like profit. After your time, packing and fees, you worked for free.</p>
<div class="box"><b>Price = (filament + power + machine + your time + packaging) × 2.5 + fees</b></div>
<table><tr><th>Example: 60 g print</th><th>Cost</th></tr><tr><td>Filament ($20 spool, +10% waste)</td><td>$1.32</td></tr><tr><td>Power + machine wear (3 h)</td><td>$0.84</td></tr><tr><td>Your time (15 min at $20/h)</td><td>$5.00</td></tr><tr><td>Packaging</td><td>$1.00</td></tr><tr><td><b>Real cost</b></td><td><b>$8.16</b></td></tr><tr><td><b>× 2.5 + Etsy fees</b></td><td><b class="o">≈ $23</b></td></tr></table>
<div class="box ex"><b>Two moves that raise every order:</b> sell a <b>set of 4</b> next to the single (most buyers pick the middle), and on Etsy US keep shipping <b>under $6</b>: Etsy ranks those listings higher. Put the rest of the postage in the price.</div>
<div class="task"><b>YOUR TASK TODAY</b><ul><li>Weigh your print in the slicer, time your hands-on work</li><li>Put it in the free calculator: boredprinter.com/tools/3d-print-price-calculator</li><li>Set your price. If it feels high, that's normal</li></ul></div>
<p class="more"><b>Print to Profit, chapter 6</b> + the toolkit spreadsheet: prices for 20 products at once, shipping and monthly profit.</p></div>""")
P.append(f"""<div class="pb"><span class="day">DAY 5</span><h2>Take photos that sell</h2>
<p>On a marketplace your photo <b>is</b> the product. You don't need a camera or a lightbox, just a window.</p>{svg('studio')}
<h3>The 5 photos, in this order</h3><ol><li><b>Hero:</b> the product alone, plain background, window light</li><li><b>In use:</b> doing its job</li><li><b>Size:</b> next to a hand or a known object</li><li><b>Detail:</b> the clever bit, close up</li><li><b>Variations:</b> colors or sizes</li></ol>
<div class="box ex"><b>Turn off the ceiling light.</b> Mixed light makes prints look yellow and cheap. Daylight from the side only.</div>
<div class="task"><b>YOUR TASK TODAY</b><ul><li>Set up by a window with white paper</li><li>Take the 5 photos</li><li>Pick the sharpest one as your hero</li></ul></div>
<p class="more"><b>Print to Profit, chapter 7</b>: before/after examples, a 10-minute studio, editing on your phone step by step, and a short video that sells.</p></div>""")
P.append("""<div class="pb"><span class="day">DAY 6</span><h2>Write a listing that gets found</h2>
<h3>Title (Etsy's 2026 rules)</h3><p>Under about <b>15 words</b>. What it is first. No "perfect gift", no "beautiful". Example:</p>
<div class="box">Switch Game Card Holder, 12 Slot Desk Stand, Personalized Cartridge Organizer</div>
<h3>The 13 tags</h3><p>Use all 13, each up to 20 characters, phrases not single words:</p>
<p><span class="tag">switch game holder</span> <span class="tag">game card holder</span> <span class="tag">cartridge holder</span> <span class="tag">switch card case</span> <span class="tag">gamer desk decor</span> <span class="tag">personalized gamer</span> …</p>
<h3>Description: answer first</h3><p>Line 1: what it does for them. Then size, what it fits, material, how to personalize, shipping time. End with a short FAQ.</p>
<div class="box ex"><b>Little-known:</b> fill in Etsy's <b>shop policies with Etsy's own template</b> and every listing <b>attribute</b> (color, material, room). Etsy uses them in search and filters.</div>
<div class="task"><b>YOUR TASK TODAY</b><ul><li>Write your title</li><li>Write 13 tags</li><li>Write the first 2 lines of your description</li><li>Publish (on Etsy it costs $0.20)</li></ul></div>
<p class="more"><b>Print to Profit, chapter 8</b>: open your shop click by click, every listing field explained, and copy-paste templates.</p></div>""")
P.append("""<div class="pb"><span class="day">DAY 7</span><h2>Get your first buyer</h2>
<p>A new listing gets almost no views at first. Your first buyers come from <b>you</b>, not from search. Do these 3 today:</p>
<h3>1. Your own network</h3><div class="box">"I've started making [product] for [who]. First 5 get 20% off. Want one?" Send to 5 people who fit, not to everyone.</div>
<h3>2. One local group</h3><div class="box">"I design and 3D print [product] here in [town]. [What it does]. $[price], pick-up or shipping. I can also make it in your color or with a name!"</div>
<h3>3. Where your buyers hang out</h3><p>Post a photo of the making-of in a hobby group or subreddit. Share, don't sell: "I got tired of [problem], so I designed this." Read the rules first. Link only if asked.</p>
<div class="task"><b>YOUR TASK TODAY</b><ul><li>Message 5 people</li><li>Post in 1 local group</li><li>Share in 1 hobby community</li></ul></div>
<p class="more"><b>Print to Profit, chapter 10</b>: a 14-day sales sprint, video scripts, scripts for local shops, and how to get your first reviews.</p></div>""")
P.append(f"""<div class="pb"><h2>You've done the 7 days. Now what?</h2>
<p>If you followed along, you now have something most people with a printer never get: <b>a real product, a fair price and a live listing.</b></p>
<p>The next part is what turns one sale into a side income: better products, more channels, batch printing and a plan for the next 30 days.</p>
<div class="box dk" style="display:flex;gap:10pt;align-items:center"><img src="data:image/webp;base64,{cover}" style="width:30mm;border-radius:3pt"><div><p style="font-size:13pt;font-weight:700;margin:0 0 4pt">Print to Profit</p><p style="color:#C9C6BF;margin:0 0 6pt;font-size:9.5pt">12 chapters · spreadsheet toolkit · listing templates · one example product followed all the way · a 30-day plan</p><p style="margin:0"><b>$10 off with code BORED10</b></p></div></div>
<ul><li>Design your own product in Tinkercad, step by step</li><li>Where to sell: Etsy, eBay, Facebook, TikTok Shop, local, with real fees</li><li>Open your Etsy shop and fill every field, click by click</li><li>Ship cheap, get reviews, batch print, scale up</li><li>30-day money-back guarantee</li></ul>
<p style="font-size:13pt;font-weight:700;margin-top:10pt">boredprinter.com/guides/print-to-profit</p>
<p class="m" style="margin-top:12pt;font-size:9pt">Questions? DM me on Instagram: @boredprinter. Not legal or tax advice. Rules and fees change, always check the source.</p></div>""")
html = f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{''.join(P)}</body></html>"
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.set_content(html); pg.wait_for_timeout(300)
    pg.pdf(path=str(OUT), width="148mm", height="210mm", print_background=True, display_header_footer=True, header_template="<span></span>",
           footer_template='<div style="font:7pt Arial;color:#999;width:100%;text-align:center">boredprinter.com · <span class="pageNumber"></span></div>')
    b.close()
print(OUT)
