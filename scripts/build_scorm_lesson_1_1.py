#!/usr/bin/env python3
"""Build the approved 8-screen SCORM 1.2 lesson 1.1.

Usage:
  python scripts/build_scorm_lesson_1_1.py

Required assets:
  academy-assets/logo/jemix-logo.png
  academy-assets/pumps/jemix-pump.png

Audio:
  voice/modules/module-01/lesson-1.1/audio/slide01.mp3 ... slide08.mp3

Output:
  dist/module-01/JEMIX_Lesson_1_1_SCORM.zip
"""
from __future__ import annotations
import shutil
import zipfile
from pathlib import Path

ROOT = Path('.')
WORK = ROOT / '_scorm_lesson_1_1'
DIST = ROOT / 'dist' / 'module-01'
OUT = DIST / 'JEMIX_Lesson_1_1_SCORM.zip'
LOGO_SRC = ROOT / 'academy-assets' / 'logo' / 'jemix-logo.png'
PUMP_SRC = ROOT / 'academy-assets' / 'pumps' / 'jemix-pump.png'
AUDIO_SRC = ROOT / 'voice' / 'modules' / 'module-01' / 'lesson-1.1' / 'audio'

SCREENS = [
    {
        'kind': 'cover',
        'title': 'Что такое насос?',
        'subtitle': 'Первый урок Академии JEMIX: базовое понятие, принцип работы и применение.',
        'audio': 'slide01.mp3',
    },
    {
        'kind': 'goals',
        'title': 'После урока вы сможете',
        'items': [
            'Объяснить, что такое насос',
            'Понять, зачем насос нужен в системе',
            'Назвать основные области применения',
            'Подготовиться к дальнейшему подбору оборудования',
        ],
        'audio': 'slide02.mp3',
    },
    {
        'kind': 'definition',
        'title': 'Что такое насос',
        'body': 'Насос не создаёт воду, а перемещает жидкость внутри системы.',
        'note': 'Насос не создаёт воду. Он передаёт воде энергию.',
        'audio': 'slide03.mp3',
    },
    {
        'kind': 'flow',
        'title': 'Источник — насос — дом',
        'body': 'Насос находится между источником и потребителем: забирает воду и помогает доставить её к точкам водоразбора.',
        'audio': 'slide04.mp3',
    },
    {
        'kind': 'applications',
        'title': 'Где применяются насосы',
        'items': [
            ['Частный дом', 'Водоснабжение кухни, душа и других точек.'],
            ['Дача и полив', 'Подача воды из колодца, ёмкости или другого источника.'],
            ['Хозяйственные задачи', 'Перекачивание воды и работа в инженерных системах.'],
        ],
        'audio': 'slide05.mp3',
    },
    {
        'kind': 'tip',
        'title': 'Совет инженера',
        'body': 'Не начинайте подбор с мощности насоса.',
        'items': ['Источник воды', 'Требуемый расход', 'Необходимый напор'],
        'audio': 'slide06.mp3',
    },
    {
        'kind': 'quiz',
        'title': 'Что делает насос?',
        'answers': [
            ['Создаёт воду', False],
            ['Передаёт жидкости энергию', True],
            ['Только очищает воду', False],
            ['Хранит запас воды', False],
        ],
        'audio': 'slide07.mp3',
    },
    {
        'kind': 'summary',
        'title': 'Главное из урока',
        'items': [
            'Насос — гидравлическая машина',
            'Он передаёт жидкости энергию',
            'Насос связывает источник воды и потребителя',
        ],
        'audio': 'slide08.mp3',
    },
]


def copy_assets() -> None:
    img = WORK / 'img'
    img.mkdir(parents=True, exist_ok=True)
    if LOGO_SRC.exists():
        shutil.copy2(LOGO_SRC, img / 'jemix-logo.png')
    if PUMP_SRC.exists():
        shutil.copy2(PUMP_SRC, img / 'jemix-pump.png')
    audio = WORK / 'audio'
    audio.mkdir(parents=True, exist_ok=True)
    for screen in SCREENS:
        src = AUDIO_SRC / screen['audio']
        if src.exists():
            shutil.copy2(src, audio / src.name)


