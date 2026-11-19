// My guides: vilka guider har den inloggade e-posten köpt?
import { userEmail, productsForEmail, json } from "../lib/shop.js";

export async function GET(req) {
  const email = await userEmail(req);
  if (!email) return json({ error: "Please log in again" }, 401);
  try {
    return json({ email, products: await productsForEmail(email) });
  } catch {
    return json({ email, products: [], error: "Couldn't check purchases right now" }, 502);
  }
}
