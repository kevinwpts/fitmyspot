// Tack-sidan: vilka guider ingick i det här köpet?
import { productsForSession, json } from "../lib/shop.js";

export async function GET(req) {
  const id = new URL(req.url).searchParams.get("session_id");
  try {
    const { products } = await productsForSession(id);
    return json({ products });
  } catch {
    return json({ products: [] }, 502);
  }
}
