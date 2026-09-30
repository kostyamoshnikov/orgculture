#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка всех внутренних ссылок и якорей сайта (RU + EN).

Зачем: у каждой страницы своя копия HTML (общего шаблона нет, всё
собирает gen.py), страниц около полусотни, и они плотно ссылаются друг
на друга — тексты ↔ теги ↔ проекты ↔ FAQ ↔ упоминания ↔ подвал. Битая
ссылка или ссылка на несуществующий якорь (#collab, #program) до сих
пор ловилась только глазами: HTML валиден, страница открывается,
ошибки нет — просто по клику 404 или прыжок в никуда.

Перенесено 30.09.2026 из пака AELITA v538 (_tools/Audit/check_links.py,
категория `links` их аудита; у них добавлено после того, как нашлись
ссылки на несуществующие id).

⚠️ Внешние ссылки НЕ проверяются сетью. Архив должен проверяться
офлайн и одинаково в любой момент: сеть сделала бы проверку то зелёной,
то красной по причинам, к архиву не относящимся. Внешние адреса — дело
ручной проверки по AUDIT-SCHEDULE.md.

Запуск:
    python3 03-website/check_links.py          # из корня архива
    python3 check_links.py                     # из 03-website
Код возврата: 0 — чисто, 1 — есть битые ссылки.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Схемы и префиксы, которые проверять нечем и не нужно.
SKIP_PREFIXES = (
    'http://', 'https://', 'mailto:', 'tel:', 'javascript:', 'data:',
    'tg://', '//',
)

# Файлы, которые лежат вне сайта и генерируются отдельно, но на них
# ссылаются страницы. Проверяются на существование по своему пути.
EXTRA_ROOTS = {
    # ссылка на сайте      : путь относительно корня архива
}


def iter_pages():
    """Все .html сайта, кроме служебных."""
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in ('assets', 'images', '__pycache__')]
        for fn in files:
            if fn.endswith('.html'):
                yield os.path.join(root, fn)


def page_ids(path, cache={}):
    """Все id= на странице (для проверки якорей)."""
    if path not in cache:
        try:
            html = open(path, encoding='utf-8').read()
        except OSError:
            cache[path] = set()
        else:
            cache[path] = set(re.findall(r'\sid="([^"]+)"', html))
    return cache[path]


def resolve(href, page):
    """href → путь на диске, который должен существовать.

    Возвращает (путь_или_None, якорь). Путь None — ссылку проверять не
    нужно (внешняя, почта и т. п.).
    """
    if not href or href.startswith(SKIP_PREFIXES) or href == '#':
        return None, None

    anchor = ''
    if '#' in href:
        href, anchor = href.split('#', 1)
    # Кэш-бастинг вида style.css?v=64 — часть адреса, а не файла:
    # без этого проверка ругалась бы на каждую страницу дважды.
    if '?' in href:
        href = href.split('?', 1)[0]

    if href == '':                      # ссылка вида "#program" — на себя
        return page, anchor

    if href.startswith('/'):
        target = os.path.join(HERE, href.lstrip('/'))
    else:
        target = os.path.normpath(os.path.join(os.path.dirname(page), href))

    # каталог → index.html внутри него
    if href.endswith('/') or os.path.isdir(target):
        target = os.path.join(target, 'index.html')

    return target, anchor


def main():
    problems = []
    pages = sorted(iter_pages())
    checked = 0

    for page in pages:
        html = open(page, encoding='utf-8').read()
        rel_page = os.path.relpath(page, HERE)
        for m in re.finditer(r'(?:href|src)="([^"]*)"', html):
            href = m.group(1)
            target, anchor = resolve(href, page)
            if target is None:
                continue
            checked += 1
            if not os.path.exists(target):
                problems.append(f'{rel_page}: ссылка «{href}» ведёт в никуда '
                                f'(нет файла {os.path.relpath(target, HERE)})')
                continue
            if anchor and target.endswith('.html'):
                if anchor not in page_ids(target):
                    problems.append(f'{rel_page}: якорь «#{anchor}» отсутствует '
                                    f'на {os.path.relpath(target, HERE)}')

    print(f'Проверено {checked} внутренних ссылок на {len(pages)} страницах.')
    if problems:
        print(f'\nБИТЫЕ ССЫЛКИ: {len(problems)}')
        for p in problems:
            print('  •', p)
        return 1
    print('чисто')
    return 0


if __name__ == '__main__':
    sys.exit(main())
