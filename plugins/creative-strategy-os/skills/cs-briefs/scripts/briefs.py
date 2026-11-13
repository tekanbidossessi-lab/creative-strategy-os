"""briefs.py — the briefs step of the creative-strategy suite, and production tracking: one page per creative that
someone can produce at 11 p.m. with nobody to ask, the script taken word for word from its reference.

    python briefs.py init    <dossier> [C01 ...] [--route ai|filmed|edit] [--force]
    python briefs.py check   <dossier> [C01 ...]           every rule a machine can verify, brief by brief
    python briefs.py render  <dossier> [C01 ...]           briefs/C##.md, deliverables/BRIEFS.md and BRIEFS.html
    python briefs.py opening <dossier> [C01 ...] [--write]  the script's opening becomes the official one (brief + strategy)
    python briefs.py fill    <dossier> <lot.yaml> [--force]  write a batch of briefs from one file (rows, fields, status)
    python briefs.py kit     <dossier> C01 [--zip]         the editor's folder: the brief, the references, the frames
    python briefs.py export  <dossier>                     the briefs into the pca-plan-attaque creatives (plan_briefs.yaml)
    python briefs.py assign  <dossier> C01 [C02 ...] --owner "…" [--due 2026-11-02] [--start]
    python briefs.py deliver <dossier> C01 <fichier> [--letter A] [--variation 1]
    python briefs.py board   <dossier>                     deliverables/PRODUCTION.md: who makes what, for when, what is late
    python briefs.py report  <dossier> [--done]

Files (creative-strategist/references/workspace.md): cycles/cycle-NN/briefs/C##.yaml (the brief, written by the
strategist), briefs/C##.md (rendered), briefs/C##-kit/ (the editor's folder), cycles/cycle-NN/creatives/ (the
finished files, named by their ad code), cycles/cycle-NN/ads.yaml (owner, due, file, status), deliverables/BRIEFS.md,
BRIEFS.html (print: one brief per page), PRODUCTION.md, audit.yaml (the briefs checks).

The suite's own method is always an error: every brief exists, is complete, and its script column is the
reference's own words. Richie's programme rules (pca-plan-attaque R1–R31) are errors with the programme
« accelerateur » and points to review otherwise. Claims stay as the references ran them: no compliance block.

Édition sous licence : seules les commandes assign, deliver, kit tournent ici ; les autres partent sur le serveur de licence."""
import html
import os
import re
import shutil
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SKILLS = HERE.parent.parent
SUITE = SKILLS / 'creative-strategist' / 'scripts'
for (need, what) in ((SUITE / 'ws.py', 'creative-strategist'), (SKILLS / 'cs-strategy' / 'scripts' / 'strategy.py', 'cs-strategy'), (SKILLS / 'cs-offer' / 'scripts' / 'offer.py', 'cs-offer')):
    if not need.exists():
        print(f'ERREUR : le skill {what} doit être installé à côté de cs-briefs (attendu : {need}).', file=sys.stderr)
        sys.exit(2)
