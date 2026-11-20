"""Enkla block för guiderna i markdown.

::: step ICON | Rubrik        → numrerat steg-kort med ikon (rubriken blir H2 i innehållsförteckningen)
::: answer                   → "Quick answer"-ruta
::: tip | Rubrik             → tips (grön)
::: warn | Rubrik            → varning (orange)
::: do | Rubrik              → "Gör detta nu"-checklista (lista med - )
::: yesno | Ja-rubrik | Nej-rubrik   → två kolumner; rader "+ text" och "- text"
::: icons                    → rutnät av ikonkort; rader "ICON | Titel | text"
Varje block slutar med en rad ":::".
"""
import re, html
from pathlib import Path
ILL = Path(__file__).resolve().parent.parent / "site/ill"

ICONS = {
  "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
  "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.6-3.6 3.3-5.5 6.5-5.5s5.9 1.9 6.5 5.5"/><path d="M16 4.6a3.5 3.5 0 0 1 0 6.8M18.5 14.8c1.7.8 2.8 2.6 3 5.2"/>',
  "bulb": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5 1 1.2 1.1 2.2h5c.1-1 .5-1.7 1.1-2.2A6 6 0 0 0 12 3z"/>',
  "scale": '<path d="M12 3v18M7 21h10M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/>',
  "tag": '<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
  "coins": '<ellipse cx="9" cy="6" rx="6" ry="2.5"/><path d="M3 6v4c0 1.4 2.7 2.5 6 2.5s6-1.1 6-2.5V6"/><path d="M9 15.5c-3.3 0-6-1.1-6-2.5v4c0 1.4 2.7 2.5 6 2.5 1.2 0 2.3-.1 3.2-.4"/><ellipse cx="17" cy="15" rx="4.5" ry="2"/><path d="M12.5 15v3c0 1.1 2 2 4.5 2s4.5-.9 4.5-2v-3"/>',
  "camera": '<path d="M4 8h3l2-3h6l2 3h3a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9a1 1 0 0 1 1-1z"/><circle cx="12" cy="13.5" r="3.5"/>',
  "box": '<path d="M3 7l9-4 9 4v10l-9 4-9-4z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
  "truck": '<path d="M2 6h12v10H2zM14 9h4l3 3v4h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
  "store": '<path d="M3 9l1.5-5h15L21 9"/><path d="M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/><path d="M5 12v8h14v-8M10 20v-5h4v5"/>',
  "ruler": '<path d="M3 17L17 3l4 4L7 21z"/><path d="M7 13l2 2M10 10l2 2M13 7l2 2"/>',
  "pencil": '<path d="M4 20l1-4L16 5l3 3L8 19z"/><path d="M14 7l3 3"/>',
  "printer": '<path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M7 14h10v7H7z"/>',
  "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
  "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
  "file": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',
  "shield": '<path d="M12 3l7 3v6c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
  "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
  "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
  "x": '<path d="M7 7l10 10M17 7L7 17"/>',
  "star": '<path d="M12 3l2.8 5.8 6.2.9-4.5 4.4 1 6.3L12 17.5 6.5 20.4l1-6.3L3 9.7l6.2-.9z"/>',
  "gift": '<rect x="3" y="8" width="18" height="5" rx="1"/><path d="M5 13v8h14v-8M12 8v13"/><path d="M12 8c-2-3-6-3-6-.5S10 8 12 8zm0 0c2-3 6-3 6-.5S14 8 12 8z"/>',
  "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
  "wrench": '<path d="M14.5 6.5a4 4 0 0 0-5 5L3 18l3 3 6.5-6.5a4 4 0 0 0 5-5l-2.5 2.5-3-3z"/>',
  "game": '<rect x="2" y="7" width="20" height="11" rx="5"/><path d="M7 11v3M5.5 12.5h3M15.5 12h.01M18 13.5h.01"/>',
  "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
  "zap": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
  "hand": '<path d="M7 11V6a1.5 1.5 0 0 1 3 0v5M10 10V4.5a1.5 1.5 0 0 1 3 0V10M13 10V5.5a1.5 1.5 0 0 1 3 0V12M16 11V8.5a1.5 1.5 0 0 1 3 0V14c0 4-3 7-7 7s-6-2-7.5-5L3 12.5a1.5 1.5 0 0 1 2.5-1.6L7 13"/>',
  "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  "list": '<path d="M9 6h12M9 12h12M9 18h12M4 6h.01M4 12h.01M4 18h.01"/>',
  "percent": '<path d="M19 5L5 19"/><circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="17" r="2.5"/>',
  "plug": '<path d="M9 2v6M15 2v6M6 8h12v4a6 6 0 0 1-12 0zM12 18v4"/>',
  "palette": '<path d="M12 3a9 9 0 0 0 0 18c1.5 0 2-1 2-2s-1-2 0-3 2-.5 3.5-.5A3.5 3.5 0 0 0 21 12a9 9 0 0 0-9-9z"/><circle cx="7.5" cy="11" r="1.2"/><circle cx="10" cy="7" r="1.2"/><circle cx="15" cy="7.5" r="1.2"/>',
  "rocket": '<path d="M5 15c-1.5 1.5-2 4.5-2 4.5s3-.5 4.5-2"/><path d="M9 15l-3-3c2-6 7-9 15-9 0 8-3 13-9 15z"/><circle cx="15" cy="9" r="1.8"/>',
  "msg": '<path d="M4 4h16v12H8l-4 4z"/>',
  "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
}

