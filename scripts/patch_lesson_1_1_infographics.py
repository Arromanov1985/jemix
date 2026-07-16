#!/usr/bin/env python3
from pathlib import Path
import argparse,re,shutil,tempfile,zipfile
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_20_SLIDES_LMS_READY.zip'
OUT=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_INFOGRAPHICS.zip'
TITLES=['Что такое насос','Зачем изучать насосы','Насосы вокруг нас','Насос простыми словами','Задача важнее мощности','Ошибка начинающего менеджера','Как думает консультант','Алгоритм подбора','История из практики','Мини-кейс','Главное правило','Задачи насосов','Ассортимент JEMIX','Ошибка при подборе','Пять правил','Ошибки новичков','Что вы уже умеете','Почему доверяют профессионалам','Первый шаг сделан','Итоги урока']
SUB=['Источник → насос → потребитель','Сначала вопросы, затем решение','Дом • полив • отопление • дренаж','Насос сообщает воде энергию','Мощнее — не значит правильнее','Нельзя начинать с модели','Задача • источник • расход • напор','Данные → расчёт → модель','Неверный выбор приводит к возврату','Сначала соберите исходные данные','Задача выбирает насос','Каждой задаче — свой тип','Разные решения для разных условий','Поверхностный насос не для глубокой скважины','Система • задача • параметры • подбор','Сначала вопросы, потом каталог','Основа профессионального подбора','Доверие начинается с вопросов','Логика важнее запоминания моделей','Следующий урок: параметры насоса']

def font(size,bold=False):
    paths=[Path('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf'),Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
    for p in paths:
        if p.exists(): return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()

def make_png(path,n):
    im=Image.new('RGB',(1600,900),'white');d=ImageDraw.Draw(im)
    red='#D71920';dark='#20252B';gray='#707780';light='#EEF1F4'
    d.rounded_rectangle((70,60,1530,840),28,fill='#FAFBFC',outline='#DDE2E7',width=3)
    d.text((120,105),f'{n:02d}',font=font(28,True),fill=red)
    d.text((210,95),TITLES[n-1],font=font(48,True),fill=dark)
    y=330
    xs=[300,800,1300]
    labels=('ИСТОЧНИК','НАСОС','РЕЗУЛЬТАТ')
    for i,x in enumerate(xs):
        fill=red if i==1 else light;txt='white' if i==1 else dark
        d.rounded_rectangle((x-145,y-75,x+145,y+75),24,fill=fill,outline=red if i==1 else '#C9D0D7',width=3)
        w=d.textbbox((0,0),labels[i],font=font(27,True))[2]
        d.text((x-w/2,y-18),labels[i],font=font(27,True),fill=txt)
        if i<2:
            d.line((x+165,y,xs[i+1]-165,y),fill=gray,width=6)
            d.polygon([(xs[i+1]-165,y),(xs[i+1]-195,y-16),(xs[i+1]-195,y+16)],fill=red)
    box=(225,560,1375,735);d.rounded_rectangle(box,22,fill='white',outline='#DDE2E7',width=3)
    text=SUB[n-1];bbox=d.textbbox((0,0),text,font=font(35,True));tw=bbox[2]-bbox[0]
    d.text(((1600-tw)/2,620),text,font=font(35,True),fill=dark)
    im.save(path,'PNG',optimize=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=SRC);p.add_argument('--output',type=Path,default=OUT);a=p.parse_args()
    if not a.source.exists(): raise SystemExit(f'ZIP not found: {a.source}')
    with tempfile.TemporaryDirectory() as td:
        w=Path(td);zipfile.ZipFile(a.source).extractall(w);img=w/'images';img.mkdir(exist_ok=True)
        for n in range(1,21): make_png(img/f'slide{n:02d}.png',n)
        app=w/'app.js';s=app.read_text(encoding='utf-8')
        found=len(re.findall(r'"image":"[^"]*"',s))
        if found<20: raise SystemExit(f'Expected 20 embedded image fields, found {found}')
        i=iter(range(1,21));s=re.sub(r'"image":"[^"]*"',lambda m:f'"image":"slide{next(i):02d}.png"',s,count=20);app.write_text(s,encoding='utf-8')
        man=w/'imsmanifest.xml';m=man.read_text(encoding='utf-8')
        entries='\n'.join(f'      <file href="images/slide{n:02d}.png"/>' for n in range(1,21))
        if 'images/slide01.png' not in m:m=m.replace('</resource>',entries+'\n    </resource>',1);man.write_text(m,encoding='utf-8')
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.unlink(missing_ok=True)
        with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as z:
            for f in w.rglob('*'):
                if f.is_file():z.write(f,f.relative_to(w).as_posix())
    with zipfile.ZipFile(a.output) as z:
        names=set(z.namelist());missing=[f'images/slide{n:02d}.png' for n in range(1,21) if f'images/slide{n:02d}.png' not in names]
        if missing:raise SystemExit('Missing: '+', '.join(missing))
    print('OK:',a.output);print('Visuals replaced: 20; audio and SCORM logic preserved')

if __name__=='__main__':main()
