"""Creative Strategy OS, licence client (runs on the buyer's computer).

What it does, and nothing else:
- keeps the buyer's licence key in ~/.csos/licence.json (the buyer types it once: `csos.py licence set <clé>`);
- computes a device id (a hash of this computer's name and user, never sent in clear);
- for a command of the suite's core, sends to the licence server: the key, the device id, the command, and the TEXT
  files of the product folder named in the command (yaml, md, json, csv, txt, srt, vtt, html). Never videos, images,
  passwords, API keys, or anything outside the product folder and the files named in the command;
- writes back the files the server changed in that folder, and prints what the command printed.

Everything here is visible to the buyer on purpose: the only lock is the licence key, checked on the server.
"""
import base64
import gzip
import hashlib
import json
import os
import platform
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_SERVER = "https://csos-licence.onrender.com"   # replaced at build time by build_plugin.py
PLUGIN_VERSION = "1.7.1"                                  # replaced at build time by build_plugin.py
MARKETPLACE = "creative-strategy-os"
MARKETPLACE_URL = "https://github.com/tekanbidossessi-lab/creative-strategy-os.git"
CONF_DIR = Path(os.environ.get("CSOS_HOME") or (Path.home() / ".csos"))
CONF = CONF_DIR / "licence.json"
TEXT_EXT = {".yaml", ".yml", ".md", ".json", ".jsonl", ".csv", ".tsv", ".txt", ".srt", ".vtt", ".html", ".htm"}
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "media", "videos", "frames"}
MAX_FILE = 40 * 1024 * 1024      # one text file of the product folder (a big candidates.yaml is 6 Mo)
MAX_TOTAL = 150 * 1024 * 1024    # all of them, before compression
TIMEOUT = 600
CRLF, LF, BACKSLASH = chr(13) + chr(10), chr(10), chr(92)


class LicenceError(Exception):
    pass


# ---------- configuration ----------
def load_conf():
    try:
        return json.loads(CONF.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_conf(conf):
    CONF_DIR.mkdir(parents=True, exist_ok=True)
    CONF.write_text(json.dumps(conf, indent=2, ensure_ascii=False), encoding="utf-8")


def server_url():
    return (os.environ.get("CSOS_SERVER") or load_conf().get("server") or DEFAULT_SERVER).rstrip("/")


def licence_key():
    key = os.environ.get("CSOS_LICENCE") or load_conf().get("key")
    if not key:
        raise LicenceError("aucune licence enregistrée sur cet ordinateur. Tape : python csos.py licence set <ta clé> "
                           "(la clé est dans l'e-mail de Chariow après l'achat).")
    return key.strip()


def device_id():
    raw = f"{platform.node()}|{os.environ.get('USERNAME') or os.environ.get('USER') or ''}|{platform.system()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


# ---------- updates (1.4.7) ----------
def ensure_auto_update():
    """Claude Code leaves auto-update off for every marketplace that isn't Anthropic's, so a buyer who never opens
    /plugin stays on the version he installed. Turn it on once, in the documented place (autoUpdate on the
    marketplace's extraKnownMarketplaces entry of the user's Claude settings), and say so. A value the buyer set
    himself (true or false, e.g. with /plugin, Marketplaces, Disable auto-update) is never touched."""
    if PLUGIN_VERSION == "dev" or os.environ.get("CSOS_NO_AUTO_UPDATE"):
        return
    home = Path(os.environ.get("CLAUDE_CONFIG_DIR") or (Path.home() / ".claude"))
    path = home / "settings.json"
    try:
        settings = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        if not isinstance(settings, dict):
            return
        markets = settings.setdefault("extraKnownMarketplaces", {})
        entry = markets.setdefault(MARKETPLACE, {"source": {"source": "git", "url": MARKETPLACE_URL}})
        if not isinstance(entry, dict) or "autoUpdate" in entry:
            return
        entry["autoUpdate"] = True
        tmp = path.with_suffix(".json.csos-tmp")
        tmp.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, path)
        print("Creative Strategy OS : mises à jour automatiques activées (chaque nouvelle version s'installe seule au "
              "démarrage de Claude). Pour les couper : /plugin, Marketplaces, creative-strategy-os, Disable "
              "auto-update.", file=sys.stderr)
    except (OSError, ValueError):
        pass   # never block a command over this


def version_line():
    return f"Creative Strategy OS {PLUGIN_VERSION}"


# ---------- transport ----------
def call(path, payload):
    """The free server sleeps after 15 minutes; while it wakes, Render answers 502/503/504 for up to a minute. Audit
    15/11/2026: retry three times, 20 s apart, instead of failing the buyer's first command."""
    import time
    for attempt in range(4):
        try:
            return _call(path, payload)
        except _Waking:
            if attempt == 0:
                print("Le serveur de licence se réveille (jusqu'à une minute la première fois)…", flush=True)
            time.sleep(20)
    raise LicenceError("le serveur de licence ne s'est pas réveillé : relance la commande dans une minute.")


class _Waking(Exception):
    pass


