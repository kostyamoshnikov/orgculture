#!/usr/bin/env python3
"""
Организованная Культурность · Неразрывные пробелы в русском тексте сайта
(v58). Перенесено из пака AELITA (`_tools/SiteDeploy/typography.py`,
pack-v485, перепроверено в v486; смотрели pack-v491) — правила те же,
байт в байт; отличаются ГДЕ применяется (см. ниже) и разбор <script>
(см. transform_html).

ЗАЧЕМ. На телефоне (30–40 знаков в строке) браузер рвёт строку где
придётся: предлог повисает в конце строки («…спектакль в» / «Петербурге»),
тире открывает новую строку, «15» отрывается от «лет». Для сайта из 38
длинных текстов это заметнее, чем у AELITA. Неразрывный пробел (U+00A0)
выглядит как обычный, но по нему строка не переносится.

ГДЕ ПРИМЕНЯЕТСЯ — ПОСЛЕДНИМ ШАГОМ gen.py, к уже записанным русским
HTML. У AELITA — при выкладке, потому что их английская версия
получается переводом русского HTML по словарю, и неразрывный пробел
ломал бы поиск фраз. У нас EN собирается из своих данных
(`texts_en.json`, `gen_en.py`), русский HTML никто не читает — поэтому
проще и надёжнее ставить сразу при сборке: что в репозитории, то и на
сайте. Исходные тексты в `gen.py` остаются с обычными пробелами.

ЧТО ТРОГАЕТ. Только видимый текст русских страниц (всё `*.html`, кроме
`en/` и `_redirect-for-online-domain/`) — узлы между тегами в <body>.
НЕ трогает: атрибуты (ссылки, alt, content), <head> (title и мета —
сниппеты поисковиков и превью соцсетей), <script>, <style>, <pre>,
<code>, <textarea>, <svg>, комментарии.

ПРАВИЛА (все — только замена обычного пробела на неразрывный):
  1. после предлогов, союзов и частиц из 1–2 букв: «в Калуге», «и на»,
     «по билету», «не только»;
  2. перед частицами «же», «ли», «бы»: «что же», «так ли»;
  3. перед тире: «Показ бренда — Мария Павлова»;
  4. число и единица: «10 ₽», «60 минут», «2026 г.», «18 %»;
  5. № и число: «№ 42»;
  6. инициал и фамилия: «Е. Абдулова», «Е. С. Руденко»;
  7. сокращение и слово: «г. Калуга», «мкр. Жукова», «ул. Ленина».

ИНВАРИАНТЫ (их проверяет аудит, категория `typography_nbsp`, на всех
русских страницах): если заменить U+00A0 обратно на пробел — файл
совпадает с исходным байт в байт; повторное применение ничего не меняет.

Запуск для просмотра одной страницы:
    python3 _tools/SiteDeploy/typography.py tochkacuire

ИНВАРИАНТЫ (проверяет `check_archive.py`, раздел 4.12): если заменить
U+00A0 обратно на пробел — текст совпадает с исходным; повторное
применение ничего не меняет.

Запуск для просмотра одной страницы:
    python3 typography.py texts/eyforiya
"""
import re
import sys
from pathlib import Path

NBSP = '\u00a0'

L = 'A-Za-zА-Яа-яЁё0-9'          # «буква слова» для границ
SHORT_WORDS = 'в к с о у и а я на по за от до из не ни об во со ко но'.split()
SHORT_RE = re.compile(
    r'(?<![' + L + r'\-])(' + '|'.join(SHORT_WORDS) + r') (?=[' + L + r'«“"(\[&])',
    re.IGNORECASE)
PARTICLE_RE = re.compile(r'(?<=[' + L + r']) (же|ли|бы)(?![' + L + r'])')
DASH_RE = re.compile(r'(?<=\S) (?=—)')
UNIT_RE = re.compile(
    r'(?<=\d) (?=(?:₽|руб|коп|мин|час|сек|дн|дней|день|мест|лет|год|г\.|гг\.|км|м\b|см\b|кг|%|тыс|млн|млрд|чел|шт|стр\.))')
NUM_SIGN_RE = re.compile(r'№ (?=\d)')
INITIAL_RE = re.compile(r'(?<![' + L + r'])([А-ЯЁ]\.) (?=[А-ЯЁ])')
# «г.» после числа — это «год» («2026 г. всё»), к следующему слову его не
# клеим; «г.» перед словом — «город» («г. Калуга»).
ABBR_RE = re.compile(
    r'(?<!\d )(?<!\d\u00a0)(?<![' + L + r'])((?:г|гг|ул|мкр|пр|пл|им|стр|корп|обл|пос|рис|см|тел)\.) (?=[' + L + r'«])')

