# Bygger SEO-sidorna /ideas/*.html. Kör: python3 tools/build_ideas.py
# Texten finns i HTML (för Google och AI). Bilder på riktiga modeller laddas i webbläsaren.
import html, json, os

SITE = "https://fitmyspot.com"
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "ideas")

ROOMS = {
 "car": ("car", "Car", "Cup holders, vents, door pockets and seat gaps are full of small problems a 3D print can fix. Use PETG or ASA, since PLA can warp in a hot car.", [
  ("Cup holder organizer", "Turns an empty cup holder into a tray for keys, coins and cards.", "car cup holder organizer", "PETG"),
  ("Vent phone mount", "Keeps your phone in view for maps instead of sliding on the seat.", "car vent phone mount", "PETG"),
  ("Seat gap filler", "Stops phones and keys from falling between the seat and console.", "car seat gap filler", "TPU"),
  ("Sunglasses clip for the visor", "Keeps sunglasses safe and easy to grab.", "sunglasses visor clip", "PETG"),
  ("Trash bin for the door pocket", "A small bin that fits the door pocket, so wrappers stay in one place.", "car door trash bin", "PETG"),
  ("Cable clips for the dashboard", "Keeps the charging cable from falling into the footwell.", "car cable clip", "PETG"),
  ("Hook for the headrest", "Holds bags so groceries don't roll around.", "car headrest hook", "PETG"),
  ("Parking ticket holder", "Holds the ticket or a parking disc on the windshield.", "parking ticket holder car", "PETG"),
 ]),
 "desk": ("desk", "Desk", "Cables, headphones and small stuff make a desk messy fast. These prints clear space and keep things where you need them.", [
  ("Headphone stand", "Gets headphones off the desk and keeps the band in shape.", "headphone stand", "PLA"),
  ("Under-desk cable tray", "Hides power strips and cables under the desk.", "under desk cable tray", "PETG"),
  ("Cable clips", "Keeps charging cables on the edge of the desk, ready to use.", "desk cable clip", "PLA"),
  ("Monitor riser", "Lifts the screen to eye level and adds storage below.", "monitor stand riser", "PLA"),
  ("Pen and tool holder", "One place for pens, scissors and a ruler.", "desk organizer pen holder", "PLA"),
  ("Controller stand", "Holds game controllers neatly next to the screen.", "controller stand", "PLA"),
  ("Laptop stand", "Raises the laptop for better posture and airflow.", "laptop stand", "PETG"),
  ("SD card and USB holder", "Stops small cards and sticks from getting lost.", "sd card holder", "PLA"),
 ]),
 "kitchen": ("kitchen", "Kitchen", "Drawers, cabinet doors and counters are where most kitchens lose space. These prints use the space you already have.", [
  ("Drawer organizer (Gridfinity)", "Modular bins that fit any drawer and keep tools sorted.", "gridfinity bin", "PLA"),
  ("Spice rack", "Fits spice jars on a shelf or inside a cabinet door.", "spice rack", "PLA"),
  ("Bag clips", "Keeps open bags of chips, coffee and pasta fresh.", "bag clip", "PLA"),
  ("Under-shelf hooks for mugs", "Hangs mugs under a shelf and frees cabinet space.", "under shelf mug hook", "PETG"),
  ("Cutting board stand", "Stores cutting boards upright so they dry.", "cutting board holder", "PETG"),
  ("Sponge holder", "Keeps the sponge off the sink so it dries faster.", "sponge holder", "PETG"),
  ("Lid organizer", "Holds pot lids upright in a drawer or cabinet.", "pot lid organizer", "PETG"),
  ("Cable holder for appliances", "Wraps the cord of a toaster or kettle neatly.", "appliance cord wrap", "PETG"),
 ]),
 "bathroom": ("bathroom", "Bathroom", "Bathrooms are small and wet, so storage matters. Print in PETG, which handles water and heat better than PLA.", [
  ("Toothbrush holder", "Keeps toothbrushes apart and off the sink.", "toothbrush holder", "PETG"),
  ("Razor wall mount", "Holds the razor on the wall so it dries.", "razor holder", "PETG"),
  ("Shower shelf", "A small shelf for shampoo bottles in the shower.", "shower shelf", "PETG"),
  ("Hair dryer holder", "Hangs the hair dryer on the wall or cabinet door.", "hair dryer holder", "PETG"),
  ("Toilet paper shelf", "A spare roll holder and a spot for your phone.", "toilet paper holder shelf", "PETG"),
  ("Soap dish with drain", "Lets the soap dry so it lasts longer.", "soap dish", "PETG"),
  ("Cable holder for the trimmer", "Keeps the charging cord from tangling.", "cable organizer", "PETG"),
  ("Towel hook", "Adds a hook where there was none, without drilling.", "adhesive towel hook", "PETG"),
 ]),
 "bedroom": ("bedroom", "Bedroom", "The nightstand and the space around the bed collect cables, glasses and phones. These prints keep it calm and tidy.", [
  ("Bedside phone holder", "Holds your phone and charger at the edge of the bed.", "bedside phone holder", "PETG"),
  ("Cable clips for the nightstand", "Stops the charging cable from falling behind the bed.", "cable clip nightstand", "PLA"),
  ("Glasses stand", "A safe spot for glasses at night.", "glasses stand", "PLA"),
  ("Headphone hook under the table", "Keeps headphones off the nightstand.", "under desk headphone hook", "PLA"),
  ("Jewelry tray", "One place for rings, watches and earrings.", "jewelry tray", "PLA"),
  ("Hangers for belts and ties", "Organizes belts in the wardrobe.", "belt hanger", "PETG"),
  ("Remote holder", "Keeps the TV remote in one place.", "remote holder", "PLA"),
  ("Book stand", "Holds a book open while you read in bed.", "book holder", "PLA"),
 ]),
 "garage": ("garage", "Garage", "Garages are full of tools, cables and small parts. Wall mounts and bins clear the floor and the bench.", [
  ("Tool wall holders", "Hangs screwdrivers, pliers and wrenches on the wall.", "tool holder wall", "PETG"),
  ("Battery holder for power tools", "Mounts tool batteries on the wall, ready to grab.", "battery holder power tool", "PETG"),
  ("Screw and bit organizer", "Sorts screws and drill bits in small bins.", "drill bit organizer", "PLA"),
  ("Extension cord hanger", "Keeps long cords from tangling.", "extension cord holder", "PETG"),
  ("Pegboard hooks", "Custom hooks for any pegboard.", "pegboard hook", "PETG"),
  ("Hose holder", "Coils the garden hose on the wall.", "hose holder", "PETG"),
  ("Bike wall mount", "Gets the bike off the floor.", "bike wall mount", "PETG"),
  ("Spray can holder", "Holds spray cans upright on a shelf.", "spray can holder", "PETG"),
 ]),
 "living-room": ("living room", "Living room", "The sofa, TV and coffee table are where remotes, controllers and cables pile up. These prints give everything a place.", [
  ("Sofa armrest tray", "A flat spot for drinks and snacks on the armrest.", "sofa armrest tray", "PLA"),
  ("Remote holder", "Keeps remotes together instead of lost in the sofa.", "remote control holder", "PLA"),
  ("TV cable cover", "Hides cables running down from the TV.", "cable cover", "PLA"),
  ("Controller wall mount", "Stores game controllers neatly.", "controller wall mount", "PLA"),
  ("Coasters", "Protects the table from cups.", "coaster", "PETG"),
  ("Plant pot", "A self-watering pot for a small plant.", "self watering planter", "PETG"),
  ("Router and modem stand", "Keeps the router upright and cool.", "router stand", "PETG"),
  ("Picture ledge", "Shows photos without drilling many holes.", "picture ledge shelf", "PLA"),
 ]),
 "hallway": ("hallway", "Hallway", "The hallway is where keys, bags and shoes get dropped. A few small prints make leaving the house faster.", [
  ("Wall key holder", "Hooks for keys by the door, so you never search for them.", "wall key holder", "PLA"),
  ("Mail organizer", "A slot for letters and bills on the wall.", "wall mail organizer", "PLA"),
  ("Shoe rack spacers", "Fits more shoes on the rack.", "shoe stacker", "PETG"),
  ("Umbrella holder", "Holds umbrellas so they drip in one place.", "umbrella holder", "PETG"),
  ("Dog leash hook", "Keeps the leash and treat bag by the door.", "leash holder", "PETG"),
  ("Coat hooks", "Extra hooks for jackets and bags.", "coat hook", "PETG"),
  ("Sunglasses holder", "A place for sunglasses by the door.", "sunglasses holder wall", "PLA"),
  ("Door stop", "Stops the door from hitting the wall.", "door stopper", "TPU"),
 ]),
}

