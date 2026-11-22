# -*- coding: utf-8 -*-
"""bookparts.py — the texts docs.py --book adds to every strategy book (1.7, 22/11/2026): the mini-course part
and the appendix glossary, for a reader who has never launched an ad. Lines between <!-- quiz --> and <!-- /quiz -->
appear only when the ads lead to a quiz, between <!-- page --> and <!-- /page --> only when they lead to a page.
Kept in a module (not references/) because docs.py runs on the buyer's computer, where only scripts ship."""

MINI_COURS = r"""# Le mini-cours

<!-- Read by docs.py --book (1.7): the part « Le mini-cours », between the briefs and the appendix. Lines between
<!-- quiz --> and <!-- /quiz --> appear only when the ads lead to a quiz (workspace.yaml destination: quiz); between
<!-- page --> and <!-- /page --> only when they lead to a page. {result} and {results} take the words of the kind
(vente, commande, inscription). Written for someone who has never launched an ad. -->

> **À quoi sert cette partie** : comprendre ce qu'il y a derrière les briefs, pour lire tes chiffres, corriger une pub
> qui ne marche pas et faire les suivantes sans attendre personne. Lis-la avant le troisième jour du test.

## Les trois premières secondes

Sur Facebook et Instagram, la personne fait défiler son fil avec le pouce. Elle décide en moins de trois secondes si
elle s'arrête. Si la première image et la première phrase ne l'arrêtent pas, le reste de la vidéo n'existe pas pour
elle, aussi bon soit-il.

C'est pour ça que chaque brief reprend son ouverture d'une vidéo qui a déjà prouvé qu'elle arrête les gens : une pub
qui tourne depuis des mois, ou une vidéo vue des centaines de milliers de fois. On ne réinvente pas l'ouverture, on
reprend celle qui a marché et on la tourne vers ton produit.

## La référence pour la structure, l'avatar pour les mots

Chaque script part d'une pub qui a déjà vendu, transcrite mot pour mot. On garde son squelette : qui parle, dans quel
ordre, ce que fait chaque moment, et ses phrases signature presque telles quelles. Ce qui change, c'est ce qui doit
changer pour ton produit : le problème, la promesse, l'offre, et les mots de tes clients.

Les mots de tes clients viennent de vrais commentaires, recopiés avec leurs fautes. Une personne qui entend ses propres
mots dans une pub a l'impression qu'on parle d'elle. Et on ne dilue jamais : si la référence est crue, directe ou
choquante, ton script l'est autant. Un mot poli à la place d'un mot cru fait perdre ce qui faisait marcher la pub.

## Les pubs natives, en vidéo et en image

Une pub native ne ressemble pas à une pub. Elle ressemble à ce que la personne voit d'habitude dans son fil : une
vidéo filmée au téléphone, quelqu'un qui raconte, une réaction, une capture de message, une photo du quotidien avec une
phrase écrite dessus. Les gens se méfient des pubs qui ont l'air de pubs ; ils regardent ce qui ressemble à la vie.

Une image native, c'est une photo brute (pas de filtre, pas de décor de magazine) avec sa première ligne posée dessus,
en gros, et un texte long écrit à la première personne en dessous. Elle coûte presque rien à produire et elle se teste
aussi bien qu'une vidéo.

<!-- quiz -->
## Pourquoi la pub vend le test, pas le produit

Ta page d'arrivée est un quiz. La pub ne vend donc rien : elle donne envie de faire le test gratuit. C'est le quiz
qui pose les questions, qui montre à la personne ce qui lui arrive, et qui présente l'offre à la fin, au moment où
elle est prête à l'entendre.

Trois règles en découlent. La pub ne montre ni le prix, ni l'offre, ni la garantie. Chaque promesse de la pub est une
chose que le quiz donne vraiment : si la pub promet ce que le quiz ne donne pas, la personne se sent trompée et
quitte le test. Et chaque pub amène quelqu'un à qui le quiz parle : une personne que le quiz n'accueille pas paie un
clic et ne finit jamais le test.
<!-- /quiz -->

## Pourquoi plusieurs idées, et pas une

Personne ne sait à l'avance quelle pub va marcher, pas même un stratège qui fait ça depuis des années. Ce qu'on sait,
c'est que sur dix idées vraiment différentes, une ou deux portent la plupart des {results}. Le test sert à les
trouver vite et pour peu d'argent.

C'est pour ça que les vidéos du test ne sont pas la même vidéo avec une autre phrase : elles changent d'avatar, d'angle,
de format et de niveau de conscience. Si elles se ressemblent toutes, le test ne t'apprend rien.

## Lire tes chiffres

Ne juge rien avant trois jours et environ 2 000 impressions par pub : avant, les chiffres bougent au hasard. Ensuite,
lis-les dans cet ordre, du haut de la vidéo vers la {result} :

- **L'accroche** (la part des gens qui regardent les 3 premières secondes) : dit si l'ouverture arrête les gens.
- **La rétention** (la part qui regarde jusqu'au bout, ou 15 secondes) : dit si le corps de la vidéo tient.
- **Le taux de clic sur le lien** : dit si la fin donne envie d'aller plus loin.
- **Le coût par {result}** : dit si tout le chemin, de la pub à la page, rapporte plus qu'il ne coûte.
- **Le CPM** (le prix de 1 000 affichages) : quand il est très haut, Meta montre mal la pub ; ce n'est pas toujours
  la faute de la vidéo.

<!-- quiz -->
Avec un quiz, trois chiffres du milieu disent où le chemin casse : **combien arrivent sur le quiz** (les clics qui
chargent vraiment la page), **combien finissent le quiz** (si beaucoup partent en route, le problème est dans les
questions, pas dans la pub), et **combien arrivent à l'offre puis achètent** (si beaucoup finissent mais peu achètent,
le problème est dans l'offre ou dans la page de résultat).
<!-- /quiz -->

## Du chiffre à la correction

Chaque chiffre faible désigne la partie de la vidéo qui a lâché. On change cette partie-là, et on garde tout le reste
mot pour mot :

- accroche faible : on change l'ouverture (la première image et la première phrase), pas le reste ;
- accroche bonne, rétention faible : le corps ne tient pas la promesse de l'ouverture ;
- rétention bonne, peu de clics : la fin n'appelle pas assez clairement à l'action ;
- beaucoup de clics, peu de {results} : le problème est après la pub (la page, le quiz, l'offre, le prix).

Une pub qui a dépensé deux fois le coût visé sans aucune {result} est coupée. Un avatar dont toutes les pubs perdent
laisse sa place au suivant de la réserve.

## La boucle créative

Une stratégie n'est jamais finie. Chaque cycle suit la même boucle : chercher ce qui marche déjà, écrire, produire,
lancer, lire les chiffres, garder ce qui gagne, changer ce qui perd, et recommencer. Chaque tour t'apprend quelque
chose sur tes clients que tu ne savais pas au tour d'avant, et le tour suivant part de là.

## Les variations des gagnantes

Quand une vidéo gagne, on ne passe pas à autre chose : on la décline. Une variation change une seule chose à la fois
(l'ouverture, la personne, le décor, la durée, le format, la fin) et garde tout le reste mot pour mot. Si on change
trois choses en même temps et que la variation gagne, on ne sait pas laquelle a compté.

Une gagnante finit toujours par s'user : les mêmes personnes la voient trop souvent et le coût monte. Les variations
la remplacent avant qu'elle s'épuise.

## Teste petit, puis grandis

Le test se fait avec un petit budget, réparti également entre les ensembles, pour que chaque idée ait sa chance. On
n'augmente le budget que sur ce qui a prouvé qu'il rapporte, et par paliers (environ 20 % tous les deux ou trois jours),
pour que Meta ne perde pas ce qu'il a appris. Doubler le budget d'un coup sur une pub qui marche la casse souvent.

## Ce qu'on attend de toi

- Produire les vidéos à partir de leur brief, sans changer les mots de la référence ni l'ouverture.
- Envoyer chaque vidéo pour contrôle avant qu'elle parte en ligne.
- Lancer le test tel qu'il est écrit, et ne rien toucher pendant trois jours.
- Envoyer l'export des résultats quand on te le demande, avec les bonnes colonnes.
- Dire ce que tes clients te disent : leurs questions, leurs doutes, leurs mots. Ce sont les idées des prochaines pubs.
"""

