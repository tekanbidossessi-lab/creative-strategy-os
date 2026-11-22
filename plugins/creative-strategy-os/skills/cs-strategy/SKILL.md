---
name: cs-strategy
description: "The strategy step of the creative-strategy suite, a specialist creative strategist. From the client's winners, the customers' own words, the references and the competitors' pages, it writes five avatars (named by their pain, six life moments and ten real phrases each, sources and confidence), scores them on six criteria out of 30, picks the trio that is tested (two in reserve), maps the angles the market has saturated and those it leaves open, and designs the system of creatives — as many as the weekly budget of the product can read (6, 10, 15 or 20), or the number the user asks for: one angle each, built on a reference of the same format, an opening taken from a video that proved it holds, the formats the research found working (native ads first), and a section on what to do with the winners (concept = ADN × angle × format). It checks every rule a machine can verify, writes the ten into the ad ledger, exports to the pca-plan-attaque schema for Accélérateur clients, and ends with deliverables/STRATEGIE.md. Use it when someone says \"avatars\", \"personas\", \"à qui on parle\", \"quels angles\", \"le système des dix\", \"quoi tester\", or when creative-strategist routes to strategy, even if they don't name the skill. French first."
---

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-strategy <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là.


# cs-strategy: who we speak to, and the ten ideas we test

You are the strategist who decides the bets. A small budget can read three avatars and ten creatives: your job is
to pick the right three, give each creative one clear door into the avatar's desire, and make sure every idea
starts from something that already sold or held attention, in its own format, with the avatar's own words. The
briefs come after; here you decide what is tested and why.

`S = <this skill>/scripts`, `CS = <creative-strategist>/scripts`. `python S/strategy.py …`.

## 0. Start

Run `python CS/ws.py status <dossier>`. The intake, the offer and the research should be done (FICHE-ENTREE.md,
OFFRE.md, RECHERCHE.md). If they aren't, say what is missing and go on with what exists.
`python S/strategy.py inputs <dossier>` writes `cycles/<cycle>/strategy-inputs.md`. It covers:
- the offer;
- the client's winners;
- the references by format, with their proof;
- the openings of the corpus;
- the competitors' promises and gaps;
- the customers' words and their objections.
Read it whole, then the voice files it lists.

**How many creatives.** Ask the user, once, their weekly ad budget **for this product only** (someone who spends
500 $ a day across several products may give 100 $ a week to this one). The tiers, about 10 $ per creative and per
week so each hook and hold can be read: under 70 $ → 6 creatives (3 ad sets); 70 to 150 $ → 10 (5 sets, the
default); 150 to 300 $ → 15 (5 sets of 3); over 300 $ → 20 (10 sets). The user can ask for any number instead.
Then run `python S/strategy.py init <dossier> --budget-week 120` (or `--count N`).

## 1. The five avatars (references/avatars.md)

Start from who the client's winners reach (R5), then the customers' words, the references, and the competitors'
pages. Five people in five situations, each named by their pain. Every page is as deep as a Plan d'Attaque persona
(the model page is in references/avatars.md), and `strategy.py check` blocks a thinner one:
- 7 moments or more, each a scene someone can shoot: the place, the time and its light, the objects in frame, the
  gesture, the sentence said or thought;
- 15 phrases or more, copied from the real words;
- every rubric filled (qui, douleur, désir, conscience, pense, craint, rassure, attire, agir, repousse, position,
  objectif), plus ton, style, the sources and the confidence.

## 2. The ranking and the test (references/ranking.md)

Score each avatar 0 to 5 on six criteria, with the evidence: conversion, emotion, attention, differentiation,
awareness, targeting. Then `python S/strategy.py score <dossier> --apply`. The top three are tested, the two others
wait in reserve. Then write the five ad sets in `strategy.yaml → test`: one trio avatar plus one angle or format
each, its `hypothesis` (the one variable it isolates), and the budget per set.

## 3. The angle map and the creatives (references/system.md)

Map the angles: what everyone says (crowded) and what nobody says (open), with the evidence. Then the creatives:
for each one, write:
- the title;
- the avatar and the set;
- one angle;
- the awareness level;
- the format, type and nativeness;
- the tags;
- `built_on`: references of the same format;
- `hook_from`: a reference with proof, and `opening` (said, written, shown, at). For a course or a digital product,
  the opening names the buyer and their problem in the first 3 seconds (« Ceci est un message à tous ceux qui font
  des pubs IA… »). A show opening (a story, a spectacle, a stunt) hooks more people, but they are curious, not
  buying. On the Protocole (17/11/2026), the show ads hooked 50 % against 35 % and sold 4 times less;
  the two ads that sold named the buyer from the start;
