/* NABD web front-end. Renders everything from window.NABD (web/build.py). No number is typed here by hand,
   except the sourced burden facts in the Impact section (research/burden.md, claims ledger section E). */
(() => {
  "use strict";
  const D = window.NABD;
  const HEAD = "NABD-UAE-v1", POOL = "NABD-Pool", PERS = "persistence";
  const store = { get: k => { try { return localStorage.getItem(k); } catch { return null; } }, set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* private mode */ } } };
  const S = { lang: store.get("nabd-lang") || "en", theme: store.get("nabd-theme"), series: "rsv", model: HEAD, shape: "flu",
              decision: "APPROVE", log: [], exw: 1, rp: { src: "heldout", id: null, w: 0, model: null, timer: null }, verify: {} };
  const L = (en, ar) => (S.lang === "ar" ? ar : en);
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  // Round half to even, like the Python that wrote the reports, so 2.25 shows as 2.2 here as it does there.
  const rnd = (x, d) => { const m = 10 ** d, v = Number(x) * m, r = Math.round(v); return ((Math.abs(v % 1) === 0.5 && r % 2 !== 0 ? r - 1 : r) / m).toFixed(d); };
  const f1 = x => (x == null ? "–" : rnd(x, 1));
  const f2 = x => (x == null ? "–" : rnd(x, 2));
  const f3 = x => (x == null ? "–" : rnd(x, 3));
  const less = r => Math.round((1 - r) * 100);
  // Numbers, ranges and signed values stay left-to-right inside Arabic text.
  const ltr = s => `<bdi dir="ltr">${s}</bdi>`;
  const ci = d => ltr(`${f2(d.ci95[0])}–${f2(d.ci95[1])}`);
  const sgn = x => ltr((x > 0 ? "+" : "") + f2(x));
  const date = s => new Date(s + "T00:00:00Z");
  const anchorDay = Lg => { const s = (Lg.anchors || []).slice(-1)[0]?.stamp || ""; return s.length >= 10 ? s.slice(0, 10) : null; };
  const anchorTxt = Lg => (Lg.anchors || []).length
    ? L(`Status: the repository is public on GitHub. On ${dfmt(anchorDay(Lg), { day: "numeric", month: "long", year: "numeric" })} the fingerprints of every lock and ledger round were sent for outside timestamps (FreeTSA, RFC 3161; OpenTimestamps on Bitcoin, which confirms within hours). The receipts are in anchors/. A timestamp proves a file existed by that time; it cannot backdate anything.`,
        `الحالة: المستودع منشور على GitHub. وفي ${dfmt(anchorDay(Lg), { day: "numeric", month: "long", year: "numeric" })} أُرسلت بصمات جميع الأقفال وجولات السجل لختمها زمنياً من جهات خارجية (FreeTSA وفق RFC 3161، وOpenTimestamps على بيتكوين ويكتمل خلال ساعات). والإيصالات في المجلد anchors/. يثبت الختم الزمني أن الملف كان موجوداً بحلول ذلك الوقت، ولا يمكنه أن ينسب إلى أي ملف تاريخاً أسبق.`)
    : L("Status: the repository is public on GitHub, which records when each commit was pushed. The fingerprints are not yet timestamped by an outside service.",
        "الحالة: المستودع منشور على GitHub الذي يسجّل وقت رفع كل تعديل. ولم تُختم البصمات زمنياً من جهة خارجية بعد.");
  const receiptTxt = Lg => {
    const R = Lg.receipt, o = R.rows, n = Lg.n_scored;
    const v = (k, en) => { const x = o[k]; if (!x) return ""; return en
      ? `${k === "rsv" ? "RSV" : "influenza"} ${x.in50 ? "inside its 50% range" : x.in95 ? "inside its 95% range, outside its 50% range" : "outside its 95% range"}`
      : `${k === "rsv" ? "الفيروس المخلوي التنفسي" : "الإنفلونزا"} ${x.in50 ? "داخل نطاق 50%" : x.in95 ? "داخل نطاق 95% وخارج نطاق 50%" : "خارج نطاق 95%"}`; };
    const we = dfmt(R.week_end, { day: "numeric", month: "short" }), is = dfmt(R.issued, { day: "numeric", month: "short" });
    const f = (k, p) => (o[k] ? `${Number(o[k][p]).toFixed(1)}%` : "–");
    return L(`${n} forecast week${n === 1 ? "" : "s"} scored so far. ${R.week} (ending ${we}): WHO published RSV ${f("rsv", "observed")} and influenza ${f("flu", "observed")}. The own-record forecast hashed on ${is} had medians of ${f("rsv", "median")} and ${f("flu", "median")}: ${[v("rsv", 1), v("flu", 1)].filter(Boolean).join("; ")}. One week is a receipt, not evidence. Merkle root of the newest round: `,
      `عدد الأسابيع المقيَّمة حتى الآن ${n}. الأسبوع ${R.week} (المنتهي في ${we}): نشرت المنظمة ${f("rsv", "observed")} للفيروس المخلوي التنفسي و${f("flu", "observed")} للإنفلونزا. وكان وسيط توقع نموذج سجل الدولة الموثَّق في ${is} ‏${f("rsv", "median")} و${f("flu", "median")}: ${[v("rsv", 0), v("flu", 0)].filter(Boolean).join("؛ ")}. أسبوع واحد إيصالٌ لا دليل. جذر ميركل لأحدث جولة: `);
  };
  const dfmt = (s, o = { day: "numeric", month: "short" }) => new Intl.DateTimeFormat(S.lang === "ar" ? "ar-AE-u-nu-latn" : "en-GB", { ...o, timeZone: "UTC" }).format(date(s));
  const cname = c => (D.countries[c] ? D.countries[c][S.lang] : c);
  const season = s => `${s}/${String((s + 1) % 100).padStart(2, "0")}`;
  const sname = s => (s === "rsv" ? L("RSV", "الفيروس المخلوي التنفسي") : L("Influenza", "الإنفلونزا"));
  const mname = k => ({
    pool: L("Pooled model", "النموذج المجمَّع عبر الدول"), local: L("Own-record model", "نموذج سجل الدولة وحدها"),
    pattern: L("Past-season pattern", "نمط المواسم السابقة"), last: L("Repeat last week", "تكرار الأسبوع الماضي"),
  }[k] || k);
  const ev = D.evidence, cur = D.current;
  const chip = (cls, txt) => `<span class="chip ${cls}">${txt}</span>`;
  const CH = {
    pre: () => chip("pre", L("Pre-registered", "مسجّل مسبقاً")), post: () => chip("post", L("Post hoc", "تحليل لاحق")),
    met: () => chip("met", L("Bar met", "تحقّق الهدف")), miss: () => chip("miss", L("Bar not met", "لم يتحقق الهدف")),
    scn: () => chip("scn", L("Scenario", "سيناريو")), wait: () => chip("wait", L("No result yet", "لا نتيجة بعد")),
    retro: () => chip("post", L("Retrospective", "تحليل استعادي")), ill: () => chip("scn", L("Illustrative", "توضيحي")),
  };

  /* ---------------------------------------------------------------- tiny chart kit */
  const lin = (d0, d1, r0, r1) => v => r0 + ((v - d0) / (d1 - d0 || 1)) * (r1 - r0);
  const pth = pts => pts.map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + "," + p[1].toFixed(1)).join("");
  const area = (up, lo) => pth(up) + pth(lo.slice().reverse()).replace(/^M/, "L") + "Z";
  const nice = m => { const s = m <= 12 ? 2 : m <= 30 ? 5 : m <= 60 ? 10 : 20; return Math.ceil(m / s) * s; };
  const yticks = m => { const s = m <= 12 ? 2 : m <= 30 ? 5 : m <= 60 ? 10 : 20; const o = []; for (let v = 0; v <= m; v += s) o.push(v); return o; };

  function fanChart(series, model) {
    const W = 760, H = 350, m = { l: 38, r: 54, t: 16, b: 34 };
    const o = D.observed, n = o.week_end.length, k0 = Math.max(0, n - 15);
    const obs = []; for (let i = k0; i < n; i++) if (o[series][i] != null) obs.push([o.week_end[i], o[series][i]]);
    const fc = (cur.forecasts[model] || {})[series] || [], pe = (cur.forecasts[PERS] || {})[series] || [];
    const other = model === HEAD ? POOL : HEAD, alt = (cur.forecasts[other] || {})[series] || [];
    const card = cur.cards[model][series], thr = Object.keys(card.max_p).map(Number);
    const last = obs[obs.length - 1];
    const t0 = date(obs[0][0]).getTime(), t1 = date(fc.length ? fc[fc.length - 1].te : last[0]).getTime();
    const ymax = nice(Math.max(...obs.map(p => p[1]), ...fc.map(r => r.q["0.975"]), ...pe.map(r => r.q["0.9"]), ...thr) * 1.06);
    const x = s => lin(t0, t1, m.l, W - m.r)(date(s).getTime()), y = lin(0, ymax, H - m.b, m.t);
    const fan = [{ te: last[0], q: Object.fromEntries(["0.025", "0.1", "0.25", "0.5", "0.75", "0.9", "0.975"].map(q => [q, last[1]])) }, ...fc];
    const line = (rows, q) => rows.map(r => [x(r.te), y(r.q[q])]);
    let g = "";
    for (const v of yticks(ymax)) g += `<line class="gridl" x1="${m.l}" x2="${W - m.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${m.l - 8}" y="${y(v) + 4}" text-anchor="end">${v}%</text>`;
    for (let i = 0; i < obs.length - 1; i += 3) g += `<text x="${x(obs[i][0])}" y="${H - 10}" text-anchor="middle">${dfmt(obs[i][0])}</text>`;
    for (const r of fc) g += `<text x="${x(r.te)}" y="${H - 10}" text-anchor="middle" class="lab">${dfmt(r.te, { day: "numeric" })}</text>`;
    for (const T of thr) g += `<line class="thr" x1="${m.l}" x2="${W - m.r}" y1="${y(T)}" y2="${y(T)}"/><text class="thr-t" x="${W - m.r + 6}" y="${y(T) + 4}">${T}%</text>`;
    const xi = x(cur.issue_date);
    g += `<line class="issue" x1="${xi}" x2="${xi}" y1="${m.t}" y2="${H - m.b}"/><text x="${xi}" y="${m.t - 4}" text-anchor="middle">${L("issued", "الإصدار")}</text>`;
    g += `<path class="b95" d="${area(line(fan, "0.975"), line(fan, "0.025"))}"/><path class="b80" d="${area(line(fan, "0.9"), line(fan, "0.1"))}"/><path class="b50" d="${area(line(fan, "0.75"), line(fan, "0.25"))}"/>`;
    if (pe.length) g += `<path class="pers-l" d="${pth([[x(last[0]), y(last[1])], ...line(pe, "0.5")])}"/>`;
    if (alt.length) g += `<path class="alt-l" d="${pth([[x(last[0]), y(last[1])], ...line(alt, "0.5")])}"/>`;
    g += `<path class="obs-l" d="${pth(obs.map(p => [x(p[0]), y(p[1])]))}"/><path class="med-l" d="${pth(line(fan, "0.5"))}"/>`;
    g += obs.slice(-6).map(p => `<circle class="dot" r="3" cx="${x(p[0])}" cy="${y(p[1])}"><title>${dfmt(p[0])}: ${f1(p[1])}%</title></circle>`).join("");
    g += fc.map(r => `<circle class="dot-t" r="4" cx="${x(r.te)}" cy="${y(r.q["0.5"])}"><title>${dfmt(r.te)}: ${f1(r.q["0.5"])}% (80%: ${f1(r.q["0.1"])}–${f1(r.q["0.9"])})</title></circle>`).join("");
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(sname(series))} ${L("forecast fan chart", "مخطط نطاق التوقع")}">${g}</svg>`;
  }

  function shapeChart(series) {
    const W = 760, H = 300, m = { l: 38, r: 16, t: 14, b: 30 };
    const o = D.observed, by = {};
    o.week_end.forEach((_, i) => { const v = o[series][i]; if (v == null) return; const w = o.iso_week[i]; (by[o.season[i]] ||= []).push([w >= 27 ? w - 27 : w + 26, v]); });
    const seasons = Object.keys(by).map(Number).sort(), curS = seasons[seasons.length - 1];
    const ymax = nice(Math.max(...seasons.flatMap(s => by[s].map(p => p[1]))) * 1.05);
    const x = lin(0, 52, m.l, W - m.r), y = lin(0, ymax, H - m.b, m.t);
    const months = L(["Jul", "Sep", "Nov", "Jan", "Mar", "May"], ["يوليو", "سبتمبر", "نوفمبر", "يناير", "مارس", "مايو"]);
    let g = "";
    for (const v of yticks(ymax)) g += `<line class="gridl" x1="${m.l}" x2="${W - m.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${m.l - 8}" y="${y(v) + 4}" text-anchor="end">${v}%</text>`;
    months.forEach((mo, i) => { g += `<text x="${x(i * 8.7 + 1)}" y="${H - 9}" text-anchor="middle">${mo}</text>`; });
    const tones = ["#b9b2a2", "#9aa7ad", "#c79a6b", "#7f9c8b", "#a58fb0"];
    seasons.forEach((s, i) => {
      const pts = by[s].sort((a, b) => a[0] - b[0]).map(p => [x(p[0]), y(p[1])]), isCur = s === curS;
      const pk = by[s].reduce((a, b) => (b[1] > a[1] ? b : a));
      g += `<path d="${pth(pts)}" fill="none" stroke="${isCur ? "var(--teal)" : tones[i % tones.length]}" stroke-width="${isCur ? 3 : 1.7}" stroke-linejoin="round" opacity="${isCur ? 1 : 0.9}"><title>${season(s)}</title></path>`;
      g += `<circle cx="${x(pk[0])}" cy="${y(pk[1])}" r="${isCur ? 4.5 : 3.2}" fill="${isCur ? "var(--teal)" : tones[i % tones.length]}"/><text x="${x(pk[0]) + (isCur ? -9 : 0)}" y="${y(pk[1]) - (isCur ? -4 : 9)}" text-anchor="${isCur ? "end" : "middle"}" class="${isCur ? "val" : ""}">${season(s)}</text>`;
    });
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${L("UAE seasons overlaid", "مواسم الإمارات متراكبة")}">${g}</svg>`;
  }

  function forest() {
    const P = ev.pool, rows = P.per_country, rh = 25, W = 760, ml = 150, mr = 24, top = 26, H = top + rows.length * rh + 58;
    const x = lin(0.35, 1.1, ml, W - mr);
    let g = "";
    for (const v of [0.4, 0.6, 0.8, 1.0]) g += `<line class="gridl" x1="${x(v)}" x2="${x(v)}" y1="${top - 6}" y2="${H - 26}"/><text x="${x(v)}" y="${H - 8}" text-anchor="middle">${v.toFixed(1)}</text>`;
    g += `<line class="one" x1="${x(1)}" x2="${x(1)}" y1="${top - 10}" y2="${H - 26}"/><text x="${x(1)}" y="${top - 14}" text-anchor="middle" class="lab">${L("same error", "الخطأ نفسه")}</text>`;
    g += `<text x="${x(0.36)}" y="${top - 14}" class="lab">${L("← pooled model better", "← النموذج المجمَّع أفضل")}</text>`;
    rows.forEach((r, i) => {
      const yy = top + i * rh + rh / 2;
      g += `<text x="${ml - 12}" y="${yy + 4}" text-anchor="end" class="lab">${esc(cname(r.c))}</text><line class="lolli" x1="${x(r.ratio)}" x2="${x(1)}" y1="${yy}" y2="${yy}"/>` +
        `<circle class="lolli-d" r="5" cx="${x(r.ratio)}" cy="${yy}"><title>${esc(cname(r.c))}: ${L("pooled", "المجمَّع")} ${f2(r.pool)} · ${L("own-record", "سجل الدولة")} ${f2(r.local)} · ${r.n} ${L("forecasts", "توقعاً")}</title></circle>` +
        `<text x="${x(r.ratio) - 10}" y="${yy + 4}" text-anchor="end" class="val">${f2(r.ratio)}</text>`;
    });
    const yy = top + rows.length * rh + 16, p = P.primary;
    g += `<line x1="${ml - 140}" x2="${W - mr}" y1="${yy - 14}" y2="${yy - 14}" class="ax"/><text x="${ml - 12}" y="${yy + 4}" text-anchor="end" class="val">${L("All 18 (95% CI)", "الدول الـ18 (فاصل 95%)")}</text>` +
      `<line x1="${x(p.ci95[0])}" x2="${x(p.ci95[1])}" y1="${yy}" y2="${yy}" stroke="var(--ink)" stroke-width="2.5"/>` +
      `<path d="M${x(p.rel_wis)},${yy - 8}l7,8l-7,8l-7,-8z" fill="var(--ink)"/><text x="${x(p.ci95[0]) - 10}" y="${yy + 4}" text-anchor="end" class="val">${f2(p.rel_wis)}</text>`;
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${L("Forecast error ratio per held-out country", "نسبة خطأ التوقع لكل دولة")}">${g}</svg>`;
  }

  function hbars(items, { unit = "", max = null, stack = false } = {}) {
    const W = 760, rh = 40, ml = 200, mr = 60, H = items.length * rh + 30;
    const mx = max || Math.max(...items.map(d => (stack ? d.a + d.b : d.v))) * 1.05, x = lin(0, mx, ml, W - mr);
    let g = "";
    items.forEach((d, i) => {
      const yy = i * rh + 8, tot = stack ? (d.t ?? d.a + d.b) : d.v;
      g += `<text x="${ml - 12}" y="${yy + 17}" text-anchor="end" class="${d.hi ? "val" : "lab"}">${esc(d.label)}</text>`;
      if (stack) g += `<rect class="barm" x="${x(0)}" y="${yy}" width="${x(d.a) - x(0)}" height="22" rx="3"><title>${L("missed", "فائتة")}: ${f1(d.a)}</title></rect><rect class="barw" x="${x(d.a)}" y="${yy}" width="${x(tot) - x(d.a)}" height="22" rx="3"><title>${L("wasted", "مهدورة")}: ${f1(d.b)}</title></rect>`;
      else g += `<rect class="${d.hi ? "barp" : "barn"}" x="${x(0)}" y="${yy}" width="${x(d.v) - x(0)}" height="22" rx="3"/>`;
      g += `<text x="${x(tot) + 8}" y="${yy + 16}" class="val">${stack ? f1(tot) : f2(tot)}${unit}</text>`;
    });
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img">${g}</svg>`;
  }

  function replayChart(u, w, mk) {
    const W = 760, H = 330, m = { l: 38, r: 54, t: 14, b: 64 }, n = u.te.length, M = u.models[mk];
    const ymax = nice(Math.max(...u.obs, ...M.hi, u.T) * 1.05), x = lin(0, n - 1, m.l, W - m.r), y = lin(0, ymax, H - m.b, m.t);
    let g = "";
    for (const v of yticks(ymax)) g += `<line class="gridl" x1="${m.l}" x2="${W - m.r}" y1="${y(v)}" y2="${y(v)}"/><text x="${m.l - 8}" y="${y(v) + 4}" text-anchor="end">${v}%</text>`;
    for (let i = 0; i < n; i += Math.ceil(n / 8)) g += `<text x="${x(i)}" y="${H - 46}" text-anchor="middle">${dfmt(u.te[i])}</text>`;
    g += `<line class="thr" x1="${m.l}" x2="${W - m.r}" y1="${y(u.T)}" y2="${y(u.T)}"/><text class="thr-t" x="${W - m.r + 6}" y="${y(u.T) + 4}">${f1(u.T)}%</text>`;
    g += `<path class="obs-f" d="${pth(u.obs.map((v, i) => [x(i), y(v)]))}"/>`;
    const idx = [...Array(w + 1).keys()];
    if (w > 0) g += `<path class="b80" d="${area(idx.map(i => [x(i), y(M.hi[i])]), idx.map(i => [x(i), y(M.lo[i])]))}"/><path class="med-l" style="stroke-width:1.6" d="${pth(idx.map(i => [x(i), y(M.med[i])]))}"/>`;
    g += `<path class="obs-l" d="${pth(idx.map(i => [x(i), y(u.obs[i])]))}"/><circle class="dot" r="4" cx="${x(w)}" cy="${y(u.obs[w])}"/>`;
    g += `<line class="issue" x1="${x(w)}" x2="${x(w)}" y1="${m.t}" y2="${H - m.b}"/>`;
    const bw = Math.max(3, (W - m.l - m.r) / n - 2);
    for (const i of idx) {
      const surge = u.obs[i] > u.T, ro = !!M.roster[i];
      if (!surge && !ro) continue;
      const col = ro && surge ? "var(--teal)" : ro ? "var(--amber)" : "var(--rose)";
      const tip = ro && surge ? L("rostered, surge came", "جُدولت وحدثت الموجة") : ro ? L("rostered, no surge (wasted)", "جُدولت بلا موجة (مهدورة)") : L("surge, not rostered (missed)", "موجة بلا جدولة (فائتة)");
      g += `<rect x="${x(i) - bw / 2}" y="${H - 34}" width="${bw}" height="12" rx="2" fill="${col}"><title>${dfmt(u.te[i])}: ${tip}</title></rect>`;
    }
    g += `<text x="${m.l}" y="${H - 6}" style="font-size:10px">${L("roster calls and surge weeks so far", "قرارات المناوبة وأسابيع الموجة حتى الآن")}</text>`;
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img">${g}</svg>`;
  }

  /* ---------------------------------------------------------------- sections */
  function nav() {
    const links = [["week", L("This week", "هذا الأسبوع")], ["science", L("The science", "العلم")], ["decisions", L("Decisions", "القرارات")],
                   ["results", L("All results", "كل النتائج")], ["brief", L("The brief", "متطلبات التحدي")], ["ledger", L("Ledger", "السجل")], ["impact", L("Impact", "الأثر")]];
    return `<div class="wrap"><a class="brand" href="#top" aria-label="NABD"><svg viewBox="0 0 34 22"><path d="M1 12h7l3-8 5 15 4-11 2 4h11" fill="none" stroke="var(--teal)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg><span>NABD</span><span class="ar">نبض</span></a>
      <nav>${links.map(([h, l]) => `<a href="#${h}">${l}</a>`).join("")}</nav>
      <div class="tools"><button class="iconbtn" data-act="lang" aria-label="Language">${S.lang === "en" ? "العربية" : "English"}</button>
      <button class="iconbtn" data-act="theme" aria-label="${L("Light or dark", "فاتح أو داكن")}">◐</button></div></div>`;
  }

  function tile(series) {
    const c = cur.cards[HEAD][series], T = Object.keys(c.max_p).map(Number).sort((a, b) => a - b)[0], p = c.max_p[String(T)];
    return `<div class="tile"><div class="name">${sname(series)}</div><div class="big num">${f1(c.last)}%<small>${L("last published week", "آخر أسبوع منشور")}</small></div>
      <div class="state">${esc(c.band ? c.band.label[S.lang] : "")}</div>
      <div class="meter" aria-hidden="true"><i style="width:${Math.round(p * 100)}%"></i></div>
      <div class="meter-l"><span>${L(`Chance above ${T}% in the next two weeks`, `احتمال تجاوز ${T}% خلال الأسبوعين المقبلين`)}</span><b class="num">${Math.round(p * 100)}%</b></div></div>`;
  }

  function hero() {
    const P = ev.pool, fr = D.freshness, rd = (D.ledger.rounds.find(r => r.file === cur.round_file) || {}).round || "";
    return `<section class="hero" id="top"><svg class="pulse" viewBox="0 0 1440 180" preserveAspectRatio="none" aria-hidden="true"><path d="M0 120h260l22-14 18 30 24-92 26 118 20-56 16 14h190l18-10 16 22 22-70 24 92 18-44 14 10h230l20-12 18 26 22-84 26 108 18-50 16 12h366"/></svg>
      <div class="wrap hero-grid"><div>
        <div class="eyebrow">${L("RSV and influenza forecasts for the UAE", "توقعات الفيروس المخلوي التنفسي والإنفلونزا في الإمارات")}</div>
        <h1>${L("Building the UAE's resilience to respiratory seasons, <em>one checkable forecast a week</em>.", "تعزيز صمود الإمارات أمام المواسم التنفسية، <em>بتوقّع أسبوعي يمكن التحقق منه</em>.")}</h1>
        <p class="lede">${L("NABD turns the UAE's own surveillance records into three-week forecasts of RSV and influenza, scored the way the CDC's FluSight hub scores forecasts. Each week becomes one proposed action, and a named person decides, supporting the national teams who protect children and communities.",
          "يحوّل نبض سجلات الرصد الإماراتية إلى توقعات لثلاثة أسابيع للفيروس المخلوي التنفسي والإنفلونزا، تُقيَّم بالطريقة التي يقيّم بها مركز FluSight التابع لمراكز مكافحة الأمراض الأمريكية توقعاته. وكل أسبوع يتحوّل ذلك إلى إجراء مقترح واحد يقرّره شخص مسمّى، دعماً للفرق الوطنية التي تحمي الأطفال والمجتمع.")}</p>
        <div class="cta"><a class="btn primary" href="#week">${L("See this week's card", "بطاقة هذا الأسبوع")}</a><a class="btn" href="#science">${L("How it was tested", "كيف اختُبر")}</a></div>
        <div class="trio">
          <div><div class="k num">${less(P.primary.rel_wis)}%</div><div class="l">${L("less influenza forecast error than a model built on each country's own record", "خطأ أقل في توقع الإنفلونزا من نموذج مبني على سجل كل دولة وحدها")}</div></div>
          <div><div class="k num">${esc(P.primary.unit_wins.replace("/", L(" of ", " من ")))}</div><div class="l">${L("countries better, with none of their data opened before the test was locked", "دولة أفضل، ولم تُفتح بيانات أيٍّ منها قبل تثبيت الاختبار")}</div></div>
          <div><div class="k num">${less(P.short.rel_wis)}%</div><div class="l">${L("less where the country's record is short, which is the UAE's position", "أقل حين يكون سجل الدولة قصيراً، وهو وضع الإمارات")}</div></div>
        </div></div>
        <aside class="now"><h3><span class="live-dot"></span>${L("This week in the UAE", "هذا الأسبوع في الإمارات")}</h3>
          ${tile("rsv")}${tile("flu")}
          <div class="fresh">${L(`WHO data through ${fr.last_week} · issued ${dfmt(cur.issue_date, { day: "numeric", month: "short", year: "numeric" })} · ledger round ${rd}`,
            `بيانات منظمة الصحة العالمية حتى ${fr.last_week} · صدر في ${dfmt(cur.issue_date, { day: "numeric", month: "short", year: "numeric" })} · جولة السجل ${rd}`)}</div>
        </aside></div></section>`;
  }

  function how() {
    const steps = [
      [L("Reads", "يقرأ"), L("Each week NABD reads the UAE's latest sentinel results from WHO FluNet: the share of samples positive for RSV and for influenza.", "كل أسبوع يقرأ نبض أحدث نتائج الرصد في الإمارات من WHO FluNet: نسبة العيّنات الإيجابية للفيروس المخلوي التنفسي وللإنفلونزا.")],
      [L("Forecasts", "يتوقّع"), L("It forecasts the next three weeks as a range, and gives the chance of crossing each pressure threshold.", "يتوقّع الأسابيع الثلاثة المقبلة على هيئة نطاق، ويعطي احتمال تجاوز كل عتبة ضغط.")],
      [L("Proposes", "يقترح"), L("The forecast becomes one proposed action per role. A named person approves, modifies or dismisses it, and the decision is logged.", "يتحوّل التوقع إلى إجراء مقترح واحد لكل دور. يعتمده شخص مسمّى أو يعدّله أو يرفضه، ويُسجَّل القرار.")],
      [L("Seals", "يوثّق"), L("Each forecast file is fingerprinted before WHO publishes the week it covers, then scored against that week when it arrives.", "يحصل كل ملف توقع على بصمة رقمية قبل أن تنشر المنظمة بيانات أسبوعه، ثم يُقيَّم مقابل ذلك الأسبوع عند صدوره.")],
    ];
    return `<section id="how"><div class="wrap"><div class="sec-head"><div class="eyebrow">${L("How NABD works", "كيف يعمل نبض")}</div>
      <h2>${L("From WHO's weekly numbers to one decision.", "من أرقام المنظمة الأسبوعية إلى قرار واحد.")}</h2></div>
      <div class="grid g4">${steps.map((s, i) => `<div class="card flat"><div class="step-n num">${i + 1}</div><h3>${s[0]}</h3><p>${s[1]}</p></div>`).join("")}</div></div></section>`;
  }

  function problem() {
    const u = ev.uae;
    return `<section class="alt" id="problem"><div class="wrap">
      <div class="sec-head"><div class="eyebrow">${L("The Monday decision", "قرار يوم الاثنين")}</div>
        <h2>${L("UAE seasons change timing and shape from year to year, and four seasons are not enough to learn one.", "يتغيّر توقيت المواسم وشكلها في الإمارات من عام إلى عام، وأربعة مواسم لا تكفي لتعلّم شكل الموسم.")}</h2>
        <p>${L("Every winter week a bed manager, a public-health duty officer and an immunisation lead plan the next three weeks from last week's numbers and last year's pattern. The lines below are WHO's UAE sentinel record: each season peaks at a different time and height.",
          "في كل أسبوع شتوي يخطط مدير الأسرّة وضابط مناوبة الصحة العامة ومسؤول التطعيم للأسابيع الثلاثة المقبلة اعتماداً على أرقام الأسبوع الماضي ونمط العام الماضي. الخطوط أدناه هي سجل الرصد في الإمارات لدى منظمة الصحة العالمية: كل موسم يبلغ ذروته في توقيت وارتفاع مختلفين.")}</p></div>
      <div class="grid g-32"><div class="card"><div class="bar"><div class="seg" role="group">
          <button data-act="shape" data-v="flu" aria-pressed="${S.shape === "flu"}">${sname("flu")}</button><button data-act="shape" data-v="rsv" aria-pressed="${S.shape === "rsv"}">${sname("rsv")}</button></div>
          <span class="sub">${L("% of sentinel samples positive, by week of season", "نسبة العيّنات الإيجابية في الرصد، بحسب أسبوع الموسم")}</span></div>
          <div id="shape">${shapeChart(S.shape)}</div><div class="src">${L("Source: WHO FluNet, UAE sentinel sites. Bold line: this season.", "المصدر: WHO FluNet، مواقع الرصد في الإمارات. الخط العريض: الموسم الحالي.")}</div></div>
        <div class="grid" style="align-content:start">
          <div class="card flat"><div class="chips">${CH.retro()}</div><div class="kpi slate num">${f2(u.flu.rel_wis)}</div>
            <p style="margin-top:8px">${L("Forecast error of a model built only on the UAE's own record, relative to simply repeating last week. 1.00 is a tie. On four seasons, that is the measured result.",
              "خطأ توقع نموذج مبني على سجل الإمارات وحده، مقارنة بتكرار الأسبوع الماضي. القيمة 1.00 تعني التعادل. وهذه هي النتيجة المقيسة على أربعة مواسم.")}</p>
            <div class="src">results/uae/SUMMARY-v2.md · ${L("95% interval", "فاصل 95%")} ${ltr(f2(u.flu.ci95[0]) + "–" + f2(u.flu.ci95[1]))}</div></div>
          <div class="note">${L("That tie is why NABD also learns from how seasons unfold in 46 countries. A short record cannot teach a model what a season looks like, and the UAE's own record grows stronger every week it is kept.",
            "هذا التعادل هو سبب تعلّم نبض أيضاً من مسار المواسم في 46 دولة. السجل القصير لا يعلّم النموذج شكل الموسم، وسجل الإمارات يزداد قوة مع كل أسبوع يُحفظ فيه.")}</div>
        </div></div></div></section>`;
  }

  function cardBody() {
    const c = cur.cards[S.model][S.series], hasPool = !!cur.cards[POOL], pb = D.playbook;
    const thr = Object.keys(c.max_p);
    const rows = c.exceed.map(e => `<tr><td>${esc(e.week[S.lang])}<div class="sub" style="margin:0">${esc(e.horizon[S.lang])}</div></td>${thr.map(T => `<td class="r num"><b>${esc(e.p[T])}</b></td>`).join("")}</tr>`).join("");
    const b = c.band;
    return `<div class="bar"><div class="seg" role="group"><button data-act="series" data-v="rsv" aria-pressed="${S.series === "rsv"}">${sname("rsv")}</button><button data-act="series" data-v="flu" aria-pressed="${S.series === "flu"}">${sname("flu")}</button></div>
        ${hasPool ? `<div class="seg sp" role="group"><button data-act="model" data-v="${HEAD}" aria-pressed="${S.model === HEAD}">${L("Headline model", "النموذج الرئيسي")}</button><button data-act="model" data-v="${POOL}" aria-pressed="${S.model === POOL}">${L("Pooled challenger", "المنافس المجمَّع")}</button></div>` : ""}</div>
      ${S.model === POOL ? `<p class="note warn" style="margin-bottom:16px">${L("Challenger view. The hashed headline forecast is still the own-record model; the pooled model runs beside it until the locked UAE test reports.", "عرض النموذج المنافس. التوقع الرئيسي الموثّق ما زال نموذج سجل الدولة؛ ويعمل النموذج المجمَّع إلى جانبه حتى تظهر نتيجة اختبار الإمارات المثبّت.")}</p>` : ""}
      <div class="grid g-32"><div class="card">${fanChart(S.series, S.model)}
          <div class="legend"><span><i class="obs"></i>${L("WHO published", "المنشور من المنظمة")}</span><span><i></i>${L("forecast median", "وسيط التوقع")}</span><span><i class="band"></i>${L("50 / 80 / 95% ranges", "نطاقات 50 / 80 / 95%")}</span>
            <span><i class="dash"></i>${L("repeat last week", "تكرار الأسبوع الماضي")}</span>${hasPool ? `<span><i class="amber"></i>${S.model === HEAD ? L("pooled challenger median", "وسيط المنافس المجمَّع") : L("headline model median", "وسيط النموذج الرئيسي")}</span>` : ""}<span><i class="rose"></i>${L("pressure thresholds", "عتبات الضغط")}</span></div>
          <p class="sub" style="margin-top:12px">${esc(c.sentence[S.lang])}</p></div>
        <div class="grid" style="align-content:start">
          <div class="card"><div class="chips">${CH.ill()}</div><h3>${L("Chance of crossing each threshold", "احتمال تجاوز كل عتبة")}</h3>
            <div class="tablewrap"><table><thead><tr><th>${L("Week", "الأسبوع")}</th>${thr.map(T => `<th class="r">&gt; ${T}%</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table></div>
            <div class="src">${L(`A threshold counts when the chance reaches ${Math.round(c.p_act * 100)}% in any future week.`, `تُحتسب العتبة عندما يبلغ الاحتمال ${Math.round(c.p_act * 100)}% في أي أسبوع مقبل.`)}</div></div>
          <div class="card"><h3>${L("Proposed action", "الإجراء المقترح")}</h3>
            ${c.renderable && b ? `<span class="band-pill tier${b.tier}">${esc(b.label[S.lang])}</span><div class="roles">${Object.entries(b.actions).map(([r, a]) => `<div class="role"><b>${esc(pb.roles[r][S.lang])}</b>${esc(a[S.lang])}</div>`).join("")}</div>`
              : `<p class="note bad">${L("Card blocked: the forecast, direction and action did not agree, so nothing is proposed.", "البطاقة محجوبة: لم تتوافق عناصر التوقع والاتجاه والإجراء، فلا يُقترح شيء.")}</p>`}
            <div class="src">${L(`Playbook v${pb.version}: thresholds and wording are placeholders until a clinician and a public-health officer review them.`, `دليل العمل ${pb.version}: العتبات والصياغة مؤقتة إلى أن يراجعها طبيب ومسؤول صحة عامة.`)}</div></div>
        </div></div>`;
  }

  function approval() {
    const pb = D.playbook, c = cur.cards[HEAD][S.series];
    const dec = [["APPROVE", L("Approve", "اعتماد")], ["MODIFY", L("Modify", "تعديل")], ["DISMISS", L("Dismiss", "رفض")]];
    return `<div class="grid g2" style="margin-top:18px"><div class="card"><h3>${L("A named person decides", "القرار لشخص مسمّى")}</h3>
        <p style="margin-bottom:14px">${L("Nothing leaves NABD without a name and a reason. Try it: this page keeps a hash-chained log for this browser session only. The audited log lives in the workbench app.",
          "لا يخرج شيء من نبض بلا اسم وسبب. جرّب: تحتفظ هذه الصفحة بسجل مترابط بالتجزئة لهذه الجلسة فقط. أما السجل المدقَّق ففي تطبيق العمل.")}</p>
        <div class="grid g2" style="gap:12px"><div class="field"><label for="ap-role">${L("Role", "الدور")}</label><select id="ap-role">${Object.entries(pb.roles).map(([k, v]) => `<option value="${k}">${esc(v[S.lang])}</option>`).join("")}</select></div>
          <div class="field"><label for="ap-name">${L("Approver name (required)", "اسم المعتمِد (إلزامي)")}</label><input type="text" id="ap-name" autocomplete="off" maxlength="80"></div></div>
        <div class="field"><label>${L("Decision", "القرار")}</label><div class="seg" role="group">${dec.map(([k, l]) => `<button data-act="decision" data-v="${k}" aria-pressed="${S.decision === k}">${l}</button>`).join("")}</div></div>
        <div class="field"><label for="ap-reason">${L("Reason", "السبب")}</label><select id="ap-reason">${pb.reason_codes.map(r => `<option value="${r.code}">${esc(r[S.lang])}</option>`).join("")}</select></div>
        <button class="btn primary" data-act="record">${L("Record the decision", "سجّل القرار")}</button> <span class="err" id="ap-err" role="alert"></span></div>
      <div class="card"><h3>${L("Session log", "سجل الجلسة")}</h3>
        <p>${L(`For ${sname(S.series)}: ${c.band ? c.band.label[S.lang] : "–"}. Each entry carries the hash of the one before it, so an edit anywhere breaks the chain.`,
          `${sname(S.series)}: ${c.band ? c.band.label[S.lang] : "–"}. يحمل كل قيد تجزئة القيد السابق، فأي تعديل يكسر السلسلة.`)}</p>
        <div class="log" id="ap-log">${S.log.length ? S.log.map(e => `<div class="e"><b>#${e.seq} · ${esc(e.decisionLabel)}</b> · ${esc(e.approver)} · ${esc(e.roleLabel)}<br>${esc(e.band)} · ${esc(e.reasonLabel)}<div class="hash">${e.ts} · ${e.hash.slice(0, 32)}…</div></div>`).join("")
          : `<div class="sub">${L("No decision recorded in this session.", "لم يُسجَّل قرار في هذه الجلسة.")}</div>`}</div></div></div>`;
  }

  const feat = f => ({
    dy1: [L("Momentum: change over the last week", "الزخم: التغيّر خلال الأسبوع الماضي"), L("sentinel positivity · last two weeks", "إيجابية الرصد · آخر أسبوعين")],
    anom: [L("Distance from this week's usual level", "البعد عن المستوى المعتاد لهذا الأسبوع"), L("sentinel positivity · this week vs past seasons", "إيجابية الرصد · هذا الأسبوع مقابل المواسم السابقة")],
    dclim: [L("Usual seasonal change to the target week", "التغيّر الموسمي المعتاد حتى الأسبوع المستهدف"), L("past seasons · now to the target week", "المواسم السابقة · من الآن إلى الأسبوع المستهدف")],
    dlogspec: [L("Change in testing volume last week", "تغيّر حجم الفحوص في الأسبوع الماضي"), L("samples tested · last two weeks", "العيّنات المفحوصة · آخر أسبوعين")],
    intercept: [L("Average week-to-week drift", "متوسط التغيّر من أسبوع إلى آخر"), L("all past seasons", "كل المواسم السابقة")],
    residual_median_offset: [L("Correction for typical past error", "تصحيح الخطأ المعتاد سابقاً"), L("earlier forecasts", "التوقعات السابقة")],
  }[f] || [f, ""]);
  function whyChart(terms) {
    const rows = terms.slice().sort((a, b) => Math.abs(b.pp) - Math.abs(a.pp)), W = 760, rh = 44, ml = 330, mr = 60, H = rows.length * rh + 26;
    const mx = Math.max(0.5, ...rows.map(t => Math.abs(t.pp))) * 1.15, x = lin(-mx, mx, ml + 56, W - mr), x0 = x(0);
    let g = `<line class="one" x1="${x0}" x2="${x0}" y1="4" y2="${H - 22}"/><text x="${x0}" y="${H - 6}" text-anchor="middle" class="lab">0</text>` +
      `<text x="${ml + 56}" y="${H - 6}" class="lab">${L("← lowers the forecast", "← يخفض التوقع")}</text><text x="${W - mr}" y="${H - 6}" text-anchor="end" class="lab">${L("raises it →", "يرفعه →")}</text>`;
    rows.forEach((t, i) => {
      const yy = i * rh + 6, [name, tag] = feat(t.f), a = Math.min(x0, x(t.pp)), w = Math.abs(x(t.pp) - x0);
      g += `<text x="${ml - 14}" y="${yy + 13}" text-anchor="end" class="lab" style="fill:var(--ink)">${esc(name)}</text><text x="${ml - 14}" y="${yy + 27}" text-anchor="end" style="font-size:10.5px">${esc(tag)}</text>` +
        `<rect class="${t.pp >= 0 ? "barp" : "barm"}" x="${a}" y="${yy + 4}" width="${Math.max(w, 1)}" height="20" rx="3"/>` +
        `<text x="${t.pp >= 0 ? x(t.pp) + 7 : x(t.pp) - 7}" y="${yy + 19}" text-anchor="${t.pp >= 0 ? "start" : "end"}" class="val">${(t.pp > 0 ? "+" : "") + f1(t.pp)}</text>`;
    });
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${L("Contribution of each input to the forecast", "إسهام كل مُدخل في التوقع")}">${g}</svg>`;
  }
  function why() {
    const ex = (cur.explain || {})[S.series]; if (!ex || !ex.length) return "";
    S.exw = Math.min(S.exw, ex.length - 1); const e = ex[S.exw];
    return `<div class="card" style="margin-top:18px"><div class="bar"><h3 style="margin:0">${L("Why the forecast says this", "لماذا يقول التوقع ذلك")}</h3>
        <div class="seg sp" role="group">${ex.map((w, i) => `<button data-act="exw" data-v="${i}" aria-pressed="${i === S.exw}">${L("week ending", "الأسبوع المنتهي في")} ${dfmt(w.te)}</button>`).join("")}</div></div>
      <p class="sub" style="margin:10px 0 6px">${L(`${sname(S.series)}, headline model: median ${f1(e.median)}% for the week ending ${dfmt(e.te)}. Each bar is the number of percentage points the forecast would move without that input, so the explanation is exact, not an approximation.`,
        `${sname(S.series)}، النموذج الرئيسي: الوسيط ${f1(e.median)}% للأسبوع المنتهي في ${dfmt(e.te)}. كل شريط هو عدد النقاط المئوية التي كان التوقع سيتحركها من دون ذلك المُدخل، فالتفسير دقيق لا تقريبي.`)}</p>
      <div style="overflow-x:auto"><div style="min-width:620px">${whyChart(e.terms)}</div></div>
      <div class="src">${L("Under each input: the signal it comes from and the period it covers. Location: UAE national sentinel sites. WHO FluNet has no breakdown by emirate or district, so NABD cannot attribute a rise to a place until a hospital or emirate feed exists.",
        "تحت كل مُدخل: الإشارة التي يأتي منها والفترة التي يغطيها. الموقع: مواقع الرصد الوطنية في الإمارات. لا تتضمن WHO FluNet تفصيلاً بحسب الإمارة أو المنطقة، فلا يستطيع نبض نسبة الارتفاع إلى مكان قبل توفر بيانات مستشفى أو إمارة.")} <span class="mono">results/uae/explain/</span></div></div>`;
  }

  function week() {
    return `<section id="week"><div class="wrap"><div class="sec-head"><div class="eyebrow">${L("This week's card", "بطاقة هذا الأسبوع")}</div>
      <h2>${L("How high, how sure, and what to do about it.", "إلى أي مدى سترتفع، وما مدى الثقة، وما الذي ينبغي فعله.")}</h2>
      <p>${L("The forecast is a range, not a line. The card turns the range into the chance of crossing each pressure threshold, then into one proposed action per role. The forecast for each week is hashed before WHO publishes that week.",
        "التوقع نطاق لا خط. تحوّل البطاقة النطاق إلى احتمال تجاوز كل عتبة ضغط، ثم إلى إجراء مقترح واحد لكل دور. ويُوثَّق توقع كل أسبوع بالتجزئة قبل أن تنشر المنظمة بيانات ذلك الأسبوع.")}</p></div>
      <div id="card-body">${cardBody()}</div><div id="why" style="scroll-margin-top:80px">${why()}</div><div id="approval">${approval()}</div></div></section>`;
  }

  function science() {
    const P = ev.pool, F = ev.fm;
    const steps = [
      [L("The obstacle", "العقبة"), L("UAE sentinel data start in 2022. A model fitted to four seasons only ties repeating last week. More local signals did not help.", "تبدأ بيانات الرصد في الإمارات عام 2022. نموذج مبني على أربعة مواسم يتعادل فقط مع تكرار الأسبوع الماضي، ولم تُفِد إضافة إشارات محلية.")],
      [L("The idea: learn across many seasons", "الفكرة: التعلّم من مواسم كثيرة"), L("One model is trained on how seasons behave across 46 countries. A country brings only its recent weeks and whatever history it has; the model supplies the rest.", "يتدرّب نموذج واحد على سلوك المواسم في 46 دولة. تأتي الدولة بأسابيعها الأخيرة وما لديها من سجل، ويكمل النموذج الباقي.")],
      [L("The test, locked twice", "الاختبار، مثبّت مرتين"), L(`${P.n_named} test countries were named and the plan locked before any of their data were downloaded. The model was then locked before a single row was extracted. ${P.n} met the pre-set data rules. Scored once.`, `سُمّيت ${P.n_named} دولة للاختبار وثُبّتت الخطة قبل تنزيل أي من بياناتها، ثم ثُبّت النموذج قبل استخراج أي صف. استوفت ${P.n} دولة قواعد البيانات المحددة مسبقاً. وأُجري التقييم مرة واحدة.`)],
    ];
    const kp = (d, lab, cls = "teal") => `<div class="card flat"><div class="kpi ${cls} num">${less(d.rel_wis)}%<small> ${L("less error", "خطأ أقل")}</small></div><p style="margin-top:6px">${lab}</p><div class="src num">${f3(d.rel_wis)} · ${L("95% interval", "فاصل 95%")} ${ci(d)} · ${ltr(esc(d.unit_wins))}</div></div>`;
    const fmItems = F ? Object.entries(F.mean_wis).sort((a, b) => a[1] - b[1]).map(([k, v]) => ({ v, hi: k === POOL || k.startsWith("Chronos"),
      label: { "NABD-Pool": L("NABD pooled model", "نموذج نبض المجمَّع"), "Chronos-2 (zero-shot)": L("Chronos-2, off the shelf", "Chronos-2 كما هو"), "Pool+FM": L("Average of the two", "متوسط الاثنين"),
               "NABD-UAE-v1": L("Own-record model", "نموذج سجل الدولة"), persistence: L("Repeat last week", "تكرار الأسبوع الماضي"), "seasonal-analog": L("Past-season pattern", "نمط المواسم السابقة") }[k] || k })) : [];
    return `<section class="alt" id="science"><div class="wrap"><div class="sec-head"><div class="eyebrow">${L("The science", "العلم")}</div>
      <h2>${L("Tested under a plan locked in advance: 18 countries the model had never seen.", "مختبَر وفق خطة ثُبّتت مسبقاً: 18 دولة لم يرها النموذج من قبل.")}</h2>
      <p>${L("If learning across countries works, it should work on countries the model has never seen, against the model each of them would build from its own record. That is the test NABD registered in advance.",
        "إن كان التعلّم عبر الدول مجدياً فيجب أن ينجح في دول لم يرها النموذج، في مواجهة النموذج الذي كانت كل دولة ستبنيه من سجلها. وهذا هو الاختبار المسجَّل مسبقاً.")}</p></div>
      <div class="grid g3">${steps.map((s, i) => `<div class="card flat"><div class="step-n num">${i + 1}</div><h3>${s[0]}</h3><p>${s[1]}</p></div>`).join("")}</div>
      <div class="grid g-32" style="margin-top:18px"><div class="card"><div class="chips">${CH.pre()}${P.verdict === "MET" ? CH.met() : CH.miss()}</div>
          <h3>${L("Forecast error of the pooled model relative to each country's own-record model", "خطأ توقع النموذج المجمَّع مقارنة بنموذج سجل كل دولة")}</h3>
          ${forest()}<div class="src">${L(`Influenza, ${P.primary.n_cells.toLocaleString()} forecasts, seasons 2022/23 to 2025/26, one to four weeks ahead. Hover a dot for the underlying scores. Source: results/pool/SUMMARY.md.`,
            `الإنفلونزا، ${P.primary.n_cells.toLocaleString()} توقعاً، المواسم 2022/23 إلى 2025/26، من أسبوع إلى أربعة أسابيع. مرّر المؤشر على النقطة لرؤية القيم. المصدر: results/pool/SUMMARY.md.`)}</div></div>
        <div class="grid" style="align-content:start">
          ${kp(P.primary, L("than each country's own-record model. The registered primary result.", "من نموذج سجل كل دولة. وهي النتيجة الأساسية المسجّلة."))}
          ${kp(P.short, L("where the country had two or fewer earlier seasons: the UAE's position.", "حين كان لدى الدولة موسمان سابقان أو أقل: وضع الإمارات."))}
          ${kp(P.vs_persistence, L(`than repeating last week. The own-record model lost to it on the same forecasts (${f2(P.local_vs_persistence.rel_wis)}).`, `من تكرار الأسبوع الماضي. وقد خسر نموذج سجل الدولة أمامه في التوقعات نفسها (${f2(P.local_vs_persistence.rel_wis)}).`))}
        </div></div>
      ${F ? `<div class="grid g-32" style="margin-top:18px"><div class="card"><div class="chips">${CH.post()}</div><h3>${L("Cross-check: a general foundation model on the same forecasts", "تحقّق إضافي: نموذج أساس عام على التوقعات نفسها")}</h3>
          ${hbars(fmItems)}<div class="src">${L(`Mean forecast error (WIS, percentage points; lower is better) on ${F.n_cells.toLocaleString()} held-out forecasts. ${F.model}, revision ${F.revision}, no fine-tuning. Source: results/fm/SUMMARY.md.`,
            `متوسط خطأ التوقع (WIS بالنقاط المئوية؛ الأقل أفضل) على ${F.n_cells.toLocaleString()} توقعاً خارج العيّنة. ${F.model}، الإصدار ${F.revision}، بلا ضبط. المصدر: results/fm/SUMMARY.md.`)}</div></div>
        <div class="grid" style="align-content:start"><div class="card flat"><h3>${L("Two unrelated methods, one answer", "طريقتان مختلفتان، وجواب واحد")}</h3>
          <p>${L(`A 120-million-parameter model trained on other time series, used off the shelf, lands level with NABD's small pooled model (${f2(F.fm_vs_pool.rel_wis)}, interval ${ci(F.fm_vs_pool)}) and shows the same gain over the own-record model (${less(F.fm_vs_local.rel_wis)}% less error). So the gain is not a quirk of one model.`,
            `نموذج بـ120 مليون مُعامل مدرَّب على سلاسل زمنية أخرى، مستخدَم كما هو، يأتي على قدم المساواة مع نموذج نبض المجمَّع الصغير (${f2(F.fm_vs_pool.rel_wis)}، الفاصل ${ci(F.fm_vs_pool)}) ويُظهر الكسب نفسه على نموذج سجل الدولة (خطأ أقل بـ${less(F.fm_vs_local.rel_wis)}%). فالكسب ليس خاصاً بنموذج واحد.`)}</p>
          <p style="margin-top:10px">${L(`NABD runs the small model: every forecast decomposes exactly into its inputs and it runs in seconds on a laptop. Averaging the two is ${less(F.ens_vs_pool.rel_wis)}% better with an interval that includes no gain (${ci(F.ens_vs_pool)}): a hypothesis, not a claim.`,
            `يشغّل نبض النموذج الصغير: كل توقع يتفكك تماماً إلى مدخلاته ويعمل في ثوانٍ على حاسوب محمول. متوسط الاثنين أفضل بـ${less(F.ens_vs_pool.rel_wis)}% وفاصله يشمل انعدام الكسب (${ci(F.ens_vs_pool)}): فرضية لا ادعاء.`)}</p></div>
          <div class="note warn">${L("Not a UAE result. UAE data had been seen before these tests, so the confirmatory UAE evidence can only come forward in time. That test is locked: see the ledger.", "ليست نتيجة عن الإمارات. فبيانات الإمارات كانت قد فُحصت قبل هذه الاختبارات، ولا يأتي الدليل المؤكِّد عنها إلا زمنياً إلى الأمام. وذلك الاختبار مثبّت: انظر السجل.")}</div></div></div>` : ""}
      </div></section>`;
  }

  function rpUnits() { return D.replay.map((u, i) => ({ ...u, i })).filter(u => u.source === S.rp.src); }
  function rpInit() {
    const us = rpUnits(); if (!us.length) return;
    if (S.rp.id == null || !us.some(u => u.i === S.rp.id)) {                 // default by rule: first country A-Z, flu, latest season
      const flu = us.filter(u => u.series === "flu"), c0 = flu.map(u => u.location).sort()[0];
      S.rp.id = flu.filter(u => u.location === c0).sort((a, b) => b.season - a.season)[0].i;
      S.rp.w = Math.floor(D.replay[S.rp.id].te.length / 2);
    }
    const u = D.replay[S.rp.id];
    if (!S.rp.model || !u.models[S.rp.model]) S.rp.model = u.models.pool ? "pool" : "local";
    S.rp.w = Math.min(S.rp.w, u.te.length - 1);
  }
  function replayBody() {
    rpInit();
    const us = rpUnits(), u = D.replay[S.rp.id], w = S.rp.w, keys = Object.keys(u.models).sort((a, b) => ["pool", "local", "last", "pattern"].indexOf(a) - ["pool", "local", "last", "pattern"].indexOf(b));
    const tally = k => { let mi = 0, wa = 0; for (let i = 0; i <= w; i++) { const su = u.obs[i] > u.T, ro = !!u.models[k].roster[i]; if (su && !ro) mi++; if (!su && ro) wa++; } return [mi, wa]; };
    return `<div class="bar"><div class="seg" role="group"><button data-act="rp-src" data-v="heldout" aria-pressed="${S.rp.src === "heldout"}">${L("18 held-out countries", "18 دولة خارج العيّنة")}</button><button data-act="rp-src" data-v="gulf" aria-pressed="${S.rp.src === "gulf"}">${L("Gulf test", "الاختبار الخليجي")}</button></div>
        <div style="min-width:240px"><select data-act="rp-unit" aria-label="${L("Country and season", "الدولة والموسم")}">${us.sort((a, b) => cname(a.location).localeCompare(cname(b.location)) || a.series.localeCompare(b.series) || b.season - a.season).map(x => `<option value="${x.i}" ${x.i === S.rp.id ? "selected" : ""}>${esc(cname(x.location))} · ${sname(x.series)} · ${season(x.season)}</option>`).join("")}</select></div>
        <div class="seg sp" role="group">${keys.map(k => `<button data-act="rp-model" data-v="${k}" aria-pressed="${S.rp.model === k}">${mname(k)}</button>`).join("")}</div></div>
      <div id="rp-chart">${replayChart(u, w, S.rp.model)}</div>
      <div class="bar" style="margin-top:10px"><button class="btn sm" data-act="rp-play">${S.rp.timer ? L("Pause", "إيقاف") : L("▶ Play the season", "▶ شغّل الموسم")}</button>
        <input type="range" min="0" max="${u.te.length - 1}" value="${w}" data-act="rp-week" aria-label="${L("Week", "الأسبوع")}" style="flex:1;min-width:180px">
        <span class="sub num" style="margin:0;min-width:120px;text-align:end">${L("week ending", "الأسبوع المنتهي في")} ${dfmt(u.te[w], { day: "numeric", month: "short", year: "numeric" })}</span></div>
      <div class="legend"><span><i class="obs"></i>${L("what happened", "ما حدث")}</span><span><i class="band"></i>${L("80% range issued two weeks earlier", "نطاق 80% الصادر قبل أسبوعين")}</span><span><i class="rose" style="height:10px"></i>${L("missed surge week", "أسبوع موجة فائت")}</span><span><i class="amber" style="height:10px"></i>${L("wasted roster week", "أسبوع مناوبة مهدور")}</span><span><i style="height:10px"></i>${L("rostered, and needed", "جُدول وكان لازماً")}</span></div>
      <div class="tally">${keys.map(k => { const [mi, wa] = tally(k); return `<div class="t ${k === S.rp.model ? "me" : ""}"><b>${mname(k)}</b><div class="n num">${mi + wa}</div><small>${L(`${mi} missed · ${wa} wasted so far`, `${mi} فائتة · ${wa} مهدورة حتى الآن`)}</small></div>`; }).join("")}</div>
      <div class="src">${L(`Rule fixed in advance: roster surge capacity when the forecast issued two weeks earlier gave at least a 30% chance of passing ${f1(u.T)}% (${u.source === "gulf" ? "the playbook threshold" : "the country's own high-season level"}). Default season chosen by rule (first country A to Z, latest season), every season selectable.`,
        `قاعدة محددة مسبقاً: تُجدول طاقة إضافية حين يعطي التوقع الصادر قبل أسبوعين احتمالاً لا يقل عن 30% لتجاوز ${f1(u.T)}% (${u.source === "gulf" ? "عتبة دليل العمل" : "مستوى الموسم المرتفع الخاص بالدولة"}). الموسم الافتراضي يُختار بقاعدة (أول دولة أبجدياً، أحدث موسم)، وكل المواسم متاحة.`)}</div>`;
  }

  function decisions() {
    const R = ev.replay_pool, G = ev.replay_gulf;
    const ps = R.per_season, items = [["NABD-Pool", "pool", true], ["NABD-UAE-v1", "local", false], ["persistence", "last", false], ["seasonal-analog", "pattern", false]]
      .map(([k, n, hi]) => ({ label: mname(n), a: ps[k].missed, b: ps[k].wasted, t: ps[k].mismatch, hi }));
    return `<section id="decisions"><div class="wrap"><div class="sec-head"><div class="eyebrow">${L("From accuracy to decisions", "من الدقة إلى القرار")}</div>
      <h2>${L("Does a better forecast change a roster? Partly. Both sides are shown.", "هل يغيّر التوقع الأفضل جدول المناوبات؟ جزئياً. والوجهان معروضان.")}</h2>
      <p>${L("One roster rule, fixed in advance, is replayed over every held-out season. A missed week is a surge with no extra staff; a wasted week is extra staff with no surge.",
        "تُعاد قاعدة مناوبات واحدة محددة مسبقاً على كل موسم خارج العيّنة. الأسبوع الفائت موجة بلا طاقة إضافية؛ والأسبوع المهدور طاقة إضافية بلا موجة.")}</p></div>
      <div class="grid g-32"><div class="card"><div class="chips">${CH.post()}</div><h3>${L("Mis-rostered weeks per season, by what the rule was fed", "أسابيع الجدولة الخاطئة في الموسم بحسب مُدخل القاعدة")}</h3>
          ${hbars(items, { stack: true })}<div class="legend"><span><i class="rose" style="height:10px"></i>${L("missed surge weeks", "أسابيع موجة فائتة")}</span><span><i style="height:10px"></i>${L("wasted roster weeks", "أسابيع مناوبة مهدورة")}</span></div>
          <div class="src">${L(`Influenza, ${R.n} seasons in ${R.n_countries} countries. Source: results/replay/pool/SUMMARY.md.`, `الإنفلونزا، ${R.n} موسماً في ${R.n_countries} دولة. المصدر: results/replay/pool/SUMMARY.md.`)}</div></div>
        <div class="grid" style="align-content:start">
          <div class="note ok">${L(`<b>Better than the own-record model:</b> ${f1(R.vs_local.mean_a)} vs ${f1(R.vs_local.mean_b)} mis-rostered weeks a season (difference ${sgn(R.vs_local.diff_per_season)}, 95% interval ${sgn(R.vs_local.ci95[0])} to ${sgn(R.vs_local.ci95[1])}), and far better than planning from past seasons (${f1(R.vs_pattern.mean_b)}).`,
            `<b>أفضل من نموذج سجل الدولة:</b> ${f1(R.vs_local.mean_a)} مقابل ${f1(R.vs_local.mean_b)} أسبوع جدولة خاطئة في الموسم (الفرق ${sgn(R.vs_local.diff_per_season)}، فاصل 95% من ${sgn(R.vs_local.ci95[0])} إلى ${sgn(R.vs_local.ci95[1])})، وأفضل كثيراً من التخطيط من المواسم السابقة (${f1(R.vs_pattern.mean_b)}).`)}</div>
          <div class="note bad">${L(`<b>Not clearly better than repeating last week:</b> ${f1(R.vs_last_week.mean_a)} vs ${f1(R.vs_last_week.mean_b)} (difference ${sgn(R.vs_last_week.diff_per_season)}, interval ${sgn(R.vs_last_week.ci95[0])} to ${sgn(R.vs_last_week.ci95[1])}). It also missed slightly more surge weeks than the own-record model (${f1(ps["NABD-Pool"].missed)} vs ${f1(ps["NABD-UAE-v1"].missed)}) while wasting fewer.`,
            `<b>ليس أفضل بوضوح من تكرار الأسبوع الماضي:</b> ${f1(R.vs_last_week.mean_a)} مقابل ${f1(R.vs_last_week.mean_b)} (الفرق ${sgn(R.vs_last_week.diff_per_season)}، الفاصل من ${sgn(R.vs_last_week.ci95[0])} إلى ${sgn(R.vs_last_week.ci95[1])}). كما فاته عدد أكبر قليلاً من أسابيع الموجة مقارنة بنموذج سجل الدولة (${f1(ps["NABD-Pool"].missed)} مقابل ${f1(ps["NABD-UAE-v1"].missed)}) مع هدر أقل.`)}</div>
          ${G ? `<div class="note">${L(`In the Gulf test the earlier own-record model showed the same pattern: ${f1(G.vs_pattern.mean_a)} vs ${f1(G.vs_pattern.mean_b)} against past-season planning over ${G.n} seasons, and a tie with repeating last week.`, `وفي الاختبار الخليجي أظهر نموذج سجل الدولة النمط نفسه: ${f1(G.vs_pattern.mean_a)} مقابل ${f1(G.vs_pattern.mean_b)} أمام التخطيط من المواسم السابقة على ${G.n} موسماً، وتعادلاً مع تكرار الأسبوع الماضي.`)}</div>` : ""}
          <p class="sub">${L("That is why the pilot's exit test is set against the hospital's own census carried forward.", "ولهذا حُدّد معيار نجاح التجربة مقابل تكرار أعداد المستشفى نفسها.")}</p>
        </div></div>
      <div class="card" style="margin-top:18px"><div class="chips">${CH.post()}</div><h3>${L("Replay a season, week by week", "أعد عرض موسم أسبوعاً بأسبوع")}</h3><div id="rp-body">${replayBody()}</div></div>
      </div></section>`;
  }

  function results() {
    const P = ev.pool, G = ev.gcc, U = ev.us, A = ev.uae, F = ev.fm, R = ev.replay_pool, lt = D.ledger.live_test, UP = ev.uae_pool;
    const yy = s => `${s}/${String((Number(s) + 1) % 100).padStart(2, "0")}`;
    const cards = [
      [CH.pre() + CH.met(), L("Learning across countries, 18 held-out countries", "التعلّم عبر الدول، 18 دولة خارج العيّنة"), `<span class="kpi teal num">${f3(P.primary.rel_wis)}</span>`,
        L(`Pooled vs own-record model, influenza. Interval ${ci(P.primary)}. Better in ${P.primary.unit_wins}.`, `المجمَّع مقابل نموذج سجل الدولة، الإنفلونزا. الفاصل ${ci(P.primary)}. أفضل في ${P.primary.unit_wins}.`), "results/pool/SUMMARY.md"],
      G && [CH.pre() + CH.met(), L("Gulf test: Oman, Qatar, Saudi Arabia", "الاختبار الخليجي: عُمان وقطر والسعودية"), `<span class="kpi teal num">${f3(G.vs_persistence.rel_wis)}</span>`,
        L(`Own-record model vs repeating last week, influenza. Interval ${ci(G.vs_persistence)}. Against past-season patterns: ${f2(G.vs_pattern.rel_wis)}.`, `نموذج سجل الدولة مقابل تكرار الأسبوع الماضي، الإنفلونزا. الفاصل ${ci(G.vs_persistence)}. ومقابل نمط المواسم السابقة: ${f2(G.vs_pattern.rel_wis)}.`), "results/gcc/SUMMARY.md"],
      U && [CH.pre() + CH.miss(), L("United States, against the CDC's combined forecast", "الولايات المتحدة، مقابل توقع CDC المجمَّع"), `<span class="kpi rose num">${f2(U.rel_wis)}</span>`,
        L(`The bar was ${U.margin}. NABD missed it (interval ${ltr(f2(U.ci95[0]) + "–" + f2(U.ci95[1]))}). Among single hub models: ${U.ranks.map(r => `${r.rank} of ${r.n} in ${r.season}`).join(", ")}.`, `كان الهدف ${U.margin} ولم يبلغه نبض (الفاصل ${ltr(f2(U.ci95[0]) + "–" + f2(U.ci95[1]))}). بين النماذج المنفردة: ${U.ranks.map(r => `${r.rank} من ${r.n} في ${r.season}`).join("، ")}.`), "results/SUMMARY.md"],
      A && [CH.retro(), L("The UAE's own four-season record", "سجل الإمارات نفسه (أربعة مواسم)"), `<span class="kpi slate num">${f2(A.flu.rel_wis)}</span>`,
        L("Own-record model vs repeating last week, forward in time: a tie for influenza and RSV. A multi-signal version did no better.", "نموذج سجل الدولة مقابل تكرار الأسبوع الماضي، زمنياً إلى الأمام: تعادل للإنفلونزا والفيروس المخلوي. ولم تكن النسخة المتعددة الإشارات أفضل."), "results/uae/SUMMARY-v2.md"],
      UP && [CH.post(), L("The UAE's own seasons, pooled model (development check)", "مواسم الإمارات نفسها، النموذج المجمَّع (فحص تطويري)"), `<span class="kpi teal num">${f2(UP.vs_persistence.rel_wis)}</span>`,
        L(`Pooled model vs repeating last week, influenza, forward in time with the UAE left out of the fit (interval ${ci(UP.vs_persistence)}). Better in both scored seasons (${Object.entries(UP.by_season).map(([s, v]) => `${yy(s)}: ${f2(v)}`).join(", ")}). Not a confirmatory test: UAE data helped choose the model. The confirmatory UAE test runs live.`,
          `النموذج المجمَّع مقابل تكرار الأسبوع الماضي، الإنفلونزا، زمنياً إلى الأمام مع استبعاد الإمارات من التدريب (الفاصل ${ci(UP.vs_persistence)}). أفضل في الموسمين المقيَّمين (${Object.entries(UP.by_season).map(([s, v]) => `${yy(s)}: ${f2(v)}`).join("، ")}). ليس اختباراً تأكيدياً: أسهمت بيانات الإمارات في اختيار النموذج. والاختبار التأكيدي للإمارات يجري حيّاً.`), "results/pool/uae_devcheck/SUMMARY.md"],
      F && [CH.post(), L("Foundation model on the same forecasts", "نموذج أساس على التوقعات نفسها"), `<span class="kpi slate num">${f2(F.fm_vs_pool.rel_wis)}</span>`,
        L(`Chronos-2 off the shelf vs NABD's pooled model: level (interval ${ci(F.fm_vs_pool)}). Both beat the own-record model.`, `Chronos-2 كما هو مقابل نموذج نبض المجمَّع: تعادل (الفاصل ${ci(F.fm_vs_pool)}). وكلاهما يتفوق على نموذج سجل الدولة.`), "results/fm/SUMMARY.md"],
      [CH.post(), L("Roster rule replayed", "إعادة تشغيل قاعدة المناوبات"), `<span class="kpi slate num">${sgn(R.vs_local.diff_per_season)}</span>`,
        L(`Mis-rostered weeks a season, pooled minus own-record. Against repeating last week: ${sgn(R.vs_last_week.diff_per_season)}, not distinguishable.`, `أسابيع الجدولة الخاطئة في الموسم، المجمَّع ناقص نموذج سجل الدولة. ومقابل تكرار الأسبوع الماضي: ${sgn(R.vs_last_week.diff_per_season)}، غير قابل للتمييز.`), "results/replay/pool/SUMMARY.md"],
      [CH.pre() + CH.wait(), L("UAE, forward in real time", "الإمارات، زمنياً إلى الأمام"), `<span class="kpi slate num">${lt.rounds.length}<small> ${L("round issued", "جولة صادرة")}</small></span>`,
        L(`Pooled vs own-record model on the live ledger, season 2026/27. Locked before its first data point. Assessed once, on or after ${dfmt(lt.final_from, { day: "numeric", month: "long", year: "numeric" })}.`, `المجمَّع مقابل نموذج سجل الدولة في السجل الحي، موسم 2026/27. ثُبّت قبل أول نقطة بيانات. يُقيَّم مرة واحدة في ${dfmt(lt.final_from, { day: "numeric", month: "long", year: "numeric" })} أو بعده.`), "docs/PREREG-LIVE.md"],
    ].filter(Boolean);
    return `<section class="alt" id="results"><div class="wrap"><div class="sec-head"><div class="eyebrow">${L("All results", "كل النتائج")}</div>
      <h2>${L("Every test NABD has run, including the ones it lost.", "كل اختبار أجراه نبض، بما فيه ما خسره.")}</h2>
      <p>${L("Numbers are relative forecast error: below 1 is better than the comparator. Each card says whether the test was registered before the data were seen.", "الأرقام خطأ توقع نسبي: أقل من 1 يعني أفضل من المقارَن به. وتبيّن كل بطاقة هل سُجّل الاختبار قبل رؤية البيانات.")}</p></div>
      <div class="grid g3">${cards.map(c => `<div class="card"><div class="chips">${c[0]}</div><h3>${c[1]}</h3><div style="margin:10px 0 8px">${c[2]}</div><p>${c[3]}</p><div class="src mono">${c[4]}</div></div>`).join("")}</div></div></section>`;
  }

  function brief() {
    const O = ev.ops || {}, RP = O.replay, R = ev.replay_pool, P = ev.pool, fr = D.freshness, pct = v => Math.round(v * 100) + "%";
    const ST = { met: () => chip("met", L("Met", "مستوفى")), part: () => chip("scn", L("Partly met", "مستوفى جزئياً")), sim: () => chip("wait", L("Scenario only", "سيناريو فقط")) };
    const reqs = [
      [ST.part(), L("Multi-signal surveillance", "رصد متعدد الإشارات"),
        L("The headline model reads laboratory positivity and testing volume from one WHO surveillance stream. A challenger added non-sentinel laboratory data, school breaks and Ramadan; it did not improve the forecast, and that result is reported. Hospital counts and wastewater are pilot inputs, not built.",
          "يقرأ النموذج الرئيسي نسبة الإيجابية المخبرية وحجم الفحوص من مسار رصد واحد لدى المنظمة. وأضاف نموذج منافس بيانات مخبرية غير رصدية والعطل المدرسية ورمضان؛ فلم يتحسن التوقع، وهذه النتيجة منشورة. أما أعداد المستشفيات ومياه الصرف فمدخلات للتجربة لم تُبنَ بعد."), "#results"],
      [ST.part(), L("Explainable anomaly detection", "كشف قابل للتفسير"),
        L("Every forecast decomposes exactly into its inputs, each tied to a signal and a time period, including how far this week sits from its usual level. Location is national only: WHO data carry no emirate or district detail.",
          "يتفكك كل توقع تماماً إلى مدخلاته، وكل مُدخل مرتبط بإشارة وفترة زمنية، ومنها مدى ابتعاد هذا الأسبوع عن مستواه المعتاد. الموقع وطني فقط: بيانات المنظمة لا تتضمن تفصيلاً بحسب الإمارة أو المنطقة."), "#why"],
      [ST.met(), L("Actionable decision support", "دعم قرار قابل للتنفيذ"),
        L("One proportionate action per named role, shown with the chance behind it and the repeat-last-week forecast beside it. A named person approves, modifies or dismisses it with a reason. Thresholds and wording await clinical review.",
          "إجراء متناسب واحد لكل دور مسمّى، يُعرض مع الاحتمال الذي يستند إليه وبجانبه توقع تكرار الأسبوع الماضي. يعتمده شخص مسمّى أو يعدّله أو يرفضه مع ذكر السبب. العتبات والصياغة بانتظار المراجعة السريرية."), "#week"],
      [ST.part(), L("Privacy-preserving views", "عروض تحفظ الخصوصية"),
        L("Weekly totals only. Person-level fields are rejected by schema, and the pilot connector suppresses any count below ten; both are tested. Actions are shown per role. Sign-in and role-based access are not built: this page is public and holds no restricted data.",
          "مجاميع أسبوعية فقط. تُرفض الحقول الفردية بحكم المخطط، ويحجب موصل التجربة أي عدد دون العشرة؛ وكلاهما مختبَر. تُعرض الإجراءات بحسب الدور. أما تسجيل الدخول والصلاحيات بحسب الدور فلم تُبنَ: هذه الصفحة عامة ولا تحوي بيانات مقيَّدة."), "#impact"],
      [ST.met(), L("Operational validation", "التحقق التشغيلي"),
        L("Lead time, sensitivity, predictive value, wasted calls, data delay, missing-input behaviour and interval coverage are all reported in the table below, each with its status.",
          "المهلة والحساسية والقيمة التنبؤية والقرارات المهدورة وتأخر البيانات وسلوك النظام عند نقص المدخلات وتغطية النطاقات، كلها في الجدول أدناه مع حالة كل منها."), "#ops"],
      [ST.sim(), L("Health and resilience impact", "الأثر الصحي والمرونة"),
        L("No outcome has been measured. The replay shows fewer mis-rostered weeks than a country's own-record model; bed and cost figures are labelled scenarios; the workforce-absence feed is simulated. A hospital pilot is how impact would be measured.",
          "لم يُقَس أي أثر بعد. تُظهر إعادة التشغيل أسابيع جدولة خاطئة أقل من نموذج سجل الدولة؛ أرقام الأسرّة والتكلفة سيناريوهات موسومة؛ وتغذية غياب العاملين محاكاة. والتجربة في مستشفى هي طريق قياس الأثر."), "#impact"],
    ];
    const order = [["NABD-Pool", "pool"], ["NABD-UAE-v1", "local"], ["persistence", "last"], ["seasonal-analog", "pattern"]];
    const rows = RP ? order.map(([k, n]) => { const m = RP.models[k], ps = R.per_season[k]; return `<tr><td>${k === "NABD-Pool" ? `<b>${mname(n)}</b>` : mname(n)}</td><td class="r num"><b>${pct(m.sens)}</b></td><td class="r num"><b>${pct(m.ppv)}</b></td><td class="r num">${f1(ps.missed)}</td><td class="r num">${f1(ps.wasted)}</td></tr>`; }).join("") : "";
    const item = (h, t, c) => `<div class="role"><b>${h}</b>${t} ${c}</div>`;
    return `<section id="brief"><div class="wrap"><div class="sec-head"><div class="eyebrow">${L("Against the brief", "مقابل متطلبات التحدي")}</div>
      <h2>${L("The six things Statement 06 asks for, and where NABD stands on each.", "المتطلبات الستة في البيان 06، وموقع نبض من كل منها.")}</h2>
      <p>${L("The headings are the organisers'. The status under each is NABD's own reading, including where it falls short.", "العناوين من صياغة المنظمين. والحالة تحت كل عنوان هي قراءة نبض نفسه، بما فيها مواضع القصور.")}</p></div>
      <div class="grid g3">${reqs.map((q, i) => `<div class="card"><div class="chips">${q[0]}</div><h3>${i + 1}. ${q[1]}</h3><p>${q[2]}</p><div class="src"><a href="${q[3]}">${L("See the evidence", "انظر الدليل")} →</a></div></div>`).join("")}</div>
      ${RP ? `<div class="grid g-32" style="margin-top:18px" id="ops"><div class="card"><div class="chips">${CH.post()}</div><h3>${L("Operational validation: the roster rule as an alert", "التحقق التشغيلي: قاعدة المناوبات بوصفها تنبيهاً")}</h3>
          <div class="tablewrap"><table><thead><tr><th>${L("What the rule was fed", "مُدخل القاعدة")}</th><th class="r">${L("Sensitivity", "الحساسية")}</th><th class="r">${L("Predictive value", "القيمة التنبؤية")}</th><th class="r">${L("Missed / season", "فائتة / موسم")}</th><th class="r">${L("Wasted / season", "مهدورة / موسم")}</th></tr></thead><tbody>${rows}</tbody></table></div>
          <div class="src">${L(`Influenza, ${RP.n} seasons in ${RP.n_countries} held-out countries, ${RP.models["NABD-Pool"].surge} surge weeks. Sensitivity: share of surge weeks that had been rostered two weeks ahead. Predictive value: share of rostered weeks that were surge weeks. The same counts as the replay above, restated; no new run. Source: results/replay/pool/summary.json, docs/DEVIATIONS.md V3.`,
            `الإنفلونزا، ${RP.n} موسماً في ${RP.n_countries} دولة خارج العيّنة، ${RP.models["NABD-Pool"].surge} أسبوع موجة. الحساسية: نسبة أسابيع الموجة التي جُدولت قبل أسبوعين. القيمة التنبؤية: نسبة الأسابيع المجدولة التي كانت أسابيع موجة. الأعداد نفسها في إعادة التشغيل أعلاه بصياغة أخرى؛ بلا تشغيل جديد. المصدر: results/replay/pool/summary.json و docs/DEVIATIONS.md V3.`)}</div>
          <p class="note warn" style="margin-top:14px">${L("Read it straight: the pooled model makes the fewest wasted calls and has the best predictive value, but it catches slightly fewer surge weeks than repeating last week.", "القراءة الصريحة: النموذج المجمَّع أقل القواعد هدراً وأعلاها قيمة تنبؤية، لكنه يلتقط أسابيع موجة أقل قليلاً من تكرار الأسبوع الماضي.")}</p></div>
        <div class="card"><h3>${L("The rest of the checklist", "بقية القائمة")}</h3><div class="roles">
          ${item(L("Lead time", "المهلة"), L("Roster calls are made two weeks before the target week. NABD does not warn earlier that a surge is starting.", "تُتخذ قرارات المناوبة قبل أسبوعين من الأسبوع المستهدف. ولا ينذر نبض أبكر ببدء الموجة."), CH.post())}
          ${item(L("Data delay", "تأخر البيانات"), L(`WHO usually publishes a week about ${fr.expected_lag_days} days after it ends. The newest published week is ${fr.last_week}, ${fr.lag_days} days old today; the card always shows this.`, `تنشر المنظمة الأسبوع عادة بعد نحو ${fr.expected_lag_days} يوماً من نهايته. أحدث أسبوع منشور هو ${fr.last_week} وعمره اليوم ${fr.lag_days} يوماً؛ وتعرض البطاقة ذلك دائماً.`), chip("pre", L("Live", "حي")))}
          ${O.dropout_us ? item(L("Missing inputs", "نقص المدخلات"), L(`In the US test, losing the latest input week multiplied forecast error by ${f2(O.dropout_us[1])}, and losing two by ${f2(O.dropout_us[2])}. A card whose forecast, direction and action disagree is blocked, not shown.`, `في الاختبار الأمريكي ضاعف فقدان أحدث أسبوع من المدخلات خطأ التوقع ${f2(O.dropout_us[1])} مرة، وفقدان أسبوعين ${f2(O.dropout_us[2])} مرة. والبطاقة التي يتعارض فيها التوقع والاتجاه والإجراء تُحجب ولا تُعرض.`), CH.retro()) : ""}
          ${P && P.coverage ? item(L("Interval coverage", "تغطية النطاقات"), L(`On the held-out forecasts the pooled model's 95% ranges contained the outcome ${pct(P.coverage["NABD-Pool"].cov95)} of the time and its 50% ranges ${pct(P.coverage["NABD-Pool"].cov50)}.`, `في التوقعات خارج العيّنة احتوت نطاقات 95% للنموذج المجمَّع النتيجة في ${pct(P.coverage["NABD-Pool"].cov95)} من الحالات ونطاقات 50% في ${pct(P.coverage["NABD-Pool"].cov50)}.`), CH.pre()) : ""}
        </div></div></div>` : ""}
      </div></section>`;
  }

  function path() {
    const ph = [
      [L("Now · November 2026", "الآن · نوفمبر 2026"), L("Working prototype. Weekly forecast rounds sealed on WHO data. The forward UAE test is locked.", "نموذج أولي عامل. جولات توقع أسبوعية موثّقة على بيانات المنظمة. واختبار الإمارات المستقبلي مثبّت."), chip("met", L("Built", "مبني"))],
      [L("December to February", "ديسمبر إلى فبراير"), L("A data-sharing note with one hospital. A clinician and a public-health officer review the playbook.", "مذكرة مشاركة بيانات مع مستشفى واحد. ومراجعة دليل العمل من طبيب ومسؤول صحة عامة."), chip("wait", L("Needs a partner", "يحتاج شريكاً"))],
      [L("Twelve-week shadow pilot", "تجربة مراقبة لاثني عشر أسبوعاً"), L("Weekly totals of paediatric respiratory cases enter through the pilot connector. No change to care. The pass mark is fixed first.", "تدخل المجاميع الأسبوعية لحالات الجهاز التنفسي للأطفال عبر موصل التجربة. لا تغيير في الرعاية. ومعيار النجاح يُحدَّد أولاً."), chip("scn", L("Connector built", "الموصل مبني"))],
      [L("April 2027 decision", "قرار أبريل 2027"), L("The pilot's exit test and the locked UAE test both report. Go or stop, on the record.", "تظهر نتيجة معيار التجربة واختبار الإمارات المثبّت معاً. استمرار أو توقف، والنتيجة موثّقة."), chip("wait", L("Planned", "مخطط"))],
      [L("Scale", "التوسّع"), L("More hospitals, a read-only feed for public-health teams, then the Gulf, where the method has already been tested in three countries.", "مستشفيات أكثر، وتغذية للقراءة فقط لفرق الصحة العامة، ثم الخليج حيث اختُبرت الطريقة في ثلاث دول."), chip("wait", L("Planned", "مخطط"))],
    ];
    const run = [
      [L("Data in", "دخول البيانات"), L("A weekly export of totals from the hospital or the health authority. The schema check rejects any person-level field and counts below ten are suppressed before anything is stored.", "تصدير أسبوعي للمجاميع من المستشفى أو الجهة الصحية. يرفض فحص المخطط أي حقل فردي وتُحجب الأعداد دون العشرة قبل أي تخزين.")],
      [L("Model changes", "تغيير النماذج"), L("A new model first runs beside the headline model on the sealed ledger and is judged by a test locked in advance. The pooled model is in that position now. The proposed rule: the headline changes only if that test is met.", "يعمل أي نموذج جديد أولاً إلى جانب النموذج الرئيسي في السجل الموثّق ويُحكم عليه باختبار مثبّت مسبقاً. والنموذج المجمَّع في هذا الموضع الآن. القاعدة المقترحة: لا يتغير النموذج الرئيسي إلا إذا تحقق ذلك الاختبار.")],
      [L("Monitoring", "المراقبة"), L("Every round is scored when its week is published, against repeating last week. Data age is shown on every card, and contradictory cards are blocked.", "تُقيَّم كل جولة عند نشر أسبوعها، مقابل تكرار الأسبوع الماضي. يظهر عمر البيانات على كل بطاقة، وتُحجب البطاقات المتعارضة.")],
      [L("People", "الأشخاص"), L("NABD proposes; a named officer decides. Every decision is logged with a reason in a chained record. Nothing is sent automatically, and nothing concerns an individual patient or worker.", "نبض يقترح، ومسؤول مسمّى يقرّر. يُسجَّل كل قرار مع سببه في سجل مترابط. لا يُرسل شيء تلقائياً، ولا شيء يخص مريضاً أو عاملاً بعينه.")],
    ];
    return `<div class="card" style="margin-top:18px" id="path"><div class="chips">${chip("scn", L("Plan", "خطة"))}</div><h3>${L("From prototype to a service the UAE can rely on", "من نموذج أولي إلى خدمة تعتمد عليها الإمارات")}</h3>
      <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(190px,1fr));margin-top:14px">${ph.map((x, i) => `<div class="card flat"><div class="step-n num">${i + 1}</div><h3>${x[0]}</h3><p>${x[1]}</p><div class="chips" style="margin-top:10px">${x[2]}</div></div>`).join("")}</div>
      <h3 style="margin-top:22px">${L("How it would run once in service", "كيف يعمل بعد دخوله الخدمة")}</h3>
      <div class="grid g2" style="margin-top:10px">${run.map(x => `<div class="role"><b>${x[0]}</b>${x[1]}</div>`).join("")}</div>
      <div class="src">${L("The pilot connector, the suppression rule, the ledger, the consistency check and the decision log exist and are tested. Hospital integration, sign-in and the public-health feed are plans.", "موصل التجربة وقاعدة الحجب والسجل وفحص الاتساق وسجل القرارات موجودة ومختبَرة. أما الربط بالمستشفيات وتسجيل الدخول وتغذية الصحة العامة فخطط.")} <span class="mono">docs/DEPLOYMENT-PLAN.md</span></div></div>`;
  }

  function ledger() {
    const Lg = D.ledger, lt = Lg.live_test, byRound = {};
    Lg.rounds.forEach(r => (byRound[r.round] ||= []).push(r));
    const mlabel = m => ({ "NABD-UAE-v1": L("Own-record model (headline)", "نموذج سجل الدولة (الرئيسي)"), "NABD-Pool": L("Pooled model (challenger)", "النموذج المجمَّع (منافس)"),
                           "NABD-UAE-v2": L("Multi-signal v2 (challenger)", "متعدد الإشارات v2 (منافس)"), persistence: L("Repeat last week", "تكرار الأسبوع الماضي") }[m] || m);
    const rows = Object.keys(byRound).sort().reverse().map(k => byRound[k].map((r, i) => {
      const v = S.verify[r.file];
      return `<tr>${i === 0 ? `<td rowspan="${byRound[k].length}"><b>${k}</b><div class="sub num" style="margin:0">${dfmt(r.issued_utc.slice(0, 10), { day: "numeric", month: "short", year: "numeric" })}<br>${L("data to", "بيانات حتى")} ${r.data_through}</div></td>` : ""}
        <td>${mlabel(r.model)}</td><td><span class="hash">${r.sha256.slice(0, 24)}…</span></td>
        <td class="r">${v === true ? `<span class="ok-t">✓ ${L("matches", "مطابق")}</span>` : v === false ? `<span class="bad-t">✗ ${L("differs", "مختلف")}</span>` : `<button class="btn sm" data-act="verify" data-v="${r.file}">${L("Verify", "تحقّق")}</button>`}</td></tr>`;
    }).join("")).join("");
    return `<section id="ledger"><div class="wrap"><div class="sec-head"><div class="eyebrow">${L("The ledger", "السجل")}</div>
      <h2>${L("Every forecast is hashed before its week is published.", "كل توقع يُوثَّق بالتجزئة قبل نشر بيانات أسبوعه.")}</h2>
      <p>${L("A forecast you can rewrite afterwards proves nothing. Each round's files get a SHA-256 fingerprint when issued. Press Verify and your browser recomputes the fingerprint from the forecast file itself.",
        "التوقع الذي يمكن تعديله لاحقاً لا يثبت شيئاً. تحصل ملفات كل جولة على بصمة SHA-256 عند الإصدار. اضغط «تحقّق» ليعيد متصفحك حساب البصمة من ملف التوقع نفسه.")}</p></div>
      <div class="grid g-32"><div class="card"><div class="bar"><h3 style="margin:0">${L("Issued rounds", "الجولات الصادرة")}</h3><button class="btn sm sp" data-act="verify-all">${L("Verify all", "تحقّق من الكل")}</button></div>
          <div class="tablewrap"><table><thead><tr><th>${L("Round", "الجولة")}</th><th>${L("Forecast", "التوقع")}</th><th>SHA-256</th><th class="r">${L("Check", "التحقق")}</th></tr></thead><tbody>${rows}</tbody></table></div>
          <div class="src">${Lg.receipt ? receiptTxt(Lg) : L(`${Lg.n_scored} forecast weeks scored so far: WHO has not yet published a target week of any round. Merkle root of the newest round: `, `عدد الأسابيع المقيَّمة حتى الآن ${Lg.n_scored}: لم تنشر المنظمة بعدُ أي أسبوع مستهدف. جذر ميركل لأحدث جولة: `)}<span class="hash">${(Lg.manifests[Lg.manifests.length - 1] || {}).merkle_root?.slice(0, 32) || ""}…</span></div></div>
        <div class="grid" style="align-content:start">
          <div class="card"><div class="chips">${CH.pre()}${CH.wait()}</div><h3>${L("The UAE test is already locked", "اختبار الإمارات مثبّت سلفاً")}</h3>
            <p>${L(`Pooled model against own-record model, every weekly round of this season, scored against WHO's published values, target weeks to ${dfmt(lt.last_target, { day: "numeric", month: "long", year: "numeric" })}. One assessment, on or after ${dfmt(lt.final_from, { day: "numeric", month: "long", year: "numeric" })}. Weekly numbers until then are descriptive only.`,
              `النموذج المجمَّع مقابل نموذج سجل الدولة في كل جولة أسبوعية هذا الموسم، مقيَّماً مقابل القيم المنشورة من المنظمة، للأسابيع المستهدفة حتى ${dfmt(lt.last_target, { day: "numeric", month: "long", year: "numeric" })}. تقييم واحد في ${dfmt(lt.final_from, { day: "numeric", month: "long", year: "numeric" })} أو بعده. والأرقام الأسبوعية حتى ذلك الحين وصفية فقط.`)}</p>
            <div class="src">docs/PREREG-LIVE.md · ${L("lock", "القفل")} <span class="hash">${(lt.lock_root || "").slice(0, 20)}…</span></div></div>
          <div class="note warn">${anchorTxt(Lg)}</div>
        </div></div></div></section>`;
  }

  function impact() {
    const a = ev.aed, cH = cur.cards[HEAD];
    const out = s => { const c = cH[s], T = Object.keys(c.max_p).map(Number).sort((x, y) => x - y)[0]; return `<div class="role"><b>${sname(s)}</b>${esc(c.band ? c.band.label[S.lang] : "")}. ${L(`Chance of being above ${T}% in the next two weeks: ${Math.round(c.max_p[String(T)] * 100)}%.`, `احتمال تجاوز ${T}% خلال الأسبوعين المقبلين: ${Math.round(c.max_p[String(T)] * 100)}%.`)}</div>`; };
    const aed = v => ltr(new Intl.NumberFormat("en").format(v));
    const col = (h, cls, items) => `<div class="card flat"><div class="chips">${chip(cls, h)}</div><ul style="margin:0;padding-inline-start:18px;color:var(--ink-2);font-size:.93rem">${items.map(i => `<li style="margin-bottom:6px">${i}</li>`).join("")}</ul></div>`;
    return `<section class="alt" id="impact"><div class="wrap"><div class="sec-head"><div class="eyebrow">${L("Impact", "الأثر")}</div>
      <h2>${L("What this is for: fewer surprises on children's wards.", "الغاية: مفاجآت أقل في أجنحة الأطفال.")}</h2>
      <p>${L("NABD is built to strengthen what the UAE already has: its surveillance records, its hospital and public-health systems, and the national teams who rely on them. The numbers below are published burden figures and labelled scenarios. NABD has no Abu Dhabi hospital data yet; the pilot is how that changes.", "يُبنى نبض لتعزيز ما تملكه الإمارات أصلاً: سجلات الرصد وأنظمة المستشفيات والصحة العامة والفرق الوطنية التي تعتمد عليها. الأرقام أدناه أرقام عبء منشورة وسيناريوهات موسومة. لا يملك نبض بيانات مستشفيات من أبوظبي بعد؛ والتجربة هي ما يغيّر ذلك.")}</p></div>
      <div class="grid g3">
        <div class="card"><div class="kpi teal num">2,189</div><p style="margin-top:8px">${L("RSV admissions of children aged five or under at one Abu Dhabi hospital (Tawam) in 2018 to 2022. Infants under six months stayed 5.8 days on average.", "حالة دخول بسبب الفيروس المخلوي لأطفال في سن الخامسة أو أقل في مستشفى واحد في أبوظبي (توام) بين 2018 و2022. وبلغ متوسط إقامة الرضّع دون ستة أشهر 5.8 يوم.")}</p><div class="src mono">research/burden.md</div></div>
        <div class="card"><div class="kpi teal num">22%</div><p style="margin-top:8px">${L("of under-twos with RSV were hospitalised in Dubai claims data, and fewer than 2% had a known risk factor. It reaches ordinary families.", "من الأطفال دون السنتين المصابين بالفيروس المخلوي أُدخلوا المستشفى بحسب بيانات مطالبات دبي، وأقل من 2% لديهم عامل خطر معروف. فهو يطال الأسر العادية.")}</p><div class="src mono">research/burden.md</div></div>
        <div class="card"><div class="chips">${CH.scn()}</div><div class="kpi slate num">${a ? aed(a.central.aed_per_season) : "–"}<small> AED</small></div><p style="margin-top:8px">${L(`Scale of paediatric RSV capacity mis-planned per season that the forecast could avoid at a Tawam-sized unit, central case. Range ${a ? aed(a.low.aed_per_season) : "–"} to ${a ? aed(a.high.aed_per_season) : "–"}. A scenario built on the Gulf replay, not a measured saving.`, `حجم طاقة الأطفال المخططة خطأً في الموسم التي قد يجنّبها التوقع في وحدة بحجم توام، الحالة الوسطى. المدى من ${a ? aed(a.low.aed_per_season) : "–"} إلى ${a ? aed(a.high.aed_per_season) : "–"}. سيناريو مبني على إعادة التشغيل الخليجية، لا وفراً مقيساً.`)}</p><div class="src mono">results/replay/SUMMARY.md</div></div>
      </div>
      <div class="grid g2" style="margin-top:18px;align-items:start">
        <div class="card"><div class="chips">${CH.ill()}</div><h3>${L("Community outlook, in two languages", "نظرة للمجتمع، بلغتين")}</h3>
          <p>${L("The same card can become a plain weekly outlook for families and schools. It is shown here as a preview: it is released only after a named public-health officer approves it.", "يمكن للبطاقة نفسها أن تصبح نظرة أسبوعية مبسّطة للأسر والمدارس. تُعرض هنا كمعاينة: لا تُنشر إلا بعد اعتماد مسؤول صحة عامة مسمّى.")}</p>
          <div class="roles">${out("rsv")}${out("flu")}</div>
          <div class="src">${L("This is surveillance information, not medical advice. Follow the Department of Health's guidance on vaccination and care.", "هذه معلومات رصد وليست نصيحة طبية. اتبع إرشادات دائرة الصحة بشأن التطعيم والرعاية.")}</div></div>
        <div class="card" style="border-color:var(--teal)"><div class="eyebrow">${L("The ask", "الطلب")}</div><h3 style="font-size:1.3rem;margin:8px 0">${L("One hospital. Twelve weeks. Aggregate counts. Shadow mode.", "مستشفى واحد. اثنا عشر أسبوعاً. أعداد مجمّعة. وضع المراقبة.")}</h3>
          <p>${L("Give NABD one hospital's weekly aggregate paediatric respiratory counts, with no change to care. The exit test is set in advance: forecast error below 0.9 of the hospital's own census carried forward. If NABD misses it, the hospital walks away and the record stays on file.", "أعطوا نبض الأعداد الأسبوعية المجمّعة لحالات الجهاز التنفسي للأطفال في مستشفى واحد، من دون أي تغيير في الرعاية. معيار النجاح محدد مسبقاً: خطأ توقع دون 0.9 من تكرار أعداد المستشفى نفسها. وإن لم يبلغه نبض ينسحب المستشفى ويبقى السجل محفوظاً.")}</p>
          <div class="src">${L("Aggregate data only: person-level fields are rejected by design and small cells are suppressed (k ≥ 10).", "بيانات مجمّعة فقط: تُرفض الحقول الفردية بحكم التصميم وتُحجب الخلايا الصغيرة (k ≥ 10).")} <span class="mono">docs/PILOT-DATA-SPEC.md</span></div></div>
      </div>
      ${path()}
      <div class="grid g3" style="margin-top:18px">
        ${col(L("Real today", "حقيقي اليوم"), "pre", [L("WHO FluNet UAE surveillance data", "بيانات رصد الإمارات من WHO FluNet"), L("Weekly forecasts from two models, with ranges", "توقعات أسبوعية من نموذجين مع النطاقات"), L("The card, its consistency gate and the hash-chained approval log", "البطاقة وبوابة الاتساق وسجل الاعتماد المترابط بالتجزئة"), (D.ledger.anchors || []).length ? L(`Three registered tests and the hashed ledger (public; sent for outside timestamps ${dfmt(anchorDay(D.ledger), { day: "numeric", month: "short" })})`, `ثلاثة اختبارات مسجّلة والسجل الموثّق (منشور؛ أُرسل للختم الزمني الخارجي في ${dfmt(anchorDay(D.ledger), { day: "numeric", month: "short" })})`) : L("Three registered tests and the hashed ledger (public; outside timestamps still to do)", "ثلاثة اختبارات مسجّلة والسجل الموثّق (منشور؛ الختم الزمني الخارجي لم يُنجز بعد)")])}
        ${col(L("Scenario or illustrative", "سيناريو أو توضيحي"), "scn", [L("Bed-days and AED figures", "أرقام أيام الأسرّة والدرهم"), L("Playbook thresholds and action wording, not yet reviewed by a clinician", "عتبات دليل العمل وصياغة الإجراءات، لم يراجعها طبيب بعد"), L("The employer sickness-absence feed is simulated on synthetic data", "تغذية غياب الموظفين محاكاة على بيانات اصطناعية")])}
        ${col(L("Not built, not claimed", "غير مبني وغير مدّعى"), "wait", [L("Any Abu Dhabi hospital, district or daily data", "أي بيانات مستشفيات أو مناطق أو بيانات يومية من أبوظبي"), L("Earlier warning of when a surge starts: NABD forecasts size and duration", "إنذار أبكر ببداية الموجة: يتوقع نبض الحجم والمدة"), L("A confirmatory UAE result for the pooled model: locked, due after April 2027", "نتيجة مؤكِّدة عن الإمارات للنموذج المجمَّع: مثبّتة، وموعدها بعد أبريل 2027")])}
      </div></div></section>`;
  }

  function footer() {
    return `<footer><div class="wrap"><b>NABD نبض</b> · ${L("Future Health Digital Innovation Challenge 2026 · Statement 06, Population and Workforce Health Early Warning", "تحدي الابتكار الرقمي لصحة المستقبل 2026 · البيان 06، الإنذار المبكر لصحة السكان والقوى العاملة")}
      <ul><li>${L("Retrospective tests use WHO's finalised values; real-time versions of FluNet do not exist. Forecasts are of laboratory positivity, not hospital load.", "تستخدم الاختبارات الاستعادية القيم النهائية من المنظمة؛ ولا توجد نسخ آنية من FluNet. والتوقعات لنسبة الإيجابية المخبرية لا لحمل المستشفيات.")}</li>
      <li>${L("Data: WHO FluNet (public-health, non-commercial use, with attribution) and the CDC FluSight hub. WHO does not endorse this work. No personal or patient-level data is used.", "البيانات: WHO FluNet (استخدام غير تجاري للصحة العامة مع الإسناد) ومنصة CDC FluSight. لا تؤيد المنظمة هذا العمل. ولا تُستخدم أي بيانات شخصية أو على مستوى المريض.")}</li>
      <li>${L("Every number on this page is generated from the repository's results files", "كل رقم في هذه الصفحة مولَّد من ملفات النتائج في المستودع")} (<span class="mono">python -m web.build</span>, ${D.built_utc.slice(0, 16).replace("T", " ")} UTC).</li></ul></div></footer>`;
  }

  /* ---------------------------------------------------------------- behaviour */
  async function sha256(text) {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
    return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
  }
  async function verify(file) {
    const r = D.ledger.rounds.find(x => x.file === file);
    try { S.verify[file] = (await sha256(D.ledger.files[file])) === r.sha256; } catch { S.verify[file] = null; alert(L("This browser cannot compute SHA-256 here. Open the page over http://localhost.", "لا يستطيع المتصفح حساب SHA-256 هنا. افتح الصفحة عبر http://localhost.")); }
  }
  async function record() {
    const name = $("ap-name").value.trim(), err = $("ap-err");
    if (!name) { err.textContent = L("Enter the approver's name: no decision is recorded without one.", "أدخل اسم المعتمِد: لا يُسجَّل قرار بلا اسم."); $("ap-name").focus(); return; }
    const role = $("ap-role").value, reason = $("ap-reason").value, c = cur.cards[HEAD][S.series], pb = D.playbook;
    const prev = S.log.length ? S.log[0].hash : "0".repeat(64);
    const body = { seq: S.log.length + 1, ts: new Date().toISOString().slice(0, 19) + "Z", approver: name, role, decision: S.decision, reason_code: reason,
                   band_id: c.band ? c.band.id : null, round_file: cur.round_file, prev };
    let hash = ""; try { hash = await sha256(JSON.stringify(body)); } catch { hash = "unavailable-over-file-protocol"; }
    S.log.unshift({ ...body, hash, band: c.band ? c.band.label[S.lang] : "", roleLabel: pb.roles[role][S.lang],
                    reasonLabel: pb.reason_codes.find(r => r.code === reason)[S.lang],
                    decisionLabel: { APPROVE: L("Approved", "اعتُمد"), MODIFY: L("Modified", "عُدّل"), DISMISS: L("Dismissed", "رُفض") }[S.decision] });
    $("approval").innerHTML = approval();
  }
  function stopPlay() { if (S.rp.timer) { clearInterval(S.rp.timer); S.rp.timer = null; } }
  function applyTheme() { if (S.theme) document.documentElement.dataset.theme = S.theme; else delete document.documentElement.dataset.theme; }

  function renderAll() {
    document.documentElement.lang = S.lang; document.documentElement.dir = S.lang === "ar" ? "rtl" : "ltr";
    document.title = L("NABD نبض · Respiratory season forecasts for the UAE", "نبض NABD · توقعات المواسم التنفسية في الإمارات");
    $("nav").innerHTML = nav();
    $("app").innerHTML = hero() + how() + problem() + week() + science() + decisions() + results() + brief() + ledger() + impact() + footer();
  }
  const part = (id, html) => { const e = $(id); if (e) e.innerHTML = html; };

  document.addEventListener("click", async e => {
    const b = e.target.closest("[data-act]"); if (!b || b.tagName === "SELECT" || b.tagName === "INPUT") return;
    const a = b.dataset.act, v = b.dataset.v;
    if (a === "lang") { stopPlay(); S.lang = S.lang === "en" ? "ar" : "en"; store.set("nabd-lang", S.lang); S.log.length = 0; renderAll(); }
    else if (a === "theme") { const dark = S.theme ? S.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches; S.theme = dark ? "light" : "dark"; store.set("nabd-theme", S.theme); applyTheme(); }
    else if (a === "shape") { S.shape = v; part("problem", problem().replace(/^<section[^>]*>|<\/section>$/g, "")); }
    else if (a === "series") { S.series = v; part("card-body", cardBody()); part("why", why()); part("approval", approval()); }
    else if (a === "exw") { S.exw = Number(v); part("why", why()); }
    else if (a === "model") { S.model = v; part("card-body", cardBody()); }
    else if (a === "decision") { S.decision = v; b.parentElement.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); }
    else if (a === "record") { await record(); }
    else if (a === "rp-src") { stopPlay(); S.rp.src = v; S.rp.id = null; S.rp.model = null; part("rp-body", replayBody()); }
    else if (a === "rp-model") { S.rp.model = v; part("rp-body", replayBody()); }
    else if (a === "rp-play") {
      if (S.rp.timer) stopPlay();
      else { const n = D.replay[S.rp.id].te.length; if (S.rp.w >= n - 1) S.rp.w = 0;
             S.rp.timer = setInterval(() => { if (S.rp.w >= n - 1) { stopPlay(); } else S.rp.w++; part("rp-body", replayBody()); }, 260); }
      part("rp-body", replayBody());
    }
    else if (a === "verify") { await verify(v); part("ledger", ledger().replace(/^<section[^>]*>|<\/section>$/g, "")); }
    else if (a === "verify-all") { for (const r of D.ledger.rounds) await verify(r.file); part("ledger", ledger().replace(/^<section[^>]*>|<\/section>$/g, "")); }
  });
  document.addEventListener("input", e => {
    const el = e.target; if (el.dataset.act !== "rp-week") return;
    stopPlay(); S.rp.w = Number(el.value); const u = D.replay[S.rp.id];
    part("rp-chart", replayChart(u, S.rp.w, S.rp.model));
  });
  document.addEventListener("change", e => {
    const el = e.target;
    if (el.dataset.act === "rp-unit") { stopPlay(); S.rp.id = Number(el.value); S.rp.w = Math.floor(D.replay[S.rp.id].te.length / 2); S.rp.model = null; part("rp-body", replayBody()); }
    else if (el.dataset.act === "rp-week") part("rp-body", replayBody());
  });

  applyTheme(); renderAll();
})();
