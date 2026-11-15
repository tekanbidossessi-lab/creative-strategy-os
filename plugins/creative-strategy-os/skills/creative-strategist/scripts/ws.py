# -*- coding: utf-8 -*-
"""ws.py — the product workspace of the creative-strategy suite.

    python ws.py init   <dossier> --name "Genouillère en bambou" [--mode free|hybrid|paid] [--stage new|established]
                        [--programme none|accelerateur] [--kind product|digital|webinar] [--path full|stage]
                        [--market GN:Guinée:GNF:fr:cod ...] [--channels meta,tiktok]
                        [--shop URL] [--business NOM] [--goal TEXTE] [--budget "15 USD"] [--team TEXTE]
    python ws.py adopt  <dossier client existant> --name ...   (mêmes options ; ne déplace rien, déduit les étapes faites)
    python ws.py status <dossier>        où on en est (réécrit aussi COMMENCE-ICI.md)
    python ws.py next   <dossier>        la prochaine action seulement
    python ws.py start  <dossier> <étape> --reason "..."   commencer ailleurs (les étapes d'avant passent en « sautée »)
    python ws.py step   <dossier> <étape> <todo|doing|done|skipped> [--output CHEMIN ...] [--note TEXTE]
    python ws.py cycle  <dossier> [--from briefs|strategy|research]   ouvrir le cycle de test suivant
    python ws.py code   <dossier> <AL|TT|IG|YT|CL|CO|C>   réserver le prochain code libre (CO = concurrent)
    python ws.py log    <dossier> "texte"   ajouter une ligne datée au journal
    python ws.py set    <dossier> clé=valeur   mode, stage, programme, kind, path, channels, goal, budget_daily, team,
                                               capacity.machine, capacity.claude, accounts.*, brand.*, engines.<tâche>
    python ws.py overview [<dossier racine>]   tous les produits du dossier : où chacun en est, quoi faire aujourd'hui
    python ws.py bilan  <dossier>        l'historique du produit, cycle par cycle (deliverables/BILAN.md)
    python ws.py check  <dossier>        vérifier les fichiers (code 1 s'il y a une erreur)
    python ws.py repair <dossier>        reconstruire state.yaml (compteurs depuis les fichiers, étapes connues)
    python ws.py doctor [<dossier>] [--mode M] [--live]   cet ordinateur est-il prêt pour la formule ?

Beyond the standard library only PyYAML is needed (doctor works without it and lists what to install).
"""
import argparse
import datetime as dt
import importlib.util
import json
import os
import platform
import re
import shutil
import sys
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    import yaml
except ImportError:
    yaml = None

HERE = Path(__file__).resolve().parent
FORMAT = 1
MODES = ("free", "hybrid", "paid")
STAGES = ("new", "established")
PROGRAMMES = ("none", "accelerateur")
from kinds import KINDS  # noqa: E402  (product, webinar: what the project sells)
STATUSES = ("todo", "doing", "done", "skipped")
STATUS_FR = {"todo": "à faire", "doing": "en cours", "done": "faite", "skipped": "sautée"}
REF_PREFIXES = ("AL", "TT", "IG", "YT", "CL")
CODE_PREFIXES = REF_PREFIXES + ("CO", "C")
CYCLE_FROM = ("research", "strategy", "briefs")
AD_STATUSES = ("brief", "production", "review", "ready", "live", "paused", "killed", "winner")
REF_SUBDIRS = ("AdLibrary", "TikTok", "Instagram", "Transcripts", "Analyses", "Frames")
WIN = os.name == "nt"
PY = "python" if WIN else "python3"


class WsError(Exception):
    """An error the user can fix; printed as one French line, never as a traceback."""


# ---------------------------------------------------------------- files

def need_yaml():
    if yaml is None:
        raise WsError(f"PyYAML manque. Installe-le : {PY} -m pip install pyyaml")


def read_text(p):
    raw = Path(p).read_bytes()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


def load_yaml(p, default=None):
    p = Path(p)
    if not p.exists():
        return default
    text = read_text(p)
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        mark = getattr(e, "problem_mark", None)
        where = f", ligne {mark.line + 1}" if mark else ""
        hint = " (tabulation interdite en YAML : utilise des espaces)" if "\t" in text else ""
        raise WsError(f"{p.name}{where} : le fichier n'est pas un YAML valide{hint}. Corrige-le ou restaure "
                      f"{p.name}.bak s'il existe.")
    return default if data is None else data


def dump_yaml(p, data):
    p = Path(p)
    try:
        if p.exists():
            shutil.copy2(p, p.with_name(p.name + ".bak"))
        tmp = p.with_name(p.name + ".tmp")
        with open(tmp, "w", encoding="utf-8", newline="\n") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=110)
        os.replace(tmp, p)
    except PermissionError:
        raise WsError(f"{p.name} est verrouillé (ouvert dans un autre programme, OneDrive ou un antivirus). "
                      "Ferme-le et relance la commande.")


def today():
    return dt.date.today().isoformat()


def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


_MODES = None


def modes_data():
    global _MODES
    need_yaml()
    if _MODES is None:
        _MODES = load_yaml(HERE / "modes.yaml")
        if not isinstance(_MODES, dict):
            raise WsError("modes.yaml est illisible : réinstalle le skill creative-strategist.")
    return _MODES


def step_ids():
    return [s["id"] for s in modes_data()["steps"]]


def step_label(sid):
    for s in modes_data()["steps"]:
        if s["id"] == sid:
            return s.get("label", sid)
    return sid


def paths_of(root, ws=None):
    root = Path(root).expanduser().resolve()
    ws = ws or {}
    custom = (ws.get("paths") or {}) if isinstance(ws, dict) else {}
    return {"root": root, "workspace": root / "workspace.yaml", "product": root / "product.yaml",
            "state": root / "state.yaml", "journal": root / "journal.md", "start": root / "COMMENCE-ICI.md",
            "refs_index": root / "library" / "references.yaml",
            "refs_dir": root / custom.get("references", "References"),
            "plan": (root / custom["plan"]) if custom.get("plan") else None}


def new_state():
    return {"cycle": 1, "counters": {k: 0 for k in CODE_PREFIXES},
            "steps": {s: {"status": "todo"} for s in step_ids()}, "effective_engines": {}, "next": ""}


def as_int(v, what):
    try:
        return int(v)
    except (TypeError, ValueError):
        raise WsError(f"state.yaml : {what} vaut « {v} », il faut un nombre. Lance : ws.py repair <dossier>")


def normalise_state(state):
    if not isinstance(state, dict):
        raise WsError("state.yaml n'a pas la bonne forme. Lance : ws.py repair <dossier>")
    if not isinstance(state.get("steps"), dict):
        raise WsError("state.yaml n'a plus la liste des étapes. Lance : ws.py repair <dossier>")
    state["cycle"] = as_int(state.get("cycle", 1), "cycle")
    counters = state.get("counters") if isinstance(state.get("counters"), dict) else {}
    state["counters"] = {k: as_int(counters.get(k, 0), f"counters.{k}") for k in CODE_PREFIXES}
    for s in step_ids():
        info = state["steps"].get(s)
        if not isinstance(info, dict):
            state["steps"][s] = {"status": "todo"}
    if not isinstance(state.get("effective_engines"), dict):
        state["effective_engines"] = {}
    return state


def open_ws(folder):
    need_yaml()
    P = paths_of(folder)
    if not P["workspace"].exists():
        raise WsError(f"pas de workspace.yaml dans {P['root']}. Crée-le avec : ws.py init \"{P['root']}\" --name …")
    ws = load_yaml(P["workspace"], {})
    if not isinstance(ws, dict):
        raise WsError("workspace.yaml n'a pas la bonne forme (il faut des « clé: valeur »). Restaure workspace.yaml.bak.")
    P = paths_of(folder, ws)
    if not P["state"].exists() or not read_text(P["state"]).strip():
        raise WsError("state.yaml est absent ou vide. Lance : ws.py repair <dossier> (les compteurs sont "
                      "recalculés depuis les fichiers).")
    state = normalise_state(load_yaml(P["state"]))
    return P, ws, state


def journal(P, text):
    new = not P["journal"].exists()
    try:
        with open(P["journal"], "a", encoding="utf-8", newline="\n") as f:
            if new:
                f.write("# Journal\n\nChaque décision et chaque consigne, datée. On ajoute, on n'efface jamais.\n\n")
            who = os.environ.get("CS_USER", "").strip()
            f.write(f"- {now()} — " + (f"[{who}] " if who else "") + f"{text}\n")
    except PermissionError:
        raise WsError("journal.md est verrouillé (ouvert ailleurs, OneDrive, antivirus). Ferme-le et relance.")


ROLES = {"strategist": "stratège", "editor": "monteur", "creator": "créateur de contenu", "buyer": "media buyer",
         "owner": "propriétaire", "closer": "appels et WhatsApp"}


def members(ws):
    m = ws.get("members")
    return [x for x in m if isinstance(x, dict) and x.get("name")] if isinstance(m, list) else []


def cmd_team(a):
    P, ws, state = open_ws(a.folder)
    team = members(ws)
    if a.action == "add":
        if not a.name:
            raise WsError("donne le nom : ws.py team <dossier> add \"Awa\" --role editor")
        if a.role and a.role not in ROLES:
            raise WsError(f"rôle « {a.role} » : {', '.join(f'{k} ({v})' for k, v in ROLES.items())}")
        team = [x for x in team if x["name"].lower() != a.name.lower()]
        team.append({"name": a.name, "role": a.role or "", "contact": a.contact or ""})
        ws["members"] = team
        dump_yaml(P["workspace"], ws)
        journal(P, f"Équipe : {a.name}" + (f" ({ROLES[a.role]})" if a.role else "") + " ajouté(e)")
    elif a.action == "remove":
        left = [x for x in team if x["name"].lower() != str(a.name or "").lower()]
        if len(left) == len(team):
            raise WsError(f"« {a.name} » n'est pas dans l'équipe")
        ws["members"] = left
        dump_yaml(P["workspace"], ws)
        journal(P, f"Équipe : {a.name} retiré(e)")
        team = left
    if not team:
        print("Pas encore d'équipe : ws.py team <dossier> add \"Awa\" --role editor --contact \"+229…\"")
        return
    print(f"L'équipe de {ws.get('name')} :")
    for x in team:
        print(f"  · {x['name']}" + (f" — {ROLES.get(x.get('role'), x.get('role'))}" if x.get("role") else "")
              + (f" — {x['contact']}" if x.get("contact") else ""))
    print("Chacun écrit son nom dans le journal : CS_USER=Awa (variable d'environnement) avant de lancer un skill.")


