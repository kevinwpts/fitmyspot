// Delad hjälp för köp: Stripe-kontroll, inloggning och filer.
// Inga köp sparas hos oss: Stripe är sanningen. Vi frågar Stripe varje gång.
import { readFile } from "node:fs/promises";
import { join } from "node:path";

export const SB_URL = "https://rcntkzrbanwigypkumvd.supabase.co";
export const SB_ANON = "sb_publishable_Eoce1JVPaM-SgVSllLbi4g_ZiTaGejr";
const STRIPE = "https://api.stripe.com/v1";

export const FILES = {
  playbook: "boredprinter-3d-print-side-hustle-playbook.pdf",
  design: "boredprinter-design-your-own-bestseller.pdf",
};

// Vilka guider ett köp ger, utifrån produktnamnet i Stripe
export function productsFromName(name = "") {
  const n = name.toLowerCase();
  if (/bundle|both/.test(n)) return ["playbook", "design"];
  if (/playbook|side hustle/.test(n)) return ["playbook"];
  if (/design/.test(n)) return ["design"];
  return [];
}

export const json = (data, status = 200) => new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store" } });

async function stripe(path) {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error("Payments are not set up yet");
  const r = await fetch(STRIPE + path, { headers: { authorization: `Bearer ${key}` } });
  if (!r.ok) throw new Error("stripe " + r.status);
  return r.json();
}

function productsOfSession(s) {
  if (s.status !== "complete" || !["paid", "no_payment_required"].includes(s.payment_status)) return [];
  const out = new Set();
  for (const li of s.line_items?.data || []) productsFromName(li.description || li.price?.product?.name || "").forEach((p) => out.add(p));
  return [...out];
}

export async function productsForSession(id) {
  if (!/^cs_[A-Za-z0-9_]+$/.test(id || "")) return { products: [] };
  const s = await stripe(`/checkout/sessions/${id}?expand[]=line_items`);
  return { products: productsOfSession(s), email: s.customer_details?.email || "" };
}

export async function productsForEmail(email) {
  const out = new Set();
  for (const e of new Set([email, email.toLowerCase()])) {
    const list = await stripe(`/checkout/sessions?limit=100&status=complete&customer_details[email]=${encodeURIComponent(e)}&expand[]=data.line_items`);
    for (const s of list.data || []) productsOfSession(s).forEach((p) => out.add(p));
  }
  return [...out];
}

// Inloggad via mejllänk (Supabase) → bekräftad e-post
export async function userEmail(req) {
  const auth = req.headers.get("authorization") || "";
  if (!auth.startsWith("Bearer ey")) return null;
  const r = await fetch(`${SB_URL}/auth/v1/user`, { headers: { apikey: SB_ANON, authorization: auth } });
  if (!r.ok) return null;
  const u = await r.json();
  return u.email && (u.email_confirmed_at || u.confirmed_at) ? u.email : null;
}

export async function pdfResponse(product) {
  const name = FILES[product];
  if (!name) return json({ error: "Unknown guide" }, 404);
  try {
    const buf = await readFile(join(process.cwd(), "private/guides", name));
    return new Response(buf, { headers: { "content-type": "application/pdf", "content-disposition": `attachment; filename="${name}"`, "x-filename": name, "cache-control": "private, no-store" } });
  } catch {
    return json({ error: "This guide isn't ready yet. You'll get an email when it is." }, 404);
  }
}
