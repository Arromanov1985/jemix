#!/usr/bin/env python3
from pathlib import Path
import json
import shutil
import zipfile

ROOT = Path('.')
WORK = ROOT / '_scorm_lesson_1_1_final'
DIST = ROOT / 'dist' / 'module-01'
OUT = DIST / 'JEMIX_Lesson_1_1_SCORM_FINAL.zip'
LOGO = ROOT / 'academy-assets' / 'logo' / 'jemix-logo.png'
PUMP = ROOT / 'academy-assets' / 'pumps' / 'jemix-pump.png'
AUDIO = ROOT / 'voice' / 'modules' / 'module-01' / 'lesson-1.1' / 'audio'

SCREENS = [
    {'kind': 'cover', 'title': 'Что такое насос?', 'subtitle': 'Первый урок Академии JEMIX: базовое понятие, принцип работы и применение.'},
    {'kind': 'goals', 'title': 'После урока вы сможете', 'items': ['Объяснить, что такое насос', 'Понять, зачем насос нужен в системе', 'Назвать основные области применения', 'Подготовиться к дальнейшему подбору оборудования']},
    {'kind': 'definition', 'title': 'Что такое насос', 'body': 'Насос — это гидравлическая машина, которая передаёт жидкости энергию и заставляет её двигаться по системе.', 'note': 'Насос не создаёт воду. Он передаёт воде энергию.'},
    {'kind': 'flow', 'title': 'Источник — насос — потребитель', 'body': 'Насос находится между источником воды и потребителем. Он обеспечивает движение воды к точкам водоразбора.'},
    {'kind': 'energy', 'title': 'Что именно передаёт насос', 'items': [['Движение', 'Жидкость начинает перемещаться по трубопроводу.'], ['Давление', 'В системе создаётся давление, необходимое для подачи воды.'], ['Напор', 'Вода преодолевает высоту и сопротивление труб.']]},
    {'kind': 'applications', 'title': 'Где применяются насосы', 'items': [['Частный дом', 'Водоснабжение кухни, душа и других точек.'], ['Дача и полив', 'Подача воды из колодца, ёмкости или другого источника.'], ['Инженерные системы', 'Отопление, дренаж, канализация и повышение давления.']]},
    {'kind': 'types', 'title': 'Разные задачи — разные насосы', 'items': [['Поверхностные', 'Устанавливаются вне источника воды.'], ['Погружные', 'Работают непосредственно в воде.'], ['Циркуляционные', 'Обеспечивают движение теплоносителя.']]},
    {'kind': 'system', 'title': 'Насос работает в составе системы', 'body': 'Результат зависит не только от насоса, но и от источника воды, трубопровода, автоматики, гидроаккумулятора и точек потребления.'},
    {'kind': 'selection', 'title': 'С чего начинается подбор', 'items': ['Определить источник воды', 'Рассчитать требуемый расход', 'Определить необходимый напор', 'Учесть условия эксплуатации']},
    {'kind': 'mistake', 'title': 'Типичная ошибка', 'body': 'Нельзя выбирать насос только по мощности двигателя. Мощность сама по себе не показывает, какой расход и напор обеспечит оборудование.', 'note': 'Сначала задача и параметры системы — потом модель насоса.'},
    {'kind': 'quiz', 'title': 'Что делает насос?', 'answers': [['Создаёт воду', False], ['Передаёт жидкости энергию', True], ['Только очищает воду', False], ['Хранит запас воды', False]]},
    {'kind': 'summary', 'title': 'Главное из урока', 'items': ['Насос передаёт жидкости энергию', 'Он обеспечивает движение, давление и напор', 'Насос всегда подбирают под конкретную систему', 'Мощность двигателя — не главный критерий выбора']},
]


def source_audio(index: int) -> Path:
    return AUDIO / f'slide{index:02d}.mp3'


