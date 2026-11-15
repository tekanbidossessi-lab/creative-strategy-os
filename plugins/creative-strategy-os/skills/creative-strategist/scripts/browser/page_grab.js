// page_grab.js — read a whole page (sign-up page, sales page, product page) for offer.py page grab, when a plain
// download fails (JS-built pages, Framer, Chariow, 429 / 403, Cloudflare). Field-tested 14–15/11/2026.
//
// HOW: open the page in the built-in browser, run this file's content with the page's name in NAME, then click the
// green SAUVERPAGE button with a REAL click (take a small screenshot first, then left_click at its place, or find
// its ref), then: python offer.py page-paste <dossier> --name <NAME>
// A local server cannot receive the page (the page blocks it): the clipboard is the way, like COPIER.
// FAQ in accordions (Framer): their answers appear only after a real click on each question, and innerText does
// not see them even open: open them with real clicks and read them on a screenshot.
await (async (NAME) => {
  await new Promise(r => setTimeout(r, 2500));
  for (let y = 0; y < document.body.scrollHeight; y += 900) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120)); }
  window.scrollTo(0, 0);
  document.querySelectorAll('details').forEach(d => d.open = true);
  const links = [...new Set([...document.querySelectorAll('a[href]')]
    .map(a => (a.innerText.trim().replace(/\s+/g, ' ').slice(0, 60) + ' -> ' + a.href))
    .filter(s => /^http/.test(s.split(' -> ')[1] || '')))].slice(0, 80);
  const forms = [...document.querySelectorAll('input,select,textarea')].map(i => i.placeholder || i.name || i.type).filter(Boolean);
  const heads = [...document.querySelectorAll('h1,h2,h3,h4')].map(h => '[' + h.tagName + '] ' + h.innerText.trim().replace(/\s+/g, ' ')).filter(s => s.length > 5);
  const vids = [...document.querySelectorAll('video,iframe')].map(v => v.tagName + ' ' + (v.src || v.currentSrc || '')).slice(0, 15);
  const players = performance.getEntriesByType('resource').map(e => e.name)
    .filter(n => /m3u8|wistia|vimeo|youtube\.com\/embed|converteai|vturb|bunny|mediadelivery|panda/i.test(n)).slice(0, 10);
  const imgs = [...document.querySelectorAll('img[alt]')].map(i => i.alt).filter(a => a && a.length > 2).slice(0, 60);
  window.__pg = `# ${NAME}\n\nURL : ${location.href}\nTitre : ${document.title}\nLu le ${new Date().toISOString().slice(0, 10)} (navigateur)\nHauteur de page : ${document.body.scrollHeight}px\n\nChamps de formulaire : ${forms.join(', ') || 'aucun'}\nVidéos / iframes : ${vids.join(' | ') || 'aucune'}\nLecteurs vidéo (réseau) : ${players.join(' | ') || 'aucun'}\nImages (alt) : ${imgs.join(' | ')}\n\nTitres :\n${heads.join('\n')}\n\nLiens :\n${links.join('\n')}\n\n---\n\n${document.body.innerText}\n`;
  let b = document.getElementById('__pgbtn'); if (b) b.remove();
  b = document.createElement('button'); b.id = '__pgbtn'; b.textContent = 'SAUVERPAGE';
  b.style.cssText = 'position:fixed;top:0;left:0;width:240px;height:90px;z-index:2147483647;background:#0a0;color:#fff;font-size:20px';
  b.onclick = () => { const t = document.createElement('textarea'); t.value = window.__pg; document.body.appendChild(t); t.select(); const ok = document.execCommand('copy'); t.remove(); b.textContent = ok ? 'OK' : 'ECHEC'; };
  document.body.appendChild(b);
  return NAME + ' : ' + window.__pg.length + ' caractères prêts · clique sur SAUVERPAGE (vrai clic), puis offer.py page-paste <dossier>';
})('NAME');