sys.path.insert(0, str(SUITE))
sys.path.insert(0, str(SKILLS / 'cs-strategy' / 'scripts'))
sys.path.insert(0, str(SKILLS / 'cs-offer' / 'scripts'))
import ws as W
import kinds as K
import strategy as S
from docs import TEXT as DOC_TEXT
from ws import WsError, open_ws, load_yaml, dump_yaml, journal, refresh, today, read_text
(fold, as_list, as_int, num) = (S.fold, S.as_list, S.as_int, S.num)
ROUTES = {'ai': "générée avec l'IA : une image par plan, puis l'animation, puis la voix", 'filmed': 'filmée au téléphone', 'edit': 'montée à partir de clips, sous une voix off'}
PROD = {'ai': ["Les images de référence, une par plan du déroulé, en 9:16 (Google Flow, ou ton générateur d'images). Très réalistes : vraie peau, vrai intérieur du pays, objets du quotidien, rien de « magazine ». La lumière vient d'une source réelle (fenêtre, lampe, écran) : des ombres visibles, jamais une lumière plate, et le visage reste lisible.", "Anime chaque image dans Google Flow : Veo (plans de 8 s) ou Omni Flash (plans de 10 s). Même personne, mêmes vêtements, mêmes objets d'un plan à l'autre. Dans le prompt vidéo, décris le mouvement et la parole, jamais ce que l'image montre déjà.", "Quand quelqu'un parle à l'écran : très animé, énergique — les mains, la tête, le regard, de petits déplacements ; jamais figé. Vérifie plan par plan que les lèvres suivent chaque mot.", 'La voix : ElevenLabs, à partir de la colonne « Ton script », avec le profil vocal de ce brief (langue et accent du marché).', "Le montage dans CapCut : les plans dans l'ordre du déroulé, sous-titres en gros au centre, le hook textuel en haut de l'écran pendant les 3 à 5 premières secondes, {FIN_ECRITE} écrits à la fin."], 'filmed': ["Téléphone à la verticale, à hauteur des yeux, près d'une fenêtre (lumière de face, jamais dans le dos).", '{OBJET}', 'Filme bloc par bloc, trois prises de chaque, puis garde la meilleure. Parle avec énergie, bouge les mains.', "Monte dans CapCut dans l'ordre du déroulé : sous-titres en gros au centre, le hook textuel en haut de l'écran les 3 à 5 premières secondes, {FIN_ECRITE} écrits à la fin."], 'edit': ['Rassemble les clips du déroulé dans un dossier : les références (leurs liens sont dans le tableau), tes propres vidéos du produit, et les plans qui manquent générés dans Google Flow (Veo 8 s ou Omni Flash 10 s).', 'Enregistre la voix off à partir de la colonne « Ton script » (ElevenLabs avec le profil vocal du brief, ou ta voix au calme, téléphone à 20 cm).', 'Dans CapCut, pose la voix, puis un clip par phrase : un changement de plan toutes les 1 à 2 secondes.', "Sous-titres en gros au centre, le hook textuel en haut de l'écran les 3 à 5 premières secondes, {FIN_ECRITE} écrits à la fin."]}
COMMENT_TOOL = "Recrée la capture du commentaire mot pour mot, avec le pseudo, dans un générateur de commentaires (TikComment, tikcomment.com, pour TikTok ; un générateur de commentaire Facebook ou Instagram pour ces réseaux), puis pose-la à l'écran 3 à 5 secondes au début de la vidéo, avant la réponse."

def kinded(lines, ws):
    """The production and checklist lines for what the project sells (kinds.py): a product ends on its price and
    payment on delivery, a webinar on the day, the hour and « gratuit »."""
    k = K.profile(ws)
    return [str(x).replace('{FIN_ECRITE}', k['end_written']).replace('{FIN_DITE}', k['end_said']).replace('{OBJET}', k['on_set']) for x in lines]

def ws_of(P):
    ws = load_yaml(P['workspace'], {}) if P['workspace'].exists() else {}
    return ws if isinstance(ws, dict) else {}

def files(P, state):
    c = S.cycle_dir(P, state)
    return {'dir': c / 'briefs', 'creatives': c / 'creatives', 'ads': c / 'ads.yaml', 'plan': c / 'plan_strategie.yaml', 'export': c / 'plan_briefs.yaml', 'md': P['root'] / 'deliverables' / 'BRIEFS.md', 'html': P['root'] / 'deliverables' / 'BRIEFS.html', 'board': P['root'] / 'deliverables' / 'PRODUCTION.md'}

def brief_path(F, code):
    return F['dir'] / f'{code}.yaml'

def load_brief(F, code):
    p = brief_path(F, code)
    data = load_yaml(p, {}) or {}
    if not isinstance(data, dict):
        raise WsError(f'briefs/{code}.yaml : il faut un brief (des champs « title: », « script: »…), voir briefs.py init')
    return data

def creatives_of(P, state, codes=None):
    F = S.paths(P, state)
    st = S.load_strategy(F)
    cr = [c for c in S.written_creatives(st) if not c['code'].startswith('C??')]
    if not cr:
        raise WsError("pas encore de créatives écrites dans strategy.yaml : la stratégie d'abord (cs-strategy)")
    if codes:
        want = {c.upper() for c in codes}
        unknown = want - {c['code'] for c in cr}
        if unknown:
            raise WsError(f"créative(s) absente(s) de strategy.yaml : {', '.join(sorted(unknown))}")
        cr = [c for c in cr if c['code'] in want]
    return (st, cr)