def parse_market(s):
    parts = (s.split(":") + ["", "", "", "", ""])[:5]
    code, country, currency, lang, pay = [p.strip() for p in parts]
    if not re.fullmatch(r"[A-Z]{2}", code or ""):
        raise WsError(f"marché « {s} » : le code pays doit faire deux lettres majuscules (ex. GN:Guinée:GNF:fr:cod)")
    # mobile: Orange Money, Wave, MTN MoMo — how a training or a service is paid in West Africa (01/11/2026)
    if pay and pay not in ("cod", "online", "both", "mobile"):
        raise WsError(f"marché « {s} » : paiement « {pay} » inconnu (cod, online, both, mobile)")
    return {"code": code, "country": country, "currency": currency, "language": lang or "fr", "payment": pay or "cod"}


# ---------------------------------------------------------------- codes

CODE_IN_NAME = re.compile(r"^(AL|TT|IG|YT|CL|CO)(\d{1,4})(?=[_.\- ]|$)", re.I)


def scan_codes(P, ws):
    """Highest number already used per prefix, from files and indexes (so a code is never reused)."""
    top = {k: 0 for k in CODE_PREFIXES}
    roots = [P["refs_dir"], P["root"] / "library"]
    for r in roots:
        if r.exists():
            for f in r.rglob("*"):
                m = CODE_IN_NAME.match(f.name)
                if m:
                    pre = m.group(1).upper()
                    top[pre] = max(top[pre], int(m.group(2)))
    refs = (load_yaml(P["refs_index"], {}) or {}) if P["refs_index"].exists() else {}
    for r in (refs.get("references") or []) if isinstance(refs, dict) else []:
        m = re.fullmatch(r"(AL|TT|IG|YT|CL)(\d+)", str((r or {}).get("code", "")) if isinstance(r, dict) else "")
        if m:
            top[m.group(1)] = max(top[m.group(1)], int(m.group(2)))
    comp = P["root"] / "library" / "competitors.yaml"
    data = (load_yaml(comp, {}) or {}) if comp.exists() else {}
    for c in (data.get("competitors") or []) if isinstance(data, dict) else []:
        m = re.fullmatch(r"CO(\d+)", str((c or {}).get("code", "")) if isinstance(c, dict) else "")
        if m:
            top["CO"] = max(top["CO"], int(m.group(1)))
    cyc = P["root"] / "cycles"
    for f in list(cyc.glob("*/ads.yaml")) + list(cyc.glob("*/plan.yaml")) + list(cyc.glob("*/strategy.yaml")):
        for m in re.finditer(r"\bC(\d{2,4})\b", read_text(f)):
            top["C"] = max(top["C"], int(m.group(1)))
    if P["plan"] and P["plan"].exists():  # legacy plans number creatives with "n:"
        text = read_text(P["plan"])
        block = text.split("\ncreatives:", 1)[1] if "\ncreatives:" in text else ""
        for m in re.finditer(r"^- n:\s*(\d+)", block, re.M):
            top["C"] = max(top["C"], int(m.group(1)))
    return top


# ---------------------------------------------------------------- next action, economics, start page

def missing_facts(ws, product):
    out = []
    src = product.get("source") if isinstance(product.get("source"), dict) else {}
    live = (ws or {}).get("kind") == "webinar"
    if not src.get("url"):
        out.append("product.yaml : l'adresse de la page " + ("d'inscription au live" if live else "produit") + " (source.url)")
    if not product.get("offers"):
        out.append("product.yaml : " + ("le prix du programme vendu pendant le live" if live else "le prix et l'offre")
                   + ", par marché (offers)")
    if not ws.get("markets"):
        out.append("workspace.yaml : au moins un marché (markets)")
    accounts = ws.get("accounts") if isinstance(ws.get("accounts"), dict) else {}
    if ws.get("stage") == "established" and "meta" in (ws.get("channels") or []) and not accounts.get("meta_ad_account_id"):
        out.append("workspace.yaml : l'identifiant du compte publicitaire Meta (accounts.meta_ad_account_id)")
    return out


def load_product(P):
    product = load_yaml(P["product"], {}) or {}
    if not isinstance(product, dict):
        raise WsError("product.yaml n'a pas la bonne forme (il faut des « clé: valeur »). Restaure product.yaml.bak.")
    return product


def breakeven(product, ws=None):
    """Max ad cost per order placed (or per sign-up for a webinar), to break even: see economics.py."""
    sys.path.insert(0, str(HERE))
    import economics
    return economics.one_line(product, (ws or {}).get("kind") or "product")


PATHS = ("full", "stage")
PATH_FR = {"full": "parcours complet", "stage": "parcours par étape"}
BOOK_STEPS = ("intake", "offer", "research", "strategy", "briefs")
BOOK_LABELS = {"intake": "Le point de départ", "offer": "L'offre et la page", "research": "La recherche",
               "strategy": "La stratégie", "briefs": "Les briefs"}
STEP_DOC = {"intake": "FICHE-ENTREE", "offer": "OFFRE", "research": "RECHERCHE", "strategy": "STRATEGIE",
            "briefs": "BRIEFS", "production": "PRODUCTION", "review": "CONTROLE", "launch": "LANCEMENT",
            "read": "LECTURE", "iterate": "VARIATIONS"}
BOOK_NAMES = ("STRATEGIE-CREATIVE", "CREATIVE-STRATEGY")   # docs.py, French and English


def path_of(ws):
    """full: the first cycle ends with ONE document, the strategy book, rebuilt after each of its five steps.
    stage: each step gives its own document. Absent = full."""
    return ws.get("path") if ws.get("path") in PATHS else "full"


def book_mode(ws, state):
    """True while the book is THE deliverable: full path, in the first cycle or in a cycle that redoes the research or
    the strategy (a new strategy = a new complete document). A cycle of variations has one document per step."""
    if path_of(ws) != "full":
        return False
    return int(state.get("cycle") or 1) == 1 or state.get("cycle_from") in ("research", "strategy")


def book_status(P):
    """The strategy book: which of its five parts exist, its file, and whether a part changed after it was bound."""
    src = P["root"] / "deliverables"
    parts = {s: src / f"{STEP_DOC[s]}.md" for s in BOOK_STEPS}
    have = [s for s, f in parts.items() if f.exists()]
    book = next((src / "word" / f"{n}.docx" for n in BOOK_NAMES if (src / "word" / f"{n}.docx").exists()), None)
    newest = max((parts[s].stat().st_mtime for s in have), default=0)
    return {"have": have, "book": book, "stale": bool(have) and (book is None or book.stat().st_mtime < newest)}


def docs_cmd(P, *args):
    return f'{PY} "{HERE / "docs.py"}" "{P["root"]}"' + "".join(f" {x}" for x in args)


def compute_next(ws, product, state, P=None):
    for s in modes_data()["steps"]:
        st = state["steps"].get(s["id"], {}).get("status", "todo")
        if st in ("done", "skipped"):
            continue
        if P is not None and s["id"] not in BOOK_STEPS and book_mode(ws, state):
            bs = book_status(P)
            if bs["stale"]:
                return ("Relier le document complet avant la production : " + docs_cmd(P, "--book")
                        + " → deliverables/word/STRATEGIE-CREATIVE.docx et .pdf. Donne les deux fichiers à l'utilisateur.")
        verb = "Continuer" if st == "doing" else "Commencer"
        if s["id"] == "intake":
            miss = missing_facts(ws, product)
            if miss:
                return f"{verb} « {s['label']} » : il manque {'; '.join(miss)}."
        how = f"skill {s['skill']}" if s.get("available") else \
            f"le skill {s['skill']} n'existe pas encore ; en attendant : {s['interim']}"
        return f"{verb} l'étape « {s['label']} » ({s['id']}) du cycle {state['cycle']} — {how}."
    return (f"Cycle {state['cycle']} terminé. Ouvre le suivant : ws.py cycle <dossier> "
            "(par défaut il repart des briefs, avec les variations des gagnantes).")


def write_start_page(P, ws, product, state):
    md = modes_data()
    icons = {"todo": "⬜", "doing": "🟨", "done": "✅", "skipped": "⏭️"}
    cap = ws.get("capacity") if isinstance(ws.get("capacity"), dict) else {}
    lines = [f"# {ws.get('name', 'Produit')} — commence ici", "",
             f"Formule **{ws.get('mode')}** · produit **{'neuf' if ws.get('stage') == 'new' else 'avec historique'}**"
             f" · programme **{ws.get('programme')}**"
             + (f" · type **{ws.get('kind')}**" if ws.get("kind", "product") != "product" else "")
             + f" · cycle **{state['cycle']}**"
             f" · machine **{cap.get('machine', 'own-pc')}** · Claude **{cap.get('claude', 'pro')}**", "",
             "## La prochaine action", "", state["next"], ""]
    lines += ["## Ton document", ""]
    bs = book_status(P)
    if book_mode(ws, state):
        lines.append("**Parcours complet** : un seul document, ta stratégie créative, qui grandit à chaque étape "
                     "jusqu'aux briefs (deliverables/word/STRATEGIE-CREATIVE.pdf).")
        lines.append("")
        lines.append(" · ".join(f"{'✅' if s in bs['have'] else '⬜'} {BOOK_LABELS[s]}" for s in BOOK_STEPS))
        lines.append("")
        if bs["book"] is None:
            lines.append("- Pas encore relié." if not bs["have"] else
                         f"- À relier : {docs_cmd(P, '--book')}")
        else:
            when = dt.datetime.fromtimestamp(bs["book"].stat().st_mtime).strftime("%d/%m/%Y %H:%M")
            lines.append(f"- Relié le {when}, {len(bs['have'])} partie(s) sur 5"
                         + (" ; une partie a changé depuis : à relier." if bs["stale"] else "."))
    else:
        why = (" (un cycle de variations : le document complet est déjà fait, chaque étape a le sien)"
               if path_of(ws) == "full" else "")
        lines.append(f"**Parcours par étape**{why} : chaque étape a son document, dans deliverables/word/ "
                     "(LANCEMENT, LECTURE, VARIATIONS…). Le document complet se relie quand tu veux : "
                     f"{docs_cmd(P, '--book')}")
    lines.append("")
    if ws.get("goal") or ws.get("budget_daily") or ws.get("team"):
        lines += ["## Le cadre", ""]
        if ws.get("goal"):
            lines.append(f"- Objectif : {ws['goal']}")
        if ws.get("budget_daily"):
            lines.append(f"- Budget de test par jour : {ws['budget_daily']}")
        if ws.get("team"):
            lines.append(f"- Qui produit les vidéos : {ws['team']}")
        lines.append("")
    be = breakeven(product, ws)
    if be:
        lines += ["## Le point d'équilibre", "", f"- {be}", ""]
    lines += [f"## Les étapes du cycle {state['cycle']}", ""]
    for s in md["steps"]:
        info = state["steps"].get(s["id"], {})
        st = info.get("status", "todo")
        when = f" ({info['date']})" if info.get("date") else ""
        lines.append(f"- {icons.get(st, '⬜')} {s['label']} — {STATUS_FR.get(st, st)}{when}")
    miss = missing_facts(ws, product)
    if miss:
        lines += ["", "## Ce qu'il manque", ""] + [f"- {m}" for m in miss]
    eff = state.get("effective_engines") or {}
    lines += ["", "## Les outils", ""]
    if not eff:
        lines.append("- Pas encore vérifiés sur cet ordinateur : lance « ws.py doctor <dossier> ».")
    else:
        for task, engine in eff.items():
            label = md["engines"].get(engine, {}).get("label", engine)
            lines.append(f"- {md['tasks'].get(task, task)} : {label}")
        lines.append(f"- (vérifié le {state.get('engines_checked_on', '?')})")
    if P["journal"].exists():
        tail = [l for l in read_text(P["journal"]).splitlines() if l.startswith("- ")][-5:]
        if tail:
            lines += ["", "## Les dernières décisions (journal.md)", ""] + tail
    try:
        P["start"].write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    except PermissionError:
        raise WsError("COMMENCE-ICI.md est ouvert dans un autre programme : ferme-le et relance.")


