#!/usr/bin/env python3
from pathlib import Path
import re,tempfile,zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_UX_v2_FINAL_WITH_JEMIX_PUMPS.zip'
ATLAS=ROOT/'dist/module-01/JEMIX_Academy_1_1_INFOGRAPHICS_ATLAS.png'
OUT=ROOT/'dist/module-01/JEMIX_Academy_1_1_SCORM_INFOGRAPHICS_FINAL.zip'
INTERACTIVE={6,9,16,18,19}

def main():
    for p in (SRC,ATLAS):
        if not p.exists(): raise SystemExit(f'Not found: {p}')
    with tempfile.TemporaryDirectory() as td:
        w=Path(td)
        with zipfile.ZipFile(SRC) as z:z.extractall(w)
        slides=sorted(w.rglob('slide[0-9][0-9].html'))
        if len(slides)!=20:raise SystemExit(f'Expected 20 slides, found {len(slides)}')
        imgdir=w/'img';imgdir.mkdir(exist_ok=True)
        a=Image.open(ATLAS).convert('RGB');W,H=a.size
        files=[];n=1
        for r in range(4):
            for c in range(5):
                x1=round(c*W/5)+2;y1=round(r*H/4)+2
                x2=round((c+1)*W/5)-2;y2=round((r+1)*H/4)-2
                p=imgdir/f'infographic-slide{n:02d}.png'
                a.crop((x1,y1,x2,y2)).save(p,'PNG',optimize=True)
                files.append(p);n+=1
        css=list(w.rglob('style-v2.css')) or list(w.rglob('*.css'))
        if not css:raise SystemExit('CSS not found')
        c=css[0];t=c.read_text(encoding='utf-8')
        rule='\n/*JEMIX_ATLAS*/.lesson-infographic-wrap{width:100%;margin:14px 0 4px;display:flex;justify-content:center}.lesson-infographic{display:block;width:100%;max-width:1180px;max-height:610px;object-fit:contain;border-radius:16px}.content>.wide{padding:14px 18px!important}.wide.jemix-infographic-screen>*:not(.audio-card):not(.lesson-infographic-wrap){display:none!important}\n'
        if '/*JEMIX_ATLAS*/' not in t:c.write_text(t+rule,encoding='utf-8')
        pat=re.compile(r'(<section\b[^>]*class=["\'][^"\']*\bwide\b[^"\']*["\'][^>]*>)',re.I)
        for i,s in enumerate(slides,1):
            h=s.read_text(encoding='utf-8');m=pat.search(h)
            if not m:raise SystemExit(f'Wide section not found in {s.name}')
            op=m.group(1)
            if i not in INTERACTIVE and 'jemix-infographic-screen' not in op:
                op=re.sub(r'class=(["\'])([^"\']*)\1',lambda x:f'class={x.group(1)}{x.group(2)} jemix-infographic-screen{x.group(1)}',op,1)
            block=f'<div class="lesson-infographic-wrap"><img class="lesson-infographic" src="img/infographic-slide{i:02d}.png" alt="Инфографика к экрану {i}"></div>'
            h=h[:m.start()]+op+block+h[m.end():];s.write_text(h,encoding='utf-8')
        man=list(w.rglob('imsmanifest.xml'))
        if not man:raise SystemExit('imsmanifest.xml not found')
        m=man[0];t=m.read_text(encoding='utf-8')
        if 'img/infographic-slide01.png' not in t:
            e='\n'.join(f'      <file href="img/{p.name}"/>' for p in files)
            t=t.replace('</resource>',e+'\n    </resource>',1);m.write_text(t,encoding='utf-8')
        OUT.parent.mkdir(parents=True,exist_ok=True);OUT.unlink(missing_ok=True)
        with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
            for p in w.rglob('*'):
                if p.is_file():z.write(p,p.relative_to(w).as_posix())
    print('OK:',OUT)
    print('Atlas split into 20 images and inserted into the lesson')
    print('Audio, quizzes, navigation and SCORM files preserved')

if __name__=='__main__':main()
