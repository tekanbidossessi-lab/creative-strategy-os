# -*- coding: utf-8 -*-
"""docs.py — the suite's deliverables as Word and PDF.

    python docs.py <dossier> --book [--no-pdf]                 # the strategy document, in one piece
    python docs.py <dossier> [LANCEMENT LECTURE …] [--no-pdf]   # one document per deliverable

--book binds the deliverables of a cycle — FICHE-ENTREE, OFFRE, RECHERCHE, STRATEGIE, BRIEFS — into one document the
client reads from start to end: a cover, a clickable table of contents (Word, PDF bookmarks, the outline of Google
Docs), a « Commence ici » page, each part opening on its own title page, one creative per page, and the machine checks
grouped in an appendix. Launch, results and iteration come weeks later and stay one document each.

Layout: A4, Calibri, the suite's own colours (deep blue, green), never the agency's print kit. A client's brand in
workspace.yaml → brand (primary_color, accent_color) replaces the colours. Every page carries one line: the tool that
made the document and how to reach its author. Language: workspace.yaml → language (fr, en).
The PDF comes from Word when it is installed (fields updated, bookmarks from the headings), otherwise from LibreOffice,
otherwise there is only the .docx (ws.py doctor says which). Out: deliverables/word/.
Markdown read: # ## ### #### titles, paragraphs, - and 1. lists, - [ ] checkboxes, | tables |, > callouts, ![](images),
``` blocks (messages to copy), --- (a new page), **bold**, *italic*, [text](https://…) and bare links (clickable).
In BRIEFS, bold inside the script table is red.
"""
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ws as W  # noqa: E402
from ws import WsError, open_ws, journal, read_text  # noqa: E402

SUITE = {"primary": "17324D", "accent": "12A27A"}
SHADE = "F2F5F7"
RED = "C0161D"
CONTACT = "Richie Tekan · WhatsApp +229 01 97 61 14 25"
TEXT = {
    "fr": {"signature": f"Créé avec Creative Strategy OS · par {CONTACT}",
           "kind": "Stratégie créative", "book": "STRATEGIE-CREATIVE", "toc": "Sommaire", "cycle": "cycle",
           "start": "Commence ici", "appendix": "Annexe", "checks": "Les vérifications",
           "checks_lead": "Chaque règle que la machine sait vérifier, partie par partie. ✅ tenue · ⚠️ à revoir · "
                          "❌ à corriger · ❔ à vérifier toi-même.",
           "parts": {"FICHE-ENTREE": ("Le point de départ", "Le produit, l'offre, ce qu'une commande peut coûter en pub, "
                                      "le suivi des ventes."),
                     "OFFRE": ("L'offre et la page", "Ce que vendent les concurrents, l'offre proposée, la page section "
                               "par section, le texte de la pub, l'appel de confirmation."),
                     "RECHERCHE": ("La recherche", "Les pubs et les vidéos qui ont déjà vendu ou retenu, ce qu'on en a "
                                   "tiré, et les mots des clients."),
                     "STRATEGIE": ("La stratégie", "À qui on parle, avec quels angles, et le système des créatives "
                                   "à tester."),
                     "BRIEFS": ("Les briefs", "Une créative par page : de quoi la produire seul, sans poser de "
                                "question.")},
           "how": ["Ce document est ta stratégie créative, de la première lecture du produit jusqu'aux briefs. "
                   "Lis-le dans l'ordre une première fois ; ensuite, sers-toi du sommaire (clique sur une ligne pour y "
                   "aller).",
                   "Chaque partie ouvre sur sa propre page. Les références citées ont leur lien : clique pour voir la "
                   "pub, la vidéo ou la page du concurrent toi-même."],
           "now_t": "Ce que tu fais maintenant",
           "now": ["Produis les créatives, une par une, à partir de leur brief (partie Les briefs). Chaque brief "
                   "donne deux routes : générée avec l'IA, ou montée à partir de clips si tu manques de crédits.",
                   "Nomme chaque fichier livré avec le code de sa créative (exemple : C01 V1 A.mp4).",
                   "Envoie les créatives produites dans la conversation avec Claude : il les contrôle (cs-review) "
                   "avant que quoi que ce soit parte en ligne."],
           "next_t": "Ce qui vient après",
           "next": ["Le lancement : un document de campagne construit sur les créatives que tu as vraiment "
                    "produites, avec le système de noms et le texte commun de la pub.",
                    "La lecture des résultats après 7 jours : Claude te dira exactement quel export du Gestionnaire "
                    "de publicités lui envoyer.",
                    "L'itération : on garde ce qui a gagné et on change une chose à la fois."],
           "draft": {"tag": "version de travail · {n} partie(s) sur 5",
                     "how": "Ce document est ta stratégie créative. Il grandit à chaque étape : cette version contient "
                            "{n} partie(s) sur 5. C'est toujours le même fichier, complété à chaque étape jusqu'aux "
                            "briefs : la nouvelle version remplace l'ancienne.",
                     "now": ["Lis les parties déjà faites. Si quelque chose ne colle pas à ton produit ou à tes clients, "
                             "dis-le à Claude : rien n'est figé.",
                             "Dis à Claude « on continue » : la prochaine partie est « {next} ».",
                             "Ne produis encore aucune vidéo : les briefs, une créative par page, arrivent dans la "
                             "dernière partie."],
                     "after": "Puis, avec le document complet : la production, le contrôle de chaque vidéo, le "
                              "lancement, la lecture des résultats et les variations."}},
    "en": {"signature": f"Made with Creative Strategy OS · by {CONTACT}",
           "kind": "Creative strategy", "book": "CREATIVE-STRATEGY", "toc": "Contents", "cycle": "cycle",
           "start": "Start here", "appendix": "Appendix", "checks": "The checks",
           "checks_lead": "Every rule the machine can check, part by part. ✅ met · ⚠️ to review · ❌ to fix · "
                          "❔ check it yourself.",
           "parts": {"FICHE-ENTREE": ("The starting point", "The product, the offer, what one order may cost in ads, "
                                      "sales tracking."),
                     "OFFRE": ("The offer and the page", "What competitors sell, the proposed offer, the page section "
                               "by section, the ad text, the confirmation call."),
                     "RECHERCHE": ("The research", "The ads and videos that already sold or held attention, what we "
                                   "took from them, and the customers' words."),
                     "STRATEGIE": ("The strategy", "Who we speak to, with which angles, and the system of creatives "
                                   "to test."),
                     "BRIEFS": ("The briefs", "One creative per page: everything to produce it alone, without asking "
                                "a question.")},
           "how": ["This document is your creative strategy, from the first read of the product to the briefs. Read "
                   "it in order once; then use the contents (click a line to jump there).",
                   "Each part opens on its own page. Every reference has its link: click to see the ad, the video or "
                   "the competitor's page yourself."],
           "now_t": "What you do now",
           "now": ["Produce the creatives one by one from their brief (part The briefs). Each brief gives two "
                   "routes: generated with AI, or edited from clips if you run short of credits.",
                   "Name each delivered file with its creative's code (example: C01 V1 A.mp4).",
                   "Send the produced creatives in the conversation with Claude: it checks them (cs-review) before "
                   "anything goes live."],
           "next_t": "What comes next",
           "next": ["The launch: a campaign document built on the creatives you actually produced, with the naming "
                    "system and the shared ad text.",
                    "Reading the results after 7 days: Claude will tell you exactly which Ads Manager export to send.",
                    "Iteration: keep what won and change one thing at a time."],
           "draft": {"tag": "working version · {n} of 5 parts",
                     "how": "This document is your creative strategy. It grows at each step: this version holds {n} "
                            "of 5 parts. It is always the same file, completed at each step up to the briefs: the new "
                            "version replaces the old one.",
                     "now": ["Read the parts already done. If something doesn't fit your product or your customers, "
                             "tell Claude: nothing is set in stone.",
                             "Tell Claude « let's continue »: the next part is « {next} ».",
                             "Don't produce any video yet: the briefs, one creative per page, come in the last part."],
                     "after": "Then, with the complete document: production, the check of every video, the launch, "
                              "reading the results and the variations."}},
}
BOOK_PARTS = ("FICHE-ENTREE", "OFFRE", "RECHERCHE", "STRATEGIE", "BRIEFS")

