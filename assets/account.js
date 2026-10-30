/*
 * Организованная Культурность — кабинет, сохранённое, оплата (с v69 сайта).
 *
 * Статический файл, пишется руками (как style.css). Конфиг — в странице:
 * window.OK_ACCOUNT = { api, lang, root } — его кладёт page_head() из
 * gen.py; адрес функции правится там (ACCOUNT_API), а не здесь.
 *
 * Что делает:
 *  • на любой странице — кнопки «☆ Сохранить» и значок кабинета в шапке;
 *  • /account/ — вход, регистрация с кодом, вход по коду, «забыли пароль»;
 *  • /account/dashboard/ — сохранённое, заказы, профиль, данные;
 *  • /account/reset/ — новый пароль по ссылке;
 *  • /pay/ — оплата услуги из КП;  /pay/order/ — заказ по ссылке.
 *
 * Хранилище браузера (Соглашение об использовании cookie, п. 2):
 *   localStorage ok_token   — вход в кабинет (без него кабинет не работает);
 *   localStorage ok_favs    — какие материалы сохранены, чтобы звёздочки
 *                             горели сразу, а не после ответа сервера;
 *   localStorage ok_pending — «код отправлен на …» на 10 минут (AELITA
 *                             pack-v639: на телефоне вкладка выгружается,
 *                             пока человек смотрит код в почте, и форма
 *                             сбрасывалась — «замкнутый круг»); пароль и
 *                             сам код не сохраняются никогда;
 *   sessionStorage ok_fav_queue — что человек отметил до входа.
 * Всё это — для работы функции, о которой человек попросил сам, поэтому
 * не ждёт согласия на cookie. «Выйти» стирает всё.
 *
 * Данные на странице — только через textContent: ни одна строка с
 * сервера не попадает в innerHTML.
 */
