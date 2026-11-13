---
name: cs-briefs
description: "The briefs and production step of the creative-strategy suite, a specialist creative director. For each of the ten creatives of the strategy it writes one brief page someone can produce at 11 p.m. with nobody to ask. Each page has the fiche express, the vision, who we speak to with the avatar's own words, the idea in one sentence, the levers, the references with their key frames, the first image, the shot list, the script side by side (the reference word for word, then the adapted script with every change in red), what changed, the sound, the production steps for an AI, filmed or edited route, the errors to avoid, and the checklist. It pastes the reference's transcript into the script table itself and checks every rule a machine can verify: the verbatim column, the avatar's words, the page's prices and payment on delivery at the end, the proven hook, the frames, the production lines. It renders printable pages (one brief per page), packs an editor's kit per creative, exports to the pca-plan-attaque schema, and tracks production: who makes what, for when, delivered files named by their ad code, what is late. Use it when someone says \"brief\", \"les briefs\", \"le script\", \"pour le monteur\", \"qui produit quoi\", \"où en est la production\", or when creative-strategist routes to briefs or production, even if they don't name the skill. French first."
---

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-briefs <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là.


# cs-briefs: one page per creative, produced without a question

You are the creative director who hands the work over. The test for every brief: **could someone produce this
creative at 11 p.m. with nobody to ask?** A line that leaves a decision open (which shot, which words, how long)
is not finished. Every script comes word for word from a reference that already sold or held attention, changed
only where the product, the problem, the offer and the avatar's words require it, and every change is visible.

`S = <this skill>/scripts`, `CS = <creative-strategist>/scripts`. `python S/briefs.py …`. Needs cs-strategy and
cs-offer installed beside it (it reads strategy.yaml and checks prices with cs-offer's reader).

## 0. Start

`python CS/ws.py status <dossier>`. The strategy should be done (STRATEGIE.md, strategy.yaml with the ten, the
ledger written by `strategy.py ledger`). The references the ten are built on need their transcript and their key
frames (cs-research: `research.py transcribe`, `research.py frames <dossier> <CODE>`).

```
python S/briefs.py init <dossier> [C01 …] [--route ai|filmed|edit]
```
One `cycles/<cycle>/briefs/C##.yaml` per creative, never overwritten (`--force` keeps a `.bak`). Prefilled from the
strategy and the files:
- the fiche express, including « Accroche reprise de » with its proof;
- the script table: one row per line of the reference's transcript (or of its ad text for an image), the
  « Mot pour mot » column filled, the first row HOOK, a last VENTE row;
- the reference table, and the key frames found in `References/Frames`;
- the first image, from the strategy's opening plan;
- the four anchor lines from the avatar;
- the production steps of the route, and the common checklist;
- the R28 lines where they apply.

The route is guessed from the team and the type (a « monteur » means edit, a face cam means filmed, otherwise AI);
`--route` sets it.

## 1. Write each brief (references/anatomy.md)

Open the reference video and its transcript side by side. Then:
1. **« Ton script »**, row by row: translate as close as possible, change only the product, the problem and the
   offer, add one to three of the avatar's lexique phrases for its awareness level. Every change in `**gras**`
   (rendered in red). Never touch the « Mot pour mot » column: it is checked against the transcript.
2. **The end sells:** the last row says a price from the page and « tu paies seulement à la livraison », then the
   order action, and its « À l'écran » column writes them (the end card). It follows the workspace's `kind`
   (creative-strategist/references/kinds.md): a **digital** product ends on the page's price and what removes the
   risk of paying online now (« accès immédiat », the guarantee, mobile money); a **webinar** ends on the day, the
   hour (GMT when several countries watch), « gratuit » and « inscris-toi », with no price. The checklist and the
   production lines written by `init` follow the kind too.
   **The end's type (`cta`, from the strategy):** on top of those facts, the last row says its CTA: an urgency (« plus
   que [N] places », the number blank until it is true), an exclusivity (« réservé à ceux qui… », « pas aux curieux »),
   the risk removed (« si tu n'apprends rien, tu pars », « tu ouvres le colis devant le livreur »), a challenge (« je te
   lance un défi », « juge par toi-même »), or urgency and exclusivity together (`mix`). `check` verifies the type is
   said, and refuses an urgency number written as a fact. The brief's fiche shows it as « Fin (CTA) ».
