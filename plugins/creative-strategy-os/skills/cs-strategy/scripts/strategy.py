"""strategy.py : this command runs on the Creative Strategy OS licence server.

Only the helpers other scripts of the plugin borrow are here (as_int, as_list, cycle_dir, fold, load_strategy, num, paths, refs_index, written_creatives)."""
import sys
from pathlib import Path
import sys
import unicodedata
from pathlib import Path
HERE = Path(__file__).resolve().parent
SUITE = HERE.parent.parent / 'creative-strategist' / 'scripts'
if not (SUITE / 'ws.py').exists():
    print(f'ERREUR : le skill creative-strategist doit être installé à côté de cs-strategy (attendu : {SUITE}).', file=sys.stderr)
    sys.exit(2)
sys.path.insert(0, str(SUITE))
import kinds as K
import numparse
from ws import WsError, open_ws, load_yaml, dump_yaml, journal, refresh, today, read_text

def fold(s):
    s = str(s or '').lower().replace('’', "'").replace('œ', 'oe').replace('æ', 'ae')
    s = unicodedata.normalize('NFKD', s)
    return ''.join((ch for ch in s if not unicodedata.combining(ch)))

def num(v):
    return numparse.parse(v) if v not in (None, '') else None

def cycle_dir(P, state):
    return P['root'] / 'cycles' / f"cycle-{state['cycle']:02d}"

def paths(P, state):
    c = cycle_dir(P, state)
    return {'avatars': P['root'] / 'library' / 'avatars.yaml', 'strategy': c / 'strategy.yaml', 'inputs': c / 'strategy-inputs.md', 'ads': c / 'ads.yaml', 'report': P['root'] / 'deliverables' / 'STRATEGIE.md'}

def load_strategy(F):
    if not F['strategy'].exists():
        raise WsError(f"pas encore de {F['strategy'].parent.name}/strategy.yaml : lance « strategy.py init <dossier> »")
    data = load_yaml(F['strategy'], {}) or {}
    if not isinstance(data, dict) or not isinstance(data.get('creatives', []), list):
        raise WsError('strategy.yaml : il faut « creatives: [...] » (voir strategy.py init)')
    return data

def written_creatives(st):
    """The creatives with a title, each given a code when it lacks one (C?? + its title in messages)."""
    out = []
    for (i, c) in enumerate(st.get('creatives') or [], 1):
        if isinstance(c, dict) and str(c.get('title') or '').strip():
            c = dict(c)
            c['code'] = str(c.get('code') or f"C?? « {c['title'][:30]} »")
            out.append(c)
    return out
_PROOF = {'days': 30, 'ads': {}}
_ADS = {}

def advertiser_ads(P):
    """Ads per advertiser in the captures (library/candidates.yaml and the references). Gadzhi's ads were 14 to 19
    days old, but he ran 540 of them on the same openings: young ads by the dozen are a budget that pays (01/11/2026)."""
    files = [P['root'] / 'library' / 'candidates.yaml', P['refs_index']]
    key = tuple(((str(f), f.stat().st_mtime) for f in files if f.exists()))
    if key not in _ADS:
        ids = {}
        for f in files:
            data = load_yaml(f, {}) if f.exists() else {}
            lst = data.get('candidates', data.get('references')) if isinstance(data, dict) else data
            for c in lst or []:
                if isinstance(c, dict) and c.get('platform') == 'adlib' and c.get('author'):
                    ids.setdefault(str(c['author']), set()).add(str(c.get('id') or c.get('code')))
        _ADS.clear()
        _ADS[key] = {a: len(v) for (a, v) in ids.items()}
    return _ADS[key]

def refs_index(P):
    data = load_yaml(P['refs_index'], {}) or {}
    refs = data.get('references') if isinstance(data, dict) else []
    ws = load_yaml(P['workspace'], {}) if P['workspace'].exists() else {}
    _PROOF.update(days=K.profile(ws if isinstance(ws, dict) else {})['proof_days'], ads=advertiser_ads(P))
    return {str(r.get('code')): r for r in refs or [] if isinstance(r, dict) and r.get('code')}

def as_list(v):
    if v in (None, ''):
        return []
    return v if isinstance(v, list) else [v]

def as_int(v):
    x = num(v)
    return int(x) if x is not None else None

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "creative-strategist" / "scripts"))
    import csos_client
    sys.exit(csos_client.forward(__file__, sys.argv[1:]))