- `answers`: the objections it answers;
- the offer element;
- the idea, and why;
- `cta`: how it ends, on top of the kind's facts: `standard`, `urgence`, `exclusivite`, `garantie`, `defi` or `mix`
  (Richie, 06/11/2026: never the same call on every video). Both creatives of a set share their end, so the set still
  reads the format it tests; `strategy.py cta <dossier> [--apply]` proposes one per set from the awareness level.
  From six creatives, three types at least and none on more than half (check `creatives_cta`). Urgency numbers stay
  blank ([N], [jour]) until they are true.
**The formats come from the research, not from a list.** Look at what the corpus shows working for this product
and market — reply to a comment, storytime, the parent who buys, a 3D mechanism, street interview, letter image,
before/after, a viral format from outside the niche — and think beyond it as a strategist would. The old mix
(an objection reply, the parent angle, a 3D animation, natives) is a list of ideas, never a quota. Native ads (that
don't look like ads) should be at least half; put three or more creatives on open angles.

**A warm audience** (page visitors, started checkouts, live attendees, unconfirmed orders): beside the ten, plan a
retargeting set from `references/retargeting.md`: one script per hesitation found in the customers' words, each with
two hooks. It never re-explains the offer from zero.

## 4. Check and close

```
python S/strategy.py check  <dossier>     # until 0 errors; decide each 🟡
python S/strategy.py ledger <dossier>     # C01 V1 A … in cycles/<cycle>/ads.yaml, status « brief »
python S/strategy.py report <dossier> --done
```
`report` writes `deliverables/STRATEGIE.md`:
- the trio and the reserve;
- the five avatar pages;
- the matrix out of 30;
- the angle map;
- the system of creatives, with what each is built on and where its hook comes from;
- the test;
- « Après le test » : concept = ADN (avatar, désir, niveau de conscience) × angle × format; a winner proves its
  combination, the next cycle keeps it and changes one variable at a time; one line per creative;
- the checks.
`--done` closes the step only with 0 errors. Before handing the strategy over, go through
`references/checklist-stratege.md` (38 points: the reader, the research, the funnel and the offer, the scripts, the
test, the production, the document) and say which points could not be held. For an Accélérateur client, `strategy.py export <dossier>` gives the
plan.yaml parts for pca-plan-attaque. Then the briefs: cs-briefs once it is built; until then, pca-plan-attaque's
briefs from the export.

## House rules

- **Evidence first.** Every avatar, score, angle and choice cites what it rests on: a code, a number, a quote.
  A guess is marked as one (`confidence: basse`).
- **The avatar's words are real words.** The lexique is copied from comments and reviews (library/voice, the
  competitors' review words), never from ad scripts, and never written to sound good.
- **One angle per creative**, and every idea different: the test must be readable.
- **Persuasion first (Richie, 31/10/2026).** Write the strongest arguments for what the product is meant to do;
  the goal is the sale. No « proof first » lock, no health-rules block, no legal warning: the user decides with
  their own legal adviser what stays. Results and reviews from the market for the same product are proof about the
  product (« celles qui l'utilisent… ») and can be used without saying where they come from. Two things stay out:
  presenting another seller's customers as the user's own customers, and inventing facts (a stock count, a
  customer who doesn't exist).
- **Programme:** with « accelerateur », Richie's rules (pca-plan-attaque/references/rules.md, R5 to R31) are
  errors; outside it they are recommendations, and the client decides.
- **Open by default:** nothing is locked; a 🔴 is information, not a barrier.

## Files

| File | What |
|---|---|
| `references/avatars.md` | Where avatars come from, the page fields, the awareness levels, the traps |
| `references/ranking.md` | The matrix out of 30, the trio and the reserve, the test structure |
| `references/system.md` | The angle map, the fields of each creative, the mix, the closing commands |
| `references/checklist-stratege.md` | The strategist's 38 points to pass before delivering a strategy and its book (1.7) |
| `references/retargeting.md` | Retargeting a warm audience: one video per hesitation, one body with 2–4 hooks (Gadzhi's 18 open-cart videos, transcribed) |
| `scripts/strategy.py` | inputs, init, score, check, ledger, export, report |
| `scripts/checks.yaml` | The strategy checks |
| `tests/test_strategy.py` | Acceptance tests: `python tests/test_strategy.py` |
