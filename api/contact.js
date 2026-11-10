// Kontakt / borttagning: sparas i databasen (ersätter Netlify Forms)
import { rpc, SCAN_KEY } from "../lib/supa.js";
export async function POST(req) {
  const f = await req.formData().catch(() => null);
  if (!f || f.get("company")) return Response.redirect(new URL("/removal-sent", req.url), 303); // honungsfälla mot bots
  const email = String(f.get("email") || "").trim();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return new Response("Invalid email", { status: 400 });
  try {
    await rpc("save_contact", { p_key: SCAN_KEY, p_email: email, p_url: String(f.get("model_url") || ""), p_msg: String(f.get("message") || "") }, new Request(req.url));
  } catch {}
  return Response.redirect(new URL("/removal-sent", req.url), 303);
}
