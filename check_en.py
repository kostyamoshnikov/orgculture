#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_en.py — проверка английской версии orgculture.ru.

Идея и структура (4 проверки, код возврата 1 при замечаниях) перенесены
из AELITA_pack (_tools/DesignSystem/i18n/check_i18n.py) — там этот
формат реально ловил расхождения при разборе разрывов смысла в
переводе AELITA. Механика другая: AELITA переводит по словарю "узел
DOM → перевод", orgculture переводит текст целиком, вручную, абзац за
абзацем (см. README.md, история v20–v22). Поэтому и промахи там были
другого типа — здесь у этой проверки другая задача: не «нашёлся ли
перевод», а «не разошлось ли что-то при следующей правке одного
текста без сверки с остальными».

Запускать из 03-website/ после любой правки TEXTS в gen.py или
texts_en.json:

    python3 check_en.py

Код возврата 1 при любых замечаниях — годится для ручной проверки
перед коммитом, не завязан на CI (у проекта его нет).
"""
import os, re, json, runpy, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

CYRILLIC = re.compile(r'[а-яёА-ЯЁ]')
ISSUES = []


def issue(section, msg):
    ISSUES.append((section, msg))


# ─────────────────────────────────────────────── загрузка данных ───
ns = runpy.run_path('gen.py')
TEXTS_RU = ns['TEXTS']
ru_by_slug = {t['slug']: t for t in TEXTS_RU}

if not os.path.isfile('texts_en.json'):
    print('texts_en.json не найден — английская версия не собрана.')
    sys.exit(1)

TEXTS_EN = json.load(open('texts_en.json', encoding='utf-8'))
en_by_slug = {t['slug']: t for t in TEXTS_EN}

glossary = {}
if os.path.isfile('glossary_en.json'):
    glossary = json.load(open('glossary_en.json', encoding='utf-8'))


# ───────────────────────────────────────── 1. пропуски и полнота ───
def check_gaps():
    ru_slugs = set(ru_by_slug)
    en_slugs = set(en_by_slug)

    missing = ru_slugs - en_slugs
    for slug in sorted(missing):
        issue('gaps', f'{slug}: есть в TEXTS (gen.py), нет в texts_en.json — '
                       f'на английском сайте текст просто не появится, без ошибки сборки')

    orphaned = en_slugs - ru_slugs
    for slug in sorted(orphaned):
        issue('gaps', f'{slug}: есть в texts_en.json, нет в TEXTS — мёртвая запись, '
                       f'gen_en.py её тихо пропустит')

    for slug in sorted(ru_slugs & en_slugs):
        ru, en = ru_by_slug[slug], en_by_slug[slug]
        if len(ru['paragraphs']) != len(en['paragraphs']):
            issue('gaps', f'{slug}: {len(ru["paragraphs"])} абзацев в RU, '
                          f'{len(en["paragraphs"])} в EN — перевод не покрывает весь текст '
                          f'(именно так выглядели 6 из 10 багов в AELITA — русский ключ '
                          f'длиннее английского значения)')
        if (ru.get('meta') is None) != (en.get('meta') is None):
            issue('gaps', f'{slug}: meta есть в одной версии и отсутствует в другой')
        if (ru.get('link') is None) != (en.get('link') is None):
            issue('gaps', f'{slug}: link есть в одной версии и отсутствует в другой')
        if ru['tag'] != glossary.get('tag_canon', {}).get(ru['tag'], en['tag']) and \
           ru['tag'] in glossary.get('tag_canon', {}) and \
           en['tag'] != glossary['tag_canon'][ru['tag']]:
            issue('gaps', f'{slug}: тег переведён как "{en["tag"]}", '
                          f'канон для "{ru["tag"]}" — "{glossary["tag_canon"][ru["tag"]]}"')


# ───────────────────────────────────────────────────── 2. канон ───
def check_canon():
    locked = glossary.get('locked_terms', {})
    for slug in sorted(set(ru_by_slug) & set(en_by_slug)):
        ru_blob = ' '.join(ru_by_slug[slug]['paragraphs'])
        en_blob = ' '.join(en_by_slug[slug]['paragraphs']) + ' ' + \
                  en_by_slug[slug]['title'] + ' ' + en_by_slug[slug]['kicker']
        for ru_term, en_term in locked.items():
            if ru_term in ru_blob and en_term not in en_blob:
                issue('canon', f'{slug}: RU упоминает «{ru_term}», но канонического '
                               f'"{en_term}" нет в EN — либо потерялось при переводе, '
                               f'либо написано другим вариантом')


# ───────────────────────────────────────────── 3. запрещённые паттерны ───
def check_forbidden():
    forbidden = list(glossary.get('forbidden_in_en', {}).keys())
    if not forbidden:
        forbidden = ['SMM', '«', '»']
    for path in sorted(glob.glob('en/**/*.html', recursive=True)):
        html = open(path, encoding='utf-8').read()
        visible = re.sub(r'<script.*?</script>', '', html, flags=re.S)
        visible = re.sub(r'<!--.*?-->', '', visible, flags=re.S)
        for pat in forbidden:
            if pat in visible:
                n = visible.count(pat)
                issue('forbidden', f'{path}: "{pat}" встречается {n} раз(а) — '
                                   f'{glossary.get("forbidden_in_en", {}).get(pat, "запрещённый паттерн")}')


# ─────────────────────────────────────────────── 4. целостность ───
def check_integrity():
    # 4a. кириллица в видимом тексте EN-страниц
    for path in sorted(glob.glob('en/**/*.html', recursive=True)):
        html = open(path, encoding='utf-8').read()
        visible = re.sub(r'<script.*?</script>', '', html, flags=re.S)
        visible = re.sub(r'<!--.*?-->', '', visible, flags=re.S)
        if CYRILLIC.search(visible):
            n = len(CYRILLIC.findall(visible))
            issue('integrity', f'{path}: {n} кириллических символов в видимом тексте')

    # 4b. сбалансированность тегов (грубая проверка, не полноценный HTML-парсер)
    for path in sorted(glob.glob('en/**/*.html', recursive=True)):
        html = open(path, encoding='utf-8').read()
        for tag in ('p', 'div', 'strong', 'em', 'a', 'section'):
            o = len(re.findall(rf'<{tag}(?:\s[^>]*)?>', html))
            c = len(re.findall(rf'</{tag}>', html))
            if o != c:
                issue('integrity', f'{path}: <{tag}> открыт {o} раз, закрыт {c} раз')

    # 4c. hreflang-пары в sitemap.xml — если файла нет, не считаем ошибкой (могли не пересобрать)
    if os.path.isfile('sitemap.xml'):
        sm = open('sitemap.xml', encoding='utf-8').read()
        ru_count = sm.count('hreflang="ru"')
        en_count = sm.count('hreflang="en"')
        if ru_count != en_count:
            issue('integrity', f'sitemap.xml: {ru_count} hreflang="ru" vs {en_count} hreflang="en" — должно совпадать')

    # 4d. внутренние ссылки на EN-страницах не 404
    broken = 0
    for path in sorted(glob.glob('en/**/*.html', recursive=True)):
        html = open(path, encoding='utf-8').read()
        base_dir = os.path.dirname(path)
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(('http', 'mailto:', 'data:', '#')):
                continue
            target = href.split('#')[0].split('?')[0]
            if not target:
                continue
            resolved = os.path.normpath(os.path.join(base_dir, target))
            ok = os.path.isfile(os.path.join(resolved, 'index.html')) if \
                (target.endswith('/') or os.path.isdir(resolved)) else os.path.isfile(resolved)
            if not ok:
                issue('integrity', f'{path}: битая ссылка "{href}"')
                broken += 1


# ───────────────────────────────────────────────────────── run ───
def main():
    check_gaps()
    check_canon()
    check_forbidden()
    check_integrity()

    sections = ['gaps', 'canon', 'forbidden', 'integrity']
    titles = {
        'gaps': '1. ПРОПУСКИ И ПОЛНОТА ПЕРЕВОДА',
        'canon': '2. КАНОН ИМЁН И НАЗВАНИЙ',
        'forbidden': '3. ЗАПРЕЩЁННЫЕ ПАТТЕРНЫ',
        'integrity': '4. ЦЕЛОСТНОСТЬ',
    }
    print('=' * 62)
    print('ПРОВЕРКА АНГЛИЙСКОЙ ВЕРСИИ orgculture.ru')
    print('=' * 62)
    print()
    for s in sections:
        found = [m for sec, m in ISSUES if sec == s]
        print(f'{titles[s]}: {len(found)}')
        if found:
            for m in found:
                print(f'   {m}')
        else:
            print('   чисто')
        print()

    if ISSUES:
        print(f'ИТОГ: {len(ISSUES)} замечаний — см. выше')
        sys.exit(1)
    else:
        print('ИТОГ: всё чисто')
        sys.exit(0)


if __name__ == '__main__':
    main()
