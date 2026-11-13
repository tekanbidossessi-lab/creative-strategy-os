// adlib_links.js — on an Ad Library page (one ad: ?id=…, or an advertiser's ads: view_all_page_id=…), opened
// in Claude in Chrome or the built-in browser, no login needed. Lists every ad card with its library id, its
// start date and the page its button leads to, then groups the ads by landing page: the page that has been
// paying for traffic the longest, with the most ads, is the one to read (competitor-pages.md).
// Paste the whole file in the javascript tool (it starts with await). It returns a short summary and puts the full
// capture behind a green COPIER button: click it for real, then
//   python <cs-research>/scripts/research.py paste <dossier>            (a search: saved and imported as candidates)
//   python <cs-research>/scripts/research.py paste <dossier> --save library/competitors/<nom>.json
//   python <cs-offer>/scripts/offer.py competitor <dossier> <landing page url> --adlib library/competitors/<nom>.json
// Measured 28/10/2026 on a knee-brace seller (Côte d'Ivoire): 28 cards, landing pages on Shopify and Cauriko.
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

  const sleep = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 30 && !document.body.innerText.match(/(ID dans la bibliothèque|Library ID)/); i++) await sleep(500);
  // load more cards: scroll until the count stops growing (Meta loads ~30 at a time), at most 25 times
  const countIds = () => (document.body.innerText.match(/(ID dans la bibliothèque|Library ID)\s*:/g) || []).length;
  let last = -1, still = 0;
  for (let i = 0; i < 25 && still < 2; i++) {
    scrollTo(0, document.documentElement.scrollHeight); await sleep(1500);
    const n = countIds(); still = n === last ? still + 1 : 0; last = n;
  }
  scrollTo(0, 0);
  const shown = ((document.body.innerText.match(/~?\s?([\d\s .,]+)\s+(résultats|results)/) || [])[1] || '').replace(/\D/g, '');
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
  for (const n of idNodes) {
    const id = n.textContent.match(/\d{8,}/)[0];
    if (seen.has(id)) continue; seen.add(id);
    // the card = the highest ancestor that still holds exactly one library id (never a block of several ads)
    const ids = el => (el.innerText.match(/(ID dans la bibliothèque|Library ID)\s*:/g) || []).length;
    let c = n;
    while (c.parentElement && ids(c.parentElement) === 1) c = c.parentElement;
    const links = [...new Set([...c.querySelectorAll('a[href]')].map(a => decode(a.href))
      .filter(h => /^https?:/.test(h) && !/facebook\.com|metastatus|instagram\.com|messenger\.com|whatsapp\.com|wa\.me/.test(h))
      .map(h => h.split('?')[0].replace(/\/$/, '')))];
    const whatsapp = [...c.querySelectorAll('a[href]')].some(a => /wa\.me|whatsapp/.test(decode(a.href)));
    const startTxt = (c.innerText.match(/(Début de diffusion le|Started running on)[^\n]+/) || [''])[0];
    const versions = (c.innerText.match(/(\d+)\s+(publicités utilisent|ads use)/) || [])[1];
    const lines = c.innerText.split('\n').map(t => t.trim()).filter(Boolean);
    const sp = lines.findIndex(t => /^(Sponsorisé|Sponsored)$/.test(t));
    // the whole ad text, from « Sponsorisé » to the media or the link: a long letter is the script a brief copies
    const stop = t => /^\d+:\d{2}\s*\/\s*\d+:\d{2}$|^[A-Z0-9][A-Z0-9.-]*\.[A-Z]{2,}$|^(Commander|En savoir plus|Acheter|Shop now|Learn more|Send message|Envoyer un message)$/.test(t);
    const after = [];
    for (const t of (sp >= 0 ? lines.slice(sp + 1) : [])) { if (stop(t)) break; after.push(t); }
    const body = after.join('\n') || lines.filter(t => t.length > 40 && !/bibliothèque|Library ID/.test(t))[0] || '';
    const video = c.querySelector('video');
    const img = [...c.querySelectorAll('img')].filter(i => i.naturalWidth > 250)
      .sort((a, b) => b.naturalWidth * b.naturalHeight - a.naturalWidth * a.naturalHeight)[0];
    cards.push({ id, start: toDate(startTxt), start_text: startTxt, versions: versions ? +versions : null,
      links, whatsapp, advertiser: sp > 0 ? lines[sp - 1].slice(0, 80) : '', text: body.slice(0, 2000),
      format: video ? 'video' : (img ? 'image' : ''), video_src: video && video.src && !video.src.startsWith('blob:') ? video.src : null,
      image: !video && img ? img.src : null });
  }
  const pages = {};
  for (const c of cards) for (const l of c.links) {
    const p = pages[l] || (pages[l] = { url: l, ads: [], first_start: null });
    p.ads.push(c.id);
    if (c.start && (!p.first_start || c.start < p.first_start)) p.first_start = c.start;
  }
  const today = new Date().toISOString().slice(0, 10);
  const ranked = Object.values(pages).map(p => ({ ...p, n_ads: p.ads.length,
    days: p.first_start ? Math.round((new Date(today) - new Date(p.first_start)) / 864e5) : null }))
    .sort((a, b) => (b.days || 0) - (a.days || 0) || b.n_ads - a.n_ads);
  const count = {};
  for (const c of cards) if (c.advertiser) count[c.advertiser] = (count[c.advertiser] || 0) + 1;
  const advertiser = Object.entries(count).sort((a, b) => b[1] - a[1]).map(e => e[0])[0] || '';
  const note = shown && +shown > cards.length ? `Meta annonce ${shown} résultats, ${cards.length} lus : relance après avoir fait défiler, ou filtre par pays` : '';
  return csCopy({ probe: 'adlib', url: location.href, read_at: new Date().toISOString(), advertiser,
    n_cards: cards.length, results_shown: shown ? +shown : null, note, landing_pages: ranked, cards },
    { cartes: cards.length, annonceur: advertiser, pages: ranked.slice(0, 5).map(p => `${p.url} · ${p.n_ads} pubs · ${p.days ?? '?'} j`), note });
})();
