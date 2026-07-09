#!/usr/bin/env python3
"""Build a minimal SCORM 1.2 test lesson for Brusnika LMS.

Usage:
  python scripts/build_scorm.py module-01

Output:
  dist/module-01/JEMIX_Module_01_SCORM_TEST.zip
"""

from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

MODULE = sys.argv[1] if len(sys.argv) > 1 else "module-01"
ROOT = Path(".")
WORK = ROOT / "_scorm_build" / MODULE
DIST = ROOT / "dist" / MODULE
OUT = DIST / "JEMIX_Module_01_SCORM_TEST.zip"


def read_audio_path() -> str:
    src = ROOT / "voice" / "modules" / MODULE / "lesson-1.1" / "audio" / "slide01.mp3"
    if src.exists():
        target_dir = WORK / "audio"
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target_dir / "slide01.mp3")
        return "audio/slide01.mp3"
    return ""


def write_manifest() -> None:
    manifest = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_MODULE_01_SCORM_TEST" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="ORG1">
    <organization identifier="ORG1">
      <title>JEMIX Academy Module 1 Test</title>
      <item identifier="ITEM1" identifierref="RES1">
        <title>Test lesson</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html" />
      <file href="style.css" />
      <file href="app.js" />
      <file href="scorm.js" />
    </resource>
  </resources>
</manifest>
"""
    (WORK / "imsmanifest.xml").write_text(manifest, encoding="utf-8")


def write_scorm_js() -> None:
    js = r"""
function findAPI(win) {
  var attempts = 0;
  while (win && attempts < 500) {
    if (win.API) return win.API;
    attempts++;
    if (win.parent === win) break;
    win = win.parent;
  }
  return null;
}

var API = findAPI(window) || (window.opener ? findAPI(window.opener) : null);
var scormReady = false;

function scormInit() {
  if (!API) return false;
  try {
    scormReady = API.LMSInitialize("") === "true";
    if (scormReady) {
      API.LMSSetValue("cmi.core.lesson_status", "incomplete");
      API.LMSCommit("");
    }
    return scormReady;
  } catch (e) {
    return false;
  }
}

function scormSetProgress(score, status) {
  if (!API || !scormReady) return;
  try {
    API.LMSSetValue("cmi.core.score.raw", String(score));
    API.LMSSetValue("cmi.core.lesson_status", status);
    API.LMSCommit("");
  } catch (e) {}
}

function scormFinish() {
  if (!API || !scormReady) return;
  try {
    API.LMSCommit("");
    API.LMSFinish("");
  } catch (e) {}
}

window.addEventListener("load", scormInit);
window.addEventListener("beforeunload", scormFinish);
"""
    (WORK / "scorm.js").write_text(js.strip() + "\n", encoding="utf-8")


def write_app(audio_path: str) -> None:
    audio_html = ""
    if audio_path:
        audio_html = f'''<div class="audio"><div class="audio-title">Прослушать объяснение</div><audio controls src="{audio_path}"></audio></div>'''

    html = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>JEMIX Academy SCORM Test</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <main class="app">
    <section class="screen active" data-screen="0">
      <div class="hero">
        <div class="brand">JEMIX Academy</div>
        <div class="badge">SCORM 1.2 TEST</div>
        <h1>Модуль 1<br>Что такое насос?</h1>
        <p>Проверяем, как SCORM-пакет открывается и сохраняет прогресс в Бруснике.</p>
        <button class="primary" onclick="nextScreen()">Начать</button>
      </div>
    </section>

    <section class="screen" data-screen="1">
      <div class="topbar"><span>JEMIX Academy</span><span>Экран 1 из 3</span></div>
      <div class="card lesson">
        <div class="label">Учебный экран</div>
        <h2>Что такое насос?</h2>
        <p class="lead">Насос - это гидравлическая машина, которая передает жидкости энергию.</p>
        <div class="scheme">
          <div>Источник воды</div><div class="arrow">-</div><div class="pump">Насос</div><div class="arrow">-</div><div>Дом</div>
        </div>
        <div class="note"><strong>Запомните:</strong> насос не создает воду. Он помогает воде двигаться по системе.</div>
        {audio_html}
        <button class="primary" onclick="nextScreen()">Далее</button>
      </div>
    </section>

    <section class="screen" data-screen="2">
      <div class="topbar"><span>JEMIX Academy</span><span>Проверка</span></div>
      <div class="card quiz">
        <div class="label">Мини-тест</div>
        <h2>Что делает насос?</h2>
        <button class="answer" onclick="answer(false)">Очищает воду</button>
        <button class="answer" onclick="answer(true)">Передает жидкости энергию</button>
        <button class="answer" onclick="answer(false)">Хранит воду</button>
        <button class="answer" onclick="answer(false)">Охлаждает воду</button>
        <div id="feedback"></div>
      </div>
    </section>

    <section class="screen" data-screen="3">
      <div class="hero complete">
        <div class="brand">JEMIX Academy</div>
        <h1>Урок завершен</h1>
        <p>Тестовый SCORM-пакет успешно пройден. Результат передан в LMS.</p>
        <button class="primary" onclick="scormFinish()">Завершить</button>
      </div>
    </section>
  </main>
  <script src="scorm.js"></script>
  <script src="app.js"></script>
</body>
</html>
"""
    (WORK / "index.html").write_text(html, encoding="utf-8")

    app = r"""
var current = 0;
var screens = [];

function showScreen(i) {
  screens.forEach(function(s) { s.classList.remove('active'); });
  screens[i].classList.add('active');
  current = i;
  var progress = Math.round((i / (screens.length - 1)) * 80);
  scormSetProgress(progress, i >= 3 ? 'completed' : 'incomplete');
}

function nextScreen() {
  if (current < screens.length - 1) showScreen(current + 1);
}

function answer(correct) {
  var fb = document.getElementById('feedback');
  if (correct) {
    fb.innerHTML = '<div class="ok">Верно. Насос передает жидкости энергию.</div>';
    scormSetProgress(100, 'completed');
    setTimeout(function() { showScreen(3); }, 800);
  } else {
    fb.innerHTML = '<div class="bad">Неверно. Подумайте, что заставляет воду двигаться.</div>';
    scormSetProgress(50, 'incomplete');
  }
}

window.addEventListener('load', function() {
  screens = Array.prototype.slice.call(document.querySelectorAll('.screen'));
  showScreen(0);
});
"""
    (WORK / "app.js").write_text(app.strip() + "\n", encoding="utf-8")


