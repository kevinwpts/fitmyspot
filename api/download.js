// Ladda ner en köpt guide. Bevis: antingen köp-id (direkt efter köpet) eller inloggning.
import { userEmail, productsForEmail, productsForSession, pdfResponse, json } from "../lib/shop.js";

export async function GET(req) {
  const q = new URL(req.url).searchParams;
  const product = q.get("product") || "";
  try {
    let owned = [];
    if (q.get("session_id")) owned = (await productsForSession(q.get("session_id"))).products;
    else {
      const email = await userEmail(req);
      if (!email) return json({ error: "Please log in again" }, 401);
      owned = await productsForEmail(email);
    }
    if (!owned.includes(product)) return json({ error: "We couldn't find this guide on your account" }, 403);
    return pdfResponse(product);
  } catch {
    return json({ error: "Download failed. Try again in a minute." }, 502);
  }
}
