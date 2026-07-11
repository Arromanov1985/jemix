#!/usr/bin/env python3
"""Build SCORM 1.2 package for JEMIX Academy lesson 2.1."""
from __future__ import annotations
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path('.')
WORK = ROOT / '_scorm_lesson_2_1'
DIST = ROOT / 'dist' / 'module-02'
OUT = DIST / 'JEMIX_Lesson_2_1_SCORM.zip'
LOGO = ROOT / 'academy-assets' / 'logo' / 'jemix-logo.png'
PUMP = ROOT / 'academy-assets' / 'pumps' / 'jemix-pump.png'
AUDIO = ROOT / 'voice' / 'modules' / 'module-02' / 'lesson-2.1' / 'audio'

SCREENS = [
  {'type':'title','title':'Водоснабжение как система','body':'Насос — только один элемент. Рабочее решение начинается с источника, линии, точек водоразбора, автоматики и защиты.'},
  {'type':'goals','title':'Что нужно понять','items':['Источник определяет способ забора воды','Расход связан с количеством точек','Напор включает высоту и потери','Насос подбирают вместе с автоматикой и защитой']},
  {'type':'theory','title':'Насос','body':'Насос передаёт воде энергию, но сам по себе не гарантирует стабильную работу системы.'},
  {'type':'scheme','title':'Карта системы','items':['Источник','Насос','Трубопровод','Автоматика','Потребители']},
  {'type':'map','title':'Вопросы продавца','items':['Откуда берём воду?','Какая глубина и уровень воды?','Сколько точек работает одновременно?','Какое расстояние до дома?','Какая автоматика уже есть?']},
  {'type':'case','title':'Практический кейс','body':'Колодец в 18 м от дома, две точки водоразбора и полив. Нужно уточнить рабочий уровень воды, трассу, расход и защиту от сухого хода.'},
  {'type':'dialogue','title':'Как это звучит','client':'Нужен насос для дома из колодца.','seller':'Уточним уровень воды, расстояние, высоту подъёма и сколько точек будет работать одновременно.'},
  {'type':'compare','title':'Ошибка в подборе','wrong':'Сразу предложить самый мощный насос','right':'Сначала собрать данные по системе и только потом выбрать модель'},
  {'type':'flags','title':'Красные флаги','items':['Неизвестен рабочий уровень воды','Не учтена длина линии','Нет защиты от сухого хода','Неясен одновременный расход']},
  {'type':'intro','title':'Быстрая проверка','body':'Что продавец должен уточнить первым?'} ,
  {'type':'quiz','title':'Квиз','question':'Клиент просит насос для дома из колодца. С чего начать?','answers':['Уточнить источник, расстояние, высоту и точки водоразбора','Сразу предложить самый мощный насос','Спросить только цену','Подобрать только по глубине'],'correct':0},
  {'type':'summary','title':'Итоги урока','items':['Водоснабжение — это система','Источник и трасса влияют на выбор','Расход и напор считаются вместе','Автоматика и защита обязательны']},
]

SCORM_JS = r'''function findAPI(w){let n=0;while(w&&n<500){if(w.API)return w.API;n++;if(w.parent===w)break;w=w.parent}return null}
var API=findAPI(window)||(window.opener?findAPI(window.opener):null),ready=false;
function init(){if(!API)return;try{ready=API.LMSInitialize("")==="true";if(ready){let p=parseInt(API.LMSGetValue("cmi.core.lesson_location")||"0",10);window.resumeIndex=isNaN(p)?0:p;API.LMSSetValue("cmi.core.lesson_status","incomplete");API.LMSCommit("")}}catch(e){}}
function save(i,score,status){if(!ready)return;try{API.LMSSetValue("cmi.core.lesson_location",String(i));API.LMSSetValue("cmi.core.score.raw",String(score));API.LMSSetValue("cmi.core.lesson_status",status);API.LMSCommit("")}catch(e){}}
function finish(){if(!ready)return;try{API.LMSCommit("");API.LMSFinish("")}catch(e){}}
window.addEventListener("load",init);window.addEventListener("beforeunload",finish);'''

