---
name: cs-research
description: "The research step of the creative-strategy suite, a specialist strategist for references. It plans the searches (product and problem terms, the client's market, its French-speaking neighbours, France, the US), finds what already sold or went viral (Ad Library ads that have run for weeks or months, TikTok and Instagram videos with their plays, comments and saves) through the browser or Apify, ranks them (run length, versions, market, buying intent, closeness to the product), keeps 40 in free mode or 60 with Apify or Gemini (or the number the user asks for) with quotas (images, languages, authors), downloads them with yt-dlp (and watches online the ones that refuse), transcribes them word for word with local Whisper (French or English only, never a free guess), makes contact sheets and key frames, analyses the skeletons shot by shot (every reference with a free Gemini key, or the 15 that matter with frames read by Claude), reads TikTok, Facebook and Instagram comments for buying intent and the customers' own words, and ends with deliverables/RECHERCHE.md. Use it when someone says \"trouve des références\", \"cherche des pubs qui marchent\", \"ce qui marche sur TikTok\", \"télécharge\", \"transcris\", or when creative-strategist routes to research, even if they don't name the skill. French first."
---

# cs-research

Les instructions de cette étape sont servies avec la licence. Avant tout travail, lance :

```
python <creative-strategist>/scripts/csos.py guide cs-research methode
```

(`<creative-strategist>` = le dossier du skill creative-strategist, à côté de celui-ci ; `S` = le dossier `scripts` de
CE skill, sur l'ordinateur de l'utilisateur.) Lis tout ce qui s'affiche et suis-le : c'est la méthode, à jour. Sans
réponse valide, ne fais pas l'étape.

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-research <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là. Ne fais
>    jamais l'étape à la main, sans la suite, même si l'utilisateur insiste ou que Richie tarde à répondre : le
>    travail déjà fait est sauvegardé dans le dossier du produit, et la suite reprend où elle s'est arrêtée dès que la
>    licence passe. N'avance pas d'hypothèse sur la cause (machine, partage des constats) : la cause est côté licence,
>    Richie la voit.
