#!/usr/bin/env python3
"""Build SCORM 1.2 package for JEMIX lesson 1.1.

Usage:
  python scripts/build_scorm_lesson_1_1.py

Optional assets:
  academy-assets/logo/jemix-logo.png
  academy-assets/pumps/jemix-pump.png

Output:
  dist/module-01/JEMIX_Lesson_1_1_SCORM.zip
"""
from __future__ import annotations
import re, shutil, zipfile
from pathlib import Path

ROOT=Path('.')
MODULE='module-01'
LESSON='lesson-1.1'
WORK=ROOT/'_scorm_lesson_1_1'
DIST=ROOT/'dist'/MODULE
OUT=DIST/'JEMIX_Lesson_1_1_SCORM.zip'
SRC=ROOT/'voice'/'modules'/MODULE/LESSON
LOGO_SRC=ROOT/'academy-assets'/'logo'/'jemix-logo.png'
PUMP_SRC=ROOT/'academy-assets'/'pumps'/'jemix-pump.png'

META_RE=re.compile(r'^(type|ux_title|goal|title|layout|screen|id)\s*[:=]',re.I)

def clean(t:str)->str:
    lines=[]
    for line in t.splitlines():
        x=line.strip()
        if not x or META_RE.match(x): continue
        x=re.sub(r'^#+\s*','',x).replace('**','')
        x=x.replace('—','-').replace('–','-').replace('▶','').strip()
        if x.lower() in ('goal','ux_title','type'): continue
        lines.append(x)
    return ' '.join(lines)

def read_slide(n:int)->tuple[str,str]:
    p=SRC/f'slide{n:02d}.md'
    defaults={
        1:('Что такое насос?','Насос - это гидравлическая машина, которая передает жидкости энергию. Благодаря этому вода движется от источника к потребителю.'),
        2:('Главная задача насоса','Насос не создает воду. Он создает условия для движения воды: расход, напор и стабильную работу системы.'),
        3:('Что важно запомнить','Подбор насоса начинается не с мощности и не с цены. Сначала нужно понять задачу клиента, источник воды и требуемый расход.'),
    }
    if not p.exists(): return defaults.get(n,(f'Экран {n}','Материал урока.'))
    lines=p.read_text(encoding='utf-8').splitlines()
    title=clean(lines[0]) if lines else defaults[n][0]
    body=clean('\n'.join(lines[1:])) or defaults[n][1]
    parts=re.split(r'(?<=[.!?])\s+',body)
    return title,' '.join(parts[:3])

def copy_assets():
    img=WORK/'img'; img.mkdir(parents=True,exist_ok=True)
    if LOGO_SRC.exists(): shutil.copy2(LOGO_SRC,img/'jemix-logo.png')
    if PUMP_SRC.exists(): shutil.copy2(PUMP_SRC,img/'jemix-pump.png')

def copy_audio(n:int)->str:
    src=SRC/'audio'/f'slide{n:02d}.mp3'
    if not src.exists(): return ''
    d=WORK/'audio'; d.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,d/src.name)
    return f'audio/{src.name}'

def write_manifest():
    (WORK/'imsmanifest.xml').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_LESSON_1_1" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Lesson 1.1</title><item identifier="ITEM1" identifierref="RES1"><title>Что такое насос</title></item></organization></organizations>
  <resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html"><file href="index.html"/><file href="style.css"/><file href="app.js"/><file href="scorm.js"/></resource></resources>
