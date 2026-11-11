// boredprinter – tittar på bilden med Gemini och föreslår prints.
import { rpc, ipHash, SCAN_KEY, testKey } from "../lib/supa.js";
// Nyckeln ligger i Netlify: Environment variables -> GEMINI_API_KEY
const MODELS = ["gemini-3.1-flash-lite", "gemini-3.8-flash"];

const PROMPT = `You are boredprinter, an assistant for 3D printing hobbyists.
Look at the attached photo of a place (for example a car interior, a desk, a sofa, a kitchen, a garage or a hallway).
1. Name the ONE main spot in the photo in 2-3 plain lowercase words starting with "your", like "your bathroom", "your curtains", "your car", "your desk". Never list two things. No description.
2. List up to 10 concrete things you can see that matter for 3D prints (objects, surfaces, gaps, mess, cables, missing storage). Look at the WHOLE photo: the main spot, but also the background, walls, floor and shelves (for example posters, plants, a guitar, lamps, a chair).
3. Suggest 10 useful 3D prints for THIS exact photo, each solving or upgrading something you can see. About 6 should be for the main spot and 3-4 for other things in the photo (for example a poster or frame hanger, a plant pot or a guitar wall mount). Never suggest two prints for the same thing. Be specific to the photo, not generic.
For each print give:
- name: short product-style name
- why: one sentence that points to what you saw in the photo
- search: 2-4 English words that would find this model on Printables or MakerWorld, using words common in model titles. Include the place word when it matters (for example "car cup holder organizer", "sofa armrest tray").
- alt: a different, simpler 2-3 word English search for the same thing (fallback)
- material: PLA, PETG, TPU or ASA. If the place gets hot (car interior, near a heater, in sunlight) never use PLA.
- time: rough print time like "45 min" or "3 h"
- grams: rough filament use in grams for one print (whole number, typical settings)
- level: Easy, Medium or Hard
- buy_price: what a similar ready-made product typically costs in a store, in US dollars (whole number)
4. CUSTOM INSERT: if the photo mainly shows an open drawer, box, tray, bin, cabinet shelf or similar container that could use a custom 3D printed organizer insert, fill "insert". Otherwise "insert" is null.
- what: 2-3 words, like "desk drawer" or "kitchen drawer"
- w_mm, d_mm, h_mm: your best estimate of the INSIDE width (left-right), depth (front-back) and height in millimeters. Use objects for scale (A4 paper 210x297, pen 140 mm long, AA battery 50 mm, credit card 86x54, fork 190 mm). Typical drawers are 300-800 wide, 350-550 deep, 60-150 high.
- confidence: "low", "medium" or "high"
- items: up to 8 short names of the things inside (like "pens", "batteries", "cables")
- rows: a layout for the insert seen from above, from the back row to the front row. 1-4 rows. Each row has "size" (fraction of the depth) and 1-5 "cells", each with "size" (fraction of the width) and a short "label" for what goes there. Sizes in each list add up to 1. Make compartments that fit the items you see (long narrow ones for pens and utensils, small square ones for small parts).
If the photo is too dark, too blurry, or does not show a place where prints make sense, return an empty prints list and set "photo_issue" to a short friendly tip (for example "The photo is too dark. Turn on a light and try again."). Otherwise "photo_issue" is null.
Reply ONLY with JSON: {"place":"...","seen":["..."],"hot":true,"photo_issue":null,"prints":[{"name":"","why":"","search":"","alt":"","material":"","time":"","grams":0,"level":"","buy_price":0}],"insert":null}`;

