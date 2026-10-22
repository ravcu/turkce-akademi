# Lise A2 · 1. Ünite · Tatil Dönüşü — Sunu Modu

The two teacher-provided PowerPoint parts contain 186 source slides. This reader preserves source order and includes 107 slides after removing the Turkish–English vocabulary lists, supplementary English grammar/translation pages, and the English explanation textbox on part 2 slide 79.

## Reader

- A1 Tanışalım presentation CSS and layout retained, including navigation, thumbnails, dictionary panel and fullscreen entry from PDF mode.
- 5267 clickable text rectangles; 1682 distinct word/form keys; five-language meanings and natural examples (EN/RU/KY/AR/FR).
- Compounds and cultural place names select together; proper names and common homonyms are distinguished by context.
- 59 answer layers reproduce native PowerPoint answer positions and colours. Red text, circles, SVG ticks and the additional blue answer connectors on source part 2 slide 16 are hidden until requested. Printed example lines remain visible.
- 35 original listening excerpts extracted from embedded PowerPoint audio. CT_MediaTrim.st and .end are durations removed from the beginning and end, respectively: excerpt end = source duration minus trimEnd. Original trim boundaries are retained.
- Slide changes stop playback. Unit 1 has no previous unit; the next presentation remains disabled until unit 2 is supplied.

## Speech

Local recorded pronunciation uses existing matching A2 recordings plus eSpeak NG synthesis for TR/EN/RU/KY/FR. Arabic uses Piper ar_JO-kareem-medium with Tashkeel and matching reviewed Piper recordings from completed A2 units. No translation service or external TTS API was called. Model SHA256: 9e95cab07b679da603bba17c4dec7ab3111320571964ee95c0379603c086491e.

The speech index references 271 local packs and 790 existing shared packs; the 35 lesson excerpts are separate. Local pack duration ranges are verified, and shared paths are checked against the repository tree. A truncated Kyrgyz pack was rebuilt before publication.

## Validation and source limits

`tests/verify-lise-a2-unit1-sunum.cjs` executes the actual phrase selection, dictionary rendering, answer toggling and audio-stop code in a DOM harness, checks every selection in five languages, and verifies the speech entry for each rendered audio button. `verification.json` records the result.

All slide images and answer layers were inspected in contact sheets, with detailed checks of answer placement. No installed browser was available for a full browser screenshot/playback test. Recordings were technically checked; every utterance was not individually listened to.

No embedded video exists in either supplied PowerPoint part. The Evliya Çelebi video activity is preserved but its video is not fabricated or replaced with unrelated media.

The tools under `tools/a2-unit1-sunu/` retain extraction, rendering, lexical editorial tables and speech preparation. Set A2_SUNU_WORK to the intermediate work directory and A2_SUNU_REPO to the repository root. Run postprocess.py after reader.py to apply the final contextual and proper-name corrections.
