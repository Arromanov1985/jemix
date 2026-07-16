#!/usr/bin/env python3
from pathlib import Path
import argparse, tempfile, zipfile
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_UX_v2_FINAL_WITH_JEMIX_PUMPS.zip'
OUT=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_INFOGRAPHICS.zip'
TITLES=['Что такое насос','Цели урока','Главная идея','Принцип работы','Основные задачи','Мини-квиз 1','Напор','Группы насосов','Мини-квиз 2','Первые параметры','Расход','Рабочая среда','Кейс 1','Кейс 2','Типичные ошибки','Проверка','Чек-лист','Итоговый тест 1','Итоговый тест 2','Итоги урока']
SUB=['Источник → насос → потребитель','Что нужно понять в первом уроке','Насос передаёт воде энергию','Забор → движение → подача','Перемещение • напор • сопротивление','Проверяем понимание','Высота и сопротивление системы','Поверхностные и погружные','Выбираем подходящую группу','Источник • напор • расход • среда','Объём воды за единицу времени','Чистая • загрязнённая • горячая','Разбираем задачу клиента','Сопоставляем условия и решение','Сначала параметры, потом модель','Закрепляем ключевую логику','Вопросы перед подбором','Проверяем знания','Финальная проверка','Главное из урока']

def fnt(size,bold=False):
    paths=[Path('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    for p in paths:
        if p.exists(): return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()

def make_png(path,n):
    im=Image.new('RGB',(1400,760),'white');d=ImageDraw.Draw(im)
    red='#E30613';dark='#20252B';gray='#69727C';line='#DDE2E7';blue='#DDEEFF'
    d.rounded_rectangle((30,30,1370,730),28,fill='#FAFBFC',outline=line,width=3)
    d.text((80,70),f'{n:02d}',font=fnt(26,True),fill=red)
    d.text((150,60),TITLES[n-1],font=fnt(44,True),fill=dark)
    y=320;xs=[250,700,1150];labels=['УСЛОВИЯ','НАСОС','РЕЗУЛЬТАТ']
    for i,x in enumerate(xs):
        fill=red if i==1 else ('#EEF1F4' if i==0 else blue);txt='white' if i==1 else dark
        d.rounded_rectangle((x-145,y-70,x+145,y+70),24,fill=fill,outline=red if i==1 else line,width=3)
        bb=d.textbbox((0,0),labels[i],font=fnt(25,True));d.text((x-(bb[2]-bb[0])/2,y-16),labels[i],font=fnt(25,True),fill=txt)
        if i<2:
            d.line((x+165,y,xs[i+1]-165,y),fill=gray,width=6)
            d.polygon([(xs[i+1]-165,y),(xs[i+1]-195,y-15),(xs[i+1]-195,y+15)],fill=red)
    d.rounded_rectangle((170,520,1230,650),22,fill='white',outline=line,width=3)
    bb=d.textbbox((0,0),SUB[n-1],font=fnt(31,True));d.text(((1400-(bb[2]-bb[0]))/2,565),SUB[n-1],font=fnt(31,True),fill=dark)
    im.save(path,'PNG',optimize=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=SRC);p.add_argument('--output',type=Path,default=OUT);a=p.parse_args()
    if not a.source.exists(): raise SystemExit(f'ZIP not found: {a.source}')
    with tempfile.TemporaryDirectory() as td:
        w=Path(td);zipfile.ZipFile(a.source).extractall(w)
        slides=sorted(w.rglob('slide[0-9][0-9].html'))
        if len(slides)!=20: raise SystemExit(f'Expected 20 slide HTML files, found {len(slides)}')
        imgdir=w/'img';imgdir.mkdir(exist_ok=True)
        for n in range(1,21): make_png(imgdir/f'infographic-slide{n:02d}.png',n)
        css_files=list(w.rglob('style-v2.css'))
        if not css_files: raise SystemExit('style-v2.css not found')
        css=css_files[0];txt=css.read_text(encoding='utf-8')
        rule='\n.lesson-infographic-wrap{margin:12px 0 18px}.lesson-infographic{display:block;width:100%;max-height:430px;object-fit:contain;border-radius:18px;background:#fff;box-shadow:0 8px 28px rgba(24,32,40,.08)}\n'
        if '.lesson-infographic-wrap' not in txt: css.write_text(txt+rule,encoding='utf-8')
        for n,slide in enumerate(slides,1):
            s=slide.read_text(encoding='utf-8')
            if 'lesson-infographic-wrap' in s: continue
            block=f'<div class="lesson-infographic-wrap"><img class="lesson-infographic" src="img/infographic-slide{n:02d}.png" alt="Инфографика к экрану {n}"></div>'
            markers=['<section class="wide">','<main class="content">','<main>']
            for marker in markers:
                if marker in s:
                    s=s.replace(marker,marker+block,1)
                    break
            else:
                raise SystemExit(f'No insertion marker found in {slide.name}')
            slide.write_text(s,encoding='utf-8')
        man=w/'imsmanifest.xml'
        if man.exists():
            m=man.read_text(encoding='utf-8')
            entries='\n'.join(f'      <file href="img/infographic-slide{n:02d}.png"/>' for n in range(1,21))
            if 'img/infographic-slide01.png' not in m:
                m=m.replace('</resource>',entries+'\n    </resource>',1);man.write_text(m,encoding='utf-8')
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.unlink(missing_ok=True)
        with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as z:
            for f in w.rglob('*'):
                if f.is_file(): z.write(f,f.relative_to(w).as_posix())
    print('OK:',a.output)
    print('Inserted 20 infographics into slide01.html ... slide20.html')
    print('Audio, tests, navigation and SCORM logic preserved')

if __name__=='__main__': main()
