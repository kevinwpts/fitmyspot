import { rpc } from "../lib/supa.js";
async function handler(req) {
  let n = null; try { n = await rpc("total_scans", {}, new Request(req.url)); } catch {}
  return new Response(JSON.stringify({ scans: n }), { headers: { "content-type": "application/json", "cache-control": "public, max-age=300" } });
}

export const GET = handler;