def package_audio_name(index: int) -> str:
    src = source_audio(index)
    if src.is_file() and src.read_bytes()[:4] == b'RIFF':
        return f'slide{index:02d}.wav'
    return f'slide{index:02d}.mp3'


def copy_assets() -> None:
    (WORK / 'img').mkdir(parents=True, exist_ok=True)
    (WORK / 'audio').mkdir(parents=True, exist_ok=True)

    if not LOGO.is_file():
        raise FileNotFoundError(f'Missing logo: {LOGO}')
    if not PUMP.is_file():
        raise FileNotFoundError(f'Missing pump image: {PUMP}')

    shutil.copy2(LOGO, WORK / 'img' / 'jemix-logo.png')
    shutil.copy2(PUMP, WORK / 'img' / 'jemix-pump.png')

    for i in range(1, 13):
        src = source_audio(i)
        if not src.is_file() or src.stat().st_size < 1024:
            raise FileNotFoundError(f'Missing or empty audio: {src}')
        shutil.copy2(src, WORK / 'audio' / package_audio_name(i))
        SCREENS[i - 1]['audio'] = package_audio_name(i)


def write_manifest() -> None:
    files = [
        'index.html', 'style.css', 'app.js', 'scorm.js',
        'img/jemix-logo.png', 'img/jemix-pump.png',
    ] + [f'audio/{package_audio_name(i)}' for i in range(1, 13)]
    file_nodes = ''.join(f'<file href="{name}"/>' for name in files)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_LESSON_1_1" version="1.0"
 xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
 xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
 <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
 <organizations default="ORG1"><organization identifier="ORG1">
  <title>JEMIX Lesson 1.1</title>
  <item identifier="ITEM1" identifierref="RES1"><title>Что такое насос</title></item>
 </organization></organizations>
 <resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">{file_nodes}</resource></resources>
