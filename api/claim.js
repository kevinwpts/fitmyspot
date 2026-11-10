// Hämta ett låst resultat efter registrering (gratis, sparas i historiken)
import { rpc, SCAN_KEY } from "../lib/supa.js";
const json = (b, s = 200) => new Response(JSON.stringify(b), { status: s, headers: { "content-type": "application/json", "cache-control": "no-store" } });
async function handler(req) {
  if (req.method !== "POST") return json({ error: "POST only" }, 405);
  if (!(req.headers.get("authorization") || "").startsWith("Bearer ey")) return json({ error: "signin_required" }, 401);
  let id; try { ({ id } = await req.json()); } catch {}
  if (!/^[0-9a-f-]{36}$/.test(String(id || ""))) return json({ error: "bad_id" }, 400);
  try {
    const r = await rpc("claim_scan", { p_key: SCAN_KEY, p_id: id }, req);
    return r ? json(r) : json({ error: "not_found" }, 404);
  } catch { return json({ error: "failed" }, 500); }
}

export const POST = handler;
