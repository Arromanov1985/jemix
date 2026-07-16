#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_BUILDER = ROOT / "scripts" / "build_lesson_1_1_scorm_20.py"
AUDIO = ROOT / "voice" / "modules" / "module-01" / "lesson-1.1" / "audio"
OLD_TEMPLATE = ROOT / "output" / "JEMIX_Academy_1_1_Chto_takoe_nasos_SCORM_UX_v2.zip"
BUILD = ROOT / "build" / "lesson-1.1-scorm-20-lms"
OUTPUT = ROOT / "dist" / "module-01" / "JEMIX_Academy_1_1_SCORM_20_SLIDES_LMS_READY.zip"

spec = importlib.util.spec_from_file_location("lesson20", SOURCE_BUILDER)
if spec is None or spec.loader is None:
    raise SystemExit(f"Cannot load source builder: {SOURCE_BUILDER}")
lesson20 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson20)

SLIDES = lesson20.SLIDES
CSS = lesson20.CSS

INDEX = '''<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>JEMIX Academy — урок 1.1</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <main id="app"><div style="padding:32px;color:white">Загрузка урока…</div></main>
  <script src="app.js"></script>
</body>
</html>'''

APP_LOGIC = r'''
let index=0,answers={},score=0;
function api(){try{let w=window;for(let i=0;i<8&&w;i++){try{if(w.API)return w.API}catch(e){};if(w===w.parent)break;w=w.parent}}catch(e){}return null}
function setLms(k,v){try{const a=api();if(a)a.LMSSetValue(k,String(v))}catch(e){}}
function commit(){try{const a=api();if(a)a.LMSCommit("")}catch(e){}}
function initLms(){try{const a=api();if(a){a.LMSInitialize("");setLms("cmi.core.lesson_status","incomplete")}}catch(e){}}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function render(){
  const s=lesson.slides[index],total=lesson.slides.length,pct=Math.round((index+1)/total*100);
  let quiz='';
  if(s.quiz){quiz='<div class="options">'+s.quiz.options.map((o,i)=>`<button class="option ${answers[index]===i?'selected':''}" onclick="pick(${i})">${esc(o)}</button>`).join('')+'</div><div id="feedback" class="feedback"></div>'}
  document.getElementById('app').innerHTML=`<div class="shell"><aside class="side"><div class="logo">Jemix</div><div class="academy">Academy</div><div class="module">МОДУЛЬ 1</div><div class="lesson">Основы насосной техники</div><div class="nav">${lesson.slides.map((x,i)=>`<button class="${i===index?'active':''}" onclick="go(${i})">${String(i+1).padStart(2,'0')}. ${esc(x.nav)}</button>`).join('')}</div></aside><section class="main"><header class="top"><div class="counter">ЭКРАН ${index+1} ИЗ ${total}</div><div class="progress"><div class="bar" style="width:${pct}%"></div></div><strong>${pct}%</strong></header><div class="content"><article class="card"><div class="visual"><img src="images/${esc(s.image)}" alt="${esc(s.title)}" onerror="this.style.display='none';this.parentElement.innerHTML='<div style=\'padding:30px;text-align:center;color:#667085\'>Изображение недоступно</div>'"></div><div class="copy"><h2>${esc(s.nav)}</h2><h1>${esc(s.title)}</h1><p>${esc(s.text)}</p><div class="audio"><audio controls preload="metadata" src="audio/slide${String(index+1).padStart(2,'0')}.mp3"></audio></div>${quiz}</div></article></div><footer class="bottom"><button class="btn" onclick="go(${index-1})" ${index===0?'disabled':''}>Назад</button><button class="btn primary" onclick="next()">${index===total-1?'Завершить урок':'Далее'}</button></footer></section></div>`
}
window.pick=i=>{answers[index]=i;document.querySelectorAll('.option').forEach((x,n)=>x.classList.toggle('selected',n===i));const q=lesson.slides[index].quiz,ok=i===q.answer;document.getElementById('feedback').textContent=ok?'Верно':'Ответ сохранён'};
window.go=i=>{if(i<0||i>=lesson.slides.length)return;index=i;render()};
window.next=()=>{if(index<lesson.slides.length-1){index++;render();return}const qs=lesson.slides.map((s,i)=>s.quiz?{s,i}:null).filter(Boolean);score=qs.length?Math.round(qs.filter(x=>answers[x.i]===x.s.quiz.answer).length/qs.length*100):100;setLms('cmi.core.score.raw',score);setLms('cmi.core.lesson_status',score>=80?'passed':'completed');commit();alert(`Урок завершён. Результат тестов: ${score}%`)};
try{initLms();render()}catch(e){document.getElementById('app').innerHTML='<pre style="background:white;color:#b42318;padding:24px;white-space:pre-wrap">Ошибка запуска урока: '+esc(e&&e.stack?e.stack:e)+'</pre>'}
window.addEventListener('beforeunload',commit);
'''


