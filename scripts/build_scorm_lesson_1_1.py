#!/usr/bin/env python3
"""Build a focused SCORM 1.2 package for lesson 1.1.

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
            1: ("Что такое насос?", "Насос - это гидравлическая машина, которая передает жидкости энергию."),
            2: ("Главная задача насоса", "Насос помогает воде двигаться от источника к потребителю и обеспечивает нужные параметры системы."),
            3: ("Что важно запомнить", "Насос не создает воду. Он сообщает жидкости энергию и помогает ей двигаться."),
        }
        return defaults.get(n, (f"Экран {n}", "Материал урока."))
    lines = p.read_text(encoding="utf-8").splitlines()
    title = clean(lines[0]) if lines else f"Экран {n}"
    body = clean("\n".join(lines[1:])) or "Материал урока."
    # keep screens short
    parts = re.split(r"(?<=[.!?])\s+", body)
    body = " ".join(parts[:3])
    return title, body


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
""".strip()+"\n", encoding="utf-8")


def js_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")


def write_index_and_app() -> None:
    slides = []
    for i in range(1, 4):
        title, body = read_slide(i)
        audio = copy_audio(i)
        slides.append({"title": title, "body": body, "audio": audio})

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
function start(){{current=0;render();scormSet(10,'incomplete');}}
function next(){{if(current<slides.length-1){{current++;render();scormSet(Math.round(((current+1)/(slides.length+1))*100),'incomplete');}}else{{quiz();}}}}
function prev(){{if(current>0){{current--;render();}}}}
function cover(){{app.innerHTML=`<main class="cover"><section class="coverCard"><div class="brand">JEMIX Academy</div><div class="line"></div><h1>Урок 1.1<br>Что такое насос?</h1><p>Короткий первый урок: объяснение, озвучка и мини-проверка.</p><button onclick="start()">Начать урок</button></section></main>`;}}
function render(){{const s=slides[current];const p=Math.round(((current+1)/(slides.length+1))*100);app.innerHTML=`<main class="shell"><header><div><b>JEMIX Academy</b><span>Модуль 1</span></div><div class="progress"><i style="width:${{p}}%"></i></div><strong>${{p}}%</strong></header><section class="card"><div class="visual"><div class="pumpIcon"><span></span></div><div class="flow"><b>Источник</b><em></em><b>Насос</b><em></em><b>Дом</b></div></div><article><div class="tag">Учебный экран ${{current+1}} из ${{slides.length}}</div><h1>${{esc(s.title)}}</h1><p>${{esc(s.body)}}</p><div class="note"><b>Запомните:</b> насос не создает воду, а передает ей энергию.</div>${{s.audio?`<div class="audio"><b>Прослушать объяснение</b><audio controls src="${{s.audio}}"></audio></div>`:''}}</article></section><footer><button onclick="prev()" ${{current===0?'disabled':''}}>Назад</button><button onclick="next()">Далее</button></footer></main>`;}}
function quiz(){{app.innerHTML=`<main class="shell"><header><div><b>JEMIX Academy</b><span>Проверка</span></div><div class="progress"><i style="width:90%"></i></div><strong>90%</strong></header><section class="quiz"><div class="tag">Мини-тест</div><h1>Что делает насос?</h1><button onclick="bad()">Очищает воду</button><button onclick="good()">Передает жидкости энергию</button><button onclick="bad()">Хранит воду</button><button onclick="bad()">Охлаждает воду</button><div id="fb"></div></section></main>`;}}
function good(){{document.getElementById('fb').innerHTML='<div class="ok">Верно. Урок завершен.</div>';scormSet(100,'completed');setTimeout(done,900);}}
function bad(){{document.getElementById('fb').innerHTML='<div class="bad">Неверно. Насос передает жидкости энергию.</div>';}}
function done(){{app.innerHTML=`<main class="cover"><section class="coverCard"><div class="brand">JEMIX Academy</div><div class="line"></div><h1>Урок завершен</h1><p>Результат передан в Бруснику.</p><button onclick="scormFinish()">Завершить</button></section></main>`;}}
window.addEventListener('load',cover);
""", encoding="utf-8")


def write_css() -> None:
    (WORK / "style.css").write_text(r"""
