// Verktygslådan: ger köparen filerna (xlsx/pdf). Samma bevis som kapitlen.
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { userEmail, productsForEmail, productsForSession, json } from "../lib/shop.js";

const FILES = {
  "print-to-profit-toolkit.xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "listing-templates.pdf": "application/pdf",
  "30-day-checklist.pdf": "application/pdf",
};

export async function GET(req) {
  const q = new URL(req.url).searchParams;
  const name = q.get("f") || "";
  const type = FILES[name];
  if (!type) return json({ error: "Unknown file" }, 404);
  try {
    let owned = [];
    if (q.get("session_id")) owned = (await productsForSession(q.get("session_id"))).products;
    else {
      const email = await userEmail(req);
      if (!email) return json({ error: "Please log in" }, 401);
      owned = await productsForEmail(email);
    }
    if (!owned.includes("playbook")) return json({ error: "Not unlocked" }, 403);
    const buf = await readFile(join(process.cwd(), "private/files", name));
    return new Response(buf, { headers: { "content-type": type, "content-disposition": `attachment; filename="${name}"`, "cache-control": "private, no-store" } });
  } catch {
    return json({ error: "Try again in a minute" }, 502);
  }
}
