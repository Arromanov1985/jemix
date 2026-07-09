#!/usr/bin/env python3
"""Build SCORM 1.2 package for JEMIX lesson 1.2.

Usage:
  python scripts/build_scorm_lesson_1_2.py

Optional assets:
  academy-assets/logo/jemix-logo.png
  academy-assets/pumps/jemix-pump.png

Output:
  dist/module-01/JEMIX_Lesson_1_2_SCORM.zip
"""
from __future__ import annotations
import shutil, zipfile
from pathlib import Path

ROOT=Path('.')
WORK=ROOT/'_scorm_lesson_1_2'
DIST=ROOT/'dist'/'module-01'
OUT=DIST/'JEMIX_Lesson_1_2_SCORM.zip'
LOGO_SRC=ROOT/'academy-assets'/'logo'/'jemix-logo.png'
PUMP_SRC=ROOT/'academy-assets'/'pumps'/'jemix-pump.png'
AUDIO_SRC=ROOT/'voice'/'modules'/'module-01'/'lesson-1.2'/'audio'

SLIDES=[
  {'title':'Основные характеристики насоса','body':'В этом уроке разберем четыре параметра, которые чаще всего нужны менеджеру при разговоре с клиентом: расход, напор, мощность и рабочие условия.','tag':'Старт урока','audio':'slide01.mp3'},
  {'title':'Расход','body':'Расход показывает, сколько воды насос способен подать за единицу времени. Для клиента это означает: хватит ли воды на душ, кухню, полив и другие точки одновременно.','tag':'Параметр 1','audio':'slide02.mp3'},
  {'title':'Напор','body':'Напор показывает, на какую высоту и с каким запасом насос может перемещать воду. При подборе важно учитывать глубину источника, расстояние до дома и требуемое давление.','tag':'Параметр 2','audio':'slide03.mp3'},
  {'title':'Мощность','body':'Мощность не выбирают отдельно от задачи. Более мощный насос не всегда лучше: он может быть дороже, шумнее и работать не в оптимальном режиме.','tag':'Параметр 3','audio':'slide04.mp3'},
  {'title':'Рабочие условия','body':'На подбор влияют источник воды, глубина, длина трассы, количество точек водоразбора и сценарий использования: дом, дача, полив или хозяйственные нужды.','tag':'Параметр 4','audio':'slide05.mp3'},
]


def copy_assets():
    img=WORK/'img'; img.mkdir(parents=True,exist_ok=True)
    if LOGO_SRC.exists(): shutil.copy2(LOGO_SRC,img/'jemix-logo.png')
    if PUMP_SRC.exists(): shutil.copy2(PUMP_SRC,img/'jemix-pump.png')
    aud=WORK/'audio'; aud.mkdir(parents=True,exist_ok=True)
    for s in SLIDES:
        src=AUDIO_SRC/s['audio']
        if src.exists(): shutil.copy2(src,aud/s['audio'])

