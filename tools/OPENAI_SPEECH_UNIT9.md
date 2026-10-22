# OpenAI speech transition — A2 unit 9

Status: preparation only. No new OpenAI audio has been generated or published.

The review generator uses OpenAI's `gpt-4o-mini-tts` model and `marin` voice.
It preserves complete example sentences, including text after semicolons.
It stores new recordings separately and does not reuse eSpeak recordings or
replace the live speech index. All generation requires an API key in the
environment and an explicit maximum number of new audio texts. API requests
can incur charges; retries may add requests. Start with a small review sample.

1. Add `OPENAI_API_KEY` in the repository's **Settings → Secrets and variables → Actions**.
   Never put it in the repository, a web page, or a chat message.
2. Open **Actions → Preview A2 unit 9 OpenAI speech → Run workflow**.
   The default limit is five new texts: one sample per officially listed target language.
   Including Kyrgyz requires the experimental option; set the limit to six for six samples.
3. Listen to the downloaded `unit9-openai-marin-review` artifact. Check completeness,
   language, pronunciation, pace and naturalness before a full generation run.
4. Only after full generation and language review should the site's speech index
   be replaced. This workflow has read-only repository permissions and never
   changes the live site. Disclose AI-generated speech in the playback interface
   when publishing the new recordings.

Kyrgyz is not on the documented supported-language list. Do not substitute Kazakh,
and do not claim native-quality Kyrgyz without a speaker's assessment.

Official reference: https://developers.openai.com/api/docs/guides/text-to-speech