// Lådinsats: tvätta AI:ns svar så att mått och layout alltid är rimliga
function cleanInsert(x) {
  if (!x || typeof x !== "object") return null;
  const n = (v, lo, hi, d) => { v = Math.round(+v); return Number.isFinite(v) ? Math.min(hi, Math.max(lo, v)) : d; };
  const norm = (arr) => { const t = arr.reduce((a, c) => a + (c.size > 0 ? c.size : 0), 0) || 1; return arr.map((c) => ({ ...c, size: (c.size > 0 ? c.size : 0) / t })); };
  let rows = Array.isArray(x.rows) ? x.rows.slice(0, 4) : [];
  rows = rows.map((r) => ({ size: +r?.size || 0, cells: norm((Array.isArray(r?.cells) ? r.cells.slice(0, 5) : []).map((c) => ({ size: +c?.size || 0, label: String(c?.label || "").slice(0, 24) }))) })).filter((r) => r.cells.length);
  if (!rows.length) rows = [{ size: 1, cells: [{ size: 0.5, label: "" }, { size: 0.5, label: "" }] }];
  rows = norm(rows).map((r) => ({ ...r, cells: r.cells.some((c) => c.size <= 0) ? r.cells.map((c) => ({ ...c, size: 1 / r.cells.length })) : r.cells }));
  return {
    what: String(x.what || "drawer").slice(0, 40),
    w_mm: n(x.w_mm, 60, 1200, 400), d_mm: n(x.d_mm, 60, 1000, 450), h_mm: n(x.h_mm, 20, 300, 80),
    confidence: ["low", "medium", "high"].includes(x.confidence) ? x.confidence : "low",
    items: (Array.isArray(x.items) ? x.items : []).slice(0, 8).map((i) => String(i).slice(0, 30)),
    rows,
  };
}

// Kända printrar: byggvolym (mm), skåp, flerfärg
const PRINTERS = {
  "bambu-a1-mini": ["Bambu Lab A1 mini", 180, false, true],
  "bambu-a1": ["Bambu Lab A1", 256, false, true],
  "bambu-p1s": ["Bambu Lab P1S", 256, true, true],
  "bambu-p2s": ["Bambu Lab P2S", 256, true, true],
  "bambu-x1c": ["Bambu Lab X1 Carbon", 256, true, true],
  "bambu-h2d": ["Bambu Lab H2D", 325, true, true],
  "prusa-mk4": ["Prusa MK4/MK4S", 250, false, false],
  "prusa-core-one": ["Prusa Core One", 250, true, false],
  "prusa-mini": ["Prusa Mini", 180, false, false],
  "creality-k1": ["Creality K1", 220, true, false],
  "creality-ender3": ["Creality Ender 3", 220, false, false],
  "elegoo-centauri": ["Elegoo Centauri Carbon", 256, true, false],
};


function extras(body) {
  const lines = [];
  const p = PRINTERS[body?.printer];
  if (p) {
    lines.push(`The user prints on a ${p[0]} (build volume about ${p[1]} mm per side${p[2] ? ", enclosed" : ", open frame"}${p[3] ? ", can print several colors" : ""}).`);
    lines.push(`Only suggest prints that fit within ${p[1]} mm or can be printed in parts.`);
    if (!p[2]) lines.push("It has no enclosure, so prefer PETG over ASA/ABS.");
  }
  lines.push('Write everything in English.');
  return lines.length ? "\n\nExtra context:\n" + lines.join("\n") : "";
}

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

