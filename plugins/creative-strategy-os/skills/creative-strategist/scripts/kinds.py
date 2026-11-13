# -*- coding: utf-8 -*-
"""kinds.py — what the project sells, and what that changes in every step of the suite.

workspace.yaml `kind`: `product` (a physical product with a page and an order, the default), `digital` (a course, a
method, templates or AI assistants sold on a sales page, paid online or by mobile money, opened at once: Protocole
Creative IA) or `webinar` (a free live that ends on a sign-up; the programme is sold during or after it). One profile
per kind, read by research (the
objections), strategy (the objections, the proof of a hook), briefs and review (how a script ends, the checklist, the
production lines), launch (the optimisation event) and read (what a result is). The webinar test of 01/11/2026 found
every product assumption these profiles replace (JOURNAL-DU-TEST.md, 132 warnings on 50 briefs).
"""
import re

KINDS = ("product", "digital", "webinar")

# the questions that block a purchase, grouped; matched on folded text (lower case, accents dropped)
OBJECTIONS = {
    "product": {
        "prix": r"\bcher\b|\btrop cher\b|\bexpensive\b|\bprix\b|\bcombien\b(?! de (?:temps|jours|semaines|mois|fois))",
        "confiance": r"\barnaque\b|\bfake\b|\bscam\b|\bmensonge\b|\bvraiment\b.*\?|\bmarche vraiment\b|\bça marche\b.*\?",
        "livraison": r"\blivr(?:aison|er|ez|ons|ee|ees|e (?:a|au|en|sur|chez)\b)|\bdeliver|\bexpedi|\bship",
        "efficacite": r"\bresultat|\befficace|\bmarche\b|\bwork|\bpour (?:la|les|le) (?:hanche|dos|lombaire|arthrose|douleur)",
        "usage": r"\bcomment (?:on )?(?:l'?utilise|le porter|mettre)\b|\btaille\b|\bsize\b|\bla nuit\b|\bdormir\b|\bsleep\b",
    },
    # a course or a method bought online: is it real, will it work for me, what exactly do I get, how do I pay
    "digital": {
        "arnaque": r"\barnaque|\bscam\b|\bfake\b|\bescro|\bmensonge|\bc'?est faux\b|\bvraiment\b.*\?|\bca marche vraiment\b",
        "pour_moi": r"\bdebutant|\bje (?:ne )?(?:connais|sais) rien\b|\bsans experience\b|\bmon (?:niveau|domaine|pays|business)\b|"
                    r"\bca marche (?:pour|avec|en|au)\b|\bmeme (?:si|sans)\b|\bsur (?:mon |un )?telephone\b|\bsans (?:ordinateur|pc)\b",
        "prix": r"\bcher\b|\btrop cher\b|\bexpensive\b|\bprix\b|\bcombien\b(?! de (?:temps|jours|semaines|mois|fois))|\breduction\b|\bpromo\b",
        "acces": r"\bacces\b|\bcomment (?:ca se passe|on recoit|je recois)|\bpdf\b|\bvideos?\b.*\?|\ba vie\b|\bcombien de temps\b.*\bacces|"
                 r"\bgroupe\b|\bwhatsapp\b|\btelegram\b|\bmodule|\bmise a jour\b",
        "paiement": r"\bmobile money\b|\borange money\b|\bwave\b|\bmomo\b|\bpaypal\b|\bcarte (?:bancaire|visa|de credit)|"
                    r"\bpayer (?:comment|avec|par)\b|\bpaiement\b|\bplusieurs fois\b|\bversement",
        "outils": r"\boutils?\b.*\b(?:payant|coute|prix|abonnement|cher)|\babonnement\b|\bcredits?\b|\bgratuit\w*\b.*\?",
        "remboursement": r"\brembours|\bgarantie\b|\bsatisfait\b|\bsi (?:ca|ça) ne marche pas\b",
    },
    # an opportunity: the doubts read in 794 TikTok comments under « gagner de l'argent en ligne » (01/11/2026)
    "webinar": {
        "arnaque": r"\barnaque|\bscam\b|\bfake\b|\bescro|\bmensonge|\bmenteur|\bpyramid|\bponzi|\bdu vent\b|"
                   r"\bne (?:repond|reponde)\w* (?:jamais|pas)|\bjamais (?:de )?reponse|\bne donne\w* jamais|\bc'?est faux\b",
        "investissement": r"\binvesti|\bpayant|\bpayer\b|\bcombien (?:ca |ça )?coute|\bcarte (?:bancaire|visa|de credit)|"
                          r"\bcapital\b|\bde l'argent pour commencer|\bprix\b|\btrop cher\b",
        "pays": r"\bafrique|\bpaypal|\bmobile money|\borange money|\bwave\b|\bmomo\b|\bmon pays\b|\bpossible (?:au|en|ici|chez)\b|"
                r"\bdepuis (?:le |la |l')?(?:benin|togo|cameroun|senegal|cote d'ivoire|mali|burkina|guinee|congo|gabon|niger)",
        "temps": r"\bpas le temps\b|\bcombien de (?:temps|jours|mois|heures)\b|\bheures? par jour\b|\bje travaille\b|"
                 r"\bapres (?:le|mon) (?:travail|boulot)\b|\ba cote de mon\b",
        "competence": r"\bdebutant|\bje (?:ne )?(?:connais|sais) rien\b|\bsans experience\b|\bsur (?:mon |un )?telephone\b|"
                      r"\bsans (?:ordinateur|pc)\b|\bmineur\b|\bj'?ai \d{2} ans\b|\btrop (?:vieux|vieille|jeune)\b|\bdiplome",
        "resultats": r"\brien gagne\b|\bj'?ai (?:tout )?(?:essaye|fait)\b.{0,40}\brien\b|\bca ne marche pas\b|"
                     r"\bpreuves?\b|\bqui a deja gagne\b",
    },
}

