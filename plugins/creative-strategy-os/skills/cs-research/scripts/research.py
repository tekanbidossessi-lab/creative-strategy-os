"""research.py — the research step of the creative-strategy suite: find, choose, download, transcribe and read the
references that already sold or went viral, so every script of the plan can start from one, word for word.

    python research.py plan       <dossier> --terms "genouillère, douleur genou, knee pain@en" [--countries GN,CI,FR,US] [--refs 40]
    python research.py paste      <dossier> [--term T] [--save fichier.json]   a browser capture copied with COPIER
    python research.py discover   <dossier> [--platform adlib|tiktok|instagram] [--limit 40] [--dry-run] [--yes] [--all]
    python research.py import     <dossier> <capture.json | apify.json | liens.txt> [--term T] [--country CC] [--lang fr]
    python research.py rank       <dossier> [--platform adlib|tiktok|instagram] [--top 20]
    python research.py pick       <dossier> <id ...> [--why "…"]   |   pick <dossier> --auto [--adlib 25 --tiktok 30]
    python research.py reject     <dossier> <id ...> --reason "…"
    python research.py download   <dossier> [CODE ...]
    python research.py transcribe <dossier> [CODE ...] [--model small|medium|auto] [--fast]
    python research.py sheet      <dossier> [--platform tiktok|adlib|instagram|all]
    python research.py frames     <dossier> <CODE> [--auto 6 | 0 3 8.5 ...]
    python research.py analyse    <dossier> <CODE ...> | --all [--engine gemini|frames|pack] [--answer vu.md]
    python research.py intent     <dossier> <comments.json>
    python research.py hooks      <dossier>                       the openings of the corpus, from the transcripts
    python research.py check      <dossier> [<id> <statut> --evidence "…"]
    python research.py status     <dossier>
    python research.py log        <dossier>                       REFERENCES_LOG.xlsx
    python research.py report     <dossier> [--done]               deliverables/RECHERCHE.md

Files (creative-strategist/references/workspace.md): library/research.yaml (the search plan), library/candidates.yaml
(everything found, with its numbers and score), library/references.yaml (the chosen ones, coded AL/TT/IG/YT/CL),
References/<Plateforme>/<CODE>_<PAYS|LANGUE>_<nom>_<id>.<ext>, References/Transcripts/, Frames/, Analyses/, _sheets/,
library/voice/ (comments: buying intent, objections, the customers' words), audit.yaml (the research checks).

Édition sous licence : seules les commandes analyse, discover, download, frames, import, paste, sheet, transcribe, voice tournent ici ; les autres partent sur le serveur de licence."""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parent
SUITE = HERE.parent.parent / 'creative-strategist' / 'scripts'
if not (SUITE / 'ws.py').exists():
    print(f'ERREUR : le skill creative-strategist doit être installé à côté de cs-research (attendu : {SUITE}).', file=sys.stderr)
    sys.exit(2)
sys.path.insert(0, str(SUITE))
import ws as W
import kinds as K
from ws import WsError, open_ws, load_yaml, dump_yaml, journal, refresh, today, read_text
PROMPT = HERE.parent / 'templates' / 'analyse_prompt.md'
PLATFORMS = {'adlib': ('AL', 'AdLibrary'), 'tiktok': ('TT', 'TikTok'), 'instagram': ('IG', 'Instagram'), 'youtube': ('YT', 'YouTube'), 'client': ('CL', 'Client')}
FR_COUNTRIES = {'SN', 'CI', 'CM', 'BJ', 'TG', 'ML', 'BF', 'GN', 'NE', 'CD', 'CG', 'GA', 'TD', 'MG', 'FR', 'BE', 'CH', 'CA', 'MA', 'TN', 'DZ', 'HT', 'RW', 'BI', 'CF', 'DJ', 'KM', 'MR'}
EN_COUNTRIES = {'US', 'GB', 'UK', 'NG', 'GH', 'KE', 'ZA', 'UG', 'TZ', 'AU', 'IE', 'IN', 'PH', 'LR', 'SL', 'GM', 'ZM', 'ZW'}
ACTORS = {'adlib': 'apify~facebook-ads-scraper', 'tiktok': 'clockworks~tiktok-scraper', 'instagram': 'apify~instagram-scraper'}
APIFY_PRICE_PER_1000 = {'adlib': 5.8, 'tiktok': 4.0, 'instagram': 2.7}
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
INTENT_PHRASES = ['\\bprix\\b', '\\btarif', '\\bcombien\\b(?! de (?:temps|jours|semaines|mois|fois))', '\\bfcfa\\b|\\bcfa\\b|\\bgnf\\b', "\\bou (?:on )?(?:peut|puis|pourrais)[- ](?:je |on )?(?:l'?)?(?:acheter|avoir|trouver|commander)", '\\bou (?:est|se trouve) (?:la boutique|le magasin|votre boutique)', '\\bvous livrez\\b|\\blivr(?:ez|aison|er|e) (?:a|au|en|sur)\\b', "\\bje (?:la |le |les )?veux\\b|\\bj'en veux\\b|\\bje voudrais (?:en |l'?)?(?:avoir|acheter|commander)", '\\binteress[ée]e?s?\\b', "\\bcomment (?:commander|l'avoir|en avoir|acheter)\\b", '\\ble lien\\b|\\bun lien\\b|\\blink\\b', '\\bnumero\\b|\\bwhatsapp\\b|\\binbox\\b|\\bdm\\b', '\\bdisponible\\b.*\\?', '\\bcommander\\b', '\\bhow much\\b', '\\bprice\\b', '\\bwhere (?:can|do) i (?:get|buy|order)\\b', '\\bdo you (?:deliver|ship)\\b', '\\binterested\\b', '\\bi want (?:one|it|this|to buy)\\b', '\\bhow (?:can|do) i (?:order|get)\\b']
OBJECTIONS = K.OBJECTIONS['product']

def slug(s, n=20):
    """A file-name part: accents dropped, letters and digits only (Windows, Drive and editors all accept it)."""
    s = unicodedata.normalize('NFKD', str(s or ''))
    s = ''.join((c for c in s if not unicodedata.combining(c)))
    s = re.sub('[^A-Za-z0-9]+', '-', s).strip('-')
    return s[:n].strip('-') or 'x'

def fold(s):
    """Lower case, accents dropped, apostrophes unified: for matching words people type."""
    s = unicodedata.normalize('NFKD', str(s or '').lower().replace('’', "'"))
    return ''.join((ch for ch in s if not unicodedata.combining(ch)))

def days_between(a, b=None):
    try:
        start = dt.date.fromisoformat(str(a)[:10])
        end = dt.date.fromisoformat(str(b)[:10]) if b else dt.date.today()
        return max(0, (end - start).days)
    except ValueError:
        return None

def lang_of_country(cc):
    cc = (cc or '').upper()
    return 'fr' if cc in FR_COUNTRIES else 'en' if cc in EN_COUNTRIES else None

def files(P):
    lib = P['root'] / 'library'
    return {'plan': lib / 'research.yaml', 'cands': lib / 'candidates.yaml', 'refs': P['refs_index'], 'raw': lib / 'research', 'voice': lib / 'voice'}

def load_list(path, key):
    data = load_yaml(path, {}) or {}
    if not isinstance(data, dict):
        raise WsError(f"{path.name} n'a pas la bonne forme (il faut « {key}: [...] »)")
    if not isinstance(data.get(key), list):
        data[key] = []
    return data

def save_refs(path, data):
    """Write references.yaml without losing what another command wrote meanwhile (01/11/2026: transcribe, running
    in the background, rewrote the file from its memory and erased 15 references that pick had just added).
    Re-read the file just before writing: a reference missing here is kept, and a field missing here is kept."""
    try:
        disk = load_list(path, 'references')['references'] if path.exists() else []
    except Exception:
        disk = []
    mine = {r.get('code'): r for r in data['references'] if r.get('code')}
    for r in disk:
        c = r.get('code')
        if c and c not in mine:
            data['references'].append(r)
        elif c:
            for (k, v) in r.items():
                mine[c].setdefault(k, v)
    data['references'].sort(key=lambda r: (str(r.get('code') or '')[:2], int(re.sub('\\D', '', str(r.get('code') or '')) or 0)))
    dump_yaml(path, data)

def cand_key(platform, cid):
    return f'{platform}:{cid}'

def ref_by_code(refs, code):
    return next((r for r in refs if str(r.get('code')) == code.upper()), None)

def adlib_search_url(country, term):
    q = urllib.parse.quote(term)
    return f'https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country}&is_targeted_country=false&media_type=all&q={q}&search_type=keyword_unordered&sort_data[mode]=total_impressions&sort_data[direction]=desc'
MEDIA_EXT = ('.mp4', '.mov', '.webm', '.jpg', '.jpeg', '.png', '.webp')

def media_files(P, ref):
    sub = P['refs_dir'] / PLATFORMS[ref['platform']][1]
    base = ref.get('base') or ''
    return sorted((f for f in sub.glob(base + '*') if f.suffix.lower() in MEDIA_EXT))

def is_video(path):
    return str(path).lower().endswith(('.mp4', '.mov', '.webm'))

def readable(path):
    """True when the file really is a picture or a video (a download can be an error page)."""
    try:
        if is_video(path):
            import av
            with av.open(str(path)) as c:
                return bool(c.streams.video)
        from PIL import Image
        with Image.open(path) as im:
            im.verify()
        return True
    except Exception:
        return False

def running_days(c):
    """From the start date to the end date, or to today when still running: recomputed each time, never frozen."""
    if not c.get('started_on'):
        return c.get('running_days')
    return days_between(c['started_on'], c.get('ended_on'))

def save_plan(F, plan):
    dump_yaml(F['plan'], plan)

def card_text(c, snap, cards):
    """The ad's text; dynamic ads (DCO) carry « {{product.brand}} » templates in the body, the cards hold the text."""
    body = snap.get('body')
    t = c.get('text') or (body.get('text') if isinstance(body, dict) else body) or ''
    if not t or '{{' in str(t):
        t = next((x.get('body') for x in cards if x.get('body') and '{{' not in str(x.get('body'))), t)
    return str(t or '')

