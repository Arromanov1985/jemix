#!/usr/bin/env python3
"""Build JEMIX Academy lesson 3.2 as a standalone SCORM 1.2 package."""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "_scorm_lesson_3_2"
DIST = ROOT / "dist" / "module-03"
OUT = DIST / "JEMIX_Lesson_3_2_SCORM.zip"
AUDIO = ROOT / "voice" / "modules" / "module-03" / "lesson-3.2" / "audio"

SLIDES = [
    ("Автоматические станции", "Как подобрать готовую насосную станцию под источник, расход и требуемый напор."),
    ("Что нужно понять", "Станция — это насос, гидроаккумулятор и автоматика, собранные в единый комплект."),
    ("Задача", "Автоматическая станция подходит для водоснабжения из неглубокого источника, повышения давления и подачи воды в дом."),
    ("Карта выбора", "Источник → глубина всасывания → расход → требуемый напор → объём гидроаккумулятора → защита."),
    ("Вопросы продавца", "Откуда берётся вода? Какова глубина до зеркала? Сколько точек потребления? Какое давление нужно в доме?"),
    ("Практический кейс", "Дом с колодцем: нужно уточнить динамический уровень, расстояние до дома, этажность и одновременный расход."),
    ("Как это звучит", "Чтобы выбрать станцию, уточню глубину всасывания, расстояние до дома, количество точек и желаемое давление."),
    ("Ошибка в подборе", "Неверно: выбирать станцию только по мощности. Верно: проверять рабочую точку, глубину всасывания и автоматику."),
    ("Красные флаги", "Если зеркало воды ниже допустимой глубины всасывания или источник нестабилен, поверхностная станция не подходит."),
    ("Быстрая проверка", "Главные параметры: источник, глубина всасывания, расход, напор и состав автоматики."),
    ("Квиз", "Что важнее всего уточнить? Правильный ответ: источник, расход, напор и автоматику."),
    ("Итоги урока", "Автоматическая станция выбирается как часть системы. Сначала проверяются условия источника и рабочая точка, затем модель."),
]

SCORM_JS = r'''let api=null;
function findAPI(w){for(let i=0;i<20&&w;i++,w=w.parent){if(w.API)return w.API}return null}
function init(){api=findAPI(window)||findAPI(window.opener);if(api){api.LMSInitialize("");const v=api.LMSGetValue("cmi.core.lesson_location");return Number(v)||0}return Number(localStorage.getItem("jemix-3.2-slide"))||0}
function save(i,done=false){if(api){api.LMSSetValue("cmi.core.lesson_location",String(i));api.LMSSetValue("cmi.core.lesson_status",done?"completed":"incomplete");api.LMSCommit("")}else localStorage.setItem("jemix-3.2-slide",String(i))}
window.addEventListener("beforeunload",()=>{if(api)api.LMSFinish("")});'''

STYLE = '''body{margin:0;font-family:"PT Sans",Arial,sans-serif;background:#f3f6f9;color:#17202a}.app{max-width:1100px;margin:auto;min-height:100vh;background:white;display:flex;flex-direction:column}.top{padding:18px 28px;background:#0b4f87;color:white}.bar{height:6px;background:#dce7f0}.bar span{display:block;height:100%;background:#f08a24}.screen{flex:1;padding:48px 60px}.screen h1{font-size:38px;margin:0 0 24px}.screen p{font-size:23px;line-height:1.45}.nav{display:flex;justify-content:space-between;padding:22px 28px;border-top:1px solid #dce3ea}button{border:0;border-radius:8px;padding:13px 24px;font-size:17px;cursor:pointer}.primary{background:#0b4f87;color:white}.audio{margin-top:30px;width:100%}.meta{opacity:.8}'''

INDEX = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX 3.2</title><link rel="stylesheet" href="style.css"></head><body><div class="app"><div class="top"><b>JEMIX Academy</b> · Модуль 3 · Урок 3.2</div><div class="bar"><span id="progress"></span></div><main class="screen"><div class="meta" id="meta"></div><h1 id="title"></h1><p id="text"></p><audio id="audio" class="audio" controls></audio></main><div class="nav"><button id="prev">Назад</button><button id="next" class="primary">Далее</button></div></div><script src="scorm.js"></script><script src="app.js"></script></body></html>'''

APP_TEMPLATE = '''const slides=__SLIDES__;let current=Math.max(0,Math.min(init(),slides.length-1));
const title=document.getElementById("title"),text=document.getElementById("text"),meta=document.getElementById("meta"),progress=document.getElementById("progress"),audio=document.getElementById("audio");
function render(){const s=slides[current];title.textContent=s[0];text.textContent=s[1];meta.textContent=`Экран ${current+1} из ${slides.length}`;progress.style.width=`${(current+1)/slides.length*100}%`;document.getElementById("prev").disabled=current===0;document.getElementById("next").textContent=current===slides.length-1?"Завершить":"Далее";audio.src=`audio/slide${String(current+1).padStart(2,"0")}.mp3`;save(current,current===slides.length-1)}
document.getElementById("prev").onclick=()=>{if(current>0){current--;render()}};document.getElementById("next").onclick=()=>{if(current<slides.length-1){current++;render()}else save(current,true)};render();'''

MANIFEST = '''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_3_2" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata><organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Academy 3.2</title><item identifier="ITEM1" identifierref="RES1"><title>Автоматические станции</title></item></organization></organizations><resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html"><file href="index.html"/><file href="style.css"/><file href="app.js"/><file href="scorm.js"/></resource></resources></manifest>'''


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
