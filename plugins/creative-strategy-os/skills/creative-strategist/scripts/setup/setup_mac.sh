#!/bin/bash
# setup_mac.sh — prepares a Mac for the Creative Strategy OS (the twin of setup_windows.ps1).
#
#   bash setup_mac.sh --check     only says what is there and what is missing
#   bash setup_mac.sh             installs what is missing, then checks again
#
# Installs (only when missing): Python 3.11+ (Homebrew when present, otherwise the python.org installer is opened),
# Google Chrome and LibreOffice when Word is absent (Homebrew casks), the Python packages of requirements.txt (ffmpeg
# comes with imageio-ffmpeg). Never touches existing data. The Claude app is installed by hand (claude.ai/download).
# Written 31/10/2026 from the Windows script; not yet run on a real Mac: run --check first and read what it says.
HERE="$(cd "$(dirname "$0")" && pwd)"
REQ="$(dirname "$(dirname "$HERE")")/requirements.txt"

say() { if [ "$1" = "1" ]; then printf "  [ok]   %s\n" "$2"; else printf "  [--]   %s\n" "$2"; [ -n "$3" ] && printf "         -> %s\n" "$3"; fi; }

find_python() {
  for c in python3.13 python3.12 python3.11 python3; do
    if command -v "$c" >/dev/null 2>&1; then
      v=$("$c" -c 'import sys;print(sys.version_info[1])' 2>/dev/null)
      if [ -n "$v" ] && [ "$v" -ge 11 ]; then echo "$c"; return; fi
    fi
  done
}
has_app() { [ -d "/Applications/$1.app" ] || [ -d "$HOME/Applications/$1.app" ]; }

report() {
  echo ""
  echo "Ce que ce Mac a :"
  PY=$(find_python)
  if [ -n "$PY" ]; then say 1 "Python 3.11 ou plus récent ($PY)"; else say 0 "Python 3.11 ou plus récent" "python.org/downloads (le programme d'installation pour macOS)"; fi
  if [ -n "$PY" ]; then
    MISSING=$("$PY" -c "import importlib.util as u;print(' '.join(m for m in ['yaml','docx','pymupdf','PIL','av','openpyxl','faster_whisper','yt_dlp','imageio_ffmpeg','google.genai'] if not u.find_spec(m)))" 2>/dev/null)
    if [ -z "$MISSING" ]; then say 1 "Paquets Python de la suite"; else say 0 "Paquets Python de la suite" "manquants : $MISSING"; fi
  fi
  if has_app "Google Chrome"; then say 1 "Google Chrome (recherches, Claude in Chrome)"; else say 0 "Google Chrome" "google.com/chrome"; fi
  echo "  [??]   Claude in Chrome (l'extension) : à vérifier à la main"
  echo "         -> claude.ai/chrome, « Ajouter à Chrome », connecte-toi avec ton compte Claude, puis connecte ce Chrome à Facebook, Instagram et TikTok"
  if [ -n "$GEMINI_API_KEY" ] || grep -q GEMINI_API_KEY "$HOME/.zshrc" 2>/dev/null; then say 1 "Clé Gemini (facultative)"; else
    say 0 "Clé Gemini gratuite (facultative : toutes les références analysées)" "aistudio.google.com/apikey, puis ajoute export GEMINI_API_KEY=\"<ta clé>\" à ~/.zshrc"; fi
  if has_app "Microsoft Word" || has_app "LibreOffice"; then say 1 "Word ou LibreOffice (les PDF)"; else say 0 "Word ou LibreOffice (les PDF)" "libreoffice.org (gratuit)"; fi
  if [ -f "$HOME/.claude/skills/creative-strategist/VERSION" ]; then say 1 "Les skills de la suite (version $(head -1 "$HOME/.claude/skills/creative-strategist/VERSION"))"; else
    say 0 "Les skills de la suite" "suite.py install <zip> (voir le guide d'installation)"; fi
  RAM=$(( $(sysctl -n hw.memsize 2>/dev/null || echo 0) / 1073741824 ))
  if [ "$RAM" -ge 8 ]; then say 1 "Mémoire : $RAM Go"; else say 0 "Mémoire : $RAM Go" "8 Go conseillés pour Whisper"; fi
  FREE=$(df -g "$HOME" 2>/dev/null | awk 'NR==2{print $4}')
  if [ -n "$FREE" ] && [ "$FREE" -ge 10 ]; then say 1 "Espace libre : $FREE Go"; else say 0 "Espace libre : ${FREE:-?} Go" "10 Go au moins (vidéos de référence, modèle Whisper)"; fi
  echo ""
}

if [ "$1" = "--check" ]; then report; exit 0; fi

echo "Installation de ce qui manque…"
BREW=$(command -v brew)
if [ -z "$(find_python)" ]; then
  if [ -n "$BREW" ]; then brew install python@3.11
  else echo "  Python : le site python.org s'ouvre ; installe la version pour macOS, puis relance ce script."; open "https://www.python.org/downloads/macos/"; exit 0; fi
fi
if ! has_app "Google Chrome"; then
  if [ -n "$BREW" ]; then brew install --cask google-chrome; else open "https://www.google.com/chrome/"; fi
fi
if ! has_app "Microsoft Word" && ! has_app "LibreOffice"; then
  if [ -n "$BREW" ]; then brew install --cask libreoffice; else echo "  LibreOffice : libreoffice.org (les PDF) ; sans lui, seulement les .docx."; fi
fi
PY=$(find_python)
if [ -n "$PY" ] && [ -f "$REQ" ]; then
  "$PY" -m pip install --upgrade pip --user
  "$PY" -m pip install -r "$REQ" --user
fi
report
echo "Ensuite : installe l'app Claude (claude.ai/download), connecte-toi, puis dans un dossier produit :"
echo "  $PY \"$HOME/.claude/skills/creative-strategist/scripts/ws.py\" doctor <dossier>"
