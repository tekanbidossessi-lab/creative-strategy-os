# Creative Strategy OS — le guide d'utilisation

*Version 1.3.2 · pour Windows et Mac*

## Ce que fait Creative Strategy OS

Tu vends un produit avec des pubs Facebook, Instagram ou TikTok. Creative Strategy OS fait avec toi le travail d'un stratège créatif. Il lit ta page et regarde ce que vendent tes concurrents. Il trouve les pubs et les vidéos qui ont déjà vendu ou retenu l'attention, décide à qui parler et avec quels angles, puis écrit les scripts à partir de ces références. Ensuite il contrôle tes vidéos avant qu'elles partent, prépare la campagne, lit les résultats et te dit quoi faire après.

Tu lui parles en français, comme à quelqu'un de ton équipe. Tu ne tapes aucune commande : c'est Claude qui les lance. À chaque étape, il te dit ce qu'il fait, ce que tu dois faire et ce qui vient après.

Les dix étapes, dans l'ordre :

1. **L'entrée** : ta page, ce qu'une commande peut te coûter en pub, ton pixel, ton compte publicitaire.
2. **L'offre** : ce que vendent les concurrents (avec leurs liens), ton offre, ta page section par section, le texte de la pub, l'appel de confirmation.
3. **La recherche** : 40 à 60 pubs et vidéos qui ont prouvé quelque chose, transcrites mot pour mot.
4. **La stratégie** : tes avatars, les angles, et le système de créatives à tester.
5. **Les briefs** : une page par créative, qu'on produit seul sans poser de question.
6. **La production** : toi, ton monteur ou l'IA, avec deux routes pour chaque vidéo.
7. **Le contrôle** : chaque créative vérifiée avant d'être lancée.
8. **Le lancement** : la campagne, les noms, les réglages, les 7 premiers jours.
9. **La lecture** : ce qui a marché, ce qui n'a pas marché, et pourquoi.
10. **Les variations** : faire durer ce qui gagne.

## Le parcours en une page

Si tu ne lis qu'une partie de ce guide, lis celle-ci.

| | Ce que tu fais | Combien de temps |
|---|---|---|
| 1 | Tu installes la suite une fois (partie « Installer ») | 30 à 60 minutes, surtout de l'attente |
| 2 | Dans l'app Claude, onglet **Code**, tu ouvres ton dossier de travail et tu écris : « Je veux lancer des pubs pour mon produit, voici ma page : <lien> » | 1 minute |
| 3 | Tu réponds à quatre questions en cliquant sur tes choix | 2 minutes |
| 4 | Claude fait les étapes 1 à 5. Après chacune, il complète **ton document de stratégie** et te dit où il est | plusieurs heures de travail de Claude, souvent sur 2 à 4 sessions |
| 5 | Tu lis le document complet, puis tu produis les vidéos à partir des briefs | à ton rythme |
| 6 | Tu envoies chaque vidéo à Claude : il la contrôle, puis prépare la campagne | — |
| 7 | Au jour 7, tu envoies tes chiffres : il te dit quoi couper, quoi garder, quoi décliner | — |

Ensuite, chaque fois que tu reviens, tu écris « On continue ». Claude reprend exactement où il s'était arrêté et te dit ce qui t'attend.

## Ce qu'il te faut

