# JEMIX Academy - lesson 2.4 audio

This package generates 20 MP3 files with Yandex SpeechKit.

## Run in VS Code PowerShell

1. Extract the ZIP archive.
2. Open the extracted folder in VS Code.
3. In the terminal run:

```powershell
Copy-Item .\.env.example .\.env
notepad .\.env
```

4. Put your credentials into `.env`:

```text
YANDEX_API_KEY=your_api_key
YANDEX_FOLDER_ID=your_folder_id
```

5. Run:

```powershell
powershell -ExecutionPolicy Bypass -File .un_yandex_audio.ps1
```

Or run directly:

```powershell
python -m pip install -r .equirements.txt
python .\generate_yandex_audio.py --voice ermil --emotion good --speed 1.0 --overwrite
```

Generated files will appear in `audio`: `slide01.mp3` through `slide20.mp3`.
Voice scripts are designed for about 30-40 seconds at speed 1.0.
