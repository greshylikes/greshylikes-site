#!/usr/bin/env python3
"""Rebuild generated static HTML whenever data/site.js or data/products.js changes.

No pip installations needed. Leave this terminal running while editing locally.
"""
from __future__ import annotations
import hashlib
import pathlib
import sys
import time
import os
import webbrowser
import json
import secrets
from threading import RLock
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import build

INPUTS = (ROOT / 'data' / 'products.js', ROOT / 'data' / 'site.js')
BUILD_LOCK = RLock()
EDITOR_TOKEN = secrets.token_urlsafe(32)


class LocalHandler(SimpleHTTPRequestHandler):
    def send_json(self, status, value):
        body = json.dumps(value).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/api/editor':
            self.send_json(200, {'token': EDITOR_TOKEN})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path not in ('/api/save', '/api/upload-image'):
            self.send_json(404, {'error': 'Unknown endpoint.'})
            return
        if (self.headers.get('Origin') != 'http://127.0.0.1:8765'
                or self.headers.get('X-Editor-Token') != EDITOR_TOKEN):
            self.send_json(403, {'error': 'Open the editor from the local updater to save.'})
            return
        if self.path == '/api/upload-image':
            self.upload_image()
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 2_000_000:
                raise ValueError('Invalid save size.')
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict) or not payload or set(payload) - {'products', 'site'}:
                raise ValueError('Expected product or website data.')
            if 'products' in payload:
                if not isinstance(payload['products'], list):
                    raise ValueError('Products must be a list.')
                ids = set()
                for product in payload['products']:
                    if not isinstance(product, dict):
                        raise ValueError('Invalid product.')
                    ident = product.get('id', '')
                    if (not isinstance(ident, str) or not ident or
                            any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in ident) or ident in ids):
                        raise ValueError('Product IDs must be unique lowercase letters, numbers and hyphens.')
                    ids.add(ident)
                    if not str(product.get('name', '')).strip() or not str(product.get('category', '')).strip():
                        raise ValueError('Every product needs a name and category.')
            if 'site' in payload and not isinstance(payload['site'], dict):
                raise ValueError('Website data must be an object.')
            with BUILD_LOCK:
                for key, value in payload.items():
                    path = ROOT / 'data' / (key + '.js')
                    variable = 'GRESHY_PRODUCTS' if key == 'products' else 'GRESHY_SITE'
                    temporary = path.with_suffix('.js.tmp')
                    temporary.write_text('// Editable website data.\nwindow.' + variable + ' = ' +
                                         json.dumps(value, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
                    temporary.replace(path)
                try:
                    build()
                except Exception as exc:
                    self.send_json(500, {'error': 'Data saved, but the website rebuild failed: ' + str(exc)})
                    return
            self.send_json(200, {'message': 'Saved. Homepage, product pages, sitemap and dist/ are updated.'})
        except (ValueError, TypeError) as exc:
            self.send_json(400, {'error': str(exc)})
        except Exception as exc:
            self.send_json(500, {'error': 'Could not save: ' + str(exc)})

    def upload_image(self):
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 10 * 1024 * 1024:
                raise ValueError('Choose an image smaller than 10 MB.')
            content = self.rfile.read(length)
            if len(content) != length:
                raise ValueError('The image upload was incomplete. Please try again.')
            if content.startswith(b'\x89PNG\r\n\x1a\n'):
                extension = '.png'
            elif content.startswith(b'\xff\xd8\xff'):
                extension = '.jpg'
            elif content.startswith((b'GIF87a', b'GIF89a')):
                extension = '.gif'
            elif content[:4] == b'RIFF' and content[8:12] == b'WEBP':
                extension = '.webp'
            else:
                raise ValueError('Choose a PNG, JPG, WebP or GIF image.')
            # Ignore the client filename; unique names preserve existing photos.
            name = 'product-' + secrets.token_hex(12) + extension
            with BUILD_LOCK:
                folder = ROOT / 'assets' / 'images'
                folder.mkdir(parents=True, exist_ok=True)
                with (folder / name).open('xb') as output:
                    output.write(content)
            self.send_json(200, {'path': 'assets/images/' + name})
        except ValueError as exc:
            self.send_json(400, {'error': str(exc)})
        except Exception as exc:
            self.send_json(500, {'error': 'Could not upload image: ' + str(exc)})

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # the editor should not flood the update terminal


def start_preview():
    try:
        server = ThreadingHTTPServer(('127.0.0.1', 8765), partial(LocalHandler, directory=str(ROOT)))
        Thread(target=server.serve_forever, daemon=True).start()
        link = 'http://127.0.0.1:8765/tools/edit-content.html'
        print('Local editor: ' + link, flush=True)
        print('Local website: http://127.0.0.1:8765/', flush=True)
        if os.environ.get('AUTO_UPDATE_NO_BROWSER') != '1':
            webbrowser.open(link)
        return server
    except OSError as exc:
        print(f'Local preview could not start on port 8765: {exc}', flush=True)
        print('The automatic SEO builder will still run.', flush=True)
        return None


def signature():
    return tuple(hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None for p in INPUTS)


def main():
    print('Greshy Likes — automatic SEO page generator', flush=True)
    print('Watching data/products.js and data/site.js. Leave this window open.', flush=True)
    print('Press Ctrl+C to stop.', flush=True)
    current = signature()
    try:
        with BUILD_LOCK:
            build()
    except Exception as exc:
        print(f'Initial build error: {exc}. Fix the data files, and save again.', flush=True)
    start_preview()
    while True:
        try:
            time.sleep(0.8)
            found = signature()
            if found != current:
                current = found
                time.sleep(0.4)  # give file downloads/copies time to finish
                current = signature()
                try:
                    with BUILD_LOCK:
                        build()
                    print('Change detected; all product pages and sitemap are up to date.', flush=True)
                except Exception as exc:
                    print(f'Build error: {exc}. Previous pages were preserved where possible.', flush=True)
        except KeyboardInterrupt:
            print('\nStopped automatic updates.', flush=True)
            return


if __name__ == '__main__':
    main()
