# Dictionary pronunciation audio

The Arabic and Kyrgyz dictionary recordings are synthetic speech generated locally. English, Russian and French recordings provide fallback pronunciation when a device has no working voice for the selected language. The site never substitutes a voice from a different language.

Source models and acknowledgements:

- Kyrgyz: Akyl-AI AkylAI-TTS, https://github.com/Akyl-AI/tts-mini (MIT code/model release). Credits: Akyl-AI, The Cramer Project, Amantur Amatov, Timur Turatali, Den Pavlov, Ulan Abdurazakov and Nursultan Bakashov. Matcha-TTS by Shivam Mehta et al.; HiFi-GAN by Jungil Kong et al.
- Arabic: Piper ar_JO-kareem-medium, https://huggingface.co/rhasspy/piper-voices/tree/main/ar/ar_JO/kareem/medium . Training dataset: https://github.com/AliMokhammad/arabicttstrain/ .
- English: Piper en_US-amy-medium, https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/amy/medium . Dataset credits: MycroftAI Mimic 3 voices.
- Russian: Piper ru_RU-ruslan-medium, https://huggingface.co/rhasspy/piper-voices/tree/main/ru/ru_RU/ruslan/medium . Dataset: RUSLAN corpus, https://ruslan-corpus.github.io/ (CC BY-NC-SA 4.0).
- French: Piper fr_FR-siwis-medium, https://huggingface.co/rhasspy/piper-voices/tree/main/fr/fr_FR/siwis/medium . Dataset: SIWIS French Speech Synthesis Database, https://datashare.is.ed.ac.uk/handle/10283/2353 (CC BY 4.0).

Piper: https://github.com/OHF-Voice/piper1-gpl . The voice model and dataset terms remain with their respective authors. No model weights are distributed in this repository; it hosts the generated educational pronunciation audio.
