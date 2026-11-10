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
  // Skicka vidare till ägarens inkorg (kräver RESEND_API_KEY och MAIL_FROM)
  const key = process.env.RESEND_API_KEY, from = process.env.MAIL_FROM, to = process.env.OWNER_EMAIL || "kevinwpts@gmail.com";
  if (key && from) {
    const esc = (v) => String(v || "").slice(0, 2000).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    await fetch("https://api.resend.com/emails", {
      method: "POST", headers: { authorization: `Bearer ${key}`, "content-type": "application/json" },
      body: JSON.stringify({ from, to: [to], reply_to: email, subject: "boredprinter: new contact message",
        html: `<p><b>From:</b> ${esc(email)}</p><p><b>Model link:</b> ${esc(f.get("model_url"))}</p><p><b>Message:</b><br>${esc(f.get("message")).replace(/\n/g, "<br>")}</p>` }),
    }).catch(() => {});
  }
  return Response.redirect(new URL("/removal-sent", req.url), 303);
}
