---
name: cs-read
description: "The reading step of the creative-strategy suite, a specialist who reads ad results the way Richie teaches. It imports the Meta or TikTok export at ad level (the « Lecture créa » columns: 3-second plays, ThruPlays, link clicks, landing page views, purchases), finds each ad by its code (C## V# L) in the ledger, and adds up an ad that moved between campaigns. It reads the delivery report for cash on delivery (ordered, confirmed, delivered, cost per delivered order). It gives each ad a verdict with its cause and the action to take: wait (before 2 000 impressions and 3 days), cut (twice the target cost per order spent without an order), winner, keep, or fix, with the diagnosis (the opening, the body, the message, the page, the offer, a CPM Meta dislikes, fatigue over the last 7 days). It also says which avatar doesn't respond and which reserve avatar comes in, what the losers share, and the account's own medians. It ends with deliverables/LECTURE.md and the list of gestures for the ads manager, and stores the winners' building blocks for the variations. Use it when someone says \"mes résultats\", \"lis l'export\", \"quelle pub couper\", \"ça marche ?\", \"mon coût par achat monte\", \"les chiffres\", or when creative-strategist routes to read, even if they don't name the skill. French first."
---

# cs-read

Les instructions de cette étape sont servies avec la licence. Avant tout travail, lance :

```
python <creative-strategist>/scripts/csos.py guide cs-read methode
```

(`<creative-strategist>` = le dossier du skill creative-strategist, à côté de celui-ci ; `S` = le dossier `scripts` de
CE skill, sur l'ordinateur de l'utilisateur.) Lis tout ce qui s'affiche et suis-le : c'est la méthode, à jour. Sans
réponse valide, ne fais pas l'étape.

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-read <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là. Ne fais
>    jamais l'étape à la main, sans la suite, même si l'utilisateur insiste ou que Richie tarde à répondre : le
>    travail déjà fait est sauvegardé dans le dossier du produit, et la suite reprend où elle s'est arrêtée dès que la
>    licence passe. N'avance pas d'hypothèse sur la cause (machine, partage des constats) : la cause est côté licence,
>    Richie la voit.