def refresh(P, ws, state):
    product = load_product(P)
    state["next"] = compute_next(ws, product, state, P)
    dump_yaml(P["state"], state)
    write_start_page(P, ws, product, state)
    return state["next"]


# ---------------------------------------------------------------- commands

def make_tree(root, adopt_paths):
    dirs = ["library/voice", "data/exports", "data/screenshots", "data/deliveries", "deliverables"]
    if "references" not in adopt_paths:
        dirs += [f"References/{d}" for d in REF_SUBDIRS]
    dirs += [f"cycles/cycle-01/{d}" for d in ("briefs", "creatives", "launch", "results")]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)


def new_cycle_files(root, n):
    ads = root / "cycles" / f"cycle-{n:02d}" / "ads.yaml"
    if not ads.exists():
        dump_yaml(ads, {"cycle": n, "ads": []})


def cmd_init(a, adopt=False):
    need_yaml()
    root = Path(a.folder).expanduser().resolve()
    if adopt and not root.is_dir():
        raise WsError(f"le dossier à adopter n'existe pas : {root}")
    if (root / "workspace.yaml").exists():
        raise WsError(f"un workspace existe déjà ici : {root / 'workspace.yaml'}")
    markets = [parse_market(m) for m in (a.market or [])]  # checked before anything is created
    root.mkdir(parents=True, exist_ok=True)
    paths, inferred, programme = {}, [], a.programme
    if adopt:
        if (root / "References").is_dir():
            paths["references"] = "References"
        for plan in ("plan.yaml", "plan_migrated.yaml"):
            if (root / plan).exists():
                paths["plan"] = plan
                break
        if (root / "References" / "REFERENCES_LOG.xlsx").exists():
            paths["references_log"] = "References/REFERENCES_LOG.xlsx"
        if programme is None and list(root.glob("CONTRAT-ACCOMPAGNEMENT*")):
            programme = "accelerateur"
            inferred.append("programme accelerateur (contrat d'accompagnement trouvé)")
    programme = programme or "none"
    make_tree(root, paths)
    (root / "library" / "competitors").mkdir(parents=True, exist_ok=True)
    ws = {"format": FORMAT, "name": a.name, "business": a.business or "", "language": "fr",
          "mode": a.mode, "programme": programme, "kind": a.kind, "stage": a.stage,
          "path": a.path or ("stage" if adopt else "full"),
          "channels": [c.strip() for c in a.channels.split(",") if c.strip()],
          "markets": markets, "goal": a.goal or "", "budget_daily": a.budget or "", "team": a.team or "",
          "capacity": {"machine": "own-pc", "claude": "pro"},
          "accounts": {"shop_url": a.shop or "", "meta_ad_account_id": "", "meta_page": "", "tiktok_account": ""},
          "brand": {"name": "", "primary_color": "", "accent_color": ""},
          "engines": {}, "paths": paths}
    P = paths_of(root, ws)
    dump_yaml(P["workspace"], ws)
    if not P["product"].exists():
        dump_yaml(P["product"], {"source": {"url": a.shop or "", "read_on": ""}, "name": a.name, "promise": "",
                                 "offers": [], "variants": [], "proof": [],
                                 "economics": {"currency": "", "unit_cost": "", "shipping_cost": "",
                                               "confirmation_rate": "", "delivery_rate": ""},
                                 "baseline": {}, "constraints": []})
    lib = {"references.yaml": {"references": []}, "avatars.yaml": {"avatars": []}, "blocks.yaml": {"blocks": []},
           "competitors.yaml": {"competitors": []}}
    for f, data in lib.items():
        fp = root / "library" / f
        if not fp.exists():
            fp.parent.mkdir(parents=True, exist_ok=True)
            dump_yaml(fp, data)
    new_cycle_files(root, 1)
    state = new_state()
    found = scan_codes(P, ws)
    state["counters"] = {k: max(state["counters"][k], found[k]) for k in CODE_PREFIXES}
    if adopt:
        refs_media = P["refs_dir"].exists() and any(CODE_IN_NAME.match(f.name) for f in P["refs_dir"].rglob("*"))
        if refs_media:
            state["steps"]["research"] = {"status": "done", "date": today()}
            inferred.append("références trouvées → research faite")
        if paths.get("plan"):
            for s in ("strategy", "briefs"):
                state["steps"][s] = {"status": "done", "date": today(), "outputs": [paths["plan"]]}
            inferred.append(f"{paths['plan']} trouvé → strategy et briefs faites")
        if list(root.glob("FICHE DE LANCEMENT*")):
            for s in ("production", "review", "launch"):
                state["steps"][s] = {"status": "done", "date": today()}
            inferred.append("fiche de lancement trouvée → production, review et launch faites")
        if any(state["steps"][s]["status"] == "done" for s in step_ids()):
            state["steps"]["intake"] = {"status": "doing", "date": today()}
            inferred.append("intake en cours : product.yaml à remplir depuis la page en ligne")
    journal(P, ("Workspace adopté (rien déplacé)" if adopt else "Workspace créé")
            + f" : formule {a.mode}, produit {a.stage}, programme {programme}, {PATH_FR[ws['path']]}"
            + (f", type {a.kind}" if a.kind != "product" else "") + "."
            + (" Déduit : " + "; ".join(inferred) + "." if inferred else "")
            + (" Compteurs repris des fichiers : " + ", ".join(f"{k}{v:02d}" for k, v in found.items() if v) + "."
               if any(found.values()) else ""))
    nxt = refresh(P, ws, state)
    print(f"Workspace prêt : {root}")
    for i in inferred:
        print(f"  déduit : {i}")
    print(f"Prochaine action : {nxt}")


def cmd_status(a):
    P, ws, state = open_ws(a.folder)
    refresh(P, ws, state)
    print(read_text(P["start"]))


def cmd_next(a):
    P, ws, state = open_ws(a.folder)
    print(refresh(P, ws, state))


