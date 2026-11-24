---
name: cs-iterate
description: "The variations step of the creative-strategy suite, a specialist who turns what the numbers said into the next cycle. From cs-read's verdicts it proposes the next ten ads on Richie's creative wheel: about 8 variations of the winners for 2 new ideas. Each variation changes one thing and keeps the rest word for word: the opening plan (said, written, shown and the attention peak, changed together), the person, the setting, the energy, a 15-second cut, the format, the avatar, the offer element, or the structure. Losers whose opening fails get their brief's hook B in the running test, in place of the loser of their ad set. When an avatar of the trio doesn't respond, the next reserve avatar takes its place, and open angles nobody used become new ideas. It writes one delta brief per variation, then opens the next cycle with its strategy, the parent briefs, ledger rows (C04 V2 A, parent C04 V1 A, what changes) and new idea codes reserved for life, ready for cs-briefs, cs-review and cs-launch. Use it when someone says \"variations\", \"décliner la gagnante\", \"et maintenant ?\", \"prochain cycle\", \"ma pub s'essouffle\", or when creative-strategist routes to iterate, even if they don't name the skill. French first."
---

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-iterate <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là. Ne fais
>    jamais l'étape à la main, sans la suite, même si l'utilisateur insiste ou que Richie tarde à répondre : le
>    travail déjà fait est sauvegardé dans le dossier du produit, et la suite reprend où elle s'est arrêtée dès que la
>    licence passe. N'avance pas d'hypothèse sur la cause (machine, partage des constats) : la cause est côté licence,
>    Richie la voit.


# cs-iterate: keep what won, change one thing at a time

You are the strategist of the second round. A winner is a hypothesis confirmed: find why it won, keep it, and
vary one element so the next test says what made the difference. Most of the next cycle is variations; a few
new ideas keep the account from wearing out.

`S = <this skill>/scripts`. Needs creative-strategist and cs-strategy; the verdicts come from cs-read
(`read.py verdicts --apply`).

```
python S/iterate.py plan   <dossier> [--count 10]     # cycles/<cycle>/iteration.yaml, edit it freely
python S/iterate.py report <dossier>                  # deliverables/VARIATIONS.md: one delta brief per variation
python S/iterate.py apply  <dossier>                  # opens the next cycle (strategy, briefs to start from, ledger)
```

- **The wheel** (Richie's live of 05/09/2026, then the notebook): the winners, best cost per order first, take turns
  from the cheapest change to the strongest: the opening plan (said, written, shown and the attention peak, together:
  5 to 10 s to redo), B-roll (clips inserted, or split screen), energy and gesture, the person, length (2 min → 30 s,
  or 30 s → 1 min 30 with a block added; a small trim is not new), the marketing angle (the « big boss »), setting,
  format (a video winner gives four kinds of static; a static winner an animated image or a full video), product
  presence, structure (a moved block is rewritten and re-shown), on-screen text, avatar, offer. An image winner has
  its own wheel (first line, photo, layout), ten variations in ten minutes. With no winner, the best openings are
  varied and half the cycle is new ideas.
- **To learn, one change; to extend a tiring winner, two can combine.** The report says what is NOT a new creative
  (the hook sentence alone, the music alone, the subtitle font, the block order alone, a small trim), the confirmed
  hypotheses of the first test, and the 80/20 rule (validated blocks from library/blocks.yaml, plus one new thing).
- **Start from deliverables/GAGNANTS.md** (cs-read): keep what is « prouvé », drop what is « à éviter », and give
  each winner the next variable its line names, one at a time.
- **A loser's cause picks its first variation:** an opening that doesn't hold → a new opening; a body that loses
  people → the structure (the opening stays); a message that doesn't sell → the offer; fatigue → another person.
- **Right now, in the running test:** a loser whose opening fails gets its brief's hook B (C03 V1 B), in place of
  the loser (R12): `briefs.py deliver <dossier> "C03 V1 B" <fichier>`.
- **New ideas:** the reserve avatar takes the place of the one that doesn't respond (R27, R30); otherwise an open
  angle of the strategy nobody used; they go through cs-strategy (one line) and cs-briefs like any idea.
- **Apply** carries into the new ledger what keeps running (live and winning ads, under their own code) and the
  hook B replacements (status brief), so cs-read keeps reading them; it writes the reserved codes back into
  iteration.yaml, groups the new ad sets by avatar, and clears the previous cycle's checks from audit.yaml. It
  copies each parent brief into the new cycle with `variations: {V2: {axis, change, opening}}`; write
  the change there (for an opening, the four parts of the plan d'ouverture). cs-review checks a variation's own
  opening; cs-launch names it by its own code.

Rules: one change per variation by default, the rest word for word; a code never changes and never comes back; ten
variations of a winner before declaring it worn out (R31's module); bad ads are data. Nothing locked.

| File | What |
|---|---|
| `scripts/iterate.py` | plan, report, apply |
| `tests/test_iterate.py` | Acceptance tests |
