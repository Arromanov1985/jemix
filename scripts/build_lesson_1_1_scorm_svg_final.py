#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "voice" / "modules" / "module-01" / "lesson-1.1" / "audio"
BUILD = ROOT / "build" / "lesson-1.1-svg-final"
OUTPUT = ROOT / "dist" / "module-01" / "JEMIX_Academy_1_1_SCORM_SVG_AUDIO_FINAL.zip"
RED = "#D71920"
INK = "#1F2937"
MUTED = "#667085"
LINE = "#D9DEE7"
PANEL = "#F7F8FA"
WHITE = "#FFFFFF"

SLIDES = [
    ("Обложка", "Что такое насос", "Источник воды → насос → потребитель", "flow", "Насос обеспечивает движение воды и создаёт необходимые условия для работы системы."),
    ("Применение", "Где применяются насосы", "Дом, полив, отопление и дренаж", "applications", "Насосы JEMIX решают разные бытовые задачи, поэтому область применения нужно уточнять до выбора модели."),
    ("Задача", "Что делает насос", "Забирает воду, создаёт напор и подаёт её потребителю", "three_steps", "Насос не создаёт воду — он передаёт жидкости энергию и обеспечивает её движение."),
    ("Система", "Насос работает в системе", "Источник → насос → трубопровод → потребитель", "system", "Оценивать нужно не отдельный насос, а всю систему целиком."),
    ("Вопросы", "С чего начинается подбор", "Источник, расход, напор и условия эксплуатации", "questions", "Профессиональный подбор начинается со сбора исходных данных, а не с открытия каталога."),
    ("Напор", "Что такое напор", "Способность подать воду на требуемую высоту и преодолеть сопротивление", "head", "Напор показывает, сможет ли вода дойти до нужной точки системы."),
    ("Расход", "Что такое расход", "Количество воды за единицу времени", "flowrate", "Расход показывает, сколько воды насос способен подать за минуту или час."),
    ("Связь", "Напор и расход", "Рабочие параметры рассматриваются вместе", "curve", "Нельзя оценивать напор и расход отдельно: рабочая точка определяется их сочетанием."),
    ("Мощность", "Почему мощность не главный параметр", "Мощный насос не всегда является подходящим", "power", "Мощность двигателя не заменяет расчёт требуемого напора и расхода."),
    ("Параметры", "Что сравнивает специалист", "Напор, расход, источник и условия работы", "cards", "Правильный выбор определяется системой параметров, а не одной цифрой в характеристиках."),
    ("Проверка", "Мини-проверка", "Что нужно выяснить первым?", "quiz", "Сначала выясняют задачу и условия объекта, затем переходят к подбору модели."),
    ("Типы", "Основные группы насосов JEMIX", "Поверхностные, погружные, дренажные и циркуляционные", "types", "Каждая группа оборудования предназначена для своей области применения."),
    ("Поверхностные", "Поверхностный насос", "Работает вне источника воды", "surface", "Подходит для задач, где условия всасывания соответствуют возможностям поверхностного насоса."),
    ("Погружные", "Погружной насос", "Работает непосредственно в воде", "submersible", "Используется для подачи воды из скважин, колодцев и других источников."),
    ("Дренажные", "Дренажный насос", "Отводит чистую или загрязнённую воду", "drainage", "Применяется для откачивания воды из подвалов, резервуаров и затопленных помещений."),
    ("Циркуляционные", "Циркуляционный насос", "Обеспечивает движение теплоносителя", "circulation", "Работает в замкнутом контуре отопления и поддерживает циркуляцию."),
    ("Компоновка", "Насос в системе водоснабжения", "Источник → насос → гидроаккумулятор → дом", "full_system", "Надёжность результата зависит от согласованной работы всех элементов системы."),
    ("Ошибки", "Типичные ошибки подбора", "Выбор по мощности, неизвестные напор и расход, отсутствие данных", "errors", "Большинство ошибок связано не с качеством оборудования, а с недостатком исходных данных."),
    ("Итоги", "Что нужно запомнить", "Система, вопросы, напор, расход и область применения", "summary", "Нет универсального насоса: модель выбирают под конкретную задачу и условия работы."),
    ("Далее", "Следующий шаг", "Основные параметры насоса", "next", "В следующем уроке подробно разбираются напор, расход и другие параметры оборудования."),
]


