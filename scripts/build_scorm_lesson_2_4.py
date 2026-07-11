#!/usr/bin/env python3
"""Build SCORM 1.2 package for JEMIX lesson 2.4: Napory i poteri."""
from __future__ import annotations
import json, shutil, zipfile
from pathlib import Path

ROOT=Path('.')
WORK=ROOT/'_scorm_lesson_2_4'
DIST=ROOT/'dist'/'module-02'
OUT=DIST/'JEMIX_Lesson_2_4_SCORM.zip'
AUDIO=ROOT/'voice'/'modules'/'module-02'/'lesson-2.4'/'audio'
LOGO=ROOT/'academy-assets'/'logo'/'jemix-logo.png'
PUMP=ROOT/'academy-assets'/'pumps'/'jemix-pump.png'

SCREENS=[
 {'type':'title','title':'Напор и потери','body':'Напор показывает, что насосу нужно преодолеть в системе.'},
 {'type':'goals','title':'Что нужно понять','items':['Высота','Длина трассы','Потери в трубах','Нужное давление']},
 {'type':'theory','title':'Из чего складывается напор','body':'Учитываем вертикальный подъём, горизонтальную трассу, местные сопротивления и требуемое давление.'},
 {'type':'scheme','title':'Карта расчёта','items':['Источник','Высота','Трасса','Фильтры и арматура','Давление у потребителя']},
 {'type':'map','title':'Вопросы продавца','items':['Глубина и уровень воды','Расстояние до дома','Диаметр трубы','Количество этажей','Какое давление нужно']},
 {'type':'case','title':'Практический кейс','body':'Скважина 30 м, дом в 40 м, два этажа. Нельзя учитывать только глубину скважины.'},
 {'type':'dialogue','title':'Как это звучит','body':'Уточним высоту, расстояние, диаметр трубы и требуемое давление — тогда определим рабочий напор.'},
 {'type':'right_wrong','title':'Ошибка в подборе','wrong':'Берём насос с максимальным напором 50 м','right':'Смотрим напор при нужном расходе и учитываем все потери'},
 {'type':'red_flags','title':'Красные флаги','items':['Неизвестен диаметр трубы','Длинная трасса','Много поворотов и фильтров','Нужно давление на втором этаже']},
 {'type':'quiz_intro','title':'Быстрая проверка','body':'Что входит в оценку напора для водоснабжения дома?'},
 {'type':'quiz','title':'Квиз','question':'Что входит в оценку напора для водоснабжения дома?','answers':['Высота, длина линии, потери и нужное давление','Только вертикальная глубина','Только мощность двигателя','Только цена насоса'],'correct':0},
 {'type':'summary','title':'Итоги урока','items':['Напор — это не мощность','Учитываем высоту и потери','Рабочая точка важнее максимума','Дальность и диаметр трубы меняют подбор']},
]
for i,s in enumerate(SCREENS,1): s['audio']=f'slide{i:02d}.mp3'

