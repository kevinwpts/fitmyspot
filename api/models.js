// boredprinter – hittar riktiga modeller (bild, namn, skapare, länk) för ett sökord.
// Källa: Printables. Vi lagrar inga filer: bara en liten bild + namn på skaparen + länk tillbaka.
const UA = "boredprinter/0.1 (+https://boredprinter.com/removal)";
const cache = new Map();

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

async function handler(req) {
  const sp = new URL(req.url).searchParams;
  const q = (sp.get("q") || "").trim().slice(0, 60);
  const alt = (sp.get("alt") || "").trim().slice(0, 60);
  if (q.length < 2) return json({ models: [] });
  const key = q + "|" + alt;
  if (cache.has(key)) return json({ models: cache.get(key) });

  // MakerWorld skyddar sin sajt mot automatisk hämtning, så dit länkar vi bara.
  // Prova flera sökningar tills vi hittar bilder: huvudsök, alternativ, sen kortare.
  const words = q.split(/\s+/);
  const tries = [q, alt, words.slice(-2).join(" "), words.slice(0, 2).join(" ")]
    .filter((t, i, a) => t && t.length > 2 && a.indexOf(t) === i);
  let models = [];
  for (const t of tries) {
    try { models = await printables(t); } catch { models = []; }
    if (models.length) break;
  }
  if (models.length) cache.set(key, models);
  return json({ models });
}


export const GET = handler;