PROFILES = {
    "product": {
        "label": "produit",
        "event": "Purchase", "event_fr": "achat", "result": "commande", "results": "commandes",
        "cost_label": "coût par commande",
        "proof_days": 30,   # an Ad Library ad that runs 30 days pays for itself
        # how a script ends: said, then written on the end card
        "end_said": "le prix et « tu paies seulement à la livraison »",
        "end_written": "le prix et « paiement à la livraison »",
        "on_set": "Le vrai produit dans sa vraie boîte, à portée de main.",
    },
    "digital": {
        "label": "produit numérique",
        "event": "Purchase", "event_fr": "achat", "result": "vente", "results": "ventes",
        "cost_label": "coût par vente",
        "proof_days": 30,
        # nothing to deliver, nothing to pay at the door: the price, then what removes the risk of paying online now
        "end_said": "le prix de la page, « accès immédiat » et la garantie (ou le paiement par mobile money)",
        "end_written": "le prix et « accès immédiat »",
        "on_set": ("Le produit se montre à l'écran : le téléphone ou l'ordinateur dans le cadre, ouvert sur ce que "
                   "l'acheteur reçoit (un module, un assistant, un résultat). Jamais une boîte ni une couverture inventée."),
    },
    "webinar": {
        "label": "webinaire",
        "event": "CompleteRegistration", "event_fr": "inscription", "result": "inscription", "results": "inscriptions",
        "cost_label": "coût par inscription",
        # a dated live: its ads stop on the day of the event, so two weeks live is already a budget that pays
        "proof_days": 14,
        "end_said": "le jour, l'heure (GMT) et « gratuit », puis « inscris-toi »",
        "end_written": "le jour, l'heure GMT et « GRATUIT »",
        "on_set": ("Ce que le live apprend se montre : le téléphone ou l'ordinateur dans le cadre, ouvert sur l'écran "
                   "dont tu parles. Jamais une affiche de formation."),
    },
}


# a digital product has sales, not orders placed then delivered: the same sums, said in its words
DIGITAL_WORDS = [
    ("des commandes passées sont payées au final : Meta montre le coût par commande passée, c'est donc la colonne "
     "« pub max » qu'il faut comparer au coût par achat du Gestionnaire.",
     "des ventes restent payées après les remboursements : c'est la colonne « pub max » qu'il faut comparer au coût "
     "par achat du Gestionnaire."),
    ("des commandes payées au final", "des ventes gardées après les remboursements"),
    ("Marge par commande livrée", "Marge par vente gardée"),
    ("Pub max par commande passée", "Pub max par vente"),
    ("par commande passée", "par vente"),
    ("par commande livrée", "par vente gardée"),
    ("Ce que peut coûter une commande", "Ce que peut coûter une vente"),
    ("aucun coût par commande", "aucun coût par vente"),
    ("chaque commande perd", "chaque vente perd"),
    ("sans commande", "sans vente"),
]


def cta_what(cta, ws):
    """What a CTA type adds, in the words of the workspace's kind (a digital product has no parcel to open)."""
    c = CTA.get(cta) or CTA["standard"]
    return (c.get("by_kind") or {}).get(kind_of(ws)) or c["what"]


def printer(ws):
    """print(), in the words of the workspace's kind."""
    import builtins
    return lambda *x, **k: builtins.print(*[say(ws, str(i)) for i in x], **k)


def say(ws, text):
    """A sentence written for a product, in the words of the workspace's kind (only « digital » differs today)."""
    if kind_of(ws) != "digital":
        return text
    for a, b in DIGITAL_WORDS:
        text = text.replace(a, b)
    return text