:root{--red:#e30613;--black:#161616;--graphite:#2b2b2b;--light:#f5f5f5;--line:#e8e8e8}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#fff;color:var(--black)}button{font-family:inherit}.cover{min-height:100vh;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle at 80% 20%,#f2f2f2,#fff 46%,#eeeeee);padding:24px}.coverCard{width:min(980px,100%);background:#fff;border:1px solid var(--line);border-radius:28px;padding:48px;box-shadow:0 24px 80px rgba(0,0,0,.12)}.brand{font-size:38px;font-weight:950;letter-spacing:.4px}.line{height:6px;background:var(--red);width:120px;border-radius:999px;margin:18px 0 34px}.cover h1{font-size:clamp(42px,7vw,76px);line-height:1.03;margin:0 0 20px}.cover p{font-size:23px;color:#555;max-width:760px;line-height:1.45}.cover button,.shell footer button,.quiz button{border:0;border-radius:16px;padding:16px 24px;font-size:18px;font-weight:900;cursor:pointer}.cover button,.shell footer button:last-child{background:var(--red);color:white}.shell{min-height:100vh;display:flex;flex-direction:column;background:#fafafa}header{height:86px;background:#fff;border-bottom:1px solid var(--line);display:grid;grid-template-columns:260px 1fr 70px;gap:22px;align-items:center;padding:0 28px}header b{font-size:25px}header span{display:block;color:#777;margin-top:4px}.progress{height:10px;background:#eee;border-radius:999px;overflow:hidden}.progress i{display:block;height:100%;background:var(--red);border-radius:999px}.card{width:min(1180px,calc(100% - 48px));margin:28px auto;display:grid;grid-template-columns:1fr 1fr;gap:28px;align-items:stretch}.visual,article,.quiz{background:#fff;border:1px solid var(--line);border-radius:28px;padding:34px;box-shadow:0 18px 48px rgba(0,0,0,.07)}.visual{display:flex;flex-direction:column;justify-content:center;min-height:520px}.pumpIcon{height:260px;border-radius:28px;background:linear-gradient(135deg,#222,#555);position:relative;display:flex;align-items:center;justify-content:center}.pumpIcon:before{content:'JEMIX';color:#fff;font-weight:950;font-size:44px}.pumpIcon span{position:absolute;right:60px;bottom:54px;width:80px;height:80px;border:10px solid var(--red);border-radius:50%}.flow{display:flex;align-items:center;justify-content:center;gap:12px;margin-top:28px;flex-wrap:wrap}.flow b{background:#f4f4f4;border-radius:14px;padding:14px 16px}.flow em{width:34px;height:4px;background:var(--red);border-radius:999px}.tag{display:inline-block;background:var(--red);color:#fff;border-radius:999px;padding:8px 14px;font-weight:900;margin-bottom:18px}article h1,.quiz h1{font-size:clamp(34px,5vw,58px);line-height:1.08;margin:0 0 20px}article p{font-size:24px;line-height:1.5;color:#444}.note,.audio{margin-top:20px;border-left:6px solid var(--red);background:#f7f7f7;border-radius:16px;padding:18px;font-size:20px;line-height:1.45}.audio audio{width:100%;margin-top:10px}footer{margin-top:auto;height:86px;background:#fff;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;padding:0 28px}footer button:first-child{background:#eee;color:#222}button:disabled{opacity:.45;cursor:not-allowed}.quiz{width:min(900px,calc(100% - 48px));margin:44px auto}.quiz button{display:block;width:100%;text-align:left;background:#fff;border:2px solid var(--line);margin:12px 0;color:#222}.quiz button:hover{border-color:var(--red)}.ok,.bad{margin-top:16px;border-radius:14px;padding:16px;font-weight:900}.ok{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}@media(max-width:860px){header{grid-template-columns:1fr;gap:8px;height:auto;padding:18px}.card{grid-template-columns:1fr;width:calc(100% - 24px);margin:12px auto}.visual,article,.quiz{padding:22px;border-radius:20px}.visual{min-height:auto}.coverCard{padding:28px}.flow em{display:none}footer{height:auto;padding:16px}.cover h1{font-size:40px}}
""".strip()+"\n", encoding="utf-8")


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
