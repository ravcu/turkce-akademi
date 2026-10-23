# Lise A2 · 2. Ünite · Hafta Sonu Planın Ne?

Reader keeps the A1 design. Both uploaded original PowerPoint parts are the authoritative source. 171 source slides minus 67 vocabulary-list slides produce 104 slides in the original sequence.

## Image fidelity and answers

`native-v2/slides/` contains clean 2400×1350 lossless WebP renders. The clean deck removes only native red DrawingML answer shapes and connectors. No picture is retouched, inpainted or recolored. All original PPTX media bytes are preserved in the conversion copies.

`native-v2/answers/` contains the corresponding 53 answer-page renders. The answer switch overlays the original answer page. The 335 source answer shapes are recorded in `native-source-audit.json`. A pixel comparison of all 53 page pairs shows zero changed pixels outside padded answer object bounds.

The 26 media icons and two added English tables are removed as native objects. The original single picture on slide 78 includes English labels; CSS hides those labels without editing the picture. The deprecated `slides/` images from the earlier destructive cleanup are not used.

## Audio and video

25 audio cuts on 24 slides come from the originals. Their boundaries follow native `p14:trim`: the start is the stored start trim, and the end is the original media duration minus the stored end trim. These durations also match the native playback animation durations. Files with different cuts are exported separately so each page starts at its proper point. The two clips on slide 37 play sequentially.

The embedded MP4 on slide 26 is retained as a video with its own player. `native-audio-audit.json` contains exact offsets and source media hashes.

## Dictionary

`translations.json` is the active dictionary. Every clickable key has EN/RU/KY/AR/FR values. Existing contextual examples were retained and 68 additional non-generic examples recovered from earlier unit dictionaries. 323 selected keys still have no example. Some uncertain OCR fragments were intentionally not turned into dictionary entries; complete coverage of every rasterized word is not claimed.

Word speech uses the existing recorded player and matching-language browser voices when available. Missing voices report an error rather than using another language.

`release-verification.json` records current checks. Rebuild code and source object audit are in `tools/a2-unit2-sunu/`.
