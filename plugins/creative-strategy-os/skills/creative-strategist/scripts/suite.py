"""suite.py in the licensed edition: updates come with the plugin.

    python suite.py version     prints the installed version
"""
import sys
from pathlib import Path

VERSION = (Path(__file__).resolve().parents[1] / "VERSION").read_text().strip()

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "version"
    if cmd == "version":
        print(f"Creative Strategy OS {VERSION} (édition sous licence, plugin)")
    else:
        print("Dans l'édition sous licence, les mises à jour passent par le plugin : dans Claude, tape "
              "/plugin puis mets à jour « creative-strategy-os ». Rien à installer à la main.")