async function handler(req) {
  if (req.method !== "POST") return json({ error: "POST only" }, 405);
  const origin = req.headers.get("origin") || "";
  const host = new URL(req.url).host;
  if (origin && new URL(origin).host !== host) return json({ error: "forbidden" }, 403);
  const key = process.env.GEMINI_API_KEY;
  if (!key) return json({ error: "missing_key" }, 500);

  let body;
  try { body = await req.json(); } catch { return json({ error: "bad_json" }, 400); }
  const { image, mime = "image/jpeg" } = body || {};
  if (typeof image !== "string" || image.length < 100) return json({ error: "no_image" }, 400);
  if (image.length > 4_000_000) return json({ error: "too_big" }, 413);
  if (!/^image\/(jpeg|png|webp)$/.test(mime)) return json({ error: "bad_type" }, 400);

  // Inloggad: förbrukar dagens gratis eller en kredit. Inte inloggad: låst förhandsvisning (max 3/dag per nätverk).
  const signedIn = (req.headers.get("authorization") || "").startsWith("Bearer ey");
  // "Show more ideas": samma bild igen, nya idéer. Bara inloggade, kostar ingen kredit (tak per dygn).
  const more = body.more === true;
  const exclude = more && Array.isArray(body.exclude) ? body.exclude.slice(0, 40).map((x) => String(x).slice(0, 80)) : [];
  if (more && !signedIn) return json({ error: "signin_required" }, 401);
  let quota;
  if (more) {
    try { quota = await rpc("use_more", { p_key: SCAN_KEY }, req); } catch { return json({ error: "quota_check_failed" }, 503); }
    if (!quota?.ok) return json({ error: quota?.reason === "signin" ? "signin_required" : "more_limit" }, quota?.reason === "signin" ? 401 : 429);
  } else try {
    quota = signedIn
      ? await rpc("use_scan", { p_ip: ipHash(req), p_key: SCAN_KEY }, req)
      : await rpc("use_preview", { p_ip: ipHash(req), p_key: SCAN_KEY, p_test: !!SCAN_KEY && req.headers.get("x-test-key") === testKey() }, req);
  } catch { return json({ error: "quota_check_failed" }, 503); }
  if (!quota.ok && quota.reason === "busy") return json({ error: "busy" }, 503);
  if (!quota.ok && quota.reason === "preview_limit") return json({ error: "signin_required" }, 401);
  if (!quota.ok && quota.reason === "signin") return json({ error: "signin_required" }, 401);
  if (!quota.ok) return json({ error: "no_credits", signed_in: signedIn }, 402);

  for (const model of MODELS) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: "POST",
        headers: { "x-goog-api-key": key, "content-type": "application/json" },
        body: JSON.stringify({
          contents: [{ role: "user", parts: [{ inline_data: { mime_type: mime, data: image } }, { text: PROMPT + extras(body) + (exclude.length ? `\nThese prints were ALREADY suggested for this photo, so do NOT repeat them or suggest near-duplicates: ${exclude.join("; ")}. Suggest 10 NEW, different prints for other things you can see (smaller objects, corners, walls, shelves, the floor), still specific to this photo.` : "") }] }],
          generationConfig: { temperature: 0.4, maxOutputTokens: 4000, responseMimeType: "application/json", thinkingConfig: { thinkingBudget: 0 } },
        }),
      });
      if (!r.ok) continue;
      const data = await r.json();
      const text = (data.candidates?.[0]?.content?.parts ?? []).map((p) => p.text ?? "").join("");
      const out = JSON.parse(text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1));
      if (!Array.isArray(out.prints)) continue;
      const up = (t) => { t = String(t || "").trim(); return t.charAt(0).toUpperCase() + t.slice(1); };
      out.prints = out.prints.slice(0, 10).map((p) => ({ ...p, name: up(p.name), why: up(p.why) }));
      out.insert = cleanInsert(out.insert);
      // Dåligt foto eller inget att föreslå: ge tillbaka krediten
      if (more) return json({ ...out, more: true });
      if (!out.prints.length) {
        try { await rpc("refund_scan", { p_ip: ipHash(req), p_key: SCAN_KEY }, req); } catch {}
        out.refunded = true;
        return json(out);
      }
      if (!signedIn) {
        // Första bilden (per nätverk och dygn) visas helt utan konto. Därefter låst tills man skapar konto.
        let full = false;
        try { full = await rpc("can_full", { p_ip: ipHash(req), p_key: SCAN_KEY }, req); } catch {}
        let id = null;
        try { id = await rpc("save_pending", { p_ip: ipHash(req), p_key: SCAN_KEY, p_result: out, p_full: !!full }, req); } catch {}
        if (full) return json({ ...out, free: true });
        if (!id) return json({ error: "ai_failed" }, 502);
        // Namn och varför visas direkt (så man ser att den hittat något). Modeller och länkar först efter konto.
        const preview = out.prints.map((p) => ({ name: String(p.name || "").slice(0, 80), why: String(p.why || "").slice(0, 200), material: p.material, time: p.time, grams: p.grams, level: p.level }));
        return json({ locked: true, id, place: out.place, seen: Array.isArray(out.seen) ? out.seen.slice(0, 5) : [], hot: !!out.hot, count: out.prints.length, first: out.prints[0]?.name || null, preview });
      }
      out.quota = { free_left: quota.free_left ?? null, credits: quota.credits ?? null, via: quota.via };
      return json(out);
    } catch { /* prova nästa modell */ }
  }
  // AI:n misslyckades: ge tillbaka krediten
  if (more) return json({ error: "ai_failed" }, 502);
  try { await rpc("refund_scan", { p_ip: ipHash(req), p_key: SCAN_KEY }, req); } catch {}
  return json({ error: "ai_failed" }, 502);
}


export const POST = handler;
