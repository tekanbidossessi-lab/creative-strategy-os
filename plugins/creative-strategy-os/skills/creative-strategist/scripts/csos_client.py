"""Creative Strategy OS, licence client (runs on the buyer's computer).

What it does, and nothing else:
- keeps the buyer's licence key in ~/.csos/licence.json (the buyer types it once: `csos.py licence set <clé>`);
- computes a device id (a hash of this computer's name and user, never sent in clear);
- for a command of the suite's core, sends to the licence server: the key, the device id, the command, and the TEXT
  files of the product folder named in the command (yaml, md, json, csv, txt, srt, vtt, html). To build a Word
  document (docs.py), also the reference images that document shows, reduced. Never videos, passwords, API keys, or
  anything outside the product folder and the files named in the command;
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
PLUGIN_VERSION = "1.9.0"                                  # replaced at build time by build_plugin.py
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


def in_cloud():
    """True when Claude Code runs on a temporary cloud machine (a « cloud » session of the Claude app or claude.ai)
    instead of the buyer's computer. 24/11/2026: a buyer worked a whole evening in one without knowing; his files
    lived in /home/user and had to be zipped back to him."""
    if str(os.environ.get("CLAUDE_CODE_REMOTE") or "").lower() in ("1", "true", "yes"):
        return True
    if os.environ.get("CLAUDE_CODE_REMOTE_ENVIRONMENT_TYPE") or os.environ.get("CLAUDE_CODE_REMOTE_SESSION_ID"):
        return True
    return platform.system() == "Linux" and not os.environ.get("DISPLAY") and (
        str(Path.home()) == "/home/user" or platform.node() in ("vm", "runsc", "sandbox"))


CLOUD_TEXT = (
    "la suite ne marche pas dans une session cloud (machine temporaire, loin de ton ordinateur). Dans l'application "
    "Claude, onglet Code, ouvre une nouvelle session, choisis ton ordinateur (« Local ») et ton dossier. Si tu as déjà "
    "du travail ici, demande à Claude un zip du dossier avant de fermer.")


def refuse_cloud():
    """1.8.0 (Richie, 24/11/2026): no cloud sessions, refused before the licence is touched."""
    if in_cloud():
        raise LicenceError(CLOUD_TEXT)


# ---------- 1.8.0: local commands need a valid key too ----------
GATE_TTL = 1800
_forwarded = False


def _gate_tag(key):
    return hashlib.sha256(f"{key}|{device_id()}|{PLUGIN_VERSION}|{server_url()}".encode("utf-8")).hexdigest()[:24]


def gate():
    """A valid licence, checked on the server at most every 30 minutes."""
    import time
    refuse_cloud()
    key = licence_key()
    conf = load_conf()
    g = conf.get("gate") if isinstance(conf.get("gate"), dict) else {}
    if g.get("tag") == _gate_tag(key) and 0 <= time.time() - float(g.get("t") or 0) < GATE_TTL:
        return
    call("/v1/licence", {"key": key, "device": device_id(), "plugin_version": PLUGIN_VERSION})
    gate_ok(key)


def gate_ok(key):
    import time
    conf = load_conf()
    conf["gate"] = {"tag": _gate_tag(key), "t": time.time()}
    try:
        save_conf(conf)
    except OSError:
        pass


class _Tee:
    """Shows everything and keeps the last lines, for the report of a local failure."""

    def __init__(self, stream):
        self.stream, self.tail = stream, ""

    def write(self, text):
        self.tail = (self.tail + str(text))[-4000:]
        return self.stream.write(text)

    def __getattr__(self, name):
        return getattr(self.stream, name)


def run_local(script_file, main):
    """Run a command that stays on this computer: the key is checked first, and a failure becomes a finding (with the
    buyer's yes), kept in an outbox until the server can be reached."""
    try:
        gate()
    except LicenceError as e:
        print(f"LICENCE : {e}", file=sys.stderr)
        return 4
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    out, err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = _Tee(out), _Tee(err)
    code, crash = 0, ""
    try:
        code = main() or 0
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
    except Exception:
        import traceback
        crash = traceback.format_exc()
        err.write(crash)
        code = 3
    finally:
        said = sys.stdout.tail + sys.stderr.tail + crash
        sys.stdout, sys.stderr = out, err
    if not _forwarded:
        bad = [ln.strip() for ln in said.splitlines() if any(m in ln for m in ("ERREUR", "échec (", "Traceback", "Error"))]
        if code not in (0, 4) or bad:
            queue_failure(script_file, code, bad or said.strip().splitlines()[-3:])
        flush_outbox()
    return code


OUTBOX = CONF_DIR / "outbox.json"


def queue_failure(script_file, code, lines):
    if not findings_on():
        return
    try:
        box = json.loads(OUTBOX.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        box = []
    args = [a for a in sys.argv[1:]]
    folder = next((a for a in args if Path(a).is_dir()), None)
    shown = " ".join("<dossier>" if a == folder else a for a in args)
    box.append({"text": f"Commande locale en échec (code {code}) : {Path(script_file).name} {shown}\n" +
                        "\n".join(lines[:12]), "folder": str(Path(folder).resolve()) if folder else None,
                "step": Path(script_file).resolve().parent.parent.name.replace("cs-", "")})
    try:
        CONF_DIR.mkdir(parents=True, exist_ok=True)
        OUTBOX.write_text(json.dumps(box[-20:], ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def flush_outbox():
    """Send the failures kept on this computer; what doesn't leave stays for the next command."""
    if not findings_on() or not OUTBOX.exists():
        return
    try:
        box = json.loads(OUTBOX.read_text(encoding="utf-8"))
        left = list(box)
        for x in box:
            note(x["text"], x.get("folder") if Path(x.get("folder") or "?").is_dir() else str(CONF_DIR), "claude", x.get("step"))
            left.pop(0)
            OUTBOX.write_text(json.dumps(left, ensure_ascii=False), encoding="utf-8")
        OUTBOX.unlink()
    except Exception:
        pass   # offline, refused: kept


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


def _claude_cli():
    """The claude command: on the PATH, or the one the desktop app ships (Windows: %LOCALAPPDATA%\Claude-Data)."""
    import glob
    import shutil as _sh
    found = _sh.which("claude")
    if found:
        return found
    roots = [os.environ.get("LOCALAPPDATA") or "", str(Path.home() / "Library" / "Application Support")]
    hits = []
    for r in roots:
        if r:
            hits += glob.glob(os.path.join(r, "Claude-Data", "*", "claude-code", "*", "*", "claude*"))
    hits = [h for h in hits if os.path.basename(h).lower() in ("claude", "claude.exe")]
    return sorted(hits, key=os.path.getmtime)[-1] if hits else ""


def self_update():
    """1.9.0: refresh the marketplace and update the plugin, the way /plugin would; Claude applies it on restart."""
    import subprocess
    cli, ok = _claude_cli(), False
    if cli:
        try:
            subprocess.run([cli, "plugin", "marketplace", "update", "creative-strategy-os"], capture_output=True,
                           timeout=120, stdin=subprocess.DEVNULL)
            r = subprocess.run([cli, "plugin", "update", "creative-strategy-os@creative-strategy-os"],
                               capture_output=True, timeout=180, stdin=subprocess.DEVNULL)
            ok = r.returncode == 0
        except (OSError, subprocess.SubprocessError):
            ok = False
    if not ok:   # at least the marketplace copy, which Claude reads at its next start
        conf = Path(os.environ.get("CLAUDE_CONFIG_DIR") or (Path.home() / ".claude"))
        mk = conf / "plugins" / "marketplaces" / "creative-strategy-os"
        if (mk / ".git").exists():
            try:
                subprocess.run(["git", "-C", str(mk), "pull", "--ff-only", "-q"], capture_output=True, timeout=120,
                               stdin=subprocess.DEVNULL)
            except (OSError, subprocess.SubprocessError):
                pass
    return ("La nouvelle version est téléchargée : ferme complètement Claude, rouvre-le, puis écris « on continue »."
            if ok else "")


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
    # 1.9.0: every request says the plugin's version (the server refuses an old plugin, and a request without one)
    payload = dict(payload, cloud=in_cloud())
    payload.setdefault("plugin_version", PLUGIN_VERSION)
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
        if e.code == 426:   # 1.9.0: too old to work; update ourselves, then the buyer restarts Claude
            done = self_update()
            raise LicenceError((msg or "mise à jour nécessaire.") + ("\n" + done if done else ""))
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


MEDIA_NAMES_MAX = 4000


def names_only(root):
    """The paths of the product folder's videos and pictures: the client's own ads (mes-pubs/) and every downloaded
    reference, frame or contact sheet. Only their names leave this computer, never their content: the server's checks
    (« le fichier de CL01 n'est pas là ») and the export reading need to know the file is there. 1.9.0: before, only
    mes-pubs/ was named, so the strategy check refused references the buyer had downloaded (Geovani, 25/11/2026)."""
    out, root = [], Path(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", "node_modules", ".venv")]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() not in TEXT_EXT and not fn.startswith("."):
                out.append(p.relative_to(root).as_posix())
                if len(out) >= MEDIA_NAMES_MAX:
                    return out
    return out


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


WRITTEN = []


def forward(script_file, argv, extra_files=None):
    """Run one core command on the licence server. Returns the command's exit code."""
    global _forwarded
    _forwarded = True
    del WRITTEN[:]
    script = Path(script_file).resolve()
    rel = f"{script.parent.parent.name}/scripts/{script.name}"
    try:
        refuse_cloud()
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
                   "files": dict(pack_dir(ws) if ws else {}, **(extra_files or {})), "placeholders": names_only(ws) if ws else [],
                   "inputs": inputs, "client": "1", "plugin_version": PLUGIN_VERSION,
                   "findings": findings_on(), "session": session_id()}
        ensure_auto_update()
        print(version_line(), file=sys.stderr, flush=True)
        before = digest(ws) if ws else {}
        res = call("/v1/run", payload)
        gate_ok(key)
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
                try:
                    dest.write_bytes(data)
                except PermissionError:
                    print(f"ERREUR : {dest.name} est ouvert (Word ou lecteur PDF) : ferme-le et relance.", file=sys.stderr)
                    return 2
                WRITTEN.append(dest)
        for relp in res.get("deleted") or []:
            dest = (ws / relp).resolve()
            # the server only ever had the text files; a video or picture here is the buyer's, never removed
            if ws in dest.parents and dest.exists() and dest.is_file() and dest.suffix.lower() in TEXT_EXT:
                dest.unlink()
    if res.get("notice"):
        print(res["notice"], file=sys.stderr)
    flush_outbox()
    return int(res.get("code", 0))


# ---------- 1.8.0: the Word documents are built on the server; the PDF is made here, by Word or LibreOffice ----------
IMG_REF = __import__("re").compile(r"[(\"']([^()\"'\n]+\.(?:jpe?g|png|webp|gif|bmp))[)\"']", 2)
MAX_IMAGES = 20 * 1024 * 1024


def document_images(ws):
    """The images the deliverables show, reduced to 1000 px: nothing else leaves the References folder."""
    import io
    out, total, src = {}, 0, ws / "deliverables"
    for md in sorted(src.glob("*.md")) if src.exists() else []:
        for ref in IMG_REF.findall(md.read_text(encoding="utf-8", errors="replace")):
            p = Path(ref) if Path(ref).is_absolute() else src / ref
            try:
                p = p.resolve()
                rel = p.relative_to(ws).as_posix()
                if rel in out or not p.is_file():
                    continue
                data = p.read_bytes()
            except (OSError, ValueError):
                continue
            try:
                from PIL import Image
                with Image.open(io.BytesIO(data)) as im:
                    im = im.convert("RGB")
                    im.thumbnail((1000, 1000))
                    buf = io.BytesIO()
                    im.save(buf, "JPEG", quality=80)
                    data = min(data, buf.getvalue(), key=len)
            except Exception:
                pass
            total += len(data)
            if total > MAX_IMAGES:
                print("  (trop d'images : les dernières ne sont pas dans le document)", file=sys.stderr)
                return out
            out[rel] = base64.b64encode(data).decode("ascii")
    return out


def forward_docs(script_file, argv, to_pdf):
    global _forwarded
    _forwarded = True
    _, ws = find_workspace(argv)
    extra = {}
    if ws is not None and "--outline" not in argv:
        extra = document_images(ws)
        mark = ws / "deliverables" / "word" / ".book-cycle"
        if mark.is_file():
            extra["deliverables/word/.book-cycle"] = {"text": mark.read_text(encoding="utf-8", errors="replace")}
            if "--book" in argv:   # a new strategy: the previous document is kept, renamed (the server never has it)
                try:
                    import yaml
                    cycle = int((yaml.safe_load((ws / "state.yaml").read_text(encoding="utf-8")) or {}).get("cycle") or 1)
                    old = int(mark.read_text(encoding="utf-8").strip())
                    if old != cycle:
                        for f in list(mark.parent.glob("STRATEGIE-CREATIVE.*")) + list(mark.parent.glob("CREATIVE-STRATEGY.*")):
                            f.replace(f.with_name(f"{f.stem}-cycle-{old:02d}{f.suffix}"))
                            print(f"Version du cycle {old} gardée : {f.stem}-cycle-{old:02d}{f.suffix}")
                except PermissionError as e:
                    print(f"ERREUR : {Path(str(e.filename)).name} est ouvert : ferme-le et relance.", file=sys.stderr)
                    return 2
                except Exception:
                    pass
    want_pdf = "--no-pdf" not in argv and "--outline" not in argv
    code = forward(script_file, list(argv) + (["--no-pdf"] if want_pdf else []), extra)
    if code == 0 and want_pdf:
        for d in [x for x in WRITTEN if x.suffix.lower() == ".docx"]:
            try:
                pdf = to_pdf(d)
            except Exception as e:
                print(f"  {e}", file=sys.stderr)
                continue
            print(f"PDF : {pdf}" if pdf else "  pas de PDF : ni Word ni LibreOffice sur cet ordinateur (ws.py doctor)")
    return code


def guide(skill, name):
    refuse_cloud()
    res = call("/v1/guide", {"key": licence_key(), "device": device_id(), "skill": skill, "name": name})
    return res.get("text", "")


def status():
    ensure_auto_update()
    refuse_cloud()
    return call("/v1/licence", {"key": licence_key(), "device": device_id(), "plugin_version": PLUGIN_VERSION})


# ---------- 1.4.9: findings shared with Richie, only with the buyer's yes ----------
FINDINGS_TEXT = (
    "Aide à améliorer Creative Strategy OS (recommandé) : comme dans une application, la suite envoie des rapports "
    "d'utilisation et d'erreurs, pour que chaque bug soit corrigé vite et que chaque nouvelle version te donne de "
    "meilleurs résultats. Un rapport contient la commande lancée, son résultat, les erreurs, et les repères de ton "
    "produit (nom, marché, étape). Jamais tes vidéos, tes clés ni tes mots de passe. Tu peux l'arrêter quand tu veux.")


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
        print("\n" + FINDINGS_TEXT + "\nPour activer : python csos.py licence findings on   ·   pour refuser : "
              "python csos.py licence findings off\n(Claude : pose la question une fois, simplement, comme une "
              "application : « Pour que la suite s'améliore et te donne de meilleurs résultats au fil des versions, "
              "j'active l'envoi des rapports d'amélioration ? C'est recommandé, et rien de personnel n'est envoyé. » "
              "Puis lance la commande qu'il choisit.)", file=sys.stderr, flush=True)
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
