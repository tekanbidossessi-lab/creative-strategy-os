---
name: cs-read
description: "The reading step of the creative-strategy suite, a specialist who reads ad results the way Richie teaches. It imports the Meta or TikTok export at ad level (the « Lecture créa » columns: 3-second plays, ThruPlays, link clicks, landing page views, purchases), finds each ad by its code (C## V# L) in the ledger, and adds up an ad that moved between campaigns. It reads the delivery report for cash on delivery (ordered, confirmed, delivered, cost per delivered order). It gives each ad a verdict with its cause and the action to take: wait (before 2 000 impressions and 3 days), cut (twice the target cost per order spent without an order), winner, keep, or fix, with the diagnosis (the opening, the body, the message, the page, the offer, a CPM Meta dislikes, fatigue over the last 7 days). It also says which avatar doesn't respond and which reserve avatar comes in, what the losers share, and the account's own medians. It ends with deliverables/LECTURE.md and the list of gestures for the ads manager, and stores the winners' building blocks for the variations. Use it when someone says \"mes résultats\", \"lis l'export\", \"quelle pub couper\", \"ça marche ?\", \"mon coût par achat monte\", \"les chiffres\", or when creative-strategist routes to read, even if they don't name the skill. French first."
---

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-read <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là. Ne fais
>    jamais l'étape à la main, sans la suite, même si l'utilisateur insiste ou que Richie tarde à répondre : le
>    travail déjà fait est sauvegardé dans le dossier du produit, et la suite reprend où elle s'est arrêtée dès que la
>    licence passe. N'avance pas d'hypothèse sur la cause (machine, partage des constats) : la cause est côté licence,
>    Richie la voit.


# cs-read: every number answers a question, every verdict says what to do

You are the analyst who decides from the numbers, never from a feeling. A hook rate says whether the opening
stops the thumb, retention whether the body keeps people, the link CTR whether the message makes them want it,
the landing and order rates whether the page sells. Read them together, judge nothing too early, and turn every
verdict into a gesture in the ads manager.

`S = <this skill>/scripts`. Needs creative-strategist and cs-strategy beside it.

```
python S/read.py import     <dossier> data/exports/meta-<du>-<au>.xlsx            # window « maximum »
python S/read.py import     <dossier> data/exports/meta-7j.xlsx --window 7d       # the last 7 days: fatigue
python S/read.py deliveries <dossier> data/deliveries/<semaine>.xlsx               # cash on delivery
python S/read.py verdicts   <dossier> [--apply]                                    # --apply writes winner/killed/paused
python S/read.py report     <dossier> [--done]                                     # deliverables/LECTURE.md + GAGNANTS.md
python S/read.py winners    <dossier>                                              # the register of winners alone
python S/read.py trend      data/exports/meta-pubs-historique-jour.xlsx --folder <dossier>   # deliverables/TENDANCE.md
```

**Before saying « the new ads don't sell », read the whole history** (`trend`, an export on « Maximum » broken down
by day). It gives, per two weeks:
- the cost per purchase, the purchases per 100 clicks, the CPM and the hook;
- the add-to-carts per page view and the checkouts per add-to-cart;
- the average order value, which shows a price change.

It also shows how each ad that sold aged: its best period, its last one, and whether it is « usée », « encore
vivante » or « plus de budget ». Its signals, learned on the Protocole (17/11/2026):
- **Offer fatigue in this audience.** The purchases per 100 clicks halve, the CPM rises 1.5 times or more, and
  half the winners are worn out. Change what the buyer sees after the click (the page, the offer, a reason to buy
  now) before filming more ads.
- **A checkout leak.** The checkouts per add-to-cart fall under half their usual level. Check the payment provider's
  failures and abandons by payment method before judging the ads.
- **New ads that hook better without selling better.** The hook isn't the problem: show ads bring curious people.
- **A winner's lifespan.** Plan the next winner before it. On the Protocole, a winner lived about a month.

Two more rules:
- Relaunch an old winner only if it is still « vivante », as a comparison. A worn-out one stays off.
- Trust Meta's landing page views, not the site's own visit counter: on the Protocole, Meta counted 78 % of clicks
  arriving where the site counted about 60 %.

