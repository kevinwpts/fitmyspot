// Delad hjälp: anrop till Supabase (krediter). URL och anon-nyckel är publika.
import { createHash, createHmac } from "node:crypto";
export const SB_URL = "https://rcntkzrbanwigypkumvd.supabase.co";
// Hemlig nyckel som bara servern har (krävs för att förbruka analyser). Ligger aldrig i webbsidan.
export const SCAN_KEY = process.env.SCAN_KEY || "";
export const SB_ANON = "sb_publishable_Eoce1JVPaM-SgVSllLbi4g_ZiTaGejr";

export function ipHash(req) {
  const ip = req.headers.get("x-real-ip") || req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
  return createHash("sha256").update("printspot:" + ip).digest("hex").slice(0, 32);
}

export async function rpc(name, args, req) {
  const auth = req.headers.get("authorization");
  const r = await fetch(`${SB_URL}/rest/v1/rpc/${name}`, {
    method: "POST",
    headers: { apikey: SB_ANON, authorization: auth && auth.startsWith("Bearer ey") ? auth : `Bearer ${SB_ANON}`, "content-type": "application/json" },
    body: JSON.stringify(args),
  });
  if (!r.ok) throw new Error("rpc " + name + " " + r.status + " " + (await r.text()).slice(0, 200));
  return r.json();
}

// Token för avregistreringslänken i veckomejlet
export const unsubToken = (uid) => createHmac("sha256", SCAN_KEY || "x").update("unsub:" + uid).digest("hex").slice(0, 32);

// Testnyckel för ägaren: hoppar över gratisgränsen utan konto (länk med ?test=...)
export const testKey = () => createHmac("sha256", SCAN_KEY || "x").update("owner-test").digest("hex").slice(0, 20);
