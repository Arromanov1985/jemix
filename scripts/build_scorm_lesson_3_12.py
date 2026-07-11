#!/usr/bin/env python3
"""Build JEMIX Academy lesson 3.12 final exam as a standalone SCORM 1.2 package."""
from __future__ import annotations
import json, shutil, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'_scorm_lesson_3_12'
DIST=ROOT/'dist'/'module-03'
OUT=DIST/'JEMIX_Lesson_3_12_SCORM.zip'
AUDIO=ROOT/'voice'/'modules'/'module-03'/'lesson-3.12'/'audio'

QUESTIONS=[
{"q":"Что проверяют до выбора автоматической насосной станции?","a":["Источник, расход, напор и режим работы","Только цену","Только мощность","Только цвет"],"c":0},
{"q":"Что обязательно учитывать при подборе скважинного насоса?","a":["Динамический уровень, расход и полный напор","Только диаметр кабеля","Только бренд","Только массу"],"c":0},
{"q":"Как выбирают колодезный насос?","a":["По рабочему уровню воды, расходу и напору","По максимальной мощности","По цвету корпуса","По длине упаковки"],"c":0},
{"q":"Что важнее для дренажного насоса?","a":["Состав воды, размер включений и высота отвода","Только напряжение","Только стоимость","Только длина шнура"],"c":0},
{"q":"Когда нужна канализационная установка?","a":["Когда самотечный отвод стоков невозможен","Для повышения давления чистой воды","Для отопительного контура","Для полива"],"c":0},
{"q":"Что нужно уточнить для повышающего насоса?","a":["Исходное давление и сценарий потребления","Только мощность","Только производителя","Только материал корпуса"],"c":0},
{"q":"По каким данным выбирают циркуляционный насос?","a":["Контур, расход, сопротивление и режим работы","Глубина скважины","Размер включений","Уровень воды в колодце"],"c":0},
{"q":"Что входит в корректный подбор автоматики?","a":["Управление, защита, датчики и обвязка","Только реле","Только кабель","Только гидробак"],"c":0}
]
SCREENS=[
{"type":"info","title":"Итоговый экзамен модуля 3","text":"Проверка выбора оборудования JEMIX по задаче клиента и условиям эксплуатации."},
{"type":"info","title":"Что проверяем","text":"Различие чистой воды, грязной воды, стоков и циркуляционного контура; логику подбора и обязательные уточняющие вопросы."},
{"type":"info","title":"Правила прохождения","text":"Ответьте на 8 вопросов. Для успешного завершения нужно набрать не менее 80%."},
{"type":"info","title":"Карта модуля","text":"Станции, поверхностные, скважинные, колодезные, дренажные, фекальные, повышающие и циркуляционные насосы, канализационные установки, автоматика."},
]+[{"type":"quiz",**q} for q in QUESTIONS]

