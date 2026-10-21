# A2 · 7. Ünite: Akıllı Teknoloji

20 source pages (book pages 135–154), using the same reader CSS as unit 5.

- English, Russian, Kyrgyz, Arabic and French editorial vocabulary. No translation API.
- Source-PDF word rectangles, reconstructed line-end words, and grouped expressions.
- Root and inflected forms, translated examples, vocabulary notebook, mini activities and printable page vocabulary.
- Local recorded synthetic pronunciation in Turkish and the five target languages. Existing unit 6 clips are reused when the text matches; new clips use eSpeak NG.
- Static reader harness checks dictionary rendering in all five languages and all 100 page-language print exports. Rectangle centres were checked for overlapping clickable words. Browser rendering could not be run in the local runtime because browser sockets are unavailable.

## Pending source material

Original S.046–S.049 listening recordings and V.008 video are not present. Their media controls remain disabled. These are distinct from the generated vocabulary pronunciation clips.

Reading answers and sample open-ended responses are provided. Media-dependent answers, some visual matching answers, and the complete six-error visual correction on page 18 still need the relevant source validation. No unverified answer overlays are placed over the book.

Unit 8 is not prepared yet; the next-unit control is disabled. The previous-unit link opens unit 6.

## Rebuild

Run tools/prepare_a2_unit7.py with the uploaded source PDF available at the documented scratch input, then run it with --build. The local editorial TSV files in tools/unit7-*.tsv are authoritative overrides. Legacy arrays with Turkish-first ordering are excluded from the five-language importer. Run node tests/verify-lise-a2-unit7.cjs for the static reader harness. Speech rebuilding uses tools/prepare_a2_unit7_speech.py and a local eSpeak NG runtime.
