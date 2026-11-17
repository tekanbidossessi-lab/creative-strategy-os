"""Creative Strategy OS, licence commands.

    python csos.py licence set <clé>      enregistre ta clé de licence sur cet ordinateur (une fois)
    python csos.py licence status         dit si ta licence est active, jusqu'à quand, et combien d'ordinateurs restent
    python csos.py licence forget         retire la clé de cet ordinateur
    python csos.py licence findings on|off|status   partage (ou non) les constats d'usage avec Richie
    python csos.py retour "<texte>" [--dossier D]  envoie ton retour à Richie (avec le partage activé)
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
            print(C.version_line())
            print(st.get("message", "Licence active."))
            if st.get("update"):
                print(st["update"])
            return 0
        if argv[1] == "findings":
            choice = argv[2] if len(argv) >= 3 else "status"
            if choice in ("on", "off"):
                C.set_findings(choice == "on")
                print("Partage des constats activé. Merci : Richie lira chacun d'eux pour améliorer la suite."
                      if choice == "on" else "Partage des constats désactivé. Rien n'est plus envoyé à Richie.")
                return 0
            print(C.FINDINGS_TEXT)
            print("État : " + ("activé" if C.findings_on() else "désactivé"))
            return 0
        if argv[1] == "forget":
            conf = C.load_conf()
            conf.pop("key", None)
            C.save_conf(conf)
            print("Clé retirée de cet ordinateur.")
            return 0
    if len(argv) >= 2 and argv[0] == "retour":   # retour "<texte>" [--dossier D] [--claude] [--etape read]
        words, folder, by, step, i = [], None, "buyer", None, 1
        while i < len(argv):
            if argv[i] == "--dossier" and i + 1 < len(argv):
                folder, i = argv[i + 1], i + 2
            elif argv[i] == "--etape" and i + 1 < len(argv):
                step, i = argv[i + 1], i + 2
            elif argv[i] == "--claude":
                by, i = "claude", i + 1
            else:
                words.append(argv[i])
                i += 1
        try:
            print(C.note(" ".join(words), folder, by, step))
        except C.LicenceError as e:
            print(f"LICENCE : {e}")
            return 4
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