def valid_mp3(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 1024:
        return False
    data = path.read_bytes()[:3]
    return data == b"ID3" or (len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0)


def manifest() -> str:
    files = ["index.html", "styles.css", "app.js"]
    files += [f"images/{name}" for name in sorted({row[3] for row in SLIDES})]
    files += [f"audio/slide{i:02d}.mp3" for i in range(1, 21)]
    tags = "\n".join(f'      <file href="{name}"/>' for name in files)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_1_1_20_LMS" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Academy</title><item identifier="ITEM1" identifierref="RES1"><title>Урок 1.1. Что такое насос</title></item></organization></organizations>
  <resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">
{tags}
  </resource></resources>
</manifest>'''


def main() -> None:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    (BUILD / "images").mkdir(parents=True)
    (BUILD / "audio").mkdir(parents=True)

    if not OLD_TEMPLATE.is_file():
        raise SystemExit(f"Template not found: {OLD_TEMPLATE}")
    with zipfile.ZipFile(OLD_TEMPLATE) as archive:
        for name in archive.namelist():
            if name.startswith("images/") and name.lower().endswith(".png"):
                (BUILD / name).write_bytes(archive.read(name))

    missing_images = {row[3] for row in SLIDES} - {p.name for p in (BUILD / "images").glob("*.png")}
    if missing_images:
        raise SystemExit("Missing images: " + ", ".join(sorted(missing_images)))

    for i in range(1, 21):
        source = AUDIO / f"slide{i:02d}.mp3"
        if not valid_mp3(source):
            raise SystemExit(f"Invalid MP3: {source}")
        shutil.copy2(source, BUILD / "audio" / source.name)

    data = {"module":"Модуль 1","lesson":"1.1","title":"Что такое насос","passingScore":80,"slides":[]}
    for i,(nav,title,text,image,quiz) in enumerate(SLIDES,1):
        data["slides"].append({"number":i,"nav":nav,"title":title,"text":text,"image":image,"quiz":quiz})

    app = "const lesson = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n" + APP_LOGIC
    (BUILD / "index.html").write_text(INDEX, encoding="utf-8")
    (BUILD / "styles.css").write_text(CSS, encoding="utf-8")
    (BUILD / "app.js").write_text(app, encoding="utf-8")
    (BUILD / "imsmanifest.xml").write_text(manifest(), encoding="utf-8")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT.exists():
        OUTPUT.unlink()
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in BUILD.rglob("*"):
            if file.is_file():
                archive.write(file, file.relative_to(BUILD).as_posix())

    with zipfile.ZipFile(OUTPUT) as archive:
        if archive.testzip():
            raise SystemExit("ZIP validation failed")
        names = set(archive.namelist())
        required = {"index.html","styles.css","app.js","imsmanifest.xml"} | {f"audio/slide{i:02d}.mp3" for i in range(1,21)}
        missing = required - names
        if missing:
            raise SystemExit("Missing in ZIP: " + ", ".join(sorted(missing)))

    print(f"OK: {OUTPUT}")
    print("Self-contained SCORM: 20 slides, 20 MP3, no fetch()")


if __name__ == "__main__":
    main()
