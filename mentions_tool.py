#!/usr/bin/env python3
"""
mentions_tool.py — работа с упоминаниями (mentions.json), v59.

По образцу пака AELITA (_tools/Mentions/search_mentions.py, pack-v491 —
только смотрели), урезано до того, что нужно одному автору: без
медиалиста и городов.

    python3 mentions_tool.py              # проверка записей (то же делает check_archive.py)
    python3 mentions_tool.py --plan       # план поиска: запросы и готовые ссылки на Яндекс/Google
    python3 mentions_tool.py --links      # живы ли ссылки в записях (нужен интернет)
    python3 mentions_tool.py --stale 90   # что не перепроверялось руками дольше N дней

Скрипт НЕ ходит в поисковики сам и не делает вид, что умеет: открытого
API под это нет, а разбор выдачи ломается от первой смены вёрстки и
упирается в капчу. Он автоматизирует то, что автоматизируется честно:
план запросов, проверку живости ссылок, напоминание о непроверенном.

Порядок работы: нашёл упоминание → запись в mentions.json →
python3 mentions_tool.py → python3 gen.py && python3 gen_en.py.

Схема записи (все поля обязательны; пустая строка — допустимое значение
для date, author_*, subject_*, note_*):
    id        OKM-001, OKM-002… — не меняется никогда
    date      YYYY-MM-DD — дата публикации, не находки; "" если не знаешь
              (не подставлять правдоподобную — это превращает пропуск в
              ошибку, которую потом никто не найдёт)
    kind      press | interview | publication | channel | podcast | venue
    subject_ru/en  о чём речь: проект, спектакль, ты
    source_ru/en   издание или канал
    author_ru/en   подпись под материалом
    title_ru/en    о чём материал, своими словами
    url
    checked   YYYY-MM-DD — когда последний раз открывал ссылку руками
    publish   true — на сайт; false — внутренняя заметка
    note_ru/en     что с этим делать (на сайт не выводится)
"""
import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(HERE, "mentions.json")
KINDS = {"press", "interview", "publication", "channel", "podcast", "venue"}
FIELDS = ["id", "date", "kind", "subject_ru", "subject_en", "source_ru", "source_en",
          "author_ru", "author_en", "title_ru", "title_en", "url", "checked", "publish",
          "note_ru", "note_en"]
REQUIRED_NONEMPTY = ["id", "kind", "source_ru", "title_ru", "url", "checked"]
REQUIRED_NONEMPTY_PUBLISHED = ["source_en", "title_en"]  # на /en/mentions/ нужен перевод
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^OKM-\d{3,}$")
CYR = re.compile(r"[А-Яа-яЁё]")


def load():
    with open(PATH, encoding="utf-8") as f:
        return json.load(f)


def validate(data):
    """Список проблем (строки). Пустой — всё в порядке."""
    problems = []
    items = data.get("mentions")
    if not isinstance(items, list):
        return ["mentions.json: нет списка \"mentions\""]
    seen = set()
    for i, m in enumerate(items):
        where = m.get("id") or f"запись №{i + 1}"
        for f in FIELDS:
            if f not in m:
                problems.append(f"{where}: нет поля {f}")
        for f in REQUIRED_NONEMPTY:
            if not m.get(f):
                problems.append(f"{where}: пустое поле {f}")
        if m.get("id") and not ID_RE.match(m["id"]):
            problems.append(f"{where}: id должен быть вида OKM-001")
        if m.get("id") in seen:
            problems.append(f"{where}: id повторяется")
        seen.add(m.get("id"))
        for f in ("date", "checked"):
            v = m.get(f, "")
            if v and not DATE_RE.match(v):
                problems.append(f"{where}: {f} не в формате YYYY-MM-DD ({v!r})")
            elif v:
                try:
                    datetime.date.fromisoformat(v)
                except ValueError:
                    problems.append(f"{where}: {f} — такой даты нет ({v!r})")
        if m.get("kind") and m["kind"] not in KINDS:
            problems.append(f"{where}: kind {m['kind']!r} — допустимо: {', '.join(sorted(KINDS))}")
        if m.get("url") and not m["url"].startswith(("https://", "http://")):
            problems.append(f"{where}: url должен начинаться с http(s)://")
        if not isinstance(m.get("publish"), bool):
            problems.append(f"{where}: publish должен быть true или false")
        if m.get("publish"):
            for f in REQUIRED_NONEMPTY_PUBLISHED:
                if not m.get(f):
                    problems.append(f"{where}: публикуется, но пустое {f} — /en/mentions/ останется без перевода")
            for f in ("subject_en", "source_en", "author_en", "title_en"):
                if CYR.search(m.get(f, "")):
                    problems.append(f"{where}: в {f} кириллица")
    return problems


def plan(data):
    print("Запросы — открыть по ссылкам, просмотреть первые страницы выдачи:\n")
    for q in data.get("queries", []):
        enc = urllib.parse.quote(q)
        print(f"  {q}")
        print(f"    Яндекс: https://yandex.ru/search/?text={enc}")
        print(f"    Google: https://www.google.com/search?q={enc}")
    useless = data.get("queries_useless", [])
    if useless:
        print("\nИскать бесполезно (проверено):")
        for q in useless:
            print(f"  {q}")
    print("\nНашёл — запись в mentions.json (схема — в начале этого файла), затем")
    print("python3 mentions_tool.py && python3 gen.py && python3 gen_en.py")
    print("Запрос, который ничего не дал, — перенеси в queries_useless: это экономит время в следующий раз.")


def links(data):
    bad = 0
    for m in data.get("mentions", []):
        url = m.get("url", "")
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = f"нет ответа ({type(e).__name__})"
        ok = isinstance(code, int) and code < 400
        # Часть сайтов не отвечает на HEAD (405) — это не мёртвая ссылка.
        if code == 405:
            ok = True
        print(f"  {'ok ' if ok else '!! '} {m.get('id')}  {code}  {url}")
        bad += 0 if ok else 1
    print(f"\nПроблемных ссылок: {bad}. Живую ссылку, открытую руками, отметь в checked сегодняшней датой.")


def stale(data, days):
    today = datetime.date.today()
    found = 0
    for m in data.get("mentions", []):
        c = m.get("checked", "")
        try:
            age = (today - datetime.date.fromisoformat(c)).days
        except ValueError:
            age = None
        if age is None or age > days:
            found += 1
            print(f"  {m.get('id')}  checked={c or '—'}  {m.get('url')}")
    print(f"\nНе перепроверялось дольше {days} дней: {found}")


def main():
    data = load()
    args = sys.argv[1:]
    if "--plan" in args:
        plan(data)
        return
    if "--links" in args:
        links(data)
        return
    if "--stale" in args:
        i = args.index("--stale")
        days = int(args[i + 1]) if i + 1 < len(args) else 90
        stale(data, days)
        return
    problems = validate(data)
    total = len(data.get("mentions", []))
    published = sum(1 for m in data.get("mentions", []) if m.get("publish"))
    print(f"mentions.json: записей {total}, на сайт {published}")
    for p in problems:
        print("  " + p)
    print("ИТОГ: всё чисто" if not problems else f"ИТОГ: {len(problems)} замечаний")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
