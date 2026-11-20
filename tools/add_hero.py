"""Lägger in en hjältebild för en gratisguide. Kör: python3 tools/add_hero.py SLUG BILD "alt-text" """
import sys, re
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parent.parent
slug, src, alt = sys.argv[1], sys.argv[2], sys.argv[3]
im = Image.open(src).convert("RGB"); w, h = im.size
if w / h > 16 / 9: nw = int(h * 16 / 9); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
else: nh = int(w * 9 / 16); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
im.resize((1600, 900), Image.LANCZOS).save(R / f"public/img/guides/{slug}.webp", "WEBP", quality=80)
md = R / f"content/guides/{slug}.md"; s = md.read_text()
s = re.sub(r'^image_alt:.*\n', '', s, flags=re.M)
s = s.replace("\nnav:", f'\nimage_alt: "{alt}"\nnav:', 1); md.write_text(s)
print("ok", slug)
