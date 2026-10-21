# Unit 6 pronunciation

These files contain synthetic educational pronunciation, not the original textbook listening/video recordings.

- Turkish: Piper tr_TR-dfki-medium (model information: https://huggingface.co/rhasspy/piper-voices/tree/main/tr/tr_TR/dfki/medium).
- English: Piper en_US-amy-medium.
- Russian: Piper ru_RU-ruslan-medium; RUSLAN corpus (CC BY-NC-SA 4.0).
- Arabic: Piper ar_JO-kareem-medium.
- French: Piper fr_FR-siwis-medium; SIWIS database (CC BY 4.0).
- Kyrgyz: eSpeak NG Kyrgyz, plus reused Akyl-AI recordings where an exact shared entry exists.

Piper: https://github.com/OHF-Voice/piper1-gpl . Voices and model cards: https://huggingface.co/rhasspy/piper-voices . eSpeak NG: https://github.com/espeak-ng/espeak-ng (GPL-3.0-or-later). Shared audio credits: ../../../../assets/speech-20261013/README.md . No voice model weights are redistributed here.

`index.json` maps each exact, normalized displayed text to its language-specific recording and time interval. The generation job validates non-silent PCM and interval lengths before publishing the index. No translation service or external speech endpoint is called by the reader.