def icon(name, size=24):
    p = ICONS.get(name.strip(), ICONS["bulb"])
    return f'<svg class="ico" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{p}</svg>'

def preprocess(md):
    lines = md.split("\n"); out = []; i = 0; step = 0
    while i < len(lines):
        m = re.match(r"^:::\s*(\w+)\s*(.*)$", lines[i])
        if not m or m.group(1) == "":
            if lines[i].startswith("## "): step = 0  # nya avsnitt börjar om på steg 1
            out.append(lines[i]); i += 1; continue
        kind, rest = m.group(1), m.group(2)
        rest = rest.strip().lstrip("|").strip()
        args = [a.strip() for a in rest.split("|")] if rest else []
        body = []; i += 1; depth = 0
        while i < len(lines):
            t = lines[i].strip()
            if re.match(r"^:::\s*\w+", t): depth += 1
            elif t == ":::":
                if depth == 0: break
                depth -= 1
            body.append(lines[i]); i += 1
        i += 1
        b = preprocess("\n".join(body)).strip() if kind in ("step", "tip", "warn", "note", "answer", "case") else "\n".join(body).strip()
        if kind == "step":
            step += 1
            ic, title = (args + ["", ""])[:2]
            out.append(f'<section class="step" markdown="1">\n<div class="stepn" aria-hidden="true">{step:02d}</div>\n<div class="stepb" markdown="1">\n\n## {title}\n\n{b}\n\n</div>\n</section>\n')
        elif kind == "answer":
            out.append(f'<div class="qa" markdown="1">\n<p class="qah">The short answer</p>\n\n{b}\n\n</div>\n')
        elif kind in ("tip", "warn", "note"):
            t = args[0] if args else ""
            who = '<p class="kev"><img src="/img/kevin-sm.webp" alt="" width="28" height="28"><span>Kevin\'s tip</span></p>\n' if kind == "tip" else ""
            out.append(f'<div class="call {kind}" markdown="1">\n{who}<div markdown="1">\n\n{"**" + t + "**" if t else ""}\n\n{b}\n\n</div>\n</div>\n')
        elif kind == "case":
            t = args[0] if args else "Follow along"
            out.append(f'<div class="case" markdown="1">\n<p class="caseh">Follow along · {html.escape(t)}</p>\n\n{b}\n\n</div>\n')
        elif kind == "download":
            # rader: filnamn | Titel | beskrivning
            items = []
            for x in body:
                if "|" not in x: continue
                f, t, d = (p.strip() for p in (x.split("|") + ["", ""])[:3])
                items.append(f'<div class="dl"><div><b>{inline(t)}</b><p>{inline(d)}</p></div><button type="button" class="btn or" data-file="{html.escape(f)}">Download</button></div>')
            out.append(f'<div class="dls">{"".join(items)}</div>\n')
        elif kind == "do":
            t = args[0] if args else "Do this now"
            items = "".join(f'<li><span class="cb" aria-hidden="true"></span><span>{inline(x[2:])}</span></li>' for x in body if x.startswith("- "))
            out.append(f'<div class="dobox"><p class="doh">{html.escape(t)}</p><ul>{items}</ul></div>\n')
        elif kind == "yesno":
            yt, nt = (args + ["Allowed", "Not allowed"])[:2] if len(args) >= 2 else ("Allowed", "Not allowed")
            ys = "".join(f'<li>{icon("check", 18)}<span>{inline(x[2:])}</span></li>' for x in body if x.startswith("+ "))
            ns = "".join(f'<li>{icon("x", 18)}<span>{inline(x[2:])}</span></li>' for x in body if x.startswith("- "))
            out.append(f'<div class="yesno"><div class="yes"><p>{html.escape(yt)}</p><ul>{ys}</ul></div><div class="no"><p>{html.escape(nt)}</p><ul>{ns}</ul></div></div>\n')
        elif kind == "icons":
            cards = []
            for x in body:
                if "|" not in x: continue
                ic, t, d = (p.strip() for p in (x.split("|") + ["", ""])[:3])
                cards.append(f'<div class="ic-card"><b>{icon(ic, 18)}<span>{inline(t)}</span></b><p>{inline(d)}</p></div>')
            out.append(f'<div class="icgrid">{"".join(cards)}</div>\n')
        elif kind == "figure":
            name = args[0] if args else ""; cap = args[1] if len(args) > 1 else ""
            svg = (ILL / f"{name}.svg").read_text().strip()
            out.append(f'<figure class="ill">{svg}{f"<figcaption>{inline(cap)}</figcaption>" if cap else ""}</figure>\n')
        else:
            out.extend([lines[i - len(body) - 2]] + body + [":::"])
    return "\n".join(out)

def inline(t):
    """Minimal inline-markdown: **fet**, [länk](url), `kod`."""
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t
