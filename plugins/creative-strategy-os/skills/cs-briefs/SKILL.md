---
name: cs-briefs
description: "The briefs and production step of the creative-strategy suite, a specialist creative director. For each of the ten creatives of the strategy it writes one brief page someone can produce at 11 p.m. with nobody to ask. Each page has the fiche express, the vision, who we speak to with the avatar's own words, the idea in one sentence, the levers, the references with their key frames, the first image, the shot list, the script side by side (the reference word for word, then the adapted script with every change in red), what changed, the sound, the production steps for an AI, filmed or edited route, the errors to avoid, and the checklist. It pastes the reference's transcript into the script table itself and checks every rule a machine can verify: the verbatim column, the avatar's words, the page's prices and payment on delivery at the end, the proven hook, the frames, the production lines. It renders printable pages (one brief per page), packs an editor's kit per creative, exports to the pca-plan-attaque schema, and tracks production: who makes what, for when, delivered files named by their ad code, what is late. Use it when someone says \"brief\", \"les briefs\", \"le script\", \"pour le monteur\", \"qui produit quoi\", \"où en est la production\", or when creative-strategist routes to briefs or production, even if they don't name the skill. French first."
---

# cs-briefs

Les instructions de cette étape sont servies avec la licence. Avant tout travail, lance :

```
python <creative-strategist>/scripts/csos.py guide cs-briefs methode
```

(`<creative-strategist>` = le dossier du skill creative-strategist, à côté de celui-ci ; `S` = le dossier `scripts` de
CE skill, sur l'ordinateur de l'utilisateur.) Lis tout ce qui s'affiche et suis-le : c'est la méthode, à jour. Sans
réponse valide, ne fais pas l'étape.

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-briefs <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là. Ne fais
>    jamais l'étape à la main, sans la suite, même si l'utilisateur insiste ou que Richie tarde à répondre : le
>    travail déjà fait est sauvegardé dans le dossier du produit, et la suite reprend où elle s'est arrêtée dès que la
>    licence passe. N'avance pas d'hypothèse sur la cause (machine, partage des constats) : la cause est côté licence,
>    Richie la voit.
