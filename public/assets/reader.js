// Läsläge: låser upp kapitel för köpare och markerar lästa kapitel
(() => {
  const $ = (id) => document.getElementById(id);
  const get = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
  const set = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };

  // Lästa kapitel får en bock i listan
  const read = get("bp_read", {});
  const cur = document.querySelector(".rtoc a[aria-current]");
  const mark = () => { const k = location.pathname; read[k] = 1; set("bp_read", read); };
  document.querySelectorAll(".rtoc a").forEach((a) => { if (read[a.getAttribute("href")]) a.classList.add("done"); });
  // Mobil: stäng listan som standard
  if (matchMedia("(max-width: 899px)").matches) document.querySelector(".rtoc")?.removeAttribute("open");

  const body = $("chBody");
  if (!body) { // gratiskapitel
    const end = document.querySelector(".rnav"); if (end && "IntersectionObserver" in window) new IntersectionObserver((es) => es[0].isIntersecting && mark()).observe(end);
    return;
  }
  const tok = (() => { const s = get("bp_token", null); return s && s.exp > Date.now() ? s.t : null; })();
  const sess = get("bp_sess", []);
  if (!tok && !sess.length) return; // inte köpt/inloggad → låsrutan syns
  $("chLock").hidden = true; $("chLoad").hidden = false;
  const q = new URLSearchParams({ g: body.dataset.g, c: body.dataset.c });
  if (!tok && sess.length) q.set("session_id", sess[sess.length - 1]);
  fetch("/api/chapter?" + q, { headers: tok ? { authorization: "Bearer " + tok } : {} })
    .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
    .then((d) => {
      body.innerHTML = d.html; body.hidden = false; $("chLoad").hidden = true;
      const end = document.querySelector(".rnav"); if (end && "IntersectionObserver" in window) new IntersectionObserver((es) => es[0].isIntersecting && mark()).observe(end);
    })
    .catch(() => { $("chLoad").hidden = true; $("chLock").hidden = false; });
})();
