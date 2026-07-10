#!/usr/bin/env python3
from pathlib import Path
import shutil, zipfile, json

ROOT=Path('.')
WORK=ROOT/'_scorm_lesson_1_1_final'
DIST=ROOT/'dist'/'module-01'
OUT=DIST/'JEMIX_Lesson_1_1_SCORM_FINAL.zip'
LOGO=ROOT/'academy-assets'/'logo'/'jemix-logo.png'
PUMP=ROOT/'academy-assets'/'pumps'/'jemix-pump.png'
AUDIO=ROOT/'voice'/'modules'/'module-01'/'lesson-1.1'/'audio'

SCREENS=[
 {'kind':'cover','title':'Что такое насос?','subtitle':'Первый урок Академии JEMIX: базовое понятие, принцип работы и применение.','audio':'slide01.mp3'},
 {'kind':'goals','title':'После урока вы сможете','items':['Объяснить, что такое насос','Понять, зачем насос нужен в системе','Назвать основные области применения','Подготовиться к дальнейшему подбору оборудования'],'audio':'slide02.mp3'},
 {'kind':'definition','title':'Что такое насос','body':'Насос не создаёт воду, а перемещает жидкость внутри системы.','note':'Насос не создаёт воду. Он передаёт воде энергию.','audio':'slide03.mp3'},
 {'kind':'flow','title':'Источник — насос — дом','body':'Насос находится между источником и потребителем: забирает воду и помогает доставить её к точкам водоразбора.','audio':'slide04.mp3'},
 {'kind':'applications','title':'Где применяются насосы','items':[['Частный дом','Водоснабжение кухни, душа и других точек.'],['Дача и полив','Подача воды из колодца, ёмкости или другого источника.'],['Хозяйственные задачи','Перекачивание воды и работа в инженерных системах.']],'audio':'slide05.mp3'},
 {'kind':'tip','title':'Совет инженера','body':'Не начинайте подбор с мощности насоса.','items':['Источник воды','Требуемый расход','Необходимый напор'],'audio':'slide06.mp3'},
 {'kind':'quiz','title':'Что делает насос?','answers':[['Создаёт воду',False],['Передаёт жидкости энергию',True],['Только очищает воду',False],['Хранит запас воды',False]],'audio':'slide07.mp3'},
 {'kind':'summary','title':'Главное из урока','items':['Насос — гидравлическая машина','Он передаёт жидкости энергию','Насос связывает источник воды и потребителя'],'audio':'slide08.mp3'}]

def cp():
    (WORK/'img').mkdir(parents=True,exist_ok=True)
    (WORK/'audio').mkdir(parents=True,exist_ok=True)
    if LOGO.exists(): shutil.copy2(LOGO,WORK/'img'/'jemix-logo.png')
    if PUMP.exists(): shutil.copy2(PUMP,WORK/'img'/'jemix-pump.png')
    for i in range(1,9):
        p=AUDIO/f'slide{i:02d}.mp3'
        if p.exists(): shutil.copy2(p,WORK/'audio'/p.name)

def manifest():
    (WORK/'imsmanifest.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_LESSON_1_1" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata><organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Lesson 1.1</title><item identifier="ITEM1" identifierref="RES1"><title>Что такое насос</title></item></organization></organizations><resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html"><file href="index.html"/><file href="style.css"/><file href="app.js"/><file href="scorm.js"/></resource></resources></manifest>''',encoding='utf-8')

def scorm():
    (WORK/'scorm.js').write_text("""function findAPI(w){let n=0;while(w&&n<500){if(w.API)return w.API;n++;if(w.parent===w)break;w=w.parent}return null}var API=findAPI(window)||(window.opener?findAPI(window.opener):null),ready=false;function scormInit(){if(!API)return false;try{ready=API.LMSInitialize('')==='true';if(ready){API.LMSSetValue('cmi.core.lesson_status','incomplete');API.LMSCommit('')}return ready}catch(e){return false}}function scormSet(score,status){if(!API||!ready)return;try{API.LMSSetValue('cmi.core.score.raw',String(score));API.LMSSetValue('cmi.core.lesson_status',status);API.LMSCommit('')}catch(e){}}function scormFinish(){if(!API||!ready)return;try{API.LMSCommit('');API.LMSFinish('')}catch(e){}}window.addEventListener('load',scormInit);window.addEventListener('beforeunload',scormFinish);""",encoding='utf-8')

