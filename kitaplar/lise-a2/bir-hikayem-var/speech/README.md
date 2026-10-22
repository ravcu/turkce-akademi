# A2 unit 9 vocabulary speech

Arabic vocabulary, phrases, meanings and example sentences use **Piper ar_JO-kareem-medium** recordings. Matching Arabic text reuses the unit 8 Piper corpus; other Arabic text has new local recordings. The remaining languages keep their existing audio entries. Original textbook listening recordings are separate from these vocabulary clips.

Settings: piper-tts 1.8.0, length_scale=1.08, noise_scale=0.55, noise_w_scale=0.7; Arabic Tashkeel diacritization; 22,050 Hz mono MP3, 64 kb/s, loudness normalization I=-18, TP=-1.5, LRA=9. Text after semicolons is retained. Alternatives separated by a slash are read with a pause. Shared unit 8 clips retain their approved model/settings and existing pronunciation overrides.

`index.json` maps normalized text to MP3 file/start/end. `languageEngines.ar` records voice provenance. `ar.json` maintains compatibility with the previous generator's per-language cache. `arabic-piper-manifest.json` records every original Arabic text and either its new speech input or its shared recording reference. Technical validation checks coverage, decoding and offset bounds; it does not constitute a native-speaker pronunciation review.

To reproduce, install `piper-tts==1.8.0`, `numpy`, `onnxruntime`, `ffmpeg` and `ffprobe`, then run from the repository root:

```sh
python tools/prepare_a2_unit9_piper_arabic.py --model /path/to/ar_JO-kareem-medium.onnx --work-dir /path/to/checkpoints --workers 4
```

The adjacent `.onnx.json` config is required. The generator requires unit 8's Piper index and checks the model digest. Output is staged in the work directory. Review/validate before replacing published files. No paid API, API key or runtime synthesis server is needed.

Acknowledgements:

- Voice: https://huggingface.co/rhasspy/piper-voices/tree/main/ar/ar_JO/kareem/medium
- Dataset and terms: https://github.com/AliMokhammad/arabicttstrain/
- Piper: https://github.com/OHF-Voice/piper1-gpl

No model weights are distributed in this repository.
