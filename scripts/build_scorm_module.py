#!/usr/bin/env python3
"""Build a full SCORM 1.2 module for JEMIX Academy.

Usage:
  python scripts/build_scorm_module.py module-01

Output:
  dist/module-01/JEMIX_Module_01_SCORM.zip
"""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

MODULE = sys.argv[1] if len(sys.argv) > 1 else "module-01"
ROOT = Path(".")
WORK = ROOT / "_scorm_module_build" / MODULE
DIST = ROOT / "dist" / MODULE
OUT = DIST / "JEMIX_Module_01_SCORM.zip"

LESSONS = [
    ("lesson-1.1", "Что такое насос"),
    ("lesson-1.2", "Где применяются насосы"),
    ("lesson-1.3", "Как устроен насос"),
    ("lesson-1.4", "Как определить тип насоса"),
    ("lesson-1.5", "Ассортимент JEMIX"),
    ("lesson-1.6", "Практический экзамен"),
]


def clean_md(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = text.replace("**", "")
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("▶", "").replace("→", "-")
    return text.strip()


def compact(text: str, max_sentences: int = 3) -> str:
    text = " ".join(x.strip() for x in text.splitlines() if x.strip())
    parts = re.split(r"(?<=[.!?])\s+", text)
    parts = [p for p in parts if p]
    return " ".join(parts[:max_sentences]) or "Материал слайда."


def read_slide(lesson: str, n: int) -> tuple[str, str]:
    p = ROOT / "voice" / "modules" / MODULE / lesson / f"slide{n:02d}.md"
    if not p.exists():
        return f"Слайд {n}", "Материал будет добавлен после финальной редакции."
    lines = p.read_text(encoding="utf-8").splitlines()
    title = clean_md(lines[0]) if lines else f"Слайд {n}"
    body = compact(clean_md("\n".join(lines[1:])))
    return title, body


def copy_audio(lesson: str, n: int) -> str:
    src = ROOT / "voice" / "modules" / MODULE / lesson / "audio" / f"slide{n:02d}.mp3"
    if not src.exists():
        return ""
    dst_dir = WORK / "audio" / lesson
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst_dir / src.name)
    return f"audio/{lesson}/{src.name}"


def build_course_data() -> dict:
    screens = []
    for lesson_idx, (lesson, lesson_title) in enumerate(LESSONS, start=1):
        for n in range(1, 4):
            title, body = read_slide(lesson, n)
            screens.append({
                "type": "lesson",
                "lesson": f"1.{lesson_idx}",
                "lessonTitle": lesson_title,
                "title": title,
                "body": body,
                "audio": copy_audio(lesson, n),
                "note": "Сначала определяем задачу клиента, затем группу оборудования и только потом модель JEMIX."
            })
        screens.append({
            "type": "quiz",
            "lesson": f"1.{lesson_idx}",
            "lessonTitle": lesson_title,
            "title": "Проверка понимания",
            "question": "С чего начинается правильный подбор насоса?",
            "answers": [
                {"text": "С задачи клиента", "correct": True},
                {"text": "С самой мощной модели", "correct": False},
                {"text": "С цены", "correct": False},
                {"text": "С цвета корпуса", "correct": False},
            ]
        })
    return {
        "module": "Модуль 1. Основы насосной техники",
        "brand": "JEMIX Academy",
        "screens": screens
    }


def write_manifest() -> None:
    manifest = """<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_MODULE_01_SCORM" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="ORG1">
    <organization identifier="ORG1">
      <title>JEMIX Academy Module 1</title>
      <item identifier="ITEM1" identifierref="RES1">
        <title>Module 1</title>
      </item>
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html" />
      <file href="style.css" />
      <file href="app.js" />
      <file href="scorm.js" />
      <file href="course-data.js" />
    </resource>
  </resources>
</manifest>
"""
    (WORK / "imsmanifest.xml").write_text(manifest, encoding="utf-8")


def write_index() -> None:
    (WORK / "index.html").write_text("""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>JEMIX Academy Module 1</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <main id="app"></main>
  <script src="scorm.js"></script>
  <script src="course-data.js"></script>
  <script src="app.js"></script>
</body>
</html>
""", encoding="utf-8")


def write_scorm_js() -> None:
    (WORK / "scorm.js").write_text(r"""
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
  } catch (e) { return false; }
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
  try { API.LMSCommit(""); API.LMSFinish(""); } catch (e) {}
}
window.addEventListener("load", scormInit);
window.addEventListener("beforeunload", scormFinish);
""".strip() + "\n", encoding="utf-8")