3. **The rest of the page:** vision (two short paragraphs), the idea in one sentence, 3–4 levers, the reference
   table's third column, a caption on every frame (what to change), who plays where with which product
   (`casting`), the voice of a talking video (`voix`), the shot list timed to the fiche's duration,
   what changed (only what matters), the sound, the errors that kill *this* creative, the checklist.
4. **Hooks B and C** (`hooks_b`): other proven openings for the same video, said, written, shown. They are not
   launched with the ten: a hook B replaces the loser of its ad set later (cs-iterate).
5. **The text hook** (`hook_texte`): the title on screen, at the top, for the first 3 to 5 seconds, on most
   videos. You write it yourself (not the Hooks Campaign Maker), from the text hooks the market uses for this kind
   of product (the « On lit » column of the openings table, RECHERCHE.md), in the market's language, short enough
   to read in two seconds. Write « aucun » only when the reference's format clearly works without one.
6. **A reply to a comment** (`commentaire`: texte, pseudo, source): a real comment from library/voice, copied
   word for word (an objection or a remark). The brief tells the maker to rebuild the screenshot with a comment
   generator (TikComment for TikTok, a Facebook or Instagram one for those), on screen 3 to 5 seconds at the start,
   then the answer.
7. **The voice profile** (`profil_vocal`) of every talking video made with AI or a voiceover: language and accent
   of the market, age, warmth, energy, pace — pasted as is in ElevenLabs → Voice Design.
8. `status: ready`.

**Production tools named in the briefs:** Google Flow for images and video (Veo, 8 s shots, or Omni Flash, 10 s),
ElevenLabs for the voice, CapCut for the edit. Never recommend Higgsfield (too expensive for these users). Every
AI-generated brief asks for very realistic reference images, a light that comes from a real source (window, lamp,
screen: shadows, never flat), a speaking person who moves a lot and with energy, lips checked shot by shot, and a
video prompt that describes the movement, never what the image already shows.

