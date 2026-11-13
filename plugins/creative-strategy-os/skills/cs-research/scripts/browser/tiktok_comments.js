// tiktok_comments.js — the comments of chosen TikTok videos, for buying intent and the customers' own words.
// Run it on any tiktok.com page (Claude in Chrome or the built-in browser, javascript tool) after replacing the IDS
// line with the videos' ids (research.py rank shows them). Paste the whole file; it starts with await.
// Click the green COPIER button it shows (a real click), then:
//   python <cs-research>/scripts/research.py paste <dossier>      (saved, and counted by research.py intent)
// It reads up to 100 comments per video (two pages of 50), through the page's own comment API, as a visitor does.
await (async () => {
  const IDS = ['7534061113365859586'];  // ← the video ids (inside the function: a second paste on the same page works)
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
  const videos = {};
  for (const id of IDS) {
    const comments = [];
    for (const cursor of [0, 50]) {
      try {
        const r = await fetch(`/api/comment/list/?aid=1988&aweme_id=${id}&count=50&cursor=${cursor}`, { credentials: 'include' });
        const j = await r.json();
        for (const c of j.comments || []) comments.push((c.text || '').replace(/\s+/g, ' ').slice(0, 180));
        if (!j.has_more) break;
      } catch (e) { break; }
      await sleep(700);
    }
    videos[id] = { read: comments.length, comments: comments.slice(0, 100) };
    await sleep(900);
  }
  return csCopy({ probe: 'tiktok_comments', read_at: new Date().toISOString(), videos },
    { videos: Object.keys(videos).length, commentaires: Object.values(videos).reduce((n, v) => n + v.read, 0) });
})();
