# JEMIX Academy — озвучка урока 1.3 по Voice Standard

## Что делает скрипт

1. Создаёт для 21 слайда:
   - `slideXX.txt`
   - `slideXX.ssml`
   - `slideXX.md`
2. Создаёт:
   - `voice_qa.md`
   - `audio_manifest.yml`
3. Проверяет:
   - SSML/XML
   - длину предложений
   - технические символы и сокращения
   - количество акцентов
   - нейтральность тестов
   - ориентировочную длительность 30–40 секунд
4. Генерирует MP3 через Yandex SpeechKit API v1.
5. При наличии `--scorm` помещает MP3 в папку `audio/` и собирает новый ZIP.

## Установка

```powershell
py -m pip install -r requirements.txt
```

## Только подготовка сценариев и QA

```powershell
py .\prepare_and_generate_lesson_1_3_voice.py --prepare-only
```

## Проверка одного слайда

```powershell
$env:YANDEX_API_KEY="НОВЫЙ_КЛЮЧ"

py .\prepare_and_generate_lesson_1_3_voice.py `
  --only 1 `
  --voice ermil `
  --emotion good `
  --speed 0.92 `
  --overwrite
```

## Генерация всех 21 MP3 и сборка SCORM

```powershell
$env:YANDEX_API_KEY="НОВЫЙ_КЛЮЧ"

$scorm = Get-ChildItem "$HOME\Downloads","$HOME\Desktop" `
  -Filter "JEMIX_Academy_Lesson_1_3_SCORM_UXv2_FINAL_EXACT.zip" `
  -File -Recurse -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

py .\prepare_and_generate_lesson_1_3_voice.py `
  --scorm $scorm.FullName `
  --voice ermil `
  --emotion good `
  --speed 0.92 `
  --overwrite
```

## Важно

- Не добавляйте реальный API-ключ в файлы репозитория.
- После синтеза MP3 нужно прослушать.
- Слова из списка `listen carefully` в `voice_qa.md` проверяются особенно внимательно.
- Тестовые слайды озвучиваются нейтрально, без акцента на правильном ответе.
