#!/usr/bin/env python3
from pathlib import Path
import argparse,re,tempfile,zipfile
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_UX_v2_FINAL_WITH_JEMIX_PUMPS.zip'
OUT=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_INFOGRAPHICS.zip'
TITLES=['Что такое насос','Цели урока','Главная идея','Принцип работы','Основные задачи','Мини-квиз 1','Напор','Группы насосов','Мини-квиз 2','Первые параметры','Расход','Рабочая среда','Кейс 1','Кейс 2','Типичные ошибки','Проверка','Чек-лист','Итоговый тест 1','Итоговый тест 2','Итоги урока']
SUB=['Источник → насос → потребитель','Что нужно понять в первом уроке','Насос передаёт воде энергию','Забор → движение → подача','Перемещение • напор • сопротивление','Проверяем понимание','Высота и сопротивление системы','Поверхностные и погружные','Выбираем подходящую группу','Источник • напор • расход • среда','Объём воды за единицу времени','Чистая • загрязнённая • горячая','Разбираем задачу клиента','Сопоставляем условия и решение','Сначала параметры, потом модель','Закрепляем ключевую логику','Вопросы перед подбором','Проверяем знания','Финальная проверка','Главное из урока']
INTERACTIVE={6,9,16,18,19}

def fnt(size,bold=False):
    paths=[Path('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    for p in paths:
        if p.exists(): return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()

def make_png(path,n):
    im=Image.new('RGB',(1600,820),'white');d=ImageDraw.Draw(im)
    red='#E30613';dark='#20252B';gray='#69727C';line='#DDE2E7';blue='#EAF4FF'
    d.text((65,55),f'{n:02d}',font=fnt(28,True),fill=red)
    d.text((135,42),TITLES[n-1],font=fnt(52,True),fill=dark)
    y=350;xs=[280,800,1320];labels=['УСЛОВИЯ','НАСОС','РЕЗУЛЬТАТ']
    for i,x in enumerate(xs):
        fill=red if i==1 else ('#F1F3F5' if i==0 else blue);txt='white' if i==1 else dark
        d.rounded_rectangle((x-175,y-88,x+175,y+88),28,fill=fill,outline=red if i==1 else line,width=4)
        bb=d.textbbox((0,0),labels[i],font=fnt(30,True));d.text((x-(bb[2]-bb[0])/2,y-19),labels[i],font=fnt(30,True),fill=txt)
        if i<2:
            d.line((x+205,y,xs[i+1]-205,y),fill=gray,width=7)
            d.polygon([(xs[i+1]-205,y),(xs[i+1]-242,y-19),(xs[i+1]-242,y+19)],fill=red)
    d.rounded_rectangle((210,590,1390,735),22,fill='white',outline=line,width=3)
    bb=d.textbbox((0,0),SUB[n-1],font=fnt(36,True));d.text(((1600-(bb[2]-bb[0]))/2,638),SUB[n-1],font=fnt(36,True),fill=dark)
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
        css=list(w.rglob('style-v2.css'))[0];txt=css.read_text(encoding='utf-8')
        rule='\n.lesson-infographic-wrap{width:100%;margin:18px 0 4px}.lesson-infographic{display:block;width:100%;height:auto;max-height:560px;object-fit:contain;border-radius:16px;background:#fff}.content>.wide{padding:16px!important}.content{gap:14px!important}\n'
        if '.lesson-infographic-wrap' not in txt: css.write_text(txt+rule,encoding='utf-8')
        for n,slide in enumerate(slides,1):
            s=slide.read_text(encoding='utf-8')
            block=f'<div class="lesson-infographic-wrap"><img class="lesson-infographic" src="img/infographic-slide{n:02d}.png" alt="Инфографика к экрану {n}"></div>'
            if n not in INTERACTIVE:
                pattern=r'(<audio\b[^>]*></audio></div>).*?(</section></main>)'
                s2,count=re.subn(pattern,lambda m:m.group(1)+block+m.group(2),s,count=1,flags=re.S)
                if count!=1: raise SystemExit(f'Audio/content block not found in {slide.name}')
                s=s2
            else:
                marker='<section class="wide">'
                if marker in s:s=s.replace(marker,marker+block,1)
            slide.write_text(s,encoding='utf-8')
        man=w/'imsmanifest.xml'
        if man.exists():
            m=man.read_text(encoding='utf-8');entries='\n'.join(f'      <file href="img/infographic-slide{n:02d}.png"/>' for n in range(1,21))
            if 'img/infographic-slide01.png' not in m:m=m.replace('</resource>',entries+'\n    </resource>',1);man.write_text(m,encoding='utf-8')
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.unlink(missing_ok=True)
        with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as z:
            for f in w.rglob('*'):
                if f.is_file():z.write(f,f.relative_to(w).as_posix())
    print('OK:',a.output)
    print('Large infographics installed; duplicate informational content removed')
    print('Audio, quizzes, navigation and SCORM logic preserved')

if __name__=='__main__':main()