def write_app_js() -> None:
    (WORK / "app.js").write_text(r"""
var current = -1;
var score = 0;
var answered = {};
var app = document.getElementById('app');

function esc(s) {
  return String(s || '').replace(/[&<>"']/g, function(c) {
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];
  });
}

function progressPercent() {
  if (current < 0) return 0;
  return Math.round(((current + 1) / COURSE.screens.length) * 100);
}

function commit(status) {
  var p = progressPercent();
  scormSetProgress(status === 'completed' ? 100 : p, status || (p >= 100 ? 'completed' : 'incomplete'));
}

function startCourse() { current = 0; render(); commit('incomplete'); }
function next() { if (current < COURSE.screens.length - 1) { current++; render(); commit('incomplete'); } else { renderComplete(); } }
function prev() { if (current > 0) { current--; render(); commit('incomplete'); } }

function renderShell(inner) {
  var p = progressPercent();
  app.innerHTML = '<div class="layout">' +
    '<aside class="side"><div class="brand">JEMIX</div><div class="academy">Academy</div><div class="module">' + esc(COURSE.module) + '</div><div class="meter"><span style="width:' + p + '%"></span></div><div class="percent">' + p + '%</div></aside>' +
    '<section class="stage">' + inner + '</section>' +
  '</div>';
}

function renderCover() {
  app.innerHTML = '<section class="cover"><div class="cover-card"><div class="badge">SCORM 1.2</div><h1>JEMIX Academy</h1><h2>Модуль 1. Основы насосной техники</h2><p>Короткие экраны, озвучка, мини-тесты и фиксация прогресса в Бруснике.</p><button onclick="startCourse()">Начать обучение</button></div></section>';
}

function renderLesson(s) {
  var audio = s.audio ? '<div class="audio"><div>Прослушать объяснение</div><audio controls src="' + esc(s.audio) + '"></audio></div>' : '';
  renderShell('<div class="top"><button onclick="prev()">Назад</button><span>' + esc(s.lesson) + ' - ' + esc(s.lessonTitle) + '</span></div><article class="card lesson"><div class="label">Учебный экран</div><h1>' + esc(s.title) + '</h1><p class="lead">' + esc(s.body) + '</p><div class="scheme"><span>Источник</span><b>-</b><span class="pump">Насос</span><b>-</b><span>Потребитель</span></div><div class="note"><strong>Запомните:</strong> ' + esc(s.note) + '</div>' + audio + '<button class="primary" onclick="next()">Далее</button></article>');
}

function renderQuiz(s) {
  var buttons = s.answers.map(function(a, i) { return '<button class="answer" onclick="answer(' + i + ')">' + esc(a.text) + '</button>'; }).join('');
  renderShell('<div class="top"><button onclick="prev()">Назад</button><span>' + esc(s.lesson) + ' - проверка</span></div><article class="card quiz"><div class="label">Мини-тест</div><h1>' + esc(s.question) + '</h1><div class="answers">' + buttons + '</div><div id="feedback"></div></article>');
}

function answer(i) {
  var s = COURSE.screens[current];
  var fb = document.getElementById('feedback');
  if (s.answers[i].correct) {
    if (!answered[current]) { score += 1; answered[current] = true; }
    fb.innerHTML = '<div class="ok">Верно. Можно идти дальше.</div><button class="primary" onclick="next()">Далее</button>';
  } else {
    fb.innerHTML = '<div class="bad">Неверно. Вернитесь к материалу выше и попробуйте еще раз.</div>';
  }
  commit('incomplete');
}

function renderComplete() {
  commit('completed');
  app.innerHTML = '<section class="cover"><div class="cover-card"><div class="badge">Завершено</div><h1>Модуль пройден</h1><h2>JEMIX Academy</h2><p>Результат передан в Бруснику. Можно закрыть урок или перейти к следующему модулю.</p><button onclick="scormFinish()">Завершить</button></div></section>';
}

function render() {
  if (current < 0) return renderCover();
  var s = COURSE.screens[current];
  if (s.type === 'quiz') return renderQuiz(s);
  return renderLesson(s);
}

window.addEventListener('load', renderCover);
""".strip() + "\n", encoding="utf-8")


def write_css() -> None:
    (WORK / "style.css").write_text(r"""
:root { --blue:#005bbb; --blue2:#0080ff; --red:#e30613; --ink:#111827; --muted:#6b7280; --bg:#eef5ff; }
*{box-sizing:border-box} body{margin:0;font-family:Arial,sans-serif;background:var(--bg);color:var(--ink)} button{font-family:inherit}.cover{min-height:100vh;padding:24px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#004a99,#0080ff)}.cover-card{width:min(980px,100%);border-radius:30px;padding:50px;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.30);color:#fff;box-shadow:0 20px 60px rgba(0,0,0,.22)}.badge{display:inline-block;background:var(--red);border-radius:999px;padding:8px 14px;font-weight:900;margin-bottom:20px}.cover h1{font-size:clamp(46px,8vw,86px);line-height:1;margin:0 0 16px}.cover h2{font-size:clamp(26px,4vw,46px);margin:0 0 18px}.cover p{font-size:22px;line-height:1.45;max-width:780px}.cover button,.primary{border:0;background:var(--red);color:#fff;border-radius:16px;padding:16px 26px;font-size:18px;font-weight:900;cursor:pointer;margin-top:20px}.layout{min-height:100vh;display:grid;grid-template-columns:280px 1fr}.side{background:#071c3a;color:#fff;padding:26px;display:flex;flex-direction:column;gap:10px}.brand{font-size:42px;font-weight:950;letter-spacing:.5px}.academy{font-size:24px;font-weight:800;color:#9ccaff}.module{margin-top:20px;color:#dbeafe;line-height:1.4}.meter{height:12px;background:rgba(255,255,255,.18);border-radius:999px;overflow:hidden;margin-top:24px}.meter span{display:block;height:100%;background:var(--red)}.percent{font-size:24px;font-weight:900}.stage{padding:28px}.top{max-width:1100px;margin:0 auto 18px;display:flex;justify-content:space-between;align-items:center;color:var(--muted);font-weight:900}.top button{border:1px solid #cbd5e1;background:#fff;border-radius:12px;padding:10px 14px;cursor:pointer}.card{max-width:1100px;margin:0 auto;background:#fff;border-radius:30px;border:1px solid #dbeafe;padding:36px;box-shadow:0 18px 46px rgba(15,23,42,.10)}.label{display:inline-block;background:var(--red);color:#fff;border-radius:999px;padding:8px 14px;font-weight:900;margin-bottom:18px}.card h1{font-size:clamp(34px,5vw,58px);line-height:1.12;margin:0 0 18px}.lead{font-size:25px;line-height:1.5;color:#374151}.scheme{margin:28px 0;display:flex;gap:14px;align-items:center;flex-wrap:wrap}.scheme span{background:#eff6ff;border:2px solid #bfdbfe;border-radius:18px;padding:18px 22px;font-size:20px;font-weight:900}.scheme .pump{background:#fff7ed;border-color:#fecaca}.scheme b{font-size:28px;color:var(--blue)}.note,.audio{margin-top:20px;padding:18px;border-radius:16px;font-size:20px;line-height:1.45}.note{background:#fff7ed;border-left:6px solid var(--red)}.audio{background:#eff6ff;border-left:6px solid var(--blue2);font-weight:800}.audio audio{width:100%;margin-top:10px}.answers{display:grid;gap:12px}.answer{display:block;width:100%;text-align:left;padding:18px 20px;border:2px solid #dbeafe;border-radius:16px;background:#f8fbff;font-size:21px;cursor:pointer}.answer:hover{border-color:var(--blue2)}.ok,.bad{margin-top:18px;padding:16px;border-radius:14px;font-size:20px;font-weight:900}.ok{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}@media(max-width:820px){.layout{grid-template-columns:1fr}.side{position:relative}.stage{padding:14px}.card{padding:24px}.cover-card{padding:30px}.scheme{display:block}.scheme span,.scheme b{display:block;margin:10px 0;text-align:center}}
""".strip() + "\n", encoding="utf-8")


def write_course_data(data: dict) -> None:
    text = "var COURSE = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    (WORK / "course-data.js").write_text(text, encoding="utf-8")


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
    data = build_course_data()
    write_manifest()
    write_index()
    write_scorm_js()
    write_app_js()
    write_css()
    write_course_data(data)
    zip_dir()
    print(f"OK: {OUT}")
    print(f"Screens: {len(data['screens'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
