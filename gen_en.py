# -*- coding: utf-8 -*-
"""
gen_en.py — генератор английской версии сайта, /en/.

Не самостоятельный источник правды: переиспользует общую вёрстку,
дизайн-токены, SVG-знак и инфраструктурные функции (header/footer/page_head,
которые уже умеют lang="en" и hreflang) из gen.py — их не нужно и не следует
дублировать. Контент — свой: EN_TEXTS/EN_PROJECTS/EN_CV_ROLES/EN_MANIFESTO
ниже, а также texts_en.json (переводы 38 текстов, переведены вручную,
слоты slug/image/link общие с русским TEXTS — переводится только то, что
видно читателю).

Запускать ПОСЛЕ gen.py (сам импортирует и выполняет gen.py через runpy —
поэтому отдельно запускать gen.py перед этим не нужно, но не вредно).

Что генерируется:
  en/index.html, en/manifesto/, en/texts/ (+38), en/projects/ (+5),
  en/recommendations/, en/about/, en/privacy/, en/cookies/, en/bot-rules/
Что НЕ дублируется на английский (осознанно, см. README):
  RSS (feed.xml — общий, тексты по-прежнему на русском источнике），
  PWA manifest.json/sw.js/offline.html (общие на весь сайт).
sitemap.xml — пересобирается этим скриптом заново (после gen.py), теперь
включает оba языка и hreflang xhtml:link на каждый URL.
"""
import os, html, json, runpy

HERE = os.path.dirname(os.path.abspath(__file__))
ns = runpy.run_path(os.path.join(HERE, "gen.py"))

ROOT = ns["ROOT"]
SITE_DOMAIN = ns["SITE_DOMAIN"]
BUILD_DATE = ns["BUILD_DATE"]
TEXTS_RU = ns["TEXTS"]
PROJECTS_RU = ns["PROJECTS"]
page_head = ns["page_head"]
header = ns["header"]
footer = ns["footer"]
marquee = ns["marquee"]
oval_divider = ns["oval_divider"]
tag_pill = ns["tag_pill"]
img_dims_attr = ns["img_dims_attr"]
link_label_with_meta_note_ru = ns["link_label_with_meta_note"]
LOGO_MARK_SVG = ns["LOGO_MARK_SVG"]
WORDMARK_SVG = ns["WORDMARK_SVG"]
NOIMG_MARK_SVG = ns["NOIMG_MARK_SVG"]

EN_ROOT = os.path.join(ROOT, "en")

def link_label_with_meta_note_en(label, url):
    esc = html.escape(label)
    if url and ("instagram.com" in url or "facebook.com" in url):
        note = ' <span class="meta-note">* Meta is recognized as an extremist organization and is banned in Russia.</span>'
        return esc + "*", note
    return esc, ""

# ---------------------------------------------------------------
# CONTENT — TEXTS (translations merged onto shared slug/image/link)
# ---------------------------------------------------------------
with open(os.path.join(HERE, "texts_en.json"), encoding="utf-8") as f:
    _EN_TEXT_DATA = json.load(f)
_ru_by_slug = {t["slug"]: t for t in TEXTS_RU}
TEXTS_EN = []
for et in _EN_TEXT_DATA:
    rt = _ru_by_slug[et["slug"]]
    TEXTS_EN.append({
        "slug": et["slug"], "tag": et["tag"], "title": et["title"],
        "kicker": et["kicker"], "image": rt["image"], "paragraphs": et["paragraphs"],
        "meta": et.get("meta"), "link": et.get("link"), "link_label": et.get("link_label"),
    })

MANIFESTO_POINTS_EN = [
  "\u201cOrganized Culturality\u201d is a free space whose forms and formats are deeply unpredictable \u2014 as are the subjects worth talking about.",
  "The author isn\u2019t here to entertain you, distract you, or tell you what to watch. The only thing that decides what gets written about is emotion.",
  "Since the texts get published, what you make of them matters a great deal.",
  "Now and then you\u2019ll want to pass something on through Culturality\u2019s other channels \u2014 they\u2019re all listed in the profile.",
  "Without a response everything carries on regardless, but it\u2019s good to feel that somebody needed to be here. Don\u2019t hold back a like, or a comment if you have one.",
  "Criticism that goes somewhere, and offers of work, are welcome too. Bear in mind that the author takes everything to heart \u2014 go easy on the insults and the advertising.",
  "There\u2019s no place here for abuse. The author isn\u2019t built for stirring up hostility, so let\u2019s not take it that far. Arguing about politics, with or without cause, is particularly out of place. If you disagree with something, leave without making a scene.",
]

CV_ROLES_EN = [
    {
        "role": "Co-founder & Producer", "org": "AELITA PRODUCTION",
        "period": "June 2025 \u2014 present",
        "bullets": [
            "Built a production company from nothing; 10+ projects delivered in under a year",
            "Producer of the Tochka Kyuri festival (Stary Oskol, October 2026)",
            "Built the brand identity, the website and the Telegram bot; runs social media across four platforms",
        ],
    },
    {
        "role": "Social Media", "org": "Komnata Sveta",
        "period": "January 2022 \u2014 present",
        "bullets": [
            "Social media for Komnata Sveta \u2014 productions by graduates of Yuri Butusov\u2019s workshop",
            "Organiser of BuFest 2026, a theatre festival at the Skorokhod venue (10\u201315 August)",
            "Ran \u201cZAVIST\u2019\u201d (dir. Sofia Nikiforova) \u2014 sold out, with real interest from the profession",
            "Brought Butusov\u2019s workshop to St. Petersburg for regular guest performances; every night sold out",
        ],
    },
    {
        "role": "Social Media, Project Manager", "org": "Scientific-Technological Theatre",
        "period": "May 2021 \u2014 present",
        "bullets": [
            "Social media for Russia\u2019s first robotic theatre, nominated for a Golden Mask in the Experiment category",
            "Performances at the New Stage of the Alexandrinsky Theatre, Sevkabel Port, Planetarium No. 1, MMOMA and elsewhere",
            "Set up collaborations with state and commercial venues across Moscow and St. Petersburg",
        ],
    },
    {
        "role": "Producer", "org": "Sofia Nikiforova (sole trader)",
        "period": "2021 \u2014 2022",
        "bullets": ["An educational project between film and theatre, inside a commercial structure"],
    },
    {
        "role": "Social Media", "org": "Svoboda self-portrait studio",
        "period": "", "bullets": ["Social media for one of St. Petersburg\u2019s more distinctive photo studios"],
    },
    {
        "role": "Social Media & PR", "org": "Novy Vyatich",
        "period": "", "bullets": ["Social media and PR for Kaluga\u2019s leading souvenir brand"],
    },
]