def norm_adlib_card(c, term, country):
    cid = str(c.get('id') or c.get('adArchiveID') or c.get('adArchiveId') or '')
    snap = c.get('snapshot') or {}
    cards = snap.get('cards') or []
    first = cards[0] if cards else {}
    videos = snap.get('videos') or []
    images = snap.get('images') or []
    video = first.get('videoHdUrl') or first.get('videoSdUrl') or (videos[0].get('videoHdUrl') if videos else None) or c.get('video_src')
    image = first.get('originalImageUrl') or first.get('resizedImageUrl') or (images[0].get('originalImageUrl') if images else None) or c.get('image')
    start = c.get('start') or (c.get('startDateFormatted') or '')[:10] or None
    if isinstance(c.get('startDate'), (int, float)):
        start = dt.datetime.utcfromtimestamp(c['startDate']).date().isoformat()
    end = None
    if c.get('isActive') is False or c.get('is_active') is False:
        end = (c.get('endDateFormatted') or '')[:10] or None
        if isinstance(c.get('endDate'), (int, float)):
            end = dt.datetime.utcfromtimestamp(c['endDate']).date().isoformat()
    link = (c.get('links') or [None])[0] or first.get('linkUrl') or snap.get('linkUrl')
    fmt_ = c.get('format') if c.get('format') in ('video', 'image', 'carousel') else {'V': 'video', 'I': 'image'}.get(c.get('format'), '')
    if not fmt_:
        fmt_ = 'video' if video else 'image' if image else ''
    if len([x for x in cards if x.get('originalImageUrl') or x.get('resizedImageUrl')]) > 1 and (not video):
        fmt_ = 'carousel'
    out = {'key': cand_key('adlib', cid), 'platform': 'adlib', 'id': cid, 'url': f'https://www.facebook.com/ads/library/?id={cid}', 'author': c.get('advertiser') or snap.get('pageName') or c.get('pageName') or '', 'country': country, 'lang': lang_of_country(country), 'term': term, 'started_on': start, 'ended_on': end, 'versions': c.get('versions') or c.get('collationCount'), 'format': fmt_, 'text': card_text(c, snap, cards)[:600], 'landing_url': link, 'media_url': video, 'image_url': image if not video else None, 'image_urls': [x.get('originalImageUrl') or x.get('resizedImageUrl') for x in cards if x.get('originalImageUrl') or x.get('resizedImageUrl')][:10] if fmt_ == 'carousel' else None}
    if c.get('page'):
        out['page'] = c['page']
    out['landing_domain'] = landing_domain(link)
    out['running_days'] = running_days(out)
    if not term and out['author']:
        out['term'] = out['author']
    if REMOVED_AD.search(out['text'] or ''):
        out['removed'] = True
    return out

def landing_domain(url):
    """The landing site without www, tracking or path: « smartgainia.tech » for http://www.smartgainia.tech/atelier?x=1;
    a Facebook redirect (l.facebook.com/l.php?u=…) is unwrapped first."""
    if not url:
        return ''
    u = str(url)
    m = re.search('[?&]u=(https?[^&]+)', u)
    if m:
        from urllib.parse import unquote
        u = unquote(m.group(1))
    m = re.match('https?://([^/?#]+)', u.strip())
    host = (m.group(1) if m else '').lower()
    return host[4:] if host.startswith('www.') else host
REMOVED_AD = re.compile('Standards publicitaires|ne respectait pas nos|advertising standards|violat(ed|ing) our', re.I)

def norm_tiktok(x, term, lang):
    a = x.get('authorMeta') or x.get('author') or {}
    a = a if isinstance(a, dict) else {}
    author = a.get('name') or a.get('uniqueId') or x.get('authorMeta.name') or x.get('a') or ''
    st = x.get('stats') or {}
    g = lambda *ks: next((x.get(k) for k in ks if x.get(k) is not None), None) if any((x.get(k) is not None for k in ks)) else next((st.get(k) for k in ks if st.get(k) is not None), None)
    cid = str(x.get('id') or '')
    url = x.get('webVideoUrl') or x.get('url') or (f'https://www.tiktok.com/@{author}/video/{cid}' if author and cid else '')
    created = x.get('createTimeISO')
    for k in ('createTime', 't'):
        if not created and isinstance(x.get(k), (int, float)):
            created = dt.datetime.utcfromtimestamp(x[k]).isoformat()
    vm = x.get('videoMeta') or x.get('video') or {}
    dur = vm.get('duration') if isinstance(vm, dict) else None
    slides = x.get('slideshowImageLinks') or ((x.get('imagePost') or {}).get('images') if isinstance(x.get('imagePost'), dict) else None)
    is_slides = bool(slides or x.get('isSlideshow') or x.get('images'))
    tl = x.get('lang') or x.get('textLanguage')
    return {'key': cand_key('tiktok', cid), 'platform': 'tiktok', 'id': cid, 'url': url, 'author': author, 'country': x.get('locationCreated') or '', 'lang': lang or (tl if tl and tl not in ('un', 'und') else None), 'term': term, 'created_on': (created or '')[:10] or None, 'views': g('playCount', 'p'), 'likes': g('diggCount', 'l'), 'comments': g('commentCount', 'c'), 'saves': g('collectCount', 's'), 'shares': g('shareCount', 'sh'), 'duration': dur or x.get('d'), 'format': 'carousel' if is_slides else 'video', 'text': str(x.get('text') or x.get('desc') or '')[:600], 'is_ad': bool(x.get('isAd')), 'image_urls': [s.get('downloadLink') or s.get('url') if isinstance(s, dict) else s for s in slides][:12] if slides else None}

def norm_instagram(x, term, lang):
    cid = str(x.get('shortCode') or x.get('id') or '')
    return {'key': cand_key('instagram', cid), 'platform': 'instagram', 'id': cid, 'url': x.get('url') or f'https://www.instagram.com/reel/{cid}/', 'author': x.get('ownerUsername') or '', 'country': '', 'lang': lang, 'term': term, 'created_on': (x.get('timestamp') or '')[:10] or None, 'views': x.get('videoPlayCount') or x.get('videoViewCount'), 'likes': x.get('likesCount'), 'comments': x.get('commentsCount'), 'duration': x.get('videoDuration'), 'format': 'video' if x.get('type') in ('Video', 'Reel') or x.get('videoUrl') else 'carousel' if x.get('type') == 'Sidecar' else 'image', 'text': str(x.get('caption') or '')[:600], 'media_url': x.get('videoUrl'), 'image_url': x.get('displayUrl')}

def norm_url(u, term, lang, country):
    """A link pasted alone: the --country given at import stands for every platform (a TikTok link has none)."""
    c = _norm_url(u, term, lang, country)
    if c is not None and (not c.get('country')) and country:
        c['country'] = country
    return c

def _norm_url(u, term, lang, country):
    u = u.strip().rstrip('.,;)')
    m = re.search('facebook\\.com/ads/library/?\\?(?:.*&)?id=(\\d+)', u)
    if m:
        return norm_adlib_card({'id': m.group(1)}, term, country)
    m = re.search('tiktok\\.com/@([^/]+)/(?:video|photo)/(\\d+)', u)
    if m:
        c = norm_tiktok({'id': m.group(2), 'authorMeta': {'name': m.group(1)}, 'webVideoUrl': u.split('?')[0]}, term, lang)
        if '/photo/' in u:
            c['format'] = 'carousel'
        return c
    m = re.search('instagram\\.com/(?:reel|p|reels)/([\\w-]+)', u)
    if m:
        return norm_instagram({'shortCode': m.group(1), 'url': u.split('?')[0]}, term, lang)
    m = re.search('(?:youtube\\.com/(?:shorts/|watch\\?v=)|youtu\\.be/)([\\w-]{6,})', u)
    if m:
        return {'key': cand_key('youtube', m.group(1)), 'platform': 'youtube', 'id': m.group(1), 'url': u.split('&')[0], 'author': '', 'country': country, 'lang': lang, 'term': term, 'format': 'video', 'text': ''}
    return None

def kind_of(item):
    """Which source an item comes from, item by item (an Apify dataset may hold error items)."""
    if not isinstance(item, dict) or item.get('error') or item.get('errorDescription'):
        return None
    if 'adArchiveID' in item or 'adArchiveId' in item or 'snapshot' in item:
        return 'adlib'
    if 'webVideoUrl' in item or 'playCount' in item or 'authorMeta' in item:
        return 'tiktok'
    if 'shortCode' in item or 'ownerUsername' in item:
        return 'instagram'
    return None

def parse_capture(data, term, country, lang):
    """Every format the suite produces or receives, to one list of candidates, plus the number of items skipped."""
    if isinstance(data, dict) and isinstance(data.get('result'), (dict, list)):
        data = data['result']
    (out, skipped) = ([], 0)
    if isinstance(data, dict) and data.get('probe') == 'batch':
        for cap in data.get('captures') or []:
            (o, s) = parse_capture(cap, term, country, lang)
            out += o
            skipped += s
        return (out, skipped)
    if isinstance(data, dict) and data.get('probe') == 'adlib':
        q = urllib.parse.parse_qs(urllib.parse.urlparse(data.get('url', '')).query)
        country = country or (q.get('country') or [''])[0]
        term = term or (q.get('q') or [''])[0]
        for c in data.get('cards') or []:
            out.append(norm_adlib_card(dict(c, advertiser=c.get('advertiser') or data.get('advertiser')), term, country))
    elif isinstance(data, dict) and data.get('probe') == 'instagram':
        for x in data.get('items') or []:
            out.append(norm_instagram(x, x.get('term') or term or data.get('term') or '', lang))
    elif isinstance(data, dict) and data.get('probe') == 'tiktok':
        term = term or data.get('term') or ''
        for x in data.get('items') or []:
            out.append(norm_tiktok(x, x.get('q') or term, lang))
    elif isinstance(data, list):
        for item in data:
            k = kind_of(item)
            if k == 'adlib':
                q = urllib.parse.parse_qs(urllib.parse.urlparse(item.get('inputUrl') or '').query)
                out.append(norm_adlib_card(item, term or (q.get('q') or [''])[0], country or (q.get('country') or [''])[0]))
            elif k == 'tiktok':
                out.append(norm_tiktok(item, term or item.get('searchQuery') or '', lang))
            elif k == 'instagram':
                out.append(norm_instagram(item, term, lang))
            else:
                skipped += 1
    elif isinstance(data, dict) and data and all((isinstance(v, dict) for v in data.values())):
        for (cid, v) in data.items():
            if 'adv' in v or 'ver' in v:
                out.append(norm_adlib_card({'id': cid, 'advertiser': v.get('adv'), 'text': v.get('body'), 'versions': int(v['ver']) if str(v.get('ver') or '').isdigit() else None, 'format': v.get('f'), 'video_src': v.get('vs')}, v.get('k') or term, country))
            elif 'p' in v or 'a' in v:
                out.append(norm_tiktok(dict(v, id=cid), v.get('q') or term, lang))
            else:
                skipped += 1
    return ([c for c in out if c and c.get('id')], skipped)