GLOSSAIRE = r"""# Le glossaire

<!-- Read by docs.py --book (1.7): the appendix's glossary, one sentence per word, for a reader who has never
launched an ad. Lines between <!-- quiz --> and <!-- /quiz --> appear only with destination: quiz. -->

- **Accroche** : la part des gens qui regardent les trois premières secondes d'une vidéo ; elle dit si l'ouverture arrête le pouce.
- **Angle** : la porte par laquelle on entre dans le désir de l'avatar (la peur, la fierté, la honte, la curiosité, l'argent…).
- **Avatar** : une personne précise à qui la pub parle, décrite par sa douleur, ses moments de vie et ses propres mots.
- **Brief** : la page qui dit tout ce qu'il faut pour produire une vidéo seul, sans poser de question.
- **Campagne, ensemble de pubs, pub** : les trois étages du Gestionnaire de publicités de Meta ; la campagne porte l'objectif, l'ensemble porte le budget et l'audience, la pub porte la vidéo et son texte.
- **ABO** : le budget fixé ensemble par ensemble, pour que chaque idée testée reçoive la même somme.
- **CPM** : le prix payé pour 1 000 affichages de la pub.
- **CTR (taux de clic)** : la part des gens qui cliquent sur le lien après avoir vu la pub.
- **Coût par vente (ou par commande, par inscription)** : ce que la pub a coûté, divisé par le nombre de ventes qu'elle a amenées.
- **Format** : la forme de la pub : face caméra, voix off, sketch, réaction, image, carte de texte…
- **Gagnante** : une pub qui amène des ventes à un coût qui laisse une marge ; on la garde et on la décline.
- **Niveau de conscience** : ce que la personne sait déjà de son problème et des solutions, de « je ne sais pas que j'ai un problème » à « je connais ton produit ».
- **Pixel** : un petit code posé sur la page qui dit à Meta qui a acheté, pour qu'il trouve des gens qui leur ressemblent.
- **Pub native** : une pub qui ressemble à ce que la personne voit d'habitude dans son fil, pas à une publicité.
- **Référence** : une pub ou une vidéo qui a déjà prouvé qu'elle marche (longue diffusion, beaucoup de vues), dont on reprend la structure.
- **Rétention** : la part des gens qui regardent la vidéo jusqu'au bout (ou 15 secondes).
- **Tunnel** : le chemin complet de la personne, de la pub jusqu'à l'achat.
- **Variation** : une copie d'une gagnante où l'on change une seule chose pour la faire durer.
<!-- quiz -->
- **Quiz** : la page d'arrivée qui pose des questions, montre un résultat et présente l'offre à la fin.
- **Taux de fin de quiz** : la part des gens qui commencent le quiz et arrivent jusqu'au résultat.
<!-- /quiz -->
"""