def valid_mp3(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 1024:
        return False
    data = path.read_bytes()[:12]
    if data.startswith(b"RIFF") and data[8:12] == b"WAVE":
        return False
    return data.startswith(b"ID3") or (len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0)


def t(x: int, y: int, text: str, size: int = 28, weight: int = 600, fill: str = INK, anchor: str = "middle") -> str:
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{fill}">{html.escape(text)}</text>'


def box(x: int, y: int, w: int, h: int, label: str, active: bool = False) -> str:
    stroke = RED if active else LINE
    fill = "#FFF7F7" if active else WHITE
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{fill}" stroke="{stroke}" stroke-width="3"/>' + t(x+w//2, y+h//2+10, label, 24, 700, RED if active else INK)


def arrow(x1: int, y1: int, x2: int, y2: int, active: bool = False) -> str:
    color = RED if active else "#AAB2BF"
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="5" stroke-linecap="round" marker-end="url(#a)"/>'


def icon_pump(x: int, y: int, scale: float = 1.0, active: bool = True) -> str:
    c = RED if active else "#7B8494"
    w, h = int(150*scale), int(92*scale)
    return f'<g transform="translate({x},{y})"><rect x="0" y="18" width="{w}" height="{h}" rx="20" fill="none" stroke="{c}" stroke-width="6"/><circle cx="{int(w*.35)}" cy="{int(h*.52)}" r="{int(h*.25)}" fill="none" stroke="{c}" stroke-width="6"/><path d="M {int(w*.6)} 45 h {int(w*.25)} v -24" fill="none" stroke="{c}" stroke-width="6" stroke-linecap="round"/><line x1="{-30}" y1="{int(h*.65)}" x2="0" y2="{int(h*.65)}" stroke="{c}" stroke-width="6"/></g>'


def base_svg(content: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="560" viewBox="0 0 1000 560">
<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="{RED}"/></marker></defs>
<rect width="1000" height="560" rx="28" fill="{PANEL}"/>{content}</svg>'''


def make_svg(kind: str) -> str:
    if kind == "flow":
        c = box(80,210,220,110,"Источник") + arrow(310,265,405,265,True) + box(410,190,230,150,"НАСОС",True) + arrow(650,265,745,265,True) + box(750,210,170,110,"Дом") + icon_pump(450,215,.8)
    elif kind == "applications":
        c = icon_pump(420,210,1.05) + t(500,390,"Один насос — разные задачи",26,700) + box(80,80,190,90,"Дом") + box(730,80,190,90,"Полив") + box(80,390,190,90,"Отопление") + box(730,390,190,90,"Дренаж")
    elif kind == "three_steps":
        c = box(90,210,220,110,"Забрать воду") + arrow(320,265,390,265,True) + box(400,210,200,110,"Создать напор",True) + arrow(610,265,680,265,True) + box(690,210,220,110,"Подать воду")
    elif kind == "system":
        c = box(35,220,190,100,"Источник") + arrow(235,270,300,270,True) + box(310,205,180,130,"Насос",True) + arrow(500,270,565,270) + box(575,220,185,100,"Труба") + arrow(770,270,825,270) + box(835,220,130,100,"Дом")
    elif kind == "questions":
        labels=["Откуда вода?","Сколько воды?","Какой напор?","Какие условия?"]
        c="".join(box(110+i*220,210,190,110,l,i==0) for i,l in enumerate(labels))
    elif kind == "head":
        c = icon_pump(400,390,.9) + '<line x1="500" y1="390" x2="500" y2="100" stroke="#AAB2BF" stroke-width="5" stroke-dasharray="12 12"/>' + arrow(540,380,540,115,True) + t(575,260,"25 м",44,800,RED,"start") + box(690,70,190,100,"Точка подачи")
    elif kind == "flowrate":
        c = '<path d="M270 120 h170 v70 h-70 v65" fill="none" stroke="#7B8494" stroke-width="14" stroke-linecap="round"/>' + '<path d="M365 265 q20 45 0 75 q-20-30 0-75" fill="#F2B8BC"/>' + box(420,330,190,110,"20 литров",True) + arrow(625,385,700,385,True) + box(710,330,180,110,"1 минута") + t(500,500,"Расход = 20 л/мин",34,800)
    elif kind == "curve":
        c = '<line x1="160" y1="430" x2="850" y2="430" stroke="#7B8494" stroke-width="4"/><line x1="160" y1="430" x2="160" y2="90" stroke="#7B8494" stroke-width="4"/>' + '<path d="M190 130 C360 160 510 250 810 400" fill="none" stroke="#AAB2BF" stroke-width="7"/>' + '<circle cx="520" cy="265" r="16" fill="#D71920"/>' + t(520,220,"Рабочая точка",24,700,RED) + t(510,490,"Расход",24,600) + t(100,260,"Напор",24,600)
    elif kind == "power":
        c = box(120,190,260,150,"МОЩНОСТЬ") + t(500,285,"≠",72,800,RED) + box(620,190,260,150,"ПОДХОДИТ",True) + t(500,410,"Сначала задача и параметры системы",28,700)
    elif kind == "cards":
        labels=["Напор","Расход","Источник","Условия"]
        c="".join(box(70+i*230,205,200,130,l,i<2) for i,l in enumerate(labels))
    elif kind == "quiz":
        c = t(500,100,"Клиент говорит: «Мне нужен насос». Что уточнить первым?",28,700) + box(100,190,240,120,"Цену") + box(380,190,240,120,"Задачу",True) + box(660,190,240,120,"Цвет") + t(500,410,"Правильный порядок: задача → условия → параметры → модель",26,700)
    elif kind == "types":
        labels=["Поверхностный","Погружной","Дренажный","Циркуляционный"]
        c="".join(box(55+i*235,205,215,130,l,i==0) for i,l in enumerate(labels))
    elif kind == "surface":
        c = box(90,300,250,120,"Источник") + icon_pump(430,220,1.2) + arrow(345,350,430,310,True) + arrow(620,310,760,250,True) + box(760,190,160,110,"Дом") + t(500,470,"Насос находится вне воды",28,700)
    elif kind == "submersible":
        c = '<rect x="180" y="90" width="280" height="380" rx="22" fill="#EEF1F5" stroke="#AAB2BF" stroke-width="4"/><rect x="300" y="280" width="60" height="150" rx="24" fill="none" stroke="#D71920" stroke-width="7"/>' + arrow(330,280,610,180,True) + box(650,120,210,110,"Дом") + t(320,515,"Насос работает в воде",28,700)
    elif kind == "drainage":
        c = '<rect x="120" y="320" width="760" height="130" rx="20" fill="#EEF1F5"/>' + '<rect x="260" y="250" width="120" height="150" rx="26" fill="none" stroke="#D71920" stroke-width="7"/>' + arrow(380,290,720,150,True) + box(720,90,180,100,"Отвод воды") + t(500,510,"Удаление воды из подвалов и резервуаров",28,700)
    elif kind == "circulation":
        c = '<rect x="170" y="100" width="660" height="350" rx="40" fill="none" stroke="#AAB2BF" stroke-width="8"/>' + icon_pump(420,365,.8) + arrow(260,100,700,100,True) + arrow(830,180,830,360,True) + arrow(700,450,310,450,True) + t(500,260,"Замкнутый контур отопления",30,700)
    elif kind == "full_system":
        c = box(30,220,180,110,"Скважина") + arrow(220,275,300,275,True) + box(310,200,180,150,"Насос",True) + arrow(500,275,580,275) + box(590,220,190,110,"Гидробак") + arrow(790,275,845,275) + box(855,220,115,110,"Дом")
    elif kind == "errors":
        labels=["Только мощность","Нет расхода","Нет напора","Нет данных"]
        c="".join(box(65+i*235,205,215,130,l,False) for i,l in enumerate(labels)) + "".join(t(170+i*235,190,"×",38,800,RED) for i in range(4))
    elif kind == "summary":
        labels=["Система","Вопросы","Напор","Расход","Назначение"]
        c="".join(box(35+i*190,210,175,120,l,i==0) for i,l in enumerate(labels))
    else:
        c = t(500,190,"Урок 1.1 завершён",42,800) + arrow(500,240,500,340,True) + box(280,360,440,120,"Основные параметры насоса",True)
    return base_svg(c)


INDEX = '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JEMIX Academy</title><link rel="stylesheet" href="styles.css"></head><body><main id="app"></main><script src="app.js"></script></body></html>'''

CSS = f'''*{{box-sizing:border-box}}body{{margin:0;background:#424B59;font-family:Arial,sans-serif;color:{INK}}}.shell{{width:min(1440px,98vw);height:min(900px,98vh);margin:1vh auto;background:white;border-radius:18px;overflow:hidden;display:grid;grid-template-columns:260px 1fr;box-shadow:0 18px 60px #0004}}.side{{padding:26px 20px;border-right:1px solid #E5E7EB;display:flex;flex-direction:column;min-height:0}}.logo{{font-size:44px;font-weight:800;color:{RED}}}.academy{{font-size:16px;margin-bottom:26px}}.meta{{font-size:12px;letter-spacing:.12em;color:#8B95A5;font-weight:700}}.lesson{{font-size:21px;font-weight:750;margin:8px 0 18px}}.nav{{overflow:auto;display:grid;gap:6px}}.nav button{{border:0;background:transparent;border-radius:10px;padding:9px 10px;text-align:left;color:#566072;cursor:pointer}}.nav button.active{{background:#F4F5F7;color:{INK};font-weight:700;border-left:4px solid {RED}}}.main{{min-width:0;display:grid;grid-template-rows:72px 1fr 94px}}.top{{border-bottom:1px solid #E5E7EB;padding:15px 28px;display:flex;align-items:center;gap:20px}}.counter{{font-size:13px;color:#667085;min-width:130px}}.progress{{height:6px;background:#ECEFF3;border-radius:9px;flex:1;overflow:hidden}}.bar{{height:100%;background:{RED}}}.content{{padding:24px 30px;overflow:auto;background:#FAFAFB}}.card{{max-width:1050px;margin:auto;background:#fff;border:1px solid #E1E5EA;border-radius:20px;padding:22px 26px;min-height:100%;display:grid;grid-template-rows:auto 1fr auto}}h1{{font-size:32px;margin:0 0 6px}}.kicker{{font-size:14px;color:{RED};font-weight:700;text-transform:uppercase;letter-spacing:.08em}}.visual{{display:flex;align-items:center;justify-content:center;min-height:420px;margin:14px 0}}.visual img{{width:100%;max-height:470px;object-fit:contain}}.takeaway{{background:#F5F6F8;border-radius:14px;padding:15px 18px;border-top:3px solid {RED};font-size:17px;line-height:1.45}}audio{{width:100%;height:42px}}.bottom{{padding:15px 28px;display:grid;grid-template-columns:160px 1fr 160px;align-items:center;gap:18px;border-top:1px solid #E5E7EB}}.btn{{border:1px solid #D8DDE5;background:#fff;border-radius:11px;padding:12px 18px;font-weight:700;cursor:pointer}}.btn.primary{{background:{RED};border-color:{RED};color:white}}.btn:disabled{{opacity:.35}}@media(max-width:900px){{.shell{{grid-template-columns:1fr;height:auto;min-height:98vh}}.side{{display:none}}.visual{{min-height:300px}}.bottom{{grid-template-columns:110px 1fr 110px}}}}'''


def make_app() -> str:
    data = [{"nav": s[0], "title": s[1], "subtitle": s[2], "image": f"slide{i:02d}.svg", "takeaway": s[4]} for i, s in enumerate(SLIDES, 1)]
    embedded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f'''const slides={embedded};let index=0;function api(){{let w=window;for(let i=0;i<8&&w;i++,w=w.parent)if(w.API)return w.API;return null}}function setLms(k,v){{try{{const a=api();if(a)a.LMSSetValue(k,String(v))}}catch(e){{}}}}function commit(){{try{{const a=api();if(a)a.LMSCommit("")}}catch(e){{}}}}function init(){{try{{const a=api();if(a){{a.LMSInitialize("");setLms("cmi.core.lesson_status","incomplete")}}}}catch(e){{}}render()}}function esc(s){{return String(s??"").replace(/[&<>"']/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}}[c]))}}function go(i){{if(i>=0&&i<slides.length){{index=i;render()}}}}function next(){{if(index<slides.length-1){{index++;render();return}}setLms("cmi.core.score.raw",100);setLms("cmi.core.lesson_status","passed");commit();alert("Урок завершён")}}function render(){{const s=slides[index],pct=Math.round((index+1)/slides.length*100);document.getElementById("app").innerHTML=`<div class="shell"><aside class="side"><div class="logo">Jemix</div><div class="academy">Academy</div><div class="meta">МОДУЛЬ 1</div><div class="lesson">Урок 1.1<br>Что такое насос</div><div class="nav">${{slides.map((x,i)=>`<button class="${{i===index?"active":""}}" onclick="go(${{i}})">${{String(i+1).padStart(2,"0")}}. ${{esc(x.nav)}}</button>`).join("")}}</div></aside><section class="main"><header class="top"><div class="counter">ЭКРАН ${{index+1}} ИЗ ${{slides.length}}</div><div class="progress"><div class="bar" style="width:${{pct}}%"></div></div><strong>${{pct}}%</strong></header><div class="content"><article class="card"><div><div class="kicker">${{esc(s.nav)}}</div><h1>${{esc(s.title)}}</h1></div><div class="visual"><img src="images/${{s.image}}" alt="${{esc(s.title)}}"></div><div class="takeaway"><strong>Главное:</strong> ${{esc(s.takeaway)}}</div></article></div><footer class="bottom"><button class="btn" onclick="go(${{index-1}})" ${{index===0?"disabled":""}}>Назад</button><audio controls preload="metadata" src="audio/slide${{String(index+1).padStart(2,"0")}}.mp3"></audio><button class="btn primary" onclick="next()">${{index===slides.length-1?"Завершить":"Далее"}}</button></footer></section></div>`}}window.go=go;window.next=next;window.onerror=m=>document.getElementById("app").innerHTML=`<pre style="padding:24px;background:white;color:#B00020">Ошибка запуска: ${{esc(m)}}</pre>`;init();window.addEventListener("beforeunload",commit);'''


def manifest(files: list[str]) -> str:
    tags = "\n".join(f'      <file href="{f}"/>' for f in files)
    return f'''<?xml version="1.0" encoding="UTF-8"?><manifest identifier="JEMIX_1_1_SVG_FINAL" version="1.0" xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2" xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2"><