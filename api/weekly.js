// My home: nya idéer varje vecka för varje sparad plats, och ett veckomejl.
// Körs av Vercel Cron en gång per dag. Kräver CRON_SECRET och GEMINI_API_KEY.
// Mejl skickas bara om RESEND_API_KEY och MAIL_FROM finns (t.ex. "boredprinter <hello@boredprinter.com>").
import { rpc, SCAN_KEY, unsubToken } from "../lib/supa.js";

const MODELS = ["gemini-3.1-flash-lite", "gemini-3.8-flash"];
const SITE = process.env.SITE_URL || "https://boredprinter.com";
const UA = "boredprinter/0.1 (+https://boredprinter.com/removal)";
const anonReq = (url) => new Request(url);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

async function ideasFor(spot, key) {
  const prompt = `You are boredprinter, an assistant for 3D printing hobbyists.
A user saved this spot in their home: "${String(spot.place).slice(0, 80)}".
Things in that spot: ${JSON.stringify(spot.seen || []).slice(0, 600)}.
They already got these ideas. Do NOT repeat them or near-duplicates: ${JSON.stringify(spot.known || []).slice(0, 1500)}.
Suggest 6 NEW, genuinely useful 3D prints for exactly these things. Each must solve a real problem or upgrade one of the listed things. No generic trinkets.
For each: name (short), why (one short sentence that names the thing it is for), search (2-4 English words common in Printables model titles), alt (simpler 2-3 words), material (PLA/PETG/TPU/ASA, never PLA for hot places like cars), time, level (Easy/Medium/Hard).
Write in English. Reply ONLY with JSON: {"prints":[{"name":"","why":"","search":"","alt":"","material":"","time":"","level":""}]}`;
  for (const model of MODELS) {
    try {
      const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
        method: "POST",
        headers: { "x-goog-api-key": key, "content-type": "application/json" },
        body: JSON.stringify({ contents: [{ role: "user", parts: [{ text: prompt }] }], generationConfig: { temperature: 0.8, maxOutputTokens: 2000, responseMimeType: "application/json", thinkingConfig: { thinkingBudget: 0 } } }),
      });
      if (!r.ok) continue;
      const d = await r.json();
      const t = (d.candidates?.[0]?.content?.parts ?? []).map((p) => p.text ?? "").join("");
      const out = JSON.parse(t.slice(t.indexOf("{"), t.lastIndexOf("}") + 1));
      if (Array.isArray(out.prints) && out.prints.length) return out.prints.slice(0, 6);
    } catch { /* nästa modell */ }
  }
  return [];
}

// Riktig modell på Printables, annars ingen idé (bara specifika modeller visas)
async function findModel(q) {
  const query = `query($q:String!){ searchPrints2(query:$q, limit:8){ items{ id name slug downloadCount image{ filePath } user{ publicUsername } } } }`;
  try {
    const r = await fetch("https://api.printables.com/graphql/", { method: "POST", headers: { "user-agent": UA, "content-type": "application/json" }, body: JSON.stringify({ query, variables: { q } }) });
    if (!r.ok) return [];
    const items = (await r.json()).data?.searchPrints2?.items ?? [];
    return items.slice(0, 5).filter((i) => i.image?.filePath && i.name).map((i) => ({
      source: "Printables", title: i.name, creator: i.user?.publicUsername ?? null,
      image: `https://media.printables.com/${i.image.filePath}`, url: `https://www.printables.com/model/${i.id}-${i.slug}`, downloads: i.downloadCount ?? 0,
    }));
  } catch { return []; }
}

async function bestIdeas(spot, key) {
  const raw = await ideasFor(spot, key);
  const used = new Set(spot.urls || []);
  const out = [];
  for (const p of raw) {
    let models = await findModel(p.search || p.name);
    if (!models.length && p.alt) models = await findModel(p.alt);
    // Mest nedladdade bland de relevanta, och aldrig en modell vi redan visat för platsen
    const m = models.filter((x) => !used.has(x.url)).sort((a, b) => b.downloads - a.downloads)[0];
    if (!m) continue;
    used.add(m.url);
    out.push({ name: String(p.name).slice(0, 80), why: String(p.why || "").slice(0, 200), search: p.search, alt: p.alt, material: p.material, time: p.time, level: p.level, model: m, week: new Date().toISOString().slice(0, 10) });
    if (out.length >= 3) break;
  }
  return out;
}

