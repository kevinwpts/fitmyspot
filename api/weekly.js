// Veckans nya idéer för sparade platser. Körs av Vercel Cron en gång per dag.
// Kräver CRON_SECRET (Vercel skickar den automatiskt) och GEMINI_API_KEY.
import { rpc, SCAN_KEY } from "../lib/supa.js";

const MODELS = ["gemini-3.1-flash-lite", "gemini-3.8-flash"];
const anonReq = (url) => new Request(url);

async function ideasFor(spot, key) {
  const prompt = `You are FitMySpot, an assistant for 3D printing hobbyists.
A user saved this spot: "${String(spot.place).slice(0, 80)}".
Things seen there: ${JSON.stringify(spot.seen || []).slice(0, 600)}.
They already got these ideas, do NOT repeat them or near-duplicates: ${JSON.stringify(spot.known || []).slice(0, 1500)}.
Suggest 3 NEW useful 3D prints for this exact spot. Write in English.
For each: name, why (one sentence), search (2-4 English words for Printables), alt (simpler 2-3 English words), material (PLA/PETG/TPU/ASA, no PLA for hot places like cars), time, level (Easy/Medium/Hard), buy_price (typical store price of a similar product in US dollars, whole number).
Reply ONLY with JSON: {"prints":[{"name":"","why":"","search":"","alt":"","material":"","time":"","level":"","buy_price":0}]}`;
  for (const model of MODELS) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: "POST",
        headers: { "x-goog-api-key": key, "content-type": "application/json" },
        body: JSON.stringify({ contents: [{ role: "user", parts: [{ text: prompt }] }], generationConfig: { temperature: 0.7, maxOutputTokens: 1500, responseMimeType: "application/json", thinkingConfig: { thinkingBudget: 0 } } }),
      });
      if (!r.ok) continue;
      const d = await r.json();
      const t = (d.candidates?.[0]?.content?.parts ?? []).map((p) => p.text ?? "").join("");
      const out = JSON.parse(t.slice(t.indexOf("{"), t.lastIndexOf("}") + 1));
      if (Array.isArray(out.prints) && out.prints.length) return out.prints.slice(0, 3);
    } catch { /* nästa modell */ }
  }
  return null;
}

export async function GET(req) {
  const secret = process.env.CRON_SECRET;
  if (!secret || req.headers.get("authorization") !== `Bearer ${secret}`) return new Response("Forbidden", { status: 403 });
  const key = process.env.GEMINI_API_KEY;
  if (!key) return new Response("Missing key", { status: 500 });
  const spots = await rpc("due_spots", { p_key: SCAN_KEY, p_limit: 25 }, anonReq(req.url)).catch(() => []);
  let done = 0;
  for (const s of spots || []) {
    const ideas = await ideasFor(s, key);
    if (ideas) { await rpc("add_spot_ideas", { p_key: SCAN_KEY, p_id: s.id, p_ideas: ideas }, anonReq(req.url)).catch(() => {}); done++; }
  }
  return Response.json({ checked: (spots || []).length, updated: done });
}
