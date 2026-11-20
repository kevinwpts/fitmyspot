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

  // Verktygslådan: ladda ner filer med samma bevis som kapitlen
  document.addEventListener("click", async (ev) => {
    const b = ev.target.closest("button[data-file]"); if (!b) return;
    const t = (() => { const s = get("bp_token", null); return s && s.exp > Date.now() ? s.t : null; })();
    const ss = get("bp_sess", []);
    const q = new URLSearchParams({ f: b.dataset.file });
    if (!t && ss.length) q.set("session_id", ss[ss.length - 1]);
    const old = b.textContent; b.disabled = true; b.textContent = "Downloading…";
    try {
      const r = await fetch("/api/file?" + q, { headers: t ? { authorization: "Bearer " + t } : {} });
      if (!r.ok) throw r.status;
      const url = URL.createObjectURL(await r.blob());
      const a = document.createElement("a"); a.href = url; a.download = b.dataset.file; document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 4000);
      b.textContent = "Downloaded ✓"; window.track && window.track("download", b.dataset.file);
    } catch (e) {
      b.textContent = e === 401 || e === 403 ? "Log in on My guides first" : "Try again";
    } finally { b.disabled = false; setTimeout(() => { b.textContent = old; }, 4000); }
  });

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
