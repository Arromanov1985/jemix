#!/usr/bin/env python3
"""Find and download the original JEMIX logo from TerraWater pages.

Usage:
  python scripts/fetch_jemix_logo.py \
      --url https://www.terrawater.ru/catalog/3 \
      --output academy-assets/logo/jemix-logo.png

Only candidates whose URL or alt text contains JEMIX/ДЖЕМИКС are accepted.
The script prefers filenames or alt text containing logo/логотип and never
redraws, approximates, or generates the logo.
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from urllib.parse import urljoin

import httpx
from PIL import Image
from playwright.async_api import async_playwright


def candidate_score(url: str, alt: str) -> int:
    text = f"{url} {alt}".lower()
    if "jemix" not in text and "джемикс" not in text:
        return -10_000
    score = 100
    if "logo" in text or "логотип" in text:
        score += 100
    if any(ext in url.lower() for ext in (".png", ".webp", ".svg")):
        score += 20
    if any(word in text for word in ("icon", "favicon", "sprite", "banner")):
        score -= 80
    return score


async def collect_candidates(page) -> list[dict]:
    candidates: list[dict] = []
    for img in await page.query_selector_all("img"):
        alt = (await img.get_attribute("alt") or "").strip()
        for attr in ("src", "data-src", "data-lazy-src", "data-original"):
            raw = await img.get_attribute(attr)
            if raw:
                url = urljoin(page.url, raw)
                candidates.append({"url": url, "alt": alt, "score": candidate_score(url, alt)})
    return candidates


async def download_best(url: str, output: Path) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 1200})
        await page.goto(url, wait_until="networkidle", timeout=90_000)
        await page.wait_for_timeout(2500)
        candidates = await collect_candidates(page)
        await browser.close()

    candidates = [c for c in candidates if c["score"] > 0]
    if not candidates:
        raise SystemExit("No exact JEMIX logo candidate found on the page")
    candidates.sort(key=lambda x: x["score"], reverse=True)

    async with httpx.AsyncClient(follow_redirects=True, timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as client:
        last_error: Exception | None = None
        for candidate in candidates:
            try:
                response = await client.get(candidate["url"])
                response.raise_for_status()
                if not response.headers.get("content-type", "").startswith("image/"):
                    continue
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(response.content)
                with Image.open(output) as image:
                    width, height = image.size
                if width < 120 or height < 30:
                    output.unlink(missing_ok=True)
                    continue
                print(f"OK: {candidate['url']} -> {output} ({width}x{height})")
                return
            except Exception as exc:
                last_error = exc
                output.unlink(missing_ok=True)
        raise SystemExit(f"Failed to download a valid JEMIX logo: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://www.terrawater.ru/catalog/3")
    parser.add_argument("--output", default="academy-assets/logo/jemix-logo.png")
    args = parser.parse_args()
    asyncio.run(download_best(args.url, Path(args.output)))


if __name__ == "__main__":
    main()