def fill_langs(found, plan):
    """A video's language: the capture's, else the search it came from, else its country."""
    langs = {(q.get('platform'), q.get('term')): q.get('lang') for q in plan.get('queries') or [] if q.get('lang')}
    by_term = {q.get('term'): q.get('lang') for q in plan.get('queries') or [] if q.get('lang')}
    missing = 0
    for c in found:
        if not c.get('lang'):
            c['lang'] = langs.get((c['platform'], c.get('term'))) or by_term.get(c.get('term')) or lang_of_country(c.get('country'))
        if not c.get('lang') and c['platform'] != 'adlib':
            missing += 1
    return missing

def merge_candidates(P, found, source):
    F = files(P)
    data = load_list(F['cands'], 'candidates')
    by = {c['key']: c for c in data['candidates'] if isinstance(c, dict) and c.get('key')}
    new = upd = 0
    for c in found:
        c = {k: v for (k, v) in c.items() if v not in (None, '', [])}
        c['source'] = source
        old = by.get(c['key'])
        if old:
            for (k, v) in c.items():
                if k in ('status', 'code', 'reason', 'found_on'):
                    continue
                if k in ('views', 'likes', 'comments', 'saves', 'shares', 'versions') and isinstance(old.get(k), (int, float)) and isinstance(v, (int, float)):
                    old[k] = max(old[k], v)
                elif k == 'text' and len(str(old.get('text') or '')) > len(str(v)):
                    continue
                else:
                    old[k] = v
            upd += 1
        else:
            c.update({'found_on': today(), 'status': 'rejected' if c.get('removed') else 'new'})
            if c.get('removed'):
                c['reason'] = 'retirée par Meta (Standards publicitaires) : rien à recopier'
            data['candidates'].append(c)
            by[c['key']] = c
            new += 1
    dump_yaml(F['cands'], data)
    return (new, upd)

def read_clipboard():
    """The clipboard's text: PowerShell on Windows, pbpaste on a Mac, xclip or xsel elsewhere."""
    if W.WIN:
        cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command', '[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw']
    elif sys.platform == 'darwin':
        cmd = ['pbpaste']
    else:
        cmd = ['xclip', '-selection', 'clipboard', '-o'] if shutil.which('xclip') else ['xsel', '-b', '-o']
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=30)
    except Exception as e:
        raise WsError(f'le presse-papier ne se lit pas ({type(e).__name__})')
    return r.stdout.decode('utf-8', 'replace').strip()

def cmd_paste(a):
    """A browser capture copied with the COPIER button: saved in library/research/ (or where --save says), then
    imported as candidates, or counted as comments. Nothing big goes through the conversation."""
    (P, ws, state) = open_ws(a.folder)
    raw = read_clipboard()
    try:
        data = json.loads(raw)
    except ValueError:
        raise WsError("le presse-papier ne contient pas une capture : clique d'abord sur le bouton vert COPIER (un vrai clic), puis relance research.py paste")
    data = json.loads(json.dumps(data, ensure_ascii=False).encode('utf-8', 'replace').decode('utf-8'))
    probe = data.get('probe') if isinstance(data, dict) else 'list'
    import hashlib
    mark = files(P)['raw'] / '.derniere-capture'
    digest = hashlib.sha256(raw.encode('utf-8', 'replace')).hexdigest()
    if not a.again and mark.exists() and (mark.read_text(encoding='utf-8').strip() == digest):
        raise WsError("c'est la même capture que la précédente : le clic sur COPIER n'a pas copié. Reclique sur le bouton vert (un vrai clic), puis relance ; --again pour l'importer quand même")
    stamp = time.strftime('%Y%m%d-%H%M%S')
    if a.save:
        dest = Path(a.save) if Path(a.save).is_absolute() else P['root'] / a.save
    else:
        tag = {'adlib': 'adlib', 'tiktok': 'tiktok', 'instagram': 'instagram', 'tiktok_comments': 'comments', 'comments': 'comments', 'batch': 'adlib'}.get(probe, 'capture')
        dest = files(P)['raw'] / f'{tag}-{stamp}.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    tmp.replace(dest)
    mark.parent.mkdir(parents=True, exist_ok=True)
    mark.write_text(digest, encoding='utf-8')
    print(f"Capture enregistrée : {(dest.relative_to(P['root']) if dest.is_relative_to(P['root']) else dest)} ({len(raw) // 1024} Ko)")
    if a.save:
        return
    if probe in ('tiktok_comments', 'comments'):
        cmd_intent(argparse.Namespace(folder=a.folder, file=str(dest)))
    elif probe in ('adlib', 'tiktok', 'instagram', 'list', 'batch'):
        cmd_import(argparse.Namespace(folder=a.folder, file=str(dest), term=a.term, country=a.country, lang=a.lang))
    else:
        print("Format inconnu : gardé tel quel, rien d'importé.")

def cmd_import(a):
    (P, ws, state) = open_ws(a.folder)
    src = Path(a.file).expanduser()
    if not src.exists() and (P['root'] / a.file).exists():
        src = P['root'] / a.file
    if not src.exists():
        raise WsError(f'fichier introuvable : {a.file}')
    raw = src.read_text(encoding='utf-8-sig')
    skipped = 0
    if src.suffix.lower() in ('.txt', '.csv') or not raw.lstrip().startswith(('{', '[')):
        found = [norm_url(u, a.term or '', a.lang, (a.country or '').upper()) for u in re.findall('https?://\\S+', raw)]
        found = [f for f in found if f]
        source = 'liens'
    else:
        (found, skipped) = parse_capture(json.loads(raw), a.term or '', (a.country or '').upper(), a.lang)
        source = 'apify' if 'apify' in src.name.lower() else 'navigateur'
    if not found:
        raise WsError(f'{src.name} : aucun candidat reconnu (sonde adlib_links.js, tiktok_capture.js, export Apify ou liste de liens)' + (f" ; {skipped} élément(s) d'erreur ou inconnu(s) écarté(s)" if skipped else ''))
    F = files(P)
    plan = load_yaml(F['plan'], {}) or {}
    no_lang = fill_langs(found, plan)
    F['raw'].mkdir(parents=True, exist_ok=True)
    keep = F['raw'] / src.name
    if src.resolve() != keep.resolve() and (not keep.exists()):
        shutil.copy2(src, keep)
    (new, upd) = merge_candidates(P, found, source)
    for q in plan.get('queries') or []:
        hits = [c for c in found if c.get('term') == q.get('term') and c['platform'] == q.get('platform') and (q['platform'] != 'adlib' or c.get('country') == q.get('country'))]
        if hits and q.get('status') != 'done':
            (q['status'], q['found']) = ('done', len(hits))
    if plan:
        save_plan(F, plan)
    journal(P, f'Recherche importée ({src.name}) : {new} nouveau(x) candidat(s), {upd} mis à jour')
    refresh(P, ws, state)
    by_p = {}
    for c in found:
        by_p[c['platform']] = by_p.get(c['platform'], 0) + 1
    print(f"{src.name} : {len(found)} candidats ({', '.join((f'{k} {v}' for (k, v) in by_p.items()))}), {new} nouveaux, {upd} mis à jour. Suite : research.py rank <dossier>")
    if skipped:
        print(f"  {skipped} élément(s) écarté(s) : erreurs de l'outil ou format inconnu")
    gone = sum((1 for c in found if c.get('removed')))
    if gone:
        print(f"  {gone} pub(s) retirée(s) par Meta : écartées du classement (l'angle est risqué pour un compte neuf)")
    if no_lang:
        print(f"  {no_lang} vidéo(s) sans langue : la recherche d'origine n'est pas dans le plan ; relance avec --lang fr|en")

def apify_input(platform, q, limit, ws):
    if platform == 'adlib':
        return {'startUrls': [{'url': q.get('url') or adlib_search_url(q['country'], q['term'])}], 'resultsLimit': limit, 'activeStatus': 'active'}
    if platform == 'tiktok':
        inp = {'searchQueries': [q['term']], 'resultsPerPage': limit, 'searchSection': '/video', 'shouldDownloadVideos': False, 'shouldDownloadCovers': False, 'commentsPerPost': 0}
        market = next((m.get('code') for m in ws.get('markets') or [] if isinstance(m, dict) and m.get('code')), None)
        if market:
            inp['proxyCountryCode'] = market
        return inp
    return {'search': q['term'].replace(' ', ''), 'searchType': 'hashtag', 'searchLimit': 1, 'resultsType': 'posts', 'resultsLimit': limit}

def apify_call(method, url, body=None, timeout=90):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method=method, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8'))

def apify_run(actor, inp, token, q, plan_saver):
    """Start a run, keep its id in the plan (paid results are never lost), wait for it, read its dataset."""
    base = 'https://api.apify.com/v2'
    if q.get('run_id') and q.get('status') == 'running':
        run = apify_call('GET', f"{base}/actor-runs/{q['run_id']}?token={token}")['data']
    else:
        run = apify_call('POST', f'{base}/acts/{actor}/runs?token={token}', inp)['data']
        q.update({'run_id': run['id'], 'dataset_id': run.get('defaultDatasetId'), 'status': 'running'})
        plan_saver()
    for _ in range(120):
        if run.get('status') in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
            break
        run = apify_call('GET', f"{base}/actor-runs/{run['id']}?token={token}&waitForFinish=10", timeout=40)['data']
    if run.get('status') != 'SUCCEEDED':
        raise RuntimeError(f"run {run.get('status', '?')}")
    ds = run.get('defaultDatasetId') or q.get('dataset_id')
    return apify_call('GET', f'{base}/datasets/{ds}/items?clean=true&format=json&token={token}', timeout=120)

