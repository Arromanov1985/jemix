#!/usr/bin/env python3
"""Build JEMIX Academy lesson 3.4 as a standalone SCORM 1.2 package."""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "_scorm_lesson_3_4"
DIST = ROOT / "dist" / "module-03"
OUT = DIST / "JEMIX_Lesson_3_4_SCORM.zip"
AUDIO = ROOT / "voice" / "modules" / "module-03" / "lesson-3.4" / "audio"

SLIDES = [
    ("Скважинные насосы", "Как подобрать насос по параметрам скважины и требуемой рабочей точке."),
    ("Что нужно понять", "Скважинный насос выбирают по диаметру, уровням воды, глубине установки, расходу и напору."),
    ("Задача", "Насос должен подать воду из скважины с нужным расходом и давлением, не выходя за допустимые режимы работы."),
    ("Карта выбора", "Диаметр скважины → статический и динамический уровни → глубина установки → расход → полный напор → автоматика и защита."),
    ("Вопросы продавца", "Каков внутренний диаметр обсадной трубы? Где статический и динамический уровни? На какой глубине будет насос? Какой расход нужен?"),
    ("Практический кейс", "Для дома со скважиной нельзя выбирать модель только по глубине. Нужно учитывать динамический уровень, потери в трассе, высоту подъёма и требуемое давление."),
    ("Как это звучит", "Чтобы подобрать скважинный насос, уточню диаметр скважины, уровни воды, глубину установки, расстояние до дома и количество точек потребления."),
    ("Ошибка в подборе", "Неверно: брать насос с максимальным напором про запас. Верно: подобрать рабочую точку в допустимой зоне характеристики."),
    ("Красные флаги", "Нет данных о динамическом уровне, дебите или диаметре скважины — подбор необходимо остановить и запросить параметры."),
    ("Быстрая проверка", "Ключевые данные: диаметр, уровни воды, глубина установки, расход, полный напор и защита от сухого хода."),
    ("Квиз", "Что важнее всего уточнить? Правильный ответ: диаметр, уровень воды и глубину установки."),
    ("Итоги урока", "Скважинный насос выбирается по параметрам источника и рабочей точке системы, а не по одному значению мощности или напора."),
]

SCORM_JS = r'''let api=null;
function findAPI(w){for(let i=0;i<20&&w;i++,w=w.parent){if(w.API)return w.API}return null}
function init(){api=findAPI(window)||findAPI(window.opener);if(api){api.LMSInitialize("");const v=api.LMSGetValue("cmi.core.lesson_location");return Number(v)||0}return Number(localStorage.getItem("jemix-3.4-slide"))||0}
function save(i,done=false){if(api){api.LMSSetValue("cmi.core.lesson_location",String(i));api.LMSSetValue("cmi.core.lesson_status",done?"completed":"incomplete");api.LMSCommit("")}else localStorage.setItem("jemix-3.4-slide",String(i))}
window.addEventListener("beforeunload",()=>{if(api)api.LMSFinish("")});'''

STYLE = '''body{margin:0;font-family:"PT Sans",Arial,sans-serif;background:#f3f6f9;color:#17202a}.app{max-width:1100px;margin:auto;min-height:100vh;background:white;display:flex;flex-direction:column}.top{padding:18px 28px;background:#0b4f87;color:white}.bar{height:6px;background:#dce7f0}.bar span{display:block;height:100%;background:#f08a24}.screen{flex:1;padding:48px 60px}.screen h1{font-size:38px;margin:0 0 24px}.screen p{font-size:23px;line-height:1.45}.nav{display:flex;justify-content:space-between;padding:22px 28px;border-top:1px solid #dce3ea}button{border:0;border-radius:8px;padding:13px 24px;font-size:17px;cursor:pointer}.primary{background:#0b4f87;color:white}.audio{margin-top:30px;width:100%}.meta{opacity:.8}'''

INDEX = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX 3.4</title><link rel="stylesheet" href="style.css"></head><body><div class="app"><div class="top"><b>JEMIX Academy</b> · Модуль 3 · Урок 3.4</div><div class="bar"><span id="progress"></span></div><main class="screen"><div class="meta" id="meta"></div><h1 id="title"></h1><p id="text"></p><audio id="audio" class="audio" controls></audio></main><div class="nav"><button id="prev">Назад</button><button id="next" class="primary">Далее</button></div></div><script src="scorm.js"></script><script src="app.js"></script></body></html>'''

APP_TEMPLATE = '''const slides=__SLIDES__;let current=Math.max(0,Math.min(init(),slides.length-1));
const title=document.getElementById("title"),text=document.getElementById("text"),meta=document.getElementById("meta"),progress=document.getElementById("progress"),audio=document.getElementById("audio");
function render(){const s=slides[current];title.textContent=s[0];text.textContent=s[1];meta.textContent=`Экран ${current+1} из ${slides.length}`;progress.style.width=`${(current+1)/slides.length*100}%`;document.getElementById("prev").disabled=current===0;document.getElementById("next").textContent=current===slides.length-1?"Завершить":"Далее";audio.src=`audio/slide${String(current+1).padStart(2,"0")}.mp3`;save(current,current===slides.length-1)}
document.getElementById("prev").onclick=()=>{if(current>0){current--;render()}};document.getElementById("next").onclick=()=>{if(current<slides.length-1){current++;render()}else save(current,true)};render();'''

MANIFEST = '''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_3_4" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata><organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Academy 3.4</title><item identifier="ITEM1" identifierref="RES1"><title>Скважинные насосы</title></item></organization></organizations><resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html"><file href="index.html"/><file href="style.css"/><file href="app.js"/><file href="scorm.js"/></resource></resources></manifest>'''


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    (WORK / "audio").mkdir(parents=True)
    (WORK / "index.html").write_text(INDEX, encoding="utf-8")
    (WORK / "style.css").write_text(STYLE, encoding="utf-8")
    (WORK / "scorm.js").write_text(SCORM_JS, encoding="utf-8")
    (WORK / "app.js").write_text(APP_TEMPLATE.replace("__SLIDES__", json.dumps(SLIDES, ensure_ascii=False)), encoding="utf-8")
    (WORK / "imsmanifest.xml").write_text(MANIFEST, encoding="utf-8")
    if AUDIO.is_dir():
        for path in AUDIO.glob("slide*.mp3"):
            shutil.copy2(path, WORK / "audio" / path.name)
    DIST.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(WORK.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(WORK).as_posix())
    print(f"OK: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
