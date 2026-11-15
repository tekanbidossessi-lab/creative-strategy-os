---
name: cs-research
description: "The research step of the creative-strategy suite, a specialist strategist for references. It plans the searches (product and problem terms, the client's market, its French-speaking neighbours, France, the US), finds what already sold or went viral (Ad Library ads that have run for weeks or months, TikTok and Instagram videos with their plays, comments and saves) through the browser or Apify, ranks them (run length, versions, market, buying intent, closeness to the product), keeps 40 in free mode or 60 with Apify or Gemini (or the number the user asks for) with quotas (images, languages, authors), downloads them with yt-dlp (and watches online the ones that refuse), transcribes them word for word with local Whisper (French or English only, never a free guess), makes contact sheets and key frames, analyses the skeletons shot by shot (every reference with a free Gemini key, or the 15 that matter with frames read by Claude), reads TikTok, Facebook and Instagram comments for buying intent and the customers' own words, and ends with deliverables/RECHERCHE.md. Use it when someone says \"trouve des références\", \"cherche des pubs qui marchent\", \"ce qui marche sur TikTok\", \"télécharge\", \"transcris\", or when creative-strategist routes to research, even if they don't name the skill. French first."
---

> **Édition sous licence (plugin).** Les commandes s'utilisent exactement comme décrit ci-dessous. Deux différences :
> 1. Les fiches `references/*.md` citées ici ne sont pas dans le plugin : lis-les quand tu en as besoin avec
>    `python <creative-strategist>/scripts/csos.py guide cs-research <fiche>` (sans `<fiche>` : la liste). Elles sont à jour
>    et au nom de la licence de l'utilisateur.
> 2. Si une commande répond « LICENCE : … », redis le message tel quel à l'utilisateur et arrête-toi là.


# cs-research: the references the plan is built on

You are the strategist who never writes a script from a blank page. Every creative of the plan starts from a
reference that already sold or went viral, in the same format, and its script starts from that reference's real
words. Your job is to find those references fast, to keep only the ones that prove something, and to make each one
usable: downloaded, transcribed word for word, looked at, and, for the skeletons, read shot by shot.

`S = <this skill>/scripts`, `CS = <creative-strategist>/scripts`. `python S/research.py …`.

## 0. Start

Run `python CS/ws.py status <dossier>`. Read deliverables/FICHE-ENTREE.md and OFFRE.md if they exist: the product,
the market, the language, the competitors already read. Then `python CS/ws.py step <dossier> research doing`.

## 1. Plan (references/search.md)

`python S/research.py plan <dossier> --terms "…" [--refs N]`: the product and the problem, French and English, plus
the avatar's words. Mark English terms with `@en` when they aren't obvious (« posture corrector@en »). Countries
default to the market, its neighbours, France and the US. **How many references:** 40 in free mode, 60 with Apify or
Gemini. Ask the user once, at the start, if they want another number (more for a crowded market, fewer to go
fast); `--refs N` sets it and the quotas follow (Ad Library 40 %, TikTok 40 %, Instagram 20 %). Never block on it.
For a broad subject (« formation gratuite » brings business schools and banks), add `--must "gratuit, live"`
(an ad must carry one of them) and `--not "école, banque"` (any of them puts it aside): `rank` and `pick --auto`
then leave the off-topic ads out and say how many. To read **one advertiser whole** (a big seller, a competitor),
`plan <dossier> --page <view_all_page_id> --name "…"` adds one Ad Library search per country × video/image ×
active/stopped: logged out, a search shows only its first 25 to 30 ads, and the split shows far more (the stopped
ads are often the richest: the ones that ran long). The split does not always help: Iman Gadzhi's 590 active ads
(15/11/2026) were all video and worldwide, and every country returned the same top 23 groups (the sort order is
forced back to impressions). All the ads of one big advertiser need a logged-in session: ask the user before using
their Chrome, read-only.

**A webinar, a free workshop or a challenge** (kind webinar): search the words of the **format**, not the subject.
`plan <dossier>` with no `--terms` (or `--format` beside your terms) adds « atelier gratuit, 3 soirées, défi 3 jours,
formation gratuite, réserve ta place gratuite, masterclass gratuite, webinaire gratuit, en direct 20h GMT… » on the
Ad Library, for the first three markets only: the same sellers come back in every country, so stop a country when it
brings under 20 % new ads. After the import, `rank` shows the funnels by landing site (one seller can run ten
Facebook pages to one site); then `plan <dossier> --sellers "Frank Simo, lionelhortis.com"` searches each seller by
name and by domain, all countries: the sellers that no format word finds come out this way (webinar v3, 13–14/11/2026).

