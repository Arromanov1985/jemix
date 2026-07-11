#!/usr/bin/env python3
"""Build SCORM 1.2 package for JEMIX lesson 2.5: Автоматика и защита."""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path('.')
WORK = ROOT / '_scorm_lesson_2_5'
DIST = ROOT / 'dist' / 'module-02'
OUT = DIST / 'JEMIX_Lesson_2_5_SCORM.zip'
LOGO = ROOT / 'academy-assets' / 'logo' / 'jemix-logo.png'
PUMP = ROOT / 'academy-assets' / 'pumps' / 'jemix-pump.png'
AUDIO = ROOT / 'voice' / 'modules' / 'module-02' / 'lesson-2.5' / 'audio'

SCREENS = [
    {'type':'title','title':'Автоматика и защита','body':'Надёжная система водоснабжения — это не только насос, но и управление, защита и правильная обвязка.'},
    {'type':'goals','title':'Что нужно понять','items':['Зачем нужна автоматика','Что защищает насос от сухого хода','Какие элементы входят в комплект','Почему насос нельзя продавать отдельно']},
    {'type':'theory','title':'Автоматика','body':'Автоматика запускает и останавливает насос по условиям системы и поддерживает удобную работу без постоянного участия пользователя.'},
    {'type':'scheme','title':'Карта системы','items':['Насос','Обратный клапан','Автоматика','Гидроаккумулятор','Защита','Фильтр и фитинги']},
    {'type':'map','title':'Вопросы продавца','items':['Есть ли автоматика сейчас?','Нужна ли защита от сухого хода?','Какой источник воды?','Есть ли гидроаккумулятор?','Какие условия монтажа?']},
    {'type':'case','title':'Практический кейс','body':'Клиент хочет купить только насос для колодца и не планирует ставить защиту. Нужно объяснить риск сухого хода и предложить рабочий комплект.'},
    {'type':'dialogue','title':'Как это звучит','client':'Мне нужен только насос. Остальное потом.','seller':'Чтобы насос не работал всухую и не включался слишком часто, сразу подберём автоматику, защиту и обвязку.'},
    {'type':'right_wrong','title':'Ошибка в подборе','wrong':'Продать насос без проверки автоматики и защиты','right':'Собрать полный комплект под источник и режим работы'},
    {'type':'red_flags','title':'Красные флаги','items':['Нестабильный уровень воды','Нет защиты от сухого хода','Частые пуски насоса','Нет обратного клапана','Неподходящий гидроаккумулятор']},
    {'type':'quiz_intro','title':'Быстрая проверка','body':'Что входит в хороший подбор системы водоснабжения?'},
    {'type':'quiz','title':'Квиз','question':'Что входит в хороший подбор системы водоснабжения?','answers':['Насос, автоматика, защита и обвязка','Только насос без уточнений','Только самый дорогой насос','Только фитинги без защиты'],'correct':0},
    {'type':'summary','title':'Итоги урока','items':['Автоматика управляет работой насоса','Защита от сухого хода сохраняет ресурс','Комплект важнее отдельного насоса','Обвязка подбирается под условия системы']},
]


def prepare() -> None:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    (WORK / 'img').mkdir()
    (WORK / 'audio').mkdir()
    if LOGO.exists(): shutil.copy2(LOGO, WORK / 'img' / 'jemix-logo.png')
    if PUMP.exists(): shutil.copy2(PUMP, WORK / 'img' / 'jemix-pump.png')
    for i in range(1, 13):
        src = AUDIO / f'slide{i:02d}.mp3'
        if src.exists(): shutil.copy2(src, WORK / 'audio' / src.name)


def write_manifest() -> None:
    files = ['index.html','style.css','app.js','scorm.js']
    files += [f'img/{p.name}' for p in (WORK/'img').iterdir()]
    files += [f'audio/{p.name}' for p in (WORK/'audio').iterdir()]
    nodes = ''.join(f'<file href="{x}"/>' for x in files)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="JEMIX_LESSON_2_5" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
  <metadata><schema>ADL SCORM</schema><schemaversion>1.2</schemaversion></metadata>
  <organizations default="ORG1"><organization identifier="ORG1"><title>JEMIX Lesson 2.5</title><item identifier="ITEM1" identifierref="RES1"><title>Автоматика и защита</title></item></organization></organizations>
  <resources><resource identifier="RES1" type="webcontent" adlcp:scormtype="sco" href="index.html">{nodes}</resource></resources>