def cmd_discover(a):
    (P, ws, state) = open_ws(a.folder)
    F = files(P)
    plan = load_yaml(F['plan'], {}) or {}
    queries = plan.setdefault('queries', [])
    mine = [q for q in queries if not a.platform or q['platform'] == a.platform]
    todo = [q for q in mine if q.get('status') in ('todo', 'running', 'empty') or a.all]
    if not todo and a.dry_run:
        todo = mine
    if not todo:
        raise WsError("aucune recherche à faire dans library/research.yaml : lance d'abord research.py plan (ou --all pour refaire les recherches faites)")
    est = sum((a.limit * APIFY_PRICE_PER_1000.get(q['platform'], 5) / 1000 for q in todo))
    if a.dry_run:
        for q in todo:
            print(f"{ACTORS[q['platform']]} ← {json.dumps(apify_input(q['platform'], q, a.limit, ws), ensure_ascii=False)}")
        print(f'{len(todo)} recherche(s) × {a.limit} résultats : environ {est:.2f} $ au plus (tarifs hauts lus le 28/10/2026).')
        return
    token = os.environ.get('APIFY_TOKEN') or W.env_state('APIFY_TOKEN')[1]
    if not token:
        raise WsError('APIFY_TOKEN absent : la recherche passe par le navigateur (references/search.md), ou enregistre le jeton (references/apify.md) puis relance')
    if not a.yes:
        raise WsError(f'{len(todo)} recherche(s) × {a.limit} résultats ≈ {est:.2f} $ au plus sur le crédit Apify. Relance avec --yes pour lancer, ou --limit plus petit')
    F['raw'].mkdir(parents=True, exist_ok=True)
    total = 0
    for q in todo:
        actor = ACTORS[q['platform']]
        try:
            items = apify_run(actor, apify_input(q['platform'], q, a.limit, ws), token, q, lambda : save_plan(F, plan))
        except urllib.error.HTTPError as e:
            detail = e.read().decode('utf-8', 'replace')[:160]
            save_plan(F, plan)
            if e.code in (401, 402, 403):
                raise WsError(f'Apify refuse (HTTP {e.code}) : jeton faux ou crédit épuisé. Les recherches déjà faites sont gardées ; continue au navigateur (ws.py set <dossier> engines.discover=browser)')
            print(f"  {q['platform']} « {q['term']} » : Apify répond HTTP {e.code} {detail} ; on passe à la suivante")
            continue
        except Exception as e:
            save_plan(F, plan)
            print(f"  {q['platform']} « {q['term']} » : pas de résultat ({type(e).__name__} : {str(e)[:80]}) ; " + ('la course est notée, relance discover pour la reprendre' if q.get('run_id') else 'on passe à la suivante'))
            continue
        name = f"apify-{q['platform']}-{slug(q.get('country') or 'all', 4)}-{slug(q['term'], 24)}-{today()}.json"
        (F['raw'] / name).write_text(json.dumps(items, ensure_ascii=False), encoding='utf-8')
        (found, skipped) = parse_capture(items, q['term'], q.get('country', ''), q.get('lang'))
        fill_langs(found, plan)
        (new, _) = merge_candidates(P, found, 'apify')
        q.update({'status': 'done' if found else 'empty', 'found': len(found), 'engine': 'apify', 'done_on': today()})
        save_plan(F, plan)
        total += len(found)
        print(f"  {q['platform']}{(' ' + q['country'] if q.get('country') else '')} « {q['term']} » : {len(found)} résultats, {new} nouveaux" + (f", {skipped} élément(s) d'erreur écarté(s)" if skipped else '') + ('' if found else ' — rien : essaie ce mot au navigateur'))
    journal(P, f'Recherche Apify : {total} résultats sur {len(todo)} recherche(s)')
    refresh(P, ws, state)

def short_metric(c):
    if c.get('platform') == 'adlib':
        d = running_days(c)
        s = (f'{d} j' if d is not None else '? j') + (' (arrêtée)' if c.get('ended_on') else '')
        return s + (f" · {c['versions']} versions" if c.get('versions') else '')
    v = c.get('views')
    s = '? vues' if v is None else f'{v / 1000000.0:.1f} M vues'.replace('.', ',') if v >= 999500 else f'{v / 1000:.0f} k vues' if v >= 1000 else f'{v} vues'
    if v is None and c.get('likes') is not None:
        s = f"{c['likes']} j'aime (vues inconnues)"
    if c.get('comments'):
        s += f" · {c['comments']} comm."
    if (c.get('intent') or {}).get('read'):
        s += f" · achat {c['intent']['buying']}/{c['intent']['read']}"
    return s

def cmd_voice(a):
    """1.6: the customers' words read elsewhere (a YouTube comments export in JSON, a text or Markdown file) go into
    library/voice, the source in the file name, so the avatars' lexique can be checked against them."""
    (P, ws, state) = open_ws(a.folder)
    src = Path(a.file)
    if not src.exists():
        raise WsError(f'fichier introuvable : {src}')
    raw = read_text(src)
    lines = []
    if src.suffix.lower() == '.json':
        try:
            data = json.loads(raw)
        except ValueError as e:
            raise WsError(f'{src.name} : JSON illisible ({e})')
        TEXT_KEYS = ('text', 'textOriginal', 'textDisplay', 'comment', 'body', 't')

        def walk(x, in_comments=False):
            if isinstance(x, list):
                for y in x:
                    walk(y, in_comments)
            elif isinstance(x, dict):
                t = next((x[k] for k in TEXT_KEYS if isinstance(x.get(k), str) and x[k].strip()), '')
                if t:
                    likes = x.get('likes') or x.get('likeCount') or x.get('votes')
                    lines.append(f"- {' '.join(t.split())}" + (f" ({likes} j'aime)" if likes else ''))
                for (k, v) in x.items():
                    if isinstance(v, (list, dict)) and k not in TEXT_KEYS:
                        walk(v, in_comments or k in ('comments', 'replies', 'items'))
            elif isinstance(x, str) and x.strip() and in_comments:
                lines.append(f"- {' '.join(x.split())}")
        walk(data, isinstance(data, list))
    else:
        lines = [l.rstrip() for l in raw.splitlines() if l.strip()]
    if not lines:
        raise WsError(f"{src.name} : aucun commentaire lu (JSON : une liste d'objets avec « text » ; sinon une ligne par commentaire)")
    vdir = P['root'] / 'library' / 'voice'
    vdir.mkdir(parents=True, exist_ok=True)
    name = f'commentaires-{slug(a.source or src.stem, 40)}-{today()}.md'
    out = vdir / name
    out.write_text(f'# Mots des clients — {a.source or src.name}\n\n*Importé le {today()} depuis {src.name}, {len(lines)} lignes.*\n\n' + '\n'.join(lines) + '\n', encoding='utf-8')
    journal(P, f'Mots des clients importés : {name} ({len(lines)} lignes)')
    refresh(P, ws, state)
    print(f'Écrit : library/voice/{name} ({len(lines)} lignes). La stratégie vérifie le lexique des avatars contre ce fichier.')

def lacks_meta(r):
    """A reference imported by its link, or whose file was already there: no author, date or views yet."""
    return r.get('platform') in ('tiktok', 'instagram', 'youtube') and bool(r.get('url')) and (not (r.get('author') and (r.get('created_on') or r.get('started_on')) and r.get('views')))

def ffmpeg_exe():
    """ffmpeg on the PATH, or the copy that comes with imageio-ffmpeg (installed by the suite's setup)."""
    import shutil
    if shutil.which('ffmpeg'):
        return shutil.which('ffmpeg')
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return ''

def ytdlp(url, out_tmpl, info_only=False):
    ff = ffmpeg_exe()
    fmt = 'b[ext=mp4]/bv*[height<=1920][ext=mp4]+ba[ext=m4a]/bv*+ba/b' if ff else 'b[ext=mp4]/b'
    cmd = [sys.executable, '-m', 'yt_dlp', '--no-playlist', '--write-info-json', '--no-progress', '--quiet', '--no-warnings', '-f', fmt, '-o', out_tmpl, url]
    if ff:
        cmd[3:3] = ['--ffmpeg-location', ff, '--merge-output-format', 'mp4']
    if info_only:
        cmd.insert(3, '--skip-download')
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    except subprocess.TimeoutExpired:
        return (1, "yt-dlp n'a pas fini en 10 minutes")
    lines = (r.stderr or r.stdout or '').strip().splitlines()
    return (r.returncode, lines[-1] if lines else '')

def fetch_file(url, dest, referer=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/124 Mobile Safari/537.36'}
    if referer:
        headers['Referer'] = referer
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=120) as r, open(dest, 'wb') as fh:
        shutil.copyfileobj(r, fh)
    if not readable(dest):
        Path(dest).unlink(missing_ok=True)
        raise ValueError("le fichier reçu n'est ni une image ni une vidéo")

def _try_fetch(url, dest):
    """The capture's own media link, tried once: True when a readable file came, False otherwise (expired link)."""
    try:
        fetch_file(url, dest, referer='https://www.facebook.com/')
        return True
    except Exception:
        Path(dest).unlink(missing_ok=True)
        return False

