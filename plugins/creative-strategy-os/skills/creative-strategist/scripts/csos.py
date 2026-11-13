"""Creative Strategy OS, licence commands.

    python csos.py licence set <clé>      enregistre ta clé de licence sur cet ordinateur (une fois)
    python csos.py licence status         dit si ta licence est active, jusqu'à quand, et combien d'ordinateurs restent
    python csos.py licence forget         retire la clé de cet ordinateur
    python csos.py guide <skill> <fiche>  affiche une fiche de méthode (ex. : guide cs-strategy avatars)
    python csos.py guide <skill>          liste les fiches de ce skill

Les fiches de méthode ne sont pas dans le plugin : elles sont servies par le serveur de licence, à jour, au nom de ta
licence. Une licence vaut pour 2 ordinateurs.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import csos_client as C  # noqa: E402


def main(argv):
    if len(argv) >= 2 and argv[0] == "licence":
        if argv[1] == "set" and len(argv) >= 3:
            conf = C.load_conf()
            conf["key"] = argv[2].strip()
            C.save_conf(conf)
            try:
                st = C.status()
            except C.LicenceError as e:
                print(f"Clé enregistrée, mais le serveur la refuse : {e}")
                return 4
            print(f"Licence active. {st.get('message', '')}".strip())
            return 0
        if argv[1] == "status":
            try:
                st = C.status()
            except C.LicenceError as e:
                print(f"LICENCE : {e}")
                return 4
            print(st.get("message", "Licence active."))
            return 0
        if argv[1] == "forget":
            conf = C.load_conf()
            conf.pop("key", None)
            C.save_conf(conf)
            print("Clé retirée de cet ordinateur.")
            return 0
    if len(argv) >= 2 and argv[0] == "guide":
        try:
            print(C.guide(argv[1], argv[2] if len(argv) > 2 else ""))
        except C.LicenceError as e:
            print(f"LICENCE : {e}")
            return 4
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
