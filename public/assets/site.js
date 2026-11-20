// boredprinter: delad JS för alla sidor (liten, inga bibliotek)
(() => {
  const SB = "https://rcntkzrbanwigypkumvd.supabase.co", KEY = "sb_publishable_Eoce1JVPaM-SgVSllLbi4g_ZiTaGejr";
  const $ = (s, r = document) => r.querySelector(s);
  window.bp = { SB, KEY };

  // Inloggning: ger en giltig token, förnyar den tyst när den gått ut (så man slipper logga in igen)
  window.bpToken = async () => {
    let s; try { s = JSON.parse(localStorage.getItem("bp_token") || "null"); } catch { return null; }
    if (!s) return null;
    if (s.exp > Date.now() + 60000) return s.t;
    if (!s.r) return null;
    try {
      const r = await fetch(`${SB}/auth/v1/token?grant_type=refresh_token`, { method: "POST", headers: { apikey: KEY, "content-type": "application/json" }, body: JSON.stringify({ refresh_token: s.r }) });
      if (!r.ok) throw 0;
      const d = await r.json();
      localStorage.setItem("bp_token", JSON.stringify({ t: d.access_token, r: d.refresh_token, exp: Date.now() + (d.expires_in || 3600) * 1000 }));
      return d.access_token;
    } catch { try { localStorage.removeItem("bp_token"); } catch {} return null; }
  };

  // Inloggningslänk från mejlet landar med #access_token → spara och gå till My guides
  if (location.hash.includes("access_token=")) {
    const p = new URLSearchParams(location.hash.slice(1));
    try { localStorage.setItem("bp_token", JSON.stringify({ t: p.get("access_token"), r: p.get("refresh_token"), exp: Date.now() + (+p.get("expires_in") || 3600) * 1000 })); } catch {}
    history.replaceState(null, "", location.pathname);
    if (location.pathname !== "/library") location.href = "/library";
  }

  // Enkel statistik utan cookies: sidvisningar, klick på knappar, anmälningar
  const noTrack = (() => { try { if (location.search.includes("notrack")) localStorage.setItem("bp_nt", "1"); return localStorage.getItem("bp_nt") === "1"; } catch { return false; } })();
  const sid = (() => { try { let s = sessionStorage.getItem("bp_sid"); if (!s) { s = Math.random().toString(36).slice(2, 10); sessionStorage.setItem("bp_sid", s); } return s; } catch { return null; } })();
  const src = (() => { const u = new URLSearchParams(location.search).get("utm_source"); if (u) return u.slice(0, 40); try { const h = document.referrer && new URL(document.referrer).hostname; return h && h !== location.hostname ? h.replace(/^www\./, "").replace(/^l\./, "").slice(0, 60) : null; } catch { return null; } })();
  window.track = (name, path) => {
    if (noTrack || navigator.webdriver || /bot|crawl|spider|preview/i.test(navigator.userAgent)) return;
    fetch(`${SB}/rest/v1/rpc/track`, { method: "POST", keepalive: true, headers: { apikey: KEY, authorization: `Bearer ${KEY}`, "content-type": "application/json" },
      body: JSON.stringify({ p_name: name, p_path: (path || location.pathname).slice(0, 200), p_ref: src, p_mobile: matchMedia("(pointer: coarse)").matches, p_sid: sid }) }).catch(() => {});
  };
  track("view");
  document.addEventListener("click", (e) => { const a = e.target.closest("a.btn, button.btn, a.more, .card"); if (a) track("click", (a.getAttribute("href") || a.textContent.trim().slice(0, 40)) + " @" + location.pathname); });

  // Header får kant när man scrollar
  const top = $(".top");
  if (top) { const f = () => top.classList.toggle("sc", scrollY > 8); addEventListener("scroll", f, { passive: true }); f(); }

  window.toast = (m) => { let t = $(".toast"); if (!t) { t = document.createElement("div"); t.className = "toast"; t.setAttribute("role", "status"); document.body.append(t); } t.textContent = m; t.hidden = false; clearTimeout(t._h); t._h = setTimeout(() => (t.hidden = true), 3200); };

  // E-postformulär (checklista / väntelista)
  document.querySelectorAll("form.sform[data-src]").forEach((f) => {
    f.addEventListener("submit", async (e) => {
      e.preventDefault();
      const inp = f.querySelector("input[type=email]"), btn = f.querySelector("button"), err = f.querySelector(".err");
      const email = inp.value.trim();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { err.textContent = "Please enter a valid email."; err.hidden = false; inp.focus(); return; }
      err.hidden = true; btn.disabled = true; btn.textContent = "Sending…";
      try {
        const r = await fetch(`${SB}/rest/v1/rpc/subscribe`, { method: "POST", headers: { apikey: KEY, authorization: `Bearer ${KEY}`, "content-type": "application/json" }, body: JSON.stringify({ p_email: email, p_source: f.dataset.src || "site" }) });
        if (!r.ok) throw 0;
        f.innerHTML = f.dataset.ok; track("signup", f.dataset.src);
      } catch { btn.disabled = false; btn.textContent = f.dataset.btn || "Send"; err.textContent = "Something went wrong. Try again."; err.hidden = false; }
    });
  });

  // Uppgifter i "Your task"-rutor: bocka av, sparas på enheten
  const TK = "bp_tasks";
  const tget = () => { try { return JSON.parse(localStorage.getItem(TK) || "{}"); } catch { return {}; } };
  const tsync = () => {
    const all = tget();
    document.querySelectorAll(".dobox").forEach((box, bi) => {
      const key = location.pathname + "#" + bi, done = all[key] || [];
      const cbs = [...box.querySelectorAll(".dock")];
      cbs.forEach((c, i) => { c.checked = done.includes(i); c.closest("li").classList.toggle("done", c.checked); });
      const n = cbs.filter((c) => c.checked).length, p = box.querySelector(".dop");
      if (p) p.textContent = n ? (n === cbs.length ? " · All done ✓" : ` · ${n} of ${cbs.length} done`) : "";
      box.classList.toggle("alldone", n > 0 && n === cbs.length);
    });
    const days = [...document.querySelectorAll(".dayck")], dd = all[location.pathname + "#days"] || [];
    days.forEach((c, i) => { c.checked = dd.includes(i); c.closest("li").classList.toggle("done", c.checked); });
    const dp = document.querySelector(".dayprog");
    if (dp && days.length) { const n = days.filter((c) => c.checked).length; dp.textContent = `${n} of ${days.length} days done`; dp.style.setProperty("--p", (n / days.length * 100) + "%"); }
  };
  document.addEventListener("change", (e) => {
    if (e.target.closest(".dayck")) {
      const all = tget(); all[location.pathname + "#days"] = [...document.querySelectorAll(".dayck")].map((x, i) => (x.checked ? i : -1)).filter((i) => i >= 0);
      try { localStorage.setItem(TK, JSON.stringify(all)); } catch {}
      return tsync();
    }
    const c = e.target.closest(".dock"); if (!c) return;
    const box = c.closest(".dobox"), bi = [...document.querySelectorAll(".dobox")].indexOf(box);
    const key = location.pathname + "#" + bi, all = tget();
    all[key] = [...box.querySelectorAll(".dock")].map((x, i) => (x.checked ? i : -1)).filter((i) => i >= 0);
    try { localStorage.setItem(TK, JSON.stringify(all)); } catch {}
    tsync();
    if (box.classList.contains("alldone")) {
      try { const r = JSON.parse(localStorage.getItem("bp_read") || "{}"); r[location.pathname] = 1; localStorage.setItem("bp_read", JSON.stringify(r)); } catch {}
      document.querySelector(`.rtoc a[href="${location.pathname}"]`)?.classList.add("done");
      track("task_done");
    }
  });
  window.bpTasks = tsync; tsync();

  // Innehållsförteckning: markera avsnittet man läser
  const toc = document.querySelectorAll(".toc a[href^='#']");
  if (toc.length && "IntersectionObserver" in window) {
    const map = new Map([...toc].map((a) => [a.getAttribute("href").slice(1), a]));
    const io = new IntersectionObserver((es) => es.forEach((en) => { if (en.isIntersecting) { toc.forEach((a) => a.classList.remove("on")); map.get(en.target.id)?.classList.add("on"); } }), { rootMargin: "-80px 0px -70% 0px" });
    map.forEach((_, id) => { const h = document.getElementById(id); h && io.observe(h); });
  }
})();