| Quoi | Pourquoi | Prix |
|---|---|---|
| Un abonnement **Claude Pro** au minimum | C'est Claude qui fait le travail. Prends Max si tu suis plusieurs produits à la fois : avec Pro, tu atteins plus vite la limite d'usage et le travail s'étale sur plus de sessions. | abonnement Claude |
| **L'app Claude** pour ordinateur (Windows ou Mac) | La suite s'utilise dans son onglet **Code**. | gratuite avec l'abonnement |
| **Python 3.11** ou plus récent | Les outils de la suite tournent avec. Le script d'installation le met s'il manque. | gratuit |
| Les **outils de la suite** : Whisper (transcription), yt-dlp (téléchargement), ffmpeg, et quelques bibliothèques | Le script d'installation les installe tous. | gratuit |
| **Google Chrome** et l'extension **Claude dans Chrome** | Claude cherche dans la Bibliothèque publicitaire, sur TikTok et Instagram, et lit les commentaires. Connecte ce Chrome à Facebook, Instagram et TikTok : Claude ne fait que lire, il ne publie rien. | gratuit |
| **Word** ou **LibreOffice** | Pour les PDF de tes documents. | LibreOffice est gratuit |
| Un ordinateur avec **8 Go de mémoire** et **10 Go libres** | Les vidéos de référence et la transcription. | — |
| *Facultatif* : une **clé Gemini gratuite** | Toutes les références sont analysées plan par plan, sans entamer ton usage Claude. | gratuit |
| *Pour produire* : **Google Flow** (Veo ou Omni Flash), **ElevenLabs**, **CapCut** | Les images, les vidéos, les voix, le montage. | offres gratuites, payantes pour plus de crédits |

## Installer (une seule fois)

Fais les étapes dans l'ordre. Ne saute pas l'étape 3 : la suite doit atterrir dans le bon dossier, sinon Claude ne la voit pas.

### Sur Windows

**1. L'app Claude.** Télécharge-la sur claude.ai/download, installe-la et connecte-toi avec ton compte Claude. Ouvre l'onglet **Code** une première fois pour vérifier qu'il s'affiche. Puis ferme l'app.

**2. Le fichier de la suite.** Tu as reçu `creative-strategy-os-1.3.2.zip`. Laisse-le dans ton dossier **Téléchargements**. Ne l'ouvre pas en double-cliquant.

**3. Mettre la suite à sa place.** Ouvre le menu Démarrer, tape **PowerShell** et ouvre « Windows PowerShell ». Copie cette ligne, colle-la avec un clic droit, puis appuie sur Entrée :

```
Expand-Archive -Path "$env:USERPROFILE\Downloads\creative-strategy-os-1.3.2.zip" -DestinationPath "$env:USERPROFILE\.claude\skills" -Force
```

Vérifie le résultat : ouvre l'Explorateur de fichiers, colle `%USERPROFILE%\.claude\skills` dans la barre d'adresse et appuie sur Entrée. Tu dois voir **dix dossiers** (creative-strategist, cs-briefs, cs-intake, cs-iterate, cs-launch, cs-offer, cs-read, cs-research, cs-review, cs-strategy) et un fichier `manifest.json`. Si tu vois un seul dossier nommé `creative-strategy-os-1.3.2`, c'est qu'il a été décompressé autrement : ouvre-le, sélectionne tout ce qu'il contient, et déplace-le d'un niveau, directement dans `skills`.

**4. Les outils.** Dans la même fenêtre PowerShell, colle cette ligne et appuie sur Entrée :

```
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.claude\skills\creative-strategist\scripts\setup\setup_windows.ps1"
```

Le script installe ce qui manque : Python, Chrome, LibreOffice si tu n'as pas Word, et les outils de la suite. Compte 10 à 30 minutes selon ta connexion. Si Windows te demande d'autoriser une installation, réponds oui. À la fin, il affiche une liste : `[ok]` en vert, ce qui manque en jaune avec la solution.

Si tu lis « Python n'est pas encore visible », c'est normal la première fois. Ferme PowerShell, ouvre-en un nouveau, et relance la même ligne. La deuxième fois, il installe les outils.

**5. Claude dans Chrome.** Dans Chrome, va sur claude.ai/chrome, clique sur « Ajouter à Chrome » et connecte-toi avec ton compte Claude. Dans ce même Chrome, connecte-toi à Facebook, Instagram et TikTok.

**6. Facultatif : la clé Gemini.** Va sur aistudio.google.com/apikey et clique sur « Create API key » (un compte Google suffit, pas de carte). Dans PowerShell, tape `setx GEMINI_API_KEY "ta clé"` en remplaçant ta clé. Ferme ensuite complètement l'app Claude, puis rouvre-la.

### Sur Mac

**1. L'app Claude.** Télécharge-la sur claude.ai/download, installe-la, connecte-toi et ouvre l'onglet **Code** une première fois. Puis ferme l'app.