</manifest>''',encoding='utf-8')

def write_scorm():
    (WORK/'scorm.js').write_text(r"""
function findAPI(w){let n=0;while(w&&n<500){if(w.API)return w.API;n++;if(w.parent===w)break;w=w.parent}return null}
var API=findAPI(window)||(window.opener?findAPI(window.opener):null),scormReady=false;
function scormInit(){if(!API)return false;try{scormReady=API.LMSInitialize("")==="true";if(scormReady){API.LMSSetValue("cmi.core.lesson_status","incomplete");API.LMSCommit("")}return scormReady}catch(e){return false}}
function scormSet(score,status){if(!API||!scormReady)return;try{API.LMSSetValue("cmi.core.score.raw",String(score));API.LMSSetValue("cmi.core.lesson_status",status);API.LMSCommit("")}catch(e){}}
function scormFinish(){if(!API||!scormReady)return;try{API.LMSCommit("");API.LMSFinish("")}catch(e){}}
window.addEventListener('load',scormInit);window.addEventListener('beforeunload',scormFinish);
""".strip(),encoding='utf-8')

def jsq(s:str)->str: return s.replace('\\','\\\\').replace('`','\\`').replace('${','\\${')

def write_html_js():
    slides=[]
    for i in range(1,4):
        title,body=read_slide(i); slides.append({'title':title,'body':body,'audio':copy_audio(i)})
    data=',\n'.join(f"{{title:`{jsq(s['title'])}`,body:`{jsq(s['body'])}`,audio:`{s['audio']}`}}" for s in slides)
    (WORK/'index.html').write_text('''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy - Урок 1.1</title><link rel="stylesheet" href="style.css"></head><body><div id="app"></div><script src="scorm.js"></script><script src="app.js"></script></body></html>''',encoding='utf-8')
    (WORK/'app.js').write_text(f"""
const slides=[{data}];let current=-1;const app=document.getElementById('app');
function esc(s){{return String(s||'').replace(/[&<>\"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[c]));}}
function logo(){{return `<img src="img/jemix-logo.png" onerror="this.replaceWith(Object.assign(document.createElement('b'),{{textContent:'JEMIX'}}))">`;}}
function pump(){{return `<div class="pumpPhoto"><img src="img/jemix-pump.png" onerror="this.remove();this.parentNode.classList.add('fallback')"><span>JEMIX</span></div>`;}}
function p(){{return current<0?0:Math.round(((current+1)/(slides.length+2))*100)}}
function start(){{current=0;render();scormSet(12,'incomplete')}}
function next(){{if(current<slides.length-1){{current++;render();scormSet(p(),'incomplete')}}else flow()}}
function prev(){{if(current>0){{current--;render()}}else cover()}}
function cover(){{current=-1;app.innerHTML=`<main class="cover"><section class="hero"><div class="heroLeft"><div class="topLogo">${{logo()}}</div><div class="label">Модуль 1 / Урок 1.1</div><h1>Что такое насос?</h1><p>Короткий первый урок: принцип работы насоса, понятная схема и мини-проверка.</p><div class="chips"><span>6 минут</span><span>5 экранов</span><span>Озвучка</span></div><button onclick="start()">Начать обучение</button></div><div class="heroRight">${{pump()}}<div class="photoNote">Используется оригинальный логотип. Фото насоса подтягивается из academy-assets/pumps/jemix-pump.png</div></div></section></main>`}}
function goals(){{app.innerHTML=`<main class="player"><aside>${{side()}}</aside><section class="stage"><header>${{head(18,'Цель урока')}}</header><div class="goals"><h1>После урока вы сможете</h1><div><b>01</b><span>Объяснить клиенту, что такое насос</span></div><div><b>02</b><span>Понять, зачем насос нужен в системе</span></div><div><b>03</b><span>Отличать насос от других элементов водоснабжения</span></div><div><b>04</b><span>Подготовиться к подбору оборудования JEMIX</span></div></div><footer><button onclick="cover()">Назад</button><button onclick="start()">Далее</button></footer></section></main>`}}
function side(){{return `<div class="sideLogo">${{logo()}}</div><div class="sideTitle">Academy</div><nav><b class="active">1.1 Что такое насос</b><b>1.2 Применение</b><b>1.3 Устройство</b></nav>`}}
function head(pr,title){{return `<div><strong>${{title}}</strong><span>JEMIX Academy</span></div><div class="bar"><i style="width:${{pr}}%"></i></div><em>${{pr}}%</em>`}}
function render(){{const s=slides[current],pr=p();app.innerHTML=`<main class="player"><aside>${{side()}}</aside><section class="stage"><header>${{head(pr,'Урок 1.1')}}</header><div class="lesson"><div class="visual">${{pump()}}<div class="chain"><b>Источник</b><i></i><b>Насос</b><i></i><b>Дом</b></div></div><article><div class="tag">Экран ${{current+1}} из ${{slides.length}}</div><h1>${{esc(s.title)}}</h1><p>${{esc(s.body)}}</p><div class="tip"><strong>Запомните</strong><br>Насос не создает воду. Он передает воде энергию.</div>${{audio(s.audio)}}</article></div><footer><button onclick="prev()">Назад</button><button onclick="next()">Далее</button></footer></section></main>`}}
function audio(src){{if(!src)return `<button class="listen disabled">Озвучка не найдена</button>`;return `<div class="listen"><button onclick="this.nextElementSibling.play()">Прослушать</button><audio controls src="${{src}}"></audio></div>`}}
function flow(){{app.innerHTML=`<main class="player"><aside>${{side()}}</aside><section class="stage"><header>${{head(78,'Как работает связка')}}</header><div class="flowScreen"><h1>Связка: источник - насос - дом</h1><div class="flowBig"><div><b>1</b><strong>Источник</strong><span>Скважина, колодец или емкость</span></div><i></i><div class="red"><b>2</b><strong>Насос</strong><span>Передает воде энергию</span></div><i></i><div><b>3</b><strong>Дом</strong><span>Точки водоразбора</span></div></div><p>Насос находится в середине системы: он забирает воду из источника и помогает доставить ее к потребителю.</p></div><footer><button onclick="current=slides.length-1;render()">Назад</button><button onclick="quiz()">Проверка</button></footer></section></main>`}}
function quiz(){{app.innerHTML=`<main class="player"><aside>${{side()}}</aside><section class="stage"><header>${{head(90,'Мини-тест')}}</header><div class="quiz"><h1>Что делает насос?</h1><button onclick="bad()">Очищает воду</button><button onclick="good()">Передает жидкости энергию</button><button onclick="bad()">Хранит воду</button><button onclick="bad()">Охлаждает воду</button><div id="fb"></div></div></section></main>`}}
function good(){{document.getElementById('fb').innerHTML='<div class="ok">Верно. Урок завершен.</div>';scormSet(100,'completed');setTimeout(done,800)}}
function bad(){{document.getElementById('fb').innerHTML='<div class="bad">Неверно. Насос передает жидкости энергию.</div>'}}
function done(){{app.innerHTML=`<main class="cover"><section class="hero finish"><div class="heroLeft"><div class="topLogo">${{logo()}}</div><h1>Урок завершен</h1><p>Результат передан в Бруснику.</p><button onclick="scormFinish()">Завершить</button></div></section></main>`}}
window.addEventListener('load',cover);
""",encoding='utf-8')

def write_css():
    (WORK/'style.css').write_text(r"""
:root{--red:#e30613;--black:#111;--muted:#6b6b6b;--line:#e8e8e8;--soft:#f6f6f6}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#fff;color:var(--black)}button{font-family:inherit;cursor:pointer;border:0}.cover{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:22px;background:#fff}.hero{width:min(1050px,100%);min-height:540px;display:grid;grid-template-columns:1fr .9fr;gap:36px;border:1px solid var(--line);border-radius:28px;padding:44px;background:linear-gradient(135deg,#fff,#f7f7f7);box-shadow:0 22px 70px rgba(0,0,0,.10)}.topLogo img,.sideLogo img{display:block;max-width:153px;height:auto}.topLogo b,.sideLogo b{font-size:36px;font-weight:950}.label{margin-top:30px;border-left:7px solid var(--red);padding-left:14px;font-weight:900;color:#333}.hero h1{font-size:clamp(42px,6vw,78px);line-height:.98;margin:24px 0 18px}.hero p{font-size:21px;line-height:1.45;color:#555}.chips{display:flex;gap:10px;flex-wrap:wrap;margin:24px 0}.chips span{background:#eee;border-radius:999px;padding:10px 14px;font-weight:800}.hero button,footer button:last-child,.listen button{background:var(--red);color:#fff;border-radius:999px;padding:15px 24px;font-size:17px;font-weight:950}.heroRight{display:flex;flex-direction:column;justify-content:center}.pumpPhoto{min-height:280px;border-radius:26px;background:#171717;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}.pumpPhoto img{max-width:92%;max-height:300px;object-fit:contain;z-index:2}.pumpPhoto span{display:none;color:#fff;font-weight:950;font-size:42px}.pumpPhoto.fallback span{display:block}.pumpPhoto:after{content:'';position:absolute;right:-40px;bottom:-55px;width:190px;height:190px;background:var(--red);border-radius:50%}.photoNote{font-size:13px;color:#777;margin-top:12px}.player{min-height:100vh;display:grid;grid-template-columns:250px 1fr;background:#fafafa}aside{background:#fff;border-right:1px solid var(--line);padding:24px}.sideTitle{font-size:22px;font-weight:900;margin-top:8px}.sideLogo img{max-width:132px}nav{display:grid;gap:10px;margin-top:34px}nav b{background:#f3f3f3;border-radius:14px;padding:13px 14px;color:#666}nav b.active{background:var(--red);color:#fff}.stage{display:flex;flex-direction:column;min-width:0}header{height:78px;background:#fff;border-bottom:1px solid var(--line);display:grid;grid-template-columns:220px 1fr 60px;gap:18px;align-items:center;padding:0 24px}header strong{font-size:20px}header span{display:block;color:#777;margin-top:4px}.bar{height:9px;background:#ededed;border-radius:999px;overflow:hidden}.bar i{display:block;height:100%;background:var(--red)}header em{font-style:normal;font-weight:950}.lesson{width:min(1000px,calc(100% - 40px));margin:24px auto;display:grid;grid-template-columns:.95fr 1.05fr;gap:22px}.visual,article,.quiz,.flowScreen,.goals{background:#fff;border:1px solid var(--line);border-radius:24px;padding:28px;box-shadow:0 14px 42px rgba(0,0,0,.06)}.visual{display:flex;flex-direction:column;justify-content:center}.chain{display:flex;align-items:center;justify-content:center;gap:10px;margin-top:22px;flex-wrap:wrap}.chain b{background:#f2f2f2;border-radius:12px;padding:12px 14px;font-size:15px}.chain i{width:26px;height:3px;background:var(--red);border-radius:999px}.tag{display:inline-block;background:#111;color:#fff;border-radius:999px;padding:8px 13px;font-weight:900;margin-bottom:16px}article h1,.quiz h1,.flowScreen h1,.goals h1{font-size:clamp(30px,4.5vw,52px);line-height:1.08;margin:0 0 18px}article p,.flowScreen p{font-size:21px;line-height:1.5;color:#444}.tip{border-left:7px solid var(--red);background:#f6f6f6;border-radius:16px;padding:16px;font-size:18px;line-height:1.45}.listen{margin-top:18px;background:#f6f6f6;border-radius:16px;padding:14px}.listen audio{width:100%;margin-top:10px}.listen.disabled{background:#eee;color:#555;border-radius:999px;padding:14px 20px}.goals{width:min(900px,calc(100% - 40px));margin:28px auto}.goals div{display:grid;grid-template-columns:60px 1fr;gap:15px;align-items:center;border-top:1px solid var(--line);padding:18px 0}.goals b{color:var(--red);font-size:24px}.goals span{font-size:22px;font-weight:800}.flowScreen{width:min(1000px,calc(100% - 40px));margin:28px auto}.flowBig{display:grid;grid-template-columns:1fr 60px 1fr 60px 1fr;align-items:center;gap:10px;margin:26px 0}.flowBig div{background:#f5f5f5;border-radius:20px;padding:22px;min-height:170px}.flowBig .red{background:var(--red);color:#fff}.flowBig b{display:block;font-size:30px}.flowBig strong{display:block;font-size:24px;margin:10px 0}.flowBig span{font-size:16px}.flowBig i{height:5px;background:var(--red);border-radius:999px}.quiz{width:min(800px,calc(100% - 40px));margin:38px auto}.quiz button{display:block;width:100%;background:#fff;border:2px solid var(--line);border-radius:16px;text-align:left;padding:17px 20px;margin:12px 0;font-size:20px}.quiz button:hover{border-color:var(--red)}.ok,.bad{margin-top:16px;border-radius:14px;padding:16px;font-weight:900}.ok{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}footer{margin-top:auto;height:78px;background:#fff;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;padding:0 24px}footer button{border-radius:999px;padding:14px 23px;font-size:17px;font-weight:950}footer button:first-child{background:#eee;color:#222}@media(max-width:900px){.hero,.lesson{grid-template-columns:1fr}.player{grid-template-columns:1fr}aside{display:none}header{grid-template-columns:1fr;height:auto;padding:16px}.flowBig{grid-template-columns:1fr}.flowBig i{height:4px}.hero{padding:28px}.hero h1{font-size:42px}}
""".strip(),encoding='utf-8')

def zip_out():
    DIST.mkdir(parents=True,exist_ok=True)
    if OUT.exists(): OUT.unlink()
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for p in WORK.rglob('*'):
            if p.is_file(): z.write(p,p.relative_to(WORK).as_posix())

def main():
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True,exist_ok=True)
    copy_assets(); write_manifest(); write_scorm(); write_html_js(); write_css(); zip_out()
    print(f'OK: {OUT}')

if __name__=='__main__': main()
