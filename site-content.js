// Подмена нескольких заголовков живым текстом из редактора
// (04-bot/worker.js, маршруты /admin). Сгенерировано gen.py —
// не редактировать руками, см. own_stats_snippet()/build_site_content_js()
// в gen.py, если нужно поменять логику.
(function () {
  var CONTENT_ENDPOINT = 'https://orgculture-bot.ЗАМЕНИ-НА-СВОЙ-АККАУНТ.workers.dev/content';

  fetch(CONTENT_ENDPOINT)
    .then(function (r) { return r.json(); })
    .then(function (content) {
      document.querySelectorAll('[data-editable]').forEach(function (el) {
        var key = el.getAttribute('data-editable');
        var value = content[key];
        if (typeof value === 'string') {
          el.textContent = value;
        }
      });
    })
    .catch(function () {
      // Редактор недоступен — молча остаёмся на статическом тексте.
    });
})();