def validate(P, ws, state):
    errors, warnings = [], []
    for k in ("format", "name", "mode", "programme", "stage", "channels", "markets"):
        if k not in ws:
            errors.append(f"workspace.yaml : clé « {k} » absente")
    if not str(ws.get("name", "")).strip():
        errors.append("workspace.yaml : le nom du produit est vide")
    if ws.get("format") not in (None, FORMAT):
        errors.append(f"workspace.yaml : format {ws.get('format')} inconnu (attendu {FORMAT})")
    for key, allowed in (("mode", MODES), ("stage", STAGES), ("programme", PROGRAMMES), ("kind", KINDS),
                         ("path", PATHS)):
        if key in ("kind", "path") and key not in ws:  # absent = product (before 1.2), full path (before 1.3.2)
            continue
        if ws.get(key) not in allowed:
            errors.append(f"workspace.yaml : {key} « {ws.get(key)} » inconnu ({', '.join(allowed)})")
    if not isinstance(ws.get("channels", []), list):
        errors.append("workspace.yaml : channels doit être une liste, ex. [meta, tiktok]")
    else:
        for ch in ws.get("channels") or []:
            if ch not in ("meta", "tiktok"):
                warnings.append(f"workspace.yaml : canal « {ch} » non géré (meta, tiktok)")
    markets = ws.get("markets") or []
    if not isinstance(markets, list):
        errors.append("workspace.yaml : markets doit être une liste")
        markets = []
    for i, m in enumerate(markets):
        if not isinstance(m, dict):
            errors.append(f"workspace.yaml : marché n°{i + 1} doit avoir code, country, currency… (pas « {m} »)")
            continue
        if not re.fullmatch(r"[A-Z]{2}", str(m.get("code", ""))):
            errors.append(f"workspace.yaml : marché n°{i + 1} sans code pays à deux lettres")
        if not m.get("currency"):
            warnings.append(f"workspace.yaml : marché {m.get('code')} sans devise")
    md = modes_data()
    engines = ws.get("engines") or {}
    if not isinstance(engines, dict):
        errors.append("workspace.yaml : engines doit être de la forme {tâche: outil}")
        engines = {}
    for task, engine in engines.items():
        if task not in md["tasks"]:
            errors.append(f"workspace.yaml : engines.{task} n'est pas une tâche connue ({', '.join(md['tasks'])})")
        elif engine not in md["engines"]:
            errors.append(f"workspace.yaml : engines.{task} = « {engine} » n'est pas un outil connu")
    for key, rel in (ws.get("paths") or {}).items():
        if not (P["root"] / rel).exists():
            errors.append(f"workspace.yaml : paths.{key} pointe vers « {rel} », introuvable")
    product = load_product(P)
    for s, info in state["steps"].items():
        if s not in step_ids():
            warnings.append(f"state.yaml : étape « {s} » qui n'existe plus ; « ws.py repair » la retire")
            continue
        if info.get("status") not in STATUSES:
            errors.append(f"state.yaml : statut « {info.get('status')} » invalide pour {s}")
        for out in info.get("outputs") or []:
            if not (P["root"] / out).exists():
                warnings.append(f"state.yaml : la sortie « {out} » de l'étape {s} est introuvable")
    intake = state["steps"].get("intake", {}).get("status")
    miss = missing_facts(ws, product)
    if intake == "done" and miss:
        errors.append("intake marqué fait mais il manque : " + "; ".join(miss))
    elif intake == "skipped" and miss:
        warnings.append("intake sautée alors qu'il manque : " + "; ".join(miss))
    refs = load_yaml(P["refs_index"], {}) or {}
    refs = refs.get("references") if isinstance(refs, dict) else None
    if refs is not None and not isinstance(refs, list):
        errors.append("library/references.yaml : « references » doit être une liste")
        refs = []
    seen = set()
    for r in refs or []:
        if not isinstance(r, dict):
            errors.append(f"library/references.yaml : entrée « {r} » sans clés (il faut code, url, file…)")
            continue
        code = str(r.get("code", ""))
        if not re.fullmatch(r"(AL|TT|IG|YT|CL)\d{2,}", code):
            errors.append(f"library/references.yaml : code « {code} » invalide (AL01, TT12…)")
        if code in seen:
            errors.append(f"library/references.yaml : code {code} en double")
        seen.add(code)
        f = r.get("file")
        if f and not any((base / f).exists() for base in (P["refs_dir"], P["root"])) \
                and not list(P["refs_dir"].rglob(Path(str(f)).name)):
            warnings.append(f"library/references.yaml : fichier de {code} introuvable ({f})")
        if not r.get("url"):
            warnings.append(f"library/references.yaml : {code} sans lien d'origine")
    comp = load_yaml(P["root"] / "library" / "competitors.yaml", {}) or {}
    comps = comp.get("competitors") if isinstance(comp, dict) else None
    if comps is not None and not isinstance(comps, list):
        errors.append("library/competitors.yaml : « competitors » doit être une liste")
        comps = []
    seen_co = set()
    for c in comps or []:
        if not isinstance(c, dict):
            errors.append(f"library/competitors.yaml : entrée « {c} » sans clés (il faut code, page_url…)")
            continue
        code = str(c.get("code", ""))
        if not re.fullmatch(r"CO\d{2,}", code):
            errors.append(f"library/competitors.yaml : code « {code} » invalide (CO01, CO02…)")
        if code in seen_co:
            errors.append(f"library/competitors.yaml : code {code} en double")
        seen_co.add(code)
        if not c.get("page_url"):
            warnings.append(f"library/competitors.yaml : {code} sans adresse de page produit (page_url)")
        if c.get("page_url") and not c.get("read_on"):
            warnings.append(f"library/competitors.yaml : {code} sans date de lecture (read_on)")
    found = scan_codes(P, ws)
    for k in CODE_PREFIXES:
        if found[k] > state["counters"][k]:
            errors.append(f"state.yaml : le compteur {k} ({state['counters'][k]}) est en dessous de {k}{found[k]:02d} "
                          "déjà utilisé ; lance « ws.py repair »")
    for ads_file in sorted((P["root"] / "cycles").glob("*/ads.yaml")):
        data = load_yaml(ads_file, {}) or {}
        ads = data.get("ads") if isinstance(data, dict) else None
        if ads is None or not isinstance(ads, list):
            errors.append(f"{ads_file.relative_to(P['root'])} : il faut une liste « ads »")
            continue
        names = set()
        for ad in ads:
            if not isinstance(ad, dict):
                errors.append(f"{ads_file.relative_to(P['root'])} : entrée « {ad} » sans clés")
                continue
            code = str(ad.get("code", ""))
            if not re.fullmatch(r"C\d{2,} V\d+ [A-Z]", code):
                errors.append(f"{ads_file.relative_to(P['root'])} : code de pub « {code} » invalide (ex. C04 V2 B)")
            if code in names:
                errors.append(f"{ads_file.relative_to(P['root'])} : pub {code} en double")
            names.add(code)
            if ad.get("status") and ad["status"] not in AD_STATUSES:
                errors.append(f"{ads_file.relative_to(P['root'])} : statut « {ad['status']} » inconnu pour {code}")
    return errors, warnings


def cmd_check(a):
    P, ws, state = open_ws(a.folder)
    errors, warnings = validate(P, ws, state)
    for w in warnings:
        print("attention : " + w)
    for e in errors:
        print("ERREUR : " + e)
    print(f"{len(errors)} erreur(s), {len(warnings)} avertissement(s).")
    if not errors:
        refresh(P, ws, state)
    sys.exit(1 if errors else 0)


# 1.4, 15/11/2026 (Richie): after every output the suite itself says what the person now has and what comes next,
# in one short paragraph that ends on one question. Hard-coded here so it never depends on the conversation:
# every step that finishes goes through set_step, the book through docs.py, the page through offer.py page.
# Claude ends its reply with this paragraph in its own words, once, as its last lines. Never a list, never pushy.
HANDOFF = {
    "intake": {
        "*": "Tu as ta fiche d'entrée : ce qu'une {one} peut coûter en pub et si ton pixel compte juste. La suite, "
             "c'est l'offre et la page : je lis les pages des concurrents dont les pubs tournent depuis des semaines, "
             "et je compare avec la tienne. On s'y met ?",
    },
    "offer": {
        "*": "Ton offre est chiffrée et ta page a son brief, section par section. Si tu veux, j'écris la page entière à "
             "partir d'une page qui vend déjà (dis « écris ma page »). La suite : les références, les pubs et les "
             "vidéos qui ont déjà vendu dans ton marché. Je lance la recherche ?",
    },
    "research": {
        "*": "Tes références sont trouvées, transcrites et lues. La suite : les avatars (à qui on parle), les angles "
             "et le système de créas à tester. Je les écris ?",
    },
    "strategy": {
        "*": "Ta stratégie est posée : les avatars, le trio testé et les créas à produire. La suite : les briefs, une "
             "page par créa que ton monteur ou ton IA peut suivre sans t'appeler. Je les écris ?",
    },
    "briefs": {
        "*": "Tes briefs sont prêts{book}. Maintenant c'est à toi : produis les vidéos (toi, ton monteur ou l'IA), "
             "nomme chaque fichier par son code (C01, C02…), puis envoie-les-moi : je contrôle chacune avant qu'un "
             "franc ne parte. Tu veux que je répartisse qui produit quoi et pour quand ?",
    },
    "production": {
        "*": "Toutes les créas sont livrées. La suite : le contrôle, vidéo par vidéo, contre son brief. Je les "
             "regarde ?",
    },
    "review": {
        "*": "Le contrôle est fait : chaque créa est bonne à lancer, à corriger ou à refaire, et chaque correction a "
             "son message prêt pour celui qui l'a faite. Quand elles sont toutes bonnes, dis « lance » et j'écris ta "
             "fiche de lancement. On lance ?",
    },
    "launch": {
        "*": "Ta campagne est prête à créer, nom par nom. Une fois en ligne, ne touche à rien pendant 3 jours. Au jour "
             "3 puis au jour 7, envoie-moi l'export au niveau des pubs (colonnes « Lecture créa ») : je te dis quoi "
             "couper, quoi garder, et pourquoi. Tu me dis le jour où elle part ?",
        "webinar": "Ta campagne est prête à créer, nom par nom. Elle tourne 7 à 10 jours avant le live et s'arrête le "
                   "jour du live. Ne touche à rien pendant 3 jours, puis envoie-moi l'export au niveau des pubs : il "
                   "reste assez de jours pour couper les perdantes et pousser les gagnantes avant le live. Après le "
                   "live, donne-moi les inscrits, les présents et les ventes. Tu me dis le jour où elle part ?",
    },
    "read": {
        "*": "Tu sais quoi couper, quoi garder et pourquoi, et le registre des gagnants dit quelle part de ta formule a "
             "gagné. Fais ces gestes dans le Gestionnaire aujourd'hui. La suite : les variations des gagnantes, le "
             "prochain lot de pubs à produire. Je les prépare ?",
        "webinar": "Tu sais quoi couper, quoi garder et pourquoi. Fais ces gestes dans le Gestionnaire aujourd'hui. "
                   "La suite : les variations des gagnantes pour le prochain live, et les pubs pour ceux qui se sont "
                   "inscrits sans venir. Je les prépare ?",
    },
    "iterate": {
        "*": "Le prochain cycle est ouvert avec ses variations, chacune ne change qu'une chose. La suite : leurs "
             "briefs, puis la même boucle (produire, contrôler, lancer, lire). J'écris les briefs ?",
    },
    "book": {
        "*": "Ton document de stratégie est relié, en Word et en PDF{parts}. {after}",
    },
    "page": {
        "*": "Ta page est écrite section par section contre une page qui vend, chaque changement expliqué. Remplis les "
             "[__] (tes chiffres, tes preuves), mets-la en ligne, puis envoie-moi le lien : je la relis sur téléphone "
             "comme un visiteur. Tu veux que j'écrive aussi le texte de la pub qui y mène ?",
    },
}
HANDOFF_ONE = {"product": "commande", "digital": "vente", "webinar": "inscription"}


def handoff(P, sid, ws=None, state=None):
    """The paragraph that closes a step: what the person has now, what comes next, one question."""
    ws = ws if ws is not None else (load_yaml(P["workspace"], {}) or {})
    kind = ws.get("kind") or "product"
    texts = HANDOFF.get(sid) or {}
    text = texts.get(kind) or texts.get("*")
    if not text:
        return ""
    book = parts = after = ""
    if sid in ("briefs", "book"):
        bs = book_status(P)
        if sid == "briefs" and state is not None and book_mode(ws, state):
            book = ", et ton document complet se relie avec eux (en Word et en PDF)"
        n = len(bs["have"])
        parts = f", {n} partie{'s' if n > 1 else ''} sur 5" if n < 5 else ", complet"
        after = (HANDOFF["briefs"]["*"].split(". ", 1)[1] if n >= 5 else
                 "Il grandit à chaque étape. On passe à la suivante ?")
    return "La suite — " + text.format(one=HANDOFF_ONE.get(kind, "commande"), book=book, parts=parts, after=after)


def set_step(P, state, sid, status, note=None, outputs=None):
    info = state["steps"].setdefault(sid, {})
    info["status"] = status
    info["date"] = today()
    if outputs:
        info["outputs"] = sorted(set((info.get("outputs") or []) + outputs))
    if status == "done":
        try:
            msg = handoff(P, sid, state=state)
        except Exception:  # noqa: BLE001 — the hand-off never stops a step
            msg = ""
        if msg:
            print("\n" + msg)


