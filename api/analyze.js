// boredprinter – tittar på bilden med Gemini och föreslår prints.
import { rpc, ipHash, SCAN_KEY, testKey } from "../lib/supa.js";
// Nyckeln ligger i Netlify: Environment variables -> GEMINI_API_KEY
const MODELS = ["gemini-3.1-flash-lite", "gemini-3.8-flash"];

const PROMPT = `You are boredprinter, an assistant for 3D printing hobbyists.
Look at the attached photo of a place (for example a car interior, a desk, a sofa, a kitchen, a garage or a hallway).
1. Name the ONE main spot in the photo in 2-3 plain lowercase words starting with "your", like "your bathroom", "your curtains", "your car", "your desk". Never list two things. No description.
2. List up to 8 concrete things you can see that matter for 3D prints (objects, surfaces, gaps, mess, cables, missing storage). Look at the WHOLE photo: the main spot, but also the background, walls, floor and shelves (for example posters, plants, a guitar, lamps, a chair).
3. Suggest 6 useful 3D prints for THIS exact photo, each solving or upgrading something you can see. About 4 should be for the main spot and 1-2 for other things in the photo (for example a poster or frame hanger, a plant pot or a guitar wall mount). Never suggest two prints for the same thing. Be specific to the photo, not generic.
For each print give:
- name: short product-style name
- why: one sentence that points to what you saw in the photo
- search: 2-4 English words that would find this model on Printables or MakerWorld, using words common in model titles. Include the place word when it matters (for example "car cup holder organizer", "sofa armrest tray").
- alt: a different, simpler 2-3 word English search for the same thing (fallback)
- material: PLA, PETG, TPU or ASA. If the place gets hot (car interior, near a heater, in sunlight) never use PLA.
- time: rough print time like "45 min" or "3 h"
- level: Easy, Medium or Hard
- buy_price: what a similar ready-made product typically costs in a store, in US dollars (whole number)
If the photo is too dark, too blurry, or does not show a place where prints make sense, return an empty prints list and set "photo_issue" to a short friendly tip (for example "The photo is too dark. Turn on a light and try again."). Otherwise "photo_issue" is null.
Reply ONLY with JSON: {"place":"...","seen":["..."],"hot":true,"photo_issue":null,"prints":[{"name":"","why":"","search":"","alt":"","material":"","time":"","level":"","buy_price":0}]}`;

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
  let quota;
  try {
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
          contents: [{ role: "user", parts: [{ inline_data: { mime_type: mime, data: image } }, { text: PROMPT + extras(body) }] }],
          generationConfig: { temperature: 0.4, maxOutputTokens: 4000, responseMimeType: "application/json", thinkingConfig: { thinkingBudget: 0 } },
        }),
      });
      if (!r.ok) continue;
      const data = await r.json();
      const text = (data.candidates?.[0]?.content?.parts ?? []).map((p) => p.text ?? "").join("");
      const out = JSON.parse(text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1));
      if (!Array.isArray(out.prints)) continue;
      out.prints = out.prints.slice(0, 8);
      // Dåligt foto eller inget att föreslå: ge tillbaka krediten
      if (!out.prints.length) {
        try { await rpc("refund_scan", { p_ip: ipHash(req), p_key: SCAN_KEY }, req); } catch {}
        out.refunded = true;
        return json(out);
      }
      if (!signedIn) {
        // Spara resultatet låst. Visa bara en smakbit tills besökaren skapar konto.
        let id = null;
        try { id = await rpc("save_pending", { p_ip: ipHash(req), p_key: SCAN_KEY, p_result: out }, req); } catch {}
        if (!id) return json({ error: "ai_failed" }, 502);
        // Namn och varför visas direkt (så man ser att den hittat något). Modeller och länkar först efter konto.
        const preview = out.prints.map((p) => ({ name: String(p.name || "").slice(0, 80), why: String(p.why || "").slice(0, 200), material: p.material, time: p.time, level: p.level }));
        return json({ locked: true, id, place: out.place, seen: Array.isArray(out.seen) ? out.seen.slice(0, 5) : [], hot: !!out.hot, count: out.prints.length, first: out.prints[0]?.name || null, preview });
      }
      out.quota = { free_left: quota.free_left ?? null, credits: quota.credits ?? null, via: quota.via };
      return json(out);
    } catch { /* prova nästa modell */ }
  }
  // AI:n misslyckades: ge tillbaka krediten
  try { await rpc("refund_scan", { p_ip: ipHash(req), p_key: SCAN_KEY }, req); } catch {}
  return json({ error: "ai_failed" }, 502);
}


export const POST = handler;
