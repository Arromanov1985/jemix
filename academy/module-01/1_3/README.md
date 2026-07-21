# Озвучка JEMIX Academy 1.3 через Yandex SpeechKit

## 1. Откройте папку в VS Code

Поместите рядом:

- `yandex_tts_lesson_1_3.py`
- `voice_texts_1_3.json`
- `JEMIX_Academy_Lesson_1_3_SCORM_UXv2_FINAL_EXACT.zip`

## 2. Установите библиотеку

```powershell
py -m pip install -r requirements.txt
```

## 3. Передайте ключ только через переменную окружения

PowerShell, только для текущего окна:

```powershell
$env:YANDEX_API_KEY="ВАШ_API_КЛЮЧ"
```

## 4. Запустите генерацию

```powershell
py .\yandex_tts_lesson_1_3.py `
  --scorm ".\JEMIX_Academy_Lesson_1_3_SCORM_UXv2_FINAL_EXACT.zip" `
  --texts ".\voice_texts_1_3.json" `
  --voice ermil `
  --emotion good `
  --speed 1.0 `
  --overwrite
```

Результат:

`JEMIX_Academy_Lesson_1_3_SCORM_UXv2_FINAL_EXACT_WITH_YANDEX_VOICE.zip`

## Пробная генерация одного экрана

```powershell
py .\yandex_tts_lesson_1_3.py `
  --scorm ".\JEMIX_Academy_Lesson_1_3_SCORM_UXv2_FINAL_EXACT.zip" `
  --only 1 `
  --voice ermil `
  --emotion good `
  --speed 1.0 `
  --overwrite
```