# 1.7 (22/11/2026): a book read only as the suite's checkpoints was refused. Each part opens on what it is for, in the
# reader's words; the tool's marks go; the mini-course and an appendix written in sentences close the book.
PURPOSE = {
    "FICHE-ENTREE": "Poser les faits avant de parler de pub : ce que tu vends, à quel prix, par quel chemin l'argent "
                    "arrive, combien une {result} peut coûter en publicité, et si le suivi des achats marche.",
    "OFFRE": "Comparer ton offre à celles qui vendent déjà sur ton marché, dire ce qu'on change sur la page, et donner "
             "le texte qui accompagne chaque pub.",
    "OFFRE_quiz": "Comparer ton offre à celles qui vendent déjà sur ton marché, montrer le quiz écran par écran (c'est "
                  "lui qui vend), et donner le texte qui accompagne chaque pub.",
    "RECHERCHE": "Montrer ce qui marche déjà sur ton marché : comment on a cherché, les pubs qui tournent depuis "
                 "longtemps, ce qu'elles ont en commun, et les mots de tes clients, tels qu'ils les écrivent.",
    "STRATEGIE": "Dire à qui on parle, avec quels angles, et pourquoi ces dix vidéos-là : les avatars, le choix des "
                 "trois testés, le système des vidéos, le test et ce qu'on fera des gagnantes.",
    "BRIEFS": "Donner, pour chaque vidéo, tout ce qu'il faut pour la produire seul à 23 h : son rôle dans le test, ce "
              "qu'il faut produire, le script à côté de la référence, la production plan par plan.",
}
PURPOSE.update({
    "PRODUCTION": "Suivre la fabrication des vidéos : qui produit quoi, pour quand, ce qui est livré et ce qui est en "
                  "retard.",
    "CONTROLE": "Vérifier chaque vidéo produite avant qu'un franc de pub ne soit dépensé dessus : l'ouverture, les mots, "
                "la fin, le son, le format. Une vidéo à reprendre dit exactement quoi corriger.",
    "LANCEMENT": "Mettre la campagne de test en ligne sans te tromper : la structure, les noms, le budget, le texte de "
                 "chaque pub, et ce qu'il faut regarder pendant les sept premiers jours.",
    "LECTURE": "Lire les résultats du test et décider pour chaque pub : la garder, la couper, la corriger ou la décliner, "
               "avec la raison écrite à côté de chaque décision.",
    "GAGNANTS": "Garder la mémoire de ce qui a gagné, cycle après cycle : ce qui compose chaque gagnante et ce qu'on "
                "change ensuite pour la faire durer.",
    "VARIATIONS": "Préparer le cycle suivant : les déclinaisons des gagnantes, chacune avec la seule chose qu'elle "
                  "change, et les nouvelles idées.",
    "MONTAGE": "Monter chaque vidéo toi-même à partir de clips : l'ouverture plan par plan, puis le reste à ton choix.",
    "BILAN": "Voir l'histoire du produit d'un coup d'œil : ce que chaque cycle a testé, ce qui a gagné, et les repères "
             "de ton compte.",
    "CONCURRENTS": "Voir ce que vendent les concurrents, à quel prix, avec quelles promesses, et depuis combien de temps "
                   "leurs pubs tournent.",
    "PAGE": "Écrire la page à partir d'une page qui vend déjà, section par section, avec chaque changement montré.",
    "TENDANCE": "Voir comment ton compte évolue, deux semaines par deux semaines : ce qui s'use, où les acheteurs "
                "décrochent, et combien de temps vit une gagnante.",
})
RESULT_WORD = {"product": ("commande", "commandes"), "digital": ("vente", "ventes"), "webinar": ("inscription", "inscriptions")}
STATE_WORD = {"✅": "tenu", "🟡": "à revoir", "⚠️": "à revoir", "🔴": "à corriger", "❌": "à corriger", "⬜": "à vérifier",
              "❔": "à vérifier", "➖": "sans objet"}
# what speaks to the tool, not to the reader: the status marks, rule codes, commands, file names, skill names
_MARKS = re.compile(r"[🟡🔴✅⬜❔➖🟢]|⚠️|❌")
_RULES = re.compile(r"\s*\((?:R\d+[a-z]?(?:\s*[,/et]+\s*R\d+[a-z]?)*(?:\s*:[^)]*)?)\)|\bR\d+[a-z]?\s*:\s*")
_TOOLISH = (r"[\w./-]*\.(?:py|ya?ml|json|md|js)\b|\bcs-(?:intake|offer|research|strategy|briefs|review|launch|read|iterate)\b|"
            r"\bcreative-strategist\b|\breferences/[\w./-]+|\blibrary/[\w./-]+|\bdeliverables/[\w./-]+|--[a-z][\w-]*")
_PAREN_TOOL = re.compile(r"\s*\((?:[^()]*?(?:" + _TOOLISH + r"))[^()]*\)")
_CODE_TOOL = re.compile(r"`[^`]*(?:" + _TOOLISH + r"|\b(?:ws|docs|research|strategy|briefs|offer|intake|launch|read|review|iterate)"
                        r"\.py\b)[^`]*`")
_OTHER_KIND = {"digital": re.compile(r"livraison|livreur|colis|\bGNF\b|formulaire à la livraison|appel de confirmation", re.I)}
CHECKLIST = re.compile(r"^(la liste de contr[ôo]le|the checklist of checks|checks)$", re.I)


def std_jpeg(p):
    """The image as python-docx can read it. Some frames written by ffmpeg are refused by python-docx (22/11/2026):
    those are saved again as a standard JPEG next to a temp folder, and that copy goes into the document."""
    p = Path(p)
    try:
        from docx.image.image import Image as _DocxImage
        _DocxImage.from_file(str(p))
        return str(p)
    except Exception:  # noqa: BLE001 — anything python-docx refuses gets a standard copy
        pass
    try:
        import tempfile
        from PIL import Image
        out = Path(tempfile.gettempdir()) / "csos-images" / (p.stem + "-std.jpg")
        out.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(p) as im:
            im.convert("RGB").save(out, "JPEG", quality=88)
        return str(out)
    except Exception:  # noqa: BLE001 — the caller writes « image illisible »
        return str(p)


BARE_FILES = {"product.yaml": "la fiche du produit", "workspace.yaml": "les réglages du produit",
              "library/competitors.yaml": "les pages des concurrents", "library/voice": "les mots des clients",
              "library/quiz.yaml": "la description du quiz", "strategy.yaml": "la stratégie"}


def reader_text(t):
    """A line for the reader: the tool's marks, rule codes, commands and file names taken out (1.7)."""
    t = str(t)
    lead = re.match(r"^\s*(✅|🟡|⚠️|🔴|❌|⬜|❔|➖)\s*", t)
    state = STATE_WORD.get(lead.group(1)) if lead else None
    for k, v in BARE_FILES.items():
        t = t.replace(k, v)
    t = _CODE_TOOL.sub("", t)
    t = _PAREN_TOOL.sub("", t)
    # a command or a capture script named in the open (« research.py paste », « browser/fb_comments.js »)
    t = re.sub(r"\b(?:[\w/-]+\.js|[a-z_]+\.py(?: [a-z-]+)?)\b", "l'outil de la suite", t)
    t = _RULES.sub(" ", t)
    t = _MARKS.sub("", t)
    t = re.sub(r"\s+([,.)])", r"\1", re.sub(r"\(\s*\)", "", t))   # French keeps its space before ; and :
    t = re.sub(r"[ \t]{2,}", " ", t).strip()
    if state and state not in ("tenu", "sans objet") and t:
        t = re.sub(r"^(\*\*[^*]+?)(\.?)\*\*", lambda m: f"{m.group(1)}** ({state}){m.group(2)}", t, count=1) \
            if t.startswith("**") else f"({state}) {t}"
    return t


