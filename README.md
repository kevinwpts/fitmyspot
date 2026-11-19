# boredprinter.com

Guides on making money with a 3D printer. Static site + 3 small Vercel functions.

- Content: `content/guides/*.md` (free + premium), `content/pages/*.md`
- Design: `site/site.css`, `site/site.js`, `site/*.html` (calculator, library, thanks)
- Build: `python3 tools/build.py` → writes `public/` (commit the output)
- Payments: Stripe Payment Links (Managed Payments). Put links in `site/site.json`.
  After-payment redirect: `https://boredprinter.com/thanks?session_id={CHECKOUT_SESSION_ID}`
  Product names in Stripe must contain "Playbook", "Design" or "Bundle".
- Env on Vercel: `STRIPE_SECRET_KEY` (restricted key, read Checkout Sessions)
- PDFs for sale: `private/guides/` (never public)
- Email list: Supabase table `subscribers` (via RPC `subscribe`)

Old photo app: branch `archive/photo-app-2026-11`.
