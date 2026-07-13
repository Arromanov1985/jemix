#!/usr/bin/env python3
"""Collect product images from a TerraWater catalog page.

Examples:
  python scripts/fetch_terrawater_images.py \
      --url https://www.terrawater.ru/catalog/3 \
      --output academy-assets/catalog-3

Notes:
- Uses Playwright because the catalog can be rendered dynamically.
- Downloads image URLs found in src/data-src/srcset and product pages.
- Creates manifest.json with source URL, local filename and dimensions.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import mimetypes
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from PIL import Image
from playwright.async_api import async_playwright

IMAGE_EXTS={'.jpg','.jpeg','.png','.webp','.gif','.avif'}
SKIP_WORDS=('logo','icon','sprite','favicon','payment','social','banner','placeholder','loader')


def slug(text:str)->str:
    text=text.lower().strip()
    text=re.sub(r'[^a-z0-9а-яё]+','-',text,flags=re.I)
    return text.strip('-') or 'image'


def ext_from(url:str,content_type:str|None)->str:
    ext=Path(urlparse(url).path).suffix.lower()
    if ext in IMAGE_EXTS:
        return ext
    if content_type:
        guess=mimetypes.guess_extension(content_type.split(';')[0].strip())
        if guess in IMAGE_EXTS:
            return guess
    return '.jpg'


def candidate_name(url:str,alt:str)->str:
    base=slug(alt)[:80] if alt else slug(Path(urlparse(url).path).stem)[:80]
    digest=hashlib.sha1(url.encode('utf-8')).hexdigest()[:8]
    return f'{base}-{digest}'

async def collect_urls(page):
    urls=[]
    for img in await page.query_selector_all('img'):
        alt=(await img.get_attribute('alt') or '').strip()
        attrs=[]
        for attr in ('src','data-src','data-lazy-src','data-original'):
            v=await img.get_attribute(attr)
            if v: attrs.append(v)
        srcset=await img.get_attribute('srcset')
        if srcset:
            attrs.extend(x.strip().split(' ')[0] for x in srcset.split(',') if x.strip())
        for raw in attrs:
            url=urljoin(page.url,raw)
            low=url.lower()
            if any(w in low for w in SKIP_WORDS):
                continue
            urls.append({'url':url,'alt':alt,'page':page.url})
    return urls

async def product_links(page,base_host:str):
    links=set()
    for a in await page.query_selector_all('a[href]'):
        href=await a.get_attribute('href')
        if not href: continue
        url=urljoin(page.url,href)
        p=urlparse(url)
        if p.netloc!=base_host: continue
        if '/catalog/' in p.path and p.path.rstrip('/')!=urlparse(page.url).path.rstrip('/'):
            links.add(url.split('#')[0])
    return sorted(links)

async def download_all(items,outdir:Path):
    outdir.mkdir(parents=True,exist_ok=True)
    seen=set(); manifest=[]
    async with httpx.AsyncClient(follow_redirects=True,timeout=30,headers={'User-Agent':'Mozilla/5.0'}) as client:
        for item in items:
            url=item['url']
            if url in seen: continue
            seen.add(url)
            try:
                r=await client.get(url)
                r.raise_for_status()
                ctype=r.headers.get('content-type','')
                if not ctype.startswith('image/'):
                    continue
                ext=ext_from(url,ctype)
                name=candidate_name(url,item.get('alt',''))+ext
                path=outdir/name
                path.write_bytes(r.content)
                width=height=None
                try:
                    with Image.open(path) as im:
                        width,height=im.size
                    if width and height and width<300 and height<300:
                        path.unlink(missing_ok=True)
                        continue
                except Exception:
                    pass
                manifest.append({
                    'file':name,'source':url,'page':item.get('page'),
                    'alt':item.get('alt',''),'width':width,'height':height,
                    'bytes':len(r.content)
                })
                print('saved',name)
            except Exception as e:
                print('skip',url,e)
    (outdir/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'OK: {len(manifest)} images -> {outdir}')

async def main_async(args):
    outdir=Path(args.output)
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        page=await browser.new_page(viewport={'width':1440,'height':1200})
        await page.goto(args.url,wait_until='networkidle',timeout=90000)
        await page.wait_for_timeout(args.wait_ms)
        items=await collect_urls(page)
        if args.follow_products:
            host=urlparse(args.url).netloc
            links=await product_links(page,host)
            for link in links[:args.max_products]:
                try:
                    await page.goto(link,wait_until='networkidle',timeout=90000)
                    await page.wait_for_timeout(1200)
                    items.extend(await collect_urls(page))
                except Exception as e:
                    print('product skip',link,e)
        await browser.close()
    await download_all(items,outdir)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--url',default='https://www.terrawater.ru/catalog/3')
    ap.add_argument('--output',default='academy-assets/catalog-3')
    ap.add_argument('--wait-ms',type=int,default=2500)
    ap.add_argument('--follow-products',action='store_true',default=True)
    ap.add_argument('--max-products',type=int,default=80)
    args=ap.parse_args()
    asyncio.run(main_async(args))

if __name__=='__main__':
    main()
