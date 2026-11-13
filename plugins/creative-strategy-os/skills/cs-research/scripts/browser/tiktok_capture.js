// tiktok_capture.js — TikTok search results with their real numbers (plays, comments, saves), in Claude in Chrome
// or the built-in browser (javascript tool). Paste the whole file; it starts with await.
//
// 1st run, on any tiktok.com page (the home page is fine): installs a listener on the page's own search requests
//    and returns "installé". Then run EVERY term, the first one included, through the page's search box (click it,
//    ctrl+a, type, Enter) and scroll 3 to 5 times with the mouse wheel. Never open a search by its address: the
//    page then loads its first results before the listener exists, and they are lost.
// Next runs: a short summary, and the full capture behind a green COPIER button. Click it for real, then:
//    python <cs-research>/scripts/research.py paste <dossier>      (saved in library/research/ and imported)
// Measured traps (two client researches): the listener must be in place before the first scroll; a new URL loses it;
// after 10–15 searches the tab slows down: open a fresh tab and install again.
await (async () => {
  // The bridge: the capture waits behind a green COPIER button. One REAL click on it (computer left_click) puts it
  // in the clipboard; then `python <cs-research>/scripts/research.py paste <dossier>` saves and imports it. Only a
  // short summary comes back here, so the conversation stays light (the old pipeline's speed, 31/10/2026).
  const csCopy = (data, summary) => {
    const txt = JSON.stringify(data);
    window.__csPayload = txt;
    let b = document.getElementById('cs-copy');
    if (!b) {
      b = document.createElement('button'); b.id = 'cs-copy';
      Object.assign(b.style, { position: 'fixed', top: '90px', right: '24px', zIndex: 2147483647, padding: '14px 26px',
        background: '#12A27A', color: '#fff', font: 'bold 17px sans-serif', border: '0', borderRadius: '10px', cursor: 'pointer',
        boxShadow: '0 4px 14px rgba(0,0,0,.25)' });
      document.body.appendChild(b);
    }
    b.textContent = `COPIER (${Math.max(1, Math.round(txt.length / 1024))} Ko)`;
    b.onclick = async () => {
      try { await navigator.clipboard.writeText(window.__csPayload); }
      catch (e) { const t = document.createElement('textarea'); t.value = window.__csPayload; document.body.appendChild(t);
        t.select(); document.execCommand('copy'); t.remove(); }
      b.textContent = 'COPIÉ ✓ — research.py paste';
    };
    return Object.assign({ copy: 'clique sur le bouton vert COPIER (vrai clic), puis research.py paste <dossier>' }, summary);
  };

  const q = new URLSearchParams(location.search).get('q') || '';
  if (!window.__ttHook) {
    window.__ttHook = 1;
    window.__tt = window.__tt || {};
    const add = (j, term) => {
      for (const d of (j && (j.item_list || j.data || j.itemList)) || []) {
        const x = d.item || d;
        if (x && x.id && x.stats) window.__tt[x.id] = { x, q: term };
      }
    };
    const term = () => new URLSearchParams(location.search).get('q') || '';
    const of = window.fetch;
    window.fetch = async (...a) => {
      const r = await of(...a);
      try { const u = (a[0] && a[0].url) || String(a[0]); if (/search\/(item|general)|api\/search/.test(u)) r.clone().json().then(j => add(j, term())).catch(() => {}); } catch (e) {}
      return r;
    };
    const oo = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (m, u) {
      this.__u = u;
      this.addEventListener('load', () => { if (/search\/(item|general)|api\/search/.test(this.__u)) { try { add(JSON.parse(this.responseText), term()); } catch (e) {} } });
      return oo.apply(this, arguments);
    };
    // a single video page carries its own data
    try {
      const el = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
      const it = el && JSON.parse(el.textContent).__DEFAULT_SCOPE__['webapp.video-detail'].itemInfo.itemStruct;
      if (it) window.__tt[it.id] = { x: it, q };
    } catch (e) {}
    return `installé sur « ${q} » : fais défiler 3 à 5 fois, puis relance ce script pour récupérer les vidéos`;
  }
  const items = Object.values(window.__tt).map(({ x, q }) => ({
    id: x.id, q, a: (x.author && x.author.uniqueId) || '', desc: (x.desc || '').slice(0, 220),
    lang: x.textLanguage && x.textLanguage !== 'un' ? x.textLanguage : null,
    p: x.stats.playCount, l: x.stats.diggCount, c: x.stats.commentCount, s: x.stats.collectCount, sh: x.stats.shareCount,
    d: x.video && x.video.duration, t: x.createTime, isAd: !!x.isAd,
    images: x.imagePost && x.imagePost.images ? x.imagePost.images.length : 0,
  }));
  return csCopy({ probe: 'tiktok', term: q, read_at: new Date().toISOString(), n: items.length, items },
    { videos: items.length, termes: [...new Set(items.map(i => i.q))].filter(Boolean) });
})();