def cmd_download(a):
    (P, ws, state) = open_ws(a.folder)
    F = files(P)
    data = load_list(F['refs'], 'references')
    want = [c.upper() for c in a.codes]
    todo = [r for r in data['references'] if isinstance(r, dict) and r.get('platform') in PLATFORMS and (r.get('code') in want if want else (not r.get('file') or lacks_meta(r)) and r.get('status') != 'cite_only')]
    if not todo:
        print('Rien à télécharger : toutes les références choisies ont leur fichier.')
        return
    try:
        import yt_dlp
        have_ytdlp = True
    except ImportError:
        have_ytdlp = False
    ok = fail = 0
    for r in todo:
        sub = P['refs_dir'] / PLATFORMS[r['platform']][1]
        sub.mkdir(parents=True, exist_ok=True)
        base = r.get('base') or f"{r['code']}_{r['id']}"
        got = media_files(P, r)
        err = ''
        try:
            if not got and r.get('format') == 'carousel' and (r.get('image_urls') or r.get('image_url')):
                for (i, u) in enumerate((r.get('image_urls') or [r.get('image_url')])[:12], 1):
                    fetch_file(u, sub / f'{base}_{i}.jpg', referer='https://www.tiktok.com/' if r['platform'] == 'tiktok' else None)
            elif not got and r.get('format') == 'image' and r.get('image_url'):
                fetch_file(r['image_url'], sub / f'{base}.jpg')
            elif not got and r.get('platform') == 'adlib' and r.get('media_url') and (r.get('format') != 'image') and _try_fetch(r['media_url'], sub / f'{base}.mp4'):
                pass
            elif not got and have_ytdlp and r.get('url'):
                (code, last) = ytdlp(r['url'], str(sub / f'{base}.%(ext)s'))
                if code != 0 or not media_files(P, r):
                    err = (last or 'aucun fichier vidéo reçu')[:160]
                    if r['platform'] == 'tiktok' and r.get('format') == 'carousel':
                        err += ' ; post photo : récupère les images dans le navigateur (references/pipeline.md)'
                    if r.get('media_url'):
                        try:
                            fetch_file(r['media_url'], sub / f'{base}.mp4', referer='https://www.facebook.com/')
                            err = ''
                        except Exception as e:
                            err += f' ; lien direct : {type(e).__name__}'
            elif got and have_ytdlp and lacks_meta(r):
                ytdlp(r['url'], str(sub / f'{base}.%(ext)s'), info_only=True)
            elif not got and r.get('media_url'):
                fetch_file(r['media_url'], sub / f'{base}.mp4')
            elif not got:
                err = 'yt-dlp absent (pip install yt-dlp) et pas de lien direct'
        except Exception as e:
            err = f'{type(e).__name__} : {str(e)[:120]}'
        got = [g for g in media_files(P, r) if readable(g)]
        for bad in set(media_files(P, r)) - set(got):
            bad.unlink(missing_ok=True)
            err = err or "fichier illisible reçu (page d'erreur au lieu de la vidéo)"
        info = next(iter(sorted(sub.glob(base + '*.info.json'))), None)
        if info:
            try:
                meta = json.loads(info.read_text(encoding='utf-8'))
                pairs = [('view_count', 'views'), ('comment_count', 'comments'), ('duration', 'duration')]
                if r['platform'] != 'adlib':
                    pairs.append(('like_count', 'likes'))
                for (k_src, k) in pairs:
                    if meta.get(k_src) is not None and (not r.get(k)):
                        r[k] = meta[k_src]
                if not r.get('text') and meta.get('description'):
                    r['text'] = meta['description'][:600]
                if not r.get('author') and (meta.get('uploader') or meta.get('channel') or meta.get('uploader_id')):
                    r['author'] = meta.get('uploader') or meta.get('channel') or meta.get('uploader_id')
                ud = str(meta.get('upload_date') or '')
                if not r.get('created_on') and re.fullmatch('\\d{8}', ud):
                    r['created_on'] = f'{ud[:4]}-{ud[4:6]}-{ud[6:]}'
                if not r.get('country') and meta.get('location'):
                    r['country'] = str(meta['location'])[:2].upper()
            except (json.JSONDecodeError, OSError):
                pass
        if got:
            r['file'] = str(got[0].relative_to(P['refs_dir'])).replace('\\', '/')
            if len(got) > 1:
                r['files'] = [str(g.relative_to(P['refs_dir'])).replace('\\', '/') for g in got]
            r['status'] = 'downloaded'
            r.pop('download_error', None)
            ok += 1
            print(f"  {r['code']} : {got[0].name}" + (f' (+{len(got) - 1})' if len(got) > 1 else '') + f' ({got[0].stat().st_size // 1024} Ko)')
        else:
            r['tries'] = int(r.get('tries') or 0) + 1
            r['download_error'] = err or 'aucun fichier reçu'
            if r['tries'] >= 2:
                r['status'] = 'cite_only'
            fail += 1
            print(f"  {r['code']} : échec — {r['download_error']}" + (f" → regarde-la en ligne et analyse-la sans fichier : {r.get('url') or ''}" if r['tries'] >= 2 else ' (nouvel essai possible)'))
        save_refs(F['refs'], data)
    if fail:
        print('Des échecs : mets yt-dlp à jour (python -m pip install -U yt-dlp), il suit les changements des sites, puis relance. Une vidéo qui refuse toujours se regarde en ligne : son lien est dans REFERENCES_LOG.xlsx.')
    journal(P, f'Téléchargements : {ok} réussi(s), {fail} échec(s)')
    refresh(P, ws, state)
    print(f'{ok} téléchargé(s), {fail} échec(s). Suite : research.py transcribe <dossier>')

def has_audio(path):
    try:
        import av
        with av.open(str(path)) as c:
            return any((s.type == 'audio' for s in c.streams))
    except Exception:
        return True

def guess_language(model, src, allowed):
    """The most likely language of the first 30 seconds, among the allowed ones only (French first when unsure)."""
    try:
        from faster_whisper import decode_audio
        audio = decode_audio(str(src), sampling_rate=16000)[:16000 * 30]
        (_, _, probs) = model.detect_language(audio)
        best = max(((l, p) for (l, p) in probs if l in allowed), key=lambda x: x[1], default=None)
        return best[0] if best else 'fr'
    except Exception:
        return 'fr' if 'fr' in allowed else sorted(allowed)[0]

def cmd_transcribe(a):
    (P, ws, state) = open_ws(a.folder)
    F = files(P)
    data = load_list(F['refs'], 'references')
    out_dir = P['refs_dir'] / 'Transcripts'
    out_dir.mkdir(parents=True, exist_ok=True)
    want = [c.upper() for c in a.codes]
    refs = [r for r in data['references'] if isinstance(r, dict) and r.get('file') and is_video(r['file']) and (not want or r.get('code') in want)]
    redo = 0
    for r in refs:
        t = r.get('transcript')
        if not t:
            continue
        f = P['refs_dir'] / t
        header = read_text(f).splitlines()[0] if f.exists() and f.stat().st_size > 0 else ''
        if getattr(a, 'redo', False) or not header or ('model=base' in header and a.model != 'base'):
            for k in ('transcript', 'has_voice', 'words'):
                r.pop(k, None)
            if header and f.exists():
                f.unlink()
            redo += 1
    if redo:
        save_refs(F['refs'], data)
        print(f'{redo} transcription(s) à refaire (fichier absent, modèle « base », ou --redo).')
    adopted = 0
    for r in refs:
        if want or r.get('transcript'):
            continue
        stem = Path(r['file']).stem
        found = [f for f in [out_dir / f'{stem}.txt', out_dir / f"{r['code']}.txt", *sorted(out_dir.glob(f"{r['code']}_*.txt"))] if f.exists() and f.stat().st_size > 0]
        if not found:
            continue
        body = [ln for ln in read_text(found[0]).splitlines() if ln.strip() and (not ln.startswith('#'))]
        words = sum((len(re.sub('^\\[\\d+:\\d{2}\\]\\s*', '', ln).split()) for ln in body))
        r.update({'transcript': f'Transcripts/{found[0].name}', 'has_voice': words >= 15, 'words': words})
        adopted += 1
    if adopted:
        save_refs(F['refs'], data)
        print(f'{adopted} transcription(s) déjà dans Transcripts/ : reprise(s) telles quelles.')
    todo = [r for r in refs if want or not r.get('transcript')]
    if not todo:
        print('Rien à transcrire.')
        return
    model_name = a.model
    if model_name == 'auto':
        (total, avail) = W.ram_mb()
        model_name = 'medium' if (avail or 0) > 2500 else 'small'
        if (avail or 0) <= 1200:
            print(f'Peu de mémoire libre ({avail} Mo) : Whisper « small » quand même, parce que ces transcriptions sont copiées mot pour mot. Ferme le navigateur intégré et les applications lourdes ; si la mémoire manque, la commande attend au lieu de passer à « base » (--model base pour le forcer).')
            a.model = 'small'
    model = None
    print(f'{len(todo)} vidéo(s) à transcrire, une à la fois.')
    allowed = {'fr', 'en'} | {str(m.get('language'))[:2] for m in ws.get('markets') or [] if isinstance(m, dict) and str(m.get('language') or '')[:2] in ('fr', 'en', 'es', 'pt', 'ar')}
    done = 0
    for r in todo:
        src = P['refs_dir'] / r['file']
        dest = out_dir / f"{Path(r['file']).stem}.txt"
        if not src.exists():
            print(f"  {r['code']} : fichier introuvable ({r['file']})")
            continue
        if not has_audio(src):
            dest.write_text(f'# {src.stem} | pas de piste son\n(Vidéo sans voix : modèle plan par plan.)\n', encoding='utf-8')
            r.update({'transcript': f'Transcripts/{dest.name}', 'has_voice': False})
            save_refs(F['refs'], data)
            print(f"  {r['code']} : pas de son")
            done += 1
            continue
        if model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                raise WsError('faster-whisper absent : python -m pip install faster-whisper av')
            for load in (1, 2):
                try:
                    model = WhisperModel(model_name, device='cpu', compute_type='int8')
                    break
                except Exception as e:
                    if load == 2:
                        raise WsError(f"Whisper ne charge pas le modèle {model_name} ({type(e).__name__}) : ferme les applications lourdes (Chrome d'abord) et relance ; les transcriptions finies sont gardées")
                    print(f'  pas assez de mémoire pour charger Whisper « {model_name} » ({type(e).__name__}) : je réessaie dans une minute', flush=True)
                    import time
                    time.sleep(60)
        lang = r.get('lang') if r.get('lang') in ('fr', 'en', 'es', 'pt', 'ar') else None
        if not lang:
            lang = guess_language(model, src, allowed)
            print(f"  {r['code']} : langue inconnue, choisie parmi {'/'.join(sorted(allowed))} : {lang}")
        lines = None
        for attempt in (1, 2):
            try:
                (segs, info) = model.transcribe(str(src), beam_size=1 if a.fast else 5, vad_filter=True, language=lang, condition_on_previous_text=False)
                lines = [f'# {src.stem} | lang={info.language} | model={model_name} | dur={info.duration:.0f}s']
                for s in segs:
                    (mm, ss) = divmod(int(s.start), 60)
                    lines.append(f'[{mm}:{ss:02d}] {s.text.strip()}')
                break
            except (MemoryError, RuntimeError) as e:
                import gc
                del model
                gc.collect()
                lighter = model_name if a.model != 'auto' else {'medium': 'small', 'small': 'base'}.get(model_name, model_name)
                if lighter == model_name:
                    import time
                    time.sleep(60)
                if attempt == 2:
                    model = None
                    break
                print(f"  {r['code']} : mémoire saturée ({type(e).__name__}) : je recharge Whisper « {lighter} » et je réessaie", flush=True)
                try:
                    model_name = lighter
                    model = WhisperModel(model_name, device='cpu', compute_type='int8')
                except Exception:
                    model = None
                    break
            except Exception as e:
                print(f"  {r['code']} : échec ({type(e).__name__}) ; relance plus tard, les autres continuent")
                break
        if model is None:
            rest = [x['code'] for x in todo[todo.index(r):]]
            if not os.environ.get('CSOS_TRANSCRIBE_CHILD') and P.get('root'):
                print(f'  la mémoire ne suffit plus pour ce processus : les {len(rest)} vidéo(s) restante(s) passent une par une, chacune dans son propre processus, en modèle « base »', flush=True)
                env = dict(os.environ, CSOS_TRANSCRIBE_CHILD='1')
                for code in rest:
                    subprocess.run([sys.executable, str(Path(__file__).resolve()), 'transcribe', str(P['root']), code, '--model', 'base'], env=env)
                data = load_list(F['refs'], 'references')
                done += sum((1 for x in data['references'] if isinstance(x, dict) and x.get('code') in rest and x.get('transcript')))
                break
            left = len(todo) - done - 1
            print(f"  {r['code']} : la mémoire de cet ordinateur ne suffit plus. Arrêt : {done} transcrite(s), {left} restante(s). Ferme le navigateur et les applications lourdes, puis relance research.py transcribe (les finies sont gardées).")
            break
        if lines is None:
            continue
        dest.write_text('\n'.join(lines), encoding='utf-8')
        words = sum((len(l.split()) for l in lines[1:]))
        r.update({'transcript': f'Transcripts/{dest.name}', 'has_voice': words >= 15, 'words': words, 'transcript_model': model_name})
        save_refs(F['refs'], data)
        done += 1
        print(f"  {r['code']} : {len(lines) - 1} segments, {words} mots", flush=True)
    journal(P, f'Transcriptions : {done} vidéo(s)')
    refresh(P, ws, state)

