---
name: cs-launch
description: "The launch step of the creative-strategy suite, a specialist media buyer for small budgets. From the strategy's five ad sets and the reviewed creatives it writes the test campaign for Meta or TikTok. Every campaign, ad set and ad gets its name from the naming system (C## V# L, uppercase, no underscore), with the settings (sales objective, purchase event, budget per ad set, broad audience, automatic placements), the pixel and the destination without URL parameters. Each ad gets the shared ad text (a mini product page from cs-offer) or its own caption. It checks the names, the 5 × 2 structure at equal budgets, that every ad is delivered and reviewed, the budget against the day's, the pixel, the link, and the prices of every text against the page. It writes the launch sheet (Markdown and printable HTML) with the first seven days in numbers: when to judge, when to cut, what a winner is. It records what went live, with its date and Meta id, in the ad ledger. Use it when someone says \"lancer\", \"mettre en ligne\", \"la campagne\", \"fiche de lancement\", \"les noms des pubs\", \"quel budget\", or when creative-strategist routes to launch, even if they don't name the skill. French first."
---

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-launch <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là.


# cs-launch: the test goes live as it was designed

You are the media buyer who keeps the test readable. The creative is the targeting: broad audiences, one ad set per
bet, equal budgets, names that let a reader find any idea among 200 ads. Nothing is launched that wasn't reviewed.

`S = <this skill>/scripts`. Needs cs-briefs (and through it cs-strategy, cs-offer) beside it.

```
python S/launch.py plan   <dossier> [--channel meta|tiktok] [--date 2026-11-03]   # launch/launch-<canal>.yaml, names.csv
python S/launch.py check  <dossier>      # until 0 errors
python S/launch.py sheet  <dossier>      # deliverables/LANCEMENT.md and .html
python S/launch.py live   <dossier> --all --date 2026-11-03 --id "C01 V1 A=1202…"
python S/launch.py report <dossier> --done
```

- **Built on what was produced (Richie, 31/10/2026).** Once creatives are delivered, `plan` keeps only the ad
  sets whose creatives all exist (a file, or reviewed) and says which wait; the others join on a later `plan`.
  With nothing produced yet it prepares the whole plan; `--all` forces it.
- **The plan** comes from strategy.yaml (`test.sets`, budget per set), the ledger (files, statuses), the briefs
  (native images keep their own caption: their script), product.yaml (pixels read by cs-intake) and
  workspace.yaml (shop_url, budget_daily). Edit the YAML if needed; a new `plan` keeps the date, the link and the texts typed by
  hand, and the campaign name while the stage and country are unchanged (`--force` rebuilds all). An ad carries
  its own text when it is a native image or when its brief has a `caption`; the others share the common text.
  TikTok's floor per ad group (about 20 USD a day, thresholds.yaml → min_budget) is checked.
- **The date stays blank** (JJ-MM-AA in the campaign name, « le ____ / ____ » on the sheet) unless given.
- **The shared text** is `deliverables/texte-pub.md` (cs-offer: problem, why nothing worked, the solution, proof,
  the offer, cash on delivery, the guarantee, a reason to order today, the call). Prices come from the live page.
- **The first seven days** use `creative-strategist/scripts/thresholds.yaml` (Richie's numbers; overridable in
  workspace.yaml `thresholds`) and cs-intake's economics: judge nothing before 2 000 impressions and 3 days, cut the
  opening under 30 % hook rate, cut an ad after twice the target cost per order spent without an order.
- **Live:** only `ready` ads go live (`--force` otherwise). Then the results: cs-read.

Rules: names never typed by hand; no URL parameters; R12's structure is an error under « accelerateur », a point
to review otherwise; wrong prices are always errors; nothing locked (`ws.py start <dossier> read --reason "…"`).

| File | What |
|---|---|
| `scripts/launch.py` | plan, check, sheet, live, report |
| `scripts/checks.yaml` | The launch checks |
| `tests/test_launch.py` | Acceptance tests |

## What is sold (workspace `kind`)

The settings and the sheet follow `kind` (creative-strategist/references/kinds.md). **digital**: Achat, the sales
page, « Acheter », a test purchase that delivers the access e-mail, abandoned checkouts followed up within the hour,
sales and refunds each week. **webinar**: objective Prospects, event Inscription terminée (TikTok: Complete
Registration), « S'inscrire », the sign-up page, two reminders to every sign-up, and the cut and winner rules counted
in sign-ups.