</manifest>'''
    (WORK / 'imsmanifest.xml').write_text(xml, encoding='utf-8')


def write_scorm_js() -> None:
    js = """function findAPI(w){var n=0;while(w&&n<500){if(w.API){return w.API;}n++;if(w.parent===w){break;}w=w.parent;}return null;}
var API=findAPI(window)||(window.opener?findAPI(window.opener):null);var ready=false;
function scormInit(){if(!API){return false;}try{ready=API.LMSInitialize('')==='true';if(ready){var status=API.LMSGetValue('cmi.core.lesson_status');if(!status||status==='not attempted'){API.LMSSetValue('cmi.core.lesson_status','incomplete');}API.LMSCommit('');}return ready;}catch(e){return false;}}
function scormSet(score,status){if(!API||!ready){return;}try{API.LMSSetValue('cmi.core.score.raw',String(score));API.LMSSetValue('cmi.core.lesson_status',status);API.LMSCommit('');}catch(e){}}
function scormFinish(){if(!API||!ready){return;}try{API.LMSCommit('');API.LMSFinish('');}catch(e){}}
window.addEventListener('load',scormInit);window.addEventListener('beforeunload',scormFinish);"""
    (WORK / 'scorm.js').write_text(js, encoding='utf-8')


def write_files() -> None:
    index_html = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy — Урок 1.1</title><link rel="stylesheet" href="style.css"></head><body><div id="app"></div><script src="scorm.js"></script><script src="app.js"></script></body></html>'''
    (WORK / 'index.html').write_text(index_html, encoding='utf-8')

    data = json.dumps(SCREENS, ensure_ascii=False)
    app = """
var screens=__DATA__;var current=0;var answered=false;var app=document.getElementById('app');
function esc(value){return String(value===null||typeof value==='undefined'?'':value).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c];});}
function logo(){return '<img class="logoImg" src="img/jemix-logo.png" alt="JEMIX">';}
function pump(){return '<div class="pumpCard"><img src="img/jemix-pump.png" alt="Насос JEMIX"></div>';}
function side(){return '<aside><div>'+logo()+'</div><div class="module">Модуль 1</div><h2>Основы насосной техники</h2><nav><button class="active">1.1 Что такое насос</button><button>1.2 Основные параметры</button><button>1.3 Виды насосов</button></nav><div class="remember"><b>Запомните</b><span>Насос не создаёт воду.<br>Он передаёт воде энергию.</span></div></aside>';}
function top(title){var p=Math.round((current+1)/screens.length*100);return '<header><div><small>Экран '+(current+1)+' из '+screens.length+'</small><strong>'+esc(title)+'</strong></div><div class="progress"><i style="width:'+p+'%"></i></div><b>'+p+'%</b></header>';}
function audioHtml(file){return '<div class="audioRow"><button type="button" onclick="toggleAudio(this)">▶ Прослушать</button><audio preload="metadata" src="audio/'+esc(file)+'"></audio></div>';}
function toggleAudio(button){var audio=button.nextElementSibling;var all=document.getElementsByTagName('audio');for(var i=0;i<all.length;i++){if(all[i]!==audio){all[i].pause();}}if(audio.paused){audio.play();button.textContent='❚❚ Пауза';}else{audio.pause();button.textContent='▶ Прослушать';}audio.onended=function(){button.textContent='▶ Прослушать';};}
function footer(){return '<footer><button class="back" type="button" onclick="back()" '+(current===0?'disabled':'')+'>← Назад</button><button class="next" type="button" onclick="next()">'+(current===screens.length-1?'Завершить':'Далее →')+'</button></footer>';}
function wrap(content,title){return '<main class="shell">'+side()+'<section class="work">'+top(title)+'<div class="content">'+content+'</div>'+footer()+'</section></main>';}
function cards(items,cls){var html='<div class="'+cls+'">';for(var i=0;i<items.length;i++){var x=items[i];html+='<div><b>0'+(i+1)+'</b><strong>'+esc(x[0])+'</strong><span>'+esc(x[1])+'</span></div>';}return html+'</div>';}
function simpleList(items){var html='<div class="list">';for(var i=0;i<items.length;i++){html+='<div>✓ '+esc(items[i])+'</div>';}return html+'</div>';}
function render(){var s=screens[current];var c='';
if(s.kind==='cover'){c='<div class="split"><section class="card"><span class="badge">1.1</span><h1>'+esc(s.title)+'</h1><p>'+esc(s.subtitle)+'</p>'+audioHtml(s.audio)+'</section>'+pump()+'</div><div class="flow"><span>Источник</span><i></i><span class="hot">Насос</span><i></i><span>Потребитель</span></div>';}
else if(s.kind==='goals'){c='<section class="wide"><span class="badge">Цель урока</span><h1>'+esc(s.title)+'</h1>'+simpleList(s.items)+audioHtml(s.audio)+'</section>';}
else if(s.kind==='definition'){c='<div class="split"><section class="card"><span class="badge">Базовое понятие</span><h1>'+esc(s.title)+'</h1><p>'+esc(s.body)+'</p><div class="note"><b>Запомните</b><span>'+esc(s.note)+'</span></div>'+audioHtml(s.audio)+'</section>'+pump()+'</div>';}
else if(s.kind==='flow'){c='<section class="wide"><span class="badge">Принцип работы</span><h1>'+esc(s.title)+'</h1><div class="flowCards"><div><b>1</b><strong>Источник</strong><span>Скважина, колодец или ёмкость</span></div><i></i><div class="red"><b>2</b><strong>Насос</strong><span>Передаёт воде энергию</span></div><i></i><div><b>3</b><strong>Потребитель</strong><span>Точки водоразбора</span></div></div><p>'+esc(s.body)+'</p>'+audioHtml(s.audio)+'</section>';}
else if(s.kind==='applications'||s.kind==='energy'||s.kind==='types'){c='<section class="wide"><span class="badge">'+(s.kind==='applications'?'Применение':s.kind==='energy'?'Результат работы':'Основные группы')+'</span><h1>'+esc(s.title)+'</h1>'+cards(s.items,'grid3')+audioHtml(s.audio)+'</section>';}
else if(s.kind==='system'){c='<div class="split"><section class="card"><span class="badge">Системный подход</span><h1>'+esc(s.title)+'</h1><p>'+esc(s.body)+'</p>'+audioHtml(s.audio)+'</section>'+pump()+'</div>';}
else if(s.kind==='selection'){c='<section class="wide"><span class="badge">Алгоритм</span><h1>'+esc(s.title)+'</h1>'+simpleList(s.items)+audioHtml(s.audio)+'</section>';}
else if(s.kind==='mistake'){c='<section class="wide tip"><span class="badge">Важно</span><h1>'+esc(s.title)+'</h1><p>'+esc(s.body)+'</p><div class="note"><b>Правильный подход</b><span>'+esc(s.note)+'</span></div>'+audioHtml(s.audio)+'</section>';}
else if(s.kind==='quiz'){var answers='<div class="answers">';for(var a=0;a<s.answers.length;a++){answers+='<button type="button" onclick="answer('+(s.answers[a][1]?'true':'false')+')">'+esc(s.answers[a][0])+'</button>';}answers+='</div>';c='<section class="wide"><span class="badge">Проверка</span><h1>'+esc(s.title)+'</h1>'+answers+'<div id="fb"></div>'+audioHtml(s.audio)+'</section>';}
else if(s.kind==='summary'){c='<section class="wide"><span class="badge">Итоги</span><h1>'+esc(s.title)+'</h1>'+simpleList(s.items)+audioHtml(s.audio)+'</section>';}
app.innerHTML=wrap(c,s.title);scormSet(Math.round((current+1)/screens.length*100),current===screens.length-1?'completed':'incomplete');}
function answer(ok){answered=ok;var f=document.getElementById('fb');f.className=ok?'ok':'bad';f.textContent=ok?'Верно. Насос передаёт жидкости энергию.':'Неверно. Попробуйте ещё раз.';}
function next(){if(screens[current].kind==='quiz'&&!answered){var f=document.getElementById('fb');f.className='bad';f.textContent='Сначала выберите правильный ответ.';return;}if(current<screens.length-1){current++;answered=false;render();}else{scormSet(100,'completed');scormFinish();}}
function back(){if(current>0){current--;answered=false;render();}}
window.addEventListener('load',render);
""".replace('__DATA__', data)
    (WORK / 'app.js').write_text(app, encoding='utf-8')

    css = """:root{--r:#ef0712;--l:#e8e8e8;--s:#f5f5f5}*{box-sizing:border-box}html,body,#app{min-height:100%;margin:0}body{font-family:Arial,sans-serif;color:#111;background:#fafafa}.shell{min-height:100vh;display:grid;grid-template-columns:260px 1fr}aside{background:#fff;border-right:1px solid var(--l);padding:24px;display:flex;flex-direction:column}.logoImg{max-width:145px}.module{margin-top:34px;color:#777;font-weight:800}aside h2{font-size:27px;line-height:1.15;margin:8px 0 22px}nav{display:grid;gap:10px}nav button{width:100%;min-height:48px;padding:12px 14px;border:0;border-radius:14px;text-align:left;font-size:16px;background:#f1f1f1;color:#555}nav .active{background:var(--r);color:#fff;font-weight:800}.remember{margin-top:auto;border-left:6px solid var(--r);border-radius:16px;background:var(--s);padding:16px;display:grid;gap:8px}.work{display:flex;flex-direction:column;min-width:0;min-height:100vh}header{min-height:78px;background:#fff;border-bottom:1px solid var(--l);display:grid;grid-template-columns:270px minmax(180px,1fr) 60px;gap:18px;align-items:center;padding:12px 28px}header small{display:block;color:#666}header strong{font-size:18px}.progress{height:9px;background:#e9e9e9;border-radius:999px;overflow:hidden}.progress i{display:block;height:100%;background:var(--r)}.content{width:min(1120px,calc(100% - 40px));margin:24px auto;flex:1;display:flex;flex-direction:column;justify-content:center}.split{display:grid;grid-template-columns:.95fr 1.15fr;gap:22px}.card,.pumpCard,.wide{background:#fff;border:1px solid var(--l);border-radius:24px;box-shadow:0 12px 34px rgba(0,0,0,.06)}.card,.wide{padding:30px}.pumpCard{min-height:430px;display:flex;align-items:center;justify-content:center}.pumpCard img{max-width:94%;max-height:390px;object-fit:contain}.badge{display:inline-block;background:var(--r);color:#fff;border-radius:13px;padding:8px 14px;font-weight:900}.card h1,.wide h1{font-size:clamp(36px,5vw,62px);line-height:1.02;margin:24px 0 20px}.card p,.wide p{font-size:21px;line-height:1.5;color:#444}.note{margin-top:22px;border-left:6px solid var(--r);background:var(--s);border-radius:16px;padding:16px;display:grid;gap:6px}.audioRow{margin-top:22px}.audioRow button{min-width:190px;min-height:48px;padding:12px 18px;border:1px solid #ddd;border-radius:14px;background:#fff;font-size:17px;font-weight:800}.flow{display:flex;align-items:center;justify-content:center;gap:20px;margin-top:18px}.flow span{background:#fff;border:1px solid var(--l);border-radius:13px;padding:12px 18px;font-weight:800}.flow i{width:42px;height:4px;background:var(--r)}.flow .hot{background:var(--r);color:#fff}.grid3,.list{display:grid;gap:14px}.grid3{grid-template-columns:repeat(3,1fr)}.grid3 div,.list div{background:var(--s);border-radius:17px;padding:18px;display:grid;gap:8px}.flowCards{display:grid;grid-template-columns:1fr 50px 1fr 50px 1fr;align-items:center;gap:10px;margin:28px 0}.flowCards div{min-height:165px;background:var(--s);border-radius:18px;padding:20px;display:flex;flex-direction:column;gap:8px}.flowCards .red{background:var(--r);color:#fff}.flowCards i{height:4px;background:var(--r)}.tip{border-left:8px solid var(--r)}.answers{display:grid;gap:12px}.answers button{width:100%;min-height:52px;padding:14px 18px;border:2px solid var(--l);border-radius:14px;background:#fff;text-align:left;font-size:18px}.answers button:hover{border-color:var(--r)}#fb{margin-top:14px;padding:14px;border-radius:12px;font-weight:800}#fb:empty{display:none}.ok{background:#dcfce7;color:#166534}.bad{background:#fee2e2;color:#991b1b}footer{min-height:74px;border-top:1px solid var(--l);background:#fff;display:flex;align-items:center;justify-content:space-between;padding:12px 28px;gap:12px}footer button{min-width:145px;min-height:48px;padding:12px 20px;border:0;border-radius:14px;font-size:17px;font-weight:900}.back{background:#fff;border:1px solid #ddd}.next{background:var(--r);color:#fff}.back:disabled{opacity:.4}@media(max-width:900px){.shell{grid-template-columns:1fr}aside{display:none}header{grid-template-columns:1fr;height:auto;padding:16px}.content{width:calc(100% - 20px);margin:10px auto}.split,.grid3{grid-template-columns:1fr}.flowCards{grid-template-columns:1fr}.flowCards i{width:100%}.flow{flex-wrap:wrap}.card,.wide{padding:22px}.card h1,.wide h1{font-size:40px}footer{padding:12px}footer button{min-width:0;width:48%;font-size:15px}}"""
    (WORK / 'style.css').write_text(css, encoding='utf-8')


def pack() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in WORK.rglob('*'):
            if path.is_file():
                archive.write(path, path.relative_to(WORK).as_posix())


def main() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)
    copy_assets()
    write_manifest()
    write_scorm_js()
    write_files()
    pack()
    print(f'OK: {OUT}')


if __name__ == '__main__':
    main()