def _call(path, payload):
    body = gzip.compress(json.dumps(payload).encode("utf-8"), 6)   # text squeezes 5 to 10 times: light on mobile data
    req = urllib.request.Request(server_url() + path, data=body, headers={
        "Content-Type": "application/json", "Content-Encoding": "gzip", "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            raw = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            raw = e.read()
            if e.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            msg = json.loads(raw.decode("utf-8")).get("error")
        except Exception:
            msg = None
        # 17/11/2026: a 503 that carries the server's own message (Chariow key refused, Chariow down) is not a server
        # waking up: say it, instead of retrying a minute and blaming the wake-up
        if e.code in (502, 503, 504) and not msg:
            raise _Waking()
        raise LicenceError(msg or f"le serveur de licence a répondu {e.code}.")
    except (urllib.error.URLError, TimeoutError, OSError):
        raise LicenceError("le serveur de licence est injoignable (pas de réseau ?). Les commandes locales "
                           "(télécharger, transcrire, images clés, contrôle vidéo, Word/PDF) marchent sans réseau ; "
                           "relance celle-ci quand tu as du réseau.")


# ---------- what is sent ----------
def find_workspace(argv):
    for i, a in enumerate(argv):
        if a.startswith("-"):
            continue
        p = Path(a)
        try:
            if p.is_dir():
                for d in [p.resolve(), *p.resolve().parents]:
                    if (d / "workspace.yaml").exists():
                        return i, d
                    if d.parent == d:
                        break
            elif p.is_file() and p.name == "workspace.yaml":
                return i, p.resolve().parent
        except OSError:
            continue
    return None, None


def pack_dir(root):
    files, total = {}, 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() not in TEXT_EXT:
                continue
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size > MAX_FILE:
                raise LicenceError(f"{p.relative_to(root)} pèse plus de 40 Mo : sors-le du dossier produit et relance.")
            total += size
            if total > MAX_TOTAL:
                raise LicenceError("le dossier produit pèse trop lourd en texte (plus de 150 Mo) : range les gros "
                                   "fichiers hors du dossier et relance.")
            data = p.read_bytes()
            try:
                files[p.relative_to(root).as_posix()] = {"text": data.decode("utf-8")}
            except UnicodeDecodeError:
                files[p.relative_to(root).as_posix()] = base64.b64encode(data).decode("ascii")
    return files


NAMES_ONLY = ("mes-pubs",)   # folders whose files go to the server by name only (the client's own videos)


def names_only(root):
    """The paths of the files in mes-pubs/ (the client's current ads, named like in Ads Manager). Only their names
    leave this computer, never their content: the server reads the export against these names."""
    out = []
    for top in NAMES_ONLY:
        d = Path(root) / top
        if d.is_dir():
            out += [p.relative_to(root).as_posix() for p in sorted(d.rglob("*"))
                    if p.is_file() and p.suffix.lower() not in TEXT_EXT]
    return out[:500]


def unpack(value):
    return value["text"].encode("utf-8") if isinstance(value, dict) else base64.b64decode(value)


def digest(root):
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                out[p.relative_to(root).as_posix()] = hashlib.sha1(p.read_bytes()).hexdigest()
            except OSError:
                pass
    return out


def forward(script_file, argv):
    """Run one core command on the licence server. Returns the command's exit code."""
    script = Path(script_file).resolve()
    rel = f"{script.parent.parent.name}/scripts/{script.name}"
    try:
        key = licence_key()
        idx, ws = find_workspace(argv)
        args, inputs = list(argv), {}
        for i, a in enumerate(argv):
            if i == idx or a.startswith("-"):
                continue
            p = Path(a)
            try:
                is_file = p.is_file()
            except OSError:
                is_file = False
            if is_file and (ws is None or ws not in p.resolve().parents):
                if p.stat().st_size > MAX_FILE:
                    raise LicenceError(f"{p.name} est trop gros pour être envoyé (plus de 40 Mo).")
                inputs[p.name] = base64.b64encode(p.read_bytes()).decode("ascii")
                args[i] = "{IN}/" + p.name
            elif is_file and ws is not None:
                args[i] = "{WS}/" + p.resolve().relative_to(ws).as_posix()
        if idx is not None:
            sub = Path(argv[idx]).resolve().relative_to(ws).as_posix() if Path(argv[idx]).is_dir() else ""
            args[idx] = "{WS}" + ("/" + sub if sub and sub != "." else "")
        payload = {"key": key, "device": device_id(), "script": rel, "argv": args,
                   "files": pack_dir(ws) if ws else {}, "placeholders": names_only(ws) if ws else [],
                   "inputs": inputs, "client": "1", "plugin_version": PLUGIN_VERSION,
                   "findings": findings_on(), "session": session_id()}
        ensure_auto_update()
        print(version_line(), file=sys.stderr, flush=True)
        before = digest(ws) if ws else {}
        res = call("/v1/run", payload)
        ask_findings_once()
    except LicenceError as e:
        print(f"LICENCE : {e}", file=sys.stderr)
        return 4
    # the server ran in its own temporary folder: put this computer's paths back in what it printed and wrote
    sp = res.get("paths") or {}
    pairs = []
    for name in inputs:
        for sep in ("/", BACKSLASH):
            pairs.append((sp.get("in", "\0") + sep + name, str(Path([a for a in argv if Path(a).name == name][0])
                                                                .resolve())))
    if ws:
        pairs.append((sp.get("ws", "\0"), str(ws)))
    pairs.append((sp.get("suite", "\0"), str(script.parents[2])))
    pairs = [(a, b) for a, b in pairs if a and a != "\0"]
    pairs += [(a.replace(BACKSLASH, BACKSLASH * 2), b.replace(BACKSLASH, BACKSLASH * 2)) for a, b in pairs
              if BACKSLASH in a]

    def localize(text):
        for a, b in pairs:
            text = text.replace(a, b)
        return text

    if res.get("stdout"):
        sys.stdout.write(localize(res["stdout"]).replace(CRLF, LF))
    if res.get("stderr"):
        sys.stderr.write(localize(res["stderr"]).replace(CRLF, LF))
    if ws:
        for relp, value in (res.get("files") or {}).items():
            dest = (ws / relp).resolve()
            if ws not in dest.parents:
                continue   # the server never writes outside the product folder
            dest.parent.mkdir(parents=True, exist_ok=True)
            data = unpack(value)
            if dest.suffix.lower() in TEXT_EXT:
                try:
                    data = localize(data.decode("utf-8")).encode("utf-8")
                except UnicodeDecodeError:
                    pass
            if before.get(relp) != hashlib.sha1(data).hexdigest():
                dest.write_bytes(data)
        for relp in res.get("deleted") or []:
            dest = (ws / relp).resolve()
            if ws in dest.parents and dest.exists() and dest.is_file():
                dest.unlink()
    if res.get("notice"):
        print(res["notice"], file=sys.stderr)
    return int(res.get("code", 0))


def guide(skill, name):
    res = call("/v1/guide", {"key": licence_key(), "device": device_id(), "skill": skill, "name": name})
    return res.get("text", "")


def status():
    ensure_auto_update()
    return call("/v1/licence", {"key": licence_key(), "device": device_id(), "plugin_version": PLUGIN_VERSION})


# ---------- 1.4.9: findings shared with Richie, only with the buyer's yes ----------
FINDINGS_TEXT = (
    "Partage des constats avec Richie (facultatif) : à chaque commande, la suite lui envoie la commande, son résultat, "
    "les erreurs et avertissements, ce qu'elle a affiché, et les faits du produit (nom, ce qui est vendu, marché, mode, "
    "étapes, repères du compte). Jamais tes vidéos, tes clés ni tes mots de passe. Richie lit chaque constat lui-même "
    "pour corriger et améliorer la suite. Tu peux arrêter à tout moment.")


def findings_on():
    return load_conf().get("findings") is True


def set_findings(on):
    conf = load_conf()
    conf["findings"] = bool(on)
    conf["findings_asked"] = True
    save_conf(conf)


def session_id():
    """One work session = commands less than 3 hours apart on this computer."""
    import time
    import uuid
    conf = load_conf()
    s = conf.get("session") if isinstance(conf.get("session"), dict) else {}
    now = int(time.time())
    if not s.get("id") or now - int(s.get("last") or 0) > 3 * 3600:
        s = {"id": time.strftime("%Y-%m-%d", time.localtime(now)) + "-" + uuid.uuid4().hex[:6]}
    s["last"] = now
    conf["session"] = s
    try:
        save_conf(conf)
    except OSError:
        pass
    return s["id"]


def ask_findings_once():
    conf = load_conf()
    if conf.get("findings") is None and not conf.get("findings_asked"):
        print("\n" + FINDINGS_TEXT + "\nPour accepter : python csos.py licence findings on   ·   pour refuser : "
              "python csos.py licence findings off\n(Claude : pose la question une fois à l'utilisateur, en une phrase, "
              "puis lance la commande qu'il choisit.)", file=sys.stderr, flush=True)
        conf["findings_asked"] = True
        try:
            save_conf(conf)
        except OSError:
            pass


def note(text, folder=None, by="buyer", step=None):
    """A buyer's own words, or Claude's note of the session, sent as one finding."""
    if not findings_on():
        raise LicenceError("le partage des constats est désactivé. Pour l'activer : python csos.py licence findings on")
    files = {}
    root = Path(folder).resolve() if folder else None
    if root is None:
        cur = Path.cwd().resolve()
        root = next((d for d in (cur, *cur.parents) if (d / "workspace.yaml").exists()), None)
    if root is not None:
        for rel in ("workspace.yaml", "state.yaml", "library/benchmarks.yaml"):
            f = root / rel
            if f.is_file() and f.stat().st_size < 200_000:
                files[rel] = {"text": f.read_text(encoding="utf-8", errors="replace")}
    res = call("/v1/finding", {"key": licence_key(), "device": device_id(), "plugin_version": PLUGIN_VERSION,
                               "findings": True, "session": session_id(), "text": str(text)[:4000], "by": by,
                               "step": step or "", "files": files})
    return res.get("message", "")