def cmd_step(a):
    P, ws, state = open_ws(a.folder)
    if a.step not in step_ids():
        raise WsError(f"étape inconnue « {a.step} ». Étapes : {', '.join(step_ids())}")
    if a.status not in STATUSES:
        raise WsError(f"statut inconnu « {a.status} » ({', '.join(STATUSES)})")
    product = load_product(P)
    miss = missing_facts(ws, product)
    if a.step == "intake" and a.status == "done" and miss:
        raise WsError("intake ne peut pas être marquée faite, il manque : " + "; ".join(miss)
                      + ". Pour avancer quand même : ws.py step <dossier> intake skipped --note \"pourquoi\"")
    set_step(P, state, a.step, a.status, outputs=a.output)
    extra = ""
    if a.step == "intake" and a.status == "skipped" and miss:
        extra = " (sautée avec des faits manquants : " + "; ".join(miss) + ")"
        print("attention : intake sautée alors qu'il manque : " + "; ".join(miss))
    journal(P, f"Étape {a.step} → {STATUS_FR[a.status]}{extra}" + (f". {a.note}" if a.note else "")
            + (f" Sorties : {', '.join(a.output)}." if a.output else ""))
    if a.status == "done" and a.step in STEP_DOC:
        if a.step in BOOK_STEPS and book_mode(ws, state):
            print("Document complet (il grandit à chaque étape, à relier maintenant) : " + docs_cmd(P, "--book"))
        elif (P["root"] / "deliverables" / f"{STEP_DOC[a.step]}.md").exists():
            print("Document de l'étape : " + docs_cmd(P, STEP_DOC[a.step]))
    print(refresh(P, ws, state))


def cmd_start(a):
    P, ws, state = open_ws(a.folder)
    ids = step_ids()
    if a.step not in ids:
        raise WsError(f"étape inconnue « {a.step} ». Étapes : {', '.join(ids)}")
    skipped = []
    for s in ids[:ids.index(a.step)]:
        if state["steps"][s].get("status") in ("todo", "doing"):
            set_step(P, state, s, "skipped")
            skipped.append(s)
    set_step(P, state, a.step, "doing")
    journal(P, f"On commence par l'étape {a.step}. Raison : {a.reason or 'non précisée'}."
            + (f" Sautées : {', '.join(skipped)}." if skipped else ""))
    print(refresh(P, ws, state))


CYCLE_CHECKS = ("briefs_", "production_", "review_", "launch_", "read_")


def cmd_cycle(a):
    P, ws, state = open_ws(a.folder)
    ids = step_ids()
    frm = a.start_from or ("briefs" if state["steps"].get("iterate", {}).get("status") == "done" else "strategy")
    if frm not in CYCLE_FROM:
        raise WsError(f"--from doit être l'un de : {', '.join(CYCLE_FROM)}")
    in_progress = [s for s in ids[ids.index(frm):] if state["steps"][s].get("status") == "doing"]
    if in_progress and not a.force:
        raise WsError(f"étape(s) encore en cours dans ce cycle : {', '.join(in_progress)}. Termine-les, ou ajoute --force.")
    if in_progress:
        print(f"attention : étape(s) encore en cours ({', '.join(in_progress)}) ; le nouveau cycle est ouvert quand même.")
    elif not any(state["steps"][s].get("status") == "done" for s in ids[ids.index(frm):]):
        print("attention : aucune étape de ce cycle n'est faite ; le nouveau cycle est ouvert quand même.")
    state["cycle"] += 1
    state["cycle_from"] = frm   # a cycle that redoes the research or the strategy gets a complete document again
    c = state["cycle"]
    for sub in ("briefs", "creatives", "launch", "results"):
        (P["root"] / "cycles" / f"cycle-{c:02d}" / sub).mkdir(parents=True, exist_ok=True)
    new_cycle_files(P["root"], c)
    for s in ids[ids.index(frm):]:
        state["steps"][s] = {"status": "todo"}
    au = P["root"] / "audit.yaml"
    if au.exists():   # the checks of one cycle's ads say nothing about the next one's
        data = load_yaml(au, {}) or {}
        checks = data.get("checks") if isinstance(data.get("checks"), dict) else None
        if checks is not None:
            gone = [k for k in checks if k.startswith(CYCLE_CHECKS)]
            for k in gone:
                checks.pop(k)
            if gone:
                dump_yaml(au, data)
    journal(P, f"Nouveau cycle {c}, à partir de l'étape {frm}. Les idées gardent leurs numéros "
               f"(prochaine idée neuve : C{state['counters']['C'] + 1:02d}).")
    print(refresh(P, ws, state))


# ---------------------------------------------------------------- the long run: every product, a product's history

SKIP_DIRS = {"References", "cycles", "library", "data", "deliverables", "creatives", "briefs", "node_modules"}


def find_workspaces(root, depth=3):
    """Every product folder (one with workspace.yaml) in root and its subfolders, without entering a product."""
    out = []

    def walk(d, n):
        if (d / "workspace.yaml").exists():
            out.append(d)
            return
        if n == 0:
            return
        try:
            subs = sorted(x for x in d.iterdir() if x.is_dir() and x.name not in SKIP_DIRS and not x.name.startswith("."))
        except OSError:
            return
        for x in subs:
            walk(x, n - 1)

    walk(root, depth)
    return out


def ledger_rows(P, cycle):
    data = load_yaml(P["root"] / "cycles" / f"cycle-{int(cycle):02d}" / "ads.yaml", {}) or {}
    return [x for x in (data.get("ads") or []) if isinstance(x, dict) and x.get("code")]


def reminders(P, state, rows):
    """What the calendar and the files say, without anyone remembering: day 3 and day 7 of the test, an export or a
    delivery report not read yet, delivered videos waiting for their check."""
    out = []
    today_ = dt.date.today()
    launched = []
    for x in rows:
        try:
            launched.append(dt.date.fromisoformat(str(x.get("launched_on"))[:10]))
        except ValueError:
            pass
    read_done = state["steps"].get("read", {}).get("status") == "done"
    if launched and not read_done:
        days = (today_ - min(launched)).days
        if days >= 7:
            out.append(f"Jour {days} du test : la lecture est due. Il faut l'export « Lecture créa » au niveau des pubs, "
                       "les deux répartitions et le rapport de livraison.")
        elif days >= 3:
            out.append(f"Jour {days} du test : premier point possible (seulement les échecs évidents ; on juge au jour 7).")
    res_dir = P["root"] / "cycles" / f"cycle-{int(state['cycle']):02d}" / "results"
    seen = max((f.stat().st_mtime for f in res_dir.glob("*.yaml")), default=0) if res_dir.exists() else 0
    for sub, what in (("exports", "Nouvel export"), ("deliveries", "Nouveau rapport de livraison")):
        d = P["root"] / "data" / sub
        new = [f.name for f in d.glob("*") if f.is_file() and f.stat().st_mtime > seen] if d.exists() else []
        if new and launched:
            out.append(f"{what} pas encore lu : {', '.join(sorted(new)[:3])}")
    waiting = [x["code"] for x in rows if x.get("status") == "review"]
    if waiting:
        out.append(f"Vidéo(s) livrée(s) à contrôler : {', '.join(waiting)}")
    return out


def cmd_overview(a):
    """« Qu'est-ce que je fais aujourd'hui ? » — every product of the folder: where it stands, what to do now."""
    need_yaml()
    root = Path(a.folder).expanduser().resolve()
    found = find_workspaces(root)
    if not found:
        raise WsError(f"aucun produit (workspace.yaml) dans {root} ni dans ses sous-dossiers")
    day = today()
    lines = [f"# Aujourd'hui, {dt.date.today().strftime('%d/%m/%Y')} — {len(found)} produit(s)", ""]
    for d in found:
        try:
            P, ws, state = open_ws(d)
            nxt = refresh(P, ws, state)
        except WsError as e:
            lines += [f"## {d.name}", "", f"- ⚠️ {e}", ""]
            continue
        cur = next((s for s in step_ids() if state["steps"][s].get("status") in ("doing", "todo")), None)
        rows = ledger_rows(P, state["cycle"])
        live = [x["code"] for x in rows if x.get("status") == "live"]
        late = [x["code"] for x in rows if x.get("status") in ("brief", "production") and x.get("due")
                and str(x.get("due")) < day]
        lines += [f"## {ws.get('name')}", "", f"- Dossier : {d}",
                  f"- Cycle {state['cycle']} · {step_label(cur) if cur else 'cycle terminé'} · {PATH_FR[path_of(ws)]}",
                  f"- Maintenant : {nxt}"]
        if live:
            lines.append(f"- En ligne : {len(live)} pub(s)")
        if late:
            lines.append(f"- En retard en production : {', '.join(late)}")
        for alert in reminders(P, state, rows):
            lines.append(f"- ⏰ {alert}")
        if book_mode(ws, state):
            bs = book_status(P)
            lines.append(f"- Document complet : {len(bs['have'])} partie(s) sur 5"
                         + (" (à relier)" if bs["stale"] else ""))
        if P["journal"].exists():
            tail = [l for l in read_text(P["journal"]).splitlines() if l.startswith("- ")][-1:]
            if tail:
                lines.append(f"- Dernière décision : {tail[0][2:]}")
        lines.append("")
    print("\n".join(lines))


def _num(v):
    try:
        return float(str(v).replace(",", ".").replace(" ", ""))
    except (TypeError, ValueError):
        return None


def _fmt(v, pct=False):
    if v is None:
        return "—"
    if pct:
        return f"{v * 100:.1f} %" if v <= 1 else f"{v:.1f} %"
    return f"{v:,.0f}".replace(",", " ") if abs(v) >= 100 else f"{v:.2f}".rstrip("0").rstrip(".")


STATUS_LABEL = {"brief": "brief", "production": "en production", "review": "au contrôle", "ready": "prête",
                "live": "en ligne", "paused": "en pause", "killed": "coupée", "winner": "gagnante"}