def reader_blocks(blocks, ws=None):
    """The blocks of a book part, for the reader: every text cleaned; in « À faire » and « Ensuite », the lines that
    belong to another kind of product (a delivery for a digital product) dropped."""
    kind = str((ws or {}).get("kind") or "product")
    other = _OTHER_KIND.get(kind)
    out, in_todo = [], False
    for k, x in blocks:
        if k == "h":
            lvl, txt = x[0], x[1]
            in_todo = bool(re.match(r"(à faire|ensuite)", txt.strip(), re.I))
            out.append(("h", (lvl, reader_text(txt)) + tuple(x[2:])))
        elif k in ("p", "ul", "ul2", "ol", "check"):
            if in_todo and other and other.search(str(x)):
                continue
            t = reader_text(x)
            if t:
                out.append((k, t))
        elif k == "quote":
            out.append((k, [reader_text(y) for y in x if reader_text(y)]))
        elif k == "table":
            out.append((k, [reader_text(row) if not re.match(r"^\|[\s:|-]+\|?$", row.strip()) else row for row in x]))
        else:
            out.append((k, x))
    return out


def kind_block(text, ws):
    """A bookparts text for this workspace: the quiz or page lines kept by destination, the kind's words put in."""
    dest = str((ws or {}).get("destination") or "page")
    for tag in ("quiz", "page"):
        keep = dest == tag
        text = re.sub(r"<!-- " + tag + r" -->\n?(.*?)<!-- /" + tag + r" -->\n?", (lambda m: m.group(1)) if keep else "",
                      text, flags=re.S)
    text = re.sub(r"<!--.*?-->\n?", "", text, flags=re.S)
    one, many = RESULT_WORD.get(str((ws or {}).get("kind") or "product"), RESULT_WORD["product"])
    return text.replace("{results}", many).replace("{result}", one)


def purpose_block(part, ws, label="À quoi sert cette partie"):
    one, _ = RESULT_WORD.get(str((ws or {}).get("kind") or "product"), RESULT_WORD["product"])
    key = part + "_quiz" if part == "OFFRE" and (ws or {}).get("destination") == "quiz" else part
    txt = PURPOSE.get(key) or PURPOSE.get(part)
    return [("quote", [f"**{label}** : {txt.replace('{result}', one)}"])] if txt else []


def course_blocks(ws):
    """The part « Le mini-cours » (bookparts.MINI_COURS), its own title line left out."""
    import bookparts
    b = parse(kind_block(bookparts.MINI_COURS, ws))
    return [x for x in b if not (x[0] == "h" and x[1][0] == 1)]


def checks_sentences(checks):
    """A checklist section as sentences: (blocks, open points). What holds is summed up; what stays open is listed
    with its state in words (à revoir, à corriger, à vérifier)."""
    ok, todo = [], []
    for k, x in checks:
        if k not in ("ul", "ol", "check", "p"):
            continue
        raw = str(x)
        lead = re.match(r"^\s*(✅|🟡|⚠️|🔴|❌|⬜|❔|➖)", raw)
        state = STATE_WORD.get(lead.group(1)) if lead else None
        label = re.sub(r"\*\*", "", reader_text(re.sub(r"^\s*(✅|🟡|⚠️|🔴|❌|⬜|❔|➖)\s*", "", raw)))
        label = re.sub(r"\s*\((?:à revoir|à corriger|à vérifier)\)", "", label)
        if not label or state == "sans objet":
            continue
        (ok if state == "tenu" else todo).append((state or "à vérifier", label))
    pl = lambda n, w: f"{n} {w}{'s' if n > 1 else ''}"
    sent = []
    if ok:
        sent.append(f"{pl(len(ok), 'point')} vérifié{'s' if len(ok) > 1 else ''} et tenu{'s' if len(ok) > 1 else ''}, "
                    "notamment : " + " ; ".join(l.split(" — ")[0].rstrip(".") for _, l in ok[:4]) + ".")
    if todo:
        sent.append(f"{pl(len(todo), 'point')} reste{'nt' if len(todo) > 1 else ''} ouvert{'s' if len(todo) > 1 else ''} :")
    out = [("p", " ".join(sent) or "Rien à signaler.")] + [("ul", f"{l.rstrip('.')} ({st}).") for st, l in todo]
    return out, todo


def annex_blocks(appendix, P, ws):
    """The appendix in sentences (1.7): per part, what was checked and holds, what stays open; then the points to
    decide, how to read the codes, the sources and the glossary."""
    import bookparts
    out, open_points = [], []
    out.append(("p", "Avant de te livrer ce document, chaque partie a été relue point par point. Voici, partie par "
                     "partie, ce qui a été vérifié, comment, et ce qui reste ouvert."))
    for ptitle, checks in appendix:
        blocks, todo = checks_sentences(checks)
        out += [("h", (2, ptitle))] + blocks
        open_points += [(ptitle, st, l) for st, l in todo]
    if open_points:
        out += [("h", (2, "Les points à trancher")),
                ("p", "Ces points demandent une décision ou une vérification de ta part avant le lancement. Chacun dit "
                      "dans quelle partie il se trouve.")]
        out += [("ul", f"**{pt}** : {l.rstrip('.')} ({st}).") for pt, st, l in open_points[:20]]
    out += [("h", (2, "Comment lire les codes")),
            ("p", "Chaque vidéo a un code. **C01** est la première idée du cycle ; **V1** est sa première version ; **A** est "
                  "sa première ouverture (B et C sont d'autres ouvertures du même corps). « C01 V1 A » est donc le nom du "
                  "fichier et de la pub dans le Gestionnaire de publicités. Les références de la recherche ont aussi un "
                  "code : **AL** pour une pub de la Bibliothèque publicitaire de Meta, **TT** pour une vidéo TikTok, **IG** "
                  "pour Instagram, **YT** pour YouTube, **CL** pour une pub à toi, **CO** pour un concurrent.")]
    n_refs = 0
    try:
        data = W.load_yaml(P["refs_index"], {}) or {}
        n_refs = len([r for r in data.get("references") or [] if isinstance(r, dict)])
    except Exception:  # noqa: BLE001 — no references file, no count
        pass
    out += [("h", (2, "Les sources")),
            ("p", ("Ce document repose sur " + (f"{n_refs} pubs et vidéos de référence, " if n_refs else "")
                   + "chacune avec son lien dans la partie La recherche, sur la page de ton produit lue telle qu'elle est en "
                     "ligne, sur les pages des concurrents, et sur les commentaires de clients recopiés avec leurs fautes. "
                     "Chaque chiffre cité dit d'où il vient."))]
    gl = parse(kind_block(bookparts.GLOSSAIRE, ws))
    out += [("h", (2, "Le glossaire"))] + [x for x in gl if not (x[0] == "h" and x[1][0] == 1)]
    return out


def brand_of(ws):
    b = ws.get("brand") if isinstance(ws.get("brand"), dict) else {}
    hexok = lambda v: bool(re.fullmatch(r"#?[0-9A-Fa-f]{6}", str(v or "")))
    return {"name": b.get("name") or "",
            "primary": (str(b["primary_color"]).lstrip("#") if hexok(b.get("primary_color")) else SUITE["primary"]).upper(),
            "accent": (str(b["accent_color"]).lstrip("#") if hexok(b.get("accent_color")) else SUITE["accent"]).upper()}


def lang_of(ws):
    return "en" if str(ws.get("language") or "fr").lower().startswith("en") else "fr"


# ------------------------------------------------------------------ Markdown → blocks

