"""offer.py : this command runs on the Creative Strategy OS licence server.

Same usage as always (python offer.py <commande> <dossier> ...). The text files of the product folder are sent to the
server with the licence key, the result comes back here. See csos_client.py for exactly what is sent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "creative-strategist" / "scripts"))
import csos_client  # noqa: E402

if __name__ == "__main__":
    sys.exit(csos_client.forward(__file__, sys.argv[1:]))