def cmd_bilan(a):
    """The product's history, every cycle: what ran, what won, what was cut and why, each idea and its variations,
    each avatar, the account's own reference points. Out: deliverables/BILAN.md (then docs.py <dossier> BILAN)."""
    P, ws, state = open_ws(a.folder)
    avatars = {}
    for x in (load_yaml(P["root"] / "library" / "avatars.yaml", {}) or {}).get("avatars") or []:
        key = x.get("n", x.get("id")) if isinstance(x, dict) else None
        if key is not None:
            avatars[str(key)] = x.get("short") or x.get("name") or ""
    cur = (ws.get("markets") or [{}])[0].get("currency", "") if ws.get("markets") else ""
    cycles = [(c, ledger_rows(P, c)) for c in range(1, int(state["cycle"]) + 1)]
    allrows = [(c, x) for c, rows in cycles for x in rows]
    res = lambda x: x.get("results") if isinstance(x.get("results"), dict) else {}
    spend = sum(_num(res(x).get("spend")) or 0 for _, x in allrows)
    buys = sum(_num(res(x).get("purchases")) or 0 for _, x in allrows)
    launched = [(c, x) for c, x in allrows if x.get("launched_on") or _num(res(x).get("spend"))]
    wins = [x["code"] for _, x in allrows if x.get("status") == "winner"]
    cut = [x["code"] for _, x in allrows if x.get("status") == "killed"]
    L = [f"# Bilan — {ws.get('name')}", "",
         f"*Au {dt.date.today().strftime('%d/%m/%Y')} · {state['cycle']} cycle(s) de test · "
         f"{len(launched)} pub(s) lancée(s)*", "", "## En bref", ""]
    L.append(f"- Dépense : {_fmt(spend)} {cur} · achats : {_fmt(buys)}"
             + (f" · coût par achat : {_fmt(spend / buys)} {cur}" if buys else ""))
    L.append(f"- Gagnantes : {', '.join(wins) if wins else 'aucune pour l’instant'}")
    L.append(f"- Coupées : {len(cut)}")
    L.append(f"- Maintenant : {state.get('next') or compute_next(ws, load_product(P), state, P)}")
    L.append("")
    L += ["## Cycle par cycle", ""]
    for c, rows in cycles:
        if not rows:
            continue
        dates = sorted(str(x["launched_on"]) for x in rows if x.get("launched_on"))
        L += [f"### Cycle {c}" + (f" · lancé le {dates[0]}" if dates else ""), "",
              "| Pub | Avatar | Format | Statut | Dépense | Achats | Coût par achat | Accroche | Verdict |",
              "|---|---|---|---|---|---|---|---|---|"]
        for x in rows:
            r = res(x)
            v = r.get("verdict") if isinstance(r.get("verdict"), dict) else {}
            why = "; ".join(v.get("causes") or []) if isinstance(v.get("causes"), list) else ""
            av = str(x.get("avatar") or "")
            L.append(" | ".join(["", x["code"], (avatars.get(av) or av or "—"), str(x.get("format") or "—"),
                                 STATUS_LABEL.get(x.get("status"), str(x.get("status") or "—")),
                                 _fmt(_num(r.get("spend"))), _fmt(_num(r.get("purchases"))), _fmt(_num(r.get("cpa"))),
                                 _fmt(_num(r.get("hook")), pct=True),
                                 (why or "—").replace("|", "/"), ""]).strip())
        L.append("")
    ideas = {}
    for c, x in allrows:
        ideas.setdefault(x["code"].split()[0], []).append((c, x))
    if ideas:
        L += ["## Chaque idée et ses variations", ""]
        for idea in sorted(ideas):
            parts = []
            for c, x in ideas[idea]:
                ch = f" ({x['change']})" if x.get("change") else ""
                parts.append(f"{x['code']} {STATUS_LABEL.get(x.get('status'), x.get('status') or '')}{ch}, cycle {c}")
            L.append(f"- **{idea}** : " + " → ".join(parts))
        L.append("")
    if avatars or any(x.get("avatar") for _, x in allrows):
        L += ["## Les avatars", "", "| Avatar | Pubs lancées | Gagnantes | Coupées |", "|---|---|---|---|"]
        keys = sorted({str(x.get("avatar")) for _, x in allrows if x.get("avatar")} | set(avatars))
        for k in keys:
            mine = [x for _, x in allrows if str(x.get("avatar")) == k]
            L.append(f"| {avatars.get(k) or k} | {sum(1 for x in mine if x.get('launched_on'))} | "
                     f"{sum(1 for x in mine if x.get('status') == 'winner')} | "
                     f"{sum(1 for x in mine if x.get('status') == 'killed')} |")
        L.append("")
    bench = (load_yaml(P["root"] / "library" / "benchmarks.yaml", {}) or {}).get("cycles") or {}
    if bench:
        L += ["## Les repères du compte (médianes, cycle par cycle)", "",
              "| Cycle | Accroche | Rétention | CTR lien | CPM | Coût par achat |", "|---|---|---|---|---|---|"]
        for k in sorted(bench):
            b = bench[k] if isinstance(bench[k], dict) else {}
            L.append(f"| {k.replace('cycle-', '')} | {_fmt(_num(b.get('hook')), True)} | {_fmt(_num(b.get('hold')), True)} | "
                     f"{_fmt(_num(b.get('ctr_link')), True)} | {_fmt(_num(b.get('cpm')))} | {_fmt(_num(b.get('cpa')))} |")
        L.append("")
    if not allrows:
        L += ["Aucune pub dans le registre pour l'instant : le bilan se remplit dès le premier lancement.", ""]
    out = P["root"] / "deliverables" / "BILAN.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    journal(P, f"Bilan écrit : {len(launched)} pub(s) lancée(s) sur {state['cycle']} cycle(s), {len(wins)} gagnante(s).")
    print(f"Écrit : {out}\nEn Word et PDF : " + docs_cmd(P, "BILAN"))


def cmd_code(a):
    P, ws, state = open_ws(a.folder)
    pre = a.prefix.upper()
    if pre not in CODE_PREFIXES:
        raise WsError(f"préfixe inconnu « {pre} » ({', '.join(CODE_PREFIXES)})")
    found = scan_codes(P, ws)
    nxt = max(state["counters"][pre], found[pre]) + 1
    state["counters"][pre] = nxt
    dump_yaml(P["state"], state)
    print(f"{pre}{nxt:02d}")


def cmd_log(a):
    P, ws, state = open_ws(a.folder)
    if not a.text.strip():
        raise WsError("le texte du journal est vide")
    journal(P, a.text.strip())
    refresh(P, ws, state)
    print("noté.")


SETTABLE = {"mode": MODES, "stage": STAGES, "programme": PROGRAMMES, "kind": KINDS, "path": PATHS,
            "name": None, "business": None,
            "language": None, "goal": None, "budget_daily": None, "team": None}


# the francophone markets the suite meets most, so « market=CM » is enough (webinar v3, 13/11/2026: markets had to be
# added by editing workspace.yaml by hand)
KNOWN_MARKETS = {
    "CI": ("Côte d'Ivoire", "XOF"), "BJ": ("Bénin", "XOF"), "SN": ("Sénégal", "XOF"), "TG": ("Togo", "XOF"),
    "BF": ("Burkina Faso", "XOF"), "ML": ("Mali", "XOF"), "NE": ("Niger", "XOF"), "GW": ("Guinée-Bissau", "XOF"),
    "CM": ("Cameroun", "XAF"), "GA": ("Gabon", "XAF"), "CG": ("Congo", "XAF"), "TD": ("Tchad", "XAF"),
    "CF": ("Centrafrique", "XAF"), "GQ": ("Guinée équatoriale", "XAF"), "CD": ("RD Congo", "CDF"),
    "GN": ("Guinée", "GNF"), "MA": ("Maroc", "MAD"), "DZ": ("Algérie", "DZD"), "TN": ("Tunisie", "TND"),
    "MG": ("Madagascar", "MGA"), "FR": ("France", "EUR"), "BE": ("Belgique", "EUR"), "CH": ("Suisse", "CHF"),
    "CA": ("Canada", "CAD"),
}


def cmd_set(a):
    P, ws, state = open_ws(a.folder)
    items = a.assignment if isinstance(a.assignment, list) else [a.assignment]
    for it in items:
        if "=" not in it:
            raise WsError(f"« {it} » : format attendu clé=valeur (ex. mode=hybrid), plusieurs séparés par un espace")
    if len(items) > 1:
        for it in items:
            cmd_set(argparse.Namespace(folder=a.folder, assignment=[it]))
        return
    key, val = [x.strip() for x in items[0].split("=", 1)]
    if key in ("market", "markets"):
        mk = ws.setdefault("markets", [])
        for v in [x.strip() for x in val.split(",") if x.strip()]:
            if v.startswith("-"):
                code = v[1:].upper()
                ws["markets"] = mk = [m for m in mk if not (isinstance(m, dict) and m.get("code") == code)]
                journal(P, f"Marché retiré : {code}")
                continue
            m = parse_market(v if ":" in v else v.upper())
            if m["code"] in KNOWN_MARKETS and not m["country"]:
                m["country"], m["currency"] = KNOWN_MARKETS[m["code"]]
            first = next((x for x in mk if isinstance(x, dict)), {})
            if ":" not in v and first.get("payment"):
                m["payment"] = first["payment"]   # same payment as the markets already there
            if any(isinstance(x, dict) and x.get("code") == m["code"] for x in mk):
                print(f"{m['code']} est déjà dans les marchés.")
                continue
            mk.append(m)
            journal(P, f"Marché ajouté : {m['code']} ({m['country'] or '?'})")
        dump_yaml(P["workspace"], ws)
        print(f"Marchés : {', '.join(x.get('code', '?') for x in mk if isinstance(x, dict))}")
        print(refresh(P, ws, state))
        return
    if not key or (not val and key in ("name", "mode", "stage", "programme", "kind", "channels") or key.endswith(".")):
        raise WsError(f"« {items[0]} » : il manque la clé ou la valeur")
    md = modes_data()
    if key.startswith("engines."):
        task = key.split(".", 1)[1]
        if task not in md["tasks"] or val not in md["engines"]:
            raise WsError(f"tâche ou outil inconnu : {task} = {val}. Tâches : {', '.join(md['tasks'])}")
        ws.setdefault("engines", {})[task] = val
    elif key in ("capacity.machine", "capacity.claude"):
        sub = key.split(".", 1)[1]
        if val not in md["capacity"][sub]:
            raise WsError(f"{key} doit être l'un de : {', '.join(md['capacity'][sub])}")
        ws.setdefault("capacity", {})[sub] = val
    elif re.fullmatch(r"(accounts|brand)\.[a-z_]+", key):
        top, sub = key.split(".", 1)
        ws.setdefault(top, {})[sub] = val
    elif key == "channels":
        chans = [c.strip() for c in val.split(",") if c.strip()]
        bad = [c for c in chans if c not in ("meta", "tiktok")]
        if bad or not chans:
            raise WsError("channels : meta, tiktok, ou les deux séparés par une virgule")
        ws["channels"] = chans
    elif key in SETTABLE:
        if SETTABLE[key] and val not in SETTABLE[key]:
            raise WsError(f"{key} doit être l'un de : {', '.join(SETTABLE[key])}")
        ws[key] = val
    else:
        raise WsError(f"clé non modifiable par set : {key}. Un marché : market=CM (market=-CM pour le retirer).")
    dump_yaml(P["workspace"], ws)
    journal(P, f"Réglage : {key} = {val}")
    if key in ("mode",) or key.startswith("engines."):
        state["effective_engines"] = {}
        print("Formule ou outils changés : relance « ws.py doctor <dossier> » pour vérifier cet ordinateur.")
    print(refresh(P, ws, state))


