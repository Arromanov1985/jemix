#!/usr/bin/env python3
"""Build SCORM 1.2 package for JEMIX lesson 2.2: Source and water intake."""
from __future__ import annotations
import json, shutil, zipfile
from pathlib import Path

ROOT=Path('.')
WORK=ROOT/'_scorm_lesson_2_2'
DIST=ROOT/'dist'/'module-02'
OUT=DIST/'JEMIX_Lesson_2_2_SCORM.zip'
LOGO=ROOT/'academy-assets'/'logo'/'jemix-logo.png'
PUMP=ROOT/'academy-assets'/'pumps'/'jemix-pump.png'
AUDIO=ROOT/'voice'/'modules'/'module-02'/'lesson-2.2'/'audio'

SCREENS=[
 {'type':'title','title':'Источник и забор воды','body':'Источник воды определяет тип насоса, схему забора и обязательную защиту.'},
 {'type':'goals','title':'Что нужно понять','items':['Различать колодец, скважину и ёмкость','Уточнять уровень воды и дебит','Видеть риск сухого хода','Связывать источник с типом насоса']},
 {'type':'theory','title':'Источник','body':'Для подбора важно знать не только глубину до дна, а рабочий уровень воды и его изменение во время отбора.'},
 {'type':'scheme','title':'Карта выбора','items':['Колодец — поверхностный или погружной','Скважина — скважинный насос','Ёмкость — поверхностный или погружной','Центральная сеть — повышающий насос']},
 {'type':'map','title':'Вопросы продавца','items':['Откуда берём воду?','Каков статический и динамический уровень?','Какой дебит источника?','Есть ли риск сухого хода?','Куда и на какую высоту подаём воду?']},
 {'type':'case','title':'Практический кейс','body':'Колодец 9 м, уровень воды летом падает до 7 м. Нужна вода в дом и полив. Следует оценить рабочий уровень, расход, напор и предусмотреть защиту от сухого хода.'},
 {'type':'dialogue','title':'Как это звучит','client':'Нужен насос для колодца глубиной 10 метров','seller':'Уточним не только глубину до дна, но и уровень воды при работе, расстояние до дома, точки потребления и риск сухого хода.'},
 {'type':'compare','title':'Ошибка в подборе','wrong':'Подбирать только по общей глубине до дна','right':'Подбирать по рабочему уровню воды, дебиту и условиям подачи'},
 {'type':'flags','title':'Красные флаги','items':['Уровень воды сильно меняется','Источник малодебитный','Нет защиты от сухого хода','Длинная всасывающая линия','Неизвестен диаметр скважины']},
 {'type':'quiz_intro','title':'Быстрая проверка','body':'Что важнее уточнить для колодца перед подбором насоса?'},
 {'type':'quiz','title':'Квиз','question':'Что важнее уточнить для колодца перед подбором насоса?','answers':['Рабочий уровень воды и риск сухого хода','Только глубину до дна','Только цвет корпуса','Только мощность двигателя'],'correct':0},
 {'type':'summary','title':'Итоги урока','items':['Источник определяет группу насоса','Рабочий уровень важнее глубины до дна','Дебит ограничивает допустимый расход','Защита от сухого хода обязательна при риске осушения']},
]


def reset():
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True); DIST.mkdir(parents=True,exist_ok=True)


def copy_assets():
    img=WORK/'img'; img.mkdir()
    if LOGO.exists(): shutil.copy2(LOGO,img/'jemix-logo.png')
    if PUMP.exists(): shutil.copy2(PUMP,img/'jemix-pump.png')
    aud=WORK/'audio'; aud.mkdir()
    for i in range(1,13):
        src=AUDIO/f'slide{i:02d}.mp3'
        if src.exists(): shutil.copy2(src,aud/src.name)


