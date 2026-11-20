// Statistik: försäljning från Stripe. Kräver statistiknyckeln (kollas i Supabase).
import { SB_URL, SB_ANON, json } from "../lib/shop.js";

export async function GET(req) {
  const q = new URL(req.url).searchParams;
  const key = q.get("k") || "", days = Math.min(365, Math.max(1, +q.get("d") || 7));
  const ok = await fetch(`${SB_URL}/rest/v1/rpc/stats_ok`, { method: "POST", headers: { apikey: SB_ANON, authorization: `Bearer ${SB_ANON}`, "content-type": "application/json" }, body: JSON.stringify({ p_key: key }) }).then((r) => r.json()).catch(() => false);
  if (ok !== true) return json({ error: "No access" }, 403);
  const sk = process.env.STRIPE_SECRET_KEY;
  if (!sk) return json({ error: "Stripe not set up" }, 500);
  const since = Math.floor(Date.now() / 1000) - days * 86400;
  let sales = 0, revenue = 0, discounted = 0, currency = "usd", after = "", more = true, n = 0;
  try {
    while (more && n++ < 10) {
      const r = await fetch(`https://api.stripe.com/v1/checkout/sessions?limit=100&status=complete&created[gte]=${since}${after}`, { headers: { authorization: `Bearer ${sk}` } });
      if (!r.ok) throw new Error("stripe " + r.status);
      const d = await r.json();
      for (const s of d.data || []) {
        if (!["paid", "no_payment_required"].includes(s.payment_status)) continue;
        sales++; revenue += s.amount_total || 0; currency = s.currency || currency;
        if ((s.total_details?.amount_discount || 0) > 0) discounted++;
      }
      more = d.has_more; if (more) after = "&starting_after=" + d.data[d.data.length - 1].id;
    }
  } catch { return json({ error: "Couldn't reach Stripe" }, 502); }
  return json({ sales, revenue: revenue / 100, currency, discounted });
}
