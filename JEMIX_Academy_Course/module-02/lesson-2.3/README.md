# JEMIX Academy — урок 2.2: аудио

Пакет содержит тексты и SSML для 20 слайдов урока «Расчёт расхода и напора».

## Рекомендуемые настройки
- Голос: `ermil`
- Эмоция: `good`
- Скорость: `1.0`
- Формат: MP3

## Запуск в PowerShell
1. Скопируйте `.env.example` в `.env`.
2. Вставьте `YANDEX_API_KEY` и `YANDEX_FOLDER_ID`.
3. Откройте PowerShell в папке проекта.
4. Выполните:

```powershell
.\run_yandex_audio.ps1
```

Готовые файлы появятся в папке `audio` с именами `slide01.mp3` — `slide20.mp3`.

Для одного слайда:

```powershell
python .\generate_yandex_audio.py --slide 7 --voice ermil --emotion good --speed 1.0 --overwrite
```
