// Цели на ключевые действия. Сгенерировано gen.py (build_analytics_events_js) —
// не редактировать руками. Список целей: ANALYTICS_GOALS в gen.py.
(function () {
  var YM_ID = 111176053;
  var GOALS = ['page_not_found', 'brief_start', 'brief_submit', 'offer_download', 'cv_download', 'press_kit_download', 'telegram_channel_click', 'telegram_bot_click', 'vk_click', 'email_click', 'review_submit', 'rss_click'];

  function consented() {
    try { return localStorage.getItem('ok_cookie_consent') === '1'; } catch (e) { return false; }
  }

  // Цель — обезличенно всегда (только имя цели и страница, в суммы дня —
  // own_stats_snippet), в Метрику — только после согласия на cookie.
  function track(name) {
    if (GOALS.indexOf(name) === -1) return;
    if (typeof window.okStats === 'function') window.okStats({ e: name, p: location.pathname });
    if (!consented()) return;
    try { if (YM_ID && typeof window.ym === 'function') window.ym(YM_ID, 'reachGoal', name); } catch (e) {}
  }
  window.okTrack = track;

  function classify(href) {
    if (/^mailto:/i.test(href)) return 'email_click';
    if (/t\.me\/orgculture_bot/i.test(href)) return 'telegram_bot_click';
    if (/t\.me\/orgculture(?:[\/?#]|$)/i.test(href)) return 'telegram_channel_click';
    if (/vk\.(?:ru|com)\/orgculture/i.test(href)) return 'vk_click';
    if (/orgculture-(?:uslugi-i-ceny|services-and-prices)\.pdf/i.test(href)) return 'offer_download';
    if (/CV-[^\/]*\.pdf/i.test(href)) return 'cv_download';
    if (/documents\/press\//i.test(href)) return 'press_kit_download';
    if (/feed\.xml/i.test(href)) return 'rss_click';
    return null;
  }

  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var goal = classify(a.getAttribute('href') || '');
    if (goal) track(goal);
  }, true);
})();