def parse_secs(s):
    """« 1 min 15 », « 1m05s », « 45 s », « 0:45 », « 1:15 » -> seconds."""
    s = re.sub('\\b(9:16|16:9|1:1|4:5|4:3)\\b', '', str(s or ''))
    m = re.search('(\\d+)\\s*m(?:in)?\\s*(\\d+)?\\s*s?\\b', s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2) or 0)
    m = re.search('\\b(\\d+):(\\d{2})\\b', s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    m = re.search('(\\d+)\\s*s\\b', s)
    return int(m.group(1)) if m else None

def strip_marks(s):
    return re.sub('\\*\\*(.+?)\\*\\*', '\\1', str(s or ''), flags=re.S)

def rows_of(b):
    sc = b.get('script') if isinstance(b.get('script'), dict) else {}
    out = []
    for r in as_list(sc.get('rows')):
        if isinstance(r, (list, tuple)):
            r = [str(x) if x is not None else '' for x in r] + [''] * 5
            out.append(r[:5])
    return out
CUT_RE = re.compile('^\\(?\\s*(coup[ée]e?|cut)\\s*\\)?$', re.I)

def is_cut(text):
    return bool(CUT_RE.match(strip_marks(text).strip()))

def kept_secs(b, total=None):
    """(seconds the script keeps, seconds of the reference): each row lasts until the next row's time; a cut row
    doesn't count; a last row without time (the sale) counts 4 s."""
    rows = rows_of(b)
    times = [parse_secs(r[1]) if r[1].strip() else None for r in rows]
    known = [t for t in times if t is not None]
    if not known:
        return (None, total)
    end_all = total or max(known) + 3
    kept = 0
    for (i, (r, t)) in enumerate(zip(rows, times)):
        if is_cut(r[3]) or not r[3].strip():
            continue
        if t is None:
            kept += 4 if i == len(rows) - 1 else 0
            continue
        nxt = next((x for x in times[i + 1:] if x is not None and x > t), end_all)
        kept += max(0, nxt - t)
    return (int(round(kept)), int(end_all))

def frame_files(P, code):
    d = P['refs_dir'] / 'Frames'
    return sorted(d.glob(f'{code}_*.jpg')) if d.exists() else []

def is_ready(b):
    return str(b.get('status') or '').strip().lower() == 'ready'

def blocks_of(P, b, img_base):
    """The brief as blocks, rendered to Markdown or HTML by the same order (pca-plan-attaque's spine)."""
    B = [('h1', f"{b.get('code')} · {b.get('title') or ''}")]
    fiche = b.get('fiche') if isinstance(b.get('fiche'), dict) else {}
    fiche = dict(fiche)
    said = parse_secs(fiche.get('Durée'))
    if said and any((is_cut(r[3]) for r in rows_of(b))):
        (kept, ref) = kept_secs(b)
        if kept and ref and (abs(said - ref) <= max(5, 0.1 * ref)) and (kept < 0.75 * said):
            fiche['Durée'] = f'environ {kept} s, vertical 9:16 (la référence : {said} s)'
    if b.get('cta') and 'Fin (CTA)' not in fiche:
        t = K.cta_of(b)
        fiche['Fin (CTA)'] = f"{K.CTA[t]['label']} : {K.cta_what(t, W.load_yaml(P['workspace'], {}) or {})}"
    B.append(('fiche', [(k, str(v)) for (k, v) in fiche.items() if str(v or '').strip()]))
    if any((str(x).strip() for x in as_list(b.get('vision')))):
        B += [('h2', '🎬 Comprendre la vision créative')] + [('p', str(x)) for x in as_list(b.get('vision')) if str(x).strip()]
    an = b.get('ancre') if isinstance(b.get('ancre'), dict) else {}
    B += [('h2', '👤 À qui on parle'), ('p', str(b.get('qui') or '')), ('ul', [f'**{lab}** : {an.get(k)}' for (k, lab) in (('douleur', 'Sa douleur'), ('desir', 'Son désir'), ('mots', 'Ses mots dans le script'), ('moment', 'Son moment de vie')) if str(an.get(k) or '').strip()])]
    B += [('h2', "💡 L'idée en une phrase"), ('p', str(b.get('idee') or ''))]
    if as_list(b.get('leviers')):
        B += [('h2', '🧠 Les leviers psychologiques'), ('ul', [str(x) for x in as_list(b.get('leviers'))])]
    B += [('h2', '🧩 Les références de ce script')]
    if b.get('sources'):
        B.append(('p', str(b['sources'])))
    rr = [[str(x) for x in (r + ['', '', ''])[:3]] for r in as_list(b.get('refs')) if isinstance(r, list)]
    index = S.refs_index(P)
    for row in rr:
        m = re.match('^\\s*([A-Z]{2,3}\\d{2,3})\\b(.*)$', row[0], re.S)
        url = str((index.get(m.group(1)) or {}).get('url') or '') if m else ''
        if url.startswith('http') and '](' not in row[0]:
            row[0] = f'[{m.group(1)}]({url}){m.group(2)}'
    if rr:
        B.append(('table', ['Référence', "Ce qu'on en prend", 'À observer et refaire'], rr))
    imgs = []
    for v in as_list(b.get('visuels')):
        if isinstance(v, dict) and isinstance(v.get('frames'), dict):
            fr = v['frames']
            for s in as_list(fr.get('stamps')):
                imgs.append((f"{img_base}/Frames/{fr.get('tag')}_{s}.jpg", f"{fr.get('tag')} · {s}"))
            if fr.get('caption'):
                cap = re.sub(f"^{re.escape(str(fr.get('tag')))}\\s*[:·-]\\s*", '', str(fr['caption']))
                imgs.append((None, f"{fr.get('tag')} : {cap}"))
        if isinstance(v, dict) and isinstance(v.get('images'), dict):
            im = v['images']
            caps = as_list(im.get('captions'))
            for (i, pth) in enumerate(as_list(im.get('paths'))):
                imgs.append((f'{img_base}/{pth}', caps[i] if i < len(caps) else ''))
    if imgs:
        B.append(('images', imgs))
    B += [('h2', '🪝 La première image, le hook'), ('p', str(b.get('hook') or ''))]
    if str(b.get('hook_texte') or '').strip():
        B.append(('callout', "Le hook textuel — en haut de l'écran, pendant les 3 à 5 premières secondes", [f"« {b['hook_texte']} »", "Gros, contrasté, deux lignes au plus, au-dessus du visage ; il dit l'accroche à ceux qui regardent sans le son."]))
    cm = b.get('commentaire') if isinstance(b.get('commentaire'), dict) else None
    if cm is not None:
        B += [('h2', "💬 Le commentaire à l'écran"), ('p', f"« {cm.get('texte')} »" + (f" — {cm['pseudo']}" if cm.get('pseudo') else '') + (f" (commentaire réel, {cm['source']})" if cm.get('source') else '') if cm.get('texte') else 'À choisir parmi les vrais commentaires (library/voice), mot pour mot.'), ('p', COMMENT_TOOL)]
    for h in as_list(b.get('hooks_b')):
        if isinstance(h, dict) and (h.get('said') or h.get('written')):
            B.append(('callout', f"Accroche {h.get('letter') or 'B'} à tester" + (f" (reprise de {h['from']})" if h.get('from') else ''), [f"On entend : « {h.get('said')} »" if h.get('said') else '', f"On lit : « {h.get('written')} »" if h.get('written') else '', f"On voit : {h.get('shown')}" if h.get('shown') else '']))
    cl = casting_lines(b)
    if cl:
        B += [('h2', '🎭 Qui joue, où, avec quoi'), ('ul', cl)]
    if as_list(b.get('deroule')):
        B += [('h2', '🏞️ Le déroulé, plan par plan'), ('ul', [str(x) for x in as_list(b.get('deroule'))])]
    sc = b.get('script') if isinstance(b.get('script'), dict) else {}
    B.append(('h2', '📝 Le script, mot pour mot'))
    if sc.get('intro'):
        B.append(('p', str(sc['intro'])))
    B.append(('table', ['Bloc', 'Temps', 'Mot pour mot dans la référence', 'Ton script', "À l'écran"], [[x if i != 3 or not is_cut(x) else '*(coupé)*' for (i, x) in enumerate(r)] for r in rows_of(b)]))
    if as_list(b.get('changes')):
        B += [('h2', "✂️ Ce qu'on a changé, et pourquoi"), ('ul', [str(x) for x in as_list(b.get('changes'))])]
    vl = voice_lines(b)
    if str(b.get('son') or '').strip() or vl:
        B += [('h2', '🎧 Le son et le rythme')] + ([('p', str(b['son']))] if str(b.get('son') or '').strip() else []) + ([('ul', vl)] if vl else [])
    B += [('h2', '🛠️ Comment produire, étape par étape'), ('ol', [str(x) for x in as_list(b.get('prod'))])]
    vx = b.get('voix') if isinstance(b.get('voix'), dict) else {}
    if str(b.get('profil_vocal') or '').strip() and (not fold(vx.get('voix_ia')).startswith('aucun')):
        B += [('h2', '🎙️ Le profil vocal (à coller dans ElevenLabs → Voice Design)'), ('code', str(b['profil_vocal']))]
    route = (b.get('production') or {}).get('route') if isinstance(b.get('production'), dict) else None
    fiche_type = str((b.get('fiche') or {}).get('Format') or '') if isinstance(b.get('fiche'), dict) else ''
    if route == 'ai' and (not fiche_type):
        B += [('h2', '🔁 Si tu manques de crédits IA : la route montage'), ('p', "La même vidéo, sans générer chaque plan : une voix off posée sur des clips. Les mots et l'ordre restent ceux du script ci-dessus."), ('ol', kinded(PROD['edit'], ws_of(P))), ('p', 'Le guide de montage complet (les clips plan par plan, les plans à générer) se demande à Claude : « fais-moi le guide de montage de ' + str(b.get('code')) + ' » (briefs.py montage).')]
    if as_list(b.get('erreurs')):
        B += [('h2', '⚠️ Les erreurs à éviter'), ('ul', [str(x) for x in as_list(b.get('erreurs'))])]
    B += [('h2', '✅ La checklist avant de publier'), ('check', [str(x) for x in as_list(b.get('checklist'))])]
    pr = b.get('production') if isinstance(b.get('production'), dict) else {}
    if pr.get('owner') or pr.get('due'):
        B.append(('p', f"*Produite par {pr.get('owner') or '?'}, pour le {pr.get('due') or '?'} · fichier à nommer « {b.get('code')} V1 A »*"))
    return B

def casting_lines(b):
    c = b.get('casting') if isinstance(b.get('casting'), dict) else {}
    labels = (('qui', "À l'écran"), ('ou', 'Où'), ('produit', 'Le produit en main'), ('accessoires', 'Les accessoires'))
    return [f'**{lab}** : {c.get(k)}' for (k, lab) in labels if str(c.get(k) or '').strip()]

def voice_lines(b):
    if isinstance(b.get('voix'), str) and b['voix'].strip():
        return [f"**Voix** : {b['voix'].strip()}"]
    v = b.get('voix') if isinstance(b.get('voix'), dict) else {}
    labels = (('langue', 'Langue ou parler'), ('genre', 'Voix'), ('ton', 'Ton'), ('voix_ia', 'Voix IA'))
    return [f'**{lab}** : {v.get(k)}' for (k, lab) in labels if str(v.get(k) or '').strip()]

def md_cell(s):
    return str(s or '').replace('|', '\\|').replace('\n', '<br>')

def to_md(B):
    L = []
    for blk in B:
        k = blk[0]
        if k == 'h1':
            L += [f'# {blk[1]}', '']
        elif k == 'h2':
            L += [f'## {blk[1]}', '']
        elif k == 'p':
            L += [blk[1], ''] if blk[1] else []
        elif k == 'fiche':
            L += [f'**{a}** : {v}  ' for (a, v) in blk[1]] + ['']
        elif k in ('ul', 'check', 'ol'):
            mark = {'ul': '- ', 'check': '- [ ] ', 'ol': '1. '}[k]
            L += [mark + str(x) for x in blk[1] if str(x).strip()] + ['']
        elif k == 'table':
            L += ['| ' + ' | '.join(blk[1]) + ' |', '|' + '---|' * len(blk[1])]
            L += ['| ' + ' | '.join((md_cell(c) for c in r)) + ' |' for r in blk[2]] + ['']
        elif k == 'images':
            L += [f'![{cap}]({p})' if p else f'*{cap}*' for (p, cap) in blk[1]] + ['']
        elif k == 'callout':
            L += [f'> **{blk[1]}**'] + [f'> {x}  ' for x in blk[2] if x] + ['']
        elif k == 'code':
            L += ['```', blk[1], '```', '']
    return '\n'.join(L)

def h_inline(s):
    s = html.escape(str(s or ''))
    s = re.sub('\\*\\*(.+?)\\*\\*', '<b class="red">\\1</b>', s, flags=re.S)
    s = re.sub('(?<!\\*)\\*(?!\\s)(.+?)(?<!\\s)\\*(?!\\*)', '<i>\\1</i>', s)
    s = re.sub('\\[([^\\]]+)\\]\\((https?://[^)\\s]+)\\)', '<a href="\\2">\\1</a>', s)
    return s.replace('\n', '<br>')

def to_html(B):
    H = ['<section class="brief">']
    for blk in B:
        k = blk[0]
        if k == 'h1':
            H.append(f'<h1>{h_inline(blk[1])}</h1>')
        elif k == 'h2':
            H.append(f'<h2>{h_inline(blk[1])}</h2>')
        elif k == 'p' and blk[1]:
            H.append(f'<p>{h_inline(blk[1])}</p>')
        elif k == 'fiche':
            H.append('<div class="fiche">' + ''.join((f'<div><b>{h_inline(a)}</b> : {h_inline(v)}</div>' for (a, v) in blk[1])) + '</div>')
        elif k in ('ul', 'ol', 'check'):
            tag = 'ol' if k == 'ol' else 'ul'
            cls = ' class="check"' if k == 'check' else ''
            H.append(f'<{tag}{cls}>' + ''.join((f'<li>{h_inline(x)}</li>' for x in blk[1] if str(x).strip())) + f'</{tag}>')
        elif k == 'table':
            H.append('<table><tr>' + ''.join((f'<th>{h_inline(h)}</th>' for h in blk[1])) + '</tr>' + ''.join(('<tr>' + ''.join((f'<td>{h_inline(c)}</td>' for c in r)) + '</tr>' for r in blk[2])) + '</table>')
        elif k == 'images':
            H.append('<div class="imgs">' + ''.join((f'<figure><img src="{html.escape(p)}" alt=""><figcaption>{h_inline(cap)}</figcaption></figure>' if p else f'<p class="cap">{h_inline(cap)}</p>' for (p, cap) in blk[1])) + '</div>')
        elif k == 'callout':
            H.append(f'<div class="callout"><b>{h_inline(blk[1])}</b>' + ''.join((f'<div>{h_inline(x)}</div>' for x in blk[2] if x)) + '</div>')
        elif k == 'code':
            H.append(f'<pre class="code">{html.escape(str(blk[1]))}</pre>')
    H.append(f"<footer>{html.escape(DOC_TEXT['fr']['signature'])}</footer></section>")
    return '\n'.join(H)
CSS = '\nbody{font-family:Arial,Helvetica,sans-serif;color:#1d1d1f;background:#fff;margin:0;padding:16px;font-size:13px;line-height:1.45}\n.brief{max-width:190mm;margin:0 auto 24px}\nh1{font-size:20px;border-bottom:3px solid #17324D;padding-bottom:6px}\nh2{font-size:15px;margin:16px 0 6px;color:#17324D}\n.fiche{background:#f3f4f7;border-left:4px solid #12A27A;padding:8px 12px}\ntable{border-collapse:collapse;width:100%;margin:6px 0}\nth,td{border:1px solid #c9ccd3;padding:4px 6px;vertical-align:top;text-align:left}\nth{background:#17324D;color:#fff}\n.red{color:#c0161d}\n.imgs{display:flex;flex-wrap:wrap;gap:8px}\nfigure{margin:0;width:110px}\nfigure img{width:110px;height:auto;border:1px solid #ccc}\nfigcaption,.cap{font-size:11px;color:#555}\n.callout{background:#eef8f4;border:1px solid #12A27A;padding:8px 12px;margin:8px 0}\nul.check{list-style:none;padding-left:4px}\npre.code{background:#f2f5f7;border:1px solid #c9ccd3;padding:8px 10px;white-space:pre-wrap;font-size:12px}\nfooter{font-size:11px;color:#6b7280;margin-top:10px}\nul.check li:before{content:"☐  "}\n@media print{body{padding:0}.brief{page-break-after:always}}\n'

def cmd_kit(a):
    (P, ws, state) = open_ws(a.folder)
    F = files(P, state)
    (st, cr) = creatives_of(P, state, [a.code])
    c = cr[0]
    if not brief_path(F, c['code']).exists():
        raise WsError(f"pas encore de brief {c['code']} : briefs.py init <dossier> {c['code']}")
    b = load_brief(F, c['code'])
    refs = S.refs_index(P)
    kit = F['dir'] / f"{c['code']}-kit"
    if kit.exists():
        shutil.rmtree(kit)
    (kit / 'references').mkdir(parents=True)
    (copied, absent) = ([], [])
    codes = [str(r[0]) for r in as_list(b.get('refs')) if isinstance(r, list) and r]
    for code in dict.fromkeys(codes + [str(x) for x in as_list(c.get('built_on'))]):
        r = refs.get(code) or {}
        for k in ('file', 'transcript'):
            if r.get(k):
                src = P['refs_dir'] / str(r[k])
                if src.exists():
                    shutil.copy(src, kit / 'references' / src.name)
                    copied.append(src.name)
                else:
                    absent.append(str(r[k]))
        for f in frame_files(P, code):
            (kit / 'Frames').mkdir(exist_ok=True)
            shutil.copy(f, kit / 'Frames' / f.name)
    imgs = [str(p) for v in as_list(b.get('visuels')) if isinstance(v, dict) and isinstance(v.get('images'), dict) for p in as_list(v['images'].get('paths'))]
    for p in imgs:
        src = P['refs_dir'] / p
        if src.exists():
            (kit / Path(p).parent).mkdir(parents=True, exist_ok=True)
            shutil.copy(src, kit / p)
    (kit / f"{c['code']}.md").write_text(to_md(blocks_of(P, b, '.')), encoding='utf-8')
    (kit / f"{c['code']}.html").write_text(f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{c['code']}</title><style>{CSS}</style></head><body>{to_html(blocks_of(P, b, '.'))}</body></html>""", encoding='utf-8')
    (kit / 'LISEZ-MOI.txt').write_text(f"{c['code']} · {b.get('title')}\n\nOuvre {c['code']}.html (ou .md) : tout est dedans. Les vidéos de référence sont dans references/, les images clés dans Frames/.\nLe fichier fini se nomme « {c['code']} V1 A » (.mp4 pour une vidéo, .jpg pour une image).\n", encoding='utf-8')
    out = kit
    if a.zip:
        out = Path(shutil.make_archive(str(kit), 'zip', kit))
    journal(P, f"Kit du monteur : {c['code']} ({len(copied)} fichier(s))")
    print(f'Écrit : {out} · {len(copied)} fichier(s) de référence' + (f" ; absents : {', '.join(absent)}" if absent else ''))

def ledger(F):
    data = load_yaml(F['ads'], {}) or {}
    if not isinstance(data, dict) or not data.get('ads'):
        raise WsError('le registre des pubs est vide : lance « strategy.py ledger <dossier> »')
    return data

def split_code(code, variation=None, letter=None):
    """« C01 », « C01 V2 », « C01 V1 B » -> (C01, 2, B); flags fill what the code leaves out."""
    m = re.fullmatch('\\s*(C\\d+)(?:\\s+V(\\d+))?(?:\\s+([A-Za-z]))?\\s*', str(code), re.I)
    if not m:
        raise WsError(f'code « {code} » : écris C01, ou le code entier "C01 V1 A"')
    return (m.group(1).upper(), int(m.group(2) or variation or 1), (m.group(3) or letter or 'A').upper())

def row_of(data, code):
    (c, v, l_) = split_code(code)
    want = f'{c} V{v} {l_}'
    r = next((x for x in data['ads'] if isinstance(x, dict) and str(x.get('code')).upper() == want), None)
    if r is None:
        raise WsError(f"« {want} » n'est pas dans le registre (cycles/…/ads.yaml)")
    return r

def iso(d):
    return bool(re.fullmatch('\\d{4}-\\d{2}-\\d{2}', str(d or '')))

def cmd_assign(a):
    (P, ws, state) = open_ws(a.folder)
    F = files(P, state)
    data = ledger(F)
    if a.due and (not iso(a.due)):
        raise WsError(f'date « {a.due} » : écris-la AAAA-MM-JJ (2026-11-02)')
    (done, draft) = ([], [])
    for code in a.codes:
        r = row_of(data, code)
        r['owner'] = a.owner
        if a.due:
            r['due'] = a.due
        if a.start and str(r.get('status') or 'brief').lower() in ('brief', ''):
            r['status'] = 'production'
        idea = r['code'].split()[0]
        bp = brief_path(F, idea)
        if bp.exists():
            b = load_brief(F, idea)
            if not is_ready(b):
                draft.append(idea)
            if not isinstance(b.get('production'), dict):
                b['production'] = {}
            b['production'].update({'owner': a.owner, **({'due': a.due} if a.due else {})})
            dump_yaml(bp, b)
        else:
            draft.append(idea)
        done.append(r['code'])
    dump_yaml(F['ads'], data)
    journal(P, f"Production : {', '.join(done)} pour {a.owner}" + (f', le {a.due}' if a.due else ''))
    W.set_step(P, state, 'production', 'doing')
    refresh(P, ws, state)
    print(f'{len(done)} créative(s) attribuée(s) à {a.owner}' + (f' pour le {a.due}' if a.due else ''))
    team = W.members(ws)
    if team and a.owner.lower() not in {x['name'].lower() for x in team}:
        print(f'''🟡 {a.owner} n'est pas dans l'équipe du dossier (ws.py team <dossier> add "{a.owner}" --role editor)''')
    if draft:
        print(f"🟡 brief pas encore « ready » : {', '.join(dict.fromkeys(draft))} : la personne produira sur un brouillon")

def cmd_deliver(a):
    (P, ws, state) = open_ws(a.folder)
    F = files(P, state)
    data = ledger(F)
    src = Path(a.file)
    if not src.exists():
        raise WsError(f'fichier introuvable : {src}')
    (idea, var, let) = split_code(a.code, a.variation, a.letter)
    code = f'{idea} V{var} {let}'
    r = next((x for x in data['ads'] if isinstance(x, dict) and str(x.get('code')).upper() == code), None)
    if r is None:
        base = row_of(data, idea)
        parent = f'{idea} V{var} A' if let != 'A' else base['code']
        if not any((str(x.get('code')).upper() == parent for x in data['ads'] if isinstance(x, dict))):
            parent = base['code']
        change = a.change or (f'ouverture {let}' if let != 'A' else '')
        if var != 1 and let == 'A' and (not a.change):
            raise WsError(f"""une variation dit ce qu'elle change : --change "plan d'ouverture : la pharmacie" ({code})""")
        r = {**{k: v for (k, v) in base.items() if k not in ('results', 'review', 'platform_ad_id', 'launched_on', 'file')}, 'code': code, 'parent': parent, 'change': change, 'status': 'production', 'review': {}, 'results': {}, 'platform_ad_id': '', 'launched_on': ''}
        data['ads'].append(r)
    elif a.change:
        r['change'] = a.change
    F['creatives'].mkdir(parents=True, exist_ok=True)
    dest = F['creatives'] / f'{code}{src.suffix.lower()}'
    if src.resolve() != dest.resolve():
        shutil.copy(src, dest)
    r['file'] = f'creatives/{dest.name}'
    r['status'] = 'review'
    r['delivered_on'] = today()
    if isinstance(r.get('review'), dict) and r['review'].get('verdict'):
        r['review'] = {'previous': {k: v for (k, v) in r['review'].items() if k in ('verdict', 'fixes', 'on')}}
    dump_yaml(F['ads'], data)
    journal(P, f'Livrée : {code} ({dest.name})')
    originals = [x for x in data['ads'] if isinstance(x, dict) and re.match('C\\d+ V1 A$', str(x.get('code') or ''))]
    if originals and all((x.get('file') for x in originals)):
        W.set_step(P, state, 'production', 'done', outputs=['cycles/…/creatives'])
    refresh(P, ws, state)
    print(f"{code} → {dest.relative_to(P['root'])}, statut « review » : le contrôle qualité ensuite (cs-review)")

def build_parser():
    ap = W.FrParser(prog='briefs.py', description='Les briefs et la production.')
    sub = ap.add_subparsers(dest='cmd', required=True, parser_class=W.FrParser)
    p = sub.add_parser('init')
    p.add_argument('folder')
    p.add_argument('codes', nargs='*')
    p.add_argument('--route', choices=sorted(ROUTES))
    p.add_argument('--force', action='store_true')
    for name in ('check', 'render', 'montage'):
        p = sub.add_parser(name)
        p.add_argument('folder')
        p.add_argument('codes', nargs='*')
        if name == 'render':
            p.add_argument('--ready', action='store_true', help='seulement les briefs finis (status: ready) dans BRIEFS.md, BRIEFS.html et le document')
    p = sub.add_parser('opening')
    p.add_argument('folder')
    p.add_argument('codes', nargs='*')
    p.add_argument('--write', action='store_true', help='récrire le brief et la stratégie (sinon, seulement la liste)')
    p = sub.add_parser('fill')
    p.add_argument('folder')
    p.add_argument('file')
    p.add_argument('--force', action='store_true', help='récrire aussi les briefs déjà prêts')
    p = sub.add_parser('kit')
    p.add_argument('folder')
    p.add_argument('code')
    p.add_argument('--zip', action='store_true')
    for name in ('export', 'board'):
        p = sub.add_parser(name)
        p.add_argument('folder')
    p = sub.add_parser('assign')
    p.add_argument('folder')
    p.add_argument('codes', nargs='+')
    p.add_argument('--owner', required=True)
    p.add_argument('--due')
    p.add_argument('--start', action='store_true', help='passer les créatives au statut « production »')
    p = sub.add_parser('deliver')
    p.add_argument('folder')
    p.add_argument('code')
    p.add_argument('file')
    p.add_argument('--letter', help="l'ouverture : A (celle du brief), B, C…")
    p.add_argument('--variation', type=int, help="la variation : 1 pour l'originale")
    p.add_argument('--change', help='ce que la variation change (le registre le garde)')
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
    cmds = {'kit': cmd_kit, 'assign': cmd_assign, 'deliver': cmd_deliver}
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
