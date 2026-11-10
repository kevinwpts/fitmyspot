import { rpc, ipHash } from "../lib/supa.js";
async function handler(req) {
  try {
    const s = await rpc("scan_status", { p_ip: ipHash(req) }, req);
    return new Response(JSON.stringify(s), { headers: { "content-type": "application/json", "cache-control": "no-store" } });
  } catch {
    return new Response(JSON.stringify({ free_left: null }), { headers: { "content-type": "application/json" } });
  }
}

export const GET = handler;