def write_css() -> None:
    css = r"""
:root {
  --blue: #005bbb;
  --blue2: #0080ff;
  --red: #e30613;
  --ink: #111827;
  --muted: #6b7280;
  --bg: #eef5ff;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: var(--bg);
  color: var(--ink);
}
.app {
  min-height: 100vh;
  display: flex;
  align-items: stretch;
  justify-content: center;
}
.screen {
  display: none;
  width: 100%;
  min-height: 100vh;
  padding: 24px;
}
.screen.active { display: block; }
.hero {
  min-height: calc(100vh - 48px);
  border-radius: 28px;
  padding: 48px;
  background: linear-gradient(135deg, var(--blue), var(--blue2));
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  box-shadow: 0 18px 50px rgba(0, 70, 160, .24);
}
.brand { font-size: 34px; font-weight: 900; margin-bottom: 18px; }
.badge {
  display: inline-block;
  width: fit-content;
  background: var(--red);
  border-radius: 999px;
  padding: 8px 14px;
  font-weight: 800;
  margin-bottom: 22px;
}
h1 { font-size: clamp(42px, 7vw, 78px); line-height: 1.02; margin: 0 0 22px; }
.hero p { font-size: 22px; max-width: 760px; line-height: 1.45; }
.primary {
  appearance: none;
  border: none;
  background: var(--red);
  color: white;
  border-radius: 16px;
  padding: 16px 26px;
  font-size: 18px;
  font-weight: 800;
  cursor: pointer;
  width: fit-content;
  margin-top: 24px;
}
.topbar {
  max-width: 1080px;
  margin: 0 auto 18px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--muted);
  font-weight: 800;
}
.card {
  max-width: 1080px;
  margin: 0 auto;
  background: white;
  border: 1px solid #dbeafe;
  border-radius: 28px;
  padding: 34px;
  box-shadow: 0 18px 44px rgba(15, 23, 42, .10);
}
.label {
  display: inline-block;
  background: var(--red);
  color: white;
  border-radius: 999px;
  padding: 8px 14px;
  font-weight: 800;
  margin-bottom: 18px;
}
h2 { font-size: clamp(34px, 5vw, 58px); margin: 0 0 18px; }
.lead { font-size: 25px; line-height: 1.45; color: #374151; }
.scheme {
  margin: 28px 0;
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.scheme div {
  background: #eff6ff;
  border: 2px solid #bfdbfe;
  border-radius: 18px;
  padding: 18px 22px;
  font-size: 20px;
  font-weight: 800;
}
.scheme .pump { background: #fff7ed; border-color: #fecaca; }
.scheme .arrow { background: white; border: none; color: var(--blue); font-size: 30px; }
.note, .audio {
  margin-top: 20px;
  padding: 18px;
  background: #fff7ed;
  border-left: 6px solid var(--red);
  border-radius: 16px;
  font-size: 20px;
  line-height: 1.45;
}
.audio { background: #eff6ff; border-left-color: var(--blue2); }
.audio audio { width: 100%; margin-top: 10px; }
.answer {
  display: block;
  width: 100%;
  text-align: left;
  padding: 18px 20px;
  margin: 12px 0;
  border: 2px solid #dbeafe;
  border-radius: 16px;
  background: #f8fbff;
  font-size: 21px;
  cursor: pointer;
}
.answer:hover { border-color: var(--blue2); }
.ok, .bad {
  margin-top: 18px;
  padding: 16px;
  border-radius: 14px;
  font-size: 20px;
  font-weight: 800;
}
.ok { background: #dcfce7; color: #166534; }
.bad { background: #fee2e2; color: #991b1b; }
@media (max-width: 720px) {
  .screen { padding: 12px; }
  .hero, .card { padding: 24px; border-radius: 20px; }
}
"""
    (WORK / "style.css").write_text(css.strip() + "\n", encoding="utf-8")


def zip_dir() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in WORK.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(WORK).as_posix())


def main() -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)
    audio_path = read_audio_path()
    write_manifest()
    write_scorm_js()
    write_app(audio_path)
    write_css()
    zip_dir()
    print(f"OK: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
