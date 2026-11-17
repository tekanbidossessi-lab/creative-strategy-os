"""review.py — the quality check of the creative-strategy suite: every finished file against its brief, before a
cent is spent on it.

    python review.py probe   <dossier> [C01 | "C01 V1 B" ...] [--no-transcribe] [--model small]
    python review.py check   <dossier> [C01 ...]           the finished files against their briefs, every rule a machine can verify
    python review.py verdict <dossier> "C01 V1 A" ok|fix|reject [--fix "…"]... [--notes "…"]
    python review.py report  <dossier> [--done]            deliverables/CONTROLE.md, with the message for each maker

Files: cycles/cycle-NN/creatives/<code>.<ext> (delivered by briefs.py deliver), creatives/_review/<code>.txt (what
is said, from Whisper, word-timed) or <code>.srt / .vtt beside the file (the editor's subtitles, used when newer
than the file), creatives/_review/<code>_sheet.png (the frames to look at, the apps' safe zones drawn),
cycles/cycle-NN/ads.yaml (review: probe, machine, verdict, fixes; status), deliverables/CONTROLE.md, audit.yaml.

What a machine can measure is measured; what only eyes can judge is judged on the contact sheet and recorded with
`verdict`. Richie's rules are errors under « accelerateur », points to review otherwise. Nothing is locked.

Édition sous licence : seules les commandes probe tournent ici ; les autres partent sur le serveur de licence."""
import math
import os
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent.parent
for (need, what) in ((SKILLS / 'creative-strategist' / 'scripts' / 'ws.py', 'creative-strategist'), (SKILLS / 'cs-briefs' / 'scripts' / 'briefs.py', 'cs-briefs')):
    if not need.exists():
        print(f'ERREUR : le skill {what} doit être installé à côté de cs-review (attendu : {need}).', file=sys.stderr)
        sys.exit(2)
sys.path.insert(0, str(SKILLS / 'cs-briefs' / 'scripts'))
import briefs as B
import ws as W
from ws import WsError, open_ws, load_yaml, dump_yaml, journal, refresh, today, read_text
IMAGE_EXT = ('.jpg', '.jpeg', '.png', '.webp')
VERDICTS = {'ok': 'ready', 'fix': 'production', 'reject': 'brief'}
SAFE = {'top': 0.12, 'bottom': 0.3, 'right': 0.15}

def ctx(folder):
    (P, ws, state) = open_ws(folder)
    F = B.files(P, state)
    F['review'] = F['creatives'] / '_review'
    F['report'] = P['root'] / 'deliverables' / 'CONTROLE.md'
    return (P, ws, state, F)

def ledger(F):
    data = load_yaml(F['ads'], {}) or {}
    if not isinstance(data, dict) or not data.get('ads'):
        raise WsError('le registre des pubs est vide : lance « strategy.py ledger <dossier> »')
    return data

def rv_of(row):
    if not isinstance(row.get('review'), dict):
        row['review'] = {}
    return row['review']

def pick(data, codes, default_status=('review',)):
    """Ledger rows by « C01 » (all its ads) or by full code; by default every row waiting for review."""
    rows = [x for x in data['ads'] if isinstance(x, dict) and x.get('code')]
    if not codes:
        return [x for x in rows if x.get('status') in default_status and x.get('file')]
    out = []
    for c in codes:
        c = c.upper().strip()
        hit = [x for x in rows if str(x['code']).upper() == c or (' ' not in c and str(x['code']).upper().startswith(c + ' '))]
        if not hit:
            raise WsError(f"« {c} » n'est pas dans le registre (cycles/…/ads.yaml)")
        out += [x for x in hit if x not in out]
    return out

def file_of(P, F, row):
    f = str(row.get('file') or '')
    if not f:
        return None
    for base in (F['creatives'].parent, P['root'], F['creatives']):
        p = base / f
        if p.exists():
            return p
    return F['creatives'].parent / f

def stamp(path):
    st = path.stat()
    return f'{int(st.st_mtime)}-{st.st_size}'

def market_lang(ws):
    m = next((m for m in ws.get('markets') or [] if isinstance(m, dict)), {})
    return m.get('language') or ws.get('language') or 'fr'

def first_frame(c):
    st = c.streams.video[0]
    for fr in c.decode(st):
        return fr
    return None