def page(slug, room, title, intro, ideas):
    e = html.escape
    url = f"{SITE}/ideas/{slug}"
    others = " · ".join(f'<a href="/ideas/{s}">{e(v[1])}</a>' for s, v in ROOMS.items() if s != slug)
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "ItemList", "name": f"3D print ideas for your {room}", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "description": w} for i, (n, w, q, m) in enumerate(ideas)]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "fitmyspot", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Print ideas", "item": SITE + "/ideas"},
            {"@type": "ListItem", "position": 3, "name": title, "item": url}]}]}
    items = "\n".join(f'''      <li class="it"><a class="pic" data-q="{e(q)}" href="https://www.printables.com/search/models?q={e(q.replace(' ', '+'))}" target="_blank" rel="noopener"></a>
        <div><h2>{i + 1}. {e(n)}</h2><p>{e(w)}</p><small>Material: {e(m)}</small></div></li>''' for i, (n, w, q, m) in enumerate(ideas))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>3D print ideas for your {e(room)} – fitmyspot</title>
<meta name="description" content="{len(ideas)} useful 3D prints for your {e(room)}, with real models to download. Or snap a photo of your {e(room)} and get ideas that fit exactly.">
<link rel="canonical" href="{url}">
<meta property="og:title" content="3D print ideas for your {e(room)}"><meta property="og:description" content="Useful prints for your {e(room)}, with real models to download."><meta property="og:image" content="{SITE}/og.png"><meta property="og:url" content="{url}"><meta property="og:type" content="article"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/icon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;600;700&display=swap">
<script type="application/ld+json">{json.dumps(ld)}</script>
<style>
:root{{--bg:#0B0C0F;--card:#131418;--soft:#1B1D22;--ink:#F5F6F7;--muted:#9AA0A8;--lime:#5EEAD4;color-scheme:dark}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Geist,system-ui,sans-serif;padding:24px max(16px,env(safe-area-inset-left,0px)) 60px max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:760px;margin:0 auto}}a{{color:inherit}}
.top{{display:flex;justify-content:space-between;align-items:center;font-weight:700;text-decoration:none}}
.crumbs{{margin-top:28px;color:var(--muted);font-size:14px}}.crumbs a{{color:var(--muted)}}
h1{{font-size:clamp(30px,6vw,46px);line-height:1.08;letter-spacing:-.035em;margin:8px 0 10px;text-wrap:balance}}
.lead{{color:var(--muted);max-width:62ch;margin:0}}
.cta{{margin:22px 0 8px;display:flex;gap:14px;align-items:center;flex-wrap:wrap;background:var(--card);border:1px solid rgba(94,234,212,.35);border-radius:20px;padding:18px}}
.cta b{{flex:1;min-width:200px}}.btn{{background:var(--ink);color:#0B0C0F;text-decoration:none;font-weight:600;padding:13px 22px;border-radius:999px;white-space:nowrap}}
ol{{list-style:none;padding:0;margin:26px 0;display:grid;gap:12px}}
.it{{display:grid;grid-template-columns:110px 1fr;gap:16px;align-items:center;background:var(--card);border-radius:18px;padding:12px}}
.it>div{{min-width:0}}.pic{{display:block;width:110px;height:110px;border-radius:12px;background:var(--soft) center/cover no-repeat}}
.it h2{{font-size:18px;margin:0 0 4px;letter-spacing:-.02em}}.it p{{margin:0 0 4px;color:var(--muted)}}.it small{{color:var(--lime);font-size:13px}}
.more{{color:var(--muted);font-size:15px;line-height:2}}
footer{{margin-top:40px;color:var(--muted);font-size:13px}}
</style></head><body><main>
<a class="top" href="/">fitmyspot</a>
<nav class="crumbs"><a href="/ideas">Print ideas</a> / {e(title)}</nav>
<h1>3D print ideas for your {e(room)}</h1>
<p class="lead">{e(intro)}</p>
<div class="cta"><b>Want ideas for <em>your</em> {e(room)}? Snap a photo and get prints that fit exactly.</b><a class="btn" href="/">Snap a photo</a></div>
<ol>
{items}
</ol>
<div class="cta"><b>Every {e(room)} is different. Get ideas for yours.</b><a class="btn" href="/">Try it free</a></div>
<p class="more">More ideas: {others}</p>
<footer>Models and photos belong to their creators. We only link to them. <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a></footer>
</main>
<script>
document.querySelectorAll(".pic").forEach(async el => {{
  try {{
    const d = await (await fetch("/api/models?q=" + encodeURIComponent(el.dataset.q))).json();
    const m = d.models && d.models[0]; if (!m || !/^https:\\/\\/media\\.printables\\.com\\//.test(m.image)) return;
    el.style.backgroundImage = 'url("' + m.image + '")'; el.href = m.url; el.setAttribute("aria-label", m.title);
  }} catch (e) {{}}
}});
</script>
<script defer src="/_vercel/insights/script.js"></script>
</body></html>'''

def hub():
    e = html.escape
    cards = "\n".join(f'<li><a href="/ideas/{s}"><b>{e(v[1])}</b><span>{len(v[3])} ideas</span></a></li>' for s, v in ROOMS.items())
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>3D print ideas for every room – fitmyspot</title>
<meta name="description" content="Useful 3D print ideas for your car, desk, kitchen, bathroom, bedroom, garage, living room and hallway. With real models to download.">
<link rel="canonical" href="{SITE}/ideas">
<meta property="og:title" content="3D print ideas for every room"><meta property="og:image" content="{SITE}/og.png"><meta property="og:url" content="{SITE}/ideas"><meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/icon.svg" type="image/svg+xml"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;600;700&display=swap">
<style>
:root{{--bg:#0B0C0F;--card:#131418;--ink:#F5F6F7;--muted:#9AA0A8;--lime:#5EEAD4;color-scheme:dark}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Geist,system-ui,sans-serif;padding:24px max(16px,env(safe-area-inset-left,0px)) 60px max(16px,env(safe-area-inset-right,0px))}}
main{{max-width:760px;margin:0 auto}}a{{color:inherit;text-decoration:none}}.top{{font-weight:700}}
h1{{font-size:clamp(30px,6vw,46px);line-height:1.08;letter-spacing:-.035em;margin:36px 0 10px}}p{{color:var(--muted);margin:0}}
ul{{list-style:none;padding:0;margin:26px 0;display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}}
li a{{display:grid;gap:2px;background:var(--card);border-radius:18px;padding:18px}}li b{{font-size:18px}}li span{{color:var(--muted);font-size:14px}}li a:hover{{outline:1px solid var(--lime)}}
.btn{{display:inline-block;margin-top:8px;background:var(--ink);color:#0B0C0F;font-weight:600;padding:13px 22px;border-radius:999px}}
</style></head><body><main>
<a class="top" href="/">fitmyspot</a>
<h1>3D print ideas for every room</h1>
<p>Pick a room to see useful prints. Or snap a photo of your own space and get ideas that fit it exactly.</p>
<ul>
{cards}
</ul>
<a class="btn" href="/">Snap a photo</a>
</main><script defer src="/_vercel/insights/script.js"></script></body></html>'''

os.makedirs(OUT, exist_ok=True)
for slug, (room, title, intro, ideas) in ROOMS.items():
    open(os.path.join(OUT, slug + ".html"), "w").write(page(slug, room, title, intro, ideas))
open(os.path.join(OUT, "index.html"), "w").write(hub())
print("built", len(ROOMS), "pages")
