#!/usr/bin/env python3
"""Build the static assembly page. Optionally import a saved photo arrangement."""
import argparse
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site/assembly.json'
REPO = 'https://github.com/yuchamichami/CoreX-Proto-RMK'


def text(value):
    return html.escape(str(value), quote=True)


def prose(value):
    pieces, cursor = [], 0
    for match in re.finditer(r'\[([^\]]+)\]\((https://[^)]+)\)', value):
        pieces += [text(value[cursor:match.start()]), f'<a href="{text(match[2])}">{text(match[1])}</a>']
        cursor = match.end()
    pieces.append(text(value[cursor:]))
    return ''.join(pieces).replace('\n', '<br>')


def body(section):
    result = [f'<p>{prose(p)}</p>' for p in section.get('paragraphs', [])]
    if section.get('bullets'):
        result.append('<ul class="supplies">' + ''.join(f'<li>{prose(p)}</li>' for p in section['bullets']) + '</ul>')
    if section.get('steps'):
        result.append('<ol class="steps">' + ''.join(f'<li>{prose(p)}</li>' for p in section['steps']) + '</ol>')
    if section.get('notes'):
        result.append('<div class="notes">' + ''.join(f'<p>{prose(p)}</p>' for p in section['notes']) + '</div>')
    return '<div class="instructions">' + ''.join(result) + '</div>'


def build(data):
    ids = {s['id'] for s in data['sections']}
    photos = data['photos']
    assert len({p['id'] for p in photos}) == len(photos), 'Duplicate photo'
    assert all(p['section'] in ids for p in photos), 'Unknown section'
    assert all(Path(p['file']).name == p['file'] for p in photos), 'Invalid photo filename'
    assert all((ROOT / 'docs/images/assembly' / p['file']).is_file() for p in photos), 'Missing photo'
    intro = f'<div class="intro"><p class="eyebrow">ASSEMBLY GUIDE</p><h1>CoreX 組み立てガイド</h1><p>{prose(data["intro"])}</p></div>'
    sections = [dict(data['preparation'], id='prepare', number='準備')]
    for i, section in enumerate(data['sections']):
        if section['id'] == 'extra':
            sections.append(dict(data['finish'], id='pairing', number='06'))
            sections.append(dict(section, number='補足'))
        else:
            sections.append(dict(section, number=f'{i+1:02}'))
    navigation, content, photo_number = [], [], 0
    short = {'trackball':'トラボを接続する', 'pairing':'左右をつなぐ'}
    for section in sections:
        label = short.get(section['id'], section['title'])
        navigation.append(f'<a class="nav-item" href="#{section["id"]}"><span>{text(label)}</span></a>')
        block = f'<section id="{section["id"]}" class="section"><div class="section-heading"><span class="section-number">{text(section["number"])}</span><h2>{text(section["title"])}</h2></div>{body(section)}'
        cards = []
        for photo in [p for p in photos if p['section'] == section['id']]:
            photo_number += 1
            image = 'images/assembly/' + photo['file']
            cards.append(f'''<figure class="photo-card" id="{text(photo['id'])}">
<a class="photo-open" href="{text(image)}" aria-label="{text(photo['title'])}：写真を拡大">
<img src="{text(image)}" alt="{text(photo['title'])}" loading="lazy" decoding="async"><span class="photo-number">{photo_number:02}</span><span class="zoom-label">拡大</span></a>
<figcaption><h3>{text(photo['title'])}</h3><p>{prose(photo['caption'])}</p></figcaption></figure>''')
        if cards:
            block += '<div class="grid">' + ''.join(cards) + '</div>'
        content.append(block + '</section>')
    return f'''<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CoreX 組み立てガイド</title>
<meta name="description" content="CoreXプロトタイプの組み立て方。写真で基板交換、トラックボールの接続、左右のペアリングを案内します。">
<link rel="canonical" href="https://yuchamichami.github.io/CoreX-Proto-RMK/">
<link rel="icon" href="site/logo.svg" type="image/svg+xml"><link rel="stylesheet" href="site/style.css"><script src="site/app.js" defer></script></head>
<body><a class="skip-link" href="#main">本文へ移動</a>
<header class="topbar"><a class="brand" href="#"><img src="site/logo.svg" alt="CoreX"><span>組み立てガイド</span></a><div class="header-links"><a href="{REPO}/blob/main/docs/usage.md">使い方・設定</a><a href="{REPO}" class="repo-link">GitHub ↗</a></div></header>
<div class="workspace"><aside><p class="aside-label">組み立ての流れ</p><nav aria-label="工程">{''.join(navigation)}</nav><p class="aside-help">写真はクリックで拡大できます。</p></aside>
<main id="main">{intro}{''.join(content)}
<footer><a href="{REPO}">CoreX-Proto-RMK</a><span>文字：Zen Maru Gothic · <a href="site/fonts/OFL.txt">OFL</a></span><a href="#">上へ戻る ↑</a></footer></main></div>
<dialog id="lightbox" aria-label="写真の拡大"><form method="dialog"><button aria-label="写真を閉じる">閉じる ×</button></form><img alt=""><p></p></dialog>
</body></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--arrangement', type=Path, help='Import captions/order from the local photo editor')
    parser.add_argument('--check', action='store_true', help='Fail if the generated page is out of date')
    args = parser.parse_args()
    data = json.loads(SOURCE.read_text())
    if args.arrangement:
        assert not args.check, 'Use --arrangement or --check separately'
        arrangement = json.loads(args.arrangement.read_text())
        data['photos'] = [p for p in arrangement['items'] if p['section'] != 'spare']
    result = build(data)
    target = ROOT / 'docs/index.html'
    if args.check:
        assert target.read_text() == result, 'Run python3 tools/build_assembly_site.py'
        print('PASS assembly page: source, photos and generated HTML')
    else:
        if args.arrangement:
            SOURCE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        target.write_text(result)
        print('Built docs/index.html')


if __name__ == '__main__':
    main()