def kind_of(ws):
    k = str((ws or {}).get("kind") or "product").strip().lower()
    return k if k in KINDS else "product"


def profile(ws):
    return dict(PROFILES[kind_of(ws)], kind=kind_of(ws), objections=OBJECTIONS[kind_of(ws)])


def objections(ws):
    return OBJECTIONS[kind_of(ws)]


# ------------------------------------------------------------------ the end of a digital product's script

ACCESS = (r"\bacc[eè]s (?:imm[ée]diat|tout de suite|direct|instantan[ée]|à vie|a vie)|\btout de suite\b|\bimm[ée]diatement\b|"
          r"\bdans (?:la minute|les minutes|5 minutes)\b|\binstant access\b|\bright away\b|\bd[eè]s (?:le paiement|maintenant)\b")
RISK = (r"\bgaranti\w*|\brembours\w*|\bsatisfait\b|\bmoney[- ]back\b|\brefund|\bmobile money\b|\borange money\b|\bwave\b|"
        r"\bmomo\b|\bsans carte\b")


def digital_end(text):
    """What a digital product's ending says beyond the price: {access, risk} → True/False."""
    t = str(text or "").lower()
    return {"access": bool(re.search(ACCESS, t)), "risk": bool(re.search(RISK, t))}


# ------------------------------------------------------------------ the end of a webinar script

DAY = (r"\b(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|demain|ce soir|aujourd'hui|monday|tuesday|wednesday|"
       r"thursday|friday|saturday|sunday|tomorrow|tonight)\b|\b\d{1,2}(?:er)? (?:janv|fevr|févr|mars|avril|mai|juin|juil|"
       r"aout|août|sept|oct|nov|dec|déc)\w*|\b\d{1,2}/\d{1,2}\b|\[jour\]|\[date\]")
# « 19 h », « 19h30 », « 19:00 », « 7 pm », and what Whisper writes when it hears « dix-neuf heures »
# « jeudi 12 novembre », « samedi 7/11 »: the day with its date, when the page gives both
DAY_FULL = (r"\b(?:lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|monday|tuesday|wednesday|thursday|friday|saturday|"
            r"sunday)\s+(?:\d{1,2}(?:er)?\s+(?:janv|fevr|févr|mars|avril|mai|juin|juil|aout|août|sept|oct|nov|dec|déc)\w*"
            r"(?:\s+\d{4})?|\d{1,2}/\d{1,2}(?:/\d{2,4})?)")
HOUR = r"\b\d{1,2} ?(?:h|heures?)(?: ?\d{2})?\b|\b\d{1,2}:\d{2}\b|\b\d{1,2} ?(?:am|pm)\b|\[heure\]|\b(?:midi|minuit)\b|\b[a-z-]+ heures\b"
FREE = r"\bgratuit\w*|\bfree\b|\b0 (?:f|franc|fcfa)\b"
SIGN_UP = r"\binscri\w*|\bregist\w*|\bsign ?up\b|\breserve\w* ta place|\bclique\w*|\bclick\b|\brejoin\w*"


def event_facts(text):
    """What a sign-up page says about the live: the day and the hour as written, free or not."""
    t = str(text or "")
    low = t.lower()
    day = re.search(DAY_FULL, low) or re.search(DAY, low)
    hour = re.search(HOUR, low)
    replay = bool(re.search(r"\breplay|\brediffusion|\benregistr", low)) and not re.search(
        r"\b(?:pas de|sans|aucun|no)\s+(?:replay|rediffusion|enregistrement)", low)
    return {"day": t[day.start():day.end()].strip() if day else "", "hour": t[hour.start():hour.end()].strip() if hour else "",
            "free": bool(re.search(FREE, low)), "replay": replay}


def event_end(text):
    """What a webinar ending says: {day, hour, free, sign_up} → True/False."""
    t = str(text or "").lower()
    return {"day": bool(re.search(DAY, t)), "hour": bool(re.search(HOUR, t)), "free": bool(re.search(FREE, t)),
            "sign_up": bool(re.search(SIGN_UP, t))}


# ------------------------------------------------------------------ the call to action: one type per creative
# Richie, 06/11/2026: the end of every video must not be the same call. The kind's own end (the price and payment on
# delivery, the access, the day and the hour) stays in every script; the CTA type is what is said on top of it, chosen
# by the script. Urgency numbers stay blank ([N], [date]) until they are true.