def build():
    if WORK.exists(): shutil.rmtree(WORK)
    (WORK/'img').mkdir(parents=True)
    (WORK/'audio').mkdir(parents=True)
    DIST.mkdir(parents=True,exist_ok=True)
    if LOGO.exists(): shutil.copy2(LOGO,WORK/'img'/'jemix-logo.png')
    if PUMP.exists(): shutil.copy2(PUMP,WORK/'img'/'jemix-pump.png')
    for i in range(1,13):
        src=AUDIO/f'slide{i:02d}.mp3'
        if src.exists(): shutil.copy2(src,WORK/'audio'/src.name)
    (WORK/'course-data.js').write_text('window.COURSE='+json.dumps({'module':'Модуль 2','lesson':'2.4','title':'Напор и потери','screens':SCREENS},ensure_ascii=False)+';',encoding='utf-8')
    (WORK/'index.html').write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX 2.4</title><link rel="stylesheet" href="style.css"></head><body><main id="app"></main><script src="scorm.js"></script><script src="course-data.js"></script><script src="app.js"></script></body></html>',encoding='utf-8')
    (WORK/'scorm.js').write_text('''function api(w){for(let i=0;w&&i<500;i++,w=w.parent){if(w.API)return w.API;if(w.parent===w)break}return null}const A=api(window)||(window.opener&&api(window.opener));let R=false;function init(){if(A){R=A.LMSInitialize("")==="true";if(R){A.LMSSetValue("cmi.core.lesson_status","incomplete");A.LMSCommit("")}}}function save(p,s){if(R){A.LMSSetValue("cmi.core.score.raw",String(p));A.LMSSetValue("cmi.core.lesson_status",s);A.LMSCommit("")}}function finish(){if(R){A.LMSCommit("");A.LMSFinish("")}}addEventListener("load",init);addEventListener("beforeunload",finish);''',encoding='utf-8')
    (WORK/'app.js').write_text('''let i=0,a=false;const app=document.getElementById("app"),S=COURSE.screens;const esc=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\\"":"&quot;","'":"&#39;"}[c]));function pct(){return Math.round((i+1)/S.length*100)}function audio(f){return `<audio controls src="audio/${f}"></audio>`}function render(){const s=S[i];let b=s.body?`<p>${esc(s.body)}</p>`:"";if(s.items)b+=`<div class="grid">${s.items.map(x=>`<div>${esc(x)}</div>`).join("")}</div>`;if(s.wrong)b+=`<div class="bad">${esc(s.wrong)}</div><div class="ok">${esc(s.right)}</div>`;if(s.type==="quiz")b+=`<div class="answers">${s.answers.map((x,n)=>`<button onclick="answer(${n})">${esc(x)}</button>`).join("")}</div><div id="fb"></div>`;app.innerHTML=`<div class="layout"><aside><img src="img/jemix-logo.png"><h2>Модуль 2</h2><b>2.4 Напор и потери</b></aside><section><header><strong>${esc(COURSE.title)}</strong><span>${pct()}%</span></header><article><span class="tag">Экран ${i+1} из ${S.length}</span><h1>${esc(s.title)}</h1>${b}${audio(s.audio)}</article><footer><button onclick="prev()">Назад</button><button onclick="next()">${i===S.length-1?"Завершить":"Далее"}</button></footer></section></div>`}function prev(){if(i>0){i--;render()}}function next(){if(i<S.length-1){i++;render();save(pct(),"incomplete")}else{save(100,"completed");app.innerHTML='<div class="done"><h1>Урок 2.4 завершён</h1><button onclick="finish()">Закрыть</button></div>'}}function answer(n){const s=S[i],fb=document.getElementById("fb");fb.innerHTML=n===s.correct?'<div class="ok">Верно</div>':'<div class="bad">Неверно. Попробуйте ещё раз.</div>'}addEventListener("load",render);''',encoding='utf-8')
    (WORK/'style.css').write_text('''*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#f4f5f7;color:#161616}.layout{min-height:100vh;display:grid;grid-template-columns:260px 1fr}aside{background:#111;color:#fff;padding:28px}aside img{max-width:150px;background:#fff;padding:8px;border-radius:8px}section{display:flex;flex-direction:column}header,footer{height:76px;background:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 32px;border-bottom:1px solid #ddd}article{margin:auto;width:min(900px,90%);background:#fff;border-radius:22px;padding:42px;box-shadow:0 18px 50px #0001}h1{font-size:42px;margin:12px 0 20px}.tag{color:#e30613;font-weight:800}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.grid div,.answers button,.bad,.ok{padding:16px;border-radius:12px;background:#f0f1f3;margin:8px 0}.answers{display:grid;gap:10px}.answers button{border:1px solid #ddd;text-align:left}.bad{background:#ffe7e7}.ok{background:#e7f7ec}audio{width:100%;margin-top:22px}footer button,.done button{padding:13px 24px;border:0;border-radius:10px;font-weight:700}.done{min-height:100vh;display:grid;place-content:center;text-align:center}''',encoding='utf-8')
    files=['index.html','style.css','app.js','scorm.js','course-data.js']
    manifest='''<?xml version="1.0" encoding="UTF-8"?><manifest identifier="JEMIX_2_4" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata><organizations default="ORG"><organization identifier="ORG"><title>JEMIX 2.4</title><item identifier="I" identifierref="R"><title>Напор и потери</title></item></organization></organizations><resources><resource identifier="R" type="webcontent" adlcp:scormtype="sco" href="index.html">'''+''.join(f'<file href="{x}"/>' for x in files)+'''</resource></resources></manifest>'''
    (WORK/'imsmanifest.xml').write_text(manifest,encoding='utf-8')
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for p in WORK.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(WORK).as_posix())
    print(OUT)

if __name__=='__main__': build()
