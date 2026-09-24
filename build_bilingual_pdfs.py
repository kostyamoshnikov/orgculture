#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Двуязычные PDF на сайте (v61 сайта / v76 архива).

Решение автора 24.09.2026: каждый PDF, опубликованный на сайте, содержит
и русскую, и английскую версию. Порядок — по языку страницы, с которой
его скачивают:
    русский сайт  → файл без -en: сначала русская часть, потом английская;
    английский сайт → файл -en:   сначала английская, потом русская.

Одноязычные части сами по себе на сайт не попадают. Их делают:
    07-documents/site-pdf-parts/*_ru.pdf, *_en.pdf
        gen_privacy_pdf.py, gen_cookies_pdf.py (RU),
        gen_legal_pdf_en.py (EN), gen_cv_pdf.py (RU + EN)
    07-documents/commercial-offers/site-general(-en)/*.pdf   — КП
    02-brandbook/brandbook2.pdf, brandbook2-en.pdf           — брендбук
Этот скрипт их склеивает в 03-website/documents/ и кладёт копии в
07-documents/ (там, где копии были и раньше).

В склеенном файле:
  • закладки «Русская версия» / «English version» на начало каждой части
    (в любом просмотрщике PDF — панель закладок/оглавления);
  • на первой странице, в правом верхнем углу мелкая строка на двух
    языках: где начинается вторая часть. Нужен шрифт с кириллицей
    (ищется DejaVu Sans / Arial / Roboto); если не нашёлся — строка не
    ставится, закладки остаются, скрипт об этом пишет.

Векторный знак для печати (press/orgculture-logo-vector.pdf) — без
текста, языковых версий у него нет; остаётся как есть.

Запуск (из любой папки), после любого генератора частей:
    python3 03-website/build_bilingual_pdfs.py
Проверка — check_archive.py, раздел 4.16: каждая страница склеенного
файла совпадает по тексту со своей частью, порядок частей верный.

Нужны Python-пакеты pypdf и reportlab (pip install pypdf reportlab) —
см. DEPENDENCIES.md.
"""
import io
import os
import shutil
import sys

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    sys.exit("❌ нужен pypdf: pip install pypdf")

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.dirname(HERE)
PARTS = os.path.join(ARCHIVE, "07-documents", "site-pdf-parts")

# (русская часть, английская часть, файл для русского сайта, файл для английского,
#  копии в 07-documents: (для RU-файла, для EN-файла) или None)
DOCS = [
    (os.path.join(PARTS, "privacy-policy_ru.pdf"), os.path.join(PARTS, "privacy-policy_en.pdf"),
     "documents/privacy-policy.pdf", "documents/privacy-policy-en.pdf",
     ("07-documents/privacy-policy.pdf", "07-documents/privacy-policy-en.pdf")),
    (os.path.join(PARTS, "cookies-policy_ru.pdf"), os.path.join(PARTS, "cookies-policy_en.pdf"),
     "documents/cookies-policy.pdf", "documents/cookies-policy-en.pdf",
     ("07-documents/cookies-policy.pdf", "07-documents/cookies-policy-en.pdf")),
    (os.path.join(PARTS, "CV-Konstantin-Moshnikov_ru.pdf"), os.path.join(PARTS, "CV-Konstantin-Moshnikov_en.pdf"),
     "documents/CV-Konstantin-Moshnikov.pdf", "documents/CV-Konstantin-Moshnikov-en.pdf",
     ("07-documents/CV-Konstantin-Moshnikov.pdf", "07-documents/CV-Konstantin-Moshnikov-en.pdf")),
    (os.path.join(ARCHIVE, "07-documents/commercial-offers/site-general/Organized_Culturality_OK_CommercialOffer.pdf"),
     os.path.join(ARCHIVE, "07-documents/commercial-offers/site-general-en/Organized_Culturality_OK_CommercialOffer_EN.pdf"),
     "documents/orgculture-uslugi-i-ceny.pdf", "documents/orgculture-services-and-prices.pdf", None),
    (os.path.join(ARCHIVE, "02-brandbook/brandbook2.pdf"), os.path.join(ARCHIVE, "02-brandbook/brandbook2-en.pdf"),
     "documents/press/orgculture-brandbook.pdf", "documents/press/orgculture-brandbook-en.pdf", None),
]

LABEL = {"ru": "Русская версия", "en": "English version"}


def stamp_text(first, second, second_page):
    if first == "ru":
        return f"Русская версия — с. 1 · English version — p. {second_page}"
    return f"English version — p. 1 · Русская версия — с. {second_page}"


FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
    "/system/fonts/Roboto-Regular.ttf",          # Android / Termux
]
_font = None


def font():
    global _font
    if _font is not None:
        return _font or None
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        print("⚠️  reportlab не установлен — строка о второй части не ставится (закладки есть)")
        _font = False
        return None
    for p in FONT_CANDIDATES:
        if os.path.isfile(p):
            pdfmetrics.registerFont(TTFont("BilingualStamp", p))
            _font = "BilingualStamp"
            return _font
    print("⚠️  не найден шрифт с кириллицей — строка о второй части не ставится (закладки есть)")
    _font = False
    return None


def overlay(page, text):
    """Мелкая строка в правом верхнем углу первой страницы."""
    f = font()
    if not f:
        return
    from reportlab.pdfgen import canvas
    w, h = float(page.mediabox.width), float(page.mediabox.height)
    size = max(6.5, min(9.0, w / 75))            # A4 ≈ 7.9 pt; брендбук — 9 pt
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(w, h))
    c.setFont(f, size)
    c.setFillColorRGB(0x9A / 255, 0x96 / 255, 0x8E / 255)   # --dim, читается на тёмном фоне
    margin = 22.7                                            # 8 мм
    c.drawRightString(w - margin, h - margin - size, text)
    c.save()
    buf.seek(0)
    page.merge_page(PdfReader(buf).pages[0])


def build(first_path, second_path, first_lang, out_path):
    a, b = PdfReader(first_path), PdfReader(second_path)
    w = PdfWriter()
    for p in a.pages:
        w.add_page(p)
    for p in b.pages:
        w.add_page(p)
    second_lang = "en" if first_lang == "ru" else "ru"
    overlay(w.pages[0], stamp_text(first_lang, second_lang, len(a.pages) + 1))
    w.add_outline_item(LABEL[first_lang], 0)
    w.add_outline_item(LABEL[second_lang], len(a.pages))
    w.page_mode = "/UseOutlines"                 # закладки открыты сразу
    w.add_metadata({"/Producer": "orgculture build_bilingual_pdfs.py"})
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        w.write(f)
    return len(a.pages), len(b.pages)


def main():
    missing = [p for d in DOCS for p in d[:2] if not os.path.isfile(p)]
    if missing:
        print("❌ нет одноязычных частей — сначала их генераторы:")
        for p in missing:
            print("   " + os.path.relpath(p, ARCHIVE))
        sys.exit(1)
    for ru, en, out_ru, out_en, mirrors in DOCS:
        for first_lang, out in (("ru", out_ru), ("en", out_en)):
            first, second = (ru, en) if first_lang == "ru" else (en, ru)
            path = os.path.join(HERE, out)
            na, nb = build(first, second, first_lang, path)
            print(f"{out}: {first_lang.upper()} {na} с. + {'EN' if first_lang == 'ru' else 'RU'} {nb} с.")
        if mirrors:
            for src, dst in zip((out_ru, out_en), mirrors):
                shutil.copyfile(os.path.join(HERE, src), os.path.join(ARCHIVE, dst))
    print("готово; копии — в 07-documents/")


if __name__ == "__main__":
    main()
