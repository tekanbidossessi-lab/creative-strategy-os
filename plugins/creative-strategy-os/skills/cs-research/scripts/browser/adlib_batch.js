// adlib_batch.js — many Ad Library searches in a row without pasting a long script each time (built-in browser or
// Claude in Chrome, no login). Measured 01/11/2026: logged out, Meta shows only the first page of a search (about 25
// to 30 ads, never more on scroll), so breadth comes from many searches, and pasting adlib_links.js 76 times costs too
// much. The Ad Library refuses frames, popups and in-page navigation, so the reader lives in the site's IndexedDB
// (Facebook wipes unknown localStorage keys between page loads: 183 ads lost that way on the first try).
//
// 1. Open any Ad Library page, paste this whole file once: it stores itself and reads the page.
// 2. For every other search: navigate to its URL (research.py plan prints them), then run the one line below. It
//    loads the stored reader as a blob: script (Facebook's policy blocks eval on some loads, allows blob:, 01/11/2026):
//      await new Promise(r=>{const q=indexedDB.open('cs_research',1);q.onupgradeneeded=()=>q.result.createObjectStore('kv');q.onsuccess=()=>{const g=q.result.transaction('kv').objectStore('kv').get('src');g.onsuccess=()=>{const s=document.createElement('script');s.src=URL.createObjectURL(new Blob(['window.__csRun=',g.result],{type:'text/javascript'}));s.onload=r;document.head.appendChild(s)}}});await window.__csRun('read')
//    Batch 10 searches per browser_batch call (navigate + this line, 25 actions at most).
// 3. Every 10 searches or so, and at the end, await window.__csRun('copy') puts everything read behind the green
//    COPIER button; real click, then research.py paste <dossier> (each search keeps its own term and country). Then
//    __csRun('clear') empties the store before the next round; ('count') says what is stored. Measured 01/11/2026:
//    83 searches, 909 ads in about 40 minutes. Logged out, a page shows ~30 ads: to see more of one advertiser, split
//    view_all_page_id by country, media_type, active_status or start_date[min]/[max].
await (async () => {
  const run = async (mode) => {
    const kv = async (key, val) => {
      const db = await new Promise((res, rej) => { const r = indexedDB.open('cs_research', 1);
        r.onupgradeneeded = () => r.result.createObjectStore('kv'); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); });
      return new Promise((res, rej) => {
        const t = db.transaction('kv', val === undefined ? 'readonly' : 'readwrite'), st = t.objectStore('kv');
        const q = val === undefined ? st.get(key) : (val === null ? st.delete(key) : st.put(val, key));
        q.onsuccess = () => res(q.result); q.onerror = () => rej(q.error); });
    };
    const load = async () => { try { return JSON.parse((await kv('caps')) || '[]'); } catch (e) { return []; } };
    const save = caps => kv('caps', JSON.stringify(caps));
    if (mode === 'clear') { await kv('caps', null); return 'vidé'; }
    if (mode === 'count') { const c = await load(); return `${c.length} recherches, ${c.reduce((n, x) => n + x.cards.length, 0)} pubs en mémoire`; }
    if (mode === 'copy') {
      const caps = await load();
      const txt = JSON.stringify({ probe: 'batch', read_at: new Date().toISOString(), captures: caps });
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
      return { copy: 'clique sur le bouton vert COPIER (vrai clic), puis research.py paste <dossier>, puis (\'clear\')',
        recherches: caps.length, pubs: caps.reduce((n, x) => n + x.cards.length, 0) };
    }
    // read the page: the same reading as adlib_links.js, one capture per search URL
    const sleep = ms => new Promise(r => setTimeout(r, ms));
    const RX = /(ID dans la bibliothèque|Library ID)\s*:/g;
    for (let i = 0; i < 30 && !document.body.innerText.match(RX); i++) await sleep(500);
    const countIds = () => (document.body.innerText.match(RX) || []).length;
    let last = -1, still = 0;
    // Logged out a page stops at ~30 ads and the loop ends after the still rounds. Logged in it loads 30 more every 5 s
    // or so, sorted by impressions (measured 01/11/2026), so the top of a search is what Meta showed most: stop at
    // window.__csMax ads (210 by default).
    const max = window.__csMax || 210;
    // and the Chrome extension drops a call after 45 s: stop scrolling 38 s after the page started loading
    for (let i = 0; i < 80 && still < 4 && last < max && performance.now() < (window.__csBudget || 38000); i++) {
      scrollTo(0, document.documentElement.scrollHeight); await sleep(2500);
      const n = countIds(); still = n === last ? still + 1 : 0; last = n;
    }
    scrollTo(0, 0);
    const shown = ((document.body.innerText.match(/~?\s?([\d\s .,]+)\s+(résultats|results)/) || [])[1] || '').replace(/\D/g, '');
    const decode = h => { try { const u = new URL(h); return u.hostname === 'l.facebook.com' ? (u.searchParams.get('u') || h) : h; } catch (e) { return h; } };
    const months = { janv: 1, jan: 1, févr: 2, fév: 2, feb: 2, mars: 3, mar: 3, avr: 4, apr: 4, mai: 5, may: 5, juin: 6, jun: 6,
      juil: 7, jul: 7, août: 8, aug: 8, sept: 9, sep: 9, oct: 10, nov: 11, déc: 12, dec: 12 };
    const toDate = s => { s = s && s.replace(/(\d)er\b/, '$1'); const m = s && s.match(/(\d{1,2})\s+([a-zéû]+)\.?\s+(\d{4})|([A-Z][a-z]{2})\w*\s+(\d{1,2}),\s+(\d{4})/i);
      if (!m) return null; const mon = months[(m[2] || m[4] || '').toLowerCase().slice(0, 4)] || months[(m[2] || m[4] || '').toLowerCase().slice(0, 3)];
      const d = +(m[1] || m[5]), y = +(m[3] || m[6]); return mon ? `${y}-${String(mon).padStart(2, '0')}-${String(d).padStart(2, '0')}` : null; };
    const idNodes = [...document.querySelectorAll('span,div')].filter(e => e.children.length === 0 &&
      /^(ID dans la bibliothèque|Library ID)\s*:\s*\d+/.test(e.textContent.trim()));
    const seen = new Set();
    const cards = [];
    const ids = el => (el.innerText.match(RX) || []).length;
    for (const n of idNodes) {
      const id = n.textContent.match(/\d{8,}/)[0];
      if (seen.has(id)) continue; seen.add(id);
      let c = n;
      while (c.parentElement && ids(c.parentElement) === 1) c = c.parentElement;
      const links = [...new Set([...c.querySelectorAll('a[href]')].map(a => decode(a.href))
        .filter(h => /^https?:/.test(h) && !/facebook\.com|metastatus|instagram\.com|messenger\.com|whatsapp\.com|wa\.me/.test(h))
        .map(h => h.split('?')[0].replace(/\/$/, '')))];
      const startTxt = (c.innerText.match(/(Début de diffusion le|Started running on)[^\n]+/) || [''])[0];
      // an inactive ad shows « 20 juil 2026 - 21 août 2026 »: its real run, start and end (01/11/2026)
      const span = c.innerText.match(/\n([^\n]{6,20}\d{4})\s+-\s+([^\n]{6,20}\d{4})\n/);
      const page = ([...c.querySelectorAll('a[href*="facebook.com"]')].map(a => a.href)
        .find(h => !/ads\/library|l\.facebook|\/policies|\/help/.test(h)) || '').split('?')[0];
      const versions = (c.innerText.match(/(\d+)\s+(publicités utilisent|ads use)/) || [])[1];
      const lines = c.innerText.split('\n').map(t => t.trim()).filter(Boolean);
      const sp = lines.findIndex(t => /^(Sponsorisé|Sponsored)$/.test(t));
      const stop = t => /^\d+:\d{2}\s*\/\s*\d+:\d{2}$|^[A-Z0-9][A-Z0-9.-]*\.[A-Z]{2,}$|^(Commander|En savoir plus|Acheter|Shop now|Learn more|Send message|Envoyer un message|S'inscrire|Sign up|Réserver|Book now)$/.test(t);
      const after = [];
      for (const t of (sp >= 0 ? lines.slice(sp + 1) : [])) { if (stop(t)) break; after.push(t); }
      const body = after.join('\n') || lines.filter(t => t.length > 40 && !/bibliothèque|Library ID/.test(t))[0] || '';
      const video = c.querySelector('video');
      const img = [...c.querySelectorAll('img')].filter(i => i.naturalWidth > 250)
        .sort((a, b) => b.naturalWidth * b.naturalHeight - a.naturalWidth * a.naturalHeight)[0];
      cards.push({ id, start: toDate(startTxt) || (span && toDate(span[1])), end: span ? toDate(span[2]) : null,
        active: !/\n(Inactive|Inactif)\n/.test('\n' + c.innerText + '\n'), page, versions: versions ? +versions : null, links,
        advertiser: sp > 0 ? lines[sp - 1].slice(0, 80) : '', text: Array.from(body).slice(0, 1500).join(''),
        format: video ? 'video' : (img ? 'image' : ''),
        video_src: video && video.src && !video.src.startsWith('blob:') ? video.src : null,
        image: !video && img ? img.src : null });
    }
    const caps = (await load()).filter(x => x.url !== location.href);
    caps.push({ probe: 'adlib', url: location.href, read_at: new Date().toISOString(), n_cards: cards.length,
      results_shown: shown ? +shown : null, cards });
    try { await save(caps); } catch (e) { return `mémoire pleine (${caps.length} recherches) : lance ('copy'), colle, puis ('clear')`; }
    const q = new URLSearchParams(location.search);
    return `${q.get('country') || ''} « ${q.get('q') || q.get('view_all_page_id') || ''} » : ${cards.length} pubs lues`
      + (shown ? ` sur ${shown}` : '') + ` · en mémoire : ${caps.length} recherches, ${caps.reduce((n, x) => n + x.cards.length, 0)} pubs`;
  };
  await new Promise(res => { const r = indexedDB.open('cs_research', 1);
    r.onupgradeneeded = () => r.result.createObjectStore('kv');
    r.onsuccess = () => { const t = r.result.transaction('kv', 'readwrite'); t.objectStore('kv').put('(' + run.toString() + ')', 'src'); t.oncomplete = res; }; });
  return run('read');
})();
