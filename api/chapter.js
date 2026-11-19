// Läsläge: ger ett låst kapitel till den som har köpt guiden.
// Bevis: inloggning (mejllänk) eller köp-id från tack-sidan. Stripe är sanningen.
import { userEmail, productsForEmail, productsForSession, chapterHtml, GUIDE_PRODUCT, json } from "../lib/shop.js";

export async function GET(req) {
  const q = new URL(req.url).searchParams;
  const guide = q.get("g") || "", slug = q.get("c") || "";
  const need = GUIDE_PRODUCT[guide];
  if (!need) return json({ error: "Unknown guide" }, 404);
  try {
    let owned = [];
    if (q.get("session_id")) owned = (await productsForSession(q.get("session_id"))).products;
    else {
      const email = await userEmail(req);
      if (!email) return json({ error: "Please log in" }, 401);
      owned = await productsForEmail(email);
    }
    if (!owned.includes(need)) return json({ error: "Not unlocked" }, 403);
    const html = await chapterHtml(guide, slug);
    if (!html) return json({ error: "Chapter not found" }, 404);
    return json({ html });
  } catch {
    return json({ error: "Try again in a minute" }, 502);
  }
}
