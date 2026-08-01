# -*- coding: utf-8 -*-
import html, os, subprocess

SECTIONS = [
  ("1. Что такое файлы cookie", [
    "Cookie — небольшие текстовые файлы, которые сайт сохраняет в браузере пользователя для распознавания при повторных посещениях и сбора статистики использования сайта.",
  ]),
  ("2. Какие cookie используются", [
    "Сайт orgculture.ru использует сервис веб-аналитики Яндекс.Метрика, который устанавливает собственные cookie для сбора обезличенной статистики посещаемости (просмотры страниц, переходы, время на сайте) и, при включённой функции Вебвизор, записи действий пользователя на странице (клики, движения курсора, скролл, ввод в поля форм) в обезличенном виде.",
    "Оператор сайта не устанавливает собственных cookie сверх тех, что необходимы для базовой работы сайта.",
    "Яндекс.Метрика запускается только после согласия, данного через баннер на сайте — до этого момента счётчик не активен и cookie не устанавливаются.",
  ]),
  ("3. Управление cookie", [
    "Пользователь может отключить cookie в настройках своего браузера. Это может ограничить работу отдельных функций сайта, но не запрещает доступ к его основному содержимому.",
  ]),
  ("4. Передача данных третьим лицам", [
    "Статистика, собираемая Яндекс.Метрикой, обрабатывается ООО «Яндекс» в соответствии с его собственной политикой конфиденциальности: yandex.ru/legal/confidential",
  ]),
  ("5. Изменения", [
    "Оператор вправе вносить изменения в настоящее Соглашение. Новая редакция вступает в силу с момента размещения на сайте.",
  ]),
]

LOGO_MARK_SVG = '''<svg viewBox="140 240 800 600" fill="none" stroke="#F5F2ED" stroke-width="27" stroke-linecap="round" stroke-linejoin="round">
  <ellipse cx="364" cy="540" rx="200" ry="110"/>
  <path d="M 764 264 L 764 816 M 764 540 L 916 264 M 764 540 L 916 816"/>
</svg>'''

sections_html = ""
for title, paras in SECTIONS:
    sections_html += f"<h2>{html.escape(title)}</h2>\n"
    for p in paras:
        sections_html += f"<p>{html.escape(p)}</p>\n"

html_doc = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<style>
  @page {{ size: A4; margin: 0; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    font-family:'DejaVu Sans',Arial,sans-serif; font-weight:300;
    background:#0A0A0A; color:#F5F2ED; line-height:1.65; font-size:13px;
    padding:24mm 20mm;
  }}
  .logo {{ width:44px; margin-bottom:22px; }}
  .eyebrow {{ font-size:10px; letter-spacing:.18em; text-transform:uppercase; color:#9A968E; font-weight:500; }}
  h1 {{ font-family:'DejaVu Sans',sans-serif; font-weight:300; font-size:21px; margin:10px 0 4px; }}
  .meta {{ color:#6E6A63; font-size:11px; margin-bottom:30px; }}
  h2 {{ font-family:'DejaVu Sans',sans-serif; font-weight:bold; font-size:13.5px; color:#D97757; margin:24px 0 9px; }}
  p {{ margin-bottom:11px; color:#C9C6C0; text-align:justify; }}
  .requisites {{
    margin-top:36px; padding:20px 0; border-top:1px solid #262523;
    font-size:11.5px; color:#9A968E; line-height:1.9;
  }}
  .foot {{ margin-top:14px; font-size:10px; color:#4A4742; letter-spacing:.06em; text-transform:uppercase; }}
</style>
</head>
<body>
  <div class="logo">{LOGO_MARK_SVG}</div>
  <div class="eyebrow">Документ</div>
  <h1>Соглашение об использовании cookie</h1>
  <div class="meta">orgculture.ru · редакция от 30.07.2026</div>
  {sections_html}
  <div class="requisites">
    Мошников Константин Алексеевич<br>
    Самозанятый (НПД) · ИНН 471508674254<br>
    г. Санкт-Петербург<br>
    Email: kostyamoshnikov@gmail.com
  </div>
  <div class="foot">Организованная Культурность — orgculture.ru</div>
</body>
</html>'''

# Промежуточный HTML пишется во временную папку ОС, а не в корень сайта —
# раньше cookies-src.html оставался лежать рядом с index.html и уезжал
# на хостинг вместе со всем остальным при деплое.
import tempfile
with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8") as f:
    f.write(html_doc)
    tmp_path = f.name

subprocess.run([
    "wkhtmltopdf", "--page-size", "A4",
    "--margin-top", "0", "--margin-bottom", "0", "--margin-left", "0", "--margin-right", "0",
    "--enable-local-file-access",
    tmp_path, "documents/cookies-policy.pdf"
])
os.remove(tmp_path)

print("cookies-policy.pdf written")