function digestHtml(user) {
  const ideas = (user.spots || []).flatMap((s) => (s.ideas || []).map((i) => ({ ...i, place: String(s.place || "").replace(/^(your|the|my)\s+/i, "") }))).slice(0, 6);
  const unsub = `${SITE}/api/unsubscribe?u=${user.id}&t=${unsubToken(user.id)}`;
  const rows = ideas.map((i) => `
    <tr><td style="padding:0 0 14px">
      <a href="${esc(i.model?.url)}" style="text-decoration:none;color:#1A1918;display:block;border:1px solid #e6e8eb;border-radius:16px;overflow:hidden">
        <img src="${esc(i.model?.image)}" width="520" alt="" style="display:block;width:100%;max-width:520px;height:auto">
        <div style="padding:14px 16px"><div style="font:600 12px Arial,sans-serif;color:#C2410C;text-transform:uppercase;letter-spacing:.06em">For your ${esc(i.place)}</div>
        <div style="font:700 18px Arial,sans-serif;margin:4px 0">${esc(i.name)}</div>
        <div style="font:400 14px Arial,sans-serif;color:#555">${esc(i.why)}</div></div>
      </a></td></tr>`).join("");
  return {
    count: ideas.length,
    html: `<!doctype html><html><body style="margin:0;background:#F3F4F6;padding:24px 12px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr><td align="center">
<table role="presentation" width="100%" style="max-width:560px;background:#fff;border-radius:20px;padding:24px" cellpadding="0" cellspacing="0">
<tr><td style="font:800 15px Arial,sans-serif;color:#1A1918;padding-bottom:14px">boredprinter</td></tr>
<tr><td style="font:700 24px Arial,sans-serif;color:#1A1918;padding-bottom:4px">Your printer is bored. Here's what to print.</td></tr>
<tr><td style="font:400 15px Arial,sans-serif;color:#555;padding-bottom:18px">${ideas.length} new ideas that fit what you have.</td></tr>
${rows}
<tr><td align="center" style="padding:6px 0 18px"><a href="${SITE}/?home" style="background:#1A1918;color:#fff;text-decoration:none;font:700 15px Arial,sans-serif;padding:14px 26px;border-radius:999px;display:inline-block">Open my home</a></td></tr>
<tr><td style="font:400 12px Arial,sans-serif;color:#888;text-align:center">You get this because you turned on weekly emails on boredprinter. <a href="${unsub}" style="color:#888">Unsubscribe</a></td></tr>
</table></td></tr></table></body></html>`,
    unsub,
  };
}

async function sendDigests(req) {
  const key = process.env.RESEND_API_KEY, from = process.env.MAIL_FROM;
  if (!key || !from) return { sent: 0, skipped: "no_mail_config" };
  const users = await rpc("weekly_digest", { p_key: SCAN_KEY }, anonReq(req.url)).catch(() => []);
  let sent = 0;
  for (const u of users || []) {
    const d = digestHtml(u);
    if (!d.count) continue;
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { authorization: `Bearer ${key}`, "content-type": "application/json" },
      body: JSON.stringify({ from, to: [u.email], subject: d.count === 1 ? "A new print for your home" : `${d.count} new prints for your home`, html: d.html, headers: { "List-Unsubscribe": `<${d.unsub}>`, "List-Unsubscribe-Post": "List-Unsubscribe=One-Click" } }),
    }).catch(() => null);
    if (r?.ok) { await rpc("mark_digest", { p_key: SCAN_KEY, p_uid: u.id }, anonReq(req.url)).catch(() => {}); sent++; }
  }
  return { sent };
}

export async function GET(req) {
  const secret = process.env.CRON_SECRET;
  if (!secret || req.headers.get("authorization") !== `Bearer ${secret}`) return new Response("Forbidden", { status: 403 });
  const key = process.env.GEMINI_API_KEY;
  if (!key) return new Response("Missing key", { status: 500 });
  const started = Date.now();
  const spots = await rpc("due_spots", { p_key: SCAN_KEY, p_limit: 40 }, anonReq(req.url)).catch(() => []);
  let done = 0;
  // 4 åt gången, och sluta i tid innan Vercel stänger (max 300 s)
  const queue = [...(spots || [])];
  await Promise.all(Array.from({ length: 4 }, async () => {
    while (queue.length && Date.now() - started < 200_000) {
      const s = queue.shift();
      const ideas = await bestIdeas(s, key);
      await rpc("add_spot_ideas", { p_key: SCAN_KEY, p_id: s.id, p_ideas: ideas }, anonReq(req.url)).catch(() => {});
      if (ideas.length) done++;
    }
  }));
  const mail = await sendDigests(req);
  return Response.json({ checked: (spots || []).length, updated: done, ...mail });
}