PROJECTS_EN = [
  {
    "slug": "aelita-production", "role": "Co-founder & Producer", "period": "June 2025 \u2014 present",
    "title": "AELITA PRODUCTION",
    "kicker": "A production company built from nothing \u2014 more than ten completed projects in under a year.",
    "facts": [("10+", "projects in a year"), ("2025", "founded")],
    "paragraphs": [
      "AELITA PRODUCTION is a production company I started in June 2025. In under a year: more than ten completed projects, from festivals to brand identities and websites for theatre companies.",
      "The work includes producing the Tochka Kyuri festival in Stary Oskol, building brand identities and full websites with Telegram bots, and running social media for several projects at once.",
      "AELITA also works with the dance company Koroche \u2014 organising performances, touring and promotion.",
    ],
    "link": "https://aelita-production.ru", "link_label": "aelita-production.ru",
  },
  {
    "slug": "bufest", "role": "Festival Organiser", "period": "August 2026",
    "title": "BuFest",
    "kicker": "A St. Petersburg theatre festival named for Yuri Butusov \u2014 three productions by his students across six evenings at Skorokhod.",
    "facts": [("3", "productions"), ("6", "evenings"), ("10\u201315 Aug", "dates")],
    "paragraphs": [
      "BuFest is a St. Petersburg theatre festival named for Yuri Butusov, a director at the Lensoviet and Vakhtangov theatres. It's organised by the theatre company Komnata Sveta and held at Skorokhod (107 Moskovsky Avenue, building 5).",
      "The main programme is three productions staged by Butusov's former students: \u201cViy. Conjectures\u201d (dir. Alexander Tserenya), \u201cThe Cherry Orchard\u201d (dir. Egor Kovalyov) and \u201cThe Seagull\u201d (dir. Ilya Zaitsev). Each runs twice, on consecutive nights, without an interval, starting at 20:00.",
      "Alongside the performances runs BuFet, a programme of one-off events: Yulia Smelkina's photographs of Butusov in rehearsal, a walk through \u201cButusov's Petersburg\u201d with Darya Pavlenko, a conversation with Van Shen, and a screening of Sofia Nikiforova's documentary \u201cChronicles of My Love.\u201d",
      "I organise the festival as part of the Komnata Sveta team, where I've run social media since January 2022.",
    ],
    "link": None, "link_label": None,
  },
  {
    "slug": "tochka-kyuri", "role": "Festival Producer", "period": "October 2026",
    "title": "Tochka Kyuri",
    "kicker": "A festival in Stary Oskol, produced by AELITA PRODUCTION.",
    "facts": [("Stary Oskol", "city"), ("Oct 2026", "dates")],
    "paragraphs": [
      "Tochka Kyuri is a festival in Stary Oskol produced by AELITA PRODUCTION. The full programme will appear here nearer the time; this page is being updated as material becomes ready.",
    ],
    "link": None, "link_label": None,
  },
  {
    "slug": "komnata-sveta", "role": "Social Media", "period": "January 2022 \u2014 present",
    "title": "Komnata Sveta",
    "kicker": "A St. Petersburg theatre company \u2014 guest performances by Yuri Butusov's workshop, and BuFest, the festival held in his memory.",
    "facts": [("2021", "first production"), ("2022", "joined")],
    "paragraphs": [
      "Komnata Sveta is a St. Petersburg theatre company. Its first production, in 2021, was \u201cZAVIST\u2019,\u201d which found its audience long before BuFest.",
      "In 2024 and 2025 the company brought Butusov's workshop to St. Petersburg for guest performances, both times to a warm reception. In 2026 those performances grew into a festival held in his memory: BuFest.",
      "I've run the company's social media since January 2022, including the run of \u201cZAVIST\u2019\u201d (dir. Sofia Nikiforova) \u2014 sold out, with real interest from the profession \u2014 and the regular guest performances by Butusov's workshop in the city.",
    ],
    "link": "https://t.me/lightroom_theatre", "link_label": "Komnata Sveta on Telegram",
  },
  {
    "slug": "robot-kostya-project", "role": "Social Media, Project Manager", "period": "May 2021 \u2014 present",
    "title": "Robot Kostya",
    "kicker": "Russia's first robotic theatre \u2014 nominated for a Golden Mask in the Experiment category.",
    "facts": [("2021", "launched"), ("Golden Mask", "nomination")],
    "paragraphs": [
      "Robot Kostya is a project of the Scientific-Technological Theatre, the first theatre in Russia to put a robot performer on stage. It's built on Chekhov's \u201cSeagull,\u201d with the robot in one of the central roles.",
      "Nominated for a Golden Mask in the Experiment category. It has played the New Stage of the Alexandrinsky Theatre, Sevkabel Port, Planetarium No. 1 and MMOMA, as well as the Tochka Dostupa festival at Lumi\u00e8re Hall in St. Petersburg.",
      "I've run the project's social media and management since May 2021 \u2014 from announcements through to setting up collaborations with state and commercial venues in Moscow and St. Petersburg.",
    ],
    "link": "https://www.instagram.com/robot.kostya/", "link_label": "Robot Kostya on Instagram",
  },
]

def collab_box_en():
    return '''<div class="collab-box" id="collab">
    <h2>Collaboration</h2>
    <p>I produce, promote and build websites for theatre and arts projects. If you have an idea, a festival or a production that wants this kind of attention to detail, get in touch.</p>
    <div class="collab-buttons">
      <a class="btn-line" href="mailto:kostyamoshnikov@gmail.com">Email me</a>
      <a class="btn-line" href="https://t.me/orgculture" target="_blank" rel="noopener">Message on Telegram</a>
    </div>
  </div>'''

def card_en(t, depth):
    root = "../" * depth if depth else "./"
    href = f"{root}en/texts/{t['slug']}/"
    if t["image"]:
        thumb = f'<div class="thumb"><img src="{root}images/{t["image"]}" alt="{html.escape(t["title"])}"{img_dims_attr(t["image"])} loading="lazy"></div>'
    else:
        thumb = f'<div class="thumb noimg">{NOIMG_MARK_SVG}</div>'
    return f'''<a class="card" href="{href}" data-tag="{html.escape(t['tag'])}">
      {thumb}
      <div class="body">
        {tag_pill(t['tag'])}
        <h3>{html.escape(t['title'])}</h3>
        <p>{html.escape(t['kicker'])}</p>
      </div>
    </a>'''

def proj_card_en(pr, depth):
    root = "../" * depth if depth else "./"
    href = f"{root}en/projects/{pr['slug']}/"
    return f'''<a class="proj-card" href="{href}">
      {tag_pill(pr['role'])}
      <div class="proj-period">{html.escape(pr['period'])}</div>
      <h3>{html.escape(pr['title'])}</h3>
      <p>{html.escape(pr['kicker'])}</p>
    </a>'''

