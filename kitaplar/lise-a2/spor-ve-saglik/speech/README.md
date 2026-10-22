# A2 unit 8 vocabulary speech

Arabic vocabulary, phrases, inflected forms, meanings and example sentences use locally generated **Piper ar_JO-kareem-medium** audio. The player uses these recordings for Arabic on all devices. The remaining languages retain their previous recordings/device-voice behavior. These files are separate from the original textbook listening tracks.

Arabic production settings: Piper TTS 1.8.0; length_scale=1.08; noise_scale=0.55; noise_w_scale=0.7; automatic Tashkeel diacritization with reviewed overrides from `../arabic-review/samples.json`; 22,050 Hz mono MP3, 64 kb/s, loudness normalization (I=-18, TP=-1.5, LRA=9). Complete source text is retained, including text after semicolons; alternatives separated by a slash are read with a pause. Index offsets include silence around every utterance.

`index.json` maps text/language to a file and start/end offsets. Its `languageEngines.ar` records the Arabic voice and model digest. `ar.json` also stores the Arabic entries for compatibility with the earlier generation script. `arabic-piper-manifest.json` records original text, speech input and cached waveform identity for each Arabic key. No paid speech API or runtime synthesis server is used.

Reproduction from the repository root:

```sh
python -m pip install piper-tts==1.8.0 numpy onnxruntime
python tools/prepare_a2_unit8_piper_arabic.py --model /path/to/ar_JO-kareem-medium.onnx --work-dir /path/to/checkpoints
```

The voice needs its adjacent `.onnx.json` file. `ffmpeg` and `ffprobe` must be installed. Output is staged in the work directory for review and validation before publication. Check every required key, MP3 decoding, offset bounds, preserved other-language entries and full sentences before replacing published assets. Technical checks do not replace a native-speaker pronunciation review.

Model and dataset acknowledgements:

- Voice: https://huggingface.co/rhasspy/piper-voices/tree/main/ar/ar_JO/kareem/medium
- Dataset and its terms: https://github.com/AliMokhammad/arabicttstrain/
- Piper: https://github.com/OHF-Voice/piper1-gpl

No model weights are distributed in this repository. The separate `arabic-review` folder retains eight old/new sample comparisons.