**2 et 3. Mettre la suite à sa place.** Laisse le zip dans **Téléchargements**. Ouvre le Terminal (Cmd + Espace, tape « Terminal »), colle cette ligne et appuie sur Entrée :

```
mkdir -p ~/.claude/skills && unzip -o ~/Downloads/creative-strategy-os-1.3.2.zip -d ~/.claude/skills
```

Pour vérifier, colle `open ~/.claude/skills` dans le Terminal : tu dois voir les dix dossiers et `manifest.json`.

**4. Les outils.** Dans le Terminal : `bash ~/.claude/skills/creative-strategist/scripts/setup/setup_mac.sh`. Si le site de Python s'ouvre, installe la version pour macOS, puis relance la même ligne.

**5. Claude dans Chrome**, comme sur Windows.

**6. Facultatif : la clé Gemini.** Ajoute la ligne `export GEMINI_API_KEY="ta clé"` à la fin du fichier `~/.zshrc`, puis ferme et rouvre l'app Claude.

### Vérifier que tout est prêt

1. Crée un dossier pour ton travail, par exemple `Documents\Mes produits`. Chaque produit y aura son sous-dossier, que Claude crée lui-même.
2. Ouvre l'app Claude, onglet **Code**, et choisis ce dossier comme dossier de travail.
3. Écris : « Vérifie que tout est prêt pour Creative Strategy OS. »

Claude lance le contrôle et te répond ligne par ligne : ce qui marche, ce qui manque, et la solution exacte. Une ligne jaune ne bloque rien : la suite passe par un autre outil.

**Les autorisations.** Dans l'onglet Code, Claude te demande la permission avant de lancer une commande ou d'écrire un fichier. Lis la ligne, puis autorise. Les commandes de la suite commencent par `python` et pointent vers `.claude\skills`. Elles ne touchent qu'au dossier de ton produit. Si l'app propose de toujours autoriser ce type de commande, tu peux l'accepter pour travailler sans interruption.

## Les deux parcours

Par défaut, tu reçois le document complet. Si tu veux seulement une étape, dis-le simplement (« juste la lecture de mes résultats »).

| | Le parcours complet (recommandé) | Le parcours par étape |
|---|---|---|
| Pour qui | Tout nouveau produit, même si tu fais déjà des pubs depuis des mois | Quand tu veux une seule chose maintenant : lire tes résultats, décliner une pub gagnante |
| Ce que tu reçois | **Un seul document** : ta stratégie créative complète, de l'entrée jusqu'aux briefs | Un document par étape faite |
| Comment il arrive | Il grandit à chaque étape : après l'entrée, il a une partie ; après les briefs, il en a cinq | À la fin de chaque étape |
| Après | Le lancement, la lecture et les variations ont chacun leur document | Pareil |

**Pourquoi le parcours complet, même si tu as déjà des pubs ?** Parce que chaque partie nourrit la suivante. Les mots de tes clients, lus dans la recherche, deviennent ceux des scripts. Ton offre, corrigée dans la partie 2, est celle que les pubs annoncent. Ton export et tes pubs gagnantes rendent la stratégie plus juste, ils ne la remplacent pas. Sauter des étapes, c'est écrire des briefs sur des suppositions.

**Tu peux changer quand tu veux.** « Fais-moi le document complet » : Claude reprend les étapes qui manquent. « Juste la lecture de mes résultats » : il fait cette étape seule.

## Ton document de stratégie

Dans le parcours complet, tout ce que Claude produit pendant les étapes 1 à 5 va dans un seul document, avec un sommaire cliquable. Tu le trouves toujours au même endroit :

`<le dossier de ton produit>\deliverables\word\STRATEGIE-CREATIVE.pdf` (et le `.docx`, si tu veux le modifier dans Word).

