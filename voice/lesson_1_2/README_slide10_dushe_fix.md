# Lesson 1.2 slide 10 audio fix

## Change

Slide 10 must use `дУше`, not `душе` from the word `душа`.

Corrected phrases:

- `Комфорт в дУше`
- `в кране, дУше или системе`

## Generate audio

Do not commit API keys, IAM tokens, or local credential files.

```bash
export YANDEX_API_KEY="YOUR_KEY"
export YANDEX_FOLDER_ID="YOUR_FOLDER_ID"

python voice/lesson_1_2/synthesize_slide10_yandex.py \
  --text voice/lesson_1_2/slide10_tts_text.txt \
  --out voice/lesson_1_2/slide10.mp3 \
  --audio-zip path/to/lesson-1.2-audio.zip \
  --zip-out voice/lesson_1_2/lesson-1.2-audio-corrected-slide10.zip
```

## Status

Prepared, but not SCORM ready.

The source package supplied for this fix contained only PNG slides and a separate audio ZIP. It did not contain a complete SCORM package with `index.html`, `imsmanifest.xml`, and `lesson.yml`.