CSS = r''':root{--red:#e30613;--ink:#161616;--muted:#6d6d6d;--line:#e7e7e7;--soft:#f7f7f7}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:var(--ink);background:#fff}.shell{min-height:100vh;display:grid;grid-template-columns:260px 1fr}.side{border-right:1px solid var(--line);padding:28px 22px;display:flex;flex-direction:column;gap:18px}.logo{max-width:150px}.module{font-size:13px;color:var(--muted);text-transform:uppercase}.side h2{margin:0;font-size:25px}.side nav{display:grid;gap:8px}.side nav span{padding:10px 12px;border-radius:10px;background:var(--soft)}.side nav .active{background:#111;color:#fff}.remember{margin-top:auto;border-left:5px solid var(--red);padding:12px;background:var(--soft)}.stage{display:flex;flex-direction:column;min-width:0}.top{height:86px;border-bottom:1px solid var(--line);display:grid;grid-template-columns:1fr 260px 70px;align-items:center;gap:18px;padding:0 34px}.bar{height:7px;background:#eee;border-radius:99px;overflow:hidden}.bar i{display:block;height:100%;background:var(--red)}.content{padding:38px;flex:1}.card{max-width:960px;margin:0 auto;border:1px solid var(--line);border-radius:24px;padding:34px;background:#fff;box-shadow:0 18px 50px rgba(0,0,0,.06)}.tag{font-size:13px;font-weight:800;color:var(--red);text-transform:uppercase}.card h1{font-size:46px;line-height:1.05;margin:12px 0 20px}.card p{font-size:21px;line-height:1.5;color:#444}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.item{padding:18px;border-radius:16px;background:var(--soft);font-size:18px}.scheme{display:flex;flex-wrap:wrap;gap:12px}.scheme span{padding:18px 22px;border:1px solid var(--line);border-radius:16px;font-weight:800}.compare{display:grid;grid-template-columns:1fr 1fr;gap:16px}.bad,.good{padding:22px;border-radius:18px}.bad{background:#fff1f1}.good{background:#eefaf1}.dialogue{display:grid;gap:12px}.bubble{padding:18px;border-radius:18px;background:var(--soft)}.bubble.seller{border-left:5px solid var(--red)}.answers{display:grid;gap:10px}.answers button{padding:16px;text-align:left;border:1px solid var(--line);border-radius:14px;background:#fff;font-size:17px}.audio{margin-top:22px;padding-top:18px;border-top:1px solid var(--line)}.audio audio{width:100%}.actions{display:flex;justify-content:space-between;padding:18px 34px;border-top:1px solid var(--line)}button{font:inherit;cursor:pointer}.actions button{padding:13px 22px;border-radius:12px;border:0}.next{background:#111;color:#fff}.feedback{margin-top:14px;font-weight:800}.ok{color:#19703b}.no{color:#b42318}@media(max-width:800px){.shell{grid-template-columns:1fr}.side{display:none}.top{grid-template-columns:1fr 150px 50px;padding:0 18px}.content{padding:18px}.card{padding:22px}.card h1{font-size:34px}.grid,.compare{grid-template-columns:1fr}}'''


