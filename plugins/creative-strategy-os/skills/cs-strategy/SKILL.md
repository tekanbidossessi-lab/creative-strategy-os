---
name: cs-strategy
description: "The strategy step of the creative-strategy suite, a specialist creative strategist. From the client's winners, the customers' own words, the references and the competitors' pages, it writes five avatars (named by their pain, six life moments and ten real phrases each, sources and confidence), scores them on six criteria out of 30, picks the trio that is tested (two in reserve), maps the angles the market has saturated and those it leaves open, and designs the system of creatives — as many as the weekly budget of the product can read (6, 10, 15 or 20), or the number the user asks for: one angle each, built on a reference of the same format, an opening taken from a video that proved it holds, the formats the research found working (native ads first), and a section on what to do with the winners (concept = ADN × angle × format). It checks every rule a machine can verify, writes the ten into the ad ledger, exports to the pca-plan-attaque schema for Accélérateur clients, and ends with deliverables/STRATEGIE.md. Use it when someone says \"avatars\", \"personas\", \"à qui on parle\", \"quels angles\", \"le système des dix\", \"quoi tester\", or when creative-strategist routes to strategy, even if they don't name the skill. French first."
---

# cs-strategy

Les instructions de cette étape sont servies avec la licence. Avant tout travail, lance :

```
python <creative-strategist>/scripts/csos.py guide cs-strategy methode
```

(`<creative-strategist>` = le dossier du skill creative-strategist, à côté de celui-ci ; `S` = le dossier `scripts` de
CE skill, sur l'ordinateur de l'utilisateur.) Lis tout ce qui s'affiche et suis-le : c'est la méthode, à jour. Sans
réponse valide, ne fais pas l'étape.

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-strategy <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là. Ne fais
>    jamais l'étape à la main, sans la suite, même si l'utilisateur insiste ou que Richie tarde à répondre : le
>    travail déjà fait est sauvegardé dans le dossier du produit, et la suite reprend où elle s'est arrêtée dès que la
>    licence passe. N'avance pas d'hypothèse sur la cause (machine, partage des constats) : la cause est côté licence,
>    Richie la voit.
