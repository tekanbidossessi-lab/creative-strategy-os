// instagram_capture.js — Instagram posts and reels with their numbers (plays, likes, comments), in Claude in Chrome
// with the user's own Instagram account logged in (Instagram shows little without it). Read-only: it never likes,
// follows or comments. Paste the whole file in the javascript tool; it starts with await.
//
// Field-tested 31/10/2026 on a logged-in account (« genouillère »: 96 posts in 4 scrolls, 24/24 of the
// first batch, then 111 through COPIER and research.py paste):
// - A page load wipes the listener. So never open a search by its URL once installed: set GO below instead, and
//   the script opens it inside the page (the listener stays, and the first batch is read too).
// - Instagram's search box only suggests accounts; keyword results exist only at /explore/search/keyword/?q=…
//   (hashtag pages now redirect there). GO does it for you.
// - Keyword results carry likes, comments, caption and date, never the plays. The plays are only in an author's
//   Reels grid: GO = '@author' adds them to the posts a search already found (never new posts). research.py rank falls back on the likes when plays are missing, and the download
//   step fills the plays from yt-dlp for the references kept.
//
// 1. GO = 'genouillère' (or '#genouillere'), paste: listener installed, results opened in the page.
// 2. Scroll 3 to 5 times (the mouse wheel, or ask Claude to scroll). Next term: change GO, paste again.
// 3. GO = '' and paste: a short summary, and the full capture behind a green COPIER button. Click it for real, then:
//    python <cs-research>/scripts/research.py paste <dossier>
await (async () => {
  const GO = '';  // ← the word to open ('genouillère', '#genouillere', '@author'), or '' to install / copy
  // The bridge: see adlib_links.js. One real click on COPIER, then research.py paste.
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

  // the searched word; on an author's Reels, the last word searched (the reels came from it)
  const term = () => {
    const m = location.pathname.match(/\/explore\/tags\/([^/]+)/) || location.search.match(/[?&]q=([^&]+)/);
    if (m) window.__igTerm = decodeURIComponent(m[1]).replace(/\+/g, ' ');
    return window.__igTerm || '';
  };
  const links = () => [...document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]')]
    .map(a => a.getAttribute('href').split('/').filter(Boolean).pop());
  // opens a page inside Instagram's own router: no reload, the listener stays
  const open = async path => {
    history.pushState({}, '', path);
    dispatchEvent(new PopStateEvent('popstate', { state: {} }));
    await new Promise(r => setTimeout(r, 5000));
  };
  // any object that looks like a post: a short code, an author, and at least one number
  const walk = (j, t, depth = 0) => {
    if (!j || typeof j !== 'object' || depth > 14) return;
    if (Array.isArray(j)) { for (const x of j) walk(x, t, depth + 1); return; }
    const code = j.code || j.shortcode;
    const user = j.user || j.owner;
    if (code && user && (j.like_count != null || j.play_count != null || j.view_count != null || j.comment_count != null
        || (j.edge_liked_by && j.edge_liked_by.count != null))) {
      const old = window.__ig[code];
      // an author's Reels only add the plays to posts a search found: its other reels carry no caption, so
      // nothing says they are about the product. The same post seen again keeps its first term.
      if (!old) { if (!/\/reels\/?$/.test(location.pathname)) window.__ig[code] = { x: j, term: t }; }
      else if (j.play_count != null && old.x.play_count == null) old.x = Object.assign({}, old.x, { play_count: j.play_count });
    }
    for (const k in j) if (j[k] && typeof j[k] === 'object') walk(j[k], t, depth + 1);
  };
  const fresh = !window.__igHook;
  if (fresh) {
    window.__igHook = 1;
    window.__ig = window.__ig || {};
    const of = window.fetch;
    window.fetch = async (...a) => {
      const r = await of(...a);
      try { const u = (a[0] && a[0].url) || String(a[0]); if (/graphql|\/api\/v1\//.test(u)) r.clone().json().then(j => walk(j, term())).catch(() => {}); } catch (e) {}
      return r;
    };
    const oo = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (m, u) {
      this.__u = u;
      this.addEventListener('load', () => { if (/graphql|\/api\/v1\//.test(this.__u)) { try { walk(JSON.parse(this.responseText), term()); } catch (e) {} } });
      return oo.apply(this, arguments);
    };
    for (const s of document.querySelectorAll('script[type="application/json"]')) { try { walk(JSON.parse(s.textContent), term()); } catch (e) {} }
  }
  if (GO) {
    const g = GO.trim();
    const path = g.startsWith('@') ? `/${g.slice(1)}/reels/` : `/explore/search/keyword/?q=${encodeURIComponent(g)}`;
    await open(path);
    const seen = links();
    return `ouvert : ${location.pathname}${location.search} · ${seen.filter(c => window.__ig[c]).length}/${seen.length} publications affichées lues `
      + `(${Object.keys(window.__ig).length} en tout). Fais défiler 3 à 5 fois, puis GO suivant, ou GO = '' pour copier.`;
  }
  if (fresh) {
    // installed on a page that already shows posts: they came before the listener, so open the page again inside it
    const seen = links();
    if (seen.length && !seen.some(c => window.__ig[c])) {
      const here = location.pathname + location.search;
      await open('/explore/');
      await open(here);
    }
    const now = links();
    return `installé : ${now.filter(c => window.__ig[c]).length}/${now.length} publications affichées lues. `
      + `Mets un mot dans GO et relance (n'ouvre pas les recherches par leur adresse : ça efface l'écoute).`;
  }
  const num = v => (v == null ? null : +v);
  const items = Object.entries(window.__ig).map(([code, { x, term: t }]) => {
    const u = x.user || x.owner || {};
    const cap = x.caption && (x.caption.text || x.caption) || (x.edge_media_to_caption && x.edge_media_to_caption.edges[0] && x.edge_media_to_caption.edges[0].node.text) || '';
    const kind = x.media_type === 2 || x.is_video || x.product_type === 'clips' ? 'Video' : (x.media_type === 8 || x.carousel_media ? 'Sidecar' : 'Image');
    return { shortCode: code, ownerUsername: u.username || '', term: t,
      videoPlayCount: num(x.play_count ?? x.ig_play_count ?? x.video_view_count ?? x.view_count),
      likesCount: num(x.like_count ?? (x.edge_liked_by && x.edge_liked_by.count)),
      commentsCount: num(x.comment_count ?? (x.edge_media_to_comment && x.edge_media_to_comment.count)),
      videoDuration: num(x.video_duration), type: kind, caption: String(cap).slice(0, 600),
      timestamp: x.taken_at ? new Date(x.taken_at * 1000).toISOString() : null,
      url: `https://www.instagram.com/${kind === 'Video' ? 'reel' : 'p'}/${code}/`,
      videoUrl: (x.video_versions && x.video_versions[0] && x.video_versions[0].url) || null,
      displayUrl: (x.image_versions2 && x.image_versions2.candidates && x.image_versions2.candidates[0] && x.image_versions2.candidates[0].url) || null };
  });
  return csCopy({ probe: 'instagram', term: term(), read_at: new Date().toISOString(), n: items.length, items },
    { posts: items.length, avec_vues: items.filter(i => i.videoPlayCount != null).length,
      termes: [...new Set(items.map(i => i.term))].filter(Boolean),
      top: items.sort((a, b) => (b.videoPlayCount || b.likesCount || 0) - (a.videoPlayCount || a.likesCount || 0)).slice(0, 5)
        .map(i => `${i.ownerUsername} · ${i.videoPlayCount ?? '?'} vues · ${i.likesCount ?? '?'} j'aime`) });
})();
