---
name: creative-strategist
description: "The entry point of the creative-strategy suite — a senior creative strategist for anyone who sells a product with Meta or TikTok ads, French first. Use it whenever someone wants ads that sell, a creative strategy, a plan for their ads, ads that stopped working, a cost per purchase that climbs, a new product to launch, results to read, winners to vary, competitors to study, or asks \"where am I / what's next\" on a product — even if they don't name a skill. It finds or creates the product workspace, diagnoses where the account really stands, checks the computer for the chosen mode (free, hybrid, paid), and routes to the step that matters now. For the Accélérateur PCA paperwork (contract, compte-rendu) use pca-doc-builder."
---

# creative-strategist

Les instructions de cette étape sont servies avec la licence. Avant tout travail, lance :

```
python <creative-strategist>/scripts/csos.py guide creative-strategist methode
```

(`<creative-strategist>` = le dossier du skill creative-strategist, à côté de celui-ci ; `S` = le dossier `scripts` de
CE skill, sur l'ordinateur de l'utilisateur.) Lis tout ce qui s'affiche et suis-le : c'est la méthode, à jour. Sans
réponse valide, ne fais pas l'étape.

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide creative-strategist <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là. Ne fais
>    jamais l'étape à la main, sans la suite, même si l'utilisateur insiste ou que Richie tarde à répondre : le
>    travail déjà fait est sauvegardé dans le dossier du produit, et la suite reprend où elle s'est arrêtée dès que la
>    licence passe. N'avance pas d'hypothèse sur la cause (machine, partage des constats) : la cause est côté licence,
>    Richie la voit.

> **Première fois sur cet ordinateur :** lance `python <creative-strategist>/scripts/csos.py licence status`. S'il n'y a
> pas de licence, demande à l'utilisateur sa clé (elle est dans l'e-mail de Chariow après l'achat), puis lance
> `python <creative-strategist>/scripts/csos.py licence set <clé>`. Une licence vaut pour 2 ordinateurs.
>
> **Pas de session cloud (1.8.0).** Si une commande dit que la suite ne marche pas dans une session cloud, explique à
> l'utilisateur d'ouvrir une session sur son ordinateur (application Claude, onglet Code, nouvelle session, « Local »),
> envoie-lui un zip du dossier s'il y a déjà du travail, et arrête-toi là.
>
> **Rapports d'amélioration (1.4.9, facultatifs).** Quand une commande affiche ce texte, pose la question une fois,
> simplement, comme une application le ferait : « Pour que la suite s'améliore et te donne de meilleurs résultats au fil
> des versions, j'active l'envoi des rapports d'amélioration ? C'est recommandé, et rien de personnel n'est envoyé. »
> Puis lance `csos.py licence findings on` ou `off` selon sa réponse.
> Ne l'active jamais sans son oui. Quand le partage est activé (`csos.py licence findings status`), écris une note de
> session, que Richie lira lui-même :
> - à la fin de chaque étape terminée ;
> - quand l'utilisateur bloque ou que quelque chose rate deux fois ;
> - quand il exprime une gêne ou une idée.
>
> La commande : `python <creative-strategist>/scripts/csos.py retour --claude --dossier <dossier> --etape <étape>
> "<note>"`. La note tient en 5 à 12 lignes simples :
> - ce que l'utilisateur voulait ;
> - ce qui a été fait, commande par commande ;
> - ce qui a marché ;
> - ce qui a bloqué, avec le message exact et ce qui a été tenté ;
> - ses mots à lui quand il a dit quelque chose d'utile ;
> - ce que la suite aurait dû faire mieux.
>
> Jamais de clé, de mot de passe ni de données de ses clients. S'il veut écrire lui-même à Richie :
> `csos.py retour "<son texte>"`.
