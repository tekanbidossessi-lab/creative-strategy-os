#!/bin/bash
# setup_linux.sh — prepares a Linux machine for the Creative Strategy OS (the twin of setup_mac.sh), 1.7.2.
#
#   bash setup_linux.sh --check     only says what is there and what is missing
#   bash setup_linux.sh             installs what is missing, then checks again
#
# Written 24/11/2026 after a buyer's Claude session ran on a temporary Linux machine in the cloud: the Mac and Windows
# scripts didn't apply, the packages were installed by hand, and Whisper failed on every video. Installs (only when
# missing, with apt when it is there): Python 3.11+, ffmpeg, LibreOffice (the PDF), then the Python packages of
# requirements.txt. Never touches existing data.
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

report() {
  echo ""
  echo "Ce que cette machine a :"
  if [ "$HOME" = "/home/user" ] || [ -n "$CLAUDE_CODE_REMOTE" ]; then
    echo "  [!!]   Machine temporaire dans le cloud : tes fichiers ne sont pas sur ton ordinateur."
    echo "         -> pour travailler sur ton PC : application Claude, onglet Code, nouvelle session, « Local »"
  fi
  PY=$(find_python)
  if [ -n "$PY" ]; then say 1 "Python 3.11 ou plus récent ($PY)"; else say 0 "Python 3.11 ou plus récent" "sudo apt install python3 python3-pip"; fi
  if [ -n "$PY" ]; then
    MISSING=$("$PY" -c "import importlib.util as u;print(' '.join(m for m in ['yaml','docx','pymupdf','PIL','av','openpyxl','faster_whisper','yt_dlp','imageio_ffmpeg','google.genai'] if not u.find_spec(m)))" 2>/dev/null)
    if [ -z "$MISSING" ]; then say 1 "Paquets Python de la suite"; else say 0 "Paquets Python de la suite" "manquants : $MISSING"; fi
  fi
  if command -v ffmpeg >/dev/null 2>&1; then say 1 "ffmpeg (le son des vidéos)"; else say 0 "ffmpeg" "sudo apt install ffmpeg (sinon celui d'imageio-ffmpeg sert)"; fi
  if command -v soffice >/dev/null 2>&1 || command -v libreoffice >/dev/null 2>&1; then say 1 "LibreOffice (les PDF)"; else say 0 "LibreOffice (les PDF)" "sudo apt install libreoffice-writer"; fi
  if [ -n "$GEMINI_API_KEY" ]; then say 1 "Clé Gemini (facultative)"; else
    say 0 "Clé Gemini gratuite (facultative : toutes les références analysées)" "aistudio.google.com/apikey, puis export GEMINI_API_KEY=\"<ta clé>\" dans ~/.bashrc"; fi
  RAM=$(( $(awk '/MemTotal/{print $2}' /proc/meminfo 2>/dev/null || echo 0) / 1048576 ))
  if [ "$RAM" -ge 8 ]; then say 1 "Mémoire : $RAM Go"; else say 0 "Mémoire : $RAM Go" "8 Go conseillés pour Whisper"; fi
  FREE=$(df -BG "$HOME" 2>/dev/null | awk 'NR==2{gsub("G","",$4);print $4}')
  if [ -n "$FREE" ] && [ "$FREE" -ge 10 ]; then say 1 "Espace libre : $FREE Go"; else say 0 "Espace libre : ${FREE:-?} Go" "10 Go au moins (vidéos de référence, modèle Whisper)"; fi
  echo ""
}

if [ "$1" = "--check" ]; then report; exit 0; fi

echo "Installation de ce qui manque…"
SUDO=""; [ "$(id -u)" != "0" ] && command -v sudo >/dev/null 2>&1 && SUDO="sudo"
if command -v apt-get >/dev/null 2>&1; then
  PKGS=""
  [ -z "$(find_python)" ] && PKGS="$PKGS python3 python3-pip"
  command -v ffmpeg >/dev/null 2>&1 || PKGS="$PKGS ffmpeg"
  { command -v soffice >/dev/null 2>&1 || command -v libreoffice >/dev/null 2>&1; } || PKGS="$PKGS libreoffice-writer"
  if [ -n "$PKGS" ]; then $SUDO apt-get update -qq && $SUDO apt-get install -y -qq $PKGS; fi
fi
PY=$(find_python)
if [ -n "$PY" ] && [ -f "$REQ" ]; then
  FLAG=""; "$PY" -m pip install --help 2>/dev/null | grep -q "break-system-packages" && FLAG="--break-system-packages"
  "$PY" -m pip install -q --upgrade pip $FLAG --user 2>/dev/null || "$PY" -m pip install -q --upgrade pip $FLAG
  "$PY" -m pip install -q -r "$REQ" $FLAG --user 2>/dev/null || "$PY" -m pip install -q -r "$REQ" $FLAG
fi
report
echo "Ensuite, dans un dossier produit :"
echo "  $PY \"$HOME/.claude/skills/creative-strategist/scripts/ws.py\" doctor <dossier>"
