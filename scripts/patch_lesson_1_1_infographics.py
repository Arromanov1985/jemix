#!/usr/bin/env python3
from pathlib import Path
import re, tempfile, zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'dist/module-01/JEMIX_Academy_1_1_SCORM_UX_v2_FINAL_WITH_JEMIX_PUMPS.zip'
ATLAS = ROOT / 'dist/module-01/JEMIX_Academy_1_1_INFOGRAPHICS_ATLAS.png'
OUT = ROOT / 'dist/module-01/JEMIX_Academy_1_1_SCORM_INFOGRAPHICS_FINAL.zip'
INTERACTIVE = {6, 9, 16, 18, 19}


def crop_tiles(atlas_path, out_dir):
    atlas = Image.open(atlas_path).convert('RGB')
    width, height = atlas.size
    for index in range(20):
        col, row = index % 5, index // 5
        x0, x1 = round(col * width / 5), round((col + 1) * width / 5)
        y0, y1 = round(row * height / 4), round((row + 1) * height / 4)
        cell = atlas.crop((x0, y0, x1, y1))
        cw, ch = cell.size
        # Берем центральную учебную область: без нарисованного сайдбара,
        # верхнего прогресса и нижнего плеера из макета.
        visual = cell.crop((round(cw * 0.28), round(ch * 0.14),
                            round(cw * 0.985), round(ch * 0.79)))
        visual.save(out_dir / f'atlas-slide{index + 1:02d}.png', optimize=True)


def main():
    if not SRC.exists():
        raise SystemExit(f'SCORM not found: {SRC}')
    if not ATLAS.exists():
        raise SystemExit(f'Atlas not found: {ATLAS}')

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        with zipfile.ZipFile(SRC) as archive:
            archive.extractall(work)

        slides = sorted(work.rglob('slide[0-9][0-9].html'))
        if len(slides) != 20:
            raise SystemExit(f'Expected 20 slides, found {len(slides)}')

        image_dir = work / 'img'
        image_dir.mkdir(exist_ok=True)
        crop_tiles(ATLAS, image_dir)

        css_files = list(work.rglob('style-v2.css'))
        if not css_files:
            raise SystemExit('style-v2.css not found')
        css = css_files[0]
        css_text = css.read_text(encoding='utf-8')
        rule = ('\n.atlas-visual{width:100%;margin:14px 0 6px;text-align:center}'
                '.atlas-visual img{display:block;width:100%;max-height:520px;'
                'object-fit:contain;border-radius:16px;background:#fff}'
                '.content>.wide{padding:16px!important}\n')
        if '.atlas-visual{' not in css_text:
            css.write_text(css_text + rule, encoding='utf-8')

        pattern = re.compile(
            r'(<div class="audio-card".*?<audio\b.*?</audio></div>)(.*?)(</section></main>)',
            re.S)

        for number, slide in enumerate(slides, 1):
            html = slide.read_text(encoding='utf-8')
            block = (f'<div class="atlas-visual"><img src="img/atlas-slide{number:02d}.png" '
                     f'alt="Инфографика экрана {number}"></div>')
            match = pattern.search(html)
            if not match:
                raise SystemExit(f'Content block not found in {slide.name}')
            if number in INTERACTIVE:
                replacement = match.group(1) + block + match.group(2) + match.group(3)
            else:
                replacement = match.group(1) + block + match.group(3)
            html = html[:match.start()] + replacement + html[match.end():]
            slide.write_text(html, encoding='utf-8')

        manifest = work / 'imsmanifest.xml'
        if manifest.exists():
            text = manifest.read_text(encoding='utf-8')
            if 'img/atlas-slide01.png' not in text:
                files = '\n'.join(
                    f'      <file href="img/atlas-slide{i:02d}.png"/>'
                    for i in range(1, 21)
                )
                text = text.replace('</resource>', files + '\n    </resource>', 1)
                manifest.write_text(text, encoding='utf-8')

        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.unlink(missing_ok=True)
        with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as archive:
            for file in work.rglob('*'):
                if file.is_file():
                    archive.write(file, file.relative_to(work).as_posix())

    print('OK:', OUT)
    print('Atlas split into 20 visuals and inserted into the lesson')
    print('Audio, quizzes, navigation and SCORM logic preserved')


if __name__ == '__main__':
    main()