# «в <a>Калуге</a>» — предлог в конце текстового узла, дальше строчный
# тег со словом: связываем с тегом, иначе правило 1 пропустило бы все
# предлоги перед ссылками.
SHORT_END_RE = re.compile(r'(?<![' + L + r'\-])(' + '|'.join(SHORT_WORDS) + r') $', re.IGNORECASE)
INLINE_OPEN_RE = re.compile(r'<(a|b|strong|em|i|span|nobr|mark|small)\b', re.IGNORECASE)

RULES = (SHORT_RE, PARTICLE_RE, DASH_RE, UNIT_RE, NUM_SIGN_RE, INITIAL_RE, ABBR_RE)

SKIP_TAGS = ('script', 'style', 'pre', 'code', 'textarea', 'svg', 'head', 'title')
TOKEN_RE = re.compile(r'(<!--.*?-->|<![^>]*>|<[^>]+>)', re.S)
TAG_RE = re.compile(r'<\s*(/)?\s*([a-zA-Z][a-zA-Z0-9-]*)')


def fix_text(s):
    """Правила к одному текстовому узлу. Меняет только ' ' на U+00A0."""
    if ' ' not in s:
        return s
    for rx in RULES:
        s = rx.sub(lambda m: m.group(0).replace(' ', NBSP), s)
    return s


RAW_BLOCK_RE = re.compile(r'<(script|style)\b.*?</\1\s*>', re.S | re.I)


def transform_html(html):
    """<script>/<style> целиком вынимаются до разбора и возвращаются после.

    Отличие от AELITA (v58): у нас в <script> встречается «j < document…»
    (сниппет Метрики) — токенайзер ниже принимал это за тег, сбивался со
    счёта открытых <script> и дальше не трогал ничего до конца страницы.
    Блоки заменяются меткой без пробелов и без «<», так что правила их
    не касаются.
    """
    saved = []
    def _hide(m):
        saved.append(m.group(0))
        return f'\x00{len(saved) - 1}\x00'
    hidden = RAW_BLOCK_RE.sub(_hide, html)
    res = _transform_tokens(hidden)
    return re.sub('\x00(\\d+)\x00', lambda m: saved[int(m.group(1))], res)


def _transform_tokens(html):
    """Весь HTML-документ: правила только к видимому тексту <body>."""
    parts = TOKEN_RE.split(html)
    depth = {t: 0 for t in SKIP_TAGS}
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # тег или комментарий
            m = TAG_RE.match(part)
            if m and not part.startswith('<!'):
                name = m.group(2).lower()
                if name in depth and not part.rstrip().endswith('/>'):
                    depth[name] += -1 if m.group(1) else 1
                    depth[name] = max(depth[name], 0)
            out.append(part)
        else:
            if any(depth.values()):
                out.append(part)
                continue
            t = fix_text(part)
            nxt = parts[i + 1] if i + 1 < len(parts) else ''
            if INLINE_OPEN_RE.match(nxt):
                t = SHORT_END_RE.sub(lambda m: m.group(0).replace(' ', NBSP), t)
            out.append(t)
    return ''.join(out)


def applies_to(rel_path):
    """Какие файлы сайта обрабатывать: русские HTML."""
    rel = str(rel_path).replace('\\', '/')
    return rel.endswith('.html') and not rel.startswith(('en/', '_redirect-for-online-domain/'))


def apply_to_site(site_root):
    """Проход по всем русским HTML сайта. Возвращает (файлов изменено, пробелов поставлено)."""
    site_root = Path(site_root)
    files = added = 0
    for path in sorted(site_root.rglob('*.html')):
        rel = path.relative_to(site_root)
        if not applies_to(rel):
            continue
        src = path.read_text(encoding='utf-8')
        res = transform_html(src)
        if res != src:
            path.write_text(res, encoding='utf-8')
            files += 1
            added += res.count(NBSP) - src.count(NBSP)
    return files, added


if __name__ == '__main__':
    site = Path(__file__).resolve().parent
    slug = sys.argv[1] if len(sys.argv) > 1 else ''
    path = site / slug / 'index.html' if slug else site / 'index.html'
    src = path.read_text(encoding='utf-8').replace(NBSP, ' ')
    res = transform_html(src)
    n = res.count(NBSP)
    print(f'{path.relative_to(site)}: неразрывных пробелов {n}')
    for line in res.splitlines():
        if NBSP in line and '<' not in line.strip()[:1]:
            print('  ' + line.strip().replace(NBSP, '⍽')[:160])