def media_facts(path):
    """Duration, displayed size (rotation applied), frame rate, bitrate, size, sound; size for an image."""
    ext = path.suffix.lower()
    size_mb = round(path.stat().st_size / 1000000.0, 2)
    if ext in IMAGE_EXT:
        from PIL import Image
        try:
            with Image.open(path) as im:
                return {'kind': 'image', 'width': im.width, 'height': im.height, 'size_mb': size_mb}
        except Exception as e:
            raise WsError(f"{path.name} ne s'ouvre pas comme une image ({type(e).__name__}) : exporte-la en .jpg ou .png")
    import av
    try:
        c = av.open(str(path))
    except Exception as e:
        raise WsError(f"{path.name} ne s'ouvre pas comme une vidéo ({type(e).__name__}) : demande un nouvel export")
    try:
        if not c.streams.video:
            raise WsError(f"{path.name} n'a pas d'image (son seul) : ce n'est pas la vidéo finie")
        v = c.streams.video[0]
        a_ = c.streams.audio[0] if c.streams.audio else None
        dur = float(c.duration) / 1000000.0 if c.duration else float(v.duration * v.time_base) if v.duration else None
        fr = first_frame(c)
        rot = int(getattr(fr, 'rotation', 0) or 0) % 360 if fr is not None else 0
        (w, h) = (v.codec_context.width, v.codec_context.height)
        if rot % 180 == 90:
            (w, h) = (h, w)
        out = {'kind': 'video', 'duration': round(dur, 2) if dur else None, 'width': w, 'height': h, 'rotation': rot, 'fps': round(float(v.average_rate), 2) if v.average_rate else None, 'audio': bool(a_), 'size_mb': size_mb, 'mbps': round(path.stat().st_size * 8 / dur / 1000000.0, 2) if dur else None}
    finally:
        c.close()
    if out['audio']:
        out.update(sound(path))
    return out
SCALE = {'s16': 32768.0, 's16p': 32768.0, 's32': 2147483648.0, 's32p': 2147483648.0, 's64': 9.2e+18, 's64p': 9.2e+18}

def sound(path, seconds=60):
    """Mean level (dBFS, 0 = loudest), peak and share of clipped samples, over the first minute."""
    import av
    try:
        import numpy as np
    except ImportError:
        return {}
    c = av.open(str(path))
    try:
        st = c.streams.audio[0]
        (tot, n, peak, clip) = (0.0, 0, 0.0, 0)
        for fr in c.decode(st):
            name = fr.format.name
            a_ = fr.to_ndarray().astype('float64')
            if name in ('u8', 'u8p'):
                a_ = (a_ - 128.0) / 128.0
            elif name in SCALE:
                a_ = a_ / SCALE[name]
            tot += float((a_ ** 2).sum())
            n += a_.size
            peak = max(peak, float(np.abs(a_).max()) if a_.size else 0)
            clip += int((np.abs(a_) >= 0.999).sum())
            if fr.time is not None and fr.time > seconds:
                break
        if not n:
            return {'loudness_db': -120.0}
        rms = math.sqrt(tot / n)
        return {'loudness_db': round(20 * math.log10(rms), 1) if rms > 0 else -120.0, 'peak_db': round(20 * math.log10(peak), 1) if peak > 0 else -120.0, 'clipped_pct': round(clip / n * 100, 3)}
    finally:
        c.close()

def frames_at(path, times):
    import av
    c = av.open(str(path))
    out = []
    try:
        if not c.streams.video:
            return out
        st = c.streams.video[0]
        for t in times:
            c.seek(int(max(0, t) / st.time_base), stream=st, any_frame=False, backward=True)
            (img, rot) = (None, 0)
            for fr in c.decode(st):
                (img, rot) = (fr.to_image(), int(getattr(fr, 'rotation', 0) or 0))
                if fr.time is None or fr.time >= t - 0.05:
                    break
            if img is not None:
                out.append((t, img.rotate(rot, expand=True) if rot % 360 else img))
    finally:
        c.close()
    return out

def look(img):
    """What a machine sees in one image: brightness, contrast, black bands top and bottom."""
    from PIL import ImageStat
    g = img.convert('L')
    st = ImageStat.Stat(g)
    (w, h) = g.size
    band = max(1, int(h * 0.1))
    (top, bot) = (ImageStat.Stat(g.crop((0, 0, w, band))), ImageStat.Stat(g.crop((0, h - band, w, h))))
    bars = top.mean[0] < 14 and bot.mean[0] < 14 and (top.stddev[0] < 5) and (bot.stddev[0] < 5) and (st.stddev[0] > 12)
    return {'mean': round(st.mean[0], 1), 'std': round(st.stddev[0], 1), 'bars': bool(bars)}