(function () {
  'use strict';
  var CFG = window.OK_ACCOUNT || {};
  var API = CFG.api || '';
  var LANG = CFG.lang === 'en' ? 'en' : 'ru';
  var ROOT = CFG.root || '/';
  var PRE = LANG === 'en' ? 'en/' : '';
  var page = (document.querySelector('[data-ok-page]') || {}).getAttribute ? document.querySelector('[data-ok-page]').getAttribute('data-ok-page') : '';

  // ── тексты ──────────────────────────────────────────────────────
  var S = {
    ru: {
      offline: 'Кабинет и оплата на сайте скоро заработают. Пока напишите на почту или в Telegram — ссылки в подвале.',
      sending: 'Отправляю…', saving: 'Сохраняю…', loading: 'Загружаю…', saved: 'Сохранено.',
      code_sent: 'Код отправлен на {email}. Он действует 10 минут.',
      code_restored: 'Код уже отправлен на {email} — введите его из последнего письма.',
      resent: 'Новый код отправлен.',
      fg_sent: 'Если на этот адрес есть кабинет, ссылка уже в почте. Проверьте и «Спам».',
      fill_email: 'Укажите почту.', fill_password: 'Введите пароль.', fill_name: 'Как к вам обращаться?',
      consent: 'Отметьте согласие на обработку данных.', consent_offer: 'Отметьте согласие с условиями оферты.',
      pw_mismatch: 'Пароли не совпадают.', hello: 'Здравствуйте, {name}',
      all: 'Всё', project: 'проект', remove: 'Убрать', save: 'Сохранить', saved_btn: 'Сохранено',
      pay: 'Оплатить', open: 'Открыть', receipt: 'Чек', order_no: 'Заказ {id}',
      st_awaiting_payment: 'ждёт оплаты', st_paid: 'оплачен', st_canceled: 'отменён', st_refunded: 'возврат',
      created: 'создан {d}', paid_at: 'оплачен {d}', receipt_wait: 'чек из «Мой налог» — скоро пришлём на почту',
      refund_line: 'возвращено {sum} · {d}',
      payer_person: 'Физическое лицо', payer_business: '{company}, ИНН {inn}',
      checkout_for: '«{title}» — {price}', checkout_login: 'Чтобы оплатить, войдите или зарегистрируйтесь — заказ и чек будут в кабинете.',
      login_link: 'Войти или зарегистрироваться →', paying_as: 'Оплачивает: {email}',
      redirect: 'Перехожу на страницу оплаты ЮKassa…',
      order_amount: 'Сумма', order_status: 'Статус', order_payer: 'Плательщик', order_note: 'Комментарий',
      order_paid_title: 'Оплата получена. Спасибо!', order_paid_text: 'Письмо-подтверждение уже в почте. Чек из «Мой налог» придёт отдельным письмом, свяжусь в течение двух рабочих дней.',
      order_waiting: 'Проверяю оплату…', order_pending_long: 'ЮKassa ещё не подтвердила оплату. Если вы оплатили — подождите пару минут и обновите страницу; если нет — оплатите ниже.',
      order_canceled: 'Счёт отменён. Если это ошибка — напишите мне.',
      order_refunded: 'По заказу оформлен возврат.',
      order_test: 'Тестовый платёж — деньги не списывались.',
      exported: 'Файл с данными скачан.', logged_out_all: 'Готово: вход сброшен на всех устройствах.',
      deleted: 'Кабинет удалён.', pw_changed: 'Пароль изменён.',
      confirm_delete: 'Удалить кабинет навсегда? Это нельзя отменить.',
      net: 'Нет связи с сервером. Проверьте интернет и попробуйте ещё раз.',
      outage: 'Кабинет и оплата на сайте временно не работают — сбой у хостинг-провайдера. Сохранённое и заказы не потеряны.',
      outage_more: 'Если срочно — почта и Telegram на странице', outage_link: '«Контакты»', outage_here: 'Если срочно — почта и Telegram ниже на этой странице.',
      outage_close: 'Скрыть сообщение'
    },
    en: {
      offline: 'Accounts and payments on the site are coming soon. For now, write by email or Telegram — links are in the footer.',
      sending: 'Sending…', saving: 'Saving…', loading: 'Loading…', saved: 'Saved.',
      code_sent: 'We sent a code to {email}. It is valid for 10 minutes.',
      code_restored: 'A code has already been sent to {email} — enter the one from the latest email.',
      resent: 'A new code has been sent.',
      fg_sent: 'If there is an account for this address, the link is already in your inbox. Check spam too.',
      fill_email: 'Enter your email.', fill_password: 'Enter your password.', fill_name: 'How should we call you?',
      consent: 'Please tick the data processing consent.', consent_offer: 'Please accept the offer terms.',
      pw_mismatch: 'The passwords do not match.', hello: 'Hello, {name}',
      all: 'All', project: 'project', remove: 'Remove', save: 'Save', saved_btn: 'Saved',
      pay: 'Pay', open: 'Open', receipt: 'Receipt', order_no: 'Order {id}',
      st_awaiting_payment: 'awaiting payment', st_paid: 'paid', st_canceled: 'cancelled', st_refunded: 'refunded',
      created: 'created {d}', paid_at: 'paid {d}', receipt_wait: 'the “My Tax” receipt will be emailed soon',
      refund_line: 'refunded {sum} · {d}',
      payer_person: 'Individual', payer_business: '{company}, INN {inn}',
      checkout_for: '“{title}” — {price}', checkout_login: 'To pay, sign in or create an account — the order and receipt will be kept there.',
      login_link: 'Sign in or sign up →', paying_as: 'Paying as: {email}',
      redirect: 'Opening the YooKassa payment page…',
      order_amount: 'Amount', order_status: 'Status', order_payer: 'Payer', order_note: 'Comment',
      order_paid_title: 'Payment received. Thank you!', order_paid_text: 'The confirmation is in your inbox. The “My Tax” receipt will follow in a separate email; I will be in touch within two business days.',
      order_waiting: 'Checking the payment…', order_pending_long: 'YooKassa has not confirmed the payment yet. If you have paid, wait a couple of minutes and reload; if not, pay below.',
      order_canceled: 'This invoice has been cancelled. If that is a mistake, write to me.',
      order_refunded: 'A refund has been issued for this order.',
      order_test: 'Test payment — no money was charged.',
      exported: 'Your data file has been downloaded.', logged_out_all: 'Done: you have been signed out on all devices.',
      deleted: 'Your account has been deleted.', pw_changed: 'Password changed.',
      confirm_delete: 'Delete the account permanently? This cannot be undone.',
      net: 'No connection to the server. Check your internet and try again.',
      outage: 'Accounts and payments on the site are temporarily down — our hosting provider has an outage. Saved items and orders are not lost.',
      outage_more: 'If it is urgent, email and Telegram are on the', outage_link: 'Contacts page', outage_here: 'If it is urgent, email and Telegram are further down this page.',
      outage_close: 'Hide this message'
    }
  }[LANG];

  // Коды ошибок функции → понятный текст (AELITA pack-v706: у каждого
  // кода — текст на странице, «Ошибка» без объяснения не показывается).
  var ERR = {
    ru: {
      email_invalid: 'Проверьте адрес почты.', name_required: 'Как к вам обращаться?',
      consent_required: 'Отметьте согласие на обработку данных.', consent_offer_required: 'Отметьте согласие с условиями оферты.',
      password_too_short: 'Пароль — не меньше 8 знаков.', password_too_long: 'Слишком длинный пароль.', password_only_digits: 'Пароль не может состоять только из цифр.',
      email_taken: 'На эту почту уже есть кабинет — войдите или восстановите пароль.',
      code_wrong: 'Код не подошёл. Проверьте последнее письмо.', code_expired: 'Код устарел — пришлём новый.',
      registration_expired: 'Регистрация устарела — заполните форму ещё раз.',
      login_failed: 'Неверная почта или пароль.', password_wrong: 'Текущий пароль не подошёл.',
      too_many_requests: 'Слишком много попыток. Подождите немного и попробуйте снова.',
      mail_failed: 'Не получилось отправить письмо. Попробуйте через пару минут.',
      reset_link_invalid: 'Ссылка устарела или уже использована — запросите новую.',
      auth_required: 'Нужно войти в кабинет.', favorite_invalid: 'Этот материал нельзя сохранить.', favorites_full: 'Сохранено слишком много — уберите что-нибудь.',
      service_unknown: 'Такой услуги нет — обновите страницу.', company_required: 'Укажите название ИП или организации.', inn_invalid: 'ИНН не прошёл проверку — 10 цифр у организации, 12 у ИП.',
      order_not_found: 'Заказ не найден. Проверьте ссылку из письма.', order_not_payable: 'Этот заказ уже оплачен или отменён.',
      payments_not_configured: 'Оплата на сайте ещё не подключена. Напишите — пришлю счёт.',
      yookassa_unreachable: 'ЮKassa сейчас не отвечает. Попробуйте через несколько минут.', yookassa_rejected: 'ЮKassa не приняла платёж. Попробуйте ещё раз или напишите мне.',
      storage_busy: 'Сервер занят — попробуйте ещё раз.', server_misconfigured: 'Кабинет временно недоступен. Напишите на почту — разберусь.',
      internal: 'Что-то пошло не так. Попробуйте ещё раз.', route_unknown: 'Сайт обновился — обновите страницу.', bad_json: 'Ошибка запроса — обновите страницу.',
      network: 'Нет связи с сервером. Проверьте интернет и попробуйте ещё раз.'
    },
    en: {
      email_invalid: 'Check the email address.', name_required: 'How should we call you?',
      consent_required: 'Please tick the data processing consent.', consent_offer_required: 'Please accept the offer terms.',
      password_too_short: 'At least 8 characters, please.', password_too_long: 'The password is too long.', password_only_digits: 'The password cannot be digits only.',
      email_taken: 'There is already an account for this email — sign in or reset the password.',
      code_wrong: 'The code did not match. Check the latest email.', code_expired: 'The code has expired — we will send a new one.',
      registration_expired: 'The sign-up has expired — please fill in the form again.',
      login_failed: 'Wrong email or password.', password_wrong: 'The current password did not match.',
      too_many_requests: 'Too many attempts. Wait a little and try again.',
      mail_failed: 'Could not send the email. Try again in a couple of minutes.',
      reset_link_invalid: 'The link has expired or was already used — request a new one.',
      auth_required: 'Please sign in.', favorite_invalid: 'This item cannot be saved.', favorites_full: 'Too many saved items — remove some.',
      service_unknown: 'Unknown service — please reload the page.', company_required: 'Enter the name of the sole trader or company.', inn_invalid: 'The INN did not pass the check — 10 digits for a company, 12 for a sole trader.',
      order_not_found: 'Order not found. Check the link in the email.', order_not_payable: 'This order is already paid or cancelled.',
      payments_not_configured: 'Online payment is not connected yet. Write to me and I will send an invoice.',
      yookassa_unreachable: 'YooKassa is not responding. Try again in a few minutes.', yookassa_rejected: 'YooKassa declined the payment. Try again or write to me.',
      storage_busy: 'The server is busy — try again.', server_misconfigured: 'The account is temporarily unavailable. Please email me.',
      internal: 'Something went wrong. Please try again.', route_unknown: 'The site has been updated — please reload.', bad_json: 'Request error — please reload.',
      network: 'No connection to the server. Check your internet and try again.'
    }
  }[LANG];

  function fmt(s, v) { return String(s).replace(/\{(\w+)\}/g, function (_, k) { return v && v[k] != null ? v[k] : ''; }); }
  function errText(code) { return ERR[code] || ERR.internal; }
  function $(id) { return document.getElementById(id); }
  function val(id) { var el = $(id); return el ? String(el.value || '').trim() : ''; }
  function rub(n) {
    var s = Math.round(Number(n)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    return LANG === 'en' ? '₽' + s.replace(/ /g, ',') : s + ' ₽';
  }
  function dateStr(iso) {
    if (!iso) return '';
    try { return new Date(iso).toLocaleDateString(LANG === 'en' ? 'en-GB' : 'ru-RU', { day: 'numeric', month: 'long', year: 'numeric' }); } catch (e) { return iso.slice(0, 10); }
  }
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'text') n.textContent = attrs[k];
      else if (k === 'cls') n.className = attrs[k];
      else if (attrs[k] !== null && attrs[k] !== undefined && attrs[k] !== false) n.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function status(id, text, kind) {
    var s = $(id); if (!s) return;
    s.textContent = text || '';
    s.classList.remove('is-error', 'is-ok');
    if (kind) s.classList.add(kind === 'error' ? 'is-error' : 'is-ok');
  }
  function url(path) { return ROOT + PRE + path; }

  // ── хранилище браузера ──────────────────────────────────────────
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function lsDel(k) { try { localStorage.removeItem(k); } catch (e) {} }
  function ssGet(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function ssSet(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} }
  function ssDel(k) { try { sessionStorage.removeItem(k); } catch (e) {} }
  function token() { return lsGet('ok_token') || ''; }
  function favCache() { try { return JSON.parse(lsGet('ok_favs') || '[]'); } catch (e) { return []; } }
  function setFavCache(list) { lsSet('ok_favs', JSON.stringify((list || []).map(function (f) { return f.t + ':' + f.s; }))); }
  function signOutLocal() { lsDel('ok_token'); lsDel('ok_favs'); lsDel('ok_pending'); ssDel('ok_fav_queue'); }

  // ── запрос к функции ────────────────────────────────────────────
  function api(route, opts) {
    opts = opts || {};
    var q = '?r=' + encodeURIComponent(route);
    if (opts.query) Object.keys(opts.query).forEach(function (k) { q += '&' + encodeURIComponent(k) + '=' + encodeURIComponent(opts.query[k]); });
    var headers = {};
    if (opts.body) headers['Content-Type'] = 'application/json';
    if (opts.auth !== false && token()) headers.Authorization = 'Bearer ' + token();
    return fetch(API + q, { method: opts.body ? 'POST' : 'GET', headers: headers, body: opts.body ? JSON.stringify(opts.body) : undefined })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (data) {
          // 5xx без нашего кода ошибки — отвечает не функция, а площадка
          // (шлюз, балансировщик): это сбой, а не ошибка в запросе.
          if (r.status >= 500 && !ERR[data.error]) noteApi(true);
          if (!r.ok) {
            var err = new Error(data.error || 'internal');
            err.code = data.error || 'internal'; err.status = r.status;
            if (r.status === 401 && err.code === 'auth_required') signOutLocal();
            throw err;
          }
          return data;
        });
      }, function () { noteApi(true); var e = new Error('network'); e.code = 'network'; throw e; });
  }

  // ── сообщение «временно не работает» ────────────────────────────
  // По образцу AELITA pack-v650 (сбой Yandex Cloud 8.10.2026): если
  // функция не отвечает 6 секунд, отвечает 5xx площадки или недоступна —
  // на страницах, которым она нужна (кабинет, оплата, заказ, бриф),
  // появляется сообщение со ссылкой на почту и Telegram. Само исчезает,
  // когда сервер ожил или мы переехали: выкладывать ничего не надо.
  // Состояние — только в памяти страницы, не в хранилище браузера:
  // Соглашение о cookie перечисляет ключи поимённо, и новых в нём нет.
  // Без JS сообщения нет — но без JS нет и кабинета.
  var outageShown = false, outageHidden = false;
  function needsApi() { return !!page || !!$('brief-form'); }
  function showOutage() {
    if (outageShown || outageHidden || !needsApi()) return;
    outageShown = true;
    var here = !!$('brief-form');
    var p = el('p', null, [S.outage + ' ']);
    if (here) p.appendChild(document.createTextNode(S.outage_here));
    else { p.appendChild(document.createTextNode(S.outage_more + ' ')); p.appendChild(el('a', { href: url('contacts/'), text: S.outage_link })); p.appendChild(document.createTextNode('.')); }
    var x = el('button', { type: 'button', cls: 'ok-outage-x', 'aria-label': S.outage_close, text: '×' });
    var box = el('div', { id: 'ok-outage', cls: 'ok-outage', role: 'status' }, [p, x]);
    x.addEventListener('click', function () { box.parentNode.removeChild(box); outageHidden = true; });
    // Сообщение встаёт наверх страницы. Если человек уже ушёл ниже (пришёл
    // по ссылке на раздел, например /contacts/#brief), страница не должна
    // прыгнуть: прокрутка сдвигается на высоту вставленного блока.
    var y = window.pageYOffset || 0;
    var anchor = $('main');
    if (anchor && anchor.parentNode) anchor.parentNode.insertBefore(box, anchor.nextSibling);
    else document.body.insertBefore(box, document.body.firstChild);
    var target = location.hash.length > 1 ? document.getElementById(location.hash.slice(1)) : null;
    if (target && target.scrollIntoView) {
      try { target.scrollIntoView({ block: 'start', behavior: 'instant' }); } catch (e) { target.scrollIntoView(true); }
    } else if (y > 0) {
      var cs = window.getComputedStyle(box);
      var dh = box.offsetHeight + (parseFloat(cs.marginTop) || 0) + (parseFloat(cs.marginBottom) || 0);
      try { window.scrollTo({ top: y + dh, behavior: 'instant' }); } catch (e) { window.scrollTo(0, y + dh); }
    }
  }
  function noteApi(down) { if (down) showOutage(); }
  function checkOutage() {
    if (!API || !needsApi()) return;
    var done = false;
    var finish = function (down) { if (done) return; done = true; noteApi(down); };
    setTimeout(function () { finish(true); }, 6000);
    fetch(API + '?r=health', { cache: 'no-store' }).then(function (r) { finish(r.status >= 500); }, function () { finish(true); });
  }

  // ── шапка: значок кабинета ──────────────────────────────────────
  function markHeader() {
    if (!token()) return;
    document.querySelectorAll('.acct-link, .acct-mobile').forEach(function (a) {
      a.classList.add('is-in');
      a.setAttribute('href', url('account/dashboard/'));
    });
  }

  // ── кнопки «Сохранить» ─────────────────────────────────────────
  function paintFav(btn, on) {
    btn.setAttribute('aria-pressed', on ? 'true' : 'false');
    var star = btn.querySelector('.fav-star'); if (star) star.textContent = on ? '★' : '☆';
    var label = btn.querySelector('.fav-label'); if (label) label.textContent = on ? S.saved_btn : S.save;
  }
  function initFavButtons() {
    var btns = document.querySelectorAll('[data-fav]');
    if (!btns.length || !API) return;
    var cache = favCache();
    btns.forEach(function (btn) {
      btn.hidden = false;
      paintFav(btn, cache.indexOf(btn.getAttribute('data-fav')) !== -1);
      btn.addEventListener('click', function () {
        var key = btn.getAttribute('data-fav'); var parts = key.split(':');
        if (!token()) {
          // Не вошёл: запомнить, что хотел сохранить, и отправить на вход.
          var q = []; try { q = JSON.parse(ssGet('ok_fav_queue') || '[]'); } catch (e) {}
          if (q.indexOf(key) === -1) q.push(key);
          ssSet('ok_fav_queue', JSON.stringify(q.slice(-20)));
          location.href = url('account/') + '?next=' + encodeURIComponent(location.pathname + location.hash);
          return;
        }
        var on = btn.getAttribute('aria-pressed') !== 'true';
        btn.disabled = true;
        api('account.fav', { body: { action: on ? 'add' : 'remove', t: parts[0], s: parts[1] } }).then(function (d) {
          setFavCache(d.favorites);
          document.querySelectorAll('[data-fav="' + key + '"]').forEach(function (b) { paintFav(b, on); });
        }).catch(function (e) {
          if (e.code === 'auth_required') { btn.click(); return; }
          btn.title = errText(e.code);
        }).then(function () { btn.disabled = false; });
      });
    });
  }
  function flushFavQueue() {
    var q = []; try { q = JSON.parse(ssGet('ok_fav_queue') || '[]'); } catch (e) {}
    if (!q.length || !token()) return Promise.resolve();
    ssDel('ok_fav_queue');
    var items = q.map(function (k) { var p = k.split(':'); return { t: p[0], s: p[1] }; });
    return api('account.fav-merge', { body: { items: items } }).then(function (d) { setFavCache(d.favorites); }).catch(function () {});
  }

  // ── /account/ ──────────────────────────────────────────────────
  function initAuth() {
    var box = $('ok-auth');
    if (!API) { var off = $('ok-offline'); if (off) { off.textContent = S.offline; off.hidden = false; } return; }
    var params = new URLSearchParams(location.search);
    var next = params.get('next') || '';
    if (!/^\/[^\/]/.test(next) && next !== '/') next = '';
    if (token()) { finishLogin(); return; }
    box.hidden = false;
    var panes = ['login', 'register', 'codelogin', 'forgot', 'code'];
    function show(name) {
      panes.forEach(function (p) { var e = $('pane-' + p); if (e) e.hidden = p !== name; });
      ['login', 'register'].forEach(function (p) { $('tab-' + p).setAttribute('aria-selected', p === name ? 'true' : 'false'); });
      var first = $('pane-' + name) && $('pane-' + name).querySelector('input');
      if (first && document.activeElement && document.activeElement.tagName !== 'BODY') first.focus();
    }
    $('tab-login').addEventListener('click', function () { show('login'); });
    $('tab-register').addEventListener('click', function () { show('register'); });
    document.querySelectorAll('[data-ok-go]').forEach(function (b) {
      b.addEventListener('click', function () {
        var target = b.getAttribute('data-ok-go');
        if (target === 'login') lsDel('ok_pending');
        var em = val('login-email');
        if (em && $('cl-email') && !val('cl-email')) $('cl-email').value = em;
        if (em && $('fg-email') && !val('fg-email')) $('fg-email').value = em;
        show(target);
      });
    });

    function finishLogin(data) {
      if (data && data.token) { lsSet('ok_token', data.token); if (data.user) setFavCache(data.user.favorites); }
      lsDel('ok_pending');
      flushFavQueue().then(function () { location.href = next || url('account/dashboard/'); });
    }

    // ожидание кода: {mode:'register'|'login', email, pending_id, exp}
    function pending() { try { var p = JSON.parse(lsGet('ok_pending') || 'null'); return p && p.exp > Date.now() ? p : null; } catch (e) { return null; } }
    function showCode(p, restored) {
      lsSet('ok_pending', JSON.stringify(p));
      $('code-sent-to').textContent = fmt(restored ? S.code_restored : S.code_sent, { email: p.email });
      $('code-input').value = '';
      show('code');
      status('code-status', '');
    }
    var p0 = pending(); if (p0) showCode(p0, true);

    $('pane-login').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var email = val('login-email'), pw = $('login-password').value;
      if (!email) return status('login-status', S.fill_email, 'error');
      if (!pw) return status('login-status', S.fill_password, 'error');
      status('login-status', S.sending);
      api('account.login', { body: { email: email, password: pw }, auth: false }).then(finishLogin)
        .catch(function (e) { status('login-status', errText(e.code), 'error'); });
    });

    $('pane-register').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var name = val('reg-name'), email = val('reg-email'), pw = $('reg-password').value;
      if (!name) return status('reg-status', S.fill_name, 'error');
      if (!email) return status('reg-status', S.fill_email, 'error');
      if (!$('reg-consent').checked) return status('reg-status', S.consent, 'error');
      status('reg-status', S.sending);
      api('account.register', { body: { name: name, email: email, password: pw, consent: true, lang: LANG }, auth: false }).then(function (d) {
        showCode({ mode: 'register', email: d.email || email, pending_id: d.pending_id, exp: Date.now() + 10 * 60 * 1000 });
      }).catch(function (e) {
        status('reg-status', errText(e.code), 'error');
        if (e.code === 'email_taken') { $('login-email').value = email; }
      });
    });

    $('pane-codelogin').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var email = val('cl-email');
      if (!email) return status('cl-status', S.fill_email, 'error');
      status('cl-status', S.sending);
      api('account.code-request', { body: { email: email, lang: LANG }, auth: false }).then(function () {
        showCode({ mode: 'login', email: email, exp: Date.now() + 10 * 60 * 1000 });
      }).catch(function (e) { status('cl-status', errText(e.code), 'error'); });
    });

    $('pane-forgot').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var email = val('fg-email');
      if (!email) return status('fg-status', S.fill_email, 'error');
      status('fg-status', S.sending);
      api('account.reset-request', { body: { email: email, lang: LANG }, auth: false })
        .then(function () { status('fg-status', S.fg_sent, 'ok'); })
        .catch(function (e) { status('fg-status', errText(e.code), 'error'); });
    });

    function submitCode() {
      var p = pending(); if (!p) { show('login'); return; }
      var code = val('code-input').replace(/\D/g, '');
      if (code.length !== 6) return;
      status('code-status', S.sending);
      var req = p.mode === 'register'
        ? api('account.register-confirm', { body: { pending_id: p.pending_id, code: code }, auth: false })
        : api('account.code-login', { body: { email: p.email, code: code }, auth: false });
      req.then(finishLogin).catch(function (e) {
        status('code-status', errText(e.code), 'error');
        if (e.code === 'registration_expired') { lsDel('ok_pending'); show('register'); status('reg-status', errText(e.code), 'error'); }
      });
    }
    $('pane-code').addEventListener('submit', function (ev) { ev.preventDefault(); submitCode(); });
    // Шестая цифра отправляет сама (AELITA pack-v639).
    $('code-input').addEventListener('input', function () { if (val('code-input').replace(/\D/g, '').length === 6) submitCode(); });
    $('code-resend').addEventListener('click', function () {
      var p = pending(); if (!p) { show('login'); return; }
      status('code-status', S.sending);
      // Регистрация: новый код к той же заявке (пароль в браузере не хранится,
      // и вводить его заново не нужно — он уже на сервере в заявке).
      var req = p.mode === 'register'
        ? api('account.register-resend', { body: { pending_id: p.pending_id }, auth: false })
        : api('account.code-request', { body: { email: p.email, lang: LANG }, auth: false });
      req.then(function () {
        p.exp = Date.now() + 10 * 60 * 1000; lsSet('ok_pending', JSON.stringify(p)); status('code-status', S.resent, 'ok');
      }).catch(function (e) {
        status('code-status', errText(e.code), 'error');
        if (e.code === 'registration_expired') { lsDel('ok_pending'); show('register'); status('reg-status', errText(e.code), 'error'); }
      });
    });
  }

  // ── /account/dashboard/ ─────────────────────────────────────────
  var catalogPromise = null;
  function catalog() {
    if (!catalogPromise) catalogPromise = fetch(ROOT + 'assets/catalog.json').then(function (r) { return r.json(); }).catch(function () { return { items: [] }; });
    return catalogPromise;
  }

  function orderRow(o, opts) {
    var badgeCls = o.status === 'paid' ? 'paid' : o.status === 'awaiting_payment' ? 'awaiting' : o.status === 'refunded' ? 'warn' : '';
    var lines = [fmt(S.created, { d: dateStr(o.createdAt) })];
    if (o.paidAt) lines.push(fmt(S.paid_at, { d: dateStr(o.paidAt) }));
    if (o.status === 'paid' && !o.receiptUrl && !o.test) lines.push(S.receipt_wait);
    if (o.refund) lines.push(fmt(S.refund_line, { sum: rub(o.refund.amount), d: dateStr(o.refund.at) }));
    if (o.test) lines.push(S.order_test);
    var actions = el('div', { cls: 'ok-actions' });
    if (o.status === 'awaiting_payment') actions.appendChild(el('a', { cls: 'btn-line btn-line-ghost', href: url('pay/order/') + '?id=' + encodeURIComponent(o.id), text: S.pay + ' ' + rub(o.amount) }));
    if (o.receiptUrl) actions.appendChild(el('a', { cls: 'btn-line', href: o.receiptUrl, target: '_blank', rel: 'noopener', text: S.receipt }));
    if (o.status !== 'awaiting_payment') actions.appendChild(el('a', { cls: 'btn-line', href: url('pay/order/') + '?id=' + encodeURIComponent(o.id), text: S.open }));
    return el('article', { cls: 'ok-order-row' }, [
      el('div', { cls: 'row1' }, [el('h3', { text: o.title }), el('span', { cls: 'ok-badge ' + badgeCls, text: S['st_' + o.status] || o.status })]),
      el('div', { cls: 'meta', text: fmt(S.order_no, { id: o.id }) + ' · ' + rub(o.amount) + ' · ' + lines.join(' · ') }),
      actions.childNodes.length ? actions : null
    ]);
  }

  // Заглушка картинки (у проектов своих картинок нет) — овал из фирстиля,
  // как разделитель на сайте. Через createElementNS, не innerHTML.
  function noImg() {
    var NS = 'http://www.w3.org/2000/svg';
    var svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('viewBox', '0 0 200 110'); svg.setAttribute('aria-hidden', 'true');
    svg.setAttribute('fill', 'none'); svg.setAttribute('stroke', 'currentColor'); svg.setAttribute('stroke-width', '8');
    var e = document.createElementNS(NS, 'ellipse');
    e.setAttribute('cx', '100'); e.setAttribute('cy', '55'); e.setAttribute('rx', '90'); e.setAttribute('ry', '45');
    svg.appendChild(e);
    return el('div', { cls: 'thumb noimg' }, [svg]);
  }

  function initDashboard() {
    if (!API) { status('dash-status', S.offline); return; }
    if (!token()) { location.replace(url('account/') + '?next=' + encodeURIComponent(location.pathname)); return; }
    status('dash-status', S.loading);
    var state = { user: null, orders: [], filter: '' };

    function renderSaved() {
      catalog().then(function (cat) {
        var byKey = {}; (cat.items || []).forEach(function (it) { byKey[it.t + ':' + it.s] = it; });
        var favs = (state.user.favorites || []).map(function (f) { return byKey[f.t + ':' + f.s]; }).filter(Boolean);
        var tags = [];
        favs.forEach(function (it) { var tg = it[LANG].tag; if (tags.indexOf(tg) === -1) tags.push(tg); });
        var fr = $('saved-filters'); fr.textContent = '';
        if (tags.length > 1) {
          [''].concat(tags).forEach(function (tg) {
            var b = el('button', { type: 'button', cls: 'filter-pill' + (state.filter === tg ? ' active' : ''), 'aria-pressed': state.filter === tg ? 'true' : 'false', text: tg || S.all });
            b.addEventListener('click', function () { state.filter = tg; renderSaved(); });
            fr.appendChild(b);
          });
        } else state.filter = '';
        var list = $('saved-list'); list.textContent = '';
        favs.filter(function (it) { return !state.filter || it[LANG].tag === state.filter; }).forEach(function (it) {
          var href = url((it.t === 'project' ? 'projects/' : 'texts/') + it.s + '/');
          var thumb = it.img
            ? el('div', { cls: 'thumb' }, [el('img', { src: ROOT + 'images/' + it.img, alt: '', loading: 'lazy' })])
            : noImg();
          var btn = el('button', { type: 'button', cls: 'fav-btn fav-compact', 'aria-pressed': 'true', 'aria-label': S.remove + ': ' + it[LANG].title }, [el('span', { cls: 'fav-star', 'aria-hidden': 'true', text: '★' }), el('span', { cls: 'fav-label', text: S.remove })]);
          btn.addEventListener('click', function () {
            btn.disabled = true;
            api('account.fav', { body: { action: 'remove', t: it.t, s: it.s } }).then(function (d) {
              state.user.favorites = d.favorites; setFavCache(d.favorites); renderSaved();
            }).catch(function (e) { btn.disabled = false; status('dash-status', errText(e.code), 'error'); });
          });
          list.appendChild(el('div', { cls: 'ok-saved-item' }, [
            el('a', { cls: 'ok-saved-link', href: href }, [thumb, el('div', { cls: 'body' }, [el('span', { cls: 'tag', text: it[LANG].tag }), el('h3', { text: it[LANG].title })])]),
            btn
          ]));
        });
        $('saved-empty').hidden = favs.length > 0;
      });
    }
    function renderOrders() {
      var box = $('orders-list'); box.textContent = '';
      state.orders.forEach(function (o) { box.appendChild(orderRow(o)); });
      $('orders-empty').hidden = state.orders.length > 0;
    }
    function render() {
      $('dash-hello').textContent = state.user.name ? fmt(S.hello, { name: state.user.name }) : $('dash-hello').textContent;
      $('profile-email').textContent = state.user.email;
      $('pf-name').value = state.user.name || '';
      renderSaved(); renderOrders();
    }

    flushFavQueue().then(function () { return api('account.me'); }).then(function (d) {
      state.user = d.user; state.orders = d.orders || []; setFavCache(d.user.favorites);
      status('dash-status', ''); render();
    }).catch(function (e) {
      if (e.code === 'auth_required') { location.replace(url('account/') + '?next=' + encodeURIComponent(location.pathname)); return; }
      status('dash-status', errText(e.code), 'error');
    });

    $('profile-form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var name = val('pf-name'); if (!name) return status('pf-status', S.fill_name, 'error');
      status('pf-status', S.saving);
      api('account.profile', { body: { name: name, lang: LANG } }).then(function (d) { state.user.name = d.user.name; render(); status('pf-status', S.saved, 'ok'); })
        .catch(function (e) { status('pf-status', errText(e.code), 'error'); });
    });
    $('password-form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      status('pw-status', S.saving);
      api('account.password', { body: { current: $('pw-current').value, password: $('pw-new').value } }).then(function (d) {
        lsSet('ok_token', d.token); $('pw-current').value = ''; $('pw-new').value = ''; status('pw-status', S.pw_changed, 'ok');
      }).catch(function (e) { status('pw-status', errText(e.code), 'error'); });
    });
    $('export-btn').addEventListener('click', function () {
      status('data-status', S.loading);
      api('account.export').then(function (d) {
        var blob = new Blob([JSON.stringify(d, null, 2)], { type: 'application/json' });
        var a = el('a', { href: URL.createObjectURL(blob), download: 'orgculture-my-data-' + new Date().toISOString().slice(0, 10) + '.json' });
        document.body.appendChild(a); a.click(); a.remove();
        status('data-status', S.exported, 'ok');
      }).catch(function (e) { status('data-status', errText(e.code), 'error'); });
    });
    $('logout-btn').addEventListener('click', function () { signOutLocal(); location.href = url('account/'); });
    $('logout-all-btn').addEventListener('click', function () {
      api('account.logout-all', { body: {} }).then(function () { signOutLocal(); status('data-status', S.logged_out_all, 'ok'); setTimeout(function () { location.href = url('account/'); }, 1200); })
        .catch(function (e) { status('data-status', errText(e.code), 'error'); });
    });
    // Подтверждение удаления — паролем в форме, без confirm()/prompt():
    // системные окна блокируют страницу и плохо читаются диктором
    // (AELITA pack-v694 убрала их из кабинета по той же причине).
    $('delete-form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var pw = $('del-password').value; if (!pw) return status('del-status', S.fill_password, 'error');
      var btn = ev.target.querySelector('button[type=submit]');
      if (btn.getAttribute('data-armed') !== '1') { btn.setAttribute('data-armed', '1'); status('del-status', S.confirm_delete, 'error'); return; }
      status('del-status', S.sending);
      api('account.delete', { body: { password: pw } }).then(function () { signOutLocal(); status('del-status', S.deleted, 'ok'); setTimeout(function () { location.href = url(''); }, 1500); })
        .catch(function (e) { btn.removeAttribute('data-armed'); status('del-status', errText(e.code), 'error'); });
    });
  }

  // ── /account/reset/ ─────────────────────────────────────────────
  function initReset() {
    var t = (location.hash.match(/t=([A-Za-z0-9_-]+)/) || [])[1] || '';
    if (!API) { status('rs-status', S.offline); return; }
    if (!t) { status('rs-status', errText('reset_link_invalid'), 'error'); return; }
    $('reset-form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var a = $('rs-password').value, b = $('rs-password2').value;
      if (a !== b) return status('rs-status', S.pw_mismatch, 'error');
      status('rs-status', S.saving);
      api('account.reset', { body: { t: t, password: a }, auth: false }).then(function (d) {
        lsSet('ok_token', d.token); setFavCache(d.user.favorites);
        history.replaceState(null, '', location.pathname);
        location.href = url('account/dashboard/');
      }).catch(function (e) { status('rs-status', errText(e.code), 'error'); });
    });
  }

  // ── плательщик и согласия (общие для /pay/ и /pay/order/) ───────
  function initPayer(prefix) {
    var radios = document.querySelectorAll('input[name="' + prefix + '-payer-type"]');
    function sync() { var b = document.querySelector('input[name="' + prefix + '-payer-type"]:checked'); $(prefix + '-business').hidden = !(b && b.value === 'business'); }
    radios.forEach(function (r) { r.addEventListener('change', sync); });
    sync();
    return {
      get: function () {
        var b = document.querySelector('input[name="' + prefix + '-payer-type"]:checked');
        if (!b || b.value !== 'business') return { type: 'person' };
        return { type: 'business', company: val(prefix + '-company'), inn: val(prefix + '-inn').replace(/\D/g, '') };
      },
      set: function (p) {
        if (!p) return;
        radios.forEach(function (r) { r.checked = r.value === (p.type === 'business' ? 'business' : 'person'); });
        if (p.company) $(prefix + '-company').value = p.company;
        if (p.inn) $(prefix + '-inn').value = p.inn;
        sync();
      }
    };
  }
  function consentsOk(prefix, statusId) {
    if (!$(prefix + '-offer').checked) { status(statusId, S.consent_offer, 'error'); return false; }
    if (!$(prefix + '-pd').checked) { status(statusId, S.consent, 'error'); return false; }
    return true;
  }

  // ── /pay/ ──────────────────────────────────────────────────────
  function initPay() {
    if (!API) { var off = $('ok-offline'); if (off) { off.textContent = S.offline; off.hidden = false; } return; }
    var form = $('checkout');
    var payer = initPayer('co');
    var chosen = null;
    document.querySelectorAll('[data-pay]').forEach(function (b) {
      b.hidden = false;
      b.addEventListener('click', function () { choose(b.getAttribute('data-pay'), true); });
    });
    function choose(id, focus) {
      var card = $('svc-' + id); if (!card) return;
      chosen = id;
      document.querySelectorAll('.ok-service').forEach(function (c) { c.classList.toggle('is-chosen', c === card); });
      $('checkout-h').textContent = fmt(S.checkout_for, { title: card.querySelector('.ok-service-h').textContent, price: card.querySelector('.ok-price').textContent });
      var who = $('checkout-who'); who.textContent = '';
      form.hidden = false;
      card.parentNode.insertBefore(form, card.nextSibling);
      if (!token()) {
        who.appendChild(document.createTextNode(S.checkout_login + ' '));
        who.appendChild(el('a', { href: url('account/') + '?next=' + encodeURIComponent(location.pathname + '?service=' + id), text: S.login_link }));
        $('co-submit').hidden = true;
      } else {
        $('co-submit').hidden = false;
        api('account.me').then(function (d) { who.textContent = fmt(S.paying_as, { email: d.user.email }); })
          .catch(function (e) { if (e.code === 'auth_required') choose(id, false); });
      }
      if (focus) $('checkout-h').scrollIntoView({ block: 'start', behavior: 'smooth' });
    }
    var pre = new URLSearchParams(location.search).get('service');
    if (pre) choose(pre, true);
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (!chosen || !consentsOk('co', 'co-status')) return;
      status('co-status', S.sending);
      $('co-submit').disabled = true;
      api('pay.checkout', { body: { serviceId: chosen, payer: payer.get(), consentOffer: true, consentPd: true, lang: LANG } }).then(function (d) {
        status('co-status', S.redirect, 'ok');
        location.href = d.confirmation_url;
      }).catch(function (e) {
        $('co-submit').disabled = false;
        if (e.code === 'auth_required') { choose(chosen, false); return; }
        status('co-status', errText(e.code), 'error');
      });
    });
  }

  // ── /pay/order/ ────────────────────────────────────────────────
  function initOrder() {
    var params = new URLSearchParams(location.search);
    var id = params.get('id') || '', k = params.get('k') || '';
    if (!API) { status('order-status', S.offline); return; }
    if (!id) { status('order-status', errText('order_not_found'), 'error'); return; }
    var payer = initPayer('op');
    var tries = 0;
    var query = { id: id }; if (k) query.k = k;

    function render(o, payment) {
      $('order-h').textContent = o.title;
      var card = $('order-card'); card.textContent = ''; card.hidden = false;
      var dl = el('dl', { cls: 'ok-kv' }, [
        el('dt', { text: fmt(S.order_no, { id: '' }).trim() }), el('dd', { text: o.id }),
        el('dt', { text: S.order_amount }), el('dd', { text: rub(o.amount) }),
        el('dt', { text: S.order_status }), el('dd', { text: S['st_' + o.status] || o.status }),
        el('dt', { text: S.order_payer }), el('dd', { text: o.payer && o.payer.type === 'business' ? fmt(S.payer_business, o.payer) : S.payer_person })
      ]);
      if (o.note) { dl.appendChild(el('dt', { text: S.order_note })); dl.appendChild(el('dd', { text: o.note })); }
      card.appendChild(dl);
      if (o.status === 'paid' || o.status === 'refunded') {
        card.appendChild(el('h2', { cls: 'ok-h2', style: 'margin-top:22px;', text: o.status === 'paid' ? S.order_paid_title : S.order_refunded }));
        if (o.status === 'paid') card.appendChild(el('p', { cls: 'ok-note', text: o.test ? S.order_test : S.order_paid_text }));
        if (o.receiptUrl) card.appendChild(el('p', {}, [el('a', { cls: 'btn-line', href: o.receiptUrl, target: '_blank', rel: 'noopener', text: S.receipt })]));
        $('order-pay').hidden = true;
        status('order-status', '');
        return;
      }
      if (o.status === 'canceled') { $('order-pay').hidden = true; status('order-status', S.order_canceled); return; }
      // ждёт оплаты
      payer.set(o.payer);
      $('order-pay').hidden = false;
      if (payment && payment.status === 'pending' && tries < 20) {
        status('order-status', S.order_waiting);
        tries++; setTimeout(load, 3000);
      } else if (payment && payment.status === 'pending') {
        status('order-status', S.order_pending_long);
      } else status('order-status', '');
    }
    function load() {
      api('pay.status', { query: query }).then(function (d) { if (d.order.key) k = d.order.key; render(d.order, d.payment); })
        .catch(function (e) { status('order-status', errText(e.code), 'error'); });
    }
    status('order-status', S.loading);
    load();

    $('order-pay').addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (!consentsOk('op', 'op-status')) return;
      status('op-status', S.sending);
      $('op-submit').disabled = true;
      api('pay.order-pay', { body: { id: id, k: k, payer: payer.get(), consentOffer: true, consentPd: true, lang: LANG } }).then(function (d) {
        status('op-status', S.redirect, 'ok');
        location.href = d.confirmation_url;
      }).catch(function (e) { $('op-submit').disabled = false; status('op-status', errText(e.code), 'error'); });
    });
  }

  // ── запуск ─────────────────────────────────────────────────────
  function start() {
    if (!API) {
      // Кабинет не подключён: значок в шапке ведёт на страницу кабинета,
      // где об этом честно написано; кнопки «Сохранить» не появляются.
    } else {
      markHeader();
      initFavButtons();
      checkOutage();
    }
    if (page === 'account') initAuth();
    else if (page === 'account-dashboard') initDashboard();
    else if (page === 'account-reset') initReset();
    else if (page === 'pay') initPay();
    else if (page === 'pay-order') initOrder();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
