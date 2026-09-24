# -*- coding: utf-8 -*-
"""
Генератор CV в PDF — по образцу gen_privacy_pdf.py / gen_cookies_pdf.py.

Зачем существует: раньше CV-PDF был единственным документом в паке БЕЗ
скрипта-генератора — существовал только как готовый файл, собранный
когда-то вручную. Из-за этого любая правка текста (например, опечатка в
названии спектакля) требовала либо ручного редактирования PDF, либо
пересборки из PPTX другим движком, что ломало вёрстку (буллеты, отступы,
порядок «плашек» навыков). Теперь CV воспроизводим тем же пайплайном,
что и остальные документы.

Данные берутся из gen.py (CV_ROLES, ABOUT_*) — единый источник правды со
страницей «Автор» на сайте, чтобы CV и сайт не расходились.

С v76 собирает ДВЕ одноязычные части — русскую (CV_ROLES из gen.py) и
английскую (CV_ROLES_EN из gen_en.py) — в 07-documents/site-pdf-parts/.
На сайт они попадают только склеенными: build_bilingual_pdfs.py делает
CV-Konstantin-Moshnikov.pdf (RU → EN) и CV-Konstantin-Moshnikov-en.pdf
(EN → RU).

Запуск (из любой папки):
    python3 03-website/gen_cv_pdf.py
    python3 03-website/build_bilingual_pdfs.py
"""
import html
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Импортируем данные из gen.py, не запуская генерацию сайта:
# gen.py выполняет сборку на верхнем уровне, поэтому читаем и исполняем
# только его начало — до первой записи файлов. Проще и надёжнее —
# продублировать здесь только нужные структуры через exec ограниченного
# куска, но пока CV_ROLES компактен, держим его импорт явным.
import re as _re

_gen_src = open(os.path.join(HERE, "gen.py"), encoding="utf-8").read()
_ns = {}
_m = _re.search(r"^CV_ROLES = \[.*?^\]", _gen_src, _re.S | _re.M)
if not _m:
    raise SystemExit("Не нашёл CV_ROLES в gen.py")
exec(_m.group(0), _ns)
CV_ROLES = _ns["CV_ROLES"]

_gen_en_src = open(os.path.join(HERE, "gen_en.py"), encoding="utf-8").read()
_m_en = _re.search(r"^CV_ROLES_EN = \[.*?^\]", _gen_en_src, _re.S | _re.M)
if not _m_en:
    raise SystemExit("Не нашёл CV_ROLES_EN в gen_en.py")
exec(_m_en.group(0), _ns)
CV_ROLES_EN = _ns["CV_ROLES_EN"]

PARTS_DIR = os.path.join(os.path.dirname(HERE), "07-documents", "site-pdf-parts")

TEXT = {
    "ru": {
        "lang": "ru",
        "roles": CV_ROLES,
        "name": "Константин Мошников",
        "headline": "Сооснователь, продюсер и SMM, AELITA PRODUCTION",
        "contacts": ["+7 904 617-01-88", "kostyamoshnikov@gmail.com",
                     "Санкт-Петербург", "aelita-production.ru"],
        "about": ("Более 15 лет на сцене — в цирке, в театре. Знаю индустрию изнутри и "
                  "понимаю её механику на каждом уровне. Продюсирую и веду SMM культурных "
                  "и арт-проектов: от концепции до выпуска, от маркетинга до логистики."),
        "skills": [
            "Продюсирование и управление проектами",
            "Организация фестивалей и мероприятий",
            "Копирайтинг и контент-стратегия",
            "Бюджетирование",
            "SMM (ВКонтакте, Telegram, Instagram)",
            "Кризисный менеджмент",
            "Организация гастролей и проката",
            "Веб (HTML, GitHub Pages)",
        ],
        "artistic": ("Артист цирка · более 15 лет. В настоящее время занят в оперетте "
                     "«Принцесса цирка» в Театре музыкальной комедии Санкт-Петербурга "
                     "— спектакль в прокате."),
        "labels": ("О себе", "Навыки", "Опыт", "Артистическая деятельность"),
        "foot": "Организованная Культурность — orgculture.ru",
        "out": "CV-Konstantin-Moshnikov_ru.pdf",
    },
    # Английский текст — по /en/about/ (gen_en.py): те же формулировки,
    # что на странице, там где они есть; остальное — перевод русского CV.
    "en": {
        "lang": "en",
        "roles": CV_ROLES_EN,
        "name": "Konstantin Moshnikov",
        "headline": "Co-founder, producer and social media, AELITA PRODUCTION",
        "contacts": ["+7 904 617-01-88", "kostyamoshnikov@gmail.com",
                     "St. Petersburg", "aelita-production.ru"],
        "about": ("15+ years on stage, in circus and in theatre. I know the industry from the "
                  "inside and understand how it works at every level. I produce and run social "
                  "media for cultural and arts projects: concept through to launch, marketing "
                  "through to logistics."),
        "skills": [
            "Production and project management",
            "Festival and event organisation",
            "Copywriting and content strategy",
            "Budgeting",
            "Social media (VK, Telegram, Instagram)",
            "Crisis management",
            "Touring and show runs",
            "Web (HTML, GitHub Pages)",
        ],
        "artistic": ("Circus performer, 15+ years. Currently in the operetta \u201cPrincess Circus\u201d "
                     "at the St. Petersburg Musical Comedy Theatre \u2014 a production currently in repertory."),
        "labels": ("About", "Skills", "Experience", "Performing arts"),
        "foot": "Organized Culturality — orgculture.ru",
        "out": "CV-Konstantin-Moshnikov_en.pdf",
    },
}