def build_search_index_en():
    idx = []
    for t in TEXTS_EN:
        blob = " ".join([t["title"], t["kicker"], t["tag"]] + t["paragraphs"])
        idx.append({"slug": t["slug"], "text": blob})
    return idx

# ---------------------------------------------------------------
# INDEX (home)
# ---------------------------------------------------------------
def build_index_en():
    latest = TEXTS_EN[:6]
    rec_with_link = [t for t in TEXTS_EN if t["link"]][:3]
    rec_html = ""
    for t in rec_with_link:
        if t["image"]:
            img = f'<div class="recimg"><img src="../images/{t["image"]}" alt=""{img_dims_attr(t["image"])} loading="lazy"></div>'
        else:
            img = f'<div class="recimg noimg">{NOIMG_MARK_SVG}</div>'
        rec_html += f'''<a class="recrow" href="texts/{t['slug']}/" style="text-decoration:none;">
      {img}
      <div>
        {tag_pill(t['tag'])}
        <h3 style="margin-top:8px;">{html.escape(t['title'])}</h3>
      </div>
      <span class="go">{html.escape(t['link_label'] or 'more')} \u2192</span>
    </a>'''

    body = f'''
{header(1, lang="en")}
<div class="hero wrap">
  <div class="mark">{LOGO_MARK_SVG}</div>
  <div class="word">{WORDMARK_SVG}</div>
  <div class="slogan">* Without aggression, but with expression</div>
  <p class="lede">A space where meanings get made. Texts about films, plays, music and people \u2014 written not to recommend, but to think something through.</p>
  <div class="hero-ctas">
    <a class="btn-line" href="texts/">Read the texts</a>
    <a class="btn-line btn-line-ghost" href="about/#collab">For projects</a>
  </div>
</div>

{marquee("WITHOUT AGGRESSION, BUT WITH EXPRESSION")}

{oval_divider()}

<section class="tight">
  <div class="wrap-wide">
    <div class="sec-head">
      <h2>Latest texts</h2>
      <a class="more" href="texts/">all texts \u2192</a>
    </div>
    <div class="grid">
      {''.join(card_en(t, 1) for t in latest)}
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap-wide">
    <div class="sec-head">
      <h2>Recommendations</h2>
      <a class="more" href="recommendations/">all recommendations \u2192</a>
    </div>
    <div class="reclist">
      {rec_html}
    </div>
  </div>
</section>

<section class="tight">
  <div class="wrap" style="text-align:center;">
    <div class="eyebrow" style="margin-bottom:18px;">Manifesto</div>
    <p style="font-size:19px;font-weight:300;line-height:1.8;max-width:620px;margin:0 auto 28px;">
      \u201cOrganized Culturality\u201d is a free space whose forms and formats are deeply unpredictable, as are the subjects worth writing about.
    </p>
    <a class="btn-line" href="manifesto/">Read the full manifesto</a>
  </div>
</section>

{footer(1, lang="en")}
'''
    return page_head("Organized Culturality", "A space where meanings get made. Texts about films, plays, music and people.", 1, path="en/", lang="en") + body

os.makedirs(EN_ROOT, exist_ok=True)
with open(os.path.join(EN_ROOT, "index.html"), "w", encoding="utf-8") as f:
    f.write(build_index_en())
print("en/index.html written")

# ---------------------------------------------------------------
# TEXTS INDEX (with search, mirrors RU version)
# ---------------------------------------------------------------
def build_texts_index_en():
    tags = sorted(set(t["tag"] for t in TEXTS_EN))
    filter_html = '<button class="filter-pill active" data-filter="all">All</button>' + \
        "".join(f'<button class="filter-pill" data-filter="{html.escape(tg)}">{html.escape(tg)}</button>' for tg in tags)
    search_data = json.dumps(build_search_index_en(), ensure_ascii=False)

    body = f'''
{header(2, "texts", relpath="texts/", lang="en")}
<section style="padding-top:64px;">
  <div class="wrap-wide">
    <div class="eyebrow">Section</div>
    <h1 style="font-size:34px;font-weight:300;margin:14px 0 10px;">Texts</h1>
    <p style="color:var(--dim);max-width:620px;font-size:15.5px;line-height:1.8;margin-bottom:32px;">
      Reviews and reflections on films, plays, music and concerts \u2014 published to no schedule, whenever something asks to be written about.
    </p>
    <div class="search-row">
      <input type="search" id="text-search" class="search-input" placeholder="Search the texts\u2026" aria-label="Search the texts" autocomplete="off">
    </div>
    <div class="filter-row" id="filter-row">
      {filter_html}
    </div>
    <div style="margin:-16px 0 32px;"><a href="../feed.xml" style="font-size:12px;color:var(--dim2);">RSS \u2192</a></div>
    <div class="grid" id="texts-grid">
      {''.join(card_en(t, 2) for t in TEXTS_EN)}
    </div>
    <p id="filter-empty" style="display:none;color:var(--dim);font-size:15px;margin-top:20px;">Nothing found. Try a different search or tag.</p>
  </div>
</section>
{footer(2, lang="en")}
<script id="search-index" type="application/json">{search_data}</script>
<script>
  (function(){{
    var row = document.getElementById('filter-row');
    var input = document.getElementById('text-search');
    var cards = document.querySelectorAll('#texts-grid .card');
    var empty = document.getElementById('filter-empty');
    var activeTag = 'all';
    var searchIdx = {{}};
    try {{
      JSON.parse(document.getElementById('search-index').textContent).forEach(function(it){{
        searchIdx[it.slug] = it.text.toLowerCase();
      }});
    }} catch(e) {{}}
    function slugFromHref(href){{
      var m = href.match(/texts\\/([^\\/]+)\\//);
      return m ? m[1] : '';
    }}
    function applyFilters(){{
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      cards.forEach(function(c){{
        var tagOk = (activeTag === 'all' || c.dataset.tag === activeTag);
        var slug = slugFromHref(c.getAttribute('href'));
        var textOk = !q || (searchIdx[slug] && searchIdx[slug].indexOf(q) !== -1);
        var match = tagOk && textOk;
        c.style.display = match ? '' : 'none';
        if (match) shown++;
      }});
      empty.style.display = shown === 0 ? 'block' : 'none';
    }}
    row.addEventListener('click', function(e){{
      var btn = e.target.closest('.filter-pill');
      if (!btn) return;
      row.querySelectorAll('.filter-pill').forEach(function(b){{ b.classList.remove('active'); }});
      btn.classList.add('active');
      activeTag = btn.dataset.filter;
      applyFilters();
    }});
    input.addEventListener('input', applyFilters);
  }})();
</script>
'''
    return page_head("Texts \u2014 Organized Culturality", "All texts: reviews and reflections on films, plays, music and concerts.", 2, path="en/texts/", lang="en") + body