def moved(a, b):
    from PIL import ImageChops, ImageStat
    (x, y) = (a.convert('L').resize((90, 160)), b.convert('L').resize((90, 160)))
    return ImageStat.Stat(ImageChops.difference(x, y)).mean[0]

def contact_sheet(path, dur, dest):
    """The first five seconds second by second, six images over the rest, the last one; the safe zones drawn."""
    from PIL import Image, ImageDraw
    times = [0.0, 0.5, 1, 2, 3, 4, 5]
    if dur and dur > 6:
        times += [5 + (dur - 5.5) * k / 7 for k in range(1, 7)] + [max(0, dur - 0.3)]
    times = [t for t in times if not dur or t < dur]
    shots = frames_at(path, times)
    if not shots:
        return (None, {})
    (w_, h_) = (180, 320)
    cols = 7
    sheet = Image.new('RGB', (cols * w_, math.ceil(len(shots) / cols) * (h_ + 20)), 'white')
    d = ImageDraw.Draw(sheet)
    for (i, (t, im)) in enumerate(shots):
        (x, y) = (i % cols * w_, i // cols * (h_ + 20))
        thumb = im.convert('RGB')
        thumb.thumbnail((w_, h_))
        sheet.paste(thumb, (x, y + 20))
        (tw, th) = thumb.size
        for yy in (y + 20 + int(th * SAFE['top']), y + 20 + int(th * (1 - SAFE['bottom']))):
            d.line([(x, yy), (x + tw, yy)], fill=(255, 0, 0), width=1)
        xx = x + int(tw * (1 - SAFE['right']))
        d.line([(xx, y + 20), (xx, y + 20 + th)], fill=(255, 0, 0), width=1)
        d.text((x + 4, y + 4), f'{int(t // 60)}:{t % 60:04.1f}', fill='red')
    dest.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dest)
    first = look(shots[0][1])
    mid = look(shots[len(shots) // 2][1])
    one = next((im for (t, im) in shots if t >= 1), None)
    half = next((look(im) for (t, im) in shots if 0.3 <= t <= 0.6), None)
    return (dest, {'first_brightness': first['mean'], 'first_std': first['std'], 'bars': first['bars'] and mid['bars'], 'half_brightness': half['mean'] if half else None, 'motion_1s': round(moved(shots[0][1], one), 1) if one is not None else None})

def spoken_source(F, row, path):
    """The editor's subtitles when newer than the file, otherwise Whisper's transcript when newer than the file."""
    for ext in ('.srt', '.vtt'):
        s = path.with_suffix(ext)
        if s.exists():
            if s.stat().st_mtime >= path.stat().st_mtime - 1:
                return (s, None)
            return (None, f"{s.name} est plus ancien que le fichier : ignoré (refais l'export des sous-titres)")
    return (F['review'] / f"{row['code']}.txt", None)

def transcribe(path, dest, lang, model_name):
    """Word-timed: a line every 1.5 s at most, so the first five seconds are really the first five seconds."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise WsError('faster-whisper absent : python -m pip install faster-whisper av (ou donne les sous-titres en .srt à côté du fichier, ou relance avec --no-transcribe)')
    model = WhisperModel(model_name, device='cpu', compute_type='int8')
    (segs, info) = model.transcribe(str(path), beam_size=5, vad_filter=True, word_timestamps=True, condition_on_previous_text=False, language=lang if lang in ('fr', 'en', 'es', 'pt', 'ar') else None)
    lines = [f'# {path.stem} | lang={info.language} | model={model_name} | dur={info.duration:.0f}s']
    for s in segs:
        (chunk, t0) = ([], None)
        for w_ in s.words or []:
            if t0 is None:
                t0 = w_.start
            if w_.start - t0 > 1.5 and chunk:
                lines.append(f"[{int(t0 // 60)}:{int(t0 % 60):02d}.{int(t0 % 1 * 10)}] {''.join(chunk).strip()}")
                (chunk, t0) = ([], w_.start)
            chunk.append(w_.word)
        if chunk:
            lines.append(f"[{int(t0 // 60)}:{int(t0 % 60):02d}.{int(t0 % 1 * 10)}] {''.join(chunk).strip()}")
        elif not s.words:
            lines.append(f'[{int(s.start // 60)}:{int(s.start % 60):02d}.{int(s.start % 1 * 10)}] {s.text.strip()}')
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text('\n'.join(lines), encoding='utf-8')

def probe_one(P, ws, F, row, a):
    path = file_of(P, F, row)
    rv = rv_of(row)
    if not path or not path.exists():
        rv['probe'] = {'error': 'fichier absent'}
        return f"  {row['code']} : fichier absent ({row.get('file') or 'pas de fichier dans le registre'})"
    facts = media_facts(path)
    facts['stamp'] = stamp(path)
    note = ''
    if facts['kind'] == 'video':
        (sheet, seen) = contact_sheet(path, facts.get('duration'), F['review'] / f"{row['code']}_sheet.png")
        facts.update(seen)
        facts['sheet'] = str(sheet.relative_to(P['root'])).replace('\\', '/') if sheet else ''
        (sp, note) = spoken_source(F, row, path)
        if sp is None:
            sp = F['review'] / f"{row['code']}.txt"
        if sp.suffix == '.txt' and sp.exists() and (sp.stat().st_mtime < path.stat().st_mtime - 1):
            sp.unlink()
        if facts.get('audio') and (not sp.exists()) and (not a.no_transcribe):
            print(f"  {row['code']} : transcription (Whisper {a.model})…", flush=True)
            transcribe(path, sp, market_lang(ws), a.model)
        facts['spoken'] = str(sp.relative_to(P['root'])).replace('\\', '/') if sp.exists() else ''
    rv['probe'] = {**facts, 'on': today()}
    rv.pop('machine', None)
    msg = f"{facts['width']}×{facts['height']}, {facts.get('duration') or '?'} s, {('son' if facts.get('audio') else 'SANS SON')}" + (f" ({facts['loudness_db']} dB)" if facts.get('loudness_db') is not None else '') + (f", planche : {facts['sheet']}" if facts.get('sheet') else '') if facts['kind'] == 'video' else f"image {facts['width']}×{facts['height']}"
    return f"  {row['code']} : {msg}" + (f' · {note}' if note else '')

def cmd_probe(a):
    (P, ws, state, F) = ctx(a.folder)
    data = ledger(F)
    rows = pick(data, a.codes)
    if not rows:
        print("Rien à contrôler : aucune pub au statut « review » (briefs.py deliver d'abord)")
        return
    bad = 0
    for row in rows:
        try:
            print(probe_one(P, ws, F, row, a))
        except WsError as e:
            rv_of(row)['probe'] = {'error': str(e), 'on': today()}
            print(f"  {row['code']} : {e}")
            bad += 1
        dump_yaml(F['ads'], data)
    journal(P, f'Contrôle : {len(rows)} fichier(s) mesuré(s)')
    W.set_step(P, state, 'review', 'doing')
    refresh(P, ws, state)
    print("Regarde chaque planche (la première image, les sous-titres, la fin ; les traits rouges sont les zones que l'appli couvre), puis review.py check." + (f' {bad} fichier(s) illisible(s).' if bad else ''))
    if bad and len(rows) == bad:
        sys.exit(2)

def build_parser():
    ap = W.FrParser(prog='review.py', description='Le contrôle qualité des créatives finies.')
    sub = ap.add_subparsers(dest='cmd', required=True, parser_class=W.FrParser)
    p = sub.add_parser('probe')
    p.add_argument('folder')
    p.add_argument('codes', nargs='*')
    p.add_argument('--no-transcribe', action='store_true')
    p.add_argument('--model', default='small')
    p = sub.add_parser('check')
    p.add_argument('folder')
    p.add_argument('codes', nargs='*')
    p = sub.add_parser('verdict')
    p.add_argument('folder')
    p.add_argument('code')
    p.add_argument('verdict', choices=sorted(VERDICTS))
    p.add_argument('--fix', action='append')
    p.add_argument('--notes')
    p.add_argument('--by')
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
    cmds = {'probe': cmd_probe}
    try:
        cmds.get(a.cmd, _forward)(a)
    except WsError as e:
        print(f'ERREUR : {e}', file=sys.stderr)
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
