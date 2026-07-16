#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "voice" / "modules" / "module-01" / "lesson-1.1" / "audio"
OLD_TEMPLATE = ROOT / "output" / "JEMIX_Academy_1_1_Chto_takoe_nasos_SCORM_UX_v2.zip"
BUILD = ROOT / "build" / "lesson-1.1-scorm-20"
OUTPUT = ROOT / "dist" / "module-01" / "JEMIX_Academy_1_1_SCORM_20_SLIDES_FINAL.zip"

SLIDES = [
    ("Обложка", "Что такое насос", "Короткий вводный урок для менеджера по продажам: назначение насоса, основные задачи и первые параметры подбора.", "v2_01_cover.png", None),
    ("Цели урока", "Что вы сможете после урока", "Объяснять назначение насоса, понимать роль напора, различать основные группы оборудования и задавать клиенту правильные вопросы.", "v2_02_objectives.png", None),
    ("Что такое насос", "Насос передаёт жидкости энергию", "Благодаря этому вода перемещается от источника к потребителю, поднимается на высоту и преодолевает сопротивление трубопровода.", "v2_03_system.png", None),
    ("Насос в системе", "Источник → насос → потребитель", "Насос не создаёт воду. Он обеспечивает её движение по системе и формирует требуемые рабочие условия.", "v2_03_system.png", None),
    ("Основные задачи", "Что должен сделать насос", "Подача воды, откачивание, повышение давления или циркуляция. Подбор начинается с точного определения задачи.", "v2_06_algorithm.png", None),
    ("Мини-квиз 1", "Главная задача насоса", "Выберите один вариант.", "v2_09_quizintro.png", {"type":"choice","options":["Перемещать жидкость и создавать напор","Только нагревать воду","Только фильтровать песок","Только измерять давление"],"answer":0}),
    ("Напор", "Что показывает напор", "Напор характеризует способность насоса поднять воду, протолкнуть её по трубам и обеспечить требуемое давление у потребителя.", "v2_07_terms.png", None),
    ("Группы насосов", "Основные группы оборудования", "Поверхностные, скважинные, дренажные и циркуляционные насосы различаются назначением и условиями работы.", "v2_04_rightwrong.png", None),
    ("Мини-квиз 2", "Какой насос работает в скважине", "Выберите правильный вариант.", "v2_09_quizintro.png", {"type":"choice","options":["Скважинный погружной","Циркуляционный","Повышающий","Манометр"],"answer":0}),
    ("Первые параметры", "С чего начинается подбор", "Задача, среда перекачивания, требуемый расход и необходимый напор. Мощность и цена рассматриваются после определения условий.", "v2_06_algorithm.png", None),
    ("Расход", "Сколько воды требуется", "Расход зависит от количества одновременно работающих точек: душа, крана, полива, стиральной машины и других потребителей.", "v2_07_terms.png", None),
    ("Среда", "Что будет перекачивать насос", "Чистую воду, загрязнённую воду, сточные воды или теплоноситель. Неверно определённая среда приводит к ошибке выбора.", "v2_07_terms.png", None),
    ("Кейс 1", "Нужно откачать воду из подвала", "С какой группы оборудования следует начать подбор?", "v2_08_case.png", {"type":"choice","options":["Дренажные насосы","Циркуляционные насосы","Манометр","Канализационная установка для раковины"],"answer":0}),
    ("Кейс 2", "Нужна циркуляция теплоносителя", "Какая группа оборудования подходит для системы отопления?", "v2_08_case.png", {"type":"choice","options":["Циркуляционные насосы","Скважинные насосы","Фекальные насосы","Дренажные насосы"],"answer":0}),
    ("Ошибки новичка", "Что нельзя делать", "Начинать подбор с мощности, не уточнять среду, путать расход с напором и предлагать модель до выяснения задачи.", "v2_04_rightwrong.png", None),
    ("Верно или неверно", "Насос можно подобрать только по мощности", "Определите, верно ли утверждение.", "v2_04_rightwrong.png", {"type":"choice","options":["Верно","Неверно"],"answer":1}),
    ("Чек-лист", "Что спросить у клиента", "Задача, тип жидкости, источник и точка подачи, расход, напор, условия монтажа и необходимость автоматической работы.", "v2_06_algorithm.png", None),
    ("Итоговый вопрос 1", "Почему важна среда перекачивания", "Выберите один вариант.", "v2_09_quizintro.png", {"type":"choice","options":["Разные среды требуют разных типов насосов","Только ради цвета корпуса","Среда не влияет на подбор","Только ради упаковки"],"answer":0}),
    ("Итоговый вопрос 2", "Напор связан с высотой и сопротивлением", "Определите, верно ли утверждение.", "v2_09_quizintro.png", {"type":"choice","options":["Верно","Неверно"],"answer":0}),
    ("Итоги урока", "Главное, что нужно запомнить", "Насос передаёт жидкости энергию. Подбор начинается с задачи, среды, расхода и напора — не только с мощности или цены.", "v2_10_summary.png", None),
]