def build() -> None:
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    (WORK/'img').mkdir()
    (WORK/'audio').mkdir()
    if LOGO.exists(): shutil.copy2(LOGO, WORK/'img'/'jemix-logo.png')
    if PUMP.exists(): shutil.copy2(PUMP, WORK/'img'/'jemix-pump.png')
    for i in range(1,13):
        src=AUDIO/f'slide{i:02d}.mp3'
        if src.exists(): shutil.copy2(src, WORK/'audio'/src.name)

    files=['index.html','style.css','app.js','scorm.js','course-data.js']
    files += [f'img/{p.name}' for p in (WORK/'img').iterdir()]
    files += [f'audio/{p.name}' for p in (WORK/'audio').iterdir()]
    manifest_files=''.join(f'<file href="{x}"/>' for x in files)
    (WORK/'imsmanifest.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>\n<manifest identifier="JEMIX_LESSON_2_1" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata><organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Lesson 2.1</title><item identifier="ITEM1" identifierref="RES1"><title>Водоснабжение как система</title></item></organization></organizations><resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">{manifest_files}</resource></resources></manifest>''',encoding='utf-8')
    (WORK/'index.html').write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy 2.1</title><link rel="stylesheet" href="style.css"></head><body><div id="app"></div><script src="scorm.js"></script><script src="course-data.js"></script><script src="app.js"></script></body></html>',encoding='utf-8')
    (WORK/'style.css').write_text(CSS,encoding='utf-8')
    (WORK/'scorm.js').write_text(SCORM_JS,encoding='utf-8')
    (WORK/'course-data.js').write_text('window.COURSE='+json.dumps(SCREENS,ensure_ascii=False)+';',encoding='utf-8')
    (WORK/'app.js').write_text(r'''const app=document.getElementById('app');let i=0,answered=false;window.addEventListener('load',()=>{i=window.resumeIndex||0;render()});function esc(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function pct(){return Math.round(((i+1)/COURSE.length)*100)}function audio(){const n=String(i+1).padStart(2,'0');return `<div class="audio"><audio controls src="audio/slide${n}.mp3"></audio></div>`}function body(s){if(s.items)return `<div class="grid">${s.items.map(x=>`<div class="item">${esc(x)}</div>`).join('')}</div>`;if(s.type==='dialogue')return `<div class="dialogue"><div class="bubble">Клиент: ${esc(s.client)}</div><div class="bubble seller">Продавец: ${esc(s.seller)}</div></div>`;if(s.type==='compare')return `<div class="compare"><div class="bad"><b>Ошибка</b><p>${esc(s.wrong)}</p></div><div class="good"><b>Правильно</b><p>${esc(s.right)}</p></div></div>`;if(s.type==='quiz')return `<p>${esc(s.question)}</p><div class="answers">${s.answers.map((x,n)=>`<button onclick="answer(${n})">${esc(x)}</button>`).join('')}</div><div id="fb" class="feedback"></div>`;return `<p>${esc(s.body)}</p>`}function render(){const s=COURSE[i],p=pct();app.innerHTML=`<main class="shell"><aside class="side"><img class="logo" src="img/jemix-logo.png" alt="JEMIX"><div class="module">Модуль 2</div><h2>Системы водоснабжения</h2><nav><span class="active">2.1 Водоснабжение как система</span><span>2.2 Источник и забор воды</span><span>2.3 Расход дома</span></nav><div class="remember"><b>Запомните</b><br>Подбираем не насос, а рабочую систему.</div></aside><section class="stage"><header class="top"><div><small>Урок 1 из 6</small><br><b>${esc(s.title)}</b></div><div class="bar"><i style="width:${p}%"></i></div><b>${p}%</b></header><div class="content"><article class="card"><div class="tag">Экран ${i+1} из ${COURSE.length}</div><h1>${esc(s.title)}</h1>${body(s)}${s.type!=='quiz'?audio():''}</article></div><footer class="actions"><button onclick="prev()" ${i===0?'disabled':''}>Назад</button><button class="next" onclick="next()">${i===COURSE.length-1?'Завершить':'Далее'}</button></footer></section></main>`;save(i,p,i===COURSE.length-1?'completed':'incomplete')}function prev(){if(i>0){i--;render()}}function next(){if(COURSE[i].type==='quiz'&&!answered)return;if(i<COURSE.length-1){i++;render()}else{save(i,100,'completed');finish();app.innerHTML='<div class="content"><article class="card"><h1>Урок 2.1 завершён</h1><p>Результат передан в LMS.</p></article></div>'}}function answer(n){const s=COURSE[i],fb=document.getElementById('fb');if(n===s.correct){answered=true;fb.innerHTML='<span class="ok">Верно. Можно продолжать.</span>'}else fb.innerHTML='<span class="no">Неверно. Проверьте логику системы и попробуйте ещё раз.</span>'}''',encoding='utf-8')
    DIST.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for p in WORK.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(WORK))
    print(OUT)

if __name__=='__main__': build()