def write_files():
    files=['index.html','style.css','app.js','scorm.js','course-data.js','img/jemix-logo.png','img/jemix-pump.png']+[f'audio/slide{i:02d}.mp3' for i in range(1,13)]
    manifest='''<?xml version="1.0" encoding="UTF-8"?>\n<manifest identifier="JEMIX_LESSON_2_2" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata><organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Lesson 2.2</title><item identifier="ITEM1" identifierref="RES1"><title>Источник и забор воды</title></item></organization></organizations><resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">'''+''.join(f'<file href="{f}"/>' for f in files if (WORK/f).exists() or not f.startswith(('img/','audio/')))+'''</resource></resources></manifest>'''
    (WORK/'imsmanifest.xml').write_text(manifest,encoding='utf-8')
    (WORK/'course-data.js').write_text('window.COURSE='+json.dumps(SCREENS,ensure_ascii=False)+';',encoding='utf-8')
    (WORK/'index.html').write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy — 2.2</title><link rel="stylesheet" href="style.css"></head><body><div id="app"></div><script src="scorm.js"></script><script src="course-data.js"></script><script src="app.js"></script></body></html>',encoding='utf-8')
    (WORK/'scorm.js').write_text('''function api(w){let n=0;while(w&&n++<500){if(w.API)return w.API;if(w.parent===w)break;w=w.parent}return null}var API=api(window)||(window.opener?api(window.opener):null),ready=false;function init(){try{ready=!!API&&API.LMSInitialize("")==="true";if(ready){API.LMSSetValue("cmi.core.lesson_status","incomplete");API.LMSCommit("")}}catch(e){}}function setScorm(p,s){if(!ready)return;try{API.LMSSetValue("cmi.core.score.raw",String(p));API.LMSSetValue("cmi.core.lesson_status",s);API.LMSSetValue("cmi.suspend_data",JSON.stringify({i:window.current||0}));API.LMSCommit("")}catch(e){}}function finish(){try{if(ready){API.LMSCommit("");API.LMSFinish("")}}catch(e){}}addEventListener("load",init);addEventListener("beforeunload",finish);''',encoding='utf-8')
    (WORK/'style.css').write_text(''':root{--r:#e30613;--k:#151515;--g:#f4f4f4;--m:#6b7280}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:var(--k);background:#fff}.shell{min-height:100vh;display:grid;grid-template-columns:270px 1fr}.side{padding:28px 22px;border-right:1px solid #ddd;background:#fafafa}.brand{font-size:34px;font-weight:900}.module{margin:22px 0 12px;font-weight:800}.nav div{padding:10px 0;color:#666}.nav .active{color:var(--r);font-weight:900}.stage{display:flex;flex-direction:column}.top{height:82px;border-bottom:1px solid #ddd;display:flex;align-items:center;gap:18px;padding:0 34px}.bar{height:7px;background:#eee;flex:1;border-radius:9px;overflow:hidden}.bar i{display:block;height:100%;background:var(--r)}.content{flex:1;padding:42px;display:flex;align-items:center;justify-content:center}.card{width:min(980px,100%);border:1px solid #ddd;border-radius:24px;padding:38px;background:#fff;box-shadow:0 18px 50px rgba(0,0,0,.08)}h1{font-size:44px;margin:8px 0 22px}.tag{color:var(--r);font-weight:900}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.item,.answer{padding:18px;border-radius:14px;background:var(--g);border:1px solid #e5e5e5}.answer{width:100%;text-align:left;margin:7px 0;font-size:17px}.audio{margin-top:24px}.audio audio{width:100%}footer{display:flex;justify-content:space-between;padding:20px 34px;border-top:1px solid #ddd}button{border:0;border-radius:12px;padding:13px 22px;font-weight:800;cursor:pointer}.next{background:var(--r);color:#fff}.ok{padding:14px;background:#eaf8ef;color:#166534;border-radius:12px;margin-top:12px}.bad{padding:14px;background:#fff0f0;color:#991b1b;border-radius:12px;margin-top:12px}@media(max-width:800px){.shell{grid-template-columns:1fr}.side{display:none}.content{padding:18px}h1{font-size:34px}.grid{grid-template-columns:1fr}}''',encoding='utf-8')
    (WORK/'app.js').write_text(r'''window.current=0;let answered=false;const app=document.getElementById('app');const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));function pct(){return Math.round((current+1)/COURSE.length*100)}function side(){return `<aside class="side"><div class="brand">JEMIX</div><div class="module">Модуль 2</div><div class="nav"><div>2.1 Система</div><div class="active">2.2 Источник</div><div>2.3 Расход</div><div>2.4 Напор</div><div>2.5 Автоматика</div></div></aside>`}function audio(){let n=String(current+1).padStart(2,'0');return `<div class="audio"><audio controls preload="metadata" src="audio/slide${n}.mp3"></audio></div>`}function items(a){return `<div class="grid">${(a||[]).map(x=>`<div class="item">${esc(x)}</div>`).join('')}</div>`}function body(s){if(s.type==='quiz')return `<div class="tag">Проверка</div><h1>${esc(s.question)}</h1>${s.answers.map((x,i)=>`<button class="answer" onclick="answer(${i})">${esc(x)}</button>`).join('')}<div id="fb"></div>${audio()}`;let h=`<div class="tag">Урок 2.2</div><h1>${esc(s.title)}</h1>`;if(s.body)h+=`<p>${esc(s.body)}</p>`;if(s.items)h+=items(s.items);if(s.client)h+=`<div class="item"><b>Клиент:</b> ${esc(s.client)}</div><div class="item"><b>Продавец:</b> ${esc(s.seller)}</div>`;if(s.wrong)h+=`<div class="grid"><div class="item"><b>Ошибка:</b><br>${esc(s.wrong)}</div><div class="item"><b>Правильно:</b><br>${esc(s.right)}</div></div>`;return h+audio()}function render(){let s=COURSE[current],p=pct();app.innerHTML=`<main class="shell">${side()}<section class="stage"><header class="top"><b>${esc(s.title)}</b><div class="bar"><i style="width:${p}%"></i></div><strong>${p}%</strong></header><div class="content"><article class="card">${body(s)}</article></div><footer><button onclick="prev()" ${current===0?'disabled':''}>Назад</button><button class="next" onclick="next()">${current===COURSE.length-1?'Завершить':'Далее'}</button></footer></section></main>`;setScorm(p,current===COURSE.length-1?'incomplete':'incomplete')}function prev(){if(current>0){current--;render()}}function next(){if(COURSE[current].type==='quiz'&&!answered)return;if(current<COURSE.length-1){current++;answered=false;render()}else{setScorm(100,'completed');app.innerHTML='<div class="content"><div class="card"><h1>Урок 2.2 завершён</h1><p>Результат передан в LMS.</p></div></div>'}}function answer(i){let s=COURSE[current],fb=document.getElementById('fb');if(i===s.correct){answered=true;fb.innerHTML='<div class="ok">Верно. Можно продолжать.</div>'}else fb.innerHTML='<div class="bad">Неверно. Попробуйте ещё раз.</div>'}addEventListener('load',render);''',encoding='utf-8')


def pack():
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for p in WORK.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(WORK))
    print(OUT)


def main():
    reset(); copy_assets(); write_files(); pack()

if __name__=='__main__': main()
