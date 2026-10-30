/*
 * Организованная Культурность — админка (/admin/, с v69 сайта).
 *
 * Статический файл, пишется руками. Конфиг — window.OK_ACCOUNT (адрес
 * функции из ACCOUNT_API в gen.py). Вход — паролем админки; токен живёт
 * в sessionStorage этой вкладки (12 часов на сервере): закрыл вкладку —
 * вышел. Ни одна строка с сервера не попадает в innerHTML.
 *
 * Главное — «Требует внимания» в обзоре: оплаты без чека НПД (ЮKassa
 * больше не выбивает их за самозанятых), чеки к аннулированию после
 * возврата, новые заявки. И доход за год против лимита НПД 2,4 млн ₽.
 */
(function () {
  'use strict';
  var CFG = window.OK_ACCOUNT || {};
  var API = CFG.api || '';
  var TOKEN_KEY = 'ok_admin';
  function $(id) { return document.getElementById(id); }
  function val(id) { var e = $(id); return e ? String(e.value || '').trim() : ''; }
  function rub(n) { return Math.round(Number(n || 0)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽'; }
  function dt(iso) { if (!iso) return '—'; try { return new Date(iso).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' }); } catch (e) { return iso; } }
  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'text') n.textContent = attrs[k];
      else if (k === 'cls') n.className = attrs[k];
      else if (attrs[k] != null && attrs[k] !== false) n.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { if (c) n.appendChild(typeof c === 'string' ? document.createTextNode(c) : c); });
    return n;
  }
  function status(id, text, kind) {
    var s = $(id); if (!s) return;
    s.textContent = text || ''; s.classList.remove('is-error', 'is-ok');
    if (kind) s.classList.add(kind === 'error' ? 'is-error' : 'is-ok');
  }
  var ERR = {
    login_failed: 'Неверный пароль.', too_many_requests: 'Слишком много попыток — подождите 15 минут.',
    admin_auth_required: 'Сессия истекла — войдите снова.', server_misconfigured: 'Функция не настроена: ADMIN_PASSWORD / ADMIN_SECRET.',
    email_invalid: 'Проверьте почту клиента.', amount_invalid: 'Проверьте сумму.', title_required: 'Укажите название или выберите услугу.',
    company_required: 'Укажите название ИП или организации.', inn_invalid: 'ИНН не прошёл проверку.',
    order_not_found: 'Заказ не найден.', order_not_payable: 'Заказ уже оплачен или отменён.', order_not_cancelable: 'Отменить можно только неоплаченный.',
    order_not_paid: 'Заказ не оплачен.', order_not_refundable: 'Возврат возможен только по оплаченному заказу.', receipt_url_invalid: 'Нужна ссылка https://… на чек из «Мой налог».',
    no_payment: 'По заказу ещё не было платежа.', payment_not_found: 'ЮKassa не нашла платёж.', mail_failed: 'Письмо не ушло — проверьте MAIL_URL.',
    payments_not_configured: 'Реквизиты ЮKassa не заданы.', yookassa_unreachable: 'ЮKassa не отвечает.', yookassa_rejected: 'ЮKassa отклонила запрос — подробности в логе функции.',
    lead_not_found: 'Заявка не найдена.', storage_busy: 'Хранилище занято — повторите.', network: 'Нет связи с функцией.', internal: 'Ошибка функции — смотрите логи.'
  };
  var errText = function (c) { return ERR[c] || ERR.internal; };

  function tok() { try { return sessionStorage.getItem(TOKEN_KEY) || ''; } catch (e) { return ''; } }
  function setTok(t) { try { if (t) sessionStorage.setItem(TOKEN_KEY, t); else sessionStorage.removeItem(TOKEN_KEY); } catch (e) {} }

  function api(route, body, query) {
    var headers = {};
    if (body) headers['Content-Type'] = 'application/json';
    if (tok()) headers.Authorization = 'Bearer ' + tok();
    var q = '';
    if (query) Object.keys(query).forEach(function (k) { q += '&' + encodeURIComponent(k) + '=' + encodeURIComponent(query[k]); });
    return fetch(API + '?r=' + encodeURIComponent(route) + q, { method: body ? 'POST' : 'GET', headers: headers, body: body ? JSON.stringify(body) : undefined })
      .then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (d) {
          if (!r.ok) {
            var e = new Error(d.error || 'internal'); e.code = d.error || 'internal';
            if (e.code === 'admin_auth_required') { setTok(''); showLogin(); }
            throw e;
          }
          return d;
        });
      }, function () { var e = new Error('network'); e.code = 'network'; throw e; });
  }

  // ── вход ────────────────────────────────────────────────────────
  function showLogin() { $('adm-app').hidden = true; $('adm-login').hidden = false; }
  function showApp() { $('adm-login').hidden = true; $('adm-app').hidden = false; loadAll(); }

  var state = { orders: [], filter: 'attention', search: '' };

  // ── обзор ───────────────────────────────────────────────────────
  var ATT = {
    npd_todo: function (a) { return 'Чек НПД не выбит: ' + a.id + ' · ' + rub(a.amount) + ' · оплачено ' + dt(a.since); },
    npd_cancel_todo: function (a) { return 'Аннулировать чек после возврата: ' + a.id; },
    amount_mismatch: function (a) { return 'Сумма у ЮKassa не совпала с заказом: ' + a.id + ' — проверьте в кабинете ЮKassa'; },
    leads_new: function (a) { return 'Новые заявки: ' + a.count; }
  };
  function renderOverview(d) {
    var box = $('ov-body'); box.textContent = '';
    if (d.standby) box.appendChild(el('p', { cls: 'ok-attention', text: 'Этот сервер помечен как запасной (флажок резерва с ' + String(d.standby).slice(0, 10) + '): данные здесь могут быть устаревшими, задачи по расписанию выключены. Проверьте ACCOUNT_API сайта или снимите флажок — 11-account/HOSTING.md.' }));
    if (d.paymentsMode !== 'live') box.appendChild(el('p', { cls: 'ok-attention', text: d.paymentsMode === 'test' ? 'ЮKassa в тестовом режиме (YOOKASSA_MODE=test): платежи не настоящие.' : 'Боевые реквизиты ЮKassa не заданы — оплата на сайте не работает.' }));
    if (!d.attention.length) box.appendChild(el('p', { cls: 'ok-note', text: 'Срочного нет.' }));
    d.attention.forEach(function (a) {
      var link = el('a', { href: a.kind === 'leads_new' ? '#leads' : '#order=' + a.id, text: 'Открыть →' });
      box.appendChild(el('div', { cls: 'ok-attention' }, [(ATT[a.kind] || function () { return a.kind; })(a) + ' ', link]));
    });
    var inc = d.income;
    var pct = Math.min(100, Math.max(0, inc.share));
    box.appendChild(el('h3', { cls: 'ok-h3', style: 'margin-top:28px;', text: 'Доход за ' + inc.year + ' (без тестовых, за вычетом возвратов)' }));
    box.appendChild(el('p', { text: rub(inc.total) + ' из ' + rub(inc.limit) + ' — лимит НПД, осталось ' + rub(inc.left) }));
    var meter = el('div', { cls: 'ok-meter', role: 'img', 'aria-label': pct + '% лимита НПД' }, [el('span', { style: 'width:' + pct + '%' })]);
    box.appendChild(meter);
    if (pct >= 80) box.appendChild(el('p', { cls: 'ok-attention', text: 'Больше 80 % лимита НПД. Выше 2,4 млн ₽ за год режим самозанятого теряется — пора решать про ИП.' }));
    var c = d.counts;
    box.appendChild(el('p', { cls: 'ok-note', text: 'Заказов: ' + c.orders + ' · ждут оплаты: ' + c.awaiting + ' · оплачено: ' + c.paid + ' · без чека: ' + c.npdTodo + ' · новых заявок: ' + c.leadsNew + ' · кабинетов: ' + c.users }));
  }

  // ── заказы ──────────────────────────────────────────────────────
  var FILTERS = [['attention', 'Требуют действия'], ['all', 'Все'], ['awaiting_payment', 'Ждут оплаты'], ['paid', 'Оплачены'], ['refunded', 'Возвраты'], ['canceled', 'Отменены']];
  function needsAction(o) { return o.npd && (o.npd.status === 'todo' || o.npd.status === 'cancel_todo'); }
  function renderFilters() {
    var fr = $('or-filters'); fr.textContent = '';
    FILTERS.forEach(function (f) {
      var b = el('button', { type: 'button', cls: 'filter-pill' + (state.filter === f[0] ? ' active' : ''), 'aria-pressed': state.filter === f[0] ? 'true' : 'false', text: f[1] });
      b.addEventListener('click', function () { state.filter = f[0]; renderOrders(); });
      fr.appendChild(b);
    });
  }
  var STATUS = { awaiting_payment: 'ждёт оплаты', paid: 'оплачен', canceled: 'отменён', refunded: 'возврат' };
  var NPD = { todo: 'чек НЕ выбит', done: 'чек выбит', cancel_todo: 'аннулировать чек', canceled: 'чек аннулирован', not_needed: 'чек не нужен' };

  function act(o, route, body, statusId, okText) {
    status(statusId, 'Выполняю…');
    return api(route, Object.assign({ id: o.id }, body || {})).then(function (d) {
      status(statusId, okText || 'Готово.', 'ok');
      loadOrders(); loadOverview();
      return d;
    }).catch(function (e) { status(statusId, errText(e.code), 'error'); });
  }

  function orderCard(o) {
    var sid = 'st-' + o.id;
    var badgeCls = o.status === 'paid' ? (needsAction(o) ? 'warn' : 'paid') : o.status === 'awaiting_payment' ? 'awaiting' : 'warn';
    var payer = o.payer && o.payer.type === 'business' ? o.payer.company + ', ИНН ' + o.payer.inn : 'физлицо';
    var meta = [o.id, rub(o.amount), o.kind === 'invoice' ? 'счёт из админки' : 'оплата с сайта', 'создан ' + dt(o.createdAt)];
    if (o.paidAt) meta.push('оплачен ' + dt(o.paidAt));
    if (o.yk && o.yk.income != null) meta.push('на счёт ' + rub(o.yk.income) + ' (' + (o.yk.method || '—') + ')');
    if (o.yk && o.yk.test) meta.push('ТЕСТ');
    if (o.refund) meta.push('возврат ' + rub(o.refund.amount) + ' ' + dt(o.refund.at));
    if (o.accountDeleted) meta.push('кабинет удалён');
    var card = el('article', { cls: 'ok-order-row', id: 'order-' + o.id }, [
      el('div', { cls: 'row1' }, [el('h3', { text: o.title }), el('span', { cls: 'ok-badge ' + badgeCls, text: (STATUS[o.status] || o.status) + (o.npd ? ' · ' + (NPD[o.npd.status] || o.npd.status) : '') })]),
      el('div', { cls: 'meta', text: meta.join(' · ') }),
      el('div', { cls: 'meta', text: (o.name ? o.name + ' · ' : '') + (o.email || '—') + ' · плательщик: ' + payer + (o.note ? ' · «' + o.note + '»' : '') })
    ]);
    var actions = el('div', { cls: 'ok-actions' });
    var copy = el('button', { type: 'button', cls: 'btn-line', text: 'Скопировать ссылку' });
    copy.addEventListener('click', function () {
      (navigator.clipboard ? navigator.clipboard.writeText(o.link) : Promise.reject()).then(function () { status(sid, 'Ссылка скопирована.', 'ok'); }, function () { status(sid, o.link); });
    });
    actions.appendChild(copy);
    if (o.status === 'awaiting_payment') {
      var resend = el('button', { type: 'button', cls: 'btn-line', text: 'Отправить письмо ещё раз' });
      resend.addEventListener('click', function () { act(o, 'admin.order-resend', null, sid, 'Письмо отправлено.'); });
      actions.appendChild(resend);
      if (o.payments && o.payments.length) {
        var chk = el('button', { type: 'button', cls: 'btn-line', text: 'Проверить оплату в ЮKassa' });
        chk.addEventListener('click', function () { act(o, 'admin.order-check', null, sid, 'Проверено.'); });
        actions.appendChild(chk);
      }
      var cancel = el('button', { type: 'button', cls: 'btn-line ok-btn-danger', text: 'Отменить счёт' });
      cancel.addEventListener('click', function () {
        if (cancel.getAttribute('data-armed') !== '1') { cancel.setAttribute('data-armed', '1'); cancel.textContent = 'Точно отменить?'; return; }
        act(o, 'admin.order-cancel', null, sid, 'Счёт отменён.');
      });
      actions.appendChild(cancel);
    }
    card.appendChild(actions);

    // Чек НПД
    if (o.npd && (o.npd.status === 'todo' || o.npd.status === 'done')) {
      var rid = 'rc-' + o.id;
      var input = el('input', { type: 'url', id: rid, cls: 'ym-disable-keys', placeholder: 'https://lknpd.nalog.ru/api/v1/receipt/…', value: o.npd.receiptUrl || '' });
      var save = el('button', { type: 'button', cls: 'btn-line', text: o.npd.status === 'done' ? 'Обновить ссылку на чек' : 'Чек выбит — отправить клиенту' });
      save.addEventListener('click', function () { act(o, 'admin.order-npd', { receiptUrl: input.value.trim() }, sid, 'Чек отмечен, клиенту ушло письмо.'); });
      var hint = o.payer && o.payer.type === 'business'
        ? 'В «Мой налог»: «Новая продажа» → услуга «' + o.title + '», ' + rub(o.amount) + ', покупатель — юрлицо/ИП, ИНН ' + o.payer.inn + ' (' + o.payer.company + '). Затем «Поделиться» → ссылка.'
        : 'В «Мой налог»: «Новая продажа» → услуга «' + o.title + '», ' + rub(o.amount) + ', покупатель — физлицо. Затем «Поделиться» → ссылка.';
      card.appendChild(el('p', { cls: 'ok-note', text: hint }));
      card.appendChild(el('div', { cls: 'ok-inline' }, [el('label', { 'for': rid, cls: 'visually-hidden', text: 'Ссылка на чек ' + o.id }), input, save]));
    }
    if (o.npd && o.npd.status === 'cancel_todo') {
      var done = el('button', { type: 'button', cls: 'btn-line', text: 'Чек аннулирован в «Мой налог»' });
      done.addEventListener('click', function () { act(o, 'admin.order-npd', { action: 'canceled' }, sid); });
      card.appendChild(el('p', { cls: 'ok-note', text: 'После возврата чек аннулируется: «Мой налог» → чек → «Аннулировать» → причина «Возврат средств». При частичном возврате — аннулировать и выбить новый на оставшуюся сумму.' }));
      card.appendChild(el('div', { cls: 'ok-actions' }, [done]));
    }
    // Возврат
    if (o.status === 'paid') {
      var aid = 'ra-' + o.id, rsn = 'rr-' + o.id;
      var amount = el('input', { type: 'number', id: aid, cls: 'ym-disable-keys', min: '1', max: String(o.amount), step: '1', value: String(o.amount) });
      var reason = el('input', { type: 'text', id: rsn, cls: 'ym-disable-keys', placeholder: 'Причина (для себя)' });
      var ref = el('button', { type: 'button', cls: 'btn-line ok-btn-danger', text: 'Вернуть деньги' });
      ref.addEventListener('click', function () {
        if (ref.getAttribute('data-armed') !== '1') { ref.setAttribute('data-armed', '1'); ref.textContent = 'Вернуть ' + rub(amount.value) + '? Нажмите ещё раз'; return; }
        act(o, 'admin.order-refund', { amount: Number(amount.value), reason: reason.value }, sid, 'Возврат оформлен в ЮKassa.');
      });
      var det = el('details', {}, [el('summary', { cls: 'ok-note', text: 'Возврат' }), el('div', { cls: 'ok-inline' }, [
        el('label', { 'for': aid, cls: 'visually-hidden', text: 'Сумма возврата' }), amount,
        el('label', { 'for': rsn, cls: 'visually-hidden', text: 'Причина возврата' }), reason, ref])]);
      card.appendChild(det);
    }
    var hist = el('details', {}, [el('summary', { cls: 'ok-note', text: 'История' }), el('ul', { cls: 'ok-note' }, (o.history || []).map(function (h) { return el('li', { text: dt(h.at) + ' — ' + h.what + ' (' + h.by + ')' }); }))]);
    card.appendChild(hist);
    card.appendChild(el('p', { cls: 'review-form-status ok-status', id: sid, role: 'status', 'aria-live': 'polite' }));
    return card;
  }

  function renderOrders() {
    renderFilters();
    var q = state.search.toLowerCase();
    var list = state.orders.filter(function (o) {
      if (state.filter === 'attention') { if (!needsAction(o)) return false; }
      else if (state.filter !== 'all' && o.status !== state.filter) return false;
      if (!q) return true;
      return [o.id, o.email, o.name, o.title, o.payer && o.payer.inn, o.payer && o.payer.company].join(' ').toLowerCase().indexOf(q) !== -1;
    });
    var box = $('or-list'); box.textContent = '';
    if (!list.length) box.appendChild(el('p', { cls: 'ok-note', text: state.filter === 'attention' ? 'Нет заказов, которые ждут действия.' : 'Ничего не найдено.' }));
    list.forEach(function (o) { box.appendChild(orderCard(o)); });
    focusFromHash();
  }

  function focusFromHash() {
    var m = /order=([A-Z0-9-]+)/.exec(location.hash);
    if (!m) return;
    var card = $('order-' + m[1]);
    if (!card && state.filter !== 'all') { state.filter = 'all'; renderOrders(); return; }
    if (card) { card.scrollIntoView({ block: 'center' }); card.style.borderColor = 'var(--accent)'; }
  }

  // ── заявки, кабинеты, журнал ───────────────────────────────────
  var LEAD_FIELDS = [['name', 'Имя'], ['who', 'Кто'], ['contact', 'Связь'], ['project', 'Проект'], ['dates', 'Сроки'], ['budget', 'Бюджет'], ['task', 'Задача']];
  function renderLeads(leads) {
    var box = $('ld-list'); box.textContent = '';
    if (!leads.length) { box.appendChild(el('p', { cls: 'ok-note', text: 'Заявок нет.' })); return; }
    leads.forEach(function (l) {
      var sid = 'ls-' + l.id;
      var dl = el('dl', { cls: 'ok-kv' });
      LEAD_FIELDS.forEach(function (f) { if (l[f[0]]) { dl.appendChild(el('dt', { text: f[1] })); dl.appendChild(el('dd', { text: l[f[0]] })); } });
      var toggle = el('button', { type: 'button', cls: 'btn-line', text: l.status === 'done' ? 'Вернуть в новые' : 'Отработано' });
      toggle.addEventListener('click', function () { api('admin.lead-status', { id: l.id, status: l.status === 'done' ? 'new' : 'done' }).then(loadLeads).then(loadOverview).catch(function (e) { status(sid, errText(e.code), 'error'); }); });
      var del = el('button', { type: 'button', cls: 'btn-line ok-btn-danger', text: 'Удалить (уничтожение ПДн)' });
      del.addEventListener('click', function () {
        if (del.getAttribute('data-armed') !== '1') { del.setAttribute('data-armed', '1'); del.textContent = 'Удалить навсегда? Нажмите ещё раз'; return; }
        api('admin.lead-status', { id: l.id, status: 'delete' }).then(loadLeads).then(loadOverview).then(loadPdlog).catch(function (e) { status(sid, errText(e.code), 'error'); });
      });
      box.appendChild(el('article', { cls: 'ok-order-row' }, [
        el('div', { cls: 'row1' }, [el('h3', { text: dt(l.at) + (l.lang === 'en' ? ' · EN' : '') }), el('span', { cls: 'ok-badge ' + (l.status === 'new' ? 'awaiting' : ''), text: l.status === 'new' ? 'новая' : 'отработана' })]),
        dl, el('div', { cls: 'ok-actions' }, [toggle, del]),
        el('p', { cls: 'review-form-status ok-status', id: sid, role: 'status', 'aria-live': 'polite' })
      ]));
    });
  }
  function table(head, rows) {
    return el('div', { cls: 'ok-tablewrap' }, [el('table', { cls: 'ok-table' }, [
      el('thead', {}, [el('tr', {}, head.map(function (h) { return el('th', { scope: 'col', text: h }); }))]),
      el('tbody', {}, rows.map(function (r) { return el('tr', {}, r.map(function (c) { return el('td', { text: String(c) }); })); }))
    ])]);
  }
  function renderClients(list) {
    var box = $('cl-list'); box.textContent = '';
    if (!list.length) { box.appendChild(el('p', { cls: 'ok-note', text: 'Кабинетов пока нет.' })); return; }
    box.appendChild(table(['Почта', 'Имя', 'Язык', 'Создан', 'Последний вход', 'Сохранено', 'Заказов'],
      list.map(function (c) { return [c.email, c.name || '—', c.lang, dt(c.createdAt), dt(c.lastLoginAt), c.favorites, c.orders]; })));
  }
  function renderPdlog(rows) {
    var box = $('pd-list'); box.textContent = '';
    if (!rows.length) { box.appendChild(el('p', { cls: 'ok-note', text: 'Записей нет.' })); return; }
    box.appendChild(table(['Когда', 'Что', 'Чьи (хэш)', 'Какие данные'], rows.map(function (r) { return [dt(r.at), r.what, r.subject, (r.data || []).join(', ')]; })));
  }

  // ── посещаемость (v70) ──────────────────────────────────────────
  // Суммы обезличенного счётчика (11-account/functions/routes/stats.js).
  var ST_PERIODS = [['today', 'Сегодня'], ['7', '7 дней'], ['30', '30 дней'], ['month', 'Этот месяц'], ['prev', 'Прошлый месяц']];
  var ST_SRC = { direct: 'прямые заходы', yandex: 'Яндекс', google: 'Google', telegram: 'Telegram', vk: 'VK' };
  var ST_DEV = { m: 'телефон', t: 'планшет', d: 'компьютер', '?': 'не определено' };
  var ST_GOAL = {
    page_not_found: 'страница 404', brief_start: 'начали бриф', brief_submit: 'отправили бриф', offer_download: 'скачали КП',
    cv_download: 'скачали CV', press_kit_download: 'скачали из пресс-кита', telegram_channel_click: 'перешли в Telegram-канал',
    telegram_bot_click: 'перешли в бота', vk_click: 'перешли в VK', email_click: 'нажали на почту', review_submit: 'отправили отзыв', rss_click: 'нажали RSS'
  };
  var stPeriod = '30';
  function nf(n) { return Math.round(Number(n || 0)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' '); }
  function topRows(map, n, label) {
    return Object.keys(map || {}).map(function (k) { return [k, map[k]]; }).sort(function (a, b) { return b[1] - a[1]; })
      .slice(0, n).map(function (r) { return [label ? (label[r[0]] || r[0]) : r[0], nf(r[1])]; });
  }
  function renderStatsPeriods() {
    var box = $('st-periods'); box.textContent = '';
    ST_PERIODS.forEach(function (p) {
      var b = el('button', { type: 'button', cls: 'filter-pill' + (stPeriod === p[0] ? ' active' : ''), 'aria-pressed': stPeriod === p[0] ? 'true' : 'false', text: p[1] });
      b.addEventListener('click', function () { stPeriod = p[0]; renderStatsPeriods(); loadStats(); });
      box.appendChild(b);
    });
  }
  function renderStats(d) {
    var box = $('st-body'); box.textContent = '';
    var t = d.total;
    var span = d.from === d.to ? d.from.split('-').reverse().join('.') : d.from.split('-').reverse().join('.') + ' — ' + d.to.split('-').reverse().join('.');
    box.appendChild(el('p', { cls: 'ok-note', text: span }));
    box.appendChild(el('div', { cls: 'ok-stat-cards' }, [
      el('div', { cls: 'ok-stat' }, [el('div', { cls: 'n', text: nf(t.views) }), el('div', { cls: 'l', text: 'просмотров' })]),
      el('div', { cls: 'ok-stat' }, [el('div', { cls: 'n', text: nf(t.visits) }), el('div', { cls: 'l', text: 'визитов' })]),
      el('div', { cls: 'ok-stat' }, [el('div', { cls: 'n', text: (d.exact ? '' : '≈ ') + nf(d.visitors) }), el('div', { cls: 'l', text: 'посетителей' + (d.exact ? '' : ' (оценка сверху)') })])
    ]));
    if (!t.views && !Object.keys(t.events || {}).length) { box.appendChild(el('p', { cls: 'ok-note', text: 'За этот период посещений нет.' })); return; }
    if (d.days.length > 1) {
      var max = Math.max.apply(null, d.days.map(function (x) { return x.views; }).concat([1]));
      var wrap = el('div', { cls: 'ok-tablewrap' }, [el('table', { cls: 'ok-table' }, [
        el('thead', {}, [el('tr', {}, ['День', 'Просмотры', 'Визиты', 'Посетители за день'].map(function (h) { return el('th', { scope: 'col', text: h }); }))]),
        el('tbody', {}, d.days.slice().reverse().map(function (x) {
          var bar = el('span', { cls: 'ok-bar', 'aria-hidden': 'true' }); bar.style.width = Math.max(2, Math.round(110 * x.views / max)) + 'px';
          return el('tr', {}, [el('td', { text: x.date.split('-').reverse().join('.') }), el('td', {}, [el('span', { cls: 'ok-barcell' }, [bar, el('span', { text: nf(x.views) })])]),
            el('td', { text: nf(x.visits) }), el('td', { text: nf(x.daily) })]);
        }))
      ])]);
      box.appendChild(el('h3', { cls: 'ok-h3', text: 'По дням' })); box.appendChild(wrap);
    }
    [['Страницы', topRows(t.pages, 15), ['Страница', 'Просмотры']],
     ['Откуда пришли', topRows(t.sources, 12, ST_SRC), ['Источник', 'Визиты']],
     ['Метки UTM (QR-коды, ссылки в постах)', topRows(t.utm, 12).map(function (r) { return [r[0].split('|').join(' / '), r[1]]; }), ['source / medium / campaign', 'Визиты']],
     ['Действия', topRows(t.events, 12, ST_GOAL), ['Что сделали', 'Раз']],
     ['Устройства', topRows(t.devices, 4, ST_DEV), ['Устройство', 'Просмотры']],
     ['Язык', topRows(t.langs, 2, { ru: 'русская версия', en: 'английская версия' }), ['Версия сайта', 'Просмотры']],
     ['Не нашли страницу (404)', topRows(t.missing, 15), ['Адрес', 'Раз']]
    ].forEach(function (b) {
      if (!b[1].length) return;
      box.appendChild(el('h3', { cls: 'ok-h3', text: b[0] }));
      box.appendChild(table(b[2], b[1]));
    });
  }
  function loadStats() { return api('admin.stats', null, { period: stPeriod }).then(renderStats).catch(fail); }

  // ── загрузка ────────────────────────────────────────────────────
  function fail(e) { status('adm-status', errText(e.code), 'error'); }
  function loadOverview() { return api('admin.overview').then(renderOverview).catch(fail); }
  function loadOrders() { return api('admin.orders').then(function (d) { state.orders = d.orders; renderOrders(); }).catch(fail); }
  function loadLeads() { return api('admin.leads').then(function (d) { renderLeads(d.leads); }).catch(fail); }
  function loadClients() { return api('admin.clients').then(function (d) { renderClients(d.clients); }).catch(fail); }
  function loadPdlog() { return api('admin.pdlog').then(function (d) { renderPdlog(d.rows); }).catch(fail); }
  function loadAll() { status('adm-status', ''); loadOverview(); loadOrders(); loadLeads(); loadClients(); renderStatsPeriods(); loadStats(); loadPdlog(); }

  // ── новый счёт ──────────────────────────────────────────────────
  function initNewForm() {
    var sel = $('nf-service');
    sel.addEventListener('change', function () {
      var o = sel.options[sel.selectedIndex];
      if (o && o.getAttribute('data-price') && !val('nf-amount')) $('nf-amount').value = o.getAttribute('data-price');
    });
    var radios = document.querySelectorAll('input[name="nf-payer-type"]');
    function sync() { var b = document.querySelector('input[name="nf-payer-type"]:checked'); $('nf-business').hidden = !(b && b.value === 'business'); }
    radios.forEach(function (r) { r.addEventListener('change', sync); }); sync();
    $('new-form').addEventListener('submit', function (ev) {
      ev.preventDefault();
      var b = document.querySelector('input[name="nf-payer-type"]:checked');
      var payer = b && b.value === 'business' ? { type: 'business', company: val('nf-company'), inn: val('nf-inn').replace(/\D/g, '') } : { type: 'person' };
      status('nf-status', 'Создаю…');
      api('admin.order-create', {
        email: val('nf-email'), name: val('nf-name'), serviceId: sel.value || undefined, title: val('nf-title'),
        amount: Number(val('nf-amount')), note: val('nf-note'), lang: $('nf-lang').value, payer: payer, send: $('nf-send').checked
      }).then(function (d) {
        status('nf-status', 'Счёт ' + d.order.id + ' создан' + (d.mailed ? ', письмо отправлено.' : '. Ссылка: ' + d.order.link), 'ok');
        $('new-form').reset(); sync();
        loadOrders(); loadOverview();
      }).catch(function (e) { status('nf-status', errText(e.code), 'error'); });
    });
  }

  function start() {
    if (!API) { status('adm-status', 'ACCOUNT_API в gen.py не задан — админка подключится после выкладки функции.'); $('adm-app').hidden = false; return; }
    $('adm-login').addEventListener('submit', function (ev) {
      ev.preventDefault();
      status('adm-login-status', 'Вхожу…');
      api('admin.login', { password: $('adm-password').value }).then(function (d) { setTok(d.token); $('adm-password').value = ''; status('adm-login-status', ''); showApp(); })
        .catch(function (e) { status('adm-login-status', errText(e.code), 'error'); });
    });
    $('adm-logout').addEventListener('click', function () { setTok(''); showLogin(); });
    $('or-search').addEventListener('input', function () { state.search = val('or-search'); renderOrders(); });
    window.addEventListener('hashchange', focusFromHash);
    initNewForm();
    if (tok()) showApp(); else showLogin();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