def open_video(path):
    import av
    try:
        return av.open(str(path))
    except Exception as e:
        raise WsError(f"{Path(path).name} ne s'ouvre pas comme une vidéo ({type(e).__name__}) : retélécharge-la (research.py download <dossier> <CODE>)")

def video_frames(path, n):
    """n frames spread over the video, each with its time; fewer when the video is shorter than n half-seconds."""
    c = open_video(path)
    try:
        st = c.streams.video[0]
        dur = float(st.duration * st.time_base) if st.duration else float(c.duration or 0) / 1000000.0
        n = max(1, min(n, int(dur * 2) or 1))
        out = []
        for i in range(n):
            t = dur * (i + 0.5) / n
            c.seek(int(t / st.time_base), stream=st, any_frame=False, backward=True)
            for fr in c.decode(st):
                out.append((t, fr.to_image()))
                break
        return (out, dur)
    finally:
        c.close()

def stamp_of(t):
    (mm, ss) = divmod(t, 60)
    whole = int(ss)
    tenth = int(round((ss - whole) * 10)) % 10
    return f'{int(mm)}m{whole:02d}s' + (f'{tenth}' if tenth else '')

def cmd_sheet(a):
    (P, ws, state) = open_ws(a.folder)
    from PIL import Image, ImageDraw
    data = load_list(files(P)['refs'], 'references')
    refs = [r for r in data['references'] if r.get('file') and (a.platform in (None, 'all') or r.get('platform') == a.platform)]
    if getattr(a, 'images', False):
        refs = [r for r in refs if not is_video(r['file'])]
    out = P['refs_dir'] / '_sheets'
    out.mkdir(parents=True, exist_ok=True)
    (per, W_, H_) = (6, 180, 320)
    made = []
    if getattr(a, 'by_author', False):
        groups = {}
        for r in refs:
            groups.setdefault(str(r.get('author') or '?'), []).append(r)
        batches = [(slug(au, 30), rs[k:k + 6]) for (au, rs) in sorted(groups.items(), key=lambda x: -len(x[1])) for k in range(0, len(rs), 6)]
    else:
        batches = [(f"{a.platform or 'all'}_{i // 6 + 1:02d}", refs[i:i + 6]) for i in range(0, len(refs), 6)]
    for (i, (name, batch)) in enumerate(batches):
        sheet = Image.new('RGB', (per * W_, len(batch) * (H_ + 22)), 'white')
        d = ImageDraw.Draw(sheet)
        for (row, r) in enumerate(batch):
            y = row * (H_ + 22)
            d.text((4, y + 4), f"{r['code']}  {str(r.get('author') or '')[:24]}  {short_metric(r)}", fill='red')
            src = P['refs_dir'] / r['file']
            try:
                if not is_video(src):
                    ims = [Image.open(P['refs_dir'] / f) for f in (r.get('files') or [r['file']])[:per]]
                else:
                    ims = [im for (_, im) in video_frames(src, per)[0]]
            except Exception:
                d.text((4, y + 40), 'illisible : retélécharge-la', fill='black')
                continue
            for (k, im) in enumerate(ims[:per]):
                im = im.convert('RGB')
                im.thumbnail((W_, H_))
                sheet.paste(im, (k * W_, y + 22))
        path = out / f"sheet_{name}{('_' + str(i + 1) if getattr(a, 'by_author', False) else '')}.png"
        sheet.save(path)
        made.append(path)
    print(f'{len(made)} planche(s) dans References/_sheets/ ({len(refs)} références) :')
    for p in made:
        print(f'  {p}')
    print('Regarde-les toutes avant de garder une référence : produit hors sujet, téléchargement cassé, mauvais pays.')

def cmd_frames(a):
    codes = [a.code] + [s for s in a.secs if re.fullmatch('[A-Za-z]{1,4}\\d{1,4}', str(s))]
    secs = [s for s in a.secs if s not in codes]
    if len(codes) > 1 and secs:
        raise WsError('des secondes précises vont avec un seul code : frames <dossier> AL01 3 7.5')
    for code in codes:
        _frames_one(a, code, secs)

def _frames_one(a, code, secs):
    (P, ws, state) = open_ws(a.folder)
    F = files(P)
    data = load_list(F['refs'], 'references')
    r = ref_by_code(data['references'], code)
    if not r or not r.get('file'):
        raise WsError(f'{code} : pas de fichier téléchargé')
    src = P['refs_dir'] / r['file']
    if not is_video(src):
        print(f"{r['code']} est une image : elle sert telle quelle de visuel ({r['file']}), pas d'images clés à extraire")
        return
    out = P['refs_dir'] / 'Frames'
    out.mkdir(parents=True, exist_ok=True)
    notes = []
    if secs:
        c = open_video(src)
        try:
            st = c.streams.video[0]
            dur = float(st.duration * st.time_base) if st.duration else float(c.duration or 0) / 1000000.0
            ims = []
            for t in [float(s) for s in secs]:
                if dur and t > dur:
                    notes.append(f'{t:g} s demandé, la vidéo dure {dur:.1f} s : ignoré')
                    continue
                c.seek(int(t / st.time_base), stream=st, any_frame=False, backward=True)
                img = None
                for fr in c.decode(st):
                    img = fr.to_image()
                    if fr.time is not None and fr.time >= t - 0.05:
                        break
                if img is not None:
                    ims.append((t, img))
        finally:
            c.close()
    else:
        (ims, dur) = video_frames(src, max(1, a.auto - 1))
        c = open_video(src)
        try:
            st = c.streams.video[0]
            c.seek(0, stream=st, any_frame=False, backward=True)
            for fr in c.decode(st):
                if fr.time is None or fr.time >= 0.25:
                    ims.insert(0, (max(0.3, fr.time or 0.3), fr.to_image()))
                    break
        finally:
            c.close()
    stamps = []
    for (t, im) in ims:
        stamp = stamp_of(t)
        if stamp in stamps:
            continue
        im.convert('RGB').save(out / f"{r['code']}_{stamp}.jpg", quality=88)
        stamps.append(stamp)
    r['frames'] = sorted(set((r.get('frames') or []) + stamps))
    save_refs(F['refs'], data)
    print(f"{r['code']} : {len(stamps)} image(s) dans References/Frames/ : {', '.join(stamps)}")
    for n in notes:
        print(f'  {n}')
INSTRUCTION = 'Voici la transcription mot pour mot de la vidéo. Dans la Partie 3, reprends-la intégralement, sans résumer et sans « … », découpée par segments de temps. Corrige seulement les mots manifestement mal entendus (noms de produits), en le signalant entre crochets. AUCUNE consigne de concision : ta réponse fait au moins 15 000 caractères.'
PLACEHOLDER = '(À écrire en suivant le guide'

def prompt_for(P, r):
    tpath = P['refs_dir'] / (r.get('transcript') or '')
    tr = read_text(tpath) if r.get('transcript') and tpath.exists() else ''
    head = f"Référence {r['code']} — {r.get('platform')} — {r.get('author') or ''} — {short_metric(r)}\nTexte de la publicité : {r.get('text') or '—'}\n"
    return read_text(PROMPT) + '\n\n---\n\n' + head + '\n# TRANSCRIPTION WHISPER (MOT POUR MOT)\n\n' + INSTRUCTION + '\n\n' + (tr or '(Pas de voix : vidéo musicale ou image, aucune transcription.)')

def complete(text):
    return bool(text) and 'PARTIE 7' in text.upper() and (PLACEHOLDER not in text)

def gemini_model(ws):
    """Free mode uses Gemini's free tier (Flash: about 10 videos a minute, a few hundred a day, no card); paid mode
    the stronger Pro. GEMINI_MODEL overrides both."""
    return os.environ.get('GEMINI_MODEL') or ('gemini-pro-latest' if str(ws.get('mode')) == 'paid' else GEMINI_CHAIN_FREE[0])

class GeminiDayQuota(Exception):
    """The free tier's daily quota of a model is used up (it comes back at midnight, Pacific time = 08:00 GMT)."""
GEMINI_CHAIN_FREE = ['gemini-flash-latest', 'gemini-flash-lite-latest', 'gemini-2.5-flash']
LONG_VIDEO_S = 180

def video_seconds(path):
    try:
        import av
        with av.open(str(path)) as c:
            return float(c.duration or 0) / 1000000
    except Exception:
        return 0.0

class GeminiSpendCap(GeminiDayQuota):
    """Billing on, and the project's monthly spend cap (AI Studio > Dépenses) is reached: Google pauses the API for
    the whole project until the 1st of the month. Another model would hit the same cap, so the run stops asking."""

def quota_kind(e):
    t = str(e)
    if re.search('spend(ing)?[ _-]?(cap|limit)|monthly (spend|usage) (cap|limit)|billing account.*(cap|limit|paused)', t, re.I):
        return 'cap'
    if '429' not in t and 'RESOURCE_EXHAUSTED' not in t:
        return None
    return 'day' if re.search('PerDay|per day|daily', t, re.I) else 'minute'

