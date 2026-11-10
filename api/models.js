// boredprinter – hittar riktiga modeller (bild, namn, skapare, länk) för ett sökord.
// Källor: MakerWorld (via Brave Search, kräver BRAVE_API_KEY) och Printables.
// Vi lagrar inga filer: bara en liten bild + namn + länk tillbaka till skaparens sida.
import { rpc, SCAN_KEY } from "../lib/supa.js";

const UA = "boredprinter/0.1 (+https://boredprinter.com/removal)";
const mem = new Map();
const anon = () => new Request("https://boredprinter.com/");

const json = (body, status = 200) => new Response(JSON.stringify(body), {
  status, headers: { "content-type": "application/json", "cache-control": "public, max-age=3600" },
});

async function printables(q) {
  const query = `query($q:String!){ searchPrints2(query:$q, limit:12){ items{ id name slug downloadCount likesCount image{ filePath } user{ publicUsername } } } }`;
  const r = await fetch("https://api.printables.com/graphql/", {
    method: "POST",
    headers: { "user-agent": UA, "content-type": "application/json" },
    body: JSON.stringify({ query, variables: { q } }),
  });
  if (!r.ok) throw new Error("pr " + r.status);
  const d = await r.json();
  const items = d.data?.searchPrints2?.items ?? [];
  // Behåll de mest relevanta, välj sen de mest nedladdade bland dem.
  const top = items.slice(0, 5).sort((a, b) => (b.downloadCount ?? 0) - (a.downloadCount ?? 0));
  return top.slice(0, 3).map((i) => ({
    source: "Printables",
    title: i.name,
    creator: i.user?.publicUsername ?? null,
    image: i.image?.filePath ? `https://media.printables.com/${i.image.filePath}` : null,
    url: `https://www.printables.com/model/${i.id}-${i.slug}`,
    downloads: i.downloadCount ?? 0,
  })).filter((m) => m.title && m.image);
}

// MakerWorld via Brave Search: bara riktiga modellsidor (…/models/123…), med bild.
async function makerworld(q) {
  const key = process.env.BRAVE_API_KEY;
  if (!key) return [];
  const u = "https://api.search.brave.com/res/v1/web/search?count=10&safesearch=strict&q=" + encodeURIComponent(`site:makerworld.com ${q}`);
  const r = await fetch(u, { headers: { "x-subscription-token": key, accept: "application/json" } });
  if (!r.ok) throw new Error("brave " + r.status);
  const d = await r.json();
  const out = [];
  for (const it of d.web?.results ?? []) {
    const url = String(it.url || "");
    if (!/^https:\/\/makerworld\.com\/(?:[a-z]{2}\/)?models\/\d+/.test(url)) continue;
    const image = it.thumbnail?.src || "";
    if (!/^https:\/\/imgs\.search\.brave\.com\//.test(image)) continue;
    // Titlar ser ut som "Cup Holder Organizer by Maker - MakerWorld: Download Free 3D Models"
    let title = String(it.title || "").replace(/<[^>]+>/g, "")
      .replace(/\s*[-|–·:]\s*MakerWorld.*$/i, "")
      .replace(/\s*[-|–·:]\s*(Free\s+)?3D\s+(Print(able)?\s+)?Models?.*$/i, "")
      .replace(/\s*[-|–·:]\s*Download.*$/i, "").trim();
    let creator = null;
    const by = title.match(/^(.*)\s+by\s+([^-|]+)$/i);
    if (by) { title = by[1].trim(); creator = by[2].trim(); }
    if (!title) continue;
    out.push({ source: "MakerWorld", title: title.slice(0, 120), creator, image, url: url.split("?")[0], downloads: null });
    if (out.length >= 3) break;
  }
  return out;
}

async function search(t) {
  const [mw, pr] = await Promise.all([makerworld(t).catch(() => []), printables(t).catch(() => [])]);
  // MakerWorld först (flest användare), sen Printables. Varvat så båda syns om fler visas.
  const out = [];
  for (let i = 0; i < 3; i++) { if (mw[i]) out.push(mw[i]); if (pr[i]) out.push(pr[i]); }
  return out;
}

async function handler(req) {
  const sp = new URL(req.url).searchParams;
  const q = (sp.get("q") || "").trim().toLowerCase().slice(0, 60);
  const alt = (sp.get("alt") || "").trim().toLowerCase().slice(0, 60);
  if (q.length < 2) return json({ models: [] });
  // Egen cache-nyckel när MakerWorld är på, så gamla "bara Printables"-svar inte fastnar
  const key = (process.env.BRAVE_API_KEY ? "mw|" : "") + q + "|" + alt;
  if (mem.has(key)) return json({ models: mem.get(key) });
  // Delad cache i databasen (7 dagar), så samma sökning inte kostar igen
  try { const hit = await rpc("get_models", { p_key: SCAN_KEY, p_q: key }, anon()); if (Array.isArray(hit) && hit.length) { mem.set(key, hit); return json({ models: hit }); } } catch {}

  // Prova flera sökningar tills vi hittar något: huvudsök, alternativ, sen kortare.
  const words = q.split(/\s+/);
  const tries = [q, alt, words.slice(-2).join(" "), words.slice(0, 2).join(" ")]
    .filter((t, i, a) => t && t.length > 2 && a.indexOf(t) === i);
  let models = [];
  for (const t of tries) {
    models = await search(t);
    if (models.length) break;
  }
  if (models.length) {
    mem.set(key, models);
    await rpc("put_models", { p_key: SCAN_KEY, p_q: key, p_models: models }, anon()).catch(() => {});
  }
  return json({ models });
}

export const GET = handler;