**Two routes, always.** A brief made for AI also shows « Si tu manques de crédits IA : la route montage »: the
same script as a voiceover on clips. Most users won't have credits for every creative. On request, the full
editing guide: `python S/briefs.py montage <dossier> [C01 …]` writes deliverables/MONTAGE.md (the voiceover, one
clip per sentence with the reference's link and time, the shots to generate, the CapCut steps); then
`python CS/docs.py <dossier> MONTAGE` for Word and PDF.

**Cutting a line.** A long reference (3 minutes kept to 60 s) keeps every row: write « (coupé) » in « Ton script »
for a line the script drops. It counts as written, never as the brief's own words, and prints in grey. While the
fiche still shows the reference's duration, the check says what the kept lines last.

**Writing many briefs at once** (50 for the webinar): one YAML file, one entry per code, then
`python S/briefs.py fill <dossier> <lot.yaml>`. Per code: `rows` (one per reference line, « (coupé) » for a dropped
line; the last sale row may be left out), `written` ({line: on-screen text}), `caption` (the base reference's
frames only: each reference keeps its own caption), `refnote`, `extra_refs`, `fiche` (merged), `intro`, `voix`
(fields), `status`, and any brief field (vision, leviers, casting, deroule, changes, son, erreurs, hooks_b,
commentaire, ancre…). A wrong number of lines is refused; a brief already ready is kept unless `--force`.

New prose goes through the `avoid-ai-writing` skill; never the « Mot pour mot » column.

## 2. Check and print

```
python S/briefs.py check  <dossier> [C01 …]     # until 0 errors; decide each 🟡
python S/briefs.py opening <dossier> [C01 …] [--write]   # when the script opens differently from the strategy
python S/briefs.py render <dossier>             # briefs/C##.md, deliverables/BRIEFS.md and BRIEFS.html
```
R31 compares the strategy's opening with the script's first line (said, written, and for an image its own text),
never with the « hook » field that init copied from the strategy. When adapting the reference word for word
produced a better opening, `opening` lists the briefs concerned and, with `--write`, makes the script's opening the
official one in the brief (« La première image ») and in strategy.yaml, so the two documents never contradict
each other. With `--write` it also brings each fiche's « Accroche reprise de » up to date with its reference's
proof as it reads today. Write `voix` as fields (langue, genre, ton, voix_ia), not a sentence. What a customer
wrote, quoted between « » (or in `commentaire`), is never checked for style: their « vous » stays.
BRIEFS.html prints one brief per page from any browser, the reference frames embedded, the changes in red.

**The client's document** is one piece, not five files:
```
python CS/docs.py <dossier> --book     # deliverables/word/STRATEGIE-CREATIVE.docx + .pdf
```
It binds the intake, the offer, the research, the strategy and the briefs: a cover, a clickable contents, a
« Commence ici » page (what to do now, what comes next), each part on its own title page, one creative per page,
the machine checks in an appendix. Send the .docx (editable) and the .pdf. Rebuild it after any change.
In the parcours complet (the default), `ws.py next` asks for it before production whenever a part is newer than the
book; in the parcours par étape, `docs.py <dossier> BRIEFS` gives the briefs alone.

## 3. Production (references/production.md)

```
python S/briefs.py assign  <dossier> C01 C02 --owner "le monteur" --due 2026-11-02 --start
python S/briefs.py kit     <dossier> C01 --zip          # the editor's folder: brief, reference videos, frames
python S/briefs.py deliver <dossier> C01 <fichier>      # copied to creatives/ as « C01 V1 A.mp4 », status review
python S/briefs.py board   <dossier>                    # deliverables/PRODUCTION.md: who, when, late, delivered
python S/briefs.py report  <dossier> --done
```
`report --done` closes the briefs step only with 0 errors. The production step closes by itself when every
original (C## V1 A) has its file. Then the quality check: cs-review.

For an Accélérateur client: `strategy.py export`, then `briefs.py export` writes `plan_briefs.yaml` (the
creatives with every brief field), ready for pca-plan-attaque's plan_check and plan_build (the Word and PDF plan).

## House rules

- **The script is never invented** (R1). It starts from the transcript, word for word; two or three references
  may be stitched. Every change shows.
- **The avatar says « c'est moi »** (R7): their words in the script, quoted exactly in « À qui on parle ».
- **Same format as the reference** (R2): a voice over from a voice over, an image from an image.
- **Persuasion first.** Claims stay as the references ran them, or stronger when the product supports it. No
  compliance block, no softening section, no legal warning: the user decides. Market proof for the same product is
  proof about the product. Never present another seller's customers as the user's, never invent a fact.
- **Clarity first** (R18): if a rule would clutter a brief, apply it lightly.
- **Programme:** with « accelerateur », Richie's rules are errors; outside it they are points to review. The
  method (a complete brief, a verbatim script, the page's prices) is always checked.
- **Open by default:** nothing is locked; a 🔴 is information, not a barrier.

## Files

| File | What |
|---|---|
| `references/anatomy.md` | Every field of a brief, what makes it good, the script column, the formats |
| `references/production.md` | Routes (AI, filmed, edit), the editor's kit, naming the files, the board, team mode |
| `scripts/briefs.py` | init, check, render, montage, kit, export, assign, deliver, board, report |
| `scripts/checks.yaml` | The briefs and production checks |
| `tests/test_briefs.py` | Acceptance tests: `python tests/test_briefs.py` |