def gemini_analyse(path, prompt, model=None):
    key = os.environ.get('GEMINI_API_KEY') or W.env_state('GEMINI_API_KEY')[1]
    if not key:
        raise WsError('GEMINI_API_KEY absente : analyse par images clés (--engine frames) ou par AI Studio (--engine pack)')
    try:
        from google import genai
    except ImportError:
        raise WsError('google-genai absent : python -m pip install google-genai')
    client = genai.Client(api_key=key)
    f = client.files.upload(file=str(path))
    try:
        for _ in range(60):
            st = getattr(getattr(f, 'state', None), 'name', str(getattr(f, 'state', '')))
            if st != 'PROCESSING':
                break
            time.sleep(5)
            f = client.files.get(name=f.name)
        if 'FAILED' in str(getattr(getattr(f, 'state', None), 'name', getattr(f, 'state', ''))):
            raise RuntimeError("Gemini n'a pas pu lire le fichier")
        cfg = None
        try:
            if video_seconds(path) > LONG_VIDEO_S:
                from google.genai import types as _t
                cfg = _t.GenerateContentConfig(media_resolution=_t.MediaResolution.MEDIA_RESOLUTION_LOW)
        except Exception:
            cfg = None
        for attempt in (1, 2, 3):
            try:
                resp = client.models.generate_content(model=model or GEMINI_MODEL, contents=[f, prompt], config=cfg)
                return resp.text or ''
            except Exception as e:
                k = quota_kind(e)
                if k == 'cap':
                    raise GeminiSpendCap(str(e)[:200])
                if k == 'day':
                    raise GeminiDayQuota(str(e)[:200])
                low = str(e).lower()
                if '404' in low or 'not_found' in low or 'no longer available' in low:
                    raise GeminiDayQuota('modèle indisponible : ' + str(e)[:150])
                if ('503' in low or 'unavailable' in low or 'high demand' in low) and attempt < 3:
                    print('    Gemini surchargé, 30 s de pause…')
                    time.sleep(30)
                    continue
                if '503' in low or 'unavailable' in low:
                    raise GeminiDayQuota('modèle surchargé : ' + str(e)[:150])
                if k == 'minute' and attempt < 3:
                    print('    quota de la minute atteint, une minute de pause…')
                    time.sleep(62)
                    continue
                raise
    finally:
        try:
            client.files.delete(name=f.name)
        except Exception:
            pass

def cmd_analyse(a):
    (P, ws, state) = open_ws(a.folder)
    F = files(P)
    data = load_list(F['refs'], 'references')
    engine = a.engine or {'gemini': 'gemini', 'frames': 'frames'}.get((state.get('effective_engines') or {}).get('analyse'), 'frames')
    out = P['refs_dir'] / 'Analyses'
    out.mkdir(parents=True, exist_ok=True)
    if a.answer and len(a.codes) != 1:
        raise WsError('--answer va avec une seule référence : research.py analyse <dossier> <CODE> --answer réponse.md')
    codes = list(a.codes)
    if a.all:
        codes += [r['code'] for r in data['references'] if isinstance(r, dict) and r.get('file') and (not r.get('analysis_complete')) and (r.get('code') not in codes)]
        if engine == 'frames' and len(codes) > 20:
            print(f'  {len(codes)} références sans Gemini : chacune se lit avec Claude (images clés). Une clé Gemini gratuite les fait toutes sans entamer ton usage Claude (ws.py doctor dit comment).')
    if not codes:
        raise WsError('donne les codes à analyser, ou --all')
    model = gemini_model(ws)
    chain = [model] + [m for m in GEMINI_CHAIN_FREE if m != model] if not os.environ.get('GEMINI_MODEL') else [model]
    waiting = []
    capped = False
    for code in codes:
        r = ref_by_code(data['references'], code)
        if not r:
            print(f'  {code} : pas dans library/references.yaml')
            continue
        if not r.get('file') and (not a.answer):
            print(f"  {code} : pas de fichier. Regarde-la en ligne ({r.get('url') or 'lien absent'}), écris ce que tu vois avec le même plan en 7 parties, puis : research.py analyse <dossier> {code} --answer vu.md")
            continue
        src = P['refs_dir'] / r['file'] if r.get('file') else None
        dest = out / f"{r['code']}_ANALYSE.md"
        if a.answer:
            ans = Path(a.answer).expanduser()
            if not ans.exists() and (P['root'] / a.answer).exists():
                ans = P['root'] / a.answer
            text = read_text(ans)
            dest.write_text(f"<!-- {r['code']} | réponse enregistrée | {today()} -->\n\n{text}", encoding='utf-8')
            r.update({'analysis': f'Analyses/{dest.name}', 'analysis_engine': r.get('analysis_engine') or 'aistudio', 'skeleton': True, 'analysis_complete': complete(text)})
            if not r.get('file'):
                r.update({'status': 'seen_online', 'analysis_engine': 'online'})
            print(f'  {code} : réponse enregistrée ({len(text)} signes)' + ('' if complete(text) else ' — PARTIE 7 absente : réponse coupée ?'))
        elif engine == 'gemini':
            if not chain:
                waiting.append(code)
                continue
            try:
                while True:
                    try:
                        model = chain[0]
                        text = gemini_analyse(src, prompt_for(P, r), model)
                        break
                    except GeminiSpendCap:
                        print("    plafond de dépenses du mois atteint (AI Studio > Dépenses) : Google met l'API en pause jusqu'au 1er du mois, je n'interroge plus Gemini")
                        chain.clear()
                        capped = True
                        raise
                    except GeminiDayQuota:
                        print(f'    {chain[0]} : quota du jour épuisé, modèle indisponible ou surchargé' + (f', je passe à {chain[1]}' if len(chain) > 1 else ''))
                        chain.pop(0)
                        if not chain:
                            raise
            except GeminiDayQuota:
                waiting.append(code)
                continue
            except WsError:
                raise
            except Exception as e:
                print(f'  {code} : Gemini refuse ({type(e).__name__} : {str(e)[:120]}) ; passe aux images clés : --engine frames')
                continue
            if not text.strip():
                print(f"  {code} : Gemini a répondu vide ; rien n'est enregistré, relance ou passe aux images clés")
                continue
            dest.write_text(f"<!-- {r['code']} | {model} | API | {today()} -->\n\n{text}", encoding='utf-8')
            r.update({'analysis': f'Analyses/{dest.name}', 'analysis_engine': 'gemini', 'skeleton': True, 'analysis_complete': complete(text)})
            print(f'  {code} : {len(text)} signes' + ('' if complete(text) else ' — PARTIE 7 absente : réponse coupée, relance'))
        elif engine == 'pack':
            pack = P['refs_dir'] / '_gemini'
            pack.mkdir(exist_ok=True)
            shutil.copy(src, pack / src.name)
            (pack / f"{r['code']}_PROMPT.txt").write_text(prompt_for(P, r), encoding='utf-8')
            r.update({'analysis_engine': 'aistudio', 'skeleton': True})
            print(f"  {code} : _gemini/{src.name} + {r['code']}_PROMPT.txt prêts pour AI Studio ; enregistre la réponse avec research.py analyse <dossier> {r['code']} --answer <fichier>")
        else:
            frames_dir = P['refs_dir'] / 'Frames'
            frames_dir.mkdir(exist_ok=True)
            stamps = []
            if is_video(src):
                (ims, _) = video_frames(src, 8)
                for (t, im) in ims:
                    stamp = stamp_of(t)
                    if stamp not in stamps:
                        im.convert('RGB').save(frames_dir / f"{r['code']}_{stamp}.jpg", quality=88)
                        stamps.append(stamp)
            if not dest.exists():
                pics = ', '.join((f"Frames/{r['code']}_{s}.jpg" for s in stamps)) or r['file']
                dest.write_text(f"<!-- {r['code']} | images clés lues par Claude | {today()} -->\n\n# {r['code']} — analyse plan par plan\n\nImages : {pics}\n\n{PLACEHOLDER} ci-dessous, en regardant chaque image et en lisant la transcription ; remplace tout ce bloc.)\n\n" + prompt_for(P, r), encoding='utf-8')
            r.update({'analysis': f'Analyses/{dest.name}', 'analysis_engine': 'frames', 'skeleton': True, 'analysis_complete': complete(read_text(dest)), 'frames': sorted(set((r.get('frames') or []) + stamps))})
            print(f"  {code} : {len(stamps)} image(s) clé(s) + le guide dans Analyses/{dest.name} ; regarde les images et écris l'analyse à la place du guide")
        save_refs(F['refs'], data)
    if waiting and capped:
        print(f"\n{len(waiting)} référence(s) attendent : le plafond de dépenses mensuel de ton projet Gemini est atteint ({', '.join(waiting[:12])}{('…' if len(waiting) > 12 else '')}). Google reprend le 1er du mois. Pour continuer avant : relève le plafond dans AI Studio (Dépenses, « Plafond de dépenses mensuel »), ou « --engine frames » (Claude lit les images clés), ou « --engine pack » (AI Studio dans le navigateur).")
        journal(P, f"Analyses Gemini : {len(waiting)} en attente, plafond de dépenses atteint ({', '.join(waiting)})")
    elif waiting:
        print(f"\n{len(waiting)} référence(s) attendent : le quota gratuit du jour est épuisé sur tous les modèles ({', '.join(waiting[:12])}{('…' if len(waiting) > 12 else '')}). Il revient à minuit heure du Pacifique (08:00 GMT, 09:00 au Bénin) : relance « research.py analyse <dossier> --all » demain, il reprend où il s'est arrêté. Si c'est urgent : « --engine frames » sur celles qui comptent (Claude lit les images clés), ou « --engine pack » pour AI Studio dans le navigateur, qui a son propre quota.")
        journal(P, f"Analyses Gemini : {len(waiting)} en attente du quota de demain ({', '.join(waiting)})")
    journal(P, f"Analyses ({('réponse' if a.answer else engine)}) : {', '.join((c.upper() for c in a.codes))}")
    refresh(P, ws, state)

def intent_of(comment):
    t = fold(comment)
    return any((re.search(p, t) for p in INTENT_PHRASES))

def objections_of(comment, table=None):
    t = fold(comment)
    return [k for (k, p) in (table or OBJECTIONS).items() if re.search(p, t)]

