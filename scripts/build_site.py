#!/usr/bin/env python3
"""Build all static SEO pages from data/*.js and export a deployable dist/ folder."""
from __future__ import annotations
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from rebuild_seo import rebuild

PUBLIC_FILES = ('index.html', 'privacy.html', 'terms.html', 'robots.txt', 'sitemap.xml')
PUBLIC_DIRS = ('assets', 'css', 'data', 'js', 'products', 'perfumes', 'personal-care', 'car-fragrance')


def build():
    rebuild()
    dest = ROOT / 'dist'
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir()
    for name in PUBLIC_FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, dest / name)
    for name in PUBLIC_DIRS:
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, dest / name)
    print(f'Public deployment files exported to {dest}')
    print('The editor and build scripts are NOT included in the published site.')
    return dest


if __name__ == '__main__':
    build()
