# FitMySpot

Snap a photo of a spot, get 3D print ideas that fit.

- `public/` – the website
- `api/` – Vercel functions (AI analysis, model search, credits)
- `lib/` – shared Supabase helpers

Environment variables (Vercel → Settings → Environment Variables):
- `GEMINI_API_KEY` – Google Gemini key
- `SCAN_KEY` – server key for the credit system (matches Supabase Vault `scan_key`)