def parse(text):
    """Markdown → a list of blocks: (kind, payload). Kinds: h (level, text), p, ul, ol, check, table, quote, code,
    img, break."""
    lines = text.replace("\r\n", "\n").split("\n")
    out, para, i = [], [], 0

    def item(first):
        """A list item and its wrapped lines (indented, not a new item): one paragraph, not one per source line."""
        nonlocal i
        parts = [first]
        while i + 1 < len(lines) and lines[i + 1][:1] in (" ", "\t") and lines[i + 1].strip() \
                and not re.match(r"^([-*]|\d+\.)\s|^\|", lines[i + 1].strip()):
            i += 1
            parts.append(lines[i].strip())
        return " ".join(parts)

    def flush():
        if para:
            out.append(("p", " ".join(x.strip() for x in para)))
            para.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("```"):
            flush()
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            out.append(("code", block))
        elif re.match(r"^#{1,4}\s", s):
            flush()
            lvl = len(s) - len(s.lstrip("#"))
            out.append(("h", (lvl, re.sub(r"\*\*|\*", "", s[lvl:].strip()))))
        elif s.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(("table", rows))
            continue
        elif s.startswith(">"):
            flush()
            box = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                box.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append(("quote", [b for b in box if b]))
            continue
        elif re.match(r"^!\[", s):
            flush()
            out.append(("img", [(m.group(2), m.group(1)) for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", s)]))
        elif re.match(r"^- \[[ xX]\]\s", s):
            flush()
            out.append(("check", item(s[6:])))
        elif re.match(r"^[-*]\s", s):
            flush()
            # an indented item is a sub-item (« - L'ouverture : » then « - on entend … » under it)
            out.append(("ul2" if ln[:1] in (" ", "\t") and out and out[-1][0] in ("ul", "ul2") else "ul", item(s[2:])))
        elif re.match(r"^\d+\.\s", s):
            flush()
            out.append(("ol", item(re.sub(r"^\d+\.\s", "", s))))
        elif s == "---":
            flush()
            out.append(("break", None))
        elif not s:
            flush()
        else:
            para.append(s.rstrip("\\").rstrip())
            if ln.endswith("  ") or ln.rstrip().endswith("\\"):   # a Markdown line break: one line, one paragraph
                flush()
        i += 1
    flush()
    return out


def split_checks(blocks):
    """Take the « La liste de contrôle » sections out of a part: (body, checks). The section runs to the next title
    of the same or a higher level."""
    body, checks, cut = [], [], None
    for b in blocks:
        if b[0] == "h":
            lvl, txt = b[1]
            if cut is not None and lvl <= cut:
                cut = None
            if cut is None and lvl == 2 and CHECKLIST.match(txt.strip()):
                cut = lvl
                continue
        (checks if cut is not None else body).append(b)
    return body, checks


# ------------------------------------------------------------------ the Word writer

class Writer:
    def __init__(self, brand, lang, header_text, base_dir, red_bold=False):
        import docx
        from docx.oxml.ns import qn
        from docx.shared import Pt, Cm, RGBColor
        self.docx, self.qn, self.Pt, self.Cm, self.RGB = docx, qn, Pt, Cm, RGBColor
        self.brand, self.lang, self.T = brand, lang, TEXT[lang]
        self.base_dir, self.red_bold = Path(base_dir), red_bold
        self.bm, self.landscape = 0, False
        d = self.doc = docx.Document()
        sec = d.sections[0]
        sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
        sec.left_margin = sec.right_margin = Cm(2.0)
        sec.top_margin, sec.bottom_margin = Cm(1.7), Cm(1.6)
        st = d.styles["Normal"]
        st.font.name, st.font.size = "Calibri", Pt(10)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        # Richie, 06/11/2026: the dense parts were hard to read; more air between lines and between items
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.line_spacing = 1.3
        for name in ("List Bullet", "List Bullet 2", "List Number"):
            if name in [s.name for s in d.styles]:
                d.styles[name].paragraph_format.space_after = Pt(5)
                d.styles[name].paragraph_format.line_spacing = 1.3
        for name, size in (("Heading 1", 22), ("Heading 2", 17), ("Heading 3", 13), ("Heading 4", 11.5)):
            h = d.styles[name]
            h.font.name, h.font.size, h.font.bold = "Calibri", Pt(size), True
            h.font.color.rgb = self.rgb(brand["primary"] if name != "Heading 4" else brand["accent"])
            h.paragraph_format.space_before = Pt(0 if name == "Heading 1" else 14)
            h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
        self._header_footer(sec, header_text)

    def rgb(self, h):
        return self.RGB.from_string(h)

    def el(self, tag, **attrs):
        from docx.oxml import OxmlElement
        e = OxmlElement(tag)
        for k, v in attrs.items():
            e.set(self.qn(k.replace("_", ":", 1)), str(v))
        return e

    # ---- page furniture
    def _field(self, par, instr, size=8, color=None):
        r = par.add_run()
        r.font.size = self.Pt(size)
        if color:
            r.font.color.rgb = self.rgb(color)
        r._r.append(self.el("w:fldChar", w_fldCharType="begin"))
        it = self.el("w:instrText")
        it.text = instr
        it.set(self.qn("xml:space"), "preserve")
        r2 = par.add_run()
        r2._r.append(it)
        r3 = par.add_run()
        r3._r.append(self.el("w:fldChar", w_fldCharType="end"))

    def _header_footer(self, sec, header_text):
        self.header_text = header_text
        self._fill_header_footer(sec, self.Cm(17.0))

    def _fill_header_footer(self, sec, tab):
        from docx.enum.text import WD_TAB_ALIGNMENT
        hdr = sec.header.paragraphs[0]
        for r in list(hdr.runs):
            r._r.getparent().remove(r._r)
        r = hdr.add_run(self.header_text)
        r.font.size, r.font.color.rgb, r.bold = self.Pt(8), self.rgb(self.brand["accent"]), True
        ftr = sec.footer.paragraphs[0]
        for r in list(ftr._p.xpath("./w:r")):
            ftr._p.remove(r)
        ftr.paragraph_format.tab_stops.add_tab_stop(tab, WD_TAB_ALIGNMENT.RIGHT)
        r = ftr.add_run(self.T["signature"] + "\t")
        r.font.size, r.font.color.rgb = self.Pt(7.5), self.rgb("6B7280")
        self._field(ftr, "PAGE", 8)

    # ---- inline text: bold, italic, links
    def link(self, par, text, url=None, anchor=None, size=None, color=None, bold=False):
        h = self.el("w:hyperlink")
        if anchor:
            h.set(self.qn("w:anchor"), anchor)
        else:
            from docx.opc.constants import RELATIONSHIP_TYPE as RT
            h.set(self.qn("r:id"), par.part.relate_to(url, RT.HYPERLINK, is_external=True))
        h.set(self.qn("w:history"), "1")
        r = par.add_run(text)
        r.bold = bold
        if size:
            r.font.size = self.Pt(size)
        r.font.color.rgb = self.rgb(color or self.brand["accent"])
        if not anchor:
            r.font.underline = True
        h.append(r._r)
        par._p.append(h)
        return r

    def inline(self, par, text, size=None, color=None, bold_all=False, red_bold=False):
        text = text.replace("<br>", "\n").replace("\\|", "|")
        pat = r"(`[^`]+`|\*\*.+?\*\*|\[[^\]]+\]\(https?://[^)\s]+\)|https?://[^\s)|>\]`]+|(?<!\*)\*(?!\s)[^*]+?\*(?!\*))"
        for part in re.split(pat, text):
            if not part:
                continue
            m = re.fullmatch(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", part)
            if m or re.fullmatch(r"https?://\S+", part):
                label, url = (m.group(1), m.group(2)) if m else (part, part.rstrip(".,;:"))
                tail = part[len(url):] if not m else ""
                self.link(par, label if m else url, url=url, size=size, bold=bold_all)
                if tail:
                    par.add_run(tail)
                continue
            r = par.add_run()
            if part.startswith("`") and part.endswith("`") and len(part) > 2:   # a command or a file name
                r.text = part[1:-1]
                r.font.name = "Consolas"
                r.font.size = self.Pt((size or 10) - 0.5)
                continue
            if part.startswith("**") and part.endswith("**") and len(part) > 4:
                r.text, r.bold = part[2:-2], True
                if red_bold:
                    r.font.color.rgb = self.rgb(RED)
                elif not color:   # bold reads as bold: in the document's dark colour, not the body grey
                    r.font.color.rgb = self.rgb(self.brand["primary"])
            elif part.startswith("*") and part.endswith("*") and len(part) > 2:
                r.text, r.italic = part[1:-1], True
            else:
                r.text = part
            if bold_all:
                r.bold = True
            if size:
                r.font.size = self.Pt(size)
            if color and not (red_bold and r.bold and not bold_all):
                r.font.color.rgb = self.rgb(color)

    # ---- blocks
    def shade(self, cell, hexcol):
        cell._tc.get_or_add_tcPr().append(self.el("w:shd", w_val="clear", w_color="auto", w_fill=hexcol))

    def borders(self, table, hexcol="D5D8DE"):
        b = self.el("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            b.append(self.el(f"w:{edge}", w_val="single", w_sz="4", w_color=hexcol))
        table._tbl.tblPr.append(b)

    @staticmethod
    def cells_of(rows):
        cells = [[c.strip() for c in re.split(r"(?<!\\)\|", r.strip().strip("|"))] for r in rows]
        return [r for r in cells if not all(re.fullmatch(r":?-{2,}:?", c) for c in r if c)]

    @staticmethod
    def measure(cells):
        """Per column: the longest cell (links and bold counted as what is read), and the header's longest word."""
        n = max(len(r) for r in cells)
        plain = lambda x: len(re.sub(r"\*\*|\[([^\]]+)\]\([^)]+\)", r"\1", x))
        need = [max(plain(r[j]) if j < len(r) else 0 for r in cells) for j in range(n)]
        word = lambda x: max((len(w) for w in re.sub(r"\*\*|\[([^\]]+)\]\([^)]+\)", r"\1", x).split()), default=0)
        head = [max(min(word(r[j]), 16) if j < len(r) else 0 for r in cells) for j in range(n)]
        return n, need, head

    @classmethod
    def is_wide(cls, rows):
        cells = cls.cells_of(rows)
        if not cells:
            return False
        n, need, _ = cls.measure(cells)
        return n >= 7 or sum(min(x, 60) for x in need) > 190

    def table(self, rows):
        from docx.enum.table import WD_TABLE_ALIGNMENT
        cells = self.cells_of(rows)
        if not cells:
            return
        n, need, head = self.measure(cells)
        if not self.landscape and self.is_wide(rows):
            self.orient(True)   # a wide table gets a landscape page; the next big title brings the portrait back
        width = 25.7 if self.landscape else 17.0
        # in cm at 8.5 pt: what each column would like (its longest cell, capped) and what it can't go under (its
        # longest word); the page width is shared out between the two
        want = [min(x, 60) * 0.19 + 0.4 for x in need]
        floor = [max(h, 3) * 0.19 + 0.45 for h in head]
        want = [max(a, b) for a, b in zip(want, floor)]
        if sum(want) <= width:
            cm = [x * width / sum(want) for x in want]
        elif sum(floor) >= width:
            cm = [x * width / sum(floor) for x in floor]
        else:
            k = (width - sum(floor)) / (sum(want) - sum(floor))
            cm = [f + (w_ - f) * k for f, w_ in zip(floor, want)]
        widths = [self.Cm(x) for x in cm]
        t = self.doc.add_table(rows=len(cells), cols=n)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        self.borders(t)
        for i, r in enumerate(cells):
            for j in range(n):
                c = t.cell(i, j)
                c.width = widths[j]
                p = c.paragraphs[0]
                p.paragraph_format.space_after = self.Pt(1)
                p.paragraph_format.line_spacing = 1.1
                txt = r[j] if j < len(r) else ""
                if i == 0:
                    self.shade(c, self.brand["primary"])
                    self.inline(p, txt, size=8.5, color="FFFFFF", bold_all=True)
                    p.paragraph_format.keep_with_next = True   # the header goes with the first row (page 36, 06/11)
                else:
                    if i % 2 == 0:
                        self.shade(c, SHADE)
                    self.inline(p, txt, size=8.5, red_bold=self.red_bold)
        t.rows[0]._tr.get_or_add_trPr().append(self.el("w:tblHeader", w_val="true"))
        t.rows[0]._tr.get_or_add_trPr().append(self.el("w:cantSplit", w_val="true"))
        self.doc.add_paragraph().paragraph_format.space_after = self.Pt(2)

    def callout(self, lines, mono=False):
        t = self.doc.add_table(rows=1, cols=1)
        c = t.cell(0, 0)
        self.shade(c, SHADE)
        b = self.el("w:tcBorders")
        b.append(self.el("w:left", w_val="single", w_sz="24", w_color=self.brand["accent"]))
        c._tc.get_or_add_tcPr().append(b)
        p = c.paragraphs[0]
        for k, ln in enumerate(lines):
            if k:
                p = c.add_paragraph()
            p.paragraph_format.space_after = self.Pt(2)
            p.paragraph_format.line_spacing = 1.15
            if mono:
                r = p.add_run(ln)
                r.font.name, r.font.size = "Consolas", self.Pt(8.5)
            else:
                self.inline(p, ln)
        self.doc.add_paragraph().paragraph_format.space_after = self.Pt(2)

    def _img_path(self, path):
        p = Path(path)
        return p if p.is_absolute() else (self.base_dir / p)

    def image(self, path, cap):
        """One image: a vertical frame 5 cm wide, a horizontal one 12 cm, so no image eats a page."""
        p = self._img_path(path)
        if not p.exists():
            self.doc.add_paragraph().add_run(f"[image absente : {path}]").italic = True
            return
        try:
            from PIL import Image
            with Image.open(p) as im:
                w_, h_ = im.size
            self.doc.add_picture(std_jpeg(p), width=self.Cm(5 if h_ > w_ else 12))
        except Exception:
            self.doc.add_paragraph().add_run(f"[image illisible : {p.name}]").italic = True
            return
        if cap:
            q = self.doc.add_paragraph()
            r = q.add_run(cap)
            r.italic, r.font.size = True, self.Pt(8)

    def images(self, items):
        """Several images in a row (the key frames of a reference): a grid of thumbnails, four per row."""
        if len(items) == 1:
            return self.image(*items[0])
        cols = min(4, len(items))
        rows = (len(items) + cols - 1) // cols
        t = self.doc.add_table(rows=rows, cols=cols)
        t.autofit = False
        for k, (path, cap) in enumerate(items):
            c = t.cell(k // cols, k % cols)
            c.width = self.Cm(17.0 / cols if not self.landscape else 25.7 / cols)
            p = self._img_path(path)
            par = c.paragraphs[0]
            if p.exists():
                try:
                    par.add_run().add_picture(std_jpeg(p), width=self.Cm(3.6))
                except Exception:
                    par.add_run(f"[image illisible : {p.name}]").italic = True
            else:
                par.add_run(f"[image absente : {path}]").italic = True
            if cap:
                r = c.add_paragraph().add_run(cap)
                r.italic, r.font.size = True, self.Pt(7.5)
        self.doc.add_paragraph().paragraph_format.space_after = self.Pt(2)

    def page_break(self):
        from docx.enum.text import WD_BREAK
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    def bookmark(self, par, name):
        self.bm += 1
        start = self.el("w:bookmarkStart", w_id=self.bm, w_name=name)
        pPr = par._p.pPr
        if pPr is not None:
            pPr.addnext(start)
        else:
            par._p.insert(0, start)
        par._p.append(self.el("w:bookmarkEnd", w_id=self.bm))

    def orient(self, landscape):
        """Open a new section in landscape or portrait (on a new page) when the orientation changes."""
        from docx.enum.section import WD_ORIENT, WD_SECTION
        if landscape == self.landscape:
            return
        sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
        sec.different_first_page_header_footer = False
        sec.orientation = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
        sec.page_width, sec.page_height = (self.Cm(29.7), self.Cm(21.0)) if landscape else (self.Cm(21.0), self.Cm(29.7))
        tab = self.Cm(25.7 if landscape else 17.0)
        sec.footer.is_linked_to_previous = False
        sec.header.is_linked_to_previous = False
        self._fill_header_footer(sec, tab)
        self.landscape = landscape

    def heading(self, lvl, text, anchor=None, landscape=False):
        """A title. A big one (level 1–2) sets the orientation of its section: landscape when it holds a wide table,
        so the title and its table share the page."""
        if lvl <= 2 and landscape != self.landscape:
            self.orient(landscape)
        h = self.doc.add_heading(text, level=min(lvl, 4))
        if anchor:
            self.bookmark(h, anchor)
        return h

    def numbered(self, n, text):
        p = self.doc.add_paragraph()
        p.paragraph_format.left_indent = self.Cm(0.6)
        p.paragraph_format.first_line_indent = self.Cm(-0.6)
        p.paragraph_format.tab_stops.add_tab_stop(self.Cm(0.6))
        self.inline(p, f"{n}.	{text}")

    def render(self, blocks):
        merged = []   # images on consecutive lines form one grid; a page break right after another is dropped
        for kind, x in blocks:
            if kind == "img" and merged and merged[-1][0] == "img":
                merged[-1] = ("img", merged[-1][1] + x)
            elif not (kind == "break" and merged and merged[-1][0] == "break"):
                merged.append((kind, x))
        blocks = merged
        n = 0
        for i, (kind, x) in enumerate(blocks):
            n = n + 1 if kind == "ol" else 0
            if kind == "h":
                lvl, txt, anchor, new_page = x if len(x) == 4 else (*x, None, False)
                wide = False
                if lvl <= 2:   # does this section hold a wide table? Then it is laid out in landscape
                    for k2, x2 in blocks[i + 1:]:
                        if k2 == "h" and x2[0] <= 2:
                            break
                        if k2 == "table" and self.is_wide(x2):
                            wide = True
                            break
                if new_page and wide == self.landscape:
                    self.page_break()
                self.heading(lvl, txt, anchor, landscape=wide)
            elif kind == "p":
                self.inline(self.doc.add_paragraph(), x)
            elif kind == "ul":
                self.inline(self.doc.add_paragraph(style="List Bullet"), x)
            elif kind == "ul2":
                self.inline(self.doc.add_paragraph(style="List Bullet 2"), x)
            elif kind == "ol":
                self.numbered(n, x)
            elif kind == "check":
                self.inline(self.doc.add_paragraph(), "☐  " + x)
            elif kind == "table":
                self.table(x)
            elif kind == "quote":
                self.callout(x)
            elif kind == "code":
                self.callout(x, mono=True)
            elif kind == "img":
                self.images(x)
            elif kind == "break":
                self.page_break()

    # ---- the book's own pages
    def spacer(self, pt):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = self.Pt(pt)
        p.paragraph_format.space_after = self.Pt(0)
        return p

    def cover(self, title, sub, meta, kind=None):
        self.doc.sections[0].different_first_page_header_footer = True   # the cover carries its own signature
        self.spacer(150)
        p = self.doc.add_paragraph()
        r = p.add_run((kind or self.T["kind"]).upper())
        r.bold, r.font.size, r.font.color.rgb = True, self.Pt(12), self.rgb(self.brand["accent"])
        p = self.doc.add_paragraph()
        r = p.add_run(title)
        r.bold, r.font.size, r.font.color.rgb = True, self.Pt(32), self.rgb(self.brand["primary"])
        p.paragraph_format.space_after = self.Pt(6)
        if sub:
            p = self.doc.add_paragraph()
            r = p.add_run(sub)
            r.font.size, r.font.color.rgb = self.Pt(14), self.rgb("4B5563")
        bar = self.doc.add_paragraph()
        bar.paragraph_format.space_before = self.Pt(10)
        bar._p.get_or_add_pPr().append(self._bottom_border(self.brand["accent"], 18))
        p = self.doc.add_paragraph()
        r = p.add_run(meta)
        r.font.size, r.font.color.rgb = self.Pt(10), self.rgb("4B5563")
        self.spacer(260)
        p = self.doc.add_paragraph()
        r = p.add_run(self.T["signature"])
        r.font.size, r.font.color.rgb = self.Pt(9), self.rgb("6B7280")

    def _bottom_border(self, color, sz):
        b = self.el("w:pBdr")
        b.append(self.el("w:bottom", w_val="single", w_sz=sz, w_space="1", w_color=color))
        return b

    def toc(self, entries):
        """entries: (level, text, anchor). Each line is a link to its heading, with its page number."""
        from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
        self.page_break()
        self.heading(1, self.T["toc"])
        for lvl, text, anchor in entries:
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.space_after = self.Pt(2 if lvl > 1 else 3)
            pf.space_before = self.Pt(7 if lvl == 1 else 0)
            pf.left_indent = self.Cm(0 if lvl == 1 else 0.7)
            pf.tab_stops.add_tab_stop(self.Cm(17.0), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
            color = self.brand["primary"] if lvl == 1 else "374151"
            self.link(p, text, anchor=anchor, size=11 if lvl == 1 else 9.5, color=color, bold=lvl == 1)
            p.add_run("\t")
            f = self.el("w:fldSimple", w_instr=f" PAGEREF {anchor} \\h ")
            r = self.el("w:r")
            t = self.el("w:t")
            t.text = "·"
            r.append(t)
            f.append(r)
            p._p.append(f)

    def part_page(self, number, title, sub, anchor):
        if self.landscape:
            self.orient(False)
        else:
            self.page_break()
        self.spacer(190)
        p = self.doc.add_paragraph()
        r = p.add_run(f"{number:02d}")
        r.bold, r.font.size, r.font.color.rgb = True, self.Pt(54), self.rgb(self.brand["accent"])
        p.paragraph_format.space_after = self.Pt(0)
        h = self.heading(1, title, anchor)
        for r in h.runs:
            r.font.size = self.Pt(34)
        h._p.get_or_add_pPr().append(self._bottom_border(self.brand["accent"], 12))
        if sub:
            p = self.doc.add_paragraph()
            r = p.add_run(sub)
            r.font.size, r.font.color.rgb = self.Pt(13), self.rgb("4B5563")
        self.page_break()

    def save(self, out):
        out.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(out))
        return out


# ------------------------------------------------------------------ one document per deliverable

DOC_KIND = {"fr": {"FICHE-ENTREE": "Le point de départ", "OFFRE": "L'offre et la page", "RECHERCHE": "La recherche",
                   "STRATEGIE": "La stratégie", "BRIEFS": "Les briefs", "PRODUCTION": "La production",
                   "CONTROLE": "Le contrôle des créatives", "LANCEMENT": "Le lancement",
                   "LECTURE": "La lecture des résultats", "GAGNANTS": "Le registre des gagnants", "VARIATIONS": "Les variations", "MONTAGE": "Le guide de montage",
                   "BILAN": "Le bilan du produit",
                   "CONCURRENTS": "Le marché et les concurrents", "PAGE": "La page, écrite comme un brief"},
            "en": {"FICHE-ENTREE": "The starting point", "OFFRE": "The offer and the page", "RECHERCHE": "The research",
                   "STRATEGIE": "The strategy", "BRIEFS": "The briefs", "PRODUCTION": "Production",
                   "CONTROLE": "The creative check", "LANCEMENT": "The launch", "LECTURE": "Reading the results", "GAGNANTS": "The register of winners",
                   "VARIATIONS": "The variations", "MONTAGE": "The editing guide",
                   "BILAN": "The product's history",
                   "CONCURRENTS": "The market and the competitors", "PAGE": "The page, written as a brief"}}


def reader_doc(blocks, stem, ws):
    """A step document for the reader (Richie, 22/11/2026: the book's rules for every document): what it is for first,
    the tool's marks out, the checks written in sentences under « Ce qui a été vérifié », the glossary at the end."""
    import bookparts
    body, checks = split_checks(blocks)
    first = next((i for i, (k, x) in enumerate(body) if k == "h" and x[0] == 1), None)
    head, rest = (body[:first + 1], body[first + 1:]) if first is not None else ([], body)
    out = head + purpose_block(stem.upper(), ws, "À quoi sert ce document") + reader_blocks(rest, ws)
    if checks:
        out += [("h", (2, "Ce qui a été vérifié"))] + checks_sentences(checks)[0]
    gl = parse(kind_block(bookparts.GLOSSAIRE, ws))
    out += [("h", (2, "Les mots à connaître"))] + [x for x in gl if not (x[0] == "h" and x[1][0] == 1)]
    return out


def build(md_path, out, brand, title_hint="", lang="fr", cover=None, ws=None):
    """One deliverable as a Word document. cover = (kind, title, subtitle, meta): the strategy book's cover page and
    clickable contents come first (the document's own first title goes onto the cover); None = the text alone."""
    md_path = Path(md_path)
    w = Writer(brand, lang, title_hint or md_path.stem, md_path.parent,
               red_bold=md_path.stem.upper().startswith("BRIEFS"))
    blocks = parse(read_text(md_path))
    if ws is not None and lang == "fr":
        blocks = reader_doc(blocks, md_path.stem, ws)
    if cover:
        kind, title, sub, meta = cover
        first = next((i for i, (k, x) in enumerate(blocks) if k == "h"), None)
        if first is not None and blocks[first][1][0] == 1:
            h1 = blocks[first][1][1]
            title, sub = title or h1, h1 if sub is None and title else sub
            blocks = blocks[:first] + blocks[first + 1:]
        levels = sorted({x[0] for k, x in blocks if k == "h"})[:2]
        if ws is not None and levels:
            # Richie, 23/11/2026: every document carries the strategy book's branding: cover, contents, and each big
            # title opening on its own page (« 01 », the title, the green line), header and signature on every page
            return build_parts(w, blocks, levels, (kind, title, sub, meta), out)
        entries, out_blocks, k_ = [], [], 0
        for k, x in blocks:
            if k == "h" and x[0] in levels:
                k_ += 1
                anchor = f"s{k_}"
                entries.append((levels.index(x[0]) + 1, x[1], anchor))
                out_blocks.append(("h", (x[0], x[1], anchor, False)))
            else:
                out_blocks.append((k, x))
        w.cover(title, sub, meta, kind=kind)
        if entries:
            w.toc(entries)
        w.page_break()
        blocks = out_blocks
    w.render(blocks)
    return w.save(out)


def build_parts(w, blocks, levels, cover, out):
    """A step document laid out like the strategy book: the cover, the contents, what comes before the first big title
    on its own page, then one part page per big title (its number, its title) followed by its content."""
    kind, title, sub, meta = cover
    top, second = levels[0], (levels[1] if len(levels) > 1 else None)
    intro, parts, entries = [], [], []
    for k, x in blocks:
        if k == "h" and x[0] == top:
            n = len(parts) + 1
            parts.append((n, x[1], f"p{n}", []))
            entries.append((1, f"{n}. {x[1]}", f"p{n}"))
            continue
        if k == "h" and x[0] == second and parts:
            anchor = f"p{parts[-1][0]}_{len(entries)}"
            entries.append((2, x[1], anchor))
            parts[-1][3].append(("h", (2, x[1], anchor, False)))
            continue
        if k == "h" and parts:
            x = (min(max(x[0], 3), 4), x[1])
        (parts[-1][3] if parts else intro).append((k, x))
    w.cover(title, sub, meta, kind=kind)
    if entries:
        w.toc(entries)
    if intro:
        w.page_break()
        w.render(intro)
    for n, ptitle, anchor, pblocks in parts:
        w.part_page(n, ptitle, "", anchor)
        while pblocks and pblocks[-1][0] == "break":
            pblocks.pop()
        w.render([b for i, b in enumerate(pblocks) if not (i == 0 and b[0] == "break")])
    return w.save(out)


def cover_of(P, ws, stem, lang="fr"):
    """The cover of a step document: its kind, the product, its own first title, the markets · cycle · date."""
    import datetime as _dt
    name = str(ws.get("name") or "").strip()
    m = re.match(r"^(.*?)\s*\((.+)\)\s*$", name)
    title = m.group(1) if m else name   # the document's own first title becomes the subtitle
    markets = ", ".join(x.get("country", "") for x in ws.get("markets") or [] if isinstance(x, dict))
    state = W.load_yaml(P["state"], {}) if P.get("state") else {}
    cycle = (state or {}).get("cycle") or 1
    meta = " · ".join(x for x in (markets, f"{TEXT[lang]['cycle']} {cycle}", _dt.date.today().strftime("%d/%m/%Y")) if x)
    kind = DOC_KIND[lang].get(stem.upper(), stem.replace("-", " ").title())
    return kind, title, None, meta


# ------------------------------------------------------------------ the strategy book

def part_blocks(name, blocks, n_part):
    """A part's blocks for the book: its own title line goes (the part page replaces it), levels are set for the book
    (BRIEFS: each creative is a level-2 title on a new page), level-1 and 2 titles get an anchor for the contents."""
    out, toc, first, k = [], [], True, 0
    for kind, x in blocks:
        if kind == "h":
            lvl, txt = x
            if first and lvl == 1:
                first = False
                continue
            first = False
            if name == "BRIEFS":
                new_lvl, new_page = (2, k > 0) if lvl == 1 else (min(lvl + 1, 4), False)
            else:
                new_lvl, new_page = (max(lvl, 2), False)
            anchor = None
            if new_lvl == 2:
                k += 1
                anchor = f"p{n_part}_{k}"
                toc.append((2, txt, anchor))
            out.append(("h", (new_lvl, txt, anchor, new_page)))
        elif kind == "break" and name == "BRIEFS":
            continue   # each creative already opens a page
        else:
            out.append((kind, x))
    while out and out[-1][0] == "break":   # the part page that follows opens its own page
        out.pop()
    return out, toc


PAGE_BRIEFS = ("PAGE-INSCRIPTION", "PAGE-C", "PAGE-A", "PAGE-B", "PAGE-D")


def part_file(src, part):
    """The file of one book part. OFFRE falls back on the page written as a brief (offer.py page write) when the step
    has no OFFRE.md: a webinar's offer is its sign-up page."""
    f = src / f"{part}.md"
    if f.exists() or part != "OFFRE":
        return f
    return next((src / f"{n}.md" for n in PAGE_BRIEFS if (src / f"{n}.md").exists()), f)


def build_book(P, ws, out, names=None, outline=False):
    lang = lang_of(ws)
    T = TEXT[lang]
    src = P["root"] / "deliverables"
    found = [n for n in BOOK_PARTS if part_file(src, n).exists() and (not names or n in names)]
    if not found:
        raise WsError("aucune partie à relier : il faut au moins un de " + ", ".join(f"{n}.md" for n in BOOK_PARTS))
    brand = brand_of(ws)
    name = str(ws.get("name") or "").strip()
    title, sub = (re.match(r"^(.*?)\s*\((.+)\)\s*$", name).groups() if re.match(r"^(.*?)\s*\((.+)\)\s*$", name)
                  else (name, ws.get("business") or ""))
    w = Writer(brand, lang, f"{name} · {T['kind']}", src, red_bold=False)
    markets = ", ".join(m.get("country", "") for m in ws.get("markets") or [] if isinstance(m, dict))
    state = W.load_yaml(P["state"], {}) if P.get("state") else {}
    cycle = (state or {}).get("cycle") or 1
    import datetime as _dt
    draft = "BRIEFS" not in found
    meta = " · ".join(x for x in (markets, f"{T['cycle']} {cycle}", _dt.date.today().strftime("%d/%m/%Y"),
                                  T["draft"]["tag"].format(n=len(found)) if draft else "") if x)
    w.cover(title, sub, meta)

    parts, entries, appendix = [], [(1, T["start"], "start")], []
    for n, part in enumerate(found, 1):
        body, checks = split_checks(parse(read_text(part_file(src, part))))
        if lang == "fr":
            body = purpose_block(part, ws) + reader_blocks(body, ws)
        blocks, toc = part_blocks(part, body, n)
        ptitle, psub = T["parts"][part]
        parts.append((n, part, ptitle, psub, blocks))
        entries.append((1, f"{n}. {ptitle}", f"p{n}"))
        entries.extend(toc)
        if checks:
            appendix.append((ptitle, checks))
    course = course_blocks(ws) if lang == "fr" and "BRIEFS" in found else []
    if course:
        n = len(parts) + 1
        cblocks, ctoc = part_blocks("COURS", [("h", (1, "Le mini-cours"))] + course, n)
        parts.append((n, "COURS", "Le mini-cours", "Lire tes chiffres, corriger une pub, faire les suivantes seul.", cblocks))
        entries.append((1, f"{n}. Le mini-cours", f"p{n}"))
        entries.extend(ctoc)
    if appendix or lang == "fr":
        entries.append((1, T["appendix"] if lang == "fr" else f"{T['appendix']} · {T['checks']}", "annexe"))
    if outline:
        return entries
    w.toc(entries)

    w.page_break()
    w.heading(1, T["start"], "start")
    missing = [p for p in BOOK_PARTS if p not in found]
    D = T["draft"]
    if "BRIEFS" in missing:   # a working version: the same file grows after each step, up to the briefs
        nxt = T["parts"][missing[0]][0]
        how = [D["how"].format(n=len(found))] + T["how"][1:]
        now = [t.format(next=nxt) for t in D["now"]]
        later = [f"**{T['parts'][p][0]}** : {T['parts'][p][1]}" for p in missing] + [D["after"]]
    else:
        how, now, later = T["how"], T["now"], T["next"]
    for t in how:
        w.inline(w.doc.add_paragraph(), t)
    w.heading(2, T["now_t"])
    for k, t in enumerate(now, 1):
        w.numbered(k, t)
    w.heading(2, T["next_t"])
    for t in later:
        w.inline(w.doc.add_paragraph(style="List Bullet"), t)

    for n, part, ptitle, psub, blocks in parts:
        w.part_page(n, ptitle, psub, f"p{n}")
        w.red_bold = part == "BRIEFS"
        w.render(blocks)
    w.red_bold = False
    if lang == "fr":
        w.part_page(len(parts) + 1, T["appendix"], "Les vérifications, le glossaire, les codes, les sources", "annexe")
        w.render(annex_blocks(appendix, P, ws))
    elif appendix:
        w.part_page(len(parts) + 1, T["checks"], T["appendix"], "annexe")
        w.inline(w.doc.add_paragraph(), T["checks_lead"])
        for ptitle, checks in appendix:
            w.heading(2, ptitle)
            w.render([(k, x) if k != "h" else ("h", (max(x[0], 3), x[1])) for k, x in checks[1:]])
    return w.save(out)


# ------------------------------------------------------------------ PDF

def to_pdf(docx_path):
    """Word (COM through PowerShell) on Windows — fields updated, PDF bookmarks from the headings — then LibreOffice;
    None when neither is here."""
    docx_path = Path(docx_path).resolve()   # Word opens a relative path from its own folder, not ours
    pdf = docx_path.with_suffix(".pdf")
    if pdf.exists():
        try:
            pdf.unlink()
        except OSError:
            raise WsError(f"{pdf.name} est ouvert : ferme-le et relance")
    if W.WIN and W.find_word():
        q = lambda p: str(p).replace("'", "''")
        ps = (f"$w=New-Object -ComObject Word.Application;$w.Visible=$false;$w.DisplayAlerts=0;"
              f"$d=$w.Documents.Open('{q(docx_path)}');$d.Fields.Update()|Out-Null;$d.Save();"
              f"$d.ExportAsFixedFormat('{q(pdf)}',17,$false,0,0,1,1,0,$true,$true,1,$true,$true,$false);"
              f"$d.Close([ref]$false);$w.Quit()")
        try:
            subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True, timeout=240)
        except Exception:
            pass
        if pdf.exists():
            return pdf
    so = shutil.which("soffice") or shutil.which("libreoffice") or next(
        (str(x) for x in (Path(r"C:/Program Files/LibreOffice/program/soffice.exe"),
                          Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")) if x.exists()), None)
    if so:
        try:
            subprocess.run([str(so), "--headless", "--convert-to", "pdf", "--outdir", str(pdf.parent), str(docx_path)],
                           capture_output=True, timeout=240)
        except Exception:
            pass
        if pdf.exists():
            return pdf
    return None


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = W.FrParser(prog="docs.py", description="Les livrables en Word et en PDF.")
    ap.add_argument("folder")
    ap.add_argument("names", nargs="*")
    ap.add_argument("--book", action="store_true", help="relier entrée, offre, recherche, stratégie et briefs en un document")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--plain", action="store_true", help="sans couverture ni sommaire (le texte seul)")
    ap.add_argument("--outline", action="store_true", help="avec --book : montrer le sommaire à valider, sans rien relier")
    a = ap.parse_args(argv)
    try:
        P, ws, state = open_ws(a.folder)
        src = P["root"] / "deliverables"
        out_dir = src / "word"
        lang = lang_of(ws)
        want = {n.upper().removesuffix(".MD") for n in a.names}
        if a.book and a.outline:
            # 1.7: the client validates the contents before a book is rebuilt
            print("Le sommaire du livre, à valider avant de le relier :")
            for lvl, txt, _ in build_book(P, ws, out_dir / "x.docx", want or None, outline=True):
                print(("  " if lvl == 1 else "      - ") + txt)
            print("Quand le client dit oui : docs.py <dossier> --book")
            return
        if a.book:
            out = out_dir / f"{TEXT[lang]['book']}.docx"
            mark = out_dir / ".book-cycle"   # the cycle the current book belongs to
            cycle = int(state.get("cycle") or 1)
            try:
                old = int(mark.read_text(encoding="utf-8").strip()) if mark.exists() else None
            except ValueError:
                old = None
            if old and old != cycle and out.exists():   # a new strategy: the previous document is kept, renamed
                for ext in (".docx", ".pdf"):
                    f = out.with_suffix(ext)
                    if f.exists():
                        keep = f.with_name(f"{f.stem}-cycle-{old:02d}{ext}")
                        try:
                            f.replace(keep)
                        except PermissionError:
                            raise WsError(f"{f.name} est ouvert : ferme-le et relance")
                        print(f"Version du cycle {old} gardée : {keep.name}")
            try:
                build_book(P, ws, out, want or None)
            except PermissionError:
                raise WsError(f"{out.name} est ouvert dans Word : ferme-le et relance")
            mark.write_text(str(cycle), encoding="utf-8")
            pdf = None if a.no_pdf else to_pdf(out)
            have = [n for n in BOOK_PARTS if part_file(src, n).exists() and (not want or n in want)]
            left = [TEXT[lang]["parts"][n][0] for n in BOOK_PARTS if n not in have]
            state_of = f"{len(have)} partie(s) sur 5" + (f", version de travail (manque : {', '.join(left)})"
                                                          if "BRIEFS" not in have else "")
            journal(P, f"Document de stratégie relié : {out.name}, {state_of}" + (" (+ PDF)" if pdf else ""))
            print(f"Relié : {state_of}.")
            print(f"Écrit : {out}" + (f"\n        {pdf}" if pdf else
                  ("" if a.no_pdf else "\n  pas de PDF : ni Word ni LibreOffice sur cet ordinateur (ws.py doctor)")))
            print("\n" + W.handoff(P, "book", ws, state))
            return
        mds = sorted(src.glob("*.md")) if src.exists() else []
        if want:
            mds = [m for m in mds if m.stem.upper() in want]
            missing = want - {m.stem.upper() for m in mds}
            if missing:
                raise WsError(f"pas de deliverables/{', '.join(sorted(missing))}.md")
        if not mds:
            raise WsError("aucun livrable .md dans deliverables/ : les skills les écrivent (report, sheet, render…)")
        brand = brand_of(ws)
        made, pdfs = [], 0
        for m in mds:
            out = out_dir / f"{m.stem}.docx"
            try:
                build(m, out, brand, f"{ws.get('name')} · {DOC_KIND[lang].get(m.stem.upper(), m.stem.replace('-', ' ').title())}", lang,
                      cover=None if a.plain else cover_of(P, ws, m.stem, lang), ws=ws)
            except PermissionError:
                raise WsError(f"{out.name} est ouvert dans Word : ferme-le et relance")
            made.append(out)
            if not a.no_pdf and to_pdf(out):
                pdfs += 1
        journal(P, f"Livrables en Word : {', '.join(x.stem for x in made)}" + (f" (+ {pdfs} PDF)" if pdfs else ""))
        print(f"Écrit : {len(made)} document(s) Word dans {out_dir}" + (f", {pdfs} PDF" if pdfs else
              ("" if a.no_pdf else " ; pas de PDF : ni Word ni LibreOffice sur cet ordinateur (ws.py doctor)")))
    except WsError as e:
        print(f"ERREUR : {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERREUR inattendue ({type(e).__name__} : {e}).", file=sys.stderr)
        if os.environ.get("WS_DEBUG"):
            raise
        sys.exit(3)


if __name__ == "__main__":
    main()
