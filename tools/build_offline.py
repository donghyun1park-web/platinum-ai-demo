#!/usr/bin/env python3
"""소스 HTML을 외부 CDN 없이 동작하는 단일 HTML로 빌드합니다.

사용법:
  python tools/build_offline.py src/the_platinum_ai_simulator_v3.html index.html
  python tools/build_offline.py SRC OUT --badge "오프라인 내장판" --title-suffix " (오프라인)"

- Three.js r165 모듈을 import map의 data: URL로, qrcode-generator 1.4.4를 인라인으로 넣습니다.
- 필요한 라이브러리는 버전을 고정해 tools/.vendor 에 한 번 내려받고 SHA-256으로 검증합니다.
- Gemini API 호출과 Google 글꼴만 인터넷을 씁니다(글꼴은 없으면 기본 글꼴로 대체).
"""
import argparse
import base64
import hashlib
import json
import os
import sys
import urllib.request

THREE = 'https://cdn.jsdelivr.net/npm/three@0.165.0/'
VENDOR = {
    # 상대 경로: (내려받을 URL, SHA-256)
    'build/three.module.min.js': (THREE + 'build/three.module.min.js', '1af5bef9a9fd79fcb73fcfd3e4dd2ac0cea8720205bc7607d67369ce194a87fa'),
    'examples/jsm/geometries/RoundedBoxGeometry.js': (THREE + 'examples/jsm/geometries/RoundedBoxGeometry.js', 'd20aeaf7077c459a8d952d215738d7b44fba028440bb862d84b622a34f0c80bb'),
    'examples/jsm/environments/RoomEnvironment.js': (THREE + 'examples/jsm/environments/RoomEnvironment.js', 'e1b92c4dd2d89752293546790bfda9828a630a79700c66f5b736fad7a88cb7e4'),
    'examples/jsm/lights/RectAreaLightUniformsLib.js': (THREE + 'examples/jsm/lights/RectAreaLightUniformsLib.js', '08085bc942253cd54948bf936fecb66b54514a135872656e475a1cab09b55214'),
    'examples/jsm/controls/OrbitControls.js': (THREE + 'examples/jsm/controls/OrbitControls.js', 'f260591ef315aa04888152e7f121865214e33fb54727145cf4e4445058db1297'),
    'examples/jsm/renderers/CSS2DRenderer.js': (THREE + 'examples/jsm/renderers/CSS2DRenderer.js', 'e900e58dbc428d8d3211f87f3ff0301e514f6dc563655c710bcda15c96397feb'),
    'qrcode.min.js': ('https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js', '164fc2c1c9eaf0a03aa8dfdb855e82e41a5c6922fbad8bb3238116207e26bef7'),
}
IMPORTS = {
    'three': 'build/three.module.min.js',
    'three/addons/geometries/RoundedBoxGeometry.js': 'examples/jsm/geometries/RoundedBoxGeometry.js',
    'three/addons/environments/RoomEnvironment.js': 'examples/jsm/environments/RoomEnvironment.js',
    'three/addons/lights/RectAreaLightUniformsLib.js': 'examples/jsm/lights/RectAreaLightUniformsLib.js',
    'three/addons/controls/OrbitControls.js': 'examples/jsm/controls/OrbitControls.js',
    'three/addons/renderers/CSS2DRenderer.js': 'examples/jsm/renderers/CSS2DRenderer.js',
}
CDN_IMPORTMAP = ('<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.165.0/build/three.module.js",'
                 '"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.165.0/examples/jsm/"}}</script>')
CDN_QR = '<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"></script>'


def ensure_vendor(vdir):
    for rel, (url, sha) in VENDOR.items():
        path = os.path.join(vdir, rel)
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            print('download', url)
            with urllib.request.urlopen(url, timeout=60) as r:
                data = r.read()
            with open(path, 'wb') as f:
                f.write(data)
        with open(path, 'rb') as f:
            got = hashlib.sha256(f.read()).hexdigest()
        if got != sha:
            sys.exit(f'hash mismatch for {rel}: {got} (expected {sha}) — delete the file and retry')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('out')
    ap.add_argument('--vendor', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.vendor'))
    ap.add_argument('--badge', default='')
    ap.add_argument('--title-suffix', default='')
    a = ap.parse_args()

    ensure_vendor(a.vendor)
    with open(a.src, encoding='utf-8') as f:
        h = f.read()

    def rep(old, new):
        nonlocal h
        if h.count(old) != 1:
            sys.exit(f'expected exactly one occurrence of: {old[:70]}')
        h = h.replace(old, new)

    def data_url(rel):
        with open(os.path.join(a.vendor, rel), 'rb') as f:
            return 'data:text/javascript;base64,' + base64.b64encode(f.read()).decode()

    imports = {spec: data_url(rel) for spec, rel in IMPORTS.items()}
    rep(CDN_IMPORTMAP, '<!-- Three.js r165 (MIT License, three.js authors) embedded — see THIRD_PARTY_NOTICES.md -->\n'
        '<script type="importmap">' + json.dumps({'imports': imports}) + '</script>')
    with open(os.path.join(a.vendor, 'qrcode.min.js'), encoding='utf-8') as f:
        qr = f.read().replace('</script', '<\\/script')
    rep(CDN_QR, '<!-- qrcode-generator 1.4.4 (MIT License, Kazuhiko Arase) embedded — see THIRD_PARTY_NOTICES.md -->\n<script>' + qr + '</script>')
    rep("font-family:'Noto Sans KR',system-ui", "font-family:'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',system-ui")
    rep('3D 엔진을 불러오지 못했습니다 (인터넷 연결 필요).', '3D 엔진을 시작하지 못했습니다 (WebGL 지원 브라우저 필요: 크롬·엣지·사파리 최신 버전).')
    rep('키가 없으면 3D 렌더와 오프라인 미리보기로 시연합니다.', '키가 없거나 인터넷이 없으면 3D 렌더와 오프라인 미리보기로 시연합니다. (AI 변환만 인터넷 필요)')
    if a.title_suffix:
        rep('<title>더 플래티넘 AI 체험관</title>', '<title>더 플래티넘 AI 체험관' + a.title_suffix + '</title>')
    if a.badge:
        rep('<span class="pill g">사내 경진대회 시연 키트 v3</span>',
            '<span class="pill g">사내 경진대회 시연 키트 v3</span><span class="pill sky">' + a.badge + '</span>')

    with open(a.out, 'w', encoding='utf-8') as f:
        f.write(h)
    print(f'wrote {a.out} ({len(h.encode("utf-8")):,} bytes)')


if __name__ == '__main__':
    main()
