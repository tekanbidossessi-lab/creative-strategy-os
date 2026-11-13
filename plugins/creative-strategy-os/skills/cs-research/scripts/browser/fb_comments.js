// fb_comments.js — the comments under a Facebook ad or post, for buying intent and the customers' own words, in
// Claude in Chrome with the user's own Facebook account logged in. Read-only: it never likes, comments or shares.
// Paste the whole file in the javascript tool (it starts with await) on the post's page, after setting REF below.
//
// Finding the ad's post: in the Ad Library, open the ad (« Voir les détails de la publicité »), then the advertiser's
// Page → its posts and reels: the same video, posted on the Page, carries the ad's comments. Or ask the client for the
// link of their own ad (Ads Manager → Aperçu → « Afficher la publication avec les commentaires »).
//
// Field-tested on 02/11/2026 (a seller's posts and reels, logged in):
// - Every comment is an article labelled « Commentaire de NOM il y a … » or « Réponse de X au commentaire de Y … »;
//   inside it come the name, the date, then the text. Only those articles are read: the post's own caption,
//   Facebook's buttons (« Répondre », « Voir l'original »…) and the name never pass for a comment any more.
// - The sort menu (« Plus pertinents ») opens only on a REAL click: Facebook ignores a scripted one. Before running,
//   two real clicks (computer tool): « Plus pertinents », then « Tous les commentaires ». The script also tries to
//   pick « Tous les commentaires » in a menu left open, but that was not reliable in the test. Without it, Facebook
//   shows only its « most relevant » comments (8 of 78 on the test post), and the script says so (tri: pertinents).
// - A post opened from a Page is a window over the Page's feed: only that window is read (the feed's other posts
//   used to mix in). It scrolls the window until no new comment comes, opens « Voir N réponses », and clicks every
//   « Voir l'original » first: Facebook shows comments translated, and the suite wants the customers' own words.
// - The seller's own replies (« contactez-nous sur WhatsApp ») are kept apart: they are not the customers' words.
// Then click the green COPIER button (a real click) and run:
//    python <cs-research>/scripts/research.py paste <dossier>      (saved, and counted by research.py intent)
const REF = 'AL01';   // ← the reference code (or the library id) these comments belong to
const PAGE = '';      // ← the advertiser's name, to set its replies apart (empty: read from the page title)
await (async () => {
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
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const shown = e => e.offsetParent !== null;
  const IS_COMMENT = '[role=article][aria-label^="Commentaire"],[role=article][aria-label^="Réponse"],[role=article][aria-label^="Comment"],[role=article][aria-label^="Reply"]';
  // a post opened from a Page is a window over the Page's feed: read that window only, never the posts behind it
  const rootOf = () => [...document.querySelectorAll('[role=dialog]')].filter(d => d.querySelector(IS_COMMENT)).pop() || document;
  let root = rootOf();
  const clickText = (re, sel = 'div[role=button],span[role=button],div[role=menuitem],span', all = false) => {
    const els = [...root.querySelectorAll(sel)].filter(e => re.test((e.innerText || '').trim()) && shown(e));
    for (const el of all ? els : els.slice(0, 1)) el.click();
    return els.length > 0;
  };
  // the sort menu, opened by the real click before the run: pick « Tous les commentaires » (the menu sits outside)
  let sort = 'tous', item = null;
  for (let i = 0; i < 6 && !item; i++) {   // the menu takes a moment to open after the real click
    item = [...document.querySelectorAll('[role=menuitem]')].find(e => /^(Tous les commentaires|All comments)/i.test((e.innerText || '').trim()));
    if (!item) await sleep(500);
  }
  if (item) item.click();
  else {
    const current = [...root.querySelectorAll('[role=button]')].map(b => (b.innerText || '').trim())
      .find(t => /^(Plus pertinents|Most relevant|Tous les commentaires|All comments|Les plus récents|Newest)$/i.test(t));
    sort = current && /pertinent|relevant/i.test(current) ? 'pertinents' : 'tous';
  }
  await sleep(1500);
  root = rootOf();
  // more comments and their replies: buttons, and the window's own scroll, until nothing new comes twice in a row
  const scroller = root === document ? document.scrollingElement
    : [...root.querySelectorAll('div')].filter(d => d.scrollHeight > d.clientHeight + 50 && /auto|scroll/.test(getComputedStyle(d).overflowY))
        .sort((a, b) => b.scrollHeight - a.scrollHeight)[0];
  let last = -1, still = 0;
  for (let i = 0; i < 40 && still < 2; i++) {
    clickText(/^(Voir plus de commentaires|Afficher plus de commentaires|Voir les commentaires précédents|View more comments|See more comments)/i);
    clickText(/^(Voir|Afficher) (les |la )?(\d+ )?(autres? )?réponses?|^View \d* ?(more )?repl/i, undefined, true);
    if (scroller) scroller.scrollTop = scroller.scrollHeight;
    await sleep(1600);
    const n = root.querySelectorAll(IS_COMMENT).length;
    still = n === last ? still + 1 : 0;
    last = n;
  }
  // the customers' own words: Facebook shows comments translated; « Voir l'original » brings them back
  clickText(/^(Voir l[’']original|See original)/i, '[role=button],span', true);
  await sleep(800);
  for (let i = 0; i < 15; i++) { if (!clickText(/^(Voir plus|En voir plus|See more)$/i)) break; await sleep(300); }

  const title = document.title.replace(/^\(\d+\)\s*/, '').split(/\s[-|]\s/)[0].trim();
  const header = root === document ? '' : ([...root.querySelectorAll('h2, h3')].map(e => (e.innerText || '').trim())
    .map(t => (t.match(/^(?:Publication de|Post by|Reel de|Vidéo de)\s+(.+)$/i) || [])[1]).find(Boolean) || '');
  const page = (PAGE || header || (/^facebook$/i.test(title) ? '' : title)).toLowerCase();
  const UI = /^(J[’']aime|Répondre|Partager|Voir l[’']original.*|Voir la traduction|Masquer la traduction|Notez cette traduction|En voir plus|Voir plus|Modifié|Auteur|Fan engagé|Top fan|Like|Reply|Share|See translation|See original|par l[’']auteur(ice)?|\d+\s*(sem|semaines?|j|jours?|h|heures?|min|minutes?|an|ans|mois|w|weeks?|d|days?|y|years?)\.?)$/i;
  const LABEL = /^(Commentaire de|Réponse de|Comment by|Reply by|Reply from)\s/i;
  const seen = new Set();
  const comments = [], seller = [];
  for (const a of root.querySelectorAll('[role=article][aria-label]')) {
    const label = a.getAttribute('aria-label') || '';
    if (!LABEL.test(label)) continue;
    const author = (label.replace(LABEL, '').match(/^(.+?)(?=\s+au commentaire de|\s+to\s|\s+il y a|\s+\d|$)/i) || [])[1] || '';
    const to = (label.match(/au commentaire de\s+(.+?)\s+il y a/i) || [])[1] || '';
    const links = new Set([...a.querySelectorAll('a')].filter(x => x.closest('[role=article]') === a).map(x => (x.innerText || '').trim()));
    const parts = [...a.querySelectorAll('div[dir=auto], span[dir=auto]')].filter(e => e.closest('[role=article]') === a)
      .map(e => (e.innerText || '').replace(/\s+/g, ' ').trim())
      .filter(t => t && t !== author && !links.has(t) && !UI.test(t));
    let text = (parts[0] || '').replace(/…?\s*(En voir plus|Voir plus|See more)$/i, '').trim();
    if (to && text.startsWith(to)) text = text.slice(to.length).trim();   // a reply opens on the name it answers
    if (!text || seen.has(author + '|' + text)) continue;
    seen.add(author + '|' + text);
    (page && author.toLowerCase() === page ? seller : comments).push(text.slice(0, 300));
  }
  const videos = { [REF]: { read: comments.length, comments: comments.slice(0, 200), seller_replies: seller.slice(0, 30),
                            url: location.href, source: 'facebook', sort } };
  return csCopy({ probe: 'comments', source: 'facebook', read_at: new Date().toISOString(), videos },
    { reference: REF, commentaires: comments.length, reponses_du_vendeur: seller.length, exemples: comments.slice(0, 3),
      tri: sort === 'pertinents' ? '« Plus pertinents » seulement : un vrai clic sur le menu, puis relance, pour tous les lire' : 'tous les commentaires' });
})();