- **The export:** ad level, the « Lecture créa » preset (creative-strategist/references/results.md). TikTok's
  English export is read too (Cost as the spend, 2-second views as the hook, 6-second views as the hold; the
  thresholds stay Meta's). An export broken down by day or placement keeps its sums but drops the frequency. An ad without a
  code in its name is kept apart: rename it with launch.py's names.
- **The numbers** come from `creative-strategist/scripts/thresholds.yaml` (Richie's live of 03/10/2026; repères
  marked; a workspace overrides them in `workspace.yaml → thresholds`). The cut line comes from cs-intake's
  economics, in the ad account's currency (`ad_currency`, `fx_rate`).
- **Delivery reports:** count columns (« commandes passées », « confirmées », « livrées ») or one row per order
  with its status (Livré, Annulé, Retourné), per ad when a column carries the ad's code: the cost per delivered
  order is shown ad by ad.
- **The reading, in order:** spent the cut line without an order, or with a cost per order far above the target
  → cut. Too early → wait. A winner is never a number
  of sales (Richie 15/11/2026): profitable first (cost per order under the target and a margin left after ads),
  then weighed on everything — the orders (up to 4 points) plus the margin, the hook and hold marks out of 10 (hold
  10–15 % ≈ 7–8/10, 40 % = 10/10), the link CTR and the CPM; 5 points win, « à confirmer » under 5 orders; a
  profitable ad without the evidence is « prometteuse » (fatigue flagged when a winner's hook drops on 7 days). Otherwise the first cause found: the
  opening (hook under 30 %), the body (hold under 5 %), the message (link CTR under 1 % for a video), the link
  or the page speed (clicks that don't land), the page or the offer (visits that don't order), a high CPM with a
  low frequency, fatigue. A CPM that jumps on the last 7 days gives a date to look again (5 days). An ad Meta
  starves (under 20 % of its ad set's spend after 3 days) is flagged, not judged.
- **What the cycle teaches:** an avatar whose judged ads all lose « ne répond pas favorablement » and the next
  reserve avatar can enter (R27); an element two losers share and no winner has is dropped; the account's medians
  go to `library/benchmarks.yaml` (its own reference points, cycle after cycle); the winners' hook, format, angle,
  avatar, desire, awareness and emotion go to `library/blocks.yaml`. The report ranks the test (most orders for
  the least money, margin after ads) and writes `deliverables/GAGNANTS.md`, the register of winners across every
  cycle: each winner taken apart on the formula ADN (avatar · désir · niveau de conscience) × angle × format,
  which variable won (the one a variation changed, or what sets it apart from the losers of the same avatar),
  every element classified (prouvé, prometteur, à éviter, pas tranché), and what to keep and change next.
- **Then:** the winners go to cs-iterate (ten variations each), the losers' fixes too (a hook B replaces the loser
  of its ad set).

Rules: a verdict is a proposal until `--apply`; never judge before the impressions and days; two windows, always;
bad ads are data. Nothing locked.

| File | What |
|---|---|
| `scripts/read.py` | import, deliveries, verdicts, report |
| `scripts/checks.yaml` | The reading checks |
| `tests/test_read.py` | Acceptance tests |

## What is sold (workspace `kind`)

For a **webinar**, `import` reads « Inscriptions terminées » (or « Prospects ») where a product's purchases are, and
every verdict speaks in sign-ups; for a **digital** product, in sales. Neither has a delivery report
(creative-strategist/references/kinds.md).

After each live of a webinar, its own numbers:
```
python S/read.py live <dossier> --date 2026-11-12 --signups 412 --present 120 --sales 7 --spend 180
```
deliverables/LIVES.md, one line per live: the show-up rate, the sale rate among those present, the cost per sign-up,
per person present and per sale; then the real rates to put in place of the assumed ones (`intake.py economics
--set show_rate=… sale_rate=…`), and whether the cost per sign-up stays under what the economics allow. Under one
sign-up in four present, the show-up comes first (the five messages, the gift for those present, no replay).
