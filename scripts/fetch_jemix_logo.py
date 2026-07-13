#!/usr/bin/env python3
"""Find and download the original JEMIX logo from TerraWater pages.

Usage:
  python scripts/fetch_jemix_logo.py \
      --url https://www.terrawater.ru/catalog/3 \
      --output academy-assets/logo/jemix-logo.png

The script only accepts candidates whose URL or alt text contains JEMIX/ДЖЕМИКС
and strongly prefers filenames/alt text containing logo/логотип. It does not
redraw, approximate, or generate the logo.
"""
from __future__ import