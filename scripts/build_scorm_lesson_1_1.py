#!/usr/bin/env python3
"""Build SCORM 1.2 package for JEMIX lesson 1.1.

Usage:
  python scripts/build_scorm_lesson_1_1.py

Output:
  dist/module-01/JEMIX_Lesson_1_1_SCORM.zip
"""

from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(".")
MODULE = "module-01"
LESSON = "lesson-1.1"
WORK = ROOT / "_scorm_lesson_1_1"
DIST = ROOT / "dist" / MODULE
OUT = DIST / "JEMIX_Lesson_1_1_SCORM.zip"
SRC = ROOT / "voice" / "modules" / MODULE / LESSON


def clean(text: str) -> str:
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = text.replace("**", "")
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("▶", "")
    return " ".join(x.strip() for x in text.splitlines() if x.strip())


def read_slide(n: int) -> tuple[str, str]:
    p = SRC / f"slide{n:02d}.md"
    if not p.exists():
        defaults = {
            1: ("Что такое насос?", "Насос - это гидравлическая машина, которая передает жидкости энергию. Благодаря этому вода движется от источника к потребителю."),
            2: ("Главная задача насоса", "Насос не создает воду. Он создает условия для движения воды: расход, напор и стабильную работу системы."),
            3: ("Что важно запомнить", "Подбор насоса начинается не с мощности и не с цены. Сначала нужно понять задачу клиента, источник воды и требуемый расход."),
        }
        return defaults.get(n, (f"Экран {n}", "Материал урока."))
    lines = p.read_text(encoding="utf-8").splitlines()
    title = clean(lines[0]) if lines else f"Экран {n}"
    body = clean("\n".join(lines[1:])) or "Материал урока."
    parts = re.split(r"(?<=[.!?])\s+", body)
    return title, " ".join(parts[:3])


def copy_audio(n: int) -> str:
    src = SRC / "audio" / f"slide{n:02d}.mp3"
    if not src.exists():
        return ""
    dst_dir = WORK / "audio"
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst_dir / src.name)
    return f"audio/{src.name}"


def write_manifest() -> None:
    (WORK / "imsmanifest.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_LESSON_1_1" version="1.0"
  xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
  xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="ORG1">
    <organization identifier="ORG1">
      <title>JEMIX Lesson 1.1</title>
      <item identifier="ITEM1" identifierref="RES1"><title>Что такое насос</title></item>
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
""", encoding="utf-8")


def write_scorm_js() -> None:
    (WORK / "scorm.js").write_text(r"""
function findAPI(win){var n=0;while(win&&n<500){if(win.API)return win.API;n++;if(win.parent===win)break;win=win.parent;}return null;}
var API=findAPI(window)||(window.opener?findAPI(window.opener):null);var scormReady=false;
function scormInit(){if(!API)return false;try{scormReady=API.LMSInitialize("")==="true";if(scormReady){API.LMSSetValue("cmi.core.lesson_status","incomplete");API.LMSCommit("");}return scormReady;}catch(e){return false;}}
function scormSet(score,status){if(!API||!scormReady)return;try{API.LMSSetValue("cmi.core.score.raw",String(score));API.LMSSetValue("cmi.core.lesson_status",status);API.LMSCommit("");}catch(e){}}
function scormFinish(){if(!API||!scormReady)return;try{API.LMSCommit("");API.LMSFinish("");}catch(e){}}
window.addEventListener("load",scormInit);window.addEventListener("beforeunload",scormFinish);
""".strip() + "\n", encoding="utf-8")


def js_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def write_index_and_app() -> None:
    slides = []
    for i in range(1, 4):
        title, body = read_slide(i)
        slides.append({"title": title, "body": body, "audio": copy_audio(i)})
    data = ",\n".join(
        f"{{title:`{js_string(s['title'])}`,body:`{js_string(s['body'])}`,audio:`{s['audio']}`}}" for s in slides
    )

    (WORK / "index.html").write_text("""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JEMIX Academy - Урок 1.1</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div id="app"></div>
<script src="scorm.js"></script>
<script src="app.js"></script>
</body>
</html>
""", encoding="utf-8")

    (WORK / "app.js").write_text(f"""
const slides=[{data}];
let current=-1;
const app=document.getElementById('app');
function esc(s){{return String(s||'').replace(/[&<>\"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[c]));}}
function progress(){{return current<0?0:Math.round(((current+1)/(slides.length+1))*100);}}
function start(){{current=0;render();scormSet(15,'incomplete');}}
function next(){{if(current<slides.length-1){{current++;render();scormSet(progress(),'incomplete');}}else{{quiz();}}}}
function prev(){{if(current>0){{current--;render();}}}}
function cover(){{app.innerHTML=`<main class="cover"><section class="hero"><div class="heroText"><div class="kicker">JEMIX Academy</div><h1>Что такое насос?</h1><p>Первый урок модуля: понятное объяснение, короткие экраны и мини-проверка.</p><button onclick="start()">Начать урок</button></div><div class="product"><div class="pump"><span>JEMIX</span></div><div class="caption">Модуль 1. Основы насосной техники</div></div></section></main>`;}}
function render(){{const s=slides[current];const p=progress();app.innerHTML=`<main class="player"><aside><div class="logo">JEMIX</div><div class="academy">Academy</div><div class="module">Модуль 1<br>Основы насосной техники</div><nav><b class="active">1.1 Что такое насос</b><b>1.2 Применение</b><b>1.3 Устройство</b></nav></aside><section class="stage"><header><div><strong>Урок 1.1</strong><span>Учебный экран ${{current+1}} из ${{slides.length}}</span></div><div class="bar"><i style="width:${{p}}%"></i></div><em>${{p}}%</em></header><div class="lesson"><div class="visual"><div class="pump large"><span>JEMIX</span></div><div class="flow"><b>Источник</b><i></i><b>Насос</b><i></i><b>Дом</b></div></div><article><div class="tag">Базовое понятие</div><h1>${{esc(s.title)}}</h1><p>${{esc(s.body)}}</p><div class="tip"><strong>Запомните</strong><br>Насос не создает воду. Он передает воде энергию.</div>${{s.audio?`<div class="audio"><strong>Озвучка</strong><audio controls src="${{s.audio}}"></audio></div>`:''}}</article></div><footer><button onclick="prev()" ${{current===0?'disabled':''}}>Назад</button><button onclick="next()">Далее</button></footer></section></main>`;}}
function quiz(){{app.innerHTML=`<main class="player"><aside><div class="logo">JEMIX</div><div class="academy">Academy</div><div class="module">Проверка знания</div></aside><section class="stage"><header><div><strong>Урок 1.1</strong><span>Мини-тест</span></div><div class="bar"><i style="width:90%"></i></div><em>90%</em></header><div class="quiz"><div class="tag">Вопрос</div><h1>Что делает насос?</h1><button onclick="bad()">Очищает воду</button><button onclick="good()">Передает жидкости энергию</button><button onclick="bad()">Хранит воду</button><button onclick="bad()">Охлаждает воду</button><div id="fb"></div></div></section></main>`;}}
function good(){{document.getElementById('fb').innerHTML='<div class="ok">Верно. Урок завершен.</div>';scormSet(100,'completed');setTimeout(done,800);}}
function bad(){{document.getElementById('fb').innerHTML='<div class="bad">Неверно. Насос передает жидкости энергию.</div>';}}
function done(){{app.innerHTML=`<main class="cover"><section class="hero finish"><div class="heroText"><div class="kicker">JEMIX Academy</div><h1>Урок завершен</h1><p>Результат передан в Бруснику.</p><button onclick="scormFinish()">Завершить</button></div></section></main>`;}}
window.addEventListener('load',cover);
""", encoding="utf-8")


def write_css() -> None:
    (WORK / "style.css").write_text(r"""
:root{--red:#e30613;--black:#111;--graphite:#2b2b2b;--muted:#777;--line:#e7e7e7;--soft:#f5f5f5;--white:#fff}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:var(--white);color:var(--black)}button{font-family:inherit;border:0;cursor:pointer}.cover{min-height:100vh;background:#fff;display:flex;align-items:center;justify-content:center;padding:32px}.hero{width:min(1240px,100%);min-height:640px;display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center;border:1px solid var(--line);border-radius:34px;padding:56px;background:linear-gradient(135deg,#fff,#f6f6f6);box-shadow:0 30px 90px rgba(0,0,0,.10)}.kicker{display:inline-block;border-left:8px solid var(--red);padding-left:14px;font-size:25px;font-weight:950;text-transform:uppercase;letter-spacing:.5px}.hero h1{font-size:clamp(52px,7vw,96px);line-height:.98;margin:34px 0 20px}.hero p{font-size:24px;line-height:1.45;color:#555;max-width:620px}.hero button,.stage footer button:last-child{background:var(--red);color:#fff;border-radius:999px;padding:18px 30px;font-size:19px;font-weight:950;margin-top:24px}.product{align-self:stretch;border-radius:30px;background:#151515;display:flex;flex-direction:column;justify-content:center;padding:40px;position:relative;overflow:hidden}.product:before{content:'';position:absolute;inset:auto -80px -100px auto;width:360px;height:360px;background:var(--red);border-radius:50%;opacity:.9}.pump{height:260px;border-radius:28px;background:linear-gradient(135deg,#202020,#4a4a4a);display:flex;align-items:center;justify-content:center;position:relative;box-shadow:inset 0 0 0 1px rgba(255,255,255,.12)}.pump span{color:#fff;font-size:46px;font-weight:950;letter-spacing:2px}.pump:after{content:'';position:absolute;right:48px;bottom:42px;width:78px;height:78px;border:12px solid var(--red);border-radius:50%;background:#222}.pump.large{height:360px}.caption{color:#fff;margin-top:26px;font-size:22px;font-weight:850;position:relative}.player{min-height:100vh;display:grid;grid-template-columns:285px 1fr;background:#fafafa}aside{background:#151515;color:#fff;padding:28px;display:flex;flex-direction:column}.logo{font-size:44px;font-weight:950;letter-spacing:2px}.academy{color:#ccc;font-size:23px;font-weight:800}.module{margin:34px 0;color:#ddd;line-height:1.45;font-size:17px}nav{display:grid;gap:10px;margin-top:16px}nav b{padding:13px 14px;border-radius:14px;color:#aaa;background:rgba(255,255,255,.04)}nav b.active{background:var(--red);color:#fff}.stage{display:flex;flex-direction:column;min-width:0}header{height:86px;background:#fff;border-bottom:1px solid var(--line);display:grid;grid-template-columns:230px 1fr 70px;gap:22px;align-items:center;padding:0 28px}header strong{font-size:22px}header span{display:block;color:var(--muted);margin-top:5px}.bar{height:10px;background:#ececec;border-radius:999px;overflow:hidden}.bar i{display:block;height:100%;background:var(--red);border-radius:999px}header em{font-style:normal;font-weight:950}.lesson{width:min(1180px,calc(100% - 48px));margin:28px auto;display:grid;grid-template-columns:1.03fr .97fr;gap:28px}.visual,article,.quiz{background:#fff;border:1px solid var(--line);border-radius:30px;padding:34px;box-shadow:0 18px 55px rgba(0,0,0,.07)}.visual{display:flex;flex-direction:column;justify-content:center}.flow{display:flex;gap:12px;align-items:center;justify-content:center;margin-top:28px;flex-wrap:wrap}.flow b{background:#f1f1f1;padding:14px 16px;border-radius:14px}.flow i{width:34px;height:4px;background:var(--red);border-radius:999px}.tag{display:inline-block;background:#111;color:#fff;border-radius:999px;padding:9px 14px;font-weight:900;margin-bottom:18px}article h1,.quiz h1{font-size:clamp(34px,5vw,60px);line-height:1.08;margin:0 0 20px}article p{font-size:24px;line-height:1.5;color:#444}.tip,.audio{margin-top:20px;border-left:7px solid var(--red);background:#f6f6f6;border-radius:18px;padding:18px;font-size:20px;line-height:1.45}.audio audio{display:block;width:100%;margin-top:10px}footer{margin-top:auto;height:86px;background:#fff;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;padding:0 28px}footer button{border-radius:999px;padding:16px 25px;font-size:18px;font-weight:950}footer button:first-child{background:#eee;color:#222}button:disabled{opacity:.45;cursor:not-allowed}.quiz{width:min(900px,calc(100% - 48px));margin:48px auto}.quiz button{display:block;width:100%;text-align:left;background:#fff;border:2px solid var(--line);border-radius:18px;padding:18px 20px;margin:12px 0;font-size:21px;color:#222}.quiz button:hover{border-color:var(--red)}.ok,.bad{margin-top:18px;border-radius:16px;padding:16px;font-weight:950}.ok{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}@media(max-width:920px){.hero{grid-template-columns:1fr;padding:28px}.player{grid-template-columns:1fr}aside{display:none}header{grid-template-columns:1fr;gap:9px;height:auto;padding:18px}.lesson{grid-template-columns:1fr;width:calc(100% - 24px);margin:12px auto}.visual,article,.quiz{padding:22px;border-radius:22px}.pump.large{height:240px}.flow i{display:none}footer{height:auto;padding:16px}.hero h1{font-size:44px}}
""".strip() + "\n", encoding="utf-8")


def zip_out() -> None:
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
    write_manifest()
    write_scorm_js()
    write_index_and_app()
    write_css()
    zip_out()
    print(f"OK: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