def cmd_repair(a):
    need_yaml()
    P = paths_of(a.folder)
    if not P["workspace"].exists():
        raise WsError(f"pas de workspace.yaml dans {P['root']}")
    ws = load_yaml(P["workspace"], {})
    if not isinstance(ws, dict):
        raise WsError("workspace.yaml n'a pas la bonne forme : restaure workspace.yaml.bak d'abord.")
    P = paths_of(a.folder, ws)
    old = None
    try:
        old = load_yaml(P["state"]) if P["state"].exists() else None
    except WsError:
        old = None
    if not isinstance(old, dict) and P["state"].with_name("state.yaml.bak").exists():
        try:
            old = load_yaml(P["state"].with_name("state.yaml.bak"))
            print("état repris depuis state.yaml.bak")
        except WsError:
            old = None
    state = new_state()
    removed = []
    if isinstance(old, dict):
        for s, info in (old.get("steps") or {}).items() if isinstance(old.get("steps"), dict) else []:
            if s in state["steps"] and isinstance(info, dict) and info.get("status") in STATUSES:
                state["steps"][s] = info
            elif s not in state["steps"]:
                removed.append(s)
        try:
            state["cycle"] = int(old.get("cycle", 1))
        except (TypeError, ValueError):
            pass
        for k, v in (old.get("counters") or {}).items() if isinstance(old.get("counters"), dict) else []:
            if k in state["counters"]:
                try:
                    state["counters"][k] = int(v)
                except (TypeError, ValueError):
                    pass
    cycles = [int(m.group(1)) for d in (P["root"] / "cycles").glob("cycle-*")
              for m in [re.fullmatch(r"cycle-(\d+)", d.name)] if m]
    state["cycle"] = max([state["cycle"]] + cycles)
    found = scan_codes(P, ws)
    state["counters"] = {k: max(state["counters"][k], found[k]) for k in CODE_PREFIXES}
    journal(P, "state.yaml réparé : compteurs recalculés depuis les fichiers"
            + (f", étapes retirées : {', '.join(removed)}" if removed else "") + ".")
    print(refresh(P, ws, state))


# ---------------------------------------------------------------- doctor

PIP = {"yt_dlp": "yt-dlp", "faster_whisper": "faster-whisper", "google.genai": "google-genai",
       "docx": "python-docx", "pymupdf": "pymupdf", "PIL": "pillow", "av": "av", "yaml": "pyyaml",
       "openpyxl": "openpyxl", "imageio_ffmpeg": "imageio-ffmpeg"}


def has_module(name):
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def env_state(name):
    """('process'|'registry'|None, value)."""
    v = os.environ.get(name)
    if v:
        return "process", v
    if WIN and not os.environ.get("CSOS_NO_REGISTRY_KEYS"):   # tests: only the process environment counts
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                return "registry", winreg.QueryValueEx(k, name)[0]
        except OSError:
            pass
    return None, None