def manifest():
    (WORK/'imsmanifest.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_LESSON_1_2" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Lesson 1.2</title><item identifier="ITEM1" identifierref="RES1"><title>Основные характеристики насоса</title></item></organization></organizations>
  <resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html"><file href="index.html"/><file href="style.css"/><file href="app.js"/><file href="scorm.js"/></resource></resources>
</manifest>''',encoding='utf-8')

def scorm():
    (WORK/'scorm.js').write_text(r"""
function findAPI(w){let n=0;while(w&&n<500){if(w.API)return w.API;n++;if(w.parent===w)break;w=w.parent}return null}
var API=findAPI(window)||(window.opener?findAPI(window.opener):null),scormReady=false;
function scormInit(){if(!API)return false;try{scormReady=API.LMSInitialize("")==="true";if(scormReady){API.LMSSetValue("cmi.core.lesson_status","incomplete");API.LMSCommit("")}return scormReady}catch(e){return false}}
function scormSet(score,status){if(!API||!scormReady)return;try{API.LMSSetValue("cmi.core.score.raw",String(score));API.LMSSetValue("cmi.core.lesson_status",status);API.LMSCommit("")}catch(e){}}
function scormFinish(){if(!API||!scormReady)return;try{API.LMSCommit("");API.LMSFinish("")}catch(e){}}
window.addEventListener('load',scormInit);window.addEventListener('beforeunload',scormFinish);
""".strip(),encoding='utf-8')

def jsq(s:str)->str: return s.replace('\\','\\\\').replace('`','\\`').replace('${','\\${')

def html_js():
    (WORK/'index.html').write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy - Урок 1.2</title><link rel="stylesheet" href="style.css"></head><body><div id="app"></div><script src="scorm.js"></script><script src="app.js"></script></body></html>',encoding='utf-8')
    data=',\n'.join(f"{{title:`{jsq(x['title'])}`,body:`{jsq(x['body'])}`,tag:`{jsq(x['tag'])}`,audio:`audio/{x['audio']}`}}" for x in SLIDES)
    (WORK/'app.js').write_text(f"""
const slides=[{data}];let current=-1;const app=document.getElementById('app');
function esc(s){{return String(s||'').replace(/[&<>\"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[c]));}}
function logo(){{return `<img src="img/jemix-logo.png" onerror="this.replaceWith(Object.assign(document.createElement('b'),{{textContent:'JEMIX'}}))">`;}}
function pump(){{return `<div class="pumpPhoto"><img src="img/jemix-pump.png" onerror="this.remove();this.parentNode.classList.add('fallback')"><span>JEMIX</span></div>`;}}
function pr(){{return current<0?0:Math.round(((current+1)/(slides.length+2))*100)}}
function side(){{return `<div class="sideLogo">${{logo()}}</div><div class="sideTitle">Academy</div><nav><b>1.1 Что такое насос</b><b class="active">1.2 Характеристики</b><b>1.3 Устройство</b><b>1.4 Виды насосов</b></nav>`}}
function head(p,t){{return `<div><strong>${{t}}</strong><span>JEMIX Academy</span></div><div class="bar"><i style="width:${{p}}%"></i></div><em>${{p}}%</em>`}}
function cover(){{current=-1;app.innerHTML=`<main class="cover"><section class="hero"><div class="heroLeft"><div class="topLogo">${{logo()}}</div><div class="label">Модуль 1 / Урок 1.2</div><h1>Основные характеристики насоса</h1><p>Разбираем параметры, которые нужны для первичного подбора и понятного объяснения клиенту.</p><div class="chips"><span>7 минут</span><span>7 экранов</span><span>Озвучка</span></div><button onclick="goals()">Начать обучение</button></div><div class="heroRight">${{pump()}}<div class="photoNote">Фото подтягивается из academy-assets/pumps/jemix-pump.png</div></div></section></main>`}}
function goals(){{app.innerHTML=`<main class="player"><aside>${{side()}}</aside><section class="stage"><header>${{head(12,'Цель урока')}}</header><div class="goals"><h1>После урока вы сможете</h1><div><b>01</b><span>Объяснить разницу между расходом и напором</span></div><div><b>02</b><span>Понять, почему мощность не выбирают первой</span></div><div><b>03</b><span>Задать клиенту правильные вопросы перед подбором</span></div><div><b>04</b><span>Не путать технические характеристики с задачей клиента</span></div></div><footer><button onclick="cover()">Назад</button><button onclick="start()">Далее</button></footer></section></main>`}}
function start(){{current=0;render();scormSet(15,'incomplete')}}
function next(){{if(current<slides.length-1){{current++;render();scormSet(pr(),'incomplete')}}else scenario()}}
function prev(){{if(current>0){{current--;render()}}else goals()}}
function audio(src){{return `<div class="listen"><button onclick="this.nextElementSibling.play()">Прослушать</button><audio controls src="${{src}}"></audio></div>`}}
function render(){{const s=slides[current],p=pr();app.innerHTML=`<main class="player"><aside>${{side()}}</aside><section class="stage"><header>${{head(p,'Урок 1.2')}}</header><div class="lesson"><div class="visual">${{pump()}}<div class="metrics"><b>Расход</b><b>Напор</b><b>Мощность</b><b>Условия</b></div></div><article><div class="tag">${{esc(s.tag)}}</div><h1>${{esc(s.title)}}</h1><p>${{esc(s.body)}}</p><div class="tip"><strong>Правило менеджера</strong><br>Сначала выясняем задачу клиента, затем смотрим характеристики подходящей модели.</div>${{audio(s.audio)}}</article></div><footer><button onclick="prev()">Назад</button><button onclick="next()">Далее</button></footer></section></main>`}}
function scenario(){{app.innerHTML=`<main class="player"><aside>${{side()}}</aside><section class="stage"><header>${{head(82,'Практика')}}</header><div class="case"><h1>Клиент говорит: нужен насос для дома</h1><p>Что спросить первым, чтобы не ошибиться с подбором?</p><button onclick="bad()">Какой бюджет?</button><button onclick="goodCase()">Источник воды, глубину и количество точек</button><button onclick="bad()">Самую мощную модель?</button><button onclick="bad()">Цвет и размер корпуса?</button><div id="fb"></div></div></section></main>`}}
function quiz(){{app.innerHTML=`<main class="player"><aside>${{side()}}</aside><section class="stage"><header>${{head(92,'Мини-тест')}}</header><div class="quiz"><h1>Что показывает расход?</h1><button onclick="good()">Сколько воды насос подает за единицу времени</button><button onclick="bad()">Высоту корпуса насоса</button><button onclick="bad()">Электрическую мощность двигателя</button><button onclick="bad()">Цвет оборудования</button><div id="fb"></div></div></section></main>`}}
function goodCase(){{document.getElementById('fb').innerHTML='<div class="ok">Верно. Сначала нужна задача и исходные условия.</div><button class="nextIn" onclick="quiz()">Перейти к тесту</button>'}}
function good(){{document.getElementById('fb').innerHTML='<div class="ok">Верно. Урок завершен.</div>';scormSet(100,'completed');setTimeout(done,800)}}
function bad(){{document.getElementById('fb').innerHTML='<div class="bad">Неверно. Для подбора сначала нужны исходные условия и задача клиента.</div>'}}
function done(){{app.innerHTML=`<main class="cover"><section class="hero finish"><div class="heroLeft"><div class="topLogo">${{logo()}}</div><h1>Урок 1.2 завершен</h1><p>Результат передан в Бруснику.</p><button onclick="scormFinish()">Завершить</button></div></section></main>`}}
window.addEventListener('load',cover);
""",encoding='utf-8')

def css():
    (WORK/'style.css').write_text(r"""
:root{--red:#e30613;--black:#111;--muted:#6b6b6b;--line:#e8e8e8;--soft:#f6f6f6}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#fff;color:var(--black)}button{font-family:inherit;cursor:pointer;border:0}.cover{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:22px;background:#fff}.hero{width:min(1050px,100%);min-height:540px;display:grid;grid-template-columns:1fr .9fr;gap:36px;border:1px solid var(--line);border-radius:28px;padding:44px;background:linear-gradient(135deg,#fff,#f7f7f7);box-shadow:0 22px 70px rgba(0,0,0,.10)}.topLogo img,.sideLogo img{display:block;max-width:153px;height:auto}.topLogo b,.sideLogo b{font-size:36px;font-weight:950}.label{margin-top:30px;border-left:7px solid var(--red);padding-left:14px;font-weight:900;color:#333}.hero h1{font-size:clamp(42px,6vw,76px);line-height:.98;margin:24px 0 18px}.hero p{font-size:21px;line-height:1.45;color:#555}.chips{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}.chips span{background:#eee;border-radius:999px;padding:10px 14px;font-weight:800}.hero button,footer button:last-child,.listen button,.nextIn{background:var(--red);color:#fff;border-radius:999px;padding:15px 24px;font-size:17px;font-weight:950}.heroRight{display:flex;flex-direction:column;justify-content:center}.pumpPhoto{min-height:280px;border-radius:26px;background:#171717;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}.pumpPhoto img{max-width:92%;max-height:300px;object-fit:contain;z-index:2}.pumpPhoto span{display:none;color:#fff;font-weight:950;font-size:42px}.pumpPhoto.fallback span{display:block}.pumpPhoto:after{content:'';position:absolute;right:-40px;bottom:-55px;width:190px;height:190px;background:var(--red);border-radius:50%}.photoNote{font-size:13px;color:#777;margin-top:12px}.player{min-height:100vh;display:grid;grid-template-columns:250px 1fr;background:#fafafa}aside{background:#fff;border-right:1px solid var(--line);padding:24px}.sideTitle{font-size:22px;font-weight:900;margin-top:8px}.sideLogo img{max-width:132px}nav{display:grid;gap:10px;margin-top:34px}nav b{background:#f3f3f3;border-radius:14px;padding:13px 14px;color:#666}nav b.active{background:var(--red);color:#fff}.stage{display:flex;flex-direction:column;min-width:0}header{height:78px;background:#fff;border-bottom:1px solid var(--line);display:grid;grid-template-columns:220px 1fr 60px;gap:18px;align-items:center;padding:0 24px}header strong{font-size:20px}header span{display:block;color:#777;margin-top:4px}.bar{height:9px;background:#ededed;border-radius:999px;overflow:hidden}.bar i{display:block;height:100%;background:var(--red)}header em{font-style:normal;font-weight:950}.lesson{width:min(1000px,calc(100% - 40px));margin:24px auto;display:grid;grid-template-columns:.95fr 1.05fr;gap:22px}.visual,article,.quiz,.case,.goals{background:#fff;border:1px solid var(--line);border-radius:24px;padding:28px;box-shadow:0 14px 42px rgba(0,0,0,.06)}.visual{display:flex;flex-direction:column;justify-content:center}.metrics{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:18px}.metrics b{background:#f2f2f2;border-radius:14px;padding:14px;text-align:center}.tag{display:inline-block;background:#111;color:#fff;border-radius:999px;padding:8px 13px;font-weight:900;margin-bottom:16px}article h1,.quiz h1,.case h1,.goals h1{font-size:clamp(30px,4.5vw,52px);line-height:1.08;margin:0 0 18px}article p,.case p{font-size:21px;line-height:1.5;color:#444}.tip{border-left:7px solid var(--red);background:#f6f6f6;border-radius:16px;padding:16px;font-size:18px;line-height:1.45}.listen{margin-top:18px;background:#f6f6f6;border-radius:16px;padding:14px}.listen audio{width:100%;margin-top:10px}.goals,.case,.quiz{width:min(850px,calc(100% - 40px));margin:28px auto}.goals div{display:grid;grid-template-columns:60px 1fr;gap:15px;align-items:center;border-top:1px solid var(--line);padding:18px 0}.goals b{color:var(--red);font-size:24px}.goals span{font-size:22px;font-weight:800}.case button,.quiz button{display:block;width:100%;background:#fff;border:2px solid var(--line);border-radius:16px;text-align:left;padding:17px 20px;margin:12px 0;font-size:20px}.case button:hover,.quiz button:hover{border-color:var(--red)}.ok,.bad{margin-top:16px;border-radius:14px;padding:16px;font-weight:900}.ok{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}footer{margin-top:auto;height:78px;background:#fff;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;padding:0 24px}footer button{border-radius:999px;padding:14px 23px;font-size:17px;font-weight:950}footer button:first-child{background:#eee;color:#222}@media(max-width:900px){.hero,.lesson{grid-template-columns:1fr}.player{grid-template-columns:1fr}aside{display:none}header{grid-template-columns:1fr;height:auto;padding:16px}.hero{padding:28px}.hero h1{font-size:42px}}
""".strip(),encoding='utf-8')

def pack():
    DIST.mkdir(parents=True,exist_ok=True)
    if OUT.exists(): OUT.unlink()
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for p in WORK.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(WORK).as_posix())

def main():
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True,exist_ok=True)
    copy_assets(); manifest(); scorm(); html_js(); css(); pack()
    print(f'OK: {OUT}')
if __name__=='__main__': main()
