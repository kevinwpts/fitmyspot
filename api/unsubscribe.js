// Avregistrera veckomejlet med ett klick (länk i mejlet). Ingen inloggning behövs.
import { timingSafeEqual } from "node:crypto";
import { rpc, SCAN_KEY, unsubToken } from "../lib/supa.js";

async function handler(req) {
  const sp = new URL(req.url).searchParams;
  const u = sp.get("u") || "", t = sp.get("t") || "";
  const ok = /^[0-9a-f-]{36}$/.test(u) && t.length === 32 && timingSafeEqual(Buffer.from(t), Buffer.from(unsubToken(u)));
  if (ok) await rpc("unsubscribe", { p_key: SCAN_KEY, p_uid: u }, new Request(req.url)).catch(() => {});
  const msg = ok ? "You're unsubscribed. You won't get weekly emails anymore." : "This link doesn't work. Turn off emails on your account page instead.";
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Emails – fitmyspot</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0B0C0F;color:#F5F6F7;font:16px/1.5 system-ui,sans-serif;text-align:center;padding:24px}a{color:#0B0C0F;background:#F5F6F7;padding:12px 22px;border-radius:999px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px}</style></head>
<body><main><h1 style="font-size:24px;margin:0 0 8px">${ok ? "Done" : "Hmm"}</h1><p style="color:#9AA0A8;margin:0">${msg}</p><a href="/">Back to fitmyspot</a></main></body></html>`, { status: ok ? 200 : 400, headers: { "content-type": "text/html; charset=utf-8" } });
}
export const GET = handler;
export const POST = handler;
