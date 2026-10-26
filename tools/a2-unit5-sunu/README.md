# A2 unit 5 native presentation build

Sources: original 52-slide and 41-slide PowerPoints. Output: kitaplar/lise-a2/dedemin-meslegi-bana-gore-mi/sunum/.

1. Place both original PPTX files under upload/ alongside repo/. build.py reads the current attachment filenames.
2. Run build.py. It extracts source artwork, red answers, SVG checks and native p14:trim audio ranges. Original media bytes remain unchanged.
3. Convert rebuild5/part*-*.pptx to matching PDFs under rebuild5/pdf/ with LibreOffice Impress. Install Carlito and Liberation fonts; map Aptos/Calibri to Carlito and Times New Roman to Liberation Serif before rendering.
4. Prepare rebuild5/pooled-dictionary.json from the existing five-language dictionaries, with valid language ordering. pool.py recreates this input using a git-source clone. After the first render/finalize pass, run repair_dictionary.py and then finalize.py again to replace legacy language arrays using valid dictionaries and the curated overrides.
5. Install the Turkish Tesseract model as /tmp/tur.traineddata. Run render.py for lossless 2400px WebP images, word rectangles, answer markers and native-duration MP3 files.
6. Run finalize.py with extra.tsv, phrases.tsv and examples.tsv. These curated overrides supply context-specific forms, root words, translations and natural examples. Legacy shifted example arrays are replaced by valid root examples.
7. Run verify_assets.py. Decode every referenced image, check image dimensions, verify MP3 durations and all dictionary/lemma references. Test the existing UI in Chromium before release.

The unchanged unit 4 viewer supplies the approved layout, answers toggle, language panel, phrase selection, sequential lesson audio and same-language speech fallback. This unit retains a source YouTube link on slide 78.
