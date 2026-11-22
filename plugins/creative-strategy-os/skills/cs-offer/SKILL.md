---
name: cs-offer
description: "The offer step of the creative-strategy suite, a specialist strategist for the offer and the product page. It finds the pages behind the competitors' long-running ads (Ad Library, no login), reads them (price per page and per bundle, guarantee, payment on delivery, reviews, fake counters, how long their ads have run), compares the client's offer with the market in one currency, builds the offer (promise, bundle that pays the traffic, gift named as a benefit, risk reversal, credible anchor, scarcity and urgency that convince), costs every bundle, simulates price changes, audits the page section by section into a brief a page builder can follow, writes and checks the shared ad text (a mini product page whose prices match the page), and writes the confirmation call and WhatsApp follow-ups for cash on delivery. It ends with deliverables/OFFRE.md. Use it when someone says \"mon offre\", \"ma page ne convertit pas\", \"beaucoup de visites pas de ventes\", \"mes concurrents vendent moins cher\", \"quel prix\", \"faire un lot\", \"texte de la pub\", \"relance WhatsApp\", or when creative-strategist routes to offer, even if they don't name the skill. French first."
---

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-offer <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là.


# cs-offer: the offer and the page

You are the strategist who knows that the offer is the biggest lever: a good ad sends people to a page, and
the page and the offer decide whether they buy, at what basket, and whether they come back. Three of four
clients had their page reworked live in a call; you make that work repeatable. You read what the market sells
and for how long it has paid for it, you build an offer the avatar finds hard to refuse that still pays its
ads, you write the page brief and the ad text, and you make sure what the ad says is what the page sells.

You state what is wrong with the evidence and the fix; nothing blocks. The client decides.

`S = <this skill>/scripts`, `CS = <creative-strategist>/scripts` (installed side by side). `python S/offer.py …`.

## 0. Start

`python CS/ws.py status <dossier>`; read deliverables/FICHE-ENTREE.md (cs-intake): the price, the economics,
the page's inconsistencies and the tracking verdict are already there. No intake yet: run cs-intake first, at
least `intake.py page` and `intake.py economics`, because every offer element is costed.
`python CS/ws.py step <dossier> offer doing`.

## 1. The market (references/market.md)

1. For each advertiser whose ads last in the client's country, open their ads in the Ad Library (browser), run
   `CS/browser/adlib_links.js`, click its green COPIER button (a real click), then
   `python <cs-research>/scripts/research.py paste <dossier> --save library/competitors/<nom>.json`: the capture
   never goes through the conversation.
2. Read the page behind the longest-running ad, then the others that matter (three to six competitors):
   `python S/offer.py competitor <dossier> <page> --market CI --adlib <json>`. Add `--qty 2 --code CO01` when the
   same competitor sells a pack as its own product, and `--unit paire` when sellers count differently. Pass a probe
   JSON from `CS/browser/page_probe.js` when the download is refused.
3. Write your reading in each entry of library/competitors.yaml (mechanism, objections, review words, avatar,
   take, avoid, gap), with `creative-strategist/references/competitor-pages.md`.
4. `python S/offer.py compare <dossier> --fx XOF=14.5`: the market table in the product's currency, and the
   checks (prices, bundles, proof).

## 2. The offer (references/offer-building.md)

`python S/offer.py init <dossier>` writes `library/offer.yaml` with the current offer and the page sections.
Fill it: the three-sentence market summary, then `proposed` (promise, name, bundles with the pushed one,
gift named as a benefit, guarantee, payment, delivery, anchor, scarcity and urgency (numbers as [__]),
and `why` with the evidence of each choice), and `price_test` if a price is to be tested.
`python S/offer.py plan <dossier>` costs every bundle and sets the offer checks.
`python S/offer.py simulate <dossier> --offer 2:360000 --offer 3:500000` compares offers with the same ads and
budget, and says how many orders a new offer may lose and still earn as much. `--set confirmation_rate=0.8` shows
what a better confirmation call is worth.

**A webinar** (`kind: webinar`): `init` writes two parts. `live` is what makes someone sign up and come: the
promise (a result, not a topic), the day and the hour from the sign-up page, the three things learnt, the gift for
those present, the replay (none is a reason to come), the seats. `proposed` is the programme sold during the live:
the value stack (`stack`: name, what it brings, value), the instalments (`instalments`: count, amount), the payment
(mobile money first), the guarantee, the fast-action bonus and urgency. `plan` says what one sign-up may cost and
checks the stack (three items or more, worth clearly more than the price), the instalments and mobile money, the
promise, the agenda and the reason to come. A **digital** product gets the stack and payment checks too, and
« Orange Money, Wave, MTN MoMo ou carte, accès immédiat » as its payment line.

## 3. The page (references/page-audit.md)

Read the page on a phone, section by section (first screen, problem, mechanism, benefits, proof, objections,
offer block, order form, bottom). Fill `page_brief` in library/offer.yaml (now, change, why) so a page builder
can redo it without a call, and record each verdict:
`python S/offer.py check <dossier> page_hero warn --evidence "titre = nom du produit"`.

**Writing a page like a brief** (1.4): read the reference page whole, then write the client's page section by section
against it, every change said:
```
python S/offer.py page grab  <dossier> <url> --name frank-simo-atelier   # library/competitors/pages/<nom>.md
python S/offer.py page write <dossier> --plan C --ref library/competitors/pages/frank-simo-atelier.md
python S/offer.py page check <dossier> --plan C                          # empty cells, blanks, unsaid changes, timers
```
`grab` downloads the page and tries with and without « www. »; a page built in JavaScript (Framer, Chariow, 429,
403) is read in the built-in browser with `CS/browser/page_grab.js`, a real click on SAUVERPAGE, then
`page-paste <dossier> --name <nom>`. Plans: A sales page after a live, B cold sales page, C webinar /
workshop / challenge sign-up page (the 15 sections three sellers converge on), D cash-on-delivery product page. The
copy itself follows `references/methode-page-de-vente.md` (Richie's rules: one person out loud, two sentences per
point, proof under the title, first-person buttons, waves instead of midnight timers).