SCORM_JS=r'''let api=null;function findAPI(w){for(let i=0;i<20&&w;i++,w=w.parent){if(w.API)return w.API}return null}function init(){api=findAPI(window)||findAPI(window.opener);if(api){api.LMSInitialize("");return Number(api.LMSGetValue("cmi.core.lesson_location"))||0}return Number(localStorage.getItem("jemix-3.12-slide"))||0}function save(i,status="incomplete",score=null){if(api){api.LMSSetValue("cmi.core.lesson_location",String(i));api.LMSSetValue("cmi.core.lesson_status",status);if(score!==null){api.LMSSetValue("cmi.core.score.raw",String(score));api.LMSSetValue("cmi.core.score.min","0");api.LMSSetValue("cmi.core.score.max","100")}api.LMSCommit("")}else localStorage.setItem("jemix-3.12-slide",String(i))}window.addEventListener("beforeunload",()=>{if(api)api.LMSFinish("")});'''
STYLE='''body{margin:0;font-family:"PT Sans",Arial,sans-serif;background:#f3f6f9;color:#17202a}.app{max-width:1100px;margin:auto;min-height:100vh;background:#fff;display:flex;flex-direction:column}.top{padding:18px 28px;background:#0b4f87;color:#fff}.bar{height:6px;background:#dce7f0}.bar span{display:block;height:100%;background:#f08a24}.screen{flex:1;padding:42px 60px}.screen h1{font-size:36px;margin:0 0 22px}.screen p{font-size:22px;line-height:1.45}.answers{display:grid;gap:12px;margin-top:24px}.answer{border:1px solid #cbd7e2;background:#fff;text-align:left;padding:15px 18px;border-radius:8px;font-size:18px}.answer.selected{outline:3px solid #0b4f87}.feedback{margin-top:18px;font-size:18px;font-weight:700}.nav{display:flex;justify-content:space-between;padding:22px 28px;border-top:1px solid #dce3ea}button{border:0;border-radius:8px;padding:13px 24px;font-size:17px}.primary{background:#0b4f87;color:#fff}.audio{margin-top:24px;width:100%}.meta{opacity:.8}'''
INDEX='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX 3.12</title><link rel="stylesheet" href="style.css"></head><body><div class="app"><div class="top"><b>JEMIX Academy</b> · Модуль 3 · Итоговый экзамен</div><div class="bar"><span id="progress"></span></div><main class="screen"><div class="meta" id="meta"></div><h1 id="title"></h1><p id="text"></p><div id="answers" class="answers"></div><div id="feedback" class="feedback"></div><audio id="audio" class="audio" controls></audio></main><div class="nav"><button id="prev">Назад</button><button id="next" class="primary">Далее</button></div></div><script src="scorm.js"></script><script src="app.js"></script></body></html>'''
APP='''const screens=__SCREENS__;let current=Math.max(0,Math.min(init(),screens.length-1));const picks={};const title=document.getElementById("title"),text=document.getElementById("text"),meta=document.getElementById("meta"),progress=document.getElementById("progress"),audio=document.getElementById("audio"),answers=document.getElementById("answers"),feedback=document.getElementById("feedback"),prev=document.getElementById("prev"),next=document.getElementById("next");function render(){const s=screens[current];title.textContent=s.title;text.textContent=s.text||s.q||"";meta.textContent=`Экран ${current+1} из ${screens.length}`;progress.style.width=`${(current+1)/screens.length*100}%`;answers.innerHTML="";feedback.textContent="";if(s.type==="quiz"){s.a.forEach((v,i)=>{const b=document.createElement("button");b.className="answer"+(picks[current]===i?" selected":"");b.textContent=v;b.onclick=()=>{picks[current]=i;render()};answers.appendChild(b)})}prev.disabled=current===0;next.textContent=current===screens.length-1?"Завершить":"Далее";audio.src=`audio/slide${String(current+1).padStart(2,"0")}.mp3`;save(current)}function finish(){let total=0,correct=0;screens.forEach((s,i)=>{if(s.type==="quiz"){total++;if(picks[i]===s.c)correct++}});const score=Math.round(correct/total*100);feedback.textContent=`Результат: ${score}%. ${score>=80?"Экзамен сдан.":"Нужно повторить материал и пройти экзамен ещё раз."}`;save(current,score>=80?"passed":"failed",score)}prev.onclick=()=>{if(current>0){current--;render()}};next.onclick=()=>{const s=screens[current];if(s.type==="quiz"&&picks[current]===undefined){feedback.textContent="Выберите ответ.";return}if(current<screens.length-1){current++;render()}else finish()};render();'''
MANIFEST='''<?xml version="1.0" encoding="UTF-8"?><manifest identifier="JEMIX_3_12" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata><organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Academy 3.12</title><item identifier="ITEM1" identifierref="RES1"><title>Итоговый экзамен модуля 3</title></item></organization></organizations><resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html"><file href="index.html"/><file href="style.css"/><file href="app.js"/><file href="scorm.js"/></resource></resources></manifest>'''

def main():
    if WORK.exists(): shutil.rmtree(WORK)
    (WORK/'audio').mkdir(parents=True)
    (WORK/'index.html').write_text(INDEX,encoding='utf-8')
    (WORK/'style.css').write_text(STYLE,encoding='utf-8')
    (WORK/'scorm.js').write_text(SCORM_JS,encoding='utf-8')
    (WORK/'app.js').write_text(APP.replace('__SCREENS__',json.dumps(SCREENS,ensure_ascii=False)),encoding='utf-8')
    (WORK/'imsmanifest.xml').write_text(MANIFEST,encoding='utf-8')
    if AUDIO.is_dir():
        for p in AUDIO.glob('slide*.mp3'): shutil.copy2(p,WORK/'audio'/p.name)
    DIST.mkdir(parents=True,exist_ok=True)
    if OUT.exists(): OUT.unlink()
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(WORK.rglob('*')):
            if p.is_file(): z.write(p,p.relative_to(WORK).as_posix())
    print(f'OK: {OUT.relative_to(ROOT)}')

if __name__=='__main__': main()