def write_manifest() -> None:
    files = ['index.html', 'style.css', 'app.js', 'scorm.js']
    file_nodes = ''.join(f'<file href="{x}"/>' for x in files)
    (WORK / 'imsmanifest.xml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_LESSON_1_1" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Lesson 1.1</title><item identifier="ITEM1" identifierref="RES1"><title>Что такое насос</title></item></organization></organizations>
  <resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">{file_nodes}</resource></resources>
</manifest>''', encoding='utf-8')


def write_scorm() -> None:
    (WORK / 'scorm.js').write_text(r'''
function findAPI(w){let n=0;while(w&&n<500){if(w.API)return w.API;n++;if(w.parent===w)break;w=w.parent}return null}
var API=findAPI(window)||(window.opener?findAPI(window.opener):null),scormReady=false;
function scormInit(){if(!API)return false;try{scormReady=API.LMSInitialize("")==="true";if(scormReady){API.LMSSetValue("cmi.core.lesson_status","incomplete");API.LMSCommit("")}return scormReady}catch(e){return false}}
function scormSet(score,status){if(!API||!scormReady)return;try{API.LMSSetValue("cmi.core.score.raw",String(score));API.LMSSetValue("cmi.core.lesson_status",status);API.LMSCommit("")}catch(e){}}
function scormFinish(){if(!API||!scormReady)return;try{API.LMSCommit("");API.LMSFinish("")}catch(e){}}
window.addEventListener('load',scormInit);window.addEventListener('beforeunload',scormFinish);
'''.strip(), encoding='utf-8')


def js_string(value: str) -> str:
    return value.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')


def write_app() -> None:
    import json
    data = json.dumps(SCREENS, ensure_ascii=False)
    (WORK / 'index.html').write_text('''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy — Урок 1.1</title><link rel="stylesheet" href="style.css"></head><body><div id="app"></div><script src="scorm.js"></script><script src="app.js"></script></body></html>''', encoding='utf-8')
    (WORK / 'app.js').write_text(f'''
const screens={data};
let index=0, answered=false;
const app=document.getElementById('app');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
function logo(){{return `<img class="logoImg" src="img/jemix-logo.png" alt="JEMIX" onerror="this.replaceWith(Object.assign(document.createElement('b'),{{className:'logoFallback',textContent:'JEMIX'}}))">`;}}
function pump(){{return `<div class="pumpCard"><img src="img/jemix-pump.png" alt="Насос JEMIX" onerror="this.style.display='none';this.nextElementSibling.style.display='block'"><b style="display:none">JEMIX</b></div>`;}}
function sidebar(){{return `<aside><div class="brand">${{logo()}}</div><div class="moduleLabel">Модуль 1</div><h2>Основы насосной техники</h2><nav><button class="active">1.1 Что такое насос</button><button>1.2 Применение</button><button>1.3 Устройство</button></nav><div class="remember"><strong>Запомните</strong><span>Насос не создаёт воду.<br>Он передаёт воде энергию.</span></div></aside>`;}}
function progress(){{return Math.round(((index+1)/screens.length)*100);}}
function topbar(title){{return `<header><div><small>Урок 1 из 6</small><strong>${{esc(title)}}</strong></div><div class="progress"><i style="width:${{progress()}}%"></i></div><b>${{progress()}}%</b><div class="sound">Звук</div><div class="menu">Меню</div></header>`;}}
function audio(file){{return `<div class="audioRow"><button class="audioBtn" onclick="toggleAudio(this)"><span>▶</span>Прослушать</button><audio src="audio/${{file}}"></audio></div>`;}}
function toggleAudio(btn){{const a=btn.nextElementSibling;if(a.paused){{document.querySelectorAll('audio').forEach(x=>x!==a&&x.pause());a.play();btn.firstElementChild.textContent='❚❚';}}else{{a.pause();btn.firstElementChild.textContent='▶';}}a.onended=()=>btn.firstElementChild.textContent='▶';}}
function actions(){{return `<footer><button class="back" onclick="back()" ${{index===0?'disabled':''}}>← Назад</button><button class="next" onclick="next()">${{index===screens.length-1?'Завершить':'Далее →'}}</button></footer>`;}}
function layout(content,title){{return `<main class="shell">${{sidebar()}}<section class="workspace">${{topbar(title)}}<div class="content">${{content}}</div>${{actions()}}</section></main>`;}}
function render(){{const s=screens[index];let body='';
if(s.kind==='cover') body=`<div class="split"><section class="textCard"><span class="badge">1.1</span><h1>${{esc(s.title)}}</h1><p>${{esc(s.subtitle)}}</p>${{audio(s.audio)}}</section>${{pump()}}</div><div class="flowStrip"><span>Источник</span><i></i><span class="activeFlow">Насос</span><i></i><span>Дом</span></div>`;
if(s.kind==='goals') body=`<section class="wideCard"><span class="badge">Цель урока</span><h1>${{esc(s.title)}}</h1><div class="goalGrid">${{s.items.map((x,i)=>`<div><b>0${{i+1}}</b><span>${{esc(x)}}</span></div>`).join('')}}</div>${{audio(s.audio)}}</section>`;
if(s.kind==='definition') body=`<div class="split"><section class="textCard"><span class="badge">Базовое понятие</span><h1>${{esc(s.title)}}</h1><p>${{esc(s.body)}}</p><div class="note"><strong>Запомните</strong><span>${{esc(s.note)}}</span></div>${{audio(s.audio)}}</section>${{pump()}}</div><div class="flowStrip"><span>Источник</span><i></i><span class="activeFlow">Насос</span><i></i><span>Дом</span></div>`;
if(s.kind==='flow') body=`<section class="wideCard"><span class="badge">Принцип работы</span><h1>${{esc(s.title)}}</h1><div class="flowCards"><div><b>1</b><strong>Источник</strong><span>Скважина, колодец или ёмкость</span></div><i></i><div class="hot"><b>2</b><strong>Насос</strong><span>Передаёт воде энергию</span></div><i></i><div><b>3</b><strong>Дом</strong><span>Точки водоразбора</span></div></div><p>${{esc(s.body)}}</p>${{audio(s.audio)}}</section>`;
if(s.kind==='applications') body=`<section class="wideCard"><span class="badge">Применение</span><h1>${{esc(s.title)}}</h1><div class="appGrid">${{s.items.map((x,i)=>`<div><b>0${{i+1}}</b><strong>${{esc(x[0])}}</strong><span>${{esc(x[1])}}</span></div>`).join('')}}</div>${{audio(s.audio)}}</section>`;
if(s.kind==='tip') body=`<section class="wideCard tipScreen"><span class="badge">Практический совет</span><h1>${{esc(s.title)}}</h1><p>${{esc(s.body)}}</p><div class="checkGrid">${{s.items.map(x=>`<div>✓ ${{esc(x)}}</div>`).join('')}}</div>${{audio(s.audio)}}</section>`;
if(s.kind==='quiz') body=`<section class="wideCard quiz"><span class="badge">Проверка</span><h1>${{esc(s.title)}}</h1><div class="answers">${{s.answers.map((x,i)=>`<button onclick="answer(${{i}},${{x[1]}})">${{esc(x[0])}}</button>`).join('')}}</div><div id="feedback"></div>${{audio(s.audio)}}</section>`;
if(s.kind==='summary') body=`<section class="wideCard"><span class="badge">Итоги</span><h1>${{esc(s.title)}}</h1><div class="summaryList">${{s.items.map(x=>`<div>✓ ${{esc(x)}}</div>`).join('')}}</div>${{audio(s.audio)}}</section>`;
app.innerHTML=layout(body,s.title);scormSet(progress(),index===screens.length-1?'completed':'incomplete');}}
function answer(i,ok){{const fb=document.getElementById('feedback');answered=ok;fb.className=ok?'ok':'bad';fb.textContent=ok?'Верно. Насос передаёт жидкости энергию.':'Неверно. Попробуйте ещё раз.';}}
function next(){{if(screens[index].kind==='quiz'&&!answered){{const fb=document.getElementById('feedback');fb.className='bad';fb.textContent='Сначала выберите правильный ответ.';return}}if(index<screens.length-1){{index++;render();}}else{{scormSet(100,'completed');scormFinish();}}}}
function back(){{if(index>0){{index--;render();}}}}
window.addEventListener('load',render);
''', encoding='utf-8')


def write_css() -> None:
    (WORK / 'style.css').write_text(r'''
:root{--red:#ef0712;--black:#111;--muted:#666;--line:#e8e8e8;--soft:#f6f6f6;--white:#fff}*{box-sizing:border-box}html,body,#app{min-height:100%;margin:0}body{font-family:Arial,sans-serif;color:var(--black);background:#fff}.shell{min-height:100vh;display:grid;grid-template-columns:260px 1fr;background:#fafafa}aside{background:#fff;border-right:1px solid var(--line);padding:24px 24px 18px;display:flex;flex-direction:column}.logoImg{max-width:145px;height:auto}.logoFallback{font-size:38px;color:var(--red)}.moduleLabel{margin-top:34px;color:#777;font-weight:800}aside h2{font-size:27px;line-height:1.15;margin:8px 0 22px}nav{display:grid;gap:10px}nav button{width:100%;min-height:48px;padding:12px 14px;border:0;border-radius:14px;text-align:left;font-size:16px;background:#f1f1f1;color:#555;white-space:normal;overflow-wrap:anywhere}nav button.active{background:var(--red);color:#fff;font-weight:800}.remember{margin-top:auto;border-left:6px solid var(--red);border-radius:16px;background:#f5f5f5;padding:16px;display:grid;gap:8px}.remember span{line-height:1.45}.workspace{min-width:0;display:flex;flex-direction:column;min-height:100vh}header{height:78px;background:#fff;border-bottom:1px solid var(--line);display:grid;grid-template-columns:250px minmax(180px,1fr) 55px 80px 80px;gap:18px;align-items:center;padding:0 28px}header small{display:block;color:#666;margin-bottom:4px}header strong{font-size:18px}.progress{height:9px;border-radius:999px;background:#e9e9e9;overflow:hidden}.progress i{display:block;height:100%;background:var(--red);border-radius:999px}.sound,.menu{font-weight:700;text-align:center}.content{width:min(1120px,calc(100% - 40px));margin:24px auto;flex:1;display:flex;flex-direction:column;justify-content:center}.split{display:grid;grid-template-columns:.95fr 1.15fr;gap:22px}.textCard,.pumpCard,.wideCard{background:#fff;border:1px solid var(--line);border-radius:24px;box-shadow:0 12px 34px rgba(0,0,0,.06)}.textCard,.wideCard{padding:30px}.pumpCard{min-height:470px;display:flex;align-items:center;justify-content:center;overflow:hidden}.pumpCard img{max-width:94%;max-height:430px;object-fit:contain}.pumpCard b{font-size:48px;color:var(--red)}.badge{display:inline-block;background:var(--red);color:#fff;border-radius:13px;padding:8px 14px;font-weight:900}.textCard h1,.wideCard h1{font-size:clamp(38px,5vw,66px);line-height:1.02;margin:24px 0 20px}.textCard p,.wideCard p{font-size:21px;line-height:1.5;color:#444}.note{margin-top:22px;border-left:6px solid var(--red);background:#f4f4f4;border-radius:16px;padding:16px;display:grid;gap:6px}.audioRow{margin-top:22px}.audioBtn{max-width:100%;min-width:190px;min-height:48px;padding:12px 18px;border:1px solid #ddd;border-radius:14px;background:#fff;font-size:17px;font-weight:800;white-space:normal;overflow-wrap:anywhere}.audioBtn span{color:var(--red);margin-right:10px}.flowStrip{display:flex;align-items:center;justify-content:center;gap:20px;margin-top:18px}.flowStrip span{background:#fff;border:1px solid var(--line);border-radius:13px;padding:12px 18px;font-weight:800}.flowStrip i{width:42px;height:4px;background:var(--red);border-radius:999px}.flowStrip .activeFlow{background:var(--red);color:#fff}.goalGrid,.appGrid,.checkGrid,.summaryList{display:grid;gap:14px}.goalGrid{grid-template-columns:1fr 1fr}.goalGrid div,.appGrid div{background:#f5f5f5;border-radius:17px;padding:18px;display:grid;gap:8px}.goalGrid b,.appGrid b{color:var(--red);font-size:22px}.goalGrid span,.appGrid strong{font-size:19px}.flowCards{display:grid;grid-template-columns:1fr 50px 1fr 50px 1fr;align-items:center;gap:10px;margin:28px 0}.flowCards div{min-height:165px;background:#f5f5f5;border-radius:18px;padding:20px;display:flex;flex-direction:column;gap:8px}.flowCards div.hot{background:var(--red);color:#fff}.flowCards i{height:4px;background:var(--red);border-radius:999px}.flowCards b{font-size:27px}.flowCards strong{font-size:22px}.appGrid{grid-template-columns:repeat(3,1fr)}.appGrid span{line-height:1.4;color:#555}.tipScreen{border-left:8px solid var(--red)}.checkGrid{grid-template-columns:repeat(3,1fr);margin:24px 0}.checkGrid div,.summaryList div{background:#f5f5f5;border-radius:15px;padding:17px;font-size:18px;font-weight:800}.answers{display:grid;gap:12px}.answers button{width:100%;min-height:52px;padding:14px 18px;border:2px solid var(--line);border-radius:14px;background:#fff;text-align:left;font-size:18px;white-space:normal;overflow-wrap:anywhere}.answers button:hover{border-color:var(--red)}#feedback{margin-top:14px;padding:14px;border-radius:12px;font-weight:800}#feedback:empty{display:none}.ok{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}footer{height:74px;border-top:1px solid var(--line);background:#fff;display:flex;align-items:center;justify-content:space-between;padding:12px 28px;gap:12px}footer button{max-width:48%;min-width:145px;min-height:48px;padding:12px 20px;border:0;border-radius:14px;font-size:17px;font-weight:900;white-space:normal;overflow-wrap:anywhere}.back{background:#fff;border:1px solid #ddd}.next{background:var(--red);color:#fff}.back:disabled{opacity:.4}@media(max-width:900px){.shell{grid-template-columns:1fr}aside{display:none}header{grid-template-columns:1fr;gap:8px;height:auto;padding:16px}.sound,.menu{display:none}.content{width:calc(100% - 20px);margin:10px auto}.split,.goalGrid,.appGrid,.checkGrid{grid-template-columns:1fr}.pumpCard{min-height:300px}.flowCards{grid-template-columns:1fr}.flowCards i{height:4px;width:100%}.flowStrip{flex-wrap:wrap}.flowStrip i{width:20px}.textCard,.wideCard{padding:22px}.textCard h1,.wideCard h1{font-size:40px}footer{padding:12px}footer button{min-width:0;width:48%;font-size:15px}}
'''.strip(), encoding='utf-8')


def pack() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in WORK.rglob('*'):
            if path.is_file():
                z.write(path, path.relative_to(WORK).as_posix())


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)
    copy_assets()
    write_manifest()
    write_scorm()
    write_app()
    write_css()
    pack()
    print(f'OK: {OUT}')
    missing=[]
    if not LOGO_SRC.exists(): missing.append(str(LOGO_SRC))
    if not PUMP_SRC.exists(): missing.append(str(PUMP_SRC))
    for i in range(1,9):
        p=AUDIO_SRC/f'slide{i:02d}.mp3'
        if not p.exists(): missing.append(str(p))
    if missing:
        print('WARNING: missing assets:')
        for x in missing: print(' -',x)

if __name__ == '__main__':
    main()