os.makedirs(os.path.join(EN_ROOT, "texts"), exist_ok=True)
with open(os.path.join(EN_ROOT, "texts", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_texts_index_en())
print("en/texts/index.html written")

# ---------------------------------------------------------------
# TEXT PAGES
# ---------------------------------------------------------------
def build_text_page_en(t, idx):
    depth = 3
    root = "../" * depth
    paras = "\n      ".join(f"<p>{html.escape(p)}</p>" for p in t["paragraphs"])

    heroimg = ""
    if t["image"]:
        heroimg = f'''<div class="wrap-wide"><div class="text-heroimg"><img src="{root}images/{t['image']}" alt="{html.escape(t['title'])}"{img_dims_attr(t['image'])}></div></div>'''

    meta_html = ""
    if t["meta"]:
        link_html = ""
        if t["link"]:
            label, note = link_label_with_meta_note_en(t["link_label"], t["link"])
            link_html = f'<br><a class="btn" href="{html.escape(t["link"])}" target="_blank" rel="noopener">{label} \u2192</a>{note}'
        meta_html = f'<div class="text-meta">{html.escape(t["meta"])}{link_html}</div>'

    prev_t = TEXTS_EN[idx-1] if idx > 0 else TEXTS_EN[-1]
    next_t = TEXTS_EN[idx+1] if idx < len(TEXTS_EN)-1 else TEXTS_EN[0]
    nav_html = f'''<div class="wrap"><div class="text-nav">
      <a href="{root}en/texts/{prev_t['slug']}/">\u2190 {html.escape(prev_t['title'][:40])}{'\u2026' if len(prev_t['title'])>40 else ''}</a>
      <a href="{root}en/texts/{next_t['slug']}/">{html.escape(next_t['title'][:40])}{'\u2026' if len(next_t['title'])>40 else ''} \u2192</a>
    </div></div>'''

    same_tag = [x for x in TEXTS_EN if x["tag"] == t["tag"] and x["slug"] != t["slug"]]
    related = same_tag[:3] if same_tag else [x for x in TEXTS_EN if x["slug"] != t["slug"]][:3]
    related_html = "".join(card_en(x, depth) for x in related)
    related_block = f'''<div class="wrap-wide" style="padding:56px 0 0;">
  <div class="sec-head"><h2 style="font-size:20px;">Related texts</h2></div>
  <div class="grid">{related_html}</div>
</div>'''

    channel_cta = f'''<div class="wrap" style="padding:56px 0 0;">
  <div class="collab-box" style="text-align:center;">
    <p style="margin-bottom:22px;">New texts go out on the Telegram channel \u2014 no algorithm, no feed.</p>
    <div class="collab-buttons">
      <a class="btn-line" href="https://t.me/orgculture" target="_blank" rel="noopener">Subscribe on Telegram</a>
    </div>
  </div>
</div>'''

    schema = {
        "@context": "https://schema.org", "@type": "Article",
        "headline": t["title"], "description": t["kicker"],
        "author": {"@type": "Person", "name": "Konstantin Moshnikov"},
        "publisher": {"@type": "Organization", "name": "Organized Culturality"},
        "mainEntityOfPage": f"{SITE_DOMAIN}/en/texts/{t['slug']}/",
        "inLanguage": "en",
    }
    if t["image"]:
        schema["image"] = f"{SITE_DOMAIN}/images/{t['image']}"
    schema_html = f'<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>'

    body = f'''
{schema_html}
{header(depth, "texts", relpath=f"texts/{t['slug']}/", lang="en")}
<div class="text-hero wrap-wide">
  {tag_pill(t['tag'])}
  <h1 style="margin-top:16px;">{html.escape(t['title'])}</h1>
  <p class="kicker">{html.escape(t['kicker'])}</p>
</div>
{heroimg}
<div class="text-body wrap">
  {paras}
  {meta_html}
</div>
{related_block}
{channel_cta}
{nav_html}
{footer(depth, lang="en")}
'''
    return page_head(f"{t['title']} \u2014 Organized Culturality", t['kicker'], depth, og_image=(f"{SITE_DOMAIN}/images/{t['image']}" if t['image'] else None), path=f"en/texts/{t['slug']}/", lang="en") + body

for i, t in enumerate(TEXTS_EN):
    d = os.path.join(EN_ROOT, "texts", t["slug"])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_text_page_en(t, i))
print(f"{len(TEXTS_EN)} en text pages written")

# ---------------------------------------------------------------
# MANIFESTO
# ---------------------------------------------------------------
def build_manifesto_en():
    items = ""
    for i, p in enumerate(MANIFESTO_POINTS_EN, 1):
        items += f'''<div class="manifesto-item">
      <div class="num">{i:02d}</div>
      <p>{html.escape(p)}</p>
    </div>
    '''
    body = f'''
{header(2, "manifesto", relpath="manifesto/", lang="en")}
<section style="padding-top:64px;">
  <div class="wrap">
    <div class="eyebrow">Manifesto</div>
    <h1 style="font-size:32px;font-weight:300;margin:14px 0 30px;">The \u201cOrganized Culturality\u201d Manifesto</h1>
    <div class="manifesto-epigraph">
      A manifesto that moves with the mood.<br><br>
      Read it if you like. These aren\u2019t rules to follow, in the end \u2014 just a request for a bit of awareness.<br><br>
      Splitting it into points was never meant to fix anything in place; it\u2019s a wish for quiet, and for some things to stay unconsidered.
    </div>
    {items}
  </div>
</section>
{footer(2, lang="en")}
'''
    return page_head("Manifesto \u2014 Organized Culturality", "The \u201cOrganized Culturality\u201d manifesto \u2014 a free space whose forms and formats are deeply unpredictable.", 2, path="en/manifesto/", lang="en") + body