- **Il grandit.** Après chaque étape, Claude le relie avec la nouvelle partie et te le dit. Tant que les briefs n'y sont pas, la couverture porte « version de travail · 3 parties sur 5 », et la page « Commence ici » te dit quelle partie vient ensuite.
- **C'est toujours le même fichier.** La nouvelle version remplace l'ancienne. Si tu veux garder une version, copie-la ailleurs.
- **Ferme-le avant que Claude le relie.** Un document ouvert dans Word ou dans ton lecteur PDF ne peut pas être remplacé. Si Claude te dit « STRATEGIE-CREATIVE.docx est ouvert », ferme-le et dis « c'est fermé ».
- **Les cinq parties** : 1. Le point de départ · 2. L'offre et la page · 3. La recherche · 4. La stratégie · 5. Les briefs. Les vérifications faites par la machine sont en annexe, à la fin.
- **Où en est ton document ?** Ouvre `COMMENCE-ICI.md` à la racine du dossier de ton produit. La partie « Ton document » montre les cinq parties (✅ faite, ⬜ à venir) et la date de la dernière version.

**Les documents d'étape.** Ensuite, et dans le parcours par étape, chaque étape a son document, dans le même dossier `deliverables\word` :

| Étape | Le document |
|---|---|
| La production | PRODUCTION (qui fait quoi, pour quand, ce qui est livré) |
| Le contrôle | CONTROLE (chaque vidéo : bonne à lancer, à corriger ou à refaire) |
| Le lancement | LANCEMENT (la campagne, les noms, les 7 premiers jours) |
| La lecture | LECTURE (le verdict de chaque pub et ce qu'il faut faire) |
| Les variations | VARIATIONS (les prochaines pubs à produire) |
| Sur demande | MONTAGE (le guide de montage d'une créative), BILAN (l'historique du produit) |

Tous tes documents ont la même présentation que ta stratégie : une couverture, un sommaire cliquable avec les numéros de page, et la même ligne en bas de chaque page.

À partir du deuxième cycle de test, tu reçois les documents d'étape : BRIEFS pour les nouvelles créatives, puis LANCEMENT, LECTURE et VARIATIONS. Le document complet reste disponible : demande « relie le document complet ».

## Ton premier produit

Dans l'onglet Code, dans ton dossier de travail, écris simplement : « Je veux lancer des pubs pour mon produit, voici ma page : <lien> ». Claude lit ta page, crée un dossier pour ce produit, puis te pose **quatre questions à choix** : tu cliques sur ta réponse (ou tu écris la tienne dans « Autre »).

- **Ce que tu vends** : un produit physique, un produit numérique ou un webinaire.
- **As-tu déjà fait des pubs sur ce produit ?** Avec ou sans export, ou pas encore.
- **Qui fait les vidéos** : toi, un monteur, ou personne pour l'instant.
- **Ton budget pub par semaine, pour ce produit seulement.** Il décide du nombre de créatives : moins de 70 $, 6 ; jusqu'à 150 $, 10 ; jusqu'à 300 $, 15 ; au-delà, 20.

Puis, en une ligne, ce que ta page ne dit pas : tes pays, ton objectif, et ton export si tu en as un (voir plus bas). Tu reçois le document complet en formule gratuite ; tu peux changer l'un ou l'autre quand tu veux.

Si tu les as, envoie aussi :

- **Des captures d'écran** des commentaires sous tes pubs et des messages WhatsApp de tes clients. Leurs mots deviennent ceux de tes scripts.
- **Le lien de tes pubs qui ont le plus de commentaires** (Gestionnaire de publicités → la pub → « Afficher la publication avec les commentaires »). Claude lit toujours les commentaires Facebook en plus de ceux de TikTok : tes pubs passent sur Facebook, et les acheteurs n'y parlent pas comme sur TikTok.

Ensuite il avance seul. Il ne t'arrête que pour une décision : **le trio d'avatars à tester**, avant d'écrire les briefs. Le reste, il le fait et te dit ce qu'il a fait.

## Reprendre un autre jour

Le travail des étapes 1 à 5 prend plusieurs heures de travail de Claude. Il s'étale souvent sur plusieurs sessions, surtout avec Pro. Rien ne se perd : tout est écrit dans le dossier du produit au fur et à mesure.

1. Ouvre l'app Claude, onglet **Code**, et le **même dossier de travail** que la dernière fois.
2. Démarre une nouvelle session.
3. Écris : « On continue ».

Claude regarde tous tes produits, te dit où tu en es et ce qui t'attend, puis reprend. Si tu as plusieurs produits, il te demande sur lequel travailler. Il ne refait jamais une étape déjà faite.

**Si Claude s'arrête en plein travail** parce que tu as atteint ta limite d'usage, attends l'heure de reprise que l'app affiche, puis écris « on continue ».

## Au quotidien, sur la durée

Tu n'as rien à retenir : Claude te le rappelle à chaque « on continue ».

- **Le jour 3 du test**, il te propose un premier point (seulement les échecs évidents).
- **Le jour 7**, il te demande l'export, les deux répartitions et le rapport de livraison, puis il dit quelle pub couper, garder ou décliner.
- **Un export que tu as déposé** et pas encore lu, **une vidéo livrée** pas encore contrôlée, **une production en retard** : il te le dit en premier.
- **À la fin de chaque test**, une question : le prochain cycle avec les variations des gagnantes (le plus souvent), ou revoir la stratégie quand rien ne gagne.
- **Quand la stratégie est refaite**, tu reçois un nouveau document complet. L'ancien est gardé à côté (STRATEGIE-CREATIVE-cycle-01.pdf).
- **Chaque mois**, demande « Fais-moi le bilan » : chaque cycle, chaque pub, ce qui a gagné, ce qui a été coupé et pourquoi, chaque idée et ses variations.

## Ce que tu dis à Claude

| Tu écris | Ce qui se passe |
|---|---|
| « Je veux lancer des pubs pour mon produit, voici ma page : <lien> » | Un nouveau produit : le dossier, les questions, puis l'entrée |
| « On continue » | Il te dit ce qui t'attend et reprend où il s'était arrêté |
| « Qu'est-ce que je fais aujourd'hui ? » | Tous tes produits : où chacun en est, ce qui est dû aujourd'hui |
| « Fais-moi le bilan » | L'historique du produit, en Word et en PDF |
| « Où j'en suis ? » | L'étape en cours, ce qui est fait, ce qui vient, l'état de ton document |
| « Relie le document complet » | Le document de stratégie, avec toutes les parties déjà faites |
| « Donne-moi le document de la lecture » | Le document d'une étape, en Word et en PDF |
| « Je ne suis pas d'accord avec l'avatar 2 » | Il explique son choix, puis change ce que tu décides |
| « Voici la vidéo de C01 » (avec le fichier) | Le contrôle de la vidéo |
| « Voici mon export du jour 7 » | La lecture des résultats |
| « Fais-moi les variations » | Les prochaines pubs à partir des gagnantes |
| « Fais-moi le guide de montage de C01 » | La voix off et, phrase par phrase, le clip à utiliser |
| « Vérifie que tout est prêt » | Le contrôle de ton ordinateur |

## Ce que tu vends

Dis à Claude dès le début ce que tu vends : **un produit physique**, **un produit numérique** (formation, ebook, modèles, accès à un groupe) ou **un webinaire** (un live gratuit où tu vends ton programme). Sans précision, il part sur un produit physique. Tu peux changer plus tard : « en fait c'est un produit numérique ».

Les dix étapes restent les mêmes. Ce qui change : ce qu'on compte, ce qui fait peur à l'acheteur, et la fin de chaque pub.

| | Produit physique | Produit numérique | Webinaire |
|---|---|---|---|
| **Ce qu'on compte** | les commandes, puis les commandes livrées | les ventes | les inscriptions, puis les présents au live, puis les ventes du programme |
| **Ce que peut coûter la pub** | par commande livrée (le paiement à la livraison et les refus comptés) | par vente : rien à livrer, presque tout le prix peut payer la pub | par inscription, à partir du prix du programme, de la part des inscrits qui viennent et de la part des présents qui achètent |
| **Ce qui fait peur à l'acheteur** | le prix, la confiance, la livraison, l'efficacité, l'usage | l'arnaque, « est-ce pour moi », le prix, l'accès, le paiement, les outils, le remboursement | l'arnaque, l'investissement, son pays, son temps, son niveau, les résultats |
| **La fin de la pub** | le prix de la page et le paiement à la livraison | le prix, et l'accès immédiat ou la garantie | le jour, l'heure (avec le fuseau) et « gratuit » |
| **La campagne** | optimisée sur les achats, bouton « Commander » | optimisée sur les achats, bouton « Acheter » | optimisée sur les prospects (l'inscription), bouton « S'inscrire » |
| **Après la vente** | l'appel de confirmation, les relances WhatsApp, le rapport de livraison | le message d'accès, la relance des paiements abandonnés | cinq messages aux inscrits avant le live, puis les chiffres de chaque live |

**Pour un produit numérique**, Claude te demande seulement ce qu'une vente te coûte en dehors de la pub (souvent zéro, ou les frais de paiement). Il te dit aussi si ta page montre clairement comment on reçoit l'accès et comment on paie (Mobile Money, carte).

**Pour un webinaire**, il te demande en plus :

- la page d'inscription : il y lit la date et l'heure du live, si c'est gratuit, s'il y a un replay, et ce que le formulaire demande ;
- le prix du programme vendu pendant le live, et le paiement en plusieurs fois s'il existe ;
- la part des inscrits qui viennent au live et la part des présents qui achètent. Si tu ne les connais pas, il part de 30 % et 5 %, et il le dit.

Dans la recherche, une pub de webinaire ne tourne que 10 à 14 jours. Ce qui prouve que le tunnel d'un annonceur paie, c'est le nombre de pubs qu'il lance, plus que la durée de chacune. **Après chaque live**, donne à Claude les inscrits, les présents, les ventes et la dépense. Il te donne le coût par présent et par vente, et remplace les taux supposés par les vrais.

## Ce que tu fais à chaque étape

| Étape | Ce que fait Claude | Ce que tu fais | Ce que tu reçois |
|---|---|---|---|
| Entrée | Lit ta page, calcule ce qu'une commande peut coûter, vérifie le pixel | Une commande test ; l'export si tu en as un | Ton document, partie 1 |
| Offre | Lit les pages des concurrents, écrit l'offre et le texte de pub | Tu corriges ta page (le document dit quoi et comment) | Ton document, parties 1 et 2 |
| Recherche | Trouve, télécharge, transcrit, analyse | Un clic sur le bouton vert COPIER quand il te le demande | Ton document, parties 1 à 3 |
| Stratégie | Avatars, angles, créatives à tester | Tu valides ou tu demandes un changement | Ton document, parties 1 à 4 |
| Briefs | Une page par créative | Tu lis, tu demandes ce qui manque | **Ton document complet** |
| Production | Le guide de montage si tu le demandes | Tu produis (IA ou montage) et nommes chaque fichier par son code | Le suivi de production |
| Contrôle | Vérifie chaque fichier | Tu envoies tes créatives à Claude | Bonne à lancer, à corriger, ou à refaire |
| Lancement | La campagne sur les créatives produites | Tu crées la campagne dans le Gestionnaire | La fiche de lancement |
| Lecture | Lit les chiffres pub par pub | Au jour 7, tu envoies l'export, les répartitions et les livraisons | La lecture et la suite |
| Variations | Décline les gagnantes | Tu produis les variations | Les variations |

Dans le parcours par étape, la dernière colonne devient : le document de l'étape.

## Le dossier de ton produit

Claude range tout dans le dossier du produit. Tu n'as pas besoin d'y toucher, mais voici ce que tu y trouves :

| Fichier ou dossier | Ce que c'est |
|---|---|
| `COMMENCE-ICI.md` | Où tu en es, la prochaine action, l'état de ton document |
| `deliverables\word\` | **Tes documents**, en Word et en PDF |
| `deliverables\` | Les mêmes documents en texte, et la page imprimable des briefs (BRIEFS.html) |
| `journal.md` | Chaque décision, datée |
| `References\` | Les pubs et vidéos de référence, leurs transcriptions, leurs images clés |
| `cycles\cycle-01\` | Les briefs, les vidéos livrées, la campagne et les résultats du premier test |
| `data\` | Tes exports, tes captures, tes rapports de livraison |

Pour donner tes vidéos à Claude, glisse-les dans la conversation ou indique où elles sont. Il les range lui-même dans `creatives`, avec le bon nom.

## L'export du Gestionnaire de publicités

Les colonnes par défaut ne disent pas si l'accroche retient. Crée une fois pour toutes le modèle de colonnes « Lecture créa » (3 minutes) :

1. Gestionnaire de publicités → onglet **Publicités**.
2. **Colonnes** → **Personnaliser les colonnes**. Coche : Impressions, Couverture, Fréquence, CPM, Montant dépensé ; Lectures de vidéo de 3 secondes, ThruPlays, Lectures à 25 %, 50 %, 75 %, 95 %, 100 %, Durée moyenne de lecture ; Clics sur un lien, CTR (taux de clics sur un lien), CPC ; Achats, Coût par achat, Valeur de conversion ; Vues de page de destination, Ajouts au panier, Paiements initiés.
3. **Créer une statistique personnalisée**, deux fois : « Taux d'accroche » = Lectures de vidéo de 3 secondes ÷ Impressions ; « Taux de rétention » = ThruPlays ÷ Impressions.
4. **Enregistrer comme préréglage** : « Lecture créa ».
5. Exporte au niveau des **publicités** (et, si tu peux, des ensembles et de la campagne), puis deux **répartitions** : par âge, et par plateforme et placement.

Envoie aussi, chaque semaine, **le rapport de livraison** : commandes passées, confirmées, livrées.

## Le système de noms

Chaque campagne, ensemble et pub a un nom fait de parties séparées par « | », en majuscules, sans accent ni tiret bas :

| Niveau | Modèle | Exemple |
|---|---|---|
| Campagne | PRODUIT \| ÉTAPE \| PAYS \| JJ-MM-AA | GENOUILLERE \| TEST \| CI \| 03-11-26 |
| Ensemble | E# \| AVATAR \| TEMPÉRATURE | E1 \| LA NUIT \| FROID |
| Publicité | C## V# L \| FORMAT \| TITRE COURT | C01 V1 A \| VIDEO \| 3 HEURES DU MATIN |

- **C##** est l'idée, donnée une fois pour toutes. **V#** la variation (V1 l'originale). **La lettre** l'ouverture (A celle du brief, B et C d'autres ouvertures).
- Une pub qui change de campagne garde son nom : ses résultats s'additionnent.
- Chercher « C04 » dans le Gestionnaire montre toutes les versions de l'idée 4.
- Ne tape jamais un nom à la main : copie-le depuis la fiche de lancement.

## Produire tes créatives

Chaque brief te donne deux routes.

- **Avec l'IA** : les images de référence dans Google Flow, très réalistes, avec une vraie source de lumière (fenêtre, lampe) ; l'animation dans Flow avec Veo (plans de 8 s) ou Omni Flash (plans de 10 s) ; la voix dans ElevenLabs avec le profil vocal du brief ; le montage dans CapCut. Une personne qui parle bouge beaucoup, avec énergie.
- **Au montage, si tu manques de crédits** : une voix off posée sur des clips, une phrase par clip. Demande à Claude « fais-moi le guide de montage de C01 » : il te donne la voix off et, phrase par phrase, le clip à utiliser.

Dans presque toutes les vidéos, il y a **le hook textuel** : le titre écrit en haut de l'écran pendant les 3 à 5 premières secondes. Pour une vidéo qui répond à un commentaire, c'est le vrai commentaire, recréé avec un générateur de commentaires (TikComment pour TikTok), à l'écran 3 à 5 secondes au début.

**La fin de chaque vidéo change d'une créative à l'autre.** Elle dit toujours ce que ta vente demande (le prix et le paiement à la livraison, l'accès, ou le jour et l'heure du live), puis une façon de pousser à agir, choisie selon le script :

| La fin | Ce qu'elle ajoute | Exemple |
|---|---|---|
| Habituelle | l'appel direct | « Clique et commande. » |
| Urgence | une limite de temps ou de quantité | « Plus que [N] pièces à ce prix. » |
| Exclusivité | pour qui c'est, et pour qui ce n'est pas | « Réservé à ceux qui ont déjà tout essayé. » |
| Risque retiré | ce que l'acheteur ne risque pas | « Tu ouvres le colis devant le livreur. » (un produit physique), « Remboursé sous [N] jours si ça ne te sert pas. » (un produit numérique) |
| Défi | une invitation à vérifier soi-même | « Essaie une semaine, et juge toi-même. » |
| Urgence et exclusivité | les deux ensemble | |

Les chiffres d'urgence restent en blanc dans le brief : remplis-les seulement s'ils sont vrais.

Quand une créative est prête, nomme le fichier par son code (« C01 V1 A.mp4 ») et **envoie-la à Claude**. Il la contrôle avant la mise en ligne.

## Gratuit, hybride, payant

- **Gratuit** : rien à payer en plus de Claude. La recherche se fait dans ton Chrome. Avec la clé Gemini gratuite, toutes les références sont analysées ; sans elle, Claude analyse les 15 qui comptent.
- **Hybride** : Apify cherche à ta place tant que son crédit gratuit mensuel suffit.
- **Payant** : Apify et Gemini en payant, pour aller plus vite et plus large.

Dis à Claude « passe en formule hybride » pour changer.

## Mettre à jour la suite

Quand tu reçois une nouvelle version (par exemple `creative-strategy-os-1.3.3.zip`), mets-la dans **Téléchargements** et écris à Claude : « Installe la mise à jour, le fichier est dans mes Téléchargements. » Il garde une copie de ta version actuelle, installe la nouvelle et lance les tests. Si un test échoue, il remet ta version d'avant tout seul. **Tes dossiers produits ne bougent pas.**

Pour le faire toi-même sur Windows, dans PowerShell (remplace le numéro de version) :

```
python "$env:USERPROFILE\.claude\skills\creative-strategist\scripts\suite.py" install "$env:USERPROFILE\Downloads\creative-strategy-os-1.3.3.zip"
```

Sur Mac, la même ligne avec `python3`, `~/.claude/skills/...` et `~/Downloads/...`. Réponds « o » quand il demande « Installer ? ». Les tests prennent quelques minutes.

## Quand quelque chose bloque

| Ce que tu vois | Ce que tu fais |
|---|---|
| Claude ne semble pas connaître la suite | Vérifie que les dix dossiers sont directement dans `.claude\skills` (Installer, étape 3), ferme complètement l'app Claude, rouvre-la, puis utilise l'onglet **Code** |
| « python n'est pas reconnu » dans PowerShell | Ferme PowerShell, ouvre-en un nouveau, relance le script d'installation |
| « Il faut cliquer sur COPIER » | Claude a mis une capture derrière un bouton vert dans Chrome. Clique dessus, puis dis « c'est copié » |
| « … est ouvert dans Word » | Ferme le document dans Word ou dans ton lecteur PDF, puis dis « c'est fermé » |
| Un PDF ne sort pas | Installe LibreOffice, ou garde le .docx |
| Une vidéo ne se télécharge pas | Rien à faire : Claude la regarde en ligne et l'analyse quand même ; son lien reste dans le fichier des références |
| La mémoire est pleine pendant la transcription | Ferme Chrome et les applications lourdes, puis dis « relance » |
| Claude s'arrête : limite d'usage atteinte | Attends l'heure de reprise, puis « on continue » |
| Claude dans Chrome ne répond pas | Ouvre Chrome, vérifie que l'extension est connectée à ton compte Claude, puis dis « Chrome est ouvert » |
| Tu ne sais plus où tu en es | « Où j'en suis ? », ou ouvre `COMMENCE-ICI.md` |
| Tu n'es pas d'accord avec un choix | Dis-le. Rien n'est bloqué : Claude explique pourquoi il a choisi, et tu décides |
