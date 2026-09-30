#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Отчёт: есть ли на первом экране телефона кнопка или ссылка-действие.

Зачем. Человек открывает страницу с телефона и видит примерно 640
пикселей по высоте. Если в них нет ни одного действия — только
заголовок и начало текста, — уйти со страницы проще, чем долистать.
У AELITA это проверено на 162 страницах (pack-v510) и дало «0 страниц
без кнопки»; у нас не проверялось никогда, а страниц с длинным
вступлением хватает.

⚠️ ЭТО ОТЧЁТ, А НЕ ПРОВЕРКА. Скрипт не открывает браузер и не считает
реальную высоту: он оценивает её по разметке — сколько крупных блоков
идёт до первого действия. Оценка грубая и намеренно занижена в пользу
«скорее всё хорошо»: попасть в список должна страница, где действия
заведомо далеко, а не та, где оно на границе. Поэтому код возврата
всегда 0 и в check_archive.py скрипт не подключён: он даёт список
кандидатов для глаз, а не приговор.

«Действие» — это ссылка-кнопка (.btn-line), ссылка на форму, бота, КП,
почту или другой раздел в основном содержании. Меню в шапке, логотип и
переключатель языка не считаются: они есть на каждой странице и
действием по смыслу страницы не являются.

Запуск:
    python3 03-website/check_first_screen.py          # из корня архива
    python3 03-website/check_first_screen.py --all    # показать все страницы
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Примерная высота первого экрана телефона в пикселях (iPhone SE/8 —
# самый маленький из живых). Берём с запасом в меньшую сторону.
FIRST_SCREEN_PX = 620

# Грубые высоты блоков. Считать точно нельзя без браузера, но порядок
# величин достаточен, чтобы отделить «кнопка в первом экране» от
# «кнопка после двух абзацев и картинки».
WEIGHTS = [
    (r'<header[^>]*>', 64),          # шапка сайта
    (r'<h1[^>]*>', 90),
    (r'<h2[^>]*>', 54),
    (r'<h3[^>]*>', 40),
    (r'<p[^>]*>', 58),               # абзац в две-три строки на телефоне
    (r'<img[^>]*>', 200),
    (r'<div class="eyebrow"', 30),
    (r'<ul[^>]*>', 40),
    (r'<li[^>]*>', 26),
    (r'<table[^>]*>', 120),
]

ACTION = re.compile(
    r'<a\s[^>]*(?:class="[^"]*btn-line|href="(?:mailto:|https://t\.me/|[^"]*\.pdf|[^"]*#brief))',
    re.I)

SKIP = {'404.html', 'offline.html'}
SKIP_DIRS = {'assets', 'images', '__pycache__', '_redirect-for-online-domain'}

# ⚠️ Страницы текстов исключены намеренно, и это не поблажка.
# Первый прогон (30.09.2026) отметил 110 страниц из 116 — и 104 из них
# были текстами. Это не находка, а свойство жанра: у статьи действие
# стоит в конце, потому что до конца её и читают; кнопка «написать»
# в первом экране рецензии на спектакль мешала бы, а не помогала.
# Проверка имеет смысл там, где страница должна к чему-то привести:
# главная, об авторе, продюсирование, проекты, контакты, пресса, FAQ,
# манифест, рекомендации, упоминания. Оставь тексты — и отчёт из
# инструмента превращается в шум, который перестают открывать.
SKIP_TEXT_PAGES = True


def main_content(html):
    """Содержимое страницы без шапки и подвала.

    Тега <main> на части страниц нет (разметка у каждой своя, общего
    шаблона нет), поэтому не полагаемся на него: режем от конца шапки
    до начала подвала. Первая версия брала «первый <section> до
    <footer>» и на страницах без <main> обрезала содержимое на первой
    же секции — отчёт показывал «нет действий» там, где их четыре.
    """
    start = 0
    m = re.search(r'</header>', html)
    if m:
        start = m.end()
    end = len(html)
    m = re.search(r'<footer', html[start:])
    if m:
        end = start + m.start()
    return html[start:end]


def first_action_offset(html):
    """Примерная высота в пикселях до первого действия. None — действий нет."""
    body = main_content(html)
    m = ACTION.search(body)
    if not m:
        return None
    before = body[:m.start()]
    px = 64  # шапка
    for pattern, weight in WEIGHTS:
        px += len(re.findall(pattern, before)) * weight
    return px


def main():
    show_all = '--all' in sys.argv
    rows = []
    for dirpath, dirnames, filenames in os.walk(HERE):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith('.html') or fn in SKIP:
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, HERE).replace(os.sep, '/')
            if SKIP_TEXT_PAGES and ('/texts/' in '/' + rel) and rel.count('/') >= 2:
                continue
            px = first_action_offset(open(path, encoding='utf-8').read())
            rows.append((rel, px))

    far = [(r, p) for r, p in rows if p is None or p > FIRST_SCREEN_PX]
    print(f'Страниц просмотрено: {len(rows)}. Порог первого экрана: {FIRST_SCREEN_PX}px.')
    if show_all:
        for rel, px in sorted(rows, key=lambda x: (x[1] is not None, x[1] or 0)):
            print(f'   {("нет действий" if px is None else str(px) + "px"):>14}  {rel}')
    elif far:
        print(f'\nКандидаты на проверку глазами — действие далеко или его нет ({len(far)}):')
        for rel, px in sorted(far, key=lambda x: (x[1] is None, -(x[1] or 0))):
            print(f'   {("нет действий" if px is None else "~" + str(px) + "px"):>14}  {rel}')
        print('\nЭто оценка по разметке, а не замер в браузере: открыть эти')
        print('страницы на телефоне и посмотреть, видно ли действие без прокрутки.')
    else:
        print('\nНа всех страницах действие попадает в первый экран (по оценке).')

    dead = [r for r, p_ in rows if p_ is None]
    if dead:
        print('\nОтдельно: страницы, где действия нет вообще — ни в первом')
        print('экране, ни ниже. Это уже не про геометрию, а про то, куда')
        print('человеку идти после прочтения:')
        for rel in sorted(dead):
            print('   •', rel)
    return 0


if __name__ == '__main__':
    sys.exit(main())