def files():
    (WORK/'index.html').write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy — Урок 1.1</title><link rel="stylesheet" href="style.css"></head><body><div id="app"></div><script src="scorm.js"></script><script src="app.js"></script></body></html>',encoding='utf-8')
    data=json.dumps(SCREENS,ensure_ascii=False)
    app=f"""
const screens={data};let index=0,answered=false;const app=document.getElementById('app');const esc=s=>String(s??'').replace(/[&<>\"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[c]));
function logo(){{return `<img class='logoImg' src='img/jemix-logo.png' alt='JEMIX'>`}}
function pump(){{return `<div class='pumpCard'><img src='img/jemix-pump.png' alt='Насос JEMIX'></div>`}}
function side(){{return `<aside><div>${{logo()}}</div><div class='module'>Модуль 1</div><h2>Основы насосной техники</h2><nav><button class='active'>1.1 Что такое насос</button><button>1.2 Применение</button><button>1.3 Устройство</button></nav><div class='remember'><b>Запомните</b><span>Насос не создаёт воду.<br>Он передаёт воде энергию.</span></div></aside>`}}
function top(title){{const p=Math.round((index+1)/screens.length*100);return `<header><div><small>Урок 1 из 6</small><strong>${{esc(title)}}</strong></div><div class='progress'><i style='width:${{p}}%'></i></div><b>${{p}}%</b><span>Звук</span><span>Меню</span></header>`}}
function audio(f){{return `<div class='audioRow'><button onclick='toggle(this)'>▶ Прослушать</button><audio src='audio/${{f}}'></audio></div>`}}
function toggle(b){{const a=b.nextElementSibling;if(a.paused){{a.play();b.textContent='❚❚ Пауза'}}else{{a.pause();b.textContent='▶ Прослушать'}}a.onended=()=>b.textContent='▶ Прослушать'}}
function foot(){{return `<footer><button class='back' onclick='back()' ${{index===0?'disabled':''}}>← Назад</button><button class='next' onclick='next()'>${{index===screens.length-1?'Завершить':'Далее →'}}</button></footer>`}}
function wrap(c,t){{return `<main class='shell'>${{side()}}<section class='work'>${{top(t)}}<div class='content'>${{c}}</div>${{foot()}}</section></main>`}}
function render(){{const s=screens[index];let c='';
if(s.kind==='cover')c=`<div class='split'><section class='card'><span class='badge'>1.1</span><h1>${{s.title}}</h1><p>${{s.subtitle}}</p>${{audio(s.audio)}}</section>${{pump()}}</div><div class='flow'><span>Источник</span><i></i><span class='hot'>Насос</span><i></i><span>Дом</span></div>`;
if(s.kind==='goals')c=`<section class='wide'><span class='badge'>Цель урока</span><h1>${{s.title}}</h1><div class='grid2'>${{s.items.map((x,i)=>`<div><b>0${{i+1}}</b><span>${{x}}</span></div>`).join('')}}</div>${{audio(s.audio)}}</section>`;
if(s.kind==='definition')c=`<div class='split'><section class='card'><span class='badge'>Базовое понятие</span><h1>${{s.title}}</h1><p>${{s.body}}</p><div class='note'><b>Запомните</b><span>${{s.note}}</span></div>${{audio(s.audio)}}</section>${{pump()}}</div>`;
if(s.kind==='flow')c=`<section class='wide'><span class='badge'>Принцип работы</span><h1>${{s.title}}</h1><div class='flowCards'><div><b>1</b><strong>Источник</strong><span>Скважина, колодец или ёмкость</span></div><i></i><div class='red'><b>2</b><strong>Насос</strong><span>Передаёт воде энергию</span></div><i></i><div><b>3</b><strong>Дом</strong><span>Точки водоразбора</span></div></div><p>${{s.body}}</p>${{audio(s.audio)}}</section>`;
if(s.kind==='applications')c=`<section class='wide'><span class='badge'>Применение</span><h1>${{s.title}}</h1><div class='grid3'>${{s.items.map((x,i)=>`<div><b>0${{i+1}}</b><strong>${{x[0]}}</strong><span>${{x[1]}}</span></div>`).join('')}}</div>${{audio(s.audio)}}</section>`;
if(s.kind==='tip')c=`<section class='wide tip'><span class='badge'>Практический совет</span><h1>${{s.title}}</h1><p>${{s.body}}</p><div class='grid3'>${{s.items.map(x=>`<div>✓ ${{x}}</div>`).join('')}}</div>${{audio(s.audio)}}</section>`;
if(s.kind==='quiz')c=`<section class='wide'><span class='badge'>Проверка</span><h1>${{s.title}}</h1><div class='answers'>${{s.answers.map((x,i)=>`<button onclick='answer(${{x[1]}})'>${{x[0]}}</button>`).join('')}}</div><div id='fb'></div>${{audio(s.audio)}}</section>`;
if(s.kind==='summary')c=`<section class='wide'><span class='badge'>Итоги</span><h1>${{s.title}}</h1><div class='list'>${{s.items.map(x=>`<div>✓ ${{x}}</div>`).join('')}}</div>${{audio(s.audio)}}</section>`;
app.innerHTML=wrap(c,s.title);scormSet(Math.round((index+1)/screens.length*100),index===screens.length-1?'completed':'incomplete')}}
function answer(ok){{answered=ok;const f=document.getElementById('fb');f.className=ok?'ok':'bad';f.textContent=ok?'Верно. Насос передаёт жидкости энергию.':'Неверно. Попробуйте ещё раз.'}}
function next(){{if(screens[index].kind==='quiz'&&!answered){{const f=document.getElementById('fb');f.className='bad';f.textContent='Сначала выберите правильный ответ.';return}}if(index<screens.length-1){{index++;render()}}else{{scormSet(100,'completed');scormFinish()}}}}
function back(){{if(index>0){{index--;render()}}}}
window.addEventListener('load',render);
"""
    (WORK/'app.js').write_text(app,encoding='utf-8')
    (WORK/'style.css').write_text(""":root{--r:#ef0712;--l:#e8e8e8;--s:#f5f5f5}*{box-sizing:border-box}html,body,#app{min-height:100%;margin:0}body{font-family:Arial,sans-serif;color:#111}.shell{min-height:100vh;display:grid;grid-template-columns:260px 1fr;background:#fafafa}aside{background:#fff;border-right:1px solid var(--l);padding:24px;display:flex;flex-direction:column}.logoImg{max-width:145px}.module{margin-top:34px;color:#777;font-weight:800}aside h2{font-size:27px;line-height:1.15;margin:8px 0 22px}nav{display:grid;gap:10px}nav button{width:100%;min-height:48px;padding:12px 14px;border:0;border-radius:14px;text-align:left;font-size:16px;background:#f1f1f1;color:#555;white-space:normal;overflow-wrap:anywhere}nav .active{background:var(--r);color:#fff;font-weight:800}.remember{margin-top:auto;border-left:6px solid var(--r);border-radius:16px;background:var(--s);padding:16px;display:grid;gap:8px}.work{display:flex;flex-direction:column;min-width:0;min-height:100vh}header{height:78px;background:#fff;border-bottom:1px solid var(--l);display:grid;grid-template-columns:250px minmax(180px,1fr) 55px 70px 70px;gap:18px;align-items:center;padding:0 28px}header small{display:block;color:#666}header strong{font-size:18px}.progress{height:9px;background:#e9e9e9;border-radius:999px;overflow:hidden}.progress i{display:block;height:100%;background:var(--r)}.content{width:min(1120px,calc(100% - 40px));margin:24px auto;flex:1;display:flex;flex-direction:column;justify-content:center}.split{display:grid;grid-template-columns:.95fr 1.15fr;gap:22px}.card,.pumpCard,.wide{background:#fff;border:1px solid var(--l);border-radius:24px;box-shadow:0 12px 34px rgba(0,0,0,.06)}.card,.wide{padding:30px}.pumpCard{min-height:470px;display:flex;align-items:center;justify-content:center}.pumpCard img{max-width:94%;max-height:430px;object-fit:contain}.badge{display:inline-block;background:var(--r);color:#fff;border-radius:13px;padding:8px 14px;font-weight:900}.card h1,.wide h1{font-size:clamp(38px,5vw,66px);line-height:1.02;margin:24px 0 20px}.card p,.wide p{font-size:21px;line-height:1.5;color:#444}.note{margin-top:22px;border-left:6px solid var(--r);background:var(--s);border-radius:16px;padding:16px;display:grid;gap:6px}.audioRow{margin-top:22px}.audioRow button{max-width:100%;min-width:190px;min-height:48px;padding:12px 18px;border:1px solid #ddd;border-radius:14px;background:#fff;font-size:17px;font-weight:800;white-space:normal;overflow-wrap:anywhere}.flow{display:flex;align-items:center;justify-content:center;gap:20px;margin-top:18px}.flow span{background:#fff;border:1px solid var(--l);border-radius:13px;padding:12px 18px;font-weight:800}.flow i{width:42px;height:4px;background:var(--r)}.flow .hot{background:var(--r);color:#fff}.grid2,.grid3,.list{display:grid;gap:14px}.grid2{grid-template-columns:1fr 1fr}.grid3{grid-template-columns:repeat(3,1fr)}.grid2 div,.grid3 div,.list div{background:var(--s);border-radius:17px;padding:18px;display:grid;gap:8px}.flowCards{display:grid;grid-template-columns:1fr 50px 1fr 50px 1fr;align-items:center;gap:10px;margin:28px 0}.flowCards div{min-height:165px;background:var(--s);border-radius:18px;padding:20px;display:flex;flex-direction:column;gap:8px}.flowCards .red{background:var(--r);color:#fff}.flowCards i{height:4px;background:var(--r)}.tip{border-left:8px solid var(--r)}.answers{display:grid;gap:12px}.answers button{width:100%;min-height:52px;padding:14px 18px;border:2px solid var(--l);border-radius:14px;background:#fff;text-align:left;font-size:18px;white-space:normal;overflow-wrap:anywhere}.answers button:hover{border-color:var(--r)}#fb{margin-top:14px;padding:14px;border-radius:12px;font-weight:800}#fb:empty{display:none}.ok{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}footer{height:74px;border-top:1px solid var(--l);background:#fff;display:flex;align-items:center;justify-content:space-between;padding:12px 28px;gap:12px}footer button{max-width:48%;min-width:145px;min-height:48px;padding:12px 20px;border:0;border-radius:14px;font-size:17px;font-weight:900;white-space:normal;overflow-wrap:anywhere}.back{background:#fff;border:1px solid #ddd}.next{background:var(--r);color:#fff}.back:disabled{opacity:.4}@media(max-width:900px){.shell{grid-template-columns:1fr}aside{display:none}header{grid-template-columns:1fr;height:auto;padding:16px}.content{width:calc(100% - 20px);margin:10px auto}.split,.grid2,.grid3{grid-template-columns:1fr}.flowCards{grid-template-columns:1fr}.flowCards i{width:100%}.flow{flex-wrap:wrap}.card,.wide{padding:22px}.card h1,.wide h1{font-size:40px}footer{padding:12px}footer button{min-width:0;width:48%;font-size:15px}}""",encoding='utf-8')

def pack():
    DIST.mkdir(parents=True,exist_ok=True)
    if OUT.exists(): OUT.unlink()
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for p in WORK.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(WORK).as_posix())

def main():
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True,exist_ok=True)
    cp(); manifest(); scorm(); files(); pack()
    print(f'OK: {OUT}')

if __name__=='__main__': main()
