#!/usr/bin/env python3
"""Build JEMIX Academy lesson 3.6.1 as a standalone SCORM 1.2 package."""
from __future__ import annotations
import json, shutil, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "_scorm_lesson_3_6_1"
DIST = ROOT / "dist" / "module-03"
OUT = DIST / "JEMIX_Lesson_3_6_1_SCORM.zip"
AUDIO = ROOT / "voice" / "modules" / "module-03" / "lesson-3.6.1" / "audio"

SLIDES = [
    ("Дренажные насосы. Основы", "Как определить, когда нужен дренажный насос и какие свойства перекачиваемой воды критичны для подбора."),
    ("Что нужно понять", "Дренажный насос выбирают прежде всего по составу воды, размеру включений, расходу, напору и условиям установки."),
    ("Задача", "Откачать чистую или загрязнённую воду из подвала, приямка, бассейна, резервуара или затопленного участка."),
    ("Карта выбора", "Среда и включения → требуемый расход → высота подъёма → длина шланга → автоматика → условия охлаждения."),
    ("Вопросы продавца", "Что за вода? Есть ли песок, ил или мусор? Каков размер включений? Куда и на какую высоту нужно откачать воду?"),
    ("Практический кейс", "Для затопленного подвала нужно уточнить загрязнённость воды, глубину приямка, высоту подъёма и длину отводящего шланга."),
    ("Как это звучит", "Уточню, насколько загрязнена вода, есть ли твёрдые включения, какую высоту и расстояние должен преодолеть насос."),
    ("Ошибка в подборе", "Неверно: выбирать только по мощности. Верно: учитывать допустимый размер включений и рабочую точку."),
    ("Красные флаги", "Крупные включения, волокнистые загрязнения, горячая или химически агрессивная жидкость могут исключить обычный дренажный насос."),
    ("Быстрая проверка", "Главные параметры: состав воды, размер включений, расход, полный напор, автоматика и режим работы."),
    ("Квиз", "Что важнее всего уточнить? Правильный ответ: состав воды и размер включений."),
    ("Итоги урока", "Дренажный насос выбирается по среде и рабочей задаче. Сначала оценивают воду и включения, затем расход и напор."),
]

SCORM_JS = r'''let api=null;function findAPI(w){for(let i=0;i<20&&w;i++,w=w.parent){if(w.API)return w.API}return null}function init(){api=findAPI(window)||findAPI(window.opener);if(api){api.LMSInitialize("");return Number(api.LMSGetValue("cmi.core.lesson_location"))||0}return Number(localStorage.getItem("jemix-3.6.1-slide"))||0}function save(i,done=false){if(api){api.LMSSetValue("cmi.core.lesson_location",String(i));api.LMSSetValue("cmi.core.lesson_status",done?"completed":"incomplete");api.LMSCommit("")}else localStorage.setItem("jemix-3.6.1-slide",String(i))}window.addEventListener("beforeunload",()=>{if(api)api.LMSFinish("")});'''
STYLE = '''body{margin:0;font-family:"PT Sans",Arial,sans-serif;background:#f3f6f9;color:#17202a}.app{max-width:1100px;margin:auto;min-height:100vh;background:#fff;display:flex;flex-direction:column}.top{padding:18px 28px;background:#0b4f87;color:#fff}.bar{height:6px;background:#dce7f0}.bar span{display:block;height:100%;background:#f08a24}.screen{flex:1;padding:48px 60px}.screen h1{font-size:38px;margin:0 0 24px}.screen p{font-size:23px;line-height:1.45}.nav{display:flex;justify-content:space-between;padding:22px 28px;border-top:1px solid #dce3ea}button{border:0;border-radius:8px;padding:13px 24px;font-size:17px}.primary{background:#0b4f87;color:#fff}.audio{margin-top:30px;width:100%}.meta{opacity:.8}'''
INDEX = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX 3.6.1</title><link rel="stylesheet" href="style.css"></head><body><div class="app"><div class="top"><b>JEMIX Academy</b> · Модуль 3 · Урок 3.6.1</div><div class="bar"><span id="progress"></span></div><main class="screen"><div class="meta" id="meta"></div><h1 id="title"></h1><p id="text"></p><audio id="audio" class="audio" controls></audio></main><div class="nav"><button id="prev">Назад</button><button id="next" class="primary">Далее</button></div></div><script src="scorm.js"></script><script src="app.js"></script></body></html>'''
APP = '''const slides=__SLIDES__;let current=Math.max(0,Math.min(init(),slides.length-1));const title=document.getElementById("title"),text=document.getElementById("text"),meta=document.getElementById("meta"),progress=document.getElementById("progress"),audio=document.getElementById("audio"),prev=document.getElementById("prev"),next=document.getElementById("next");function render(){const s=slides[current];title.textContent=s[0];text.textContent=s[1];meta.textContent=`Экран ${current+1} из ${slides.length}`;progress.style.width=`${(current+1)/slides.length*100}%`;prev.disabled=current===0;next.textContent=current===slides.length-1?"Завершить":"Далее";audio.src=`audio/slide${String(current+1).padStart(2,"0")}.mp3`;save(current,current===slides.length-1)}prev.onclick=()=>{if(current>0){current--;render()}};next.onclick=()=>{if(current<slides.length-1){current++;render()}else save(current,true)};render();'''
MANIFEST = '''<?xml version="1.0" encoding="UTF-8"?><manifest identifier="JEMIX_3_6_1" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata><organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Academy 3.6.1</title><item identifier="ITEM1" identifierref="RES1"><title>Дренажные насосы. Основы</title></item></organization></organizations><resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html"><file href="index.html"/><file href="style.css"/><file href="app.js"/><file href="scorm.js"/></resource></resources></manifest>'''

def main() -> None:
    if WORK.exists(): shutil.rmtree(WORK)
    (WORK / "audio").mkdir(parents=True)
    (WORK / "index.html").write_text(INDEX, encoding="utf-8")
    (WORK / "style.css").write_text(STYLE, encoding="utf-8")
    (WORK / "scorm.js").write_text(SCORM_JS, encoding="utf-8")
    (WORK / "app.js").write_text(APP.replace("__SLIDES__", json.dumps(SLIDES, ensure_ascii=False)), encoding="utf-8")
    (WORK / "imsmanifest.xml").write_text(MANIFEST, encoding="utf-8")
    if AUDIO.is_dir():
        for p in AUDIO.glob("slide*.mp3"): shutil.copy2(p, WORK / "audio" / p.name)
    DIST.mkdir(parents=True, exist_ok=True)
    if OUT.exists(): OUT.unlink()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(WORK.rglob("*")):
            if p.is_file(): z.write(p, p.relative_to(WORK).as_posix())
    print(f"OK: {OUT.relative_to(ROOT)}")

if __name__ == "__main__": main()
