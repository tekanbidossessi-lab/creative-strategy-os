"""pagefacts.py : this command runs on the Creative Strategy OS licence server.

Only the helpers other scripts of the plugin borrow are here (unescape_json_text)."""
import sys
from pathlib import Path
import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

def unescape_json_text(t):
    return t.replace('\\"', '"').replace('\\/', '/')

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "creative-strategist" / "scripts"))
    import csos_client
    sys.exit(csos_client.forward(__file__, sys.argv[1:]))