INDEX = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy — урок 1.1</title><link rel="stylesheet" href="styles.css"></head><body><main id="app"></main><script src="app.js"></script></body></html>'''

CSS = '''*{box-sizing:border-box}body{margin:0;background:#424b59;font-family:Inter,Arial,sans-serif;color:#101828}.shell{width:min(1400px,96vw);height:min(850px,96vh);margin:2vh auto;background:#fff;border-radius:18px;overflow:hidden;display:grid;grid-template-columns:260px 1fr;box-shadow:0 18px 60px #0004}.side{padding:28px 22px;border-right:1px solid #e5e7eb;display:flex;flex-direction:column;min-height:0}.logo{font-size:44px;font-weight:800;color:#ed1424;line-height:1}.academy{font-size:16px;margin-bottom:28px}.module{font-size:12px;letter-spacing:.15em;color:#8992a3;font-weight:700}.lesson{font-size:24px;font-weight:750;margin:8px 0 16px}.nav{overflow:auto;display:grid;gap:7px}.nav button{border:1px solid #e5e7eb;background:#f8f8f9;border-radius:11px;padding:10px 12px;text-align:left;cursor:pointer}.nav button.active{border-color:#ed1424;color:#d90919;background:#fff}.main{min-width:0;display:grid;grid-template-rows:76px 1fr 82px}.top{border-bottom:1px solid #e5e7eb;padding:16px 28px;display:flex;align-items:center;gap:24px}.counter{min-width:100px;font-size:13px;color:#667085}.progress{height:7px;background:#eef0f3;border-radius:10px;flex:1;overflow:hidden}.bar{height:100%;background:#ed1424}.content{padding:24px;overflow:auto;background:#f7f8fa}.card{background:#fff;border:1px solid #e0e4ea;border-radius:20px;padding:24px;min-height:100%;display:grid;grid-template-columns:minmax(300px,46%) 1fr;gap:28px;align-items:center}.visual{background:#f4f6f8;border-radius:16px;min-height:420px;display:flex;align-items:center;justify-content:center;overflow:hidden}.visual img{width:100%;height:100%;object-fit:contain}.copy h1{font-size:34px;margin:0 0 8px}.copy h2{font-size:21px;color:#ed1424;margin:0 0 18px}.copy p{font-size:18px;line-height:1.55}.audio{margin:22px 0}.audio audio{width:100%}.options{display:grid;gap:10px;margin-top:18px}.option{border:1px solid #d9dde4;background:#fff;border-radius:12px;padding:13px;text-align:left;cursor:pointer}.option.selected{border-color:#ed1424;background:#fff2f3}.feedback{margin-top:12px;font-weight:700}.bottom{padding:16px 28px;display:flex;justify-content:space-between;border-top:1px solid #e5e7eb}.btn{border:1px solid #d9dde4;background:#fff;border-radius:11px;padding:12px 22px;font-weight:700;cursor:pointer}.btn.primary{background:#ed1424;color:#fff;border-color:#ed1424}.btn:disabled{opacity:.4}@media(max-width:900px){.shell{grid-template-columns:1fr;height:auto;min-height:96vh}.side{display:none}.card{grid-template-columns:1fr}.visual{min-height:260px}}'''

APP = r'''let lesson=null,index=0,answers={},score=0;function api(){let w=window;for(let i=0;i<8&&w;i++,w=w.parent){if(w.API)return w.API}return null}function setLms(k,v){try{const a=api();if(a)a.LMSSetValue(k,String(v))}catch(e){}}function commit(){try{const a=api();if(a)a.LMSCommit("")}catch(e){}}function initLms(){try{const a=api();if(a){a.LMSInitialize("");setLms("cmi.core.lesson_status","incomplete")}}catch(e){}}function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}function render(){const s=lesson.slides[index],total=lesson.slides.length,pct=Math.round((index+1)/total*100);let quiz='';if(s.quiz){quiz='<div class="options">'+s.quiz.options.map((o,i)=>`<button class="option ${answers[index]===i?'selected':''}" onclick="pick(${i})">${esc(o)}</button>`).join('')+'</div><div id="feedback" class="feedback"></div>'}document.getElementById('app').innerHTML=`<div class="shell"><aside class="side"><div class="logo">Jemix</div><div class="academy">Academy</div><div class="module">МОДУЛЬ 1</div><div class="lesson">Основы насосной техники</div><div class="nav">${lesson.slides.map((x,i)=>`<button class="${i===index?'active':''}" onclick="go(${i})">${String(i+1).padStart(2,'0')}. ${esc(x.nav)}</button>`).join('')}</div></aside><section class="main"><header class="top"><div class="counter">ЭКРАН ${index+1} ИЗ ${total}</div><div class="progress"><div class="bar" style="width:${pct}%"></div></div><strong>${pct}%</strong></header><div class="content"><article class="card"><div class="visual"><img src="images/${esc(s.image)}" alt="${esc(s.title)}"></div><div class="copy"><h2>${esc(s.nav)}</h2><h1>${esc(s.title)}</h1><p>${esc(s.text)}</p><div class="audio"><audio controls preload="metadata" src="audio/slide${String(index+1).padStart(2,'0')}.mp3"></audio></div>${quiz}</div></article></div><footer class="bottom"><button class="btn" onclick="go(${index-1})" ${index===0?'disabled':''}>Назад</button><button class="btn primary" onclick="next()">${index===total-1?'Завершить урок':'Далее'}</button></footer></section></div>`}window.pick=i=>{answers[index]=i;document.querySelectorAll('.option').forEach((x,n)=>x.classList.toggle('selected',n===i));const q=lesson.slides[index].quiz,ok=i===q.answer;document.getElementById('feedback').textContent=ok?'Верно':'Ответ сохранён. Правильный вариант будет учтён в результате.'};window.go=i=>{if(i<0||i>=lesson.slides.length)return;index=i;render()};window.next=()=>{if(index<lesson.slides.length-1){index++;render();return}const qs=lesson.slides.map((s,i)=>s.quiz?{s,i}:null).filter(Boolean);score=qs.length?Math.round(qs.filter(x=>answers[x.i]===x.s.quiz.answer).length/qs.length*100):100;setLms('cmi.core.score.raw',score);setLms('cmi.core.lesson_status',score>=80?'passed':'completed');commit();alert(`Урок завершён. Результат тестов: ${score}%`)};fetch('lesson-data.json').then(r=>r.json()).then(d=>{lesson=d;initLms();render()}).catch(e=>document.getElementById('app').textContent='Ошибка загрузки урока: '+e);window.addEventListener('beforeunload',commit);'''


def valid_mp3(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 1024:
        return False
    h = path.read_bytes()[:3]
    return h == b"ID3" or (len(h) >= 2 and h[0] == 0xFF and (h[1] & 0xE0) == 0xE0)


def extract_images() -> None:
    images = BUILD / "images"
    images.mkdir(parents=True, exist_ok=True)
    if not OLD_TEMPLATE.is_file():
        raise SystemExit(f"Не найден исходный шаблон с изображениями: {OLD_TEMPLATE}")
    with zipfile.ZipFile(OLD_TEMPLATE) as z:
        for name in z.namelist():
            if name.startswith("images/") and name.lower().endswith(".png"):
                (BUILD / name).parent.mkdir(parents=True, exist_ok=True)
                (BUILD / name).write_bytes(z.read(name))
    missing = {row[3] for row in SLIDES} - {p.name for p in images.glob("*.png")}
    if missing:
        raise SystemExit("Не найдены изображения: " + ", ".join(sorted(missing)))


def make_manifest() -> str:
    files = ["index.html", "styles.css", "app.js", "lesson-data.json"]
    files += [f"images/{name}" for name in sorted({row[3] for row in SLIDES})]
    files += [f"audio/slide{i:02d}.mp3" for i in range(1, 21)]
    tags = "\n".join(f'      <file href="{x}"/>' for x in files)
    return f'''<?xml version="1.0" encoding="UTF-8"?>\n<manifest identifier="JEMIX_1_1_20" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata><organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Academy</title><item identifier="ITEM1" identifierref="RES1"><title>Урок 1.1. Что такое насос</title></item></organization></organizations><resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">\n{tags}\n    </resource></resources></manifest>'''


def main() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    extract_images()
    audio_out = BUILD / "audio"
    audio_out.mkdir()
    for i in range(1, 21):
        src = AUDIO / f"slide{i:02d}.mp3"
        if not valid_mp3(src):
            raise SystemExit(f"Отсутствует или некорректен MP3: {src}")
        shutil.copy2(src, audio_out / src.name)
    data = {"module":"Модуль 1","lesson":"1.1","title":"Что такое насос","passingScore":80,"slides":[]}
    for i,(nav,title,text,image,quiz) in enumerate(SLIDES,1):
        data["slides"].append({"number":i,"nav":nav,"title":title,"text":text,"image":image,"quiz":quiz})
    (BUILD / "index.html").write_text(INDEX, encoding="utf-8")
    (BUILD / "styles.css").write_text(CSS, encoding="utf-8")
    (BUILD / "app.js").write_text(APP, encoding="utf-8")
    (BUILD / "lesson-data.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (BUILD / "imsmanifest.xml").write_text(make_manifest(), encoding="utf-8")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as z:
        for file in BUILD.rglob("*"):
            if file.is_file():
                z.write(file, file.relative_to(BUILD).as_posix())
    with zipfile.ZipFile(OUTPUT) as z:
        if z.testzip():
            raise SystemExit("Собранный ZIP повреждён")
        names=set(z.namelist())
        required={"imsmanifest.xml","index.html","app.js","styles.css","lesson-data.json"}|{f"audio/slide{i:02d}.mp3" for i in range(1,21)}
        missing=required-names
        if missing:
            raise SystemExit("В ZIP отсутствуют: "+", ".join(sorted(missing)))
    print(f"OK: {OUTPUT}")
    print("Slides: 20; MP3: 20; SCORM: 1.2")

if __name__ == "__main__":
    main()
