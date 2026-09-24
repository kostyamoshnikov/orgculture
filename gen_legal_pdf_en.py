# -*- coding: utf-8 -*-
"""
Английские PDF политики конфиденциальности и соглашения о cookie (v60).

Зачем: до v60 кнопка «Download PDF» на /en/privacy/ и /en/cookies/
отдавала русский PDF. У AELITA правило «каждый файл сайта на двух
языках» (pack-v186, З-11) — здесь то же, в самой простой форме:
отдельный английский файл рядом с русским.

Текст — НЕ копия. Разделы берутся из gen_en.py (PRIVACY_SECTIONS_EN,
COOKIES_SECTIONS_EN) — тех же, из которых собраны /en/privacy/ и
/en/cookies/ — через разбор исходника (ast), без запуска сборки сайта.
Правишь текст политики — правь gen_en.py (и русский — gen.py +
gen_privacy_pdf.py / gen_cookies_pdf.py), затем запусти этот скрипт.
Дата редакции тоже берётся из gen_en.py, из вызова legal_page_en().

Оговорка о приоритете русского текста (LEGAL_EN_NOTE в gen_en.py) —
та же, что на английских страницах.

Вёрстка — та же, что у русских PDF (gen_privacy_pdf.py): тёмный лист,
знак, реквизиты внизу.

Запуск (из любой папки):
    python3 03-website/gen_legal_pdf_en.py
Нужен wkhtmltopdf (см. DEPENDENCIES.md).
"""
import ast
import html
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "gen_en.py")
# С v76 — английская ЧАСТЬ документа; на сайт — только склеенной с русской
# (build_bilingual_pdfs.py).
PARTS_DIR = os.path.join(os.path.dirname(HERE), "07-documents", "site-pdf-parts")

tree = ast.parse(open(SRC, encoding="utf-8").read())
consts = {}
meta = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        name = node.targets[0].id
        if name in ("PRIVACY_SECTIONS_EN", "COOKIES_SECTIONS_EN", "LEGAL_EN_NOTE"):
            consts[name] = ast.literal_eval(node.value)
    if isinstance(node, ast.FunctionDef) and node.name in ("build_privacy_en", "build_cookies_en"):
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and getattr(sub.func, "id", "") == "legal_page_en":
                meta[node.name] = (ast.literal_eval(sub.args[1]), ast.literal_eval(sub.args[2]))
missing = {"PRIVACY_SECTIONS_EN", "COOKIES_SECTIONS_EN", "LEGAL_EN_NOTE"} - set(consts)
if missing or len(meta) != 2:
    raise SystemExit(f"gen_en.py: не найдено {sorted(missing) or 'вызов legal_page_en()'} — структура файла менялась?")

LOGO_MARK_SVG = '''<svg viewBox="140 240 800 600" fill="none" stroke="#F5F2ED" stroke-width="27" stroke-linecap="round" stroke-linejoin="round">
  <ellipse cx="364" cy="540" rx="200" ry="110"/>
  <path d="M 764 264 L 764 816 M 764 540 L 916 264 M 764 540 L 916 816"/>
</svg>'''

STYLE = '''
  @page { size: A4; margin: 0; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family:'DejaVu Sans',Arial,sans-serif; font-weight:300;
    background:#0A0A0A; color:#F5F2ED; line-height:1.65; font-size:13px;
    padding:24mm 20mm;
  }
  .logo { width:44px; margin-bottom:22px; }
  .eyebrow { font-size:10px; letter-spacing:.18em; text-transform:uppercase; color:#9A968E; font-weight:500; }
  h1 { font-family:'DejaVu Sans',sans-serif; font-weight:300; font-size:21px; margin:10px 0 4px; }
  .meta { color:#6E6A63; font-size:11px; margin-bottom:6px; }
  .note { color:#9A968E; font-size:11px; font-style:italic; margin-bottom:30px; }
  h2 { font-family:'DejaVu Sans',sans-serif; font-weight:500; font-size:13.5px; color:#D97757; margin:24px 0 9px; }
  p { margin-bottom:11px; color:#C9C6C0; text-align:justify; }
  .requisites {
    margin-top:36px; padding:20px 0; border-top:1px solid #262523;
    font-size:11.5px; color:#9A968E; line-height:1.9;
  }
  .foot { margin-top:14px; font-size:10px; color:#4A4742; letter-spacing:.06em; text-transform:uppercase; }
'''


def render(h1, doc_meta, sections, out_name):
    body = ""
    for title, paras in sections:
        body += f"<h2>{html.escape(title)}</h2>\n" + "".join(f"<p>{html.escape(p)}</p>\n" for p in paras)
    doc = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><style>{STYLE}</style></head>
<body>
  <div class="logo">{LOGO_MARK_SVG}</div>
  <div class="eyebrow">Document</div>
  <h1>{html.escape(h1)}</h1>
  <div class="meta">{html.escape(doc_meta)}</div>
  <div class="note">{html.escape(consts["LEGAL_EN_NOTE"])}</div>
  {body}
  <div class="requisites">
    Konstantin Alekseevich Moshnikov<br>
    Self-employed (NPD tax regime) · INN 471508674254<br>
    St. Petersburg, Russia<br>
    Email: kostyamoshnikov@gmail.com
  </div>
  <div class="foot">Organized Culturality — orgculture.ru</div>
</body></html>'''
    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(doc)
        tmp = f.name
    os.makedirs(PARTS_DIR, exist_ok=True)
    out = os.path.join(PARTS_DIR, out_name)
    try:
        subprocess.run(["wkhtmltopdf", "--quiet", "--page-size", "A4",
                        "--margin-top", "0", "--margin-bottom", "0", "--margin-left", "0", "--margin-right", "0",
                        "--enable-local-file-access", tmp, out], check=True)
    finally:
        os.remove(tmp)
    print(f"site-pdf-parts/{out_name} written — на сайт: python3 build_bilingual_pdfs.py")


render(*meta["build_privacy_en"], consts["PRIVACY_SECTIONS_EN"], "privacy-policy_en.pdf")
render(*meta["build_cookies_en"], consts["COOKIES_SECTIONS_EN"], "cookies-policy_en.pdf")
