"""Prepare OpenAI speech separately; never overwrite the current live recordings.

Default: report the corpus without making paid requests.
Use --generate --max-requests N with OPENAI_API_KEY in the environment.
Review samples before a full run. Kyrgyz requires --include-kyrgyz-experimental.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import unicodedata
import urllib.error
import urllib.request

LANGUAGES = {'tr': 'Turkish', 'en': 'English', 'ru': 'Russian',
             'ky': 'Kyrgyz', 'ar': 'Arabic', 'fr': 'French'}
MODEL = 'gpt-4o-mini-tts'
VOICE = 'marin'


def clean(text):
    return re.sub(r'\s+', ' ', re.sub(r'(^|\s)[\-−–—]+(?=\s*\S)',
                  r'\1', unicodedata.normalize('NFC', str(text)))).strip()


def key(text, language):
    text = clean(text)
    if language == 'tr':
        text = text.replace('I', 'ı').replace('İ', 'i')
    return re.sub(r'^[.!?,:;…\s]+|[.!?,:;…\s]+$', '', text.lower())


def instructions(language):
    return (f'Read the input exactly in {LANGUAGES[language]}. Use clear, natural '
            'pronunciation, a warm neutral teaching tone and a slightly slow pace. '
            'Do not translate, explain, add an introduction, or omit any words. '
            'Read the complete input, including every clause after semicolons. '
            'Respect the punctuation with natural pauses.')


def duration(path):
    return float(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=nw=1:nk=1', str(path)], stderr=subprocess.DEVNULL))


def generate(text, language, token):
    payload = json.dumps({'model': MODEL, 'voice': VOICE, 'input': text,
                          'instructions': instructions(language),
                          'response_format': 'mp3'}).encode()
    request = urllib.request.Request('https://api.openai.com/v1/audio/speech',
        data=payload, headers={'Authorization': 'Bearer ' + token,
                              'Content-Type': 'application/json'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except urllib.error.HTTPError as error:
            # Do not retry authentication/billing errors or expose request headers.
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise RuntimeError(f'OpenAI Speech request failed: HTTP {error.code}') from None
            time.sleep(2 ** attempt)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--unit', type=Path, default=Path('kitaplar/lise-a2/bir-hikayem-var'))
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--max-requests', type=int, default=0,
                        help='Hard limit on new text-generation jobs; retries may add API requests.')
    parser.add_argument('--include-kyrgyz-experimental', action='store_true')
    args = parser.parse_args()
    source = json.loads((args.unit / 'speech/index.json').read_text())
    corpus = {lang: {k: k for k in source['entries'][lang]}
              for lang in LANGUAGES if lang != 'ky' or args.include_kyrgyz_experimental}
    glossary = json.loads((args.unit / 'translations.json').read_text())

    def add(lang, text):
        if lang in corpus and isinstance(text, str) and text.strip():
            k = key(text, lang)
            if k in corpus[lang]:
                corpus[lang][k] = clean(text)  # Preserve the full original sentence.

    for entry in glossary.get('examples', {}).values():
        tr, values = entry if isinstance(entry, list) else (entry['tr'], entry['values'])
        add('tr', tr)
        for lang, value in zip(['en', 'ru', 'ky', 'ar', 'fr'], values):
            add(lang, value)
    for section in ['forms', 'phrases']:
        for entry in glossary.get(section, {}).values():
            add('tr', entry.get('exampleTr'))
            add('tr', entry.get('text'))
            add('tr', entry.get('lemma'))
            for lang, value in zip(['en', 'ru', 'ky', 'ar', 'fr'], entry.get('examples', [])):
                add(lang, value)
    print(json.dumps({lang: {'texts': len(items), 'characters': sum(map(len, items.values()))}
                      for lang, items in corpus.items()}, ensure_ascii=False, indent=2))
    if not args.generate:
        return
    token = os.environ.get('OPENAI_API_KEY')
    if not token:
        raise SystemExit('OPENAI_API_KEY is not configured. Do not paste keys into chat or commit them.')
    if args.max_requests < 1:
        raise SystemExit('Set --max-requests explicitly before any paid generation.')
    output = args.unit / 'speech-openai-review'
    result = {'engine': 'OpenAI Speech API', 'model': MODEL, 'voice': VOICE,
              'kyrgyzStatus': 'experimental; native-speaker review required', 'entries': {}}
    calls = 0
    complete = True
    # Round-robin languages provides multilingual samples before a complete run.
    jobs = {lang: iter(sorted(items.items(), key=lambda item:
                (0 if ';' in item[1] or '؛' in item[1] else 1 if len(item[1]) > 40 else 2,
                 item[0]))) for lang, items in corpus.items()}
    while jobs:
        for lang in list(jobs):
            try:
                k, text = next(jobs[lang])
            except StopIteration:
                del jobs[lang]
                continue
            identity = json.dumps([MODEL, VOICE, instructions(lang), text], ensure_ascii=False)
            digest = hashlib.sha256(identity.encode()).hexdigest()
            path = output / lang / (digest + '.mp3')
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                if calls >= args.max_requests:
                    complete = False
                    continue
                if len(text) > 4096:
                    raise SystemExit('Input exceeds the API limit; split it at sentence boundaries first.')
                data = generate(text, lang, token)
                temporary = path.with_suffix('.pending.mp3')
                temporary.write_bytes(data)
                if len(data) < 500 or duration(temporary) <= .04:
                    raise RuntimeError('Invalid speech response; live files were not modified.')
                temporary.replace(path)
                calls += 1
            result['entries'].setdefault(lang, {})[k] = [path.relative_to(output).as_posix(), 0, duration(path)]
    result['complete'] = complete
    result['reviewRequired'] = True
    (output / 'review-index.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f'New generated texts: {calls}. Review output only; current speech/index.json is unchanged.')


if __name__ == '__main__':
    main()
