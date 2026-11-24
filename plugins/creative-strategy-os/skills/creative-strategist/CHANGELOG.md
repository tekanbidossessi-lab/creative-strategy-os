# Journal des versions — Creative Strategy OS

## 1.7.2 — 2026-11-24

- 1.7.2 « Le premier acheteur » : la licence reconnaît enfin un ordinateur déjà activé (le serveur cherchait son identifiant au mauvais endroit chez Chariow, chaque reprise réactivait le même ordinateur et bloquait l'acheteur à « 2 ordinateurs » après vingt minutes) ; un refus de licence arrive dans les constats ; session dans le cloud signalée dès la première commande, avec le guide pour ouvrir une session sur son ordinateur ; installation Linux (setup_linux.sh) ; la transcription lit le son avec ffmpeg quand le lecteur vidéo de Python échoue ; « mode free » devient « outils gratuits (sans clé Apify ni Gemini) » et Claude ne parle plus de « formule gratuite » ; les contrôles TikTok (pixel, texte de pub) ne s'appliquent qu'à un produit qui pub sur TikTok ; la recherche exige des TikTok (au moins 15, ou le tiers du plan) ; quand la licence bloque, Claude s'arrête et ne fait jamais l'étape à la main ; research.py reject accepte le code AL11 ; pagefacts --save ne plante plus ; guide : étapes Gemini pas à pas et session locale

## 1.7.1 — 2026-11-23

- 1.7.1 : chaque document de la suite a la présentation du livre de stratégie : couverture, sommaire cliquable, chaque grand titre sur sa propre page (son numéro, son titre, le trait vert), en haut le produit et le type de document, en bas « Créé avec Creative Strategy OS · par Richie Tekan · WhatsApp » et le numéro de page

## 1.7.0 — 2026-11-22

- 1.7.0 « Le livre pour un débutant » : le livre de stratégie garde sa structure et parle au lecteur, jamais à l'outil (encadré « À quoi sert cette partie », marques, codes de règle, commandes et noms de fichiers retirés) ; partie « Le mini-cours » (trois secondes, référence et avatar, natives, pourquoi la pub vend le test, lire tes chiffres avec ceux du quiz, du chiffre à la correction, boucle, variations, teste petit) ; Annexe en phrases (vérifications, points à trancher, codes, sources, glossaire) ; docs.py --book --outline pour valider le sommaire ; « Après l'achat » pour le digital, lignes d'un autre type filtrées ; briefs : rôle dans le test et ce qu'il faut produire en tête, alerte quand un mot fort de la référence disparaît ; checklist du stratège en 38 points ; téléchargement par le lien vidéo des captures, transcription relancée vidéo par vidéo en base quand la mémoire manque, images refusées par Word réenregistrées
- Les mêmes règles pour tous les documents (lancement, lecture, variations, contrôle, gagnants, montage, bilan, page, tendance) : encadré « À quoi sert ce document », traces de l'outil retirées, contrôles écrits en phrases sous « Ce qui a été vérifié », les mots à connaître à la fin.

## 1.6.0 — 2026-11-20

- 1.6.0 « Pubs vers un quiz » : destination page ou quiz ; avec un quiz, chaque pub vend le test gratuit (ni prix, ni offre, ni garantie), chaque promesse est vérifiée contre library/quiz.yaml (intake.py quiz) et chaque avatar du trio doit être quelqu'un que le quiz accueille ; les profils et écrans info du quiz deviennent des angles ; 5 squelettes de pubs vers un quiz qui durent ; recherche par page d'arrivée (rank --landing quiz) et mots du quiz ; pick --id pour une pub vue en direct ; research.py voice pour importer des commentaires ; produit pas encore en ligne (intake.py offline) ; nombre d'avatars réglable (avatars=N, profile_of) ; règles du test en champs (cut_rule, avatar_fail_rule) ; briefs init garde les sources ; ws.py step --output plusieurs fichiers ; fins du rapport selon le type de produit

## 1.5.0 — 2026-11-17

- 1.5.0 : partage des constats avec Richie (avec le oui de l'acheteur, base Notion relue à la main) ; tendance du compte par deux semaines (usure de l'offre, fuite au paiement, vie des gagnantes) ; leçons de la page Protocole dans l'audit de page ; ouverture d'une formation qui nomme l'acheteur ; 1-2 images noires au début = note, pas défaut

## 1.4.8 — 2026-11-16

- Guide d'utilisation 1.4.8 : préparer le Gestionnaire de publicités avant l'export (le tableau Lecture créa, groupe par groupe, et l'export pas à pas), le lien d'installation entier, les mises à jour automatiques, la version d'essai.

## 1.4.7 — 2026-11-16

- Version d'essai : une clé d'essai (produit Chariow à part, reconnu par le serveur) fait une stratégie complète jusqu'aux briefs, avec 20 références et 5 créatives ; lancement, lecture des résultats, variations et contrôle des vidéos restent dans la licence complète ; chaque document porte « Version d'essai » en haut.

## 1.4.6 — 2026-11-16

- Tes créatives actuelles : quand le produit a déjà eu des pubs, la suite demande les vidéos et images en ligne, chacune nommée exactement comme sa pub dans le Gestionnaire de publicités, dans le dossier mes-pubs/. intake.py export relie chaque fichier à ses chiffres et à sa référence CL, et liste les fichiers à renommer et les pubs qui ont dépensé sans vidéo reçue (--videos pour un autre dossier).
- Le plugin porte le logo de Creative Strategy OS (icône, nom affiché, page GitHub).

## 1.4.5 — 2026-11-15

- Gemini : les modèles « gemini-flash-latest » puis « gemini-flash-lite-latest » (Google les garde toujours en service) puis 2.5 Flash ; 2.5 Flash-Lite est fermé aux nouveaux comptes. Un modèle indisponible (404) ou surchargé (503, après deux pauses de 30 s) passe au suivant au lieu d'arrêter l'analyse.
- Facturation Gemini : quand le plafond de dépenses mensuel du projet est atteint, la suite arrête d'interroger Gemini et dit quoi faire (relever le plafond, images clés, AI Studio) ; le guide conseille un plafond de 5 à 10 $ si la facturation est activée.

## 1.4.4 — 2026-11-15

- Petit budget : sous 105 $ par semaine pour un produit, 2 ou 3 idées avec 2 ou 3 accroches chacune (un ensemble = une idée, le même corps, seule l'ouverture change) ; la vérification de la stratégie le contrôle.
- Notes sur 10 : rétention 10 % = 7/10, 15 % = 8/10, 40 % = 10/10 (parfait) ; accroche 37 % = 6/10, 45 % = 7/10, 80 % = 10/10, dans la lecture et le classement.
- La gagnante au cas par cas : plus de nombre de ventes fixé. Rentable d'abord (coût sous la cible, marge après la pub), puis pesée sur les ventes, la marge, l'accroche, la rétention, le CTR et le CPM ; « à confirmer » sous 5 ventes ; « prometteuse » sans assez de preuves. Classement du test : le plus de ventes pour le moins d'argent.
- Le registre des gagnants (deliverables/GAGNANTS.md, read.py winners) : chaque gagnante décomposée sur ADN (avatar · désir · niveau de conscience) × angle × format, la variable gagnante, chaque élément classé sur tous les cycles (prouvé, prometteur, mitigé, à éviter), ce que les variations ont prouvé, la prochaine variable à changer ; cs-iterate part de là.

## 1.4.3 — 2026-11-15

- Audit du 15/11 : le budget écrit en FCFA, GNF, naira, cedi, euros ou dirhams est lu (avant, la stratégie retombait sur 10 créas quel que soit le budget) ; la fiche de lancement prévient quand le budget par pub ne permet pas de juger en une semaine ; le client de licence attend le réveil du serveur gratuit au lieu d'échouer ; le guide explique l'installation avec une licence (plugin, clé, outils).

## 1.4.2 — 2026-11-15

- Gemini gratuit : quand le quota du jour d'un modèle est épuisé, l'analyse passe au modèle suivant (2.5 Flash puis 2.5 Flash-Lite, chacun son quota) ; quand tous le sont, les références restantes attendent le lendemain (analyse --all reprend) avec les solutions immédiates (images clés, AI Studio). Vidéos de plus de 3 minutes envoyées en basse résolution (environ 3 fois moins de jetons). Clé Gemini testée en vrai.

## 1.4.1 — 2026-11-15

- Recherche : chaque vendeur trouvé (un site avec 3 pubs ou plus) entre seul dans library/sellers.yaml et ses recherches par site et par nom, tous pays, sont ajoutées au plan une fois (research.py rank).

## 1.4.0 — 2026-11-15

- La suite, après chaque sortie : chaque étape finie, le document relié et la page vérifiée se terminent par un court paragraphe « La suite — » écrit dans le code (ws.py HANDOFF, par étape et par type) : ce que tu as, ce qui vient (produis les vidéos et envoie-les-moi, lance, envoie l'export du jour 3), et une seule question.
- Webinaire, atelier, défi : les pubs tournent 7 à 10 jours avant le live et s'arrêtent le jour du live ; la fiche de lancement calcule la fenêtre depuis live.dates (« Le calendrier des pubs », « Jusqu'au live »), lecture au jour 3 et au jour 5.
- Guide d'utilisation 1.4.0 (Word et PDF) : écrire ta page de vente ou d'inscription avec la suite, le script de ta VSL, « la suite » après chaque étape, la fenêtre des pubs d'un live.
- Les pages qui vendent (cs-offer/references/pages-qui-vendent.md) : la page d'offre d'Iman Gadzhi démontée en 23 blocs, les pages de vente de Roméo Moumouni et de Frank Simo, six pages d'inscription africaines, huit types de titres (formule, pourquoi, quand, comment l'adapter), 14 principes, quatre plans de page, une liste de contrôle.
- La vidéo de vente (cs-offer/references/vsl.md) : la VSL de Djokoinfluent démontée diapositive par diapositive, la règle en 12 points, un plan en 16 blocs pour en faire une ; comment télécharger une VSL (Wistia, ConverteAI, YouTube).
- Le reciblage (cs-strategy/references/retargeting.md) : les 18 vidéos d'ouverture de panier de Gadzhi transcrites, une vidéo par hésitation, un corps et 2 à 4 accroches ; la stratégie prévoit un ensemble de reciblage pour un public chaud.
- offer.py page grab / write / check : lire une page entière (sans navigateur d'abord, avec et sans « www. », sinon browser/page_grab.js et le presse-papier), l'écrire comme un brief sur un des quatre plans (référence mot pour mot, ta page, ce qui change), la contrôler (cases vides, blancs, changements non dits, capitales, minuteurs).
- La méthode « page de vente » de Richie entre dans cs-offer (references/methode-page-de-vente.md), avec la règle de la voix (une personne, à voix haute, deux phrases par point).
- Le webinaire : le format du live (live, atelier, défi, masterclass, conférence), le nombre de soirées, les dates, l'heure GMT, le prix du ticket ; un défi payant finit ses scripts sur son prix au lieu de « gratuit ». Le livre relie la page en brief à la place de l'offre quand il n'y a pas d'OFFRE.md.
- Recherche : research.py plan ajoute les mots du format (atelier gratuit, 3 soirées, défi 3 jours, réserve ta place…) pour un webinaire, sur trois marchés ; plan --sellers suit chaque vendeur par son nom et son domaine, tous pays ; rank montre les funnels par site d'arrivée (un vendeur, plusieurs pages Facebook) ; la page Facebook et le domaine de chaque pub sont gardés.
- Recherche : le navigateur intégré en premier, Chrome seulement pour ce qui demande une connexion ; vider le lecteur avant une série ; hors connexion, ~25 groupes de pubs par recherche (toutes les pubs d'un annonceur demandent une session connectée).
- Corrigé : frames accepte plusieurs codes ; transcribe ne passe plus seul à Whisper « base » (il attend la mémoire), refait une transcription absente ou faite en « base », --redo ; briefs.py opening --write n'efface plus le titre à l'écran ; la vérification des mots de l'avatar accepte une phrase conjuguée ou citée ; le téléchargement YouTube fusionne image et son avec le ffmpeg d'imageio-ffmpeg.
- ws.py set prend plusieurs réglages d'un coup et ajoute un marché (market=CM,GA ; market=-CM pour le retirer), pays et monnaie remplis seuls.
- Lecture des pages : barres fixes au-dessus de 20 % de l'écran, compteur figé, minuteur à zéro, avis répété, date passée, page d'arrivée morte (page-audit.md).

## 1.3.2 — 2026-11-09

- Deux parcours : complet (recommandé, par défaut) — le premier cycle finit par UN document de stratégie, relié après chaque étape de l'entrée aux briefs (« version de travail · N parties sur 5 » jusqu'aux briefs) ; par étape — un document par étape.
- ws.py : path full|stage (init --path, set path=…), « Ton document » sur COMMENCE-ICI.md, step done affiche le document à faire, next demande le document complet avant la production s'il est plus ancien qu'une partie.
- docs.py : chaque document d'étape a la couverture et le sommaire cliquable du document de stratégie (--plain pour le texte seul) ; --book affiche le nombre de parties reliées et la page « Commence ici » d'une version de travail nomme la partie suivante.
- Guide d'utilisation 1.3.2 : installation pas à pas (décompression au bon endroit, vérification des dix dossiers), l'onglet Code, les deux parcours, ton document, reprendre un autre jour, ce que tu dis à Claude, le dossier du produit, mettre à jour, tableau des blocages.
- Simple à utiliser : l'utilisateur dit « on continue ». Questions à choix (outil de questions de Claude Code) à trois moments seulement : la première conversation (ce que tu vends, pubs déjà faites, qui fait les vidéos, budget), le trio avant les briefs, la fin d'un cycle de test (references/process.md).
- ws.py overview : tous les produits du dossier, leur prochaine action et les rappels (jour 3, jour 7, export ou rapport de livraison pas lu, vidéos à contrôler, production en retard). ws.py bilan : l'historique du produit, cycle par cycle (deliverables/BILAN.md, docs.py BILAN).
- Un cycle qui refait la recherche ou la stratégie redonne un document complet ; l'ancien est gardé tout seul (STRATEGIE-CREATIVE-cycle-01.docx / .pdf).

## 1.3.1 — 2026-11-07

- Entrée : le prix écrit dans le texte de la page est lu (« PRIX AUJOURD'HUI : 12 500 FCFA », prix barré « PRIX DE VENTE NORMAL »), les montants de preuve et de valeur sont laissés de côté ; un prix noté à la main est gardé et marqué.
- Entrée : economics --set price=… marche pour tous les types de projet, plus seulement le webinaire.
- Entrée : une pub et ses copies (« - Copie », « Copie de », « (Copy) ») comptent comme une seule gagnante, leurs chiffres additionnés.
- Offre : un produit numérique parle en ventes (plus de « 1 unité » ni de « commande livrée »), son modèle contient la pile de valeur ; « prix de lancement » compte comme urgence ; un prix barré au-delà de ×2 est orange, pas rouge, pour un produit numérique ou un programme.
- Corrigé : offer.py lint ne plante plus quand le paiement en plusieurs fois est une phrase ; une preuve chiffrée de la page (« 325 000 FCFA de ventes ») n'est plus prise pour un prix absent.
- Recherche : une référence importée par son lien reçoit son pays (--country), son auteur, sa date et ses vues au téléchargement ; une transcription déjà dans Transcripts/ est reprise sans la refaire.
- Briefs : « questions-réponses » n'ajoute plus de bloc commentaire ; la fin « risque retiré » est décrite selon le type de projet (plus de colis pour un produit numérique).
- Document : l'en-tête d'un tableau ne reste plus seul en bas de page. Installation : l'aide de --kind cite digital, ws.py doctor prévient quand la mémoire libre est sous 1 500 Mo.

## 1.3.0 — 2026-11-06

- Les fins des vidéos (CTA) : un type par créative en plus des faits de la fin (urgence, exclusivité, risque retiré, défi, urgence et exclusivité) ; strategy.py cta propose un type par ensemble, briefs.py check vérifie que la fin le dit et refuse un chiffre d'urgence inventé ; « la fin » devient un levier des variations.
- Commentaires Facebook obligatoires pour chaque projet : contrôle refs_fb_comments (40 commentaires sur 2 publications au moins), fichiers de mots des clients nommés par leur source, la stratégie signale des avatars qui ne reposent que sur TikTok.
- Après le test : un tableau dit ce que chaque chiffre (accroche, rétention, CTR, page, CPM, coût par résultat) change dans la créative, et chaque créative dit ce qu'elle devient selon ses chiffres.
- Le document : une page par avatar avec un grand titre et chaque partie en liste, chaque créative en détail (idée, raison, ouverture, fin), plus d'espace entre les lignes, le gras plus visible, les sous-listes.
- Guide d'utilisation 1.3.0 : les fins des vidéos et les commentaires Facebook.

## 1.2.1 — 2026-11-02

- Noms des clients retirés de la suite : exemples, contrôles et tests parlent désormais d'« un client », d'« une boutique » ou d'un vendeur fictif (GenouPlus, Bambou Confort, Boutique Exemple).
- Adresses de boutiques, identifiants de pixel, de compte publicitaire et de pubs réelles remplacés par des valeurs fictives dans les tests.
- Guide d'utilisation : version 1.2.1.

## 1.2.0 — 2026-11-02

- Les types de projet : produit physique, produit numérique, webinaire (kind dans workspace.yaml), de l'entrée à la lecture
- Webinaire : économie par inscription, page d'inscription, offre du live, cinq messages, campagne Prospects, read.py live
- Numérique : coût par vente, objections propres, fin de pub accès ou garantie, campagne Acheter
- Recherche : --must/--not, plan --page, copies groupées, jumelles par transcription ou fichier, part du marché, Whisper qui réessaie
- Stratégie et briefs : diversité à l'échelle, égalité du trio, (coupé), durée gardée, une légende par référence, briefs.py fill
- Guide d'utilisation : la section Ce que tu vends

## 1.1.3 — 2026-11-02

- Avatars au niveau d'une page de Plan d'Attaque : strategy.py check bloque un avatar trop mince (15 phrases réelles, 7 moments d'au moins 20 mots qui sont des scènes, chaque rubrique, ton, style, sources) ; references/avatars.md donne la page modèle.
- Bibliothèque publicitaire connectée : le lecteur charge jusqu'à 210 pubs en 38 s, garde les dates de début et de fin d'une pub arrêtée et le lien de la page de l'annonceur.
- Briefs : une voix écrite en phrase s'imprime et le contrôle demande les champs ; « Voix du déçu » au lieu de « Voix de Le déçu » ; plus de profil ElevenLabs quand le brief dit la vraie voix ; le code d'une référence n'est plus imprimé deux fois sous ses images.
- Briefs : R31 compare l'ouverture de la stratégie à la première ligne du script (il passait à tort sur le champ hook recopié de la stratégie) ; nouvelle commande briefs.py opening [--write] pour faire de l'ouverture du script l'ouverture officielle, dans le brief et dans la stratégie.
- Tests : le test du contrôle trouve ffmpeg comme la suite (celui d'imageio-ffmpeg quand il n'est pas installé).

## 1.1.2 — 2026-11-01

- Test du webinaire : recherche par lots dans la Bibliothèque publicitaire (adlib_batch.js), plus de références perdues entre deux commandes, pubs retirées par Meta écartées, paste plus sûr (même capture refusée, écriture d'un seul coup), paiement mobile money, render --ready (seuls les briefs finis dans le document)

## 1.1.1 — 2026-10-31

- Instagram testé dans un Chrome connecté : le mot à chercher va dans la ligne GO du script (les recherches s'ouvrent dans la page, plus de premier lot perdu), les vues viennent des Reels de l'auteur, le classement se sert des j'aime quand les vues manquent

## 1.1.0 — 2026-10-31

- Un seul document de l'entrée aux briefs : A4, une page de titre par partie, sommaire cliquable, une créative par page, les vérifications en annexe, une ligne de signature ; plus de charte Momentum.
- Les liens partout : concurrents (page et pub), références des tableaux et des briefs.
- Recherche : 40 références en formule gratuite, 60 sinon, ou le nombre choisi ; Instagram et commentaires Facebook (Chrome de l'utilisateur, lecture seule) ; Whisper limité au français et à l'anglais ; une vidéo qui ne se télécharge pas est analysée en ligne ; clé Gemini gratuite facultative pour tout analyser ; le document dit ce qui est analysé et pourquoi.
- Vitesse : les captures du navigateur passent par le presse-papier (bouton COPIER, research.py paste), plus par la conversation.
- Offre : « Comment t'en servir », urgence écrite pour convaincre (chiffres à remplir), plusieurs pays.
- Stratégie : nombre de créatives selon le budget hebdomadaire d'un produit (6, 10, 15, 20) ; formats tirés de la recherche ; section « Après le test » (concept = ADN × angle × format) ; persuasion d'abord.
- Briefs : hook textuel, commentaire à l'écran, profil vocal, outils (Google Flow Veo ou Omni Flash, ElevenLabs, CapCut), réalisme et lumière, route montage dans chaque brief, briefs.py montage.
- Lancement sur les créatives produites ; ce qu'il faut envoyer au jour 7. Lecture : hypothèses confirmées ou non, ce qui n'a pas marché, la suite. Variations : la méthode du live du 05/09/2026.
- Installation Windows et Mac (setup_mac.sh), Claude dans Chrome et clé Gemini vérifiés ; guide d'utilisation dans creative-strategist/guide ; en-têtes des skills réparés (cinq ne se déclenchaient plus bien).

## 1.0.1 — 2026-10-30

Le test de bout en bout sur un vrai produit (une genouillère vendue en Côte d'Ivoire, formule gratuite) : une trentaine de corrections, dont :

- Whisper sautait la dernière phrase d'une vidéo longue (la vente) : corrigé dans le contrôle, la recherche et le Plan d'Attaque.
- La capture de la Bibliothèque publicitaire garde tout le texte de la pub, plus seulement sa première ligne.
- La fiche d'entrée : une lecture par téléchargement n'efface plus les pixels vus par le navigateur ; une sonde d'une autre page est refusée (--other-page).
- Les briefs d'image ont leurs propres étapes de production ; deux alertes contraires aux règles retirées.
- Le lancement : le texte commun corrigé arrive sur la feuille, deux ensembles sur un même avatar portent le nom de leur angle, la température d'un ensemble ne change plus d'un lancement à l'autre.
- Le contrôle reconnaît « seulement à la livraison » même quand le verbe est mal entendu, et n'affiche plus les fichiers rejetés.
- Les variations ne proposent plus un angle déjà testé, et nomment les créatives jamais lancées.

## 1.0.0 — 2026-10-28

- La suite complète, dix skills : creative-strategist (l'entrée, le dossier produit, les formules), cs-intake (la fiche d'entrée), cs-offer (l'offre et la page), cs-research (les références), cs-strategy (avatars, angles, système des dix), cs-briefs (les briefs et la production), cs-review (le contrôle qualité), cs-launch (le lancement), cs-read (la lecture des résultats), cs-iterate (les variations).
- Chaque skill testé sur des données réelles ou une copie fidèle, relu par un relecteur indépendant, corrigé.
- Les livrables en Word et en PDF dans le kit d'impression (docs.py) : Momentum Media pour l'Accélérateur, la marque du client sinon.
- Les seuils de lecture de Richie (live du 03/10/2026) dans un seul fichier, thresholds.yaml, modifiable par dossier.
- Les mises à jour : suite.py (version, test, pack, install, rollback).