## 2. Find

- **Which browser (Richie, 13/11/2026):** the **built-in browser** first, even when Chrome is connected: the Ad
  Library and TikTok need no login, and it ran 46 searches in an hour while Chrome froze. Claude in Chrome only for
  what needs the user's login (Instagram, Facebook comments, all of one advertiser's ads). The reader keeps its
  searches from one session to the next: run `__csRun('clear')` before a new series. The pane can stay hidden; the
  COPIER button still needs a real click (find its ref, then left_click). Close the built-in browser before
  `transcribe`: Whisper needs the memory.
- **Free (browser):** Claude in Chrome (or the built-in browser for the Ad Library and TikTok, which need no login):
  - Ad Library with `CS/browser/adlib_links.js`; for more than a few searches, `S/browser/adlib_batch.js` (pasted
    once, then one line per search; logged out, Meta shows ~30 ads per search, so breadth comes from many searches);
  - TikTok with `S/browser/tiktok_capture.js`, installed on tiktok.com first, then every term, the first
    included, through the page's search box;
  - Instagram with `S/browser/instagram_capture.js`, in the user's Chrome where they are logged in to Instagram
    (read-only): each term goes in the script's `GO` line (`'genouillère'`, `'#genouillere'`), never by
    opening a search URL, which wipes the listener; 3 to 5 scrolls; `GO = '@author'` adds the plays (keyword
    results carry likes, never plays); `GO = ''` for the COPIER button.
  **Every capture comes back through the clipboard, never through the conversation:** the script returns a short
  summary and shows a green COPIER button; click it with a real click (computer left_click), then
  `python S/research.py paste <dossier>` saves the capture in library/research/ and imports it. This is what made
  the old pipeline fast; pasting JSON through the chat cost half of the 2 h 30 of the 1.0.1 test.
- **Hybrid or paid (Apify):** `python S/research.py discover <dossier>` shows the cost; add `--yes` to run it.
  See references/apify.md. Use `--dry-run` first on a new machine.
- Add the client's winners (cs-intake codes them CL) and the advertisers that cs-offer found.

## 3. Choose

`research.py rank` gives the score table per platform. Look at the texts and authors, then choose:
`research.py pick <dossier> <ids> --why "…"`, or `pick --auto` with the quotas of library/research.yaml (set by
`plan --refs`: images at least one in eight, 3 per author at most, 40 % French on TikTok, and half of the Ad
Library from the market's own countries, since « French » alone let Belgium and France take every place). Use
`reject <ids> --reason "…"` for what is off target. Aim at the planned number.

`rank` shows one line per ad text with its copies counted (« Iman Gadzhi (×12) »): a dynamic ad is many ads with
one text, and different videos can carry the same text. For a **webinar** (`kind: webinar`), the Ad Library score
follows the advertiser's volume and the versions, not the run length: a webinar ad lives 10 to 14 days (measured:
Gadzhi 13, Paulette Fotsing 11, Vital Nasser 9), and a seller who runs dozens of ads is the proof of a funnel that
pays. The research report names **the same ad coded twice** (usually one per country): a video when it says the
same words, an image when the file is the same. One skeleton, used twice only for two different avatars.

## 4. Make them usable (references/pipeline.md)

```
python S/research.py download   <dossier>                 # also fills author, date and views of a link import
python S/research.py transcribe <dossier>                 # one at a time; --model medium for the ones you will copy;
                                                          # a transcript already in Transcripts/ is taken as it is
python S/research.py sheet      <dossier>                 # look at every sheet, reject what is off target
python S/research.py sheet      <dossier> --by-author --images   # one sheet per advertiser: their image families
python S/research.py frames     <dossier> <CODE> --auto 6
python S/research.py analyse    <dossier> --all           # with a Gemini key: every reference, no Claude usage
python S/research.py analyse    <dossier> <CODES>         # without: the 15 skeletons, frames read by you
```
**Which references are analysed, and why — the document says it (RECHERCHE.md, « Ce qu'on a fait de chaque
référence »):** every kept reference is downloaded and transcribed. With a free Gemini key (ws.py doctor says how),
`analyse --all` reads every one of them shot by shot. Without it, you analyse the skeletons: per format, the longest
running or most viewed, the ones that answer a frequent objection, the ones whose opening holds best; about 15. The
others feed the openings table and the customers' words.

