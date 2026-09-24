// Цели на ключевые действия. Сгенерировано gen.py (build_analytics_events_js) —
// не редактировать руками. Список целей: ANALYTICS_GOALS в gen.py.
(function () {
  var YM_ID = 111176053;
  var ENDPOINT = 'https://orgculture-bot.ЗАМЕНИ-НА-СВОЙ-АККАУНТ.workers.dev/track';
  var GOALS = ['brief_submit', 'offer_download', 'cv_download', 'press_kit_download', 'telegram_channel_click', 'telegram_bot_click', 'vk_click', 'email_click', 'review_submit', 'rss_click'];

  function consented() {
    try { return localStorage.getItem('ok_cookie_consent') === '1'; } catch (e) { return false; }
  }

  function track(name) {
    if (GOALS.indexOf(name) === -1 || !consented()) return;
    try { if (YM_ID && typeof window.ym === 'function') window.ym(YM_ID, 'reachGoal', name); } catch (e) {}
    try {
      var p = location.pathname;
      var payload = JSON.stringify({ event: name, path: p, lang: (p.indexOf('/en/') === 0 || p === '/en') ? 'en' : 'ru' });
      navigator.sendBeacon(ENDPOINT, new Blob([payload], { type: 'text/plain' }));
    } catch (e) {}
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