CTA = {
    "standard": {"label": "la fin habituelle", "what": "les faits de la fin, puis l'appel direct (« commande », « inscris-toi »)"},
    "urgence": {"label": "urgence", "what": "une limite de temps ou de quantité, chiffres en blanc tant qu'ils ne sont "
                                            "pas vrais : « plus que [N] places », « jusqu'à [jour] minuit »"},
    "exclusivite": {"label": "exclusivité", "what": "pour qui c'est, et pour qui ce n'est pas : « réservé à ceux qui… », "
                                                    "« pas pour les curieux »"},
    "garantie": {"label": "risque retiré", "what": "ce que l'acheteur ne risque pas : « tu paies seulement à la livraison », "
                                                   "« tu ouvres le colis devant le livreur »",
                 "by_kind": {"digital": "ce que l'acheteur ne risque pas : « remboursé sous [N] jours si ça ne te sert "
                                        "pas », « tu testes, et si tu n'apprends rien, tu es remboursé »",
                             "webinar": "ce que l'inscrit ne risque pas : « c'est gratuit », « si tu n'apprends rien, "
                                        "tu pars »"}},
    "defi": {"label": "défi", "what": "une invitation à vérifier soi-même : « je te lance un défi », « viens voir par toi-même »"},
    "mix": {"label": "urgence et exclusivité", "what": "la limite et le public visé, dans la même fin"},
}
CTA_MARKS = {
    "urgence": (r"\bprix de lancement\b|\bplus que\b|\bderni[eè]re?s? (?:places?|jours?|heures?|chance)|\bplaces? limit|\bstock limit|\bil (?:ne )?reste\b|"
                r"\bjusqu'?[àa] (?:ce soir|demain|minuit|dimanche|lundi|mardi|mercredi|jeudi|vendredi|samedi|\[)|"
                r"\b(?:ce soir|aujourd'hui) seulement\b|\bavant (?:ce soir|demain|minuit|dimanche|la fin|le \d|\[)|"
                r"\bferme (?:ce soir|demain|dimanche|bient)|\ble prix (?:remonte|augmente|change)|\[n\]|\[nombre\]|"
                r"\bmaintenant ou jamais\b|\bpas de deuxi[eè]me|\bne (?:reviendra|reviens) pas\b"),
    "exclusivite": (r"\br[ée]serv[ée]e?s? (?:aux?|à|a|pour)\b|\bseulement pour (?:ceux|celles|toi|les)|\buniquement (?:pour|aux?)\b|"
                    r"\bpas pour (?:tout le monde|les curieux|toi si)|\bsi tu n'?es pas\b|\bseul(?:e|s)? (?:ceux|celles|les)\b|"
                    r"\bpas de replay\b|\bune seule fois\b|\bsur invitation\b|\ben priv[ée]e?\b|\bgroupe ferm|\bcercle\b|"
                    r"\bje ne (?:le )?(?:referai|refais|referais) pas\b|\bpas pour les\b"),
    "garantie": RISK + (r"|\bsi tu n'?apprends rien\b|\btu ne perds rien\b|\bsans risque\b|\bouvr\w* le colis\b|"
                        r"\btu v[ée]rifies? (?:avant|devant)\b|\brien [àa] payer\b|\btu n'?as rien pay"),
    "defi": r"\bje te (?:lance|d[ée]fie)\b|\bd[ée]fi\b|\bviens? (?:v[ée]rifier|voir par toi)|\bjuge par toi|\bteste par toi|\bpar toi-m[eê]me\b",
}


def cta_of(c):
    """The CTA type of a creative (strategy) or a brief: standard when none is set."""
    v = str((c or {}).get("cta") or "standard").strip().lower()
    v = {"exclusivité": "exclusivite", "défi": "defi", "urgency": "urgence", "exclusivity": "exclusivite",
         "risk": "garantie", "challenge": "defi"}.get(v, v)
    return v if v in CTA else "standard"


def cta_marks(text):
    """What a script's end does beyond the facts: {urgence, exclusivite, garantie, defi} → True/False."""
    t = str(text or "").lower()
    return {k: bool(re.search(p, t)) for k, p in CTA_MARKS.items()}


def cta_missing(cta, text):
    """What a CTA type asks the end to say and the end doesn't: a list of type names (empty when it holds)."""
    m = cta_marks(text)
    need = {"urgence": ["urgence"], "exclusivite": ["exclusivite"], "garantie": ["garantie"], "defi": ["defi"],
            "mix": ["urgence", "exclusivite"]}.get(cta, [])
    return [k for k in need if not m[k]]


def cta_invented_number(text):
    """An urgency number written as a fact (« plus que 12 places ») instead of a blank: the number, or ''."""
    m = re.search(r"\b(?:plus que|il (?:ne )?reste(?: plus que)?|seulement|limit[ée]e?s? [àa])\s+(\d+)\s+(?:places?|jours?|heures?|"
                  r"pi[eè]ces?|unit[ée]s?|personnes?|stocks?)", str(text or "").lower())
    return m.group(1) if m else ""