def ram_mb():
    fake = os.environ.get("WS_FAKE_RAM")  # test hook: "total,avail"
    if fake:
        t, av = fake.split(",")
        return int(t), int(av)
    try:
        if WIN:
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("l", ctypes.c_ulong), ("load", ctypes.c_ulong), ("total", ctypes.c_ulonglong),
                            ("avail", ctypes.c_ulonglong), ("a", ctypes.c_ulonglong), ("b", ctypes.c_ulonglong),
                            ("c", ctypes.c_ulonglong), ("d", ctypes.c_ulonglong), ("e", ctypes.c_ulonglong)]
            s = MS()
            s.l = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(s))
            return int(s.total // 2 ** 20), int(s.avail // 2 ** 20)
        pages, size = os.sysconf("SC_PHYS_PAGES"), os.sysconf("SC_PAGE_SIZE")
        return int(pages * size // 2 ** 20), int(os.sysconf("SC_AVPHYS_PAGES") * size // 2 ** 20)
    except Exception:
        return None, None


def find_word():
    if not WIN:
        return Path("/Applications/Microsoft Word.app").exists() or None
    for base in (os.environ.get("ProgramFiles", r"C:\Program Files"),
                 os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")):
        for ver in ("root\\Office16", "Office16", "root\\Office15", "Office15"):
            if (Path(base) / "Microsoft Office" / ver / "WINWORD.EXE").exists():
                return True
    return None


def find_soffice():
    if shutil.which("soffice") or shutil.which("libreoffice"):
        return True
    return any(Path(c).exists() for c in (r"C:\Program Files\LibreOffice\program\soffice.exe",
                                           r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
                                           "/Applications/LibreOffice.app/Contents/MacOS/soffice"))


def find_ffmpeg():
    return bool(shutil.which("ffmpeg")) or has_module("imageio_ffmpeg")


def whisper_model_cached(size="small"):
    hub = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface")) / "hub"
    snaps = list((hub / f"models--Systran--faster-whisper-{size}" / "snapshots").glob("*/model.bin"))
    return any(s.exists() and s.stat().st_size > 50_000_000 for s in snaps)


def http_json(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "creative-strategist-doctor"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


KEY_WHERE = {
    "GEMINI_API_KEY": "clé Gemini gratuite (facultative : sans elle, Claude lit les images clés) : aistudio.google.com/apikey, "
                      "connecte-toi avec un compte Google, « Create API key », pas de carte bancaire",
    "APIFY_TOKEN": "jeton Apify : console.apify.com → Settings → API & Integrations (5 $ d'usage offerts chaque mois)",
}


def env_fix(var):
    where = KEY_WHERE.get(var, "crée la clé")
    if WIN:
        return (f"{where} ; puis dans PowerShell : setx {var} \"<ta clé>\" ; ferme et rouvre complètement l'app "
                "Claude pour qu'elle la voie")
    return (f"{where} ; puis ajoute la ligne export {var}=\"<ta clé>\" à ~/.zshrc, quitte et rouvre l'app Claude "
            "(sur Mac, lance-la depuis le Terminal si elle ne voit pas la clé : open -a Claude)")


def check_engine(engine, spec, live, root):
    """Returns (status, problems, fixes, notes, manual). status: ok | missing | manual | unbuilt."""
    needs = spec.get("needs") or {}
    problems, fixes, notes = [], [], []
    prec = needs.get("python_recommended")
    if prec and sys.version_info[:2] < tuple(prec):
        notes.append(f"Python {platform.python_version()} : marche encore, mais les nouvelles versions demandent "
                     f"{prec[0]}.{prec[1]} ou plus. À prévoir : installer Python {prec[0]}.{prec[1]}+ (python.org)")
    missing = [m for m in needs.get("python", []) if not has_module(m)]
    if missing:
        problems.append("paquets Python absents : " + ", ".join(PIP.get(m, m) for m in missing))
        fixes.append(f"{PY} -m pip install " + " ".join(PIP.get(m, m) for m in missing))
    for var in needs.get("env", []):
        where, _ = env_state(var)
        if where is None:
            problems.append(f"clé {var} absente")
            fixes.append(env_fix(var))
        elif where == "registry":
            notes.append(f"clé {var} enregistrée mais pas encore visible par l'app : ferme et rouvre complètement "
                         "l'app Claude")
    if needs.get("ffmpeg") and not find_ffmpeg():
        notes.append("ffmpeg absent : certaines vidéos Instagram peuvent sortir sans le son. "
                     f"Solution : {PY} -m pip install imageio-ffmpeg")
    if needs.get("disk_mb"):
        free = shutil.disk_usage(root if root else Path.home()).free // 2 ** 20
        if free < needs["disk_mb"]:
            problems.append(f"{free} Mo libres sur le disque, il en faut {needs['disk_mb']}")
            fixes.append("libérer de la place sur le disque")
    if engine == "whisper" and has_module("faster_whisper") and not whisper_model_cached("small"):
        notes.append("modèle Whisper « small » pas encore téléchargé : environ 500 Mo au premier usage")
    if needs.get("free_ram_mb"):
        total, avail = ram_mb()
        if avail is not None and avail < needs["free_ram_mb"]:
            notes.append(f"seulement {avail} Mo de mémoire libre ({needs['free_ram_mb']} conseillés) : ferme le "
                         "navigateur et les applications lourdes avant la transcription")
    if engine == "auto" and not find_word() and not find_soffice():
        notes.append("ni Word ni LibreOffice : les documents sortiront en .docx seulement, sans PDF. "
                     "LibreOffice est gratuit : libreoffice.org")
    if live and engine == "gemini" and env_state("GEMINI_API_KEY")[1]:
        try:
            d = http_json("https://generativelanguage.googleapis.com/v1beta/models?key=" + env_state("GEMINI_API_KEY")[1])
            n = len(d.get("models", []))
            notes.append(f"la clé Gemini répond ({n} modèles visibles). Le niveau gratuit, lui, se vérifie au premier "
                         "envoi de vidéo : s'il refuse, l'analyse passe aux images clés")
        except Exception as e:
            problems.append(f"la clé Gemini ne répond pas ({type(e).__name__})")
            fixes.append("vérifie la clé sur aistudio.google.com/apikey")
    if live and engine == "apify" and env_state("APIFY_TOKEN")[1]:
        try:
            d = http_json("https://api.apify.com/v2/users/me?token=" + env_state("APIFY_TOKEN")[1])
            data = d.get("data") or {}
            if not data:
                problems.append("le jeton Apify ne renvoie pas de compte")
            else:
                notes.append(f"Apify répond : compte {data.get('username')}, plan {(data.get('plan') or {}).get('id', '?')}")
        except Exception as e:
            problems.append(f"le jeton Apify ne répond pas ({type(e).__name__})")
            fixes.append("vérifie le jeton dans Apify > Settings > API & Integrations")
    if spec.get("field_tested") is False and spec.get("implemented", True):
        notes.append("branché mais pas encore essayé avec une vraie clé : fais un premier essai sur une seule recherche "
                     "ou une seule référence, et compare avec la voie gratuite")
    if not spec.get("implemented", True):
        status = "unbuilt"
    elif problems:
        status = "missing"
    elif needs.get("manual") and not needs.get("python") and not needs.get("env"):
        status = "manual"
    else:
        status = "ok"
    return status, problems, fixes, notes, needs.get("manual")


def doctor_without_yaml():
    req = HERE.parent / "requirements.txt"
    names = []
    if req.exists():
        for line in req.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                names.append(line)
    mods = {"pyyaml": "yaml", "python-docx": "docx", "pymupdf": "pymupdf", "pillow": "PIL", "av": "av",
            "faster-whisper": "faster_whisper", "yt-dlp": "yt_dlp", "openpyxl": "openpyxl",
            "imageio-ffmpeg": "imageio_ffmpeg"}
    miss = [n for n in names if not has_module(mods.get(n, n))]
    print("Il manque des paquets Python. Installe-les en une fois :")
    print(f"  {PY} -m pip install " + " ".join(miss or ["pyyaml"]))
    print("puis relance doctor.")
    sys.exit(1)


def cmd_doctor(a):
    if yaml is None:
        doctor_without_yaml()
    md = modes_data()
    root, ws, P, state = None, {}, None, None
    if a.folder:
        P0 = paths_of(a.folder)
        if not P0["workspace"].exists():
            raise WsError(f"pas de workspace.yaml dans {P0['root']}. Sans dossier : ws.py doctor --mode free|hybrid|paid")
        P, ws, state = open_ws(a.folder)
        root = P["root"]
    mode = a.mode or ws.get("mode") or "free"
    if mode not in MODES:
        raise WsError(f"formule inconnue « {mode} » ({', '.join(MODES)})")
    eng = dict(md["modes"][mode])
    overrides = ws.get("engines") or {}
    if not a.mode and isinstance(overrides, dict):
        eng.update({k: v for k, v in overrides.items() if k in md["tasks"] and v in md["engines"]})
    cap = ws.get("capacity") if isinstance(ws.get("capacity"), dict) else {}
    total, avail = ram_mb()
    print(f"Formule {mode} · {platform.system()} {platform.version()} · Python {platform.python_version()} · "
          f"{os.cpu_count()} cœurs" + (f" · mémoire {total} Mo ({avail} Mo libres)" if total else ""))
    print(f"Tiers : {md['tiers'][mode]}")
    print()
    icons = {"ok": "✅", "missing": "❌", "manual": "❔", "unbuilt": "🔧"}
    optional = set((md.get("optional") or {}).get(mode) or [])   # a free extra: its absence is not a problem
    blockers, degraded, effective = 0, [], {}
    for task, engine in eng.items():
        spec = md["engines"].get(engine, {})
        status, problems, fixes, notes, manual = check_engine(engine, spec, a.live, root)
        icon = "💡" if status == "missing" and task in optional else icons[status]
        print(f"{icon} {md['tasks'][task]}\n      {spec.get('label', engine)}" + (" (facultatif)" if task in optional else ""))
        if status == "unbuilt":
            print("      pas encore branché dans la suite")
            if problems:
                print("      à préparer pour ce moment-là : " + " ; ".join(fixes or problems))
        else:
            for p in problems:
                print(f"      problème : {p}")
            for f in fixes:
                print(f"      solution : {f}")
        for n in notes:
            print(f"      ⚠️  {n}")
        if manual and status in ("manual", "ok"):
            print(f"      à vérifier à la main : {manual}")
        effective[task] = engine
        if status in ("missing", "unbuilt"):
            alt = None
            for fb in ((md.get("fallbacks") or {}).get(task) or {}).get(engine, []):
                if check_engine(fb, md["engines"][fb], False, root)[0] in ("ok", "manual"):
                    alt = fb
                    break
            if alt:
                if task not in optional:
                    degraded.append(task)
                effective[task] = alt
                print(f"      → utilisé à la place : {md['engines'][alt]['label']}")
            else:
                blockers += 1
    print()
    machine = cap.get("machine", "own-pc")
    if machine == "own-pc":
        thr = md["capacity"]["machine"]["own-pc"]["warn_ram_mb"]
        if total and total < thr:
            print(f"⚠️  Machine : {total} Mo de mémoire au total. Ça marche, mais ferme tout le reste pendant "
                  "les transcriptions, ou passe sur un VPS (capacity.machine=vps).")
        if avail is not None and avail < 1500:   # 195 Mo libres ont figé Chrome deux fois (test du 06/11/2026)
            print(f"⚠️  Mémoire libre : {avail} Mo seulement. Le navigateur peut se figer et Whisper ne pas charger : "
                  "redémarre l'ordinateur ou ferme les applications lourdes avant la recherche (1 500 Mo libres conseillés).")
    else:
        print("❔ Machine : VPS — à vérifier à la main : bureau à distance ouvert, app Claude installée dessus.")
    print(f"❔ Claude : {md['capacity']['claude'][cap.get('claude', 'pro')]['label']} — à vérifier : app Claude ouverte "
          "avec cet abonnement.")
    print()
    if blockers:
        print(f"❌ {blockers} tâche(s) sans aucun outil qui marche : applique les « solution » ci-dessus.")
    elif degraded:
        print(f"🟡 Utilisable. {len(degraded)} tâche(s) tournent sur l'outil de secours au lieu de celui de la formule "
              f"{mode} : {', '.join(md['tasks'][t] for t in degraded)}.")
    else:
        print(f"✅ Prêt pour la formule {mode}. Restent les points ❔ à vérifier à la main.")
    if P is not None and not a.mode:
        state["effective_engines"] = effective
        state["engines_checked_on"] = today()
        refresh(P, ws, state)
        print("Outils réellement utilisés notés dans state.yaml et COMMENCE-ICI.md.")
    sys.exit(1 if blockers else 0)


# ---------------------------------------------------------------- main

class FrParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"ERREUR : commande incomplète ou mal écrite ({message}). Aide : ws.py -h", file=sys.stderr)
        sys.exit(2)


def build_parser():
    ap = FrParser(prog="ws.py", description="Workspace de la suite creative-strategist")
    sub = ap.add_subparsers(dest="cmd", required=True, parser_class=FrParser)

    def add_init(name, default_programme):
        p = sub.add_parser(name)
        p.add_argument("folder")
        p.add_argument("--name", required=True)
        p.add_argument("--business", default="")
        p.add_argument("--mode", choices=MODES, default="free")
        p.add_argument("--stage", choices=STAGES, default="new")
        p.add_argument("--programme", choices=PROGRAMMES, default=default_programme)
        p.add_argument("--kind", choices=KINDS, default="product",
                       help="product (une page, une commande), digital (un produit numérique payé en ligne, accès immédiat) "
                            "ou webinar (un live gratuit, une inscription)")
        p.add_argument("--path", choices=PATHS, default=None,
                       help="full (le premier cycle finit par UN document complet, relié à chaque étape ; par défaut "
                            "pour init) ou stage (un document par étape ; par défaut pour adopt)")
        p.add_argument("--market", action="append", help="CODE:Pays:DEVISE:langue:paiement, ex. GN:Guinée:GNF:fr:cod")
        p.add_argument("--channels", default="meta")
        p.add_argument("--shop", default="")
        p.add_argument("--goal", default="")
        p.add_argument("--budget", default="")
        p.add_argument("--team", default="")

    add_init("init", "none")
    add_init("adopt", None)
    for name in ("status", "next", "check", "repair", "bilan"):
        sub.add_parser(name).add_argument("folder")
    sub.add_parser("overview").add_argument("folder", nargs="?", default=".")
    p = sub.add_parser("cycle")
    p.add_argument("folder")
    p.add_argument("--from", dest="start_from", choices=CYCLE_FROM)
    p.add_argument("--force", action="store_true")
    p = sub.add_parser("doctor")
    p.add_argument("folder", nargs="?")
    p.add_argument("--mode", choices=MODES)
    p.add_argument("--live", action="store_true", help="tester aussi les clés Gemini et Apify en ligne")
    p = sub.add_parser("step")
    p.add_argument("folder")
    p.add_argument("step")
    p.add_argument("status")
    p.add_argument("--output", action="append")
    p.add_argument("--note")
    p = sub.add_parser("start")
    p.add_argument("folder")
    p.add_argument("step")
    p.add_argument("--reason", default="")
    p = sub.add_parser("code")
    p.add_argument("folder")
    p.add_argument("prefix")
    p = sub.add_parser("log")
    p.add_argument("folder")
    p.add_argument("text")
    p = sub.add_parser("team")
    p.add_argument("folder")
    p.add_argument("action", nargs="?", choices=("list", "add", "remove"), default="list")
    p.add_argument("name", nargs="?")
    p.add_argument("--role")
    p.add_argument("--contact")
    p = sub.add_parser("set")
    p.add_argument("folder")
    p.add_argument("assignment", nargs="+", help="clé=valeur, plusieurs séparés par un espace ; market=CM ajoute un marché")
    return ap


def main(argv=None):
    a = build_parser().parse_args(argv)
    cmds = {"init": lambda: cmd_init(a), "adopt": lambda: cmd_init(a, adopt=True), "status": lambda: cmd_status(a),
            "next": lambda: cmd_next(a), "check": lambda: cmd_check(a), "doctor": lambda: cmd_doctor(a),
            "step": lambda: cmd_step(a), "start": lambda: cmd_start(a), "cycle": lambda: cmd_cycle(a),
            "code": lambda: cmd_code(a), "log": lambda: cmd_log(a), "set": lambda: cmd_set(a),
            "repair": lambda: cmd_repair(a), "team": lambda: cmd_team(a), "overview": lambda: cmd_overview(a),
            "bilan": lambda: cmd_bilan(a)}
    try:
        cmds[a.cmd]()
    except WsError as e:
        print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(2)
    except PermissionError as e:
        print(f"ERREUR : fichier verrouillé ({Path(str(e.filename or '')).name or 'inconnu'}) : ferme-le dans les "
              "autres programmes (Word, OneDrive, antivirus) et relance.", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"ERREUR : accès au disque impossible ({e.strerror or e}) pour {e.filename or 'un fichier'}.",
              file=sys.stderr)
        sys.exit(2)
    except Exception as e:  # last resort: one line, never a traceback
        print(f"ERREUR inattendue ({type(e).__name__} : {e}). Lance « ws.py check <dossier> » puis, si besoin, "
              "« ws.py repair <dossier> ».", file=sys.stderr)
        if os.environ.get("WS_DEBUG"):
            raise
        sys.exit(3)


if __name__ == "__main__":
    main()
