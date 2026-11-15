"""offer.py — the offer step of the creative-strategy suite: the market, the offer, the page, the ad text, the follow-up.

    python offer.py competitor <dossier> <adresse | sonde.json> [--name N] [--qty 2] [--market CI]
                               [--adlib adlib.json] [--ads ID,ID] [--code CO01]
    python offer.py compare    <dossier> [--fx XOF=14.3 ...] [--market GN]
    python offer.py init       <dossier>                    écrit library/offer.yaml à remplir
    python offer.py plan       <dossier>                    vérifie et chiffre l'offre proposée
    python offer.py simulate   <dossier> --offer 2:385000[:libellé] ... [--cpa 2.5]
    python offer.py lint       <dossier> <texte.md> [--offer proposed|current]
    python offer.py check      <dossier> [<id> <ok|warn|fail|todo|na> --evidence "…"]
    python offer.py report     <dossier> [--done]

Files (creative-strategist/references/workspace.md): library/competitors.yaml and library/competitors/CO##_<nom>/,
library/offer.yaml (the proposed offer and the page brief), deliverables/texte-pub.md, deliverables/messages.md,
deliverables/OFFRE.md, audit.yaml (checks, shared with the intake). Nothing is blocked.

Édition sous licence : seules les commandes page-paste tournent ici ; les autres partent sur le serveur de licence."""
import json
import os
import re
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
SUITE = HERE.parent.parent / 'creative-strategist' / 'scripts'
if not (SUITE / 'ws.py').exists():
    print(f'ERREUR : le skill creative-strategist doit être installé à côté de cs-offer (attendu : {SUITE}).', file=sys.stderr)
    sys.exit(2)
sys.path.insert(0, str(SUITE))
import ws as W
import economics as E
import pagefacts as PF
from audit import Audit, STATUSES, ICON, STATUS_FR
from ws import WsError, open_ws, load_yaml, dump_yaml, journal, refresh, today, read_text

def slug(s):
    s = re.sub('[^\\w]+', '-', PF.unescape_json_text(str(s or '')).lower(), flags=re.U).strip('-')
    return s[:40] or 'concurrent'

def cmd_page_paste(a):
    """Save the page copied by browser/page_grab.js (SAUVERPAGE): the clipboard is on the user's computer."""
    (P, ws, state) = open_ws(a.folder)
    import subprocess
    if sys.platform == 'win32':
        cmd = ['powershell', '-NoProfile', '-Command', '[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw']
    elif sys.platform == 'darwin':
        cmd = ['pbpaste']
    else:
        cmd = ['xclip', '-selection', 'clipboard', '-o']
    body = subprocess.run(cmd, capture_output=True).stdout.decode('utf-8', 'replace').replace('\r\n', '\n')
    if not body.startswith('# '):
        raise WsError('le presse-papier ne contient pas une page : lance browser/page_grab.js sur la page, clique sur SAUVERPAGE (un vrai clic), puis relance offer.py page-paste')
    name = slug(a.name or body.splitlines()[0][2:]) or 'page'
    out_dir = P['root'] / 'library' / 'competitors' / 'pages'
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f'{name}.md'
    dest.write_text(body, encoding='utf-8')
    journal(P, f"Page enregistrée depuis le navigateur : {dest.relative_to(P['root'])}")
    print(f"Page enregistrée : {dest.relative_to(P['root'])} ({len(body)} caractères). Suite : offer.py page write")

def build_parser():
    ap = W.FrParser(prog='offer.py', description="L'offre : le marché, l'offre, la page, le texte, la relance.")
    sub = ap.add_subparsers(dest='cmd', required=True, parser_class=W.FrParser)
    p = sub.add_parser('competitor', help="lire la page d'un concurrent")
    p.add_argument('folder')
    p.add_argument('source')
    p.add_argument('--name')
    p.add_argument('--qty', type=int, help='quand la page vend un lot comme un produit à part (2, 3…)')
    p.add_argument('--unit', help="ce qu'une unité contient : paire, pièce, 30 jours de cure… (pour comparer juste)")
    p.add_argument('--force', action='store_true', help='ajouter la page même si elle ne parle pas du produit')
    p.add_argument('--market')
    p.add_argument('--adlib', help='le JSON de browser/adlib_links.js')
    p.add_argument('--ads', help='identifiants de pubs de la Bibliothèque, séparés par des virgules')
    p.add_argument('--code')
    p = sub.add_parser('page', help="lire une page (grab), l'écrire comme un brief (write), la contrôler (check)")
    p.add_argument('action', choices=('grab', 'write', 'check'))
    p.add_argument('folder')
    p.add_argument('url', nargs='?')
    p.add_argument('--name', help='le nom du fichier (ex. frank-simo-atelier)')
    p.add_argument('--clipboard', action='store_true', help='enregistrer la page copiée par browser/page_grab.js')
    p.add_argument('--plan', help='A vente après un live · B vente froide · C inscription webinaire/défi · D produit COD')
    p.add_argument('--ref', help='la page de référence (library/competitors/pages/<nom>.md)')
    p.add_argument('--force', action='store_true')
    p = sub.add_parser('page-paste', help='enregistrer la page copiée par browser/page_grab.js (presse-papier)')
    p.add_argument('folder')
    p.add_argument('--name')
    p = sub.add_parser('compare', help="le marché face à l'offre du client")
    p.add_argument('folder')
    p.add_argument('--fx', nargs='+', metavar='DEVISE=taux')
    p.add_argument('--market')
    p = sub.add_parser('init', help='écrire library/offer.yaml à remplir')
    p.add_argument('folder')
    p = sub.add_parser('plan', help="vérifier et chiffrer l'offre proposée")
    p.add_argument('folder')
    p = sub.add_parser('simulate', help='comparer des offres (prix, lots)')
    p.add_argument('folder')
    p.add_argument('--offer', nargs='+', action='extend', metavar='qté:prix[:libellé]')
    p.add_argument('--set', nargs='+', metavar='clé=valeur', help='change un taux pour les offres testées, ex. confirmation_rate=0.8')
    p.add_argument('--cpa', type=float, help='coût par achat actuel, devise du compte pub')
    p.add_argument('--market')
    p = sub.add_parser('lint', help='vérifier un texte de pub')
    p.add_argument('folder')
    p.add_argument('file')
    p.add_argument('--offer', choices=('proposed', 'current'))
    p.add_argument('--channel', choices=('meta', 'tiktok'), default='meta')
    p = sub.add_parser('check', help='lister les contrôles, ou en noter un')
    p.add_argument('folder')
    p.add_argument('id', nargs='?')
    p.add_argument('status', nargs='?', choices=STATUSES)
    p.add_argument('--evidence', default='')
    p = sub.add_parser('report', help='écrire deliverables/OFFRE.md')
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
    cmds = {'page-paste': cmd_page_paste}
    try:
        cmds.get(a.cmd, _forward)(a)
    except WsError as e:
        print(f'ERREUR : {e}', file=sys.stderr)
        sys.exit(2)
    except E.EcoError as e:
        print(f'ERREUR : {e}', file=sys.stderr)
        sys.exit(2)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f'ERREUR : fichier JSON illisible ({e.__class__.__name__}) : refais la sonde et enregistre son résultat tel quel.', file=sys.stderr)
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