os.makedirs(os.path.join(EN_ROOT, "manifesto"), exist_ok=True)
with open(os.path.join(EN_ROOT, "manifesto", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_manifesto_en())
print("en/manifesto/index.html written")

# ---------------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------------
def build_recommendations_en():
    rows = ""
    for t in TEXTS_EN:
        if t["image"]:
            img = f'<div class="recimg"><img src="../../images/{t["image"]}" alt=""{img_dims_attr(t["image"])} loading="lazy"></div>'
        else:
            img = f'<div class="recimg noimg">{NOIMG_MARK_SVG}</div>'
        if t["link"]:
            label, note = link_label_with_meta_note_en(t["link_label"], t["link"])
            go = f'<a class="go" href="{html.escape(t["link"])}" target="_blank" rel="noopener">{label} \u2192</a>{note}'
        else:
            go = f'<a class="go" href="../texts/{t["slug"]}/">read \u2192</a>'
        rows += f'''<div class="recrow">
      {img}
      <div>
        {tag_pill(t['tag'])}
        <h3 style="margin-top:8px;">{html.escape(t['title'])}</h3>
        <p>{html.escape(t['kicker'])}</p>
      </div>
      {go}
    </div>
    '''
    body = f'''
{header(2, "recommendations", relpath="recommendations/", lang="en")}
<section style="padding-top:64px;">
  <div class="wrap-wide">
    <div class="eyebrow">Section</div>
    <h1 style="font-size:32px;font-weight:300;margin:14px 0 10px;">Recommendations</h1>
    <p style="color:var(--dim);max-width:620px;font-size:15.5px;line-height:1.8;margin-bottom:44px;">
      What to watch, hear and go and see \u2014 short verdicts, with a link to the source and to the full text.
    </p>
    <div class="reclist">
      {rows}
    </div>
  </div>
</section>
{footer(2, lang="en")}
'''
    return page_head("Recommendations \u2014 Organized Culturality", "What to watch, hear and go and see: films, plays, concerts, records.", 2, path="en/recommendations/", lang="en") + body

os.makedirs(os.path.join(EN_ROOT, "recommendations"), exist_ok=True)
with open(os.path.join(EN_ROOT, "recommendations", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_recommendations_en())
print("en/recommendations/index.html written")

# ---------------------------------------------------------------
# ABOUT
# ---------------------------------------------------------------
def build_about_en():
    roles_html = ""
    for r in CV_ROLES_EN:
        bullets = "".join(f"<li>{html.escape(b)}</li>" for b in r["bullets"])
        period = f'<span class="period">{html.escape(r["period"])}</span>' if r["period"] else ""
        roles_html += f'''<div class="cv-role">
      <div class="row1"><h4>{html.escape(r['role'])}</h4>{period}</div>
      <div class="org">{html.escape(r['org'])}</div>
      <ul>{bullets}</ul>
    </div>
    '''
    body = f'''
{header(2, "about", relpath="about/", lang="en")}
<section style="padding-top:64px;">
  <div class="wrap-wide about-grid">
    <div class="about-photo"><img src="../../images/author.jpg" alt="Author of Organized Culturality"{img_dims_attr("author.jpg")}></div>
    <div class="about-copy">
      <div class="eyebrow">Author</div>
      <h1 style="font-size:30px;font-weight:300;margin:14px 0 24px;">Konstantin Moshnikov</h1>
      <p>15+ years on stage, in circus and in theatre. I know the industry from the inside, at every level of it.</p>
      <p>I produce and run social media for cultural and arts projects: concept through to launch, marketing through to logistics. \u201cOrganized Culturality\u201d runs alongside that work \u2014 texts about whatever struck a nerve, with no obligation to convince anyone of anything.</p>
      <p style="color:var(--dim);font-size:14.5px;">
        aelita-production.ru \u00b7 kostyamoshnikov@gmail.com \u00b7 +7 904 617-01-88
      </p>
      <p style="font-size:14.5px;">
        <a href="https://t.me/orgculture" target="_blank" rel="noopener" style="color:var(--accent);">\u201cOrganized Culturality\u201d on Telegram</a> \u00b7
        <a href="https://vk.ru/orgculture" target="_blank" rel="noopener" style="color:var(--accent);">VK</a>
      </p>
      <div style="margin-top:22px;"><a class="btn-line" href="../../documents/CV-Konstantin-Moshnikov.pdf" download>Download CV</a></div>

      <div class="oval-divider" style="justify-content:flex-start;margin:40px 0 8px;"><div style="width:64px;">{ns['OVAL_DIVIDER_SVG']}</div></div>
      <div class="eyebrow" style="margin-bottom:8px;">Experience</div>
      <div class="cv-block">
        {roles_html}
      </div>

      <div class="eyebrow" style="margin:36px 0 8px;">Performing arts</div>
      <p style="font-size:15px;color:var(--dim);">Circus performer, 15+ years. Currently in the operetta \u201cPrincess Circus\u201d at the St. Petersburg Musical Comedy Theatre (August and October 2026).</p>
    </div>
  </div>
</section>
{footer(2, lang="en")}
'''
    return page_head("Author \u2014 Organized Culturality", "Konstantin Moshnikov \u2014 producer, social media, circus performer. Author of \u201cOrganized Culturality.\u201d", 2, path="en/about/", lang="en") + body

os.makedirs(os.path.join(EN_ROOT, "about"), exist_ok=True)
with open(os.path.join(EN_ROOT, "about", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_about_en())
print("en/about/index.html written")

# ---------------------------------------------------------------
# PROJECTS
# ---------------------------------------------------------------
def build_projects_index_en():
    body = f'''
{header(2, "projects", relpath="projects/", lang="en")}
<section style="padding-top:64px;">
  <div class="wrap-wide">
    <div class="eyebrow">Section</div>
    <h1 style="font-size:34px;font-weight:300;margin:14px 0 10px;">Projects</h1>
    <p style="color:var(--dim);max-width:620px;font-size:15.5px;line-height:1.8;margin-bottom:44px;">
      Producing, promotion and websites for theatre and arts projects \u2014 the work that runs alongside the writing.
    </p>
    <div class="grid">
      {''.join(proj_card_en(pr, 2) for pr in PROJECTS_EN)}
    </div>
    <div style="height:60px;"></div>
    {collab_box_en()}
  </div>
</section>
{footer(2, lang="en")}
'''
    return page_head("Projects \u2014 Organized Culturality", "Producing, promotion and websites for theatre and arts projects: AELITA PRODUCTION, BuFest, Komnata Sveta, Robot Kostya.", 2, path="en/projects/", lang="en") + body

os.makedirs(os.path.join(EN_ROOT, "projects"), exist_ok=True)
with open(os.path.join(EN_ROOT, "projects", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_projects_index_en())
print("en/projects/index.html written")

def build_project_page_en(pr, idx):
    depth = 3
    root = "../" * depth
    paras = "\n      ".join(f"<p>{html.escape(x)}</p>" for x in pr["paragraphs"])
    facts_html = "".join(f'<div class="proj-fact"><div class="n">{html.escape(n)}</div><div class="l">{html.escape(l)}</div></div>' for n, l in pr["facts"])

    link_html = ""
    if pr["link"]:
        label, note = link_label_with_meta_note_en(pr["link_label"], pr["link"])
        link_html = f'<div style="margin-top:36px;"><a class="btn-line" href="{html.escape(pr["link"])}" target="_blank" rel="noopener">{label} \u2192</a>{note}</div>'

    prev_p = PROJECTS_EN[idx-1] if idx > 0 else PROJECTS_EN[-1]
    next_p = PROJECTS_EN[idx+1] if idx < len(PROJECTS_EN)-1 else PROJECTS_EN[0]
    nav_html = f'''<div class="wrap"><div class="text-nav">
      <a href="{root}en/projects/{prev_p['slug']}/">\u2190 {html.escape(prev_p['title'])}</a>
      <a href="{root}en/projects/{next_p['slug']}/">{html.escape(next_p['title'])} \u2192</a>
    </div></div>'''

    body = f'''
{header(depth, "projects", relpath=f"projects/{pr['slug']}/", lang="en")}
<div class="text-hero wrap-wide">
  {tag_pill(pr['role'])}
  <h1 style="margin-top:16px;">{html.escape(pr['title'])}</h1>
  <p class="kicker">{html.escape(pr['kicker'])}</p>
</div>
<div class="wrap">
  <div class="proj-fact-row">{facts_html}</div>
</div>
<div class="text-body wrap">
  {paras}
  {link_html}
</div>
{nav_html}
<div class="wrap" style="padding:60px 0;">{collab_box_en()}</div>
{footer(depth, lang="en")}
'''
    return page_head(f"{pr['title']} \u2014 Organized Culturality", pr['kicker'], depth, path=f"en/projects/{pr['slug']}/", lang="en") + body

for i, pr in enumerate(PROJECTS_EN):
    d = os.path.join(EN_ROOT, "projects", pr["slug"])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_project_page_en(pr, i))
print(f"{len(PROJECTS_EN)} en project pages written")

# ---------------------------------------------------------------
# LEGAL PAGES
# ---------------------------------------------------------------
def legal_page_en(title_ru_equiv, h1, doc_meta, sections, extra_links, path, description):
    sections_html = ""
    for stitle, paras in sections:
        sections_html += f"<h2>{html.escape(stitle)}</h2>\n" + "\n".join(f"<p>{html.escape(p)}</p>" for p in paras) + "\n"
    links_html = "".join(f'<a class="btn-line" href="{href}"{extra}>{html.escape(label)}</a>' for href, label, extra in extra_links)
    body = f'''
{header(2, relpath=path, lang="en")}
<section style="padding-top:64px;">
  <div class="wrap">
    <div class="eyebrow">Document</div>
    <h1 style="font-size:30px;font-weight:300;margin:14px 0 4px;">{h1}</h1>
    <div class="doc-meta">{doc_meta}</div>
    <div class="doc-body" style="margin-top:36px;">
      {sections_html}
      <div class="doc-requisites">
        Konstantin Alekseevich Moshnikov<br>
        Self-employed (NPD tax regime) \u00b7 INN 471508674254<br>
        St. Petersburg, Russia<br>
        Email: kostyamoshnikov@gmail.com
      </div>
    </div>
    <div style="margin-top:36px;display:flex;gap:16px;flex-wrap:wrap;">
      {links_html}
    </div>
  </div>
</section>
{footer(2, lang="en")}
'''
    return page_head(title_ru_equiv, description, 2, path=f"en/{path}", lang="en") + body

def build_privacy_en():
    sections = [
      ("1. General Provisions", [
        "1.1. The personal data controller is Konstantin Alekseevich Moshnikov, self-employed (payer of professional income tax), INN 471508674254, St. Petersburg, Russia.",
        "1.2. This Policy is drafted in accordance with Federal Law No. 152-FZ \u201cOn Personal Data\u201d of 27.07.2006 and sets out how personal data of orgculture.ru users and its related communication channels (Telegram, email) is processed.",
        "1.3. Using the site, contacting the Telegram bot, or using any other channel listed on the site constitutes agreement with the terms of this Policy.",
      ]),
      ("2. Purposes of Processing", [
        "Responding to users, including replies to inquiries and collaboration requests; concluding and performing paid-service agreements (production, promotion, website development, and other services provided by the Controller outside the site, by direct arrangement); improving the site; complying with the requirements of Russian law.",
      ]),
      ("3. Categories of Data Processed", [
        "Name; phone number; email address; Telegram ID and username; message content \u2014 to the extent voluntarily provided by the user when making contact.",
        "Anonymized technical data about site visits (cookies, click and on-page activity statistics) is also processed automatically via Yandex Metrica \u2014 see the Cookie Policy for details.",
      ]),
      ("4. Legal Grounds for Processing", [
        "Consent of the data subject; performance of a contract to which the data subject is a party or beneficiary; fulfillment of obligations under Russian law.",
      ]),
      ("5. Terms and Conditions of Processing", [
        "5.1. The Controller takes the necessary organizational and technical measures to protect personal data from unlawful or accidental access, destruction, alteration, blocking, copying, or dissemination.",
        "5.2. Data is not transferred to third parties, except where expressly required by Russian law, for anonymized statistics processed by Yandex Metrica (Yandex LLC), or with the data subject's separate consent. Once the purpose of processing is achieved, or consent is withdrawn, data is destroyed or anonymized.",
      ]),
      ("6. Rights of Data Subjects", [
        "Users are entitled to: receive information regarding the processing of their personal data; request correction, blocking, or deletion of data that is incomplete, outdated, or inaccurate; withdraw consent to processing. Requests can be sent to: kostyamoshnikov@gmail.com",
      ]),
      ("7. Liability", [
        "The Controller is liable for violations of personal data processing procedures in accordance with Russian law. Users are responsible for the accuracy of the data they provide.",
      ]),
      ("8. Changes to This Policy", [
        "The Controller may amend this Policy. The new version takes effect once published on the site.",
      ]),
    ]
    extra_links = [
      ("../../", "\u2190 Home", ""),
      ("../../documents/privacy-policy.pdf", "Download PDF", " download"),
    ]
    return legal_page_en("Privacy Policy \u2014 Organized Culturality", "Privacy Policy", "orgculture.ru \u00b7 revised 30.07.2026", sections, extra_links, "privacy/", "Privacy policy for orgculture.ru.")

os.makedirs(os.path.join(EN_ROOT, "privacy"), exist_ok=True)
with open(os.path.join(EN_ROOT, "privacy", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_privacy_en())
print("en/privacy/index.html written")

def build_bot_rules_en():
    sections = [
      ("1. General Provisions", [
        "1.1. These Rules govern the relationship between Konstantin Alekseevich Moshnikov, self-employed (INN 471508674254), and users of the \u201cOrganized Culturality\u201d Telegram bot.",
        "1.2. By using the bot \u2014 including by sending /start \u2014 the user accepts these Rules and the Privacy Policy.",
        "1.3. These Rules form an integral part of the documents published on orgculture.ru.",
      ]),
      ("2. Purpose of the Bot", [
        "The bot provides access to the site's informational materials (manifesto, texts, projects, recommendations) and lets users send a message directly \u2014 forwarded to the site operator, with the option of a reply.",
      ]),
      ("3. Data Processing", [
        "Contacting the bot involves processing: Telegram ID and username, as well as the content of voluntarily sent messages (text, photos, documents, voice messages). See the Privacy Policy for details.",
      ]),
      ("4. Liability", [
        "The Operator does not guarantee an instant reply to messages sent via the bot. The Operator reserves the right not to respond to messages containing abuse, spam, or unlawful content.",
      ]),
      ("5. Changes to These Rules", [
        "The Operator may amend these Rules. The new version takes effect once published on the site.",
      ]),
    ]
    extra_links = [
      ("../../", "\u2190 Home", ""),
      ("../privacy/", "Privacy Policy", ""),
    ]
    return legal_page_en("Bot Usage Rules \u2014 Organized Culturality", "Telegram Bot Usage Rules", "@orgculture \u00b7 revised 30.07.2026", sections, extra_links, "bot-rules/", "Usage rules for the \u201cOrganized Culturality\u201d Telegram bot.")

os.makedirs(os.path.join(EN_ROOT, "bot-rules"), exist_ok=True)
with open(os.path.join(EN_ROOT, "bot-rules", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_bot_rules_en())
print("en/bot-rules/index.html written")

def build_cookies_en():
    sections = [
      ("1. What Cookies Are", [
        "Cookies are small text files a site saves in the user's browser to recognize them on return visits and to gather usage statistics.",
      ]),
      ("2. What Cookies This Site Uses", [
        "orgculture.ru uses cookies from Yandex Metrica for anonymized visit statistics (pageviews, click activity, general navigation patterns). No advertising or cross-site tracking cookies are used.",
      ]),
      ("3. Consent", [
        "Yandex Metrica only starts once you click \u201cAccept\u201d in the cookie banner, or if you already gave consent on a previous visit. Declining doesn't restrict access to the site \u2014 it simply means visit statistics aren't collected.",
      ]),
      ("4. Managing Cookies", [
        "You can withdraw consent at any time via \u201cCookie settings\u201d in the site footer, or by clearing cookies in your browser settings. Browsers can also usually be configured to block cookies entirely.",
      ]),
      ("5. Changes to This Policy", [
        "The Operator may amend this Policy. The new version takes effect once published on the site.",
      ]),
    ]
    extra_links = [
      ("../../", "\u2190 Home", ""),
      ("../../documents/cookies-policy.pdf", "Download PDF", " download"),
    ]
    return legal_page_en("Cookie Policy \u2014 Organized Culturality", "Cookie Policy", "orgculture.ru \u00b7 revised 30.07.2026", sections, extra_links, "cookies/", "Cookie usage policy for orgculture.ru.")

os.makedirs(os.path.join(EN_ROOT, "cookies"), exist_ok=True)
with open(os.path.join(EN_ROOT, "cookies", "index.html"), "w", encoding="utf-8") as f:
    f.write(build_cookies_en())
print("en/cookies/index.html written")

# ---------------------------------------------------------------
# COMBINED SITEMAP (RU + EN, with hreflang alternates)
# ---------------------------------------------------------------
def build_combined_sitemap():
    core = ["", "manifesto/", "texts/", "projects/", "recommendations/", "about/", "privacy/", "bot-rules/", "cookies/"]
    ru_paths = list(core) + [f"texts/{t['slug']}/" for t in TEXTS_RU] + [f"projects/{p['slug']}/" for p in PROJECTS_RU]
    en_paths = list(core) + [f"texts/{t['slug']}/" for t in TEXTS_EN] + [f"projects/{p['slug']}/" for p in PROJECTS_EN]
    entries = []
    for rp, ep in zip(ru_paths, en_paths):
        entries.append((rp, f"en/{ep}"))
    urls = []
    for rp, ep in entries:
        urls.append(f'''  <url>
    <loc>{SITE_DOMAIN}/{rp}</loc>
    <lastmod>{BUILD_DATE}</lastmod>
    <xhtml:link rel="alternate" hreflang="ru" href="{SITE_DOMAIN}/{rp}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE_DOMAIN}/{ep}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE_DOMAIN}/{rp}"/>
  </url>''')
        urls.append(f'''  <url>
    <loc>{SITE_DOMAIN}/{ep}</loc>
    <lastmod>{BUILD_DATE}</lastmod>
    <xhtml:link rel="alternate" hreflang="ru" href="{SITE_DOMAIN}/{rp}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{SITE_DOMAIN}/{ep}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE_DOMAIN}/{rp}"/>
  </url>''')
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
{chr(10).join(urls)}
</urlset>
'''
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)
    print("sitemap.xml rewritten with RU+EN hreflang alternates")

build_combined_sitemap()

# ---------------------------------------------------------------
# RSS FEED (EN)
# ---------------------------------------------------------------
xml_escape = ns["xml_escape"]

def build_rss_en():
    items = ""
    for t in TEXTS_EN:
        link = f"{SITE_DOMAIN}/en/texts/{t['slug']}/"
        items += f'''  <item>
    <title>{xml_escape(t['title'])}</title>
    <link>{link}</link>
    <guid>{link}</guid>
    <description>{xml_escape(t['kicker'])}</description>
    <category>{xml_escape(t['tag'])}</category>
  </item>
'''
    from datetime import datetime as _dt
    build_dt = _dt.strptime(BUILD_DATE, "%Y-%m-%d")
    last_build_date = build_dt.strftime("%a, %d %b %Y 12:00:00 +0000")
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Organized Culturality \u2014 Texts</title>
  <link>{SITE_DOMAIN}/en/texts/</link>
  <atom:link href="{SITE_DOMAIN}/en/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Reviews and reflections on films, plays, music, and concerts.</description>
  <language>en</language>
  <lastBuildDate>{last_build_date}</lastBuildDate>
{items}</channel>
</rss>
'''
    with open(os.path.join(EN_ROOT, "feed.xml"), "w", encoding="utf-8") as f:
        f.write(rss)
    print("en/feed.xml written")

build_rss_en()

# ---------------------------------------------------------------
# PWA \u2014 en/manifest.json, en/offline.html
# ---------------------------------------------------------------
def build_manifest_en():
    manifest = {
        "name": "Organized Culturality",
        "short_name": "OC",
        "description": "A space for meanings and new significances to be born \u2014 texts, manifesto, projects.",
        "start_url": "/en/",
        "scope": "/en/",
        "display": "standalone",
        "background_color": "#0A0A0A",
        "theme_color": "#0A0A0A",
        "lang": "en",
        "icons": [
            {"src": "/assets/icons/favicon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/assets/icons/favicon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        ],
    }
    with open(os.path.join(EN_ROOT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("en/manifest.json written")

def build_offline_page_en():
    doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>You're offline \u2014 Organized Culturality</title>
<style>
  *{{margin:0;padding:0;box-sizing:border-box;}}
  body{{
    background:#0A0A0A;color:#F5F2ED;font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;
    min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px;
  }}
  svg{{width:100px;height:auto;margin-bottom:28px;}}
  h1{{font-weight:300;font-size:20px;margin-bottom:10px;}}
  p{{color:#9A968E;font-size:14px;}}
</style>
</head>
<body>
  {LOGO_MARK_SVG}
  <h1>No internet connection</h1>
  <p>This page hasn\u2019t been loaded yet \u2014 open it again once you\u2019re back online.</p>
</body>
</html>'''
    with open(os.path.join(EN_ROOT, "offline.html"), "w", encoding="utf-8") as f:
        f.write(doc)
    print("en/offline.html written")

build_manifest_en()
build_offline_page_en()

# ---------------------------------------------------------------
# SERVICE WORKER \u2014 rebuilt to precache both languages and pick the
# right offline fallback (RU/EN) based on the request path.
# ---------------------------------------------------------------
def build_combined_service_worker():
    SITE_VERSION = ns["SITE_VERSION"]
    ru_core = ["/", "/manifesto/", "/texts/", "/projects/", "/recommendations/", "/about/",
               "/privacy/", "/cookies/", "/bot-rules/"]
    en_core = ["/en/", "/en/manifesto/", "/en/texts/", "/en/projects/", "/en/recommendations/",
               "/en/about/", "/en/privacy/", "/en/cookies/", "/en/bot-rules/"]
    precache = ru_core + en_core + [
        "/offline.html", "/en/offline.html", "/manifest.json", "/en/manifest.json",
        "/assets/icons/favicon.svg", "/assets/icons/favicon-192.png", "/assets/icons/favicon-512.png",
        f"/assets/style.css?v={SITE_VERSION}",
    ]
    precache_js = ",\n  ".join(f"'{p}'" for p in precache)
    sw = f'''// \u2500\u2500 Organized Culturality \u00b7 Service Worker (RU + EN) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
// \u0421\u0442\u0440\u0430\u0442\u0435\u0433\u0438\u044f: Cache First \u0434\u043b\u044f \u0441\u0442\u0430\u0442\u0438\u043a\u0438, Network First \u0434\u043b\u044f HTML \u0441\u0442\u0440\u0430\u043d\u0438\u0446.
// \u041e\u0444\u043b\u0430\u0439\u043d-\u0444\u043e\u043b\u0431\u044d\u043a \u0432\u044b\u0431\u0438\u0440\u0430\u0435\u0442\u0441\u044f \u043f\u043e \u043f\u0440\u0435\u0444\u0438\u043a\u0441\u0443 /en/ \u0432 \u043f\u0443\u0442\u0438 \u0437\u0430\u043f\u0440\u043e\u0441\u0430.
//
// \u26a0\ufe0f \u042d\u0442\u043e\u0442 \u0444\u0430\u0439\u043b \u043f\u0435\u0440\u0435\u0441\u043e\u0431\u0438\u0440\u0430\u0435\u0442\u0441\u044f \u0432 gen_en.py (\u043f\u043e\u0441\u043b\u0435 gen.py) \u2014 \u043d\u0435 \u043f\u0440\u0430\u0432\u044c\u0442\u0435 \u0432\u0435\u0440\u0441\u0438\u044e
// \u0432 gen.py \u0438\u0437\u043e\u043b\u0438\u0440\u043e\u0432\u0430\u043d\u043d\u043e: \u0441\u043f\u0438\u0441\u043e\u043a PRECACHE_URLS \u0437\u0434\u0435\u0441\u044c \u0432\u043a\u043b\u044e\u0447\u0430\u0435\u0442 \u043e\u0431\u0430 \u044f\u0437\u044b\u043a\u0430.

const SITE_VERSION = {SITE_VERSION};
const CACHE_NAME = `orgculture-v${{SITE_VERSION}}`;
const STATIC_CACHE = `orgculture-static-v${{SITE_VERSION}}`;

const PRECACHE_URLS = [
  {precache_js}
];

self.addEventListener('install', event => {{
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
}});

self.addEventListener('activate', event => {{
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key !== CACHE_NAME && key !== STATIC_CACHE)
          .map(key => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
}});

self.addEventListener('fetch', event => {{
  const {{ request }} = event;
  const url = new URL(request.url);

  if (url.origin !== location.origin) return;

  if (request.headers.get('accept')?.includes('text/html')) {{
    event.respondWith(networkFirst(request));
    return;
  }}

  if (
    url.pathname.startsWith('/assets/') ||
    url.pathname.startsWith('/images/') ||
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.js') ||
    url.pathname.endsWith('.png') ||
    url.pathname.endsWith('.svg') ||
    url.pathname.endsWith('.ico')
  ) {{
    event.respondWith(cacheFirst(request));
    return;
  }}

  event.respondWith(networkFirst(request));
}});

async function networkFirst(request) {{
  const cache = await caches.open(CACHE_NAME);
  try {{
    const response = await fetch(request);
    if (response.ok) {{
      cache.put(request, response.clone());
    }}
    return response;
  }} catch {{
    const cached = await cache.match(request);
    if (cached) return cached;
    if (request.headers.get('accept')?.includes('text/html')) {{
      const url = new URL(request.url);
      const isEn = url.pathname.startsWith('/en/');
      const fallback = await cache.match(isEn ? '/en/offline.html' : '/offline.html');
      if (fallback) return fallback;
      const title = isEn ? 'Organized Culturality' : '\u041e\u0440\u0433\u0430\u043d\u0438\u0437\u043e\u0432\u0430\u043d\u043d\u0430\u044f \u041a\u0443\u043b\u044c\u0442\u0443\u0440\u043d\u043e\u0441\u0442\u044c';
      const msg = isEn ? 'No internet connection' : '\u041d\u0435\u0442 \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0435\u043d\u0438\u044f \u043a \u0438\u043d\u0442\u0435\u0440\u043d\u0435\u0442\u0443';
      return new Response(
        `<html><body style=\"background:#0A0A0A;color:#F5F2ED;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;text-align:center\"><div><h1 style=\"font-weight:300;\">${{title}}</h1><p style=\"color:#9A968E;\">${{msg}}</p></div></body></html>`,
        {{ headers: {{ 'Content-Type': 'text/html; charset=utf-8' }} }}
      );
    }}
    return new Response('', {{ status: 503 }});
  }}
}}

async function cacheFirst(request) {{
  const cache = await caches.open(STATIC_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;
  try {{
    const response = await fetch(request);
    if (response.ok) {{
      cache.put(request, response.clone());
    }}
    return response;
  }} catch {{
    return new Response('', {{ status: 503 }});
  }}
}}
'''
    with open(os.path.join(ROOT, "sw.js"), "w", encoding="utf-8") as f:
        f.write(sw)
    print("sw.js rewritten with RU+EN precache and locale-aware offline fallback")

build_combined_service_worker()
print("EN site build complete")
