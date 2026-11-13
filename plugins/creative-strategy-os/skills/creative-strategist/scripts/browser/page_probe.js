// page_probe.js — run on an open product page (the client's or a competitor's), in Claude in Chrome or in
// the Claude app's built-in browser (javascript tool). It reads nothing private and changes nothing: it
// collects what any visitor's browser already has, as compact JSON. Save the result to a .json file, then:
//   python <cs-intake>/scripts/intake.py page <dossier> <fichier.json>      (client page)
//   python <creative-strategist>/scripts/pagefacts.py <fichier.json>        (any page, facts only)
// Best read in mobile size. It waits for the page to finish loading, scrolls to the bottom and back so lazy
// blocks and pixels load, then reads. Paste the whole file as is (it starts with await).
await (async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  for (let i = 0; i < 40 && (document.readyState !== 'complete' || !document.body); i++) await sleep(500);
  if (!document.body) return { probe: 1, error: "la page n'a pas fini de charger : attends quelques secondes et relance" };
  const H = document.documentElement.scrollHeight;
  for (const y of [H / 3, (2 * H) / 3, H]) { scrollTo(0, y); await sleep(700); }
  scrollTo(0, 0); await sleep(600);
  const clip = (s, n) => (s || '').replace(/\s+/g, ' ').trim().slice(0, n);
  const out = {
    probe: 1, method: 'browser', url: location.href, read_at: new Date().toISOString(),
    title: document.title, viewport: [innerWidth, innerHeight],
    h1: [...document.querySelectorAll('h1')].map(e => clip(e.innerText, 200)).filter(Boolean).slice(0, 3),
  };
  const meta = n => (document.querySelector(`meta[property="${n}"],meta[name="${n}"]`) || {}).content || '';
  out.meta = {
    description: meta('description'), og_title: meta('og:title'),
    price: meta('og:price:amount') || meta('product:price:amount'),
    currency: meta('og:price:currency') || meta('product:price:currency'),
  };

  // Structured data (JSON-LD Product)
  const ld = [];
  document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
    try {
      const j = JSON.parse(s.textContent);
      [].concat(j, (j && j['@graph']) || []).forEach(x => { if (x && /Product/.test([].concat(x['@type']).join())) ld.push(x); });
    } catch (e) {}
  });
  out.jsonld = ld.slice(0, 2).map(p => ({
    name: p.name, brand: (p.brand && p.brand.name) || p.brand || '',
    offers: [].concat(p.offers || []).flatMap(o => o && o.offers ? [].concat(o.offers) : [o]).slice(0, 12)
      .map(o => ({ price: o && (o.price ?? o.lowPrice), currency: o && o.priceCurrency, name: o && o.name })),
    rating: p.aggregateRating ? { value: p.aggregateRating.ratingValue, count: p.aggregateRating.reviewCount || p.aggregateRating.ratingCount } : null,
  }));

  // Shopify: the product's own JSON, same origin (works once the page itself has loaded)
  const isShopify = !!(window.Shopify || document.querySelector('script[src*="cdn.shopify.com"],link[href*="cdn.shopify.com"]'));
  if (isShopify) {
    out.platform = 'shopify';
    try {
      const path = location.pathname.replace(/\/$/, '');
      if (/\/products\//.test(path)) {
        const r = await fetch(path + '.js', { credentials: 'same-origin' });
        if (r.ok) {
          const j = await r.json();
          out.shopify = {
            title: j.title, price: j.price / 100, compare_at: j.compare_at_price ? j.compare_at_price / 100 : null,
            currency: (window.Shopify && window.Shopify.currency && window.Shopify.currency.active) || '',
            variants: (j.variants || []).slice(0, 30).map(v => ({ title: v.title, price: v.price / 100,
              compare_at: v.compare_at_price ? v.compare_at_price / 100 : null, available: v.available })),
          };
        }
      }
    } catch (e) { out.shopify_error = String(e); }
  }

  // Evidence for pagefacts.py, kept small (the result is saved to a file by hand):
  // the product's own data block, the bundle objects, the pixel snippets, the tracking calls.
  const scripts = [...document.scripts].map(s => s.textContent || '').join('\n').replace(/\\"/g, '"').replace(/\\\//g, '/');
  const html = document.documentElement.outerHTML;
  const handle = location.pathname.replace(/\/$/, '').split('/').pop();
  const at = scripts.indexOf(`"slug":"${handle}"`) >= 0 ? scripts.indexOf(`"slug":"${handle}"`) : scripts.indexOf(`"handle":"${handle}"`);
  out.data_snippets = at >= 0 ? [scripts.slice(Math.max(0, at - 300), at + 1500)] : [];
  const tiers = scripts.match(/\{[^{}]{0,300}"quantity"\s*:\s*\d+[^{}]{0,300}\}/g) || [];
  out.data_snippets.push(...tiers.filter(t => /"price"/.test(t)).slice(0, 12));
  const grab = (re, text, n, w) => { const res = []; let m; re.lastIndex = 0;
    while ((m = re.exec(text)) && res.length < n) res.push(text.slice(Math.max(0, m.index - w[0]), m.index + w[1])); return res; };
  out.pixel_snippets = grab(/fbq\(\s*['"]init|signals\/config\/|pixel_?[iI]d|pixelCode|pixel_code|ttq\.load|snaptr\(\s*['"]init|\bG-[A-Z0-9]{6,}|AW-\d{6,}|GTM-[A-Z0-9]{4,}/g,
    html.replace(/\\"/g, '"'), 25, [40, 80]);
  out.resources = performance.getEntriesByType('resource').map(e => e.name).map(u => {
    let m;
    if ((m = u.match(/facebook\.com\/tr\/?\?(.*)/))) { const q = new URLSearchParams(m[1]); return `facebook.com/tr/?id=${q.get('id')}&ev=${q.get('ev')}`; }
    if ((m = u.match(/signals\/config\/(\d+)/))) return `connect.facebook.net/signals/config/${m[1]}`;
    if ((m = u.match(/sdkid=([A-Z0-9]+)/))) return `analytics.tiktok.com/?sdkid=${m[1]}`;
    if ((m = u.match(/[?&]id=((?:G|AW|GTM)-[A-Z0-9]+)/))) return `googletagmanager.com/?id=${m[1]}`;
    return null;
  }).filter(Boolean).slice(0, 40);

  // What the pixels report at runtime
  out.runtime = {};
  try { out.runtime.fbq = window.fbq && fbq.getState ? fbq.getState().pixels.map(p => p.id) : null; } catch (e) {}
  try { out.runtime.fbq_instance = window._fbq && _fbq.instance ? Object.keys(_fbq.instance.pixelsByID || {}) : null; } catch (e) {}
  try { out.runtime.ttq = window.ttq && ttq._i ? Object.keys(ttq._i) : null; } catch (e) {}
  try { out.runtime.datalayer = Array.isArray(window.dataLayer) ? window.dataLayer.length : null; } catch (e) {}

  // What a visitor sees
  const visible = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; };
  const firstScreen = [];
  document.querySelectorAll('h1,h2,h3,p,span,button,a,li,strong,b,del,s,label').forEach(el => {
    if (firstScreen.length > 80 || el.children.length > 3) return;
    const r = el.getBoundingClientRect();
    if (r.top + scrollY < innerHeight && r.bottom > 0 && visible(el)) {
      const t = clip(el.innerText, 160); if (t && !firstScreen.includes(t)) firstScreen.push(t);
    }
  });
  out.first_screen = firstScreen.join(' | ').slice(0, 1500);
  out.body_text = (document.body.innerText || '').replace(/[ \t ]+/g, ' ').replace(/\s*\n\s*/g, '\n').trim().slice(0, 8000);
  out.buttons = [...document.querySelectorAll('button,a[role=button],input[type=submit]')].filter(visible)
    .map(b => clip(b.innerText || b.value, 60)).filter(Boolean).slice(0, 25);
  out.whatsapp = [...document.querySelectorAll('a[href*="wa.me"],a[href*="whatsapp"]')].map(a => a.href).slice(0, 5);
  out.form_fields = [...document.querySelectorAll('form input,form select,form textarea')]
    .filter(i => i.type !== 'hidden' && visible(i)).map(i => clip(i.placeholder || i.name || i.type, 40)).slice(0, 25);
  out.struck_prices = [...document.querySelectorAll('del,s,.compare-price,[class*="compare"]')].filter(visible)
    .map(e => clip(e.innerText, 40)).filter(Boolean).slice(0, 10);
  return out;
})();