def cmd_intent(a):
    (P, ws, state) = open_ws(a.folder)
    F = files(P)
    src = Path(a.file).expanduser()
    if not src.exists() and (P['root'] / a.file).exists():
        src = P['root'] / a.file
    if not src.exists():
        raise WsError(f'fichier introuvable : {a.file}')
    raw = json.loads(src.read_text(encoding='utf-8-sig'))
    raw = raw.get('result', raw) if isinstance(raw, dict) else raw
    items = raw.get('videos', raw) if isinstance(raw, dict) else {}
    if not isinstance(items, dict) or not items or (not all((isinstance(v, dict) for v in items.values()))):
        raise WsError(f'{src.name} : il faut le résultat de browser/tiktok_comments.js ou fb_comments.js ({{{{id: {{{{read, comments: [...]}}}}}}}})')
    refs = load_list(F['refs'], 'references')
    cands = load_list(F['cands'], 'candidates')
    table = K.objections(ws)
    (voice, totals, done) = ([], {k: 0 for k in table}, 0)
    for (vid, v) in items.items():
        comments = [str(c) for c in v.get('comments') or []]
        read = int(v.get('read') or len(comments))
        buying = [c for c in comments if intent_of(c)]
        obj = {k: 0 for k in table}
        for c in comments:
            for k in objections_of(c, table):
                obj[k] += 1
                totals[k] += 1
        it = {'buying': len(buying), 'read': read, 'objections': {k: n for (k, n) in obj.items() if n}}
        for lst in (refs['references'], cands['candidates']):
            for x in lst:
                if str(x.get('id')) == str(vid) or str(x.get('code') or '') == str(vid):
                    x['intent'] = it
        code = next((r['code'] for r in refs['references'] if str(r.get('id')) == str(vid) or r.get('code') == vid), vid)
        voice += [f"- [{code}]{(' 🛒' if intent_of(c) else '')}{(' (' + ', '.join(objections_of(c, table)) + ')' if objections_of(c, table) else '')} {c}" for c in comments]
        done += 1
    save_refs(F['refs'], refs)
    dump_yaml(F['cands'], cands)
    F['voice'].mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime('%Y-%m-%d-%H%M%S')
    source = str((raw.get('source') if isinstance(raw, dict) else '') or next((v.get('source') for v in items.values() if v.get('source')), '') or 'tiktok').lower()
    source = source if source in ('facebook', 'instagram', 'tiktok') else 'tiktok'
    vf = F['voice'] / f'commentaires-{source}-{stamp}.md'
    head = f"# Commentaires {(source.capitalize() if source != 'tiktok' else 'TikTok')} lus le {today()}\n\nTels quels : les mots des acheteurs, leurs questions, leurs objections. 🛒 = demande à acheter (prix, livraison, lien). Entre parenthèses : le type d'objection.\n\nObjections comptées : " + ', '.join((f'{k} {n}' for (k, n) in totals.items() if n)) + '\n\n'
    vf.write_text(head + '\n'.join(voice) + '\n', encoding='utf-8')
    journal(P, f"Intention d'achat lue sur {done} vidéo(s) ; commentaires dans library/voice/{vf.name}")
    refresh(P, ws, state)
    print(f"{done} vidéo(s) : intention d'achat notée ; {len(voice)} commentaires dans library/voice/{vf.name}")
    print('Objections : ' + (', '.join((f'{k} {n}' for (k, n) in sorted(totals.items(), key=lambda x: -x[1]) if n)) or 'aucune repérée'))

def build_parser():
    ap = W.FrParser(prog='research.py', description='La recherche : trouver, choisir, télécharger, transcrire, lire.')
    sub = ap.add_subparsers(dest='cmd', required=True, parser_class=W.FrParser)
    p = sub.add_parser('plan')
    p.add_argument('folder')
    p.add_argument('--terms')
    p.add_argument('--countries')
    p.add_argument('--refs', type=int, help='nombre de références à garder (40 en mode gratuit, 60 sinon)')
    p.add_argument('--must', help='mots dont une pub pertinente porte au moins un, séparés par des virgules')
    p.add_argument('--not', dest='not', help='mots qui mettent une pub de côté (« école, banque »)')
    p.add_argument('--page', help="l'identifiant d'une page d'annonceur à lire en entier (view_all_page_id)")
    p.add_argument('--name', help="le nom de l'annonceur, pour --page")
    p.add_argument('--format', action='store_true', help='ajouter les mots du format (atelier gratuit, 3 soirées, défi…)')
    p.add_argument('--sellers', help='suivre des vendeurs : noms ou domaines, tous pays (la boule de neige)')
    p = sub.add_parser('discover')
    p.add_argument('folder')
    p.add_argument('--platform', choices=('adlib', 'tiktok', 'instagram'))
    p.add_argument('--limit', type=int, default=40)
    p.add_argument('--dry-run', dest='dry_run', action='store_true')
    p.add_argument('--yes', action='store_true', help='accepter le coût estimé et lancer')
    p.add_argument('--all', action='store_true', help='refaire aussi les recherches déjà faites')
    p = sub.add_parser('paste')
    p.add_argument('folder')
    p.add_argument('--term')
    p.add_argument('--country')
    p.add_argument('--lang')
    p.add_argument('--save', help='seulement enregistrer la capture à cet endroit (ex. library/competitors/kinova.json)')
    p.add_argument('--again', action='store_true', help="importer même si c'est la même capture que la précédente")
    p = sub.add_parser('import')
    p.add_argument('folder')
    p.add_argument('file')
    p.add_argument('--term')
    p.add_argument('--country')
    p.add_argument('--lang')
    p = sub.add_parser('rank')
    p.add_argument('folder')
    p.add_argument('--platform', choices=tuple(PLATFORMS))
    p.add_argument('--top', type=int, default=20)
    p.add_argument('--landing', choices=('quiz',), help="seulement les pubs dont la page d'arrivée est un quiz")
    p = sub.add_parser('pick')
    p.add_argument('folder')
    p.add_argument('ids', nargs='*')
    p.add_argument('--why')
    p.add_argument('--auto', action='store_true')
    p.add_argument('--adlib', type=int)
    p.add_argument('--tiktok', type=int)
    p.add_argument('--instagram', type=int)
    p.add_argument('--id', nargs='+', help="l'id d'une pub vue en direct dans la Bibliothèque (téléchargée par yt-dlp)")
    p.add_argument('--author', help="avec --id : l'annonceur")
    p.add_argument('--text', help='avec --id : le texte de la pub')
    p.add_argument('--country', help='avec --id : le pays (code)')
    p.add_argument('--started', help='avec --id : la date de début de diffusion (AAAA-MM-JJ)')
    p = sub.add_parser('voice')
    p.add_argument('folder')
    p.add_argument('file', help='commentaires : JSON (YouTube…), .txt ou .md')
    p.add_argument('--source', help="d'où viennent ces mots (« youtube durer au lit ») : va dans le nom du fichier")
    p = sub.add_parser('reject')
    p.add_argument('folder')
    p.add_argument('ids', nargs='+')
    p.add_argument('--reason', required=True)
    p = sub.add_parser('download')
    p.add_argument('folder')
    p.add_argument('codes', nargs='*')
    p = sub.add_parser('transcribe')
    p.add_argument('folder')
    p.add_argument('codes', nargs='*')
    p.add_argument('--model', default='auto', choices=('base', 'small', 'medium', 'auto'))
    p.add_argument('--fast', action='store_true')
    p.add_argument('--redo', action='store_true', help='refaire les transcriptions déjà faites')
    p = sub.add_parser('sheet')
    p.add_argument('folder')
    p.add_argument('--platform', choices=tuple(PLATFORMS) + ('all',))
    p.add_argument('--by-author', dest='by_author', action='store_true', help='une planche par annonceur')
    p.add_argument('--images', action='store_true', help='seulement les images')
    p = sub.add_parser('frames')
    p.add_argument('folder')
    p.add_argument('code')
    p.add_argument('secs', nargs='*', help="des secondes (un seul code), ou d'autres codes : frames <dossier> AL01 AL09")
    p.add_argument('--auto', type=int, default=6)
    p = sub.add_parser('analyse')
    p.add_argument('folder')
    p.add_argument('codes', nargs='*')
    p.add_argument('--all', action='store_true', help='toutes les références téléchargées pas encore analysées')
    p.add_argument('--engine', choices=('gemini', 'frames', 'pack'))
    p.add_argument('--answer', help='enregistrer une réponse écrite ailleurs (AI Studio) pour cette référence')
    p = sub.add_parser('intent')
    p.add_argument('folder')
    p.add_argument('file')
    p = sub.add_parser('check')
    p.add_argument('folder')
    p.add_argument('id', nargs='?')
    p.add_argument('status', nargs='?', choices=('ok', 'warn', 'fail', 'todo', 'na'))
    p.add_argument('--evidence', default='')
    for name in ('hooks', 'status', 'log'):
        p = sub.add_parser(name)
        p.add_argument('folder')
    p = sub.add_parser('report')
    p.add_argument('folder')
    p.add_argument('--done', action='store_true')
    return ap

def _forward(a):
    """Commands not listed as local run on the licence server (see csos_client.py)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'creative-strategist' / 'scripts'))
    import csos_client
    sys.exit(csos_client.forward(__file__, sys.argv[1:]))

def main(argv=None):
    a = build_parser().parse_args(argv)
    cmds = {'discover': cmd_discover, 'paste': cmd_paste, 'import': cmd_import, 'download': cmd_download, 'transcribe': cmd_transcribe, 'sheet': cmd_sheet, 'frames': cmd_frames, 'analyse': cmd_analyse, 'voice': cmd_voice}
    try:
        cmds.get(a.cmd, _forward)(a)
    except WsError as e:
        print(f'ERREUR : {e}', file=sys.stderr)
        sys.exit(2)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f'ERREUR : fichier JSON illisible ({type(e).__name__}) : refais la capture et enregistre son résultat tel quel.', file=sys.stderr)
        sys.exit(2)
    except PermissionError as e:
        print(f"ERREUR : fichier verrouillé ({Path(str(e.filename or '')).name or 'inconnu'}) : ferme-le et relance.", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f'ERREUR inattendue ({type(e).__name__} : {e}).', file=sys.stderr)
        if os.environ.get('WS_DEBUG'):
            raise
        sys.exit(3)
if __name__ == '__main__':
    main()