LOGO_MARK_SVG = '''<svg viewBox="140 240 800 600" fill="none" stroke="#F5F2ED" stroke-width="27" stroke-linecap="round" stroke-linejoin="round">
  <ellipse cx="364" cy="540" rx="200" ry="110"/>
  <path d="M 764 264 L 764 816 M 764 540 L 916 264 M 764 540 L 916 816"/>
</svg>'''

def render(T):
    skills_html = "".join(
        f'<span class="pill">{html.escape(s)}</span>' for s in T["skills"]
    )

    roles_html = ""
    for r in T["roles"]:
        bullets = "".join(f"<li>{html.escape(b)}</li>" for b in r["bullets"])
        roles_html += f'''<div class="role">
        <div class="role-head">
          <div class="role-title">{html.escape(r['role'])}</div>
          <div class="role-period">{html.escape(r['period'])}</div>
        </div>
        <div class="role-org">{html.escape(r['org'])}</div>
        <ul>{bullets}</ul>
      </div>
    '''

    contacts_html = " &nbsp;·&nbsp; ".join(html.escape(c) for c in T["contacts"])

    html_doc = f'''<!DOCTYPE html>
    <html lang="{T['lang']}">
    <head>
    <meta charset="UTF-8">
    <style>
      @page {{ size: A4; margin: 0; }}
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      body {{
        font-family:'DejaVu Sans',Arial,sans-serif; font-weight:300;
        background:#0A0A0A; color:#F5F2ED; line-height:1.6; font-size:11px;
        padding:16mm 16mm;
      }}
      .logo {{ width:38px; margin-bottom:16px; }}
      h1 {{ font-weight:300; font-size:24px; margin-bottom:5px; letter-spacing:.01em; }}
      .headline {{ color:#D97757; font-size:12px; margin-bottom:8px; }}
      .contacts {{ color:#9A968E; font-size:10.5px; margin-bottom:22px; }}
      .eyebrow {{
        font-size:8.5px; letter-spacing:.22em; text-transform:uppercase;
        color:#6E6A63; font-weight:500; margin:20px 0 8px;
      }}
      .about {{ color:#C9C6C0; font-size:11px; line-height:1.75; }}
      .pill {{
        display:inline-block; border:1px solid #262523; border-radius:999px;
        padding:5px 13px; margin:0 5px 6px 0; font-size:10px; color:#C9C6C0;
      }}
      .role {{ border-top:1px solid #1C1B1A; padding:11px 0 3px; }}
      .role-head {{ display:flex; justify-content:space-between; align-items:baseline; }}
      .role-title {{ font-size:12.5px; color:#F5F2ED; }}
      .role-period {{ font-size:9.5px; color:#6E6A63; white-space:nowrap; }}
      .role-org {{ font-size:10.5px; color:#D97757; margin:2px 0 6px; }}
      ul {{ list-style:none; }}
      li {{
        position:relative; padding-left:12px; margin-bottom:3px;
        font-size:10.5px; color:#C9C6C0; line-height:1.6;
      }}
      li:before {{
        content:"•"; position:absolute; left:0; top:0; color:#6E6A63;
      }}
      .artistic {{ color:#C9C6C0; font-size:10.5px; line-height:1.7; }}
      .foot {{
        margin-top:22px; padding-top:12px; border-top:1px solid #1C1B1A;
        font-size:8.5px; color:#4A4742; letter-spacing:.18em; text-transform:uppercase;
      }}
    </style>
    </head>
    <body>
      <div class="logo">{LOGO_MARK_SVG}</div>
      <h1>{html.escape(T["name"])}</h1>
      <div class="headline">{html.escape(T["headline"])}</div>
      <div class="contacts">{contacts_html}</div>

      <div class="eyebrow">{T["labels"][0]}</div>
      <div class="about">{html.escape(T["about"])}</div>

      <div class="eyebrow">{T["labels"][1]}</div>
      <div>{skills_html}</div>

      <div class="eyebrow">{T["labels"][2]}</div>
      {roles_html}

      <div class="eyebrow">{T["labels"][3]}</div>
      <div class="artistic">{html.escape(T["artistic"])}</div>

      <div class="foot">{html.escape(T["foot"])}</div>
    </body>
    </html>'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False,
                                     encoding="utf-8") as f:
        f.write(html_doc)
        tmp_path = f.name

    subprocess.run([
        "wkhtmltopdf", "--page-size", "A4",
        "--margin-top", "0", "--margin-bottom", "0",
        "--margin-left", "0", "--margin-right", "0",
        "--enable-local-file-access",
        tmp_path, os.path.join(PARTS_DIR, T["out"])
    ])
    os.remove(tmp_path)

    print(f"site-pdf-parts/{T['out']} written")


os.makedirs(PARTS_DIR, exist_ok=True)
for _lang in ("ru", "en"):
    render(TEXT[_lang])