</manifest>'''
    (WORK/'imsmanifest.xml').write_text(xml, encoding='utf-8')


def write_runtime() -> None:
    (WORK/'index.html').write_text('<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy — 2.5</title><link rel="stylesheet" href="style.css"></head><body><div id="app"></div><script src="scorm.js"></script><script src="app.js"></script></body></html>', encoding='utf-8')
    (WORK/'scorm.js').write_text('''function findAPI(w){let i=0;while(w&&i<500){if(w.API)return w.API;i++;if(w.parent===w)break;w=w.parent}return null}const API=findAPI(window)||(window.opener?findAPI(window.opener):null);let ready=false;function init(){try{ready=!!API&&API.LMSInitialize("")==="true";if(ready&&API.LMSGetValue("cmi.core.lesson_status")==="not attempted")API.LMSSetValue("cmi.core.lesson_status","incomplete")}catch(e){}}function setProgress(score,status,loc){if(!ready)return;API.LMSSetValue("cmi.core.score.raw",String(score));API.LMSSetValue("cmi.core.lesson_status",status);API.LMSSetValue("cmi.core.lesson_location",String(loc));API.LMSCommit("")}function finish(){if(ready){API.LMSCommit("");API.LMSFinish("")}}window.addEventListener("load",init);window.addEventListener("beforeunload",finish);''', encoding='utf-8')
    data = json.dumps(SCREENS, ensure_ascii=False)
    app = f'''const screens={data};let n=0;const app=document.getElementById('app');const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));function audio(i){{const f=`audio/slide${{String(i+1).padStart(2,'0')}}.mp3`;return `<div class="audio"><button onclick="this.nextElementSibling.play()">Прослушать</button><audio controls src="${{f}}"></audio></div>`}}function block(s){{if(s.items)return `<div class="grid">${{s.items.map(x=>`<div>${{esc(x)}}</div>`).join('')}}</div>`;if(s.client)return `<div class="dialog"><p><b>Клиент:</b> ${{esc(s.client)}}</p><p><b>Продавец:</b> ${{esc(s.seller)}}</p></div>`;if(s.wrong)return `<div class="compare"><div><b>Ошибка</b><p>${{esc(s.wrong)}}</p></div><div><b>Правильно</b><p>${{esc(s.right)}}</p></div></div>`;if(s.type==='quiz')return `<h2>${{esc(s.question)}}</h2><div class="answers">${{s.answers.map((x,i)=>`<button onclick="answer(${{i}})">${{esc(x)}}</button>`).join('')}}</div><div id="fb"></div>`;return `<p class="lead">${{esc(s.body||'')}}</p>`}}function render(){{const s=screens[n],p=Math.round((n+1)/screens.length*100);app.innerHTML=`<main><aside><img src="img/jemix-logo.png" alt="JEMIX"><h3>Модуль 2</h3><p>2.5 Автоматика и защита</p><div class="meter"><i style="width:${{p}}%"></i></div><b>${{p}}%</b></aside><section><header><span>Урок 2.5</span><strong>${{esc(s.title)}}</strong></header><article><span class="tag">${{esc(s.type)}}</span><h1>${{esc(s.title)}}</h1>${{block(s)}}${{audio(n)}}</article><footer><button onclick="prev()" ${{n===0?'disabled':''}}>Назад</button><button onclick="next()">${{n===screens.length-1?'Завершить':'Далее'}}</button></footer></section></main>`;setProgress(p,n===screens.length-1?'incomplete':'incomplete',n)}}function prev(){{if(n>0){{n--;render()}}}}function next(){{if(n<screens.length-1){{n++;render()}}else{{setProgress(100,'completed',n);app.innerHTML='<div class="done"><h1>Урок 2.5 завершён</h1><p>Результат передан в LMS.</p></div>'}}}}function answer(i){{const s=screens[n],fb=document.getElementById('fb');if(i===s.correct){{fb.innerHTML='<div class="ok">Верно</div>';}}else fb.innerHTML='<div class="bad">Неверно. Попробуйте ещё раз.</div>'}}window.addEventListener('load',render);'''
    (WORK/'app.js').write_text(app, encoding='utf-8')
    (WORK/'style.css').write_text(''':root{--red:#e30613;--ink:#111827;--muted:#6b7280;--line:#e5e7eb}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:var(--ink);background:#f6f7f9}main{min-height:100vh;display:grid;grid-template-columns:270px 1fr}aside{background:#fff;border-right:1px solid var(--line);padding:32px}aside img{max-width:150px}.meter{height:8px;background:#eee;border-radius:8px;overflow:hidden;margin:22px 0 8px}.meter i{display:block;height:100%;background:var(--red)}section{display:grid;grid-template-rows:auto 1fr auto}header,footer{background:#fff;padding:22px 32px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:20px}footer{border-top:1px solid var(--line);border-bottom:0}article{margin:34px;max-width:980px;background:#fff;border-radius:24px;padding:42px;box-shadow:0 15px 45px rgba(0,0,0,.08)}h1{font-size:44px;margin:12px 0 24px}.lead{font-size:22px;line-height:1.5}.tag{color:var(--red);font-weight:800;text-transform:uppercase}.grid,.compare{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.grid div,.compare div,.dialog{border:1px solid var(--line);border-radius:16px;padding:20px;background:#fafafa}.audio{margin-top:28px;padding-top:20px;border-top:1px solid var(--line)}button{border:0;border-radius:12px;padding:13px 20px;font-weight:800;cursor:pointer}.answers{display:grid;gap:12px}.answers button{text-align:left}.ok{color:#167c3a;font-weight:800;margin-top:16px}.bad{color:#b42318;font-weight:800;margin-top:16px}.done{min-height:100vh;display:grid;place-content:center;text-align:center;background:#fff}@media(max-width:800px){main{grid-template-columns:1fr}aside{display:none}article{margin:16px;padding:24px}.grid,.compare{grid-template-columns:1fr}h1{font-size:34px}}''', encoding='utf-8')


def build() -> None:
    prepare(); write_manifest(); write_runtime(); DIST.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in WORK.rglob('*'):
            if p.is_file(): z.write(p, p.relative_to(WORK))
    print(f'Built {OUT}')


if __name__ == '__main__':
    build()