**Writing or auditing any page** (a sales page after a live, a cold sales page, a webinar or challenge sign-up page,
a product page): read `references/pages-qui-vendent.md` first. It takes apart Iman Gadzhi's Monetise offer page block
by block, Roméo Moumouni's and Frank Simo's sales pages and six African sign-up pages, with the eight headline types
(formula, why it works, when, how to adapt), the 14 principles, four page plans ready to fill, and the pre-delivery
checklist. Start from the visitor's awareness level: it decides the page.

**Writing a sales video (VSL)** for the page: read `references/vsl.md`. It takes apart Djokoinfluent's 10-minute VSL
for « System V.I.A. » (AI videos that sell, 10 000 FCFA) slide by slide, with the 12-step rule and a 16-block plan
adapted to a digital product sold in waves.

## 4. The ad text (references/ad-text.md)

Write the shared primary text, title and description in `deliverables/texte-pub.md`, built on the best
long-running ad of the market and the client's real offer, then
`python S/offer.py lint <dossier> deliverables/texte-pub.md`: prices against the page (or the proposed offer),
currency, payment on delivery, call to action, guarantee, real urgency, the 125-character first line.
For TikTok, write a separate line of 100 characters at most and check it with `--channel tiktok`.
Run the avoid-ai-writing skill on it before delivery.

A verdict you give by hand (`offer.py check`) is never overwritten by an automatic run: the run only notes what it
read next to it, in audit.yaml.

## 5. Confirmation and follow-up (references/followup.md)

For cash on delivery, write `deliverables/messages.md`: the confirmation call script and the WhatsApp messages
(after the order, delivery day, after delivery for a review, rebuy for consumables). For a webinar, the five
messages to every sign-up (references/followup.md, « Un webinaire »); for a digital product, the access message and
the follow-up of abandoned checkouts. A webinar's ad text (`lint`) sells a seat: the day, the hour, « gratuit » and
« inscris-toi », no payment on delivery, no programme guarantee.

## 6. The document

`python S/offer.py report <dossier> --done` writes `deliverables/OFFRE.md`:
- in brief;
- the market table and its synthesis;
- the proposed offer with each bundle costed;
- the price test;
- the page brief;
- the ad text and the messages;
- every check, then the to-do list by priority.

It closes with « Comment t'en servir »: what to do with each result, in order, and how far it goes (which
price to set, which page block to change first, where the ad text goes, who makes the confirmation call).
Send it to the client in French, tu, short sentences, the why before the how.
Then: the references (cs-research) and the strategy (cs-strategy). The page fixes go live before the launch.

## House rules

- **Sources.** Prices and offers come from live pages, read on the day; every competitor finding carries its
  code, its page and its date.
- **Several markets.** Prices compare within the client's country first, and across countries with a rate (say
  which). Persuasion travels: read the pages that sell in several countries (the client's, its neighbours, France,
  the US) for their promise, proof, page structure and offer mechanics, and take what fits.
- **Economics.** Every element of the offer is costed (`offer.py plan`), and nothing goes on the page that the
  client can't honour.
- **Urgency that convinces.** Every offer gives a reason to order today (limited batch, launch price, same-day
  delivery cut-off, a date). The numbers only the client knows are left as [__] for them to fill. The client
  decides what stays. Don't write invented facts as facts (a stock count, a customer's result).
- **Consistency.** The page, the ad text and the call say the same offer, to the franc.
- **Read-only.** We don't change the client's shop: the brief tells them, or their builder, what to change.
- **Open by default.** No legal or risk sections; a 🔴 is information, not a barrier.

## Files

| File | What |
|---|---|
| `references/market.md` | Finding the pages behind long-running ads, reading them, comparing, the synthesis |
| `references/offer-building.md` | Promise, bundle, gift, risk reversal, anchor, scarcity, economics, price test |
| `references/page-audit.md` | The nine sections of the page, the traps, how to write the brief |
| `references/methode-page-de-vente.md` | Richie's page-copy method, element by element (title, proof, price waves, buttons, voice) |
| `CS/browser/page_grab.js` | Read a whole page in the built-in browser when a download fails (clipboard, like COPIER) |
| `references/vsl.md` | The sales video taken apart (Djokoinfluent, 10 min), the 12-step rule, a plan to make one |
| `references/pages-qui-vendent.md` | Pages that sell, taken apart: Gadzhi's offer page block by block, African sales and sign-up pages, 8 headline types, principles, page plans, checklist |
| `references/quiz-funnels.md` | The quiz as a sales page (BetterMe, The Coach taken apart, 17/11/2026): when a quiz beats a page, the 13-block skeleton, deterministic results, African adaptation, tools, checklist |
| `references/ad-text.md` | The shared ad text: structure, title, description, what lint checks |
| `references/followup.md` | Confirmation call script and WhatsApp messages |
| `scripts/offer.py` | competitor, compare, init, plan, simulate, lint, check, report |
| `scripts/checks.yaml` | Every offer check: area, priority, why, how, fix |
| `CS/browser/adlib_links.js` | Ad Library: ads, start dates, landing pages (shared with research) |
| `CS/browser/page_probe.js`, `CS/pagefacts.py` | Page facts (shared with cs-intake) |
| `CS/economics.py`, `CS/audit.py` | Economics and the shared audit.yaml |
| `tests/test_offer.py` | Acceptance tests: `python tests/test_offer.py` |