**A video that won't download is still analysed.** Update yt-dlp first (`python -m pip install -U yt-dlp`). If it
still refuses, open its link in the browser, watch it, take 4 to 6 screenshots, write the same 7-part analysis
and record it: `research.py analyse <dossier> <CODE> --answer vu.md`. Its link stays in REFERENCES_LOG.xlsx.
With `pack`, record the AI Studio answer the same way.

**Comments, TikTok and Facebook, every project (Richie's rule, 06/11/2026):** the ads run on Meta, and Facebook's buyers
don't talk like TikTok's, so the avatars rest on both. TikTok with `S/browser/tiktok_comments.js`; Facebook with
`S/browser/fb_comments.js` on posts that carry the market's comments: the client's own ads (Ads Manager → the ad →
« Afficher la publication avec les commentaires »), the competitors' ads reposted on their Page (Reels or Vidéos), or
the posts of the subject's groups. Facebook's search pages refuse the browser extension (tested 06/11/2026): open a post
by its link. At least 40 Facebook comments on 2 posts or more before the avatars (check `refs_fb_comments`), in the
user's Chrome. Both go
through COPIER and `research.py paste`. When a script reads nothing, screenshots of the comments do the job. This
gives buying intent, the objections by type, and the customers' words in library/voice. Then run `research.py hooks <dossier>`: what every reference says in its first seconds.
Group those openings by angle before the strategy.

## 5. Close

Run `research.py status` for the checks and `research.py log` for REFERENCES_LOG.xlsx. Then
`research.py report <dossier> --done` writes deliverables/RECHERCHE.md.

Hand over to cs-strategy: the avatars and the system of ten creatives, built on these references, the
customers' words and the competitors' pages.

## House rules

- **Proof over taste.** A reference is kept for what it proves (months of spend, versions, plays,
  comments that ask to buy), never because it looks nice. Write the reason in `--why`.
- **Word for word.** Only Whisper transcripts are a script source. Correct the misheard words of the ones you
  copy. A reference watched online (no file) is analysed and can inspire a format, but its words are copied only
  from what you heard and wrote down.
- **Same format.** Each creative will start from a reference of its own format: keep images, carousels,
  talking heads, voice-overs, demos and objection replies in the mix.
- **Read-only.** Searches and comments are what any visitor sees, or what the user's own logged-in Chrome shows
  them (Instagram, Facebook comments). Never like, follow, comment or post; no accounts created; no private data.
- **One step per session if needed:** every command writes to the workspace; a cut loses nothing.
- **Open by default:** no legal or risk sections; a 🔴 is information, not a barrier.

## Files

| File | What |
|---|---|
| `references/search.md` | The plan, the browser and Apify routes, what to keep and why |
| `references/pipeline.md` | Download, transcribe, look, frames, analyse, buying intent, with the traps met so far |
| `references/apify.md` | Setting up Apify, what it sends, costs, failures |
| `scripts/research.py` | plan, discover, paste, import, rank, pick, reject, download, transcribe, sheet, frames, analyse, intent, hooks, check, status, log, report |
| `scripts/checks.yaml` | The research checks (count, mix, images, long-running ads, files, transcripts, skeletons, intent, voice) |
| `scripts/browser/tiktok_capture.js`, `tiktok_comments.js` | TikTok search results with their numbers; comments |
| `scripts/browser/instagram_capture.js`, `fb_comments.js` | Instagram posts and reels with their numbers (field-tested logged in, 31/10/2026); Facebook comments (user's Chrome, read-only; field-tested 02/11/2026: two real clicks on the sort menu first, « Plus pertinents » then « Tous les commentaires ») |
| `CS/browser/adlib_links.js` | Ad Library: every ad, start date, versions, format, landing page |
| `scripts/browser/adlib_batch.js` | Many Ad Library searches in a row: reader kept in IndexedDB, one line per search, one COPIER per ten (tested 01/11/2026: 83 searches, 909 ads) |
| `templates/analyse_prompt.md` | The reverse-engineering prompt (7 parts) for the skeletons |
| `tests/test_research.py` | Acceptance tests: `python tests/test_research.py` |
