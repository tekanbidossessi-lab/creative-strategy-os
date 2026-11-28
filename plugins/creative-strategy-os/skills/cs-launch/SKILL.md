---
name: cs-launch
description: "The launch step of the creative-strategy suite, a specialist media buyer for small budgets. From the strategy's five ad sets and the reviewed creatives it writes the test campaign for Meta or TikTok. Every campaign, ad set and ad gets its name from the naming system (C## V# L, uppercase, no underscore), with the settings (sales objective, purchase event, budget per ad set, broad audience, automatic placements), the pixel and the destination without URL parameters. Each ad gets the shared ad text (a mini product page from cs-offer) or its own caption. It checks the names, the 5 × 2 structure at equal budgets, that every ad is delivered and reviewed, the budget against the day's, the pixel, the link, and the prices of every text against the page. It writes the launch sheet (Markdown and printable HTML) with the first seven days in numbers: when to judge, when to cut, what a winner is. It records what went live, with its date and Meta id, in the ad ledger. Use it when someone says \"lancer\", \"mettre en ligne\", \"la campagne\", \"fiche de lancement\", \"les noms des pubs\", \"quel budget\", or when creative-strategist routes to launch, even if they don't name the skill. French first."
---

# cs-launch

Les instructions de cette étape sont servies avec la licence. Avant tout travail, lance :

```
python <creative-strategist>/scripts/csos.py guide cs-launch methode
```

(`<creative-strategist>` = le dossier du skill creative-strategist, à côté de celui-ci ; `S` = le dossier `scripts` de
CE skill, sur l'ordinateur de l'utilisateur.) Lis tout ce qui s'affiche et suis-le : c'est la méthode, à jour. Sans
réponse valide, ne fais pas l'étape.

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-launch <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là. Ne fais
>    jamais l'étape à la main, sans la suite, même si l'utilisateur insiste ou que Richie tarde à répondre : le
>    travail déjà fait est sauvegardé dans le dossier du produit, et la suite reprend où elle s'est arrêtée dès que la
>    licence passe. N'avance pas d'hypothèse sur la cause (machine, partage des constats) : la cause est côté licence,
>    Richie la voit.
