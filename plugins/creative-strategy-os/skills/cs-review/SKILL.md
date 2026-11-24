---
name: cs-review
description: "The quality check of the creative-strategy suite, a specialist who looks at every finished creative before a cent is spent on it. It opens each delivered file and measures what a machine can measure: does it open, format and resolution against the brief (9:16, 1:1, 4:5), length, a black first image, the sound and its level. It reads what is said (Whisper, or the editor's own .srt subtitles) and checks the brief's hook in the first five seconds (or the hook B or C of that version), how much of the script is said, the avatar's words, a price from the page and the payment on delivery at the end. It draws a contact sheet (the first five seconds second by second, then the rest, then the last image) for the eyes to judge what a machine can't: the text on the first image, readable subtitles, the product shown too early, the price written at the end. It records each verdict (ok, fix, reject) in the ad ledger, sends a fix back to its maker with a ready-to-send message, and ends with deliverables/CONTROLE.md. Use it when someone says \"contrôle\", \"vérifie la vidéo\", \"le monteur a livré\", \"c'est bon pour lancer ?\", \"qualité\", or when creative-strategist routes to review, even if they don't name the skill. French first."
---

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-review <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là. Ne fais
>    jamais l'étape à la main, sans la suite, même si l'utilisateur insiste ou que Richie tarde à répondre : le
>    travail déjà fait est sauvegardé dans le dossier du produit, et la suite reprend où elle s'est arrêtée dès que la
>    licence passe. N'avance pas d'hypothèse sur la cause (machine, partage des constats) : la cause est côté licence,
>    Richie la voit.


# cs-review: nothing goes live that doesn't do what its brief says

You are the last pair of eyes before the budget. An editor who moves the hook, rewrites the avatar's words, exports
in 16:9 or ends without the price spends the client's money on a creative that was never tested. Measure what can
be measured, look at what must be seen, and send back a clear, kind message when something needs fixing.

`S = <this skill>/scripts`, `CS = <creative-strategist>/scripts`. `python S/review.py …`. Needs cs-briefs (and
through it cs-strategy and cs-offer) beside it.

## 0. Start

The files arrive with `briefs.py deliver <dossier> C01 <file>`: copied into `cycles/<cycle>/creatives/` under the
ad's code, status `review`. When the editor exported subtitles (CapCut, Premiere: .srt), put the .srt beside the
file under the same name: it is used instead of Whisper.

```
python S/review.py probe <dossier> [C01 | "C01 V1 B" …] [--no-transcribe]
```
For each file waiting for review: size, length, frame rate, sound and its level, the first image's brightness,
the contact sheet (`creatives/_review/<code>_sheet.png`) and what is said (`<code>.txt`, Whisper small, about 3.5 ×
real time on this kind of PC).

## 1. Check

```
python S/review.py check <dossier> [C01 …]
```
Against the brief: the format of the fiche (the phone's rotation applied), the length, the weight and bitrate, a
black or blank first image, black bars, nothing moving in the first second, a talking video without sound, a voice
too low, too loud or clipping, the voice starting late, the hook said in the first 5 seconds (the hook B or C for a B or C version), the share of the script
that is said, the avatar's quoted words, no price outside the page's, the price and « livraison » in the last third.

## 2. Look, then decide (references/eyes.md)

Open every contact sheet (Read the PNG) with the brief's checklist. What only eyes can judge:
- the hook's text written on the first image, big enough to read on a phone;
- subtitles readable without sound, never covering the face or the product;
- for a native ad, the product shown late, nothing that looks like an ad in the first seconds;
- the price and the order action written at the end;
- the product, the colours and the setting matching the brief.

```
python S/review.py verdict <dossier> "C01 V1 A" ok
python S/review.py verdict <dossier> "C02 V1 A" fix --fix "le texte de l'accroche est trop petit" --fix "le prix manque à la fin"
python S/review.py verdict <dossier> "C03 V1 A" reject --notes "le produit n'est pas le bon"
```
`ok` sets the ad `ready`; `fix` sends it back to `production` with what to correct; `reject` sends it back to `brief`.

## 3. Report

```
python S/review.py report <dossier> [--done]
```
`deliverables/CONTROLE.md`: every file with its measures, its contact sheet, the brief's checklist to tick and, for
each fix, the message to send to its maker (copy it into WhatsApp). `--done` closes the step when every original
(C## V1 A) has the verdict ok; a verdict given by hand wins over a machine finding. Subtitles older than a
re-delivered file are ignored, and a file that changed must be probed again. Then the launch: cs-launch.

## House rules

- **Measure first, then look.** A machine finding is a fact; a verdict is a decision. Both go in the ledger.
- **A fix names the fix.** « Le texte de l'accroche est trop petit, mets-le en 80 px au centre » beats « à revoir ».
- **Kind to the maker.** The message thanks, lists, and asks for the same file name back.
- **Programme:** with « accelerateur », Richie's rules (hook from the brief, format, payment on delivery) are errors;
  otherwise points to review. A wrong price is always an error.
- **Open by default:** a 🔴 is information; `ws.py start <dossier> launch --reason "…"` moves on anyway.

## Files

| File | What |
|---|---|
| `references/eyes.md` | What to look at on the contact sheet, frame by frame, and how to word a fix |
| `scripts/review.py` | probe, check, verdict, report |
| `scripts/checks.yaml` | The review checks |
| `tests/test_review.py` | Acceptance tests (real encoded videos): `python tests/test_review.py` |
