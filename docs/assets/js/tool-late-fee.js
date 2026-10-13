/* Invoice late fee and interest calculator */
(function () {
  'use strict';
  var DAY = 86400000;

  function parseDate(id) {
    var v = FF.val(id);
    if (!v) return null;
    var p = v.split('-');
    if (p.length !== 3) return null;
    var d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2]));
    return isNaN(d.getTime()) ? null : d;
  }

  function ukCompensation(amount) {
    if (amount < 1000) return 40;
    if (amount < 10000) return 70;
    return 100;
  }

  function calc() {
    var amount = FF.num('invoiceAmount', 0);
    var method = FF.val('method') || 'monthly';
    var due    = parseDate('dueDate');
    var asOf   = parseDate('asOfDate');

    var warn   = document.getElementById('warn');
    var result = document.getElementById('result');

    if (!due || !asOf || amount <= 0) {
      warn.hidden = false;
      warn.textContent = 'Enter the invoice amount, the date it was due, and today’s date.';
      result.hidden = true;
      return;
    }
    var days = Math.floor((asOf - due) / DAY);
    if (days <= 0) {
      warn.hidden = false;
      warn.textContent = 'This invoice is not overdue yet — no late fee applies on that date.';
      result.hidden = true;
      return;
    }
    warn.hidden = true;

    var fee = 0, flat = 0, interest = 0, label = '', basis = '';

    if (method === 'monthly') {
      var mRate  = FF.num('monthlyRate', 1.5) / 100;
      var whole  = FF.val('proration') === 'month';
      var months = whole ? Math.ceil(days / 30) : days / 30;
      interest = amount * mRate * months;
      label = (mRate * 100).toFixed(2) + '% per month';
      basis = whole
        ? months + ' started month(s)'
        : days + ' days (' + months.toFixed(2) + ' months, prorated daily)';
    } else if (method === 'annual') {
      var aRate = FF.num('annualRate', 8) / 100;
      interest = amount * aRate * (days / 365);
      label = (aRate * 100).toFixed(2) + '% per year';
      basis = days + ' days ÷ 365';
    } else if (method === 'flat') {
      flat  = FF.num('flatFee', 0);
      label = 'one-off flat fee';
      basis = days + ' days overdue';
    } else if (method === 'flatmonthly') {
      flat = FF.num('flatFee', 0);
      var m2 = FF.num('monthlyRate', 1.5) / 100;
      var months2 = Math.ceil(days / 30);
      interest = amount * m2 * months2;
      label = 'flat fee + ' + (m2 * 100).toFixed(2) + '% per month';
      basis = months2 + ' started month(s)';
    } else if (method === 'uk') {
      var base = FF.num('ukBaseRate', 4.0) / 100;
      var stat = base + 0.08;
      interest = amount * stat * (days / 365);
      flat = ukCompensation(amount);
      label = 'UK statutory: base ' + (base * 100).toFixed(2) + '% + 8% = ' + (stat * 100).toFixed(2) + '%';
      basis = days + ' days ÷ 365, plus fixed compensation';
    }

    fee = flat + interest;
    var total   = amount + fee;
    var perDay  = interest > 0 ? interest / days : 0;

    FF.set('outTotal', FF.money(total));
    FF.set('outSub', FF.money(fee) + ' of late charges on a ' + FF.money(amount) + ' invoice.');
    FF.set('outDays',   days.toLocaleString('en-US') + ' days');
    FF.set('outPerDay', FF.money(perDay));
    FF.set('outFee',    FF.money(fee));

    FF.set('bAmount',   FF.money(amount));
    FF.set('bFlat',     FF.money(flat));
    FF.set('bInterest', FF.money(interest));
    FF.set('bTotal',    FF.money(total));
    FF.set('bLabel',    label);
    FF.set('bBasis',    basis);
    FF.show('result');
  }

  function syncFields() {
    var method = FF.val('method') || 'monthly';
    var map = {
      monthly:     ['f-monthly', 'f-proration'],
      annual:      ['f-annual'],
      flat:        ['f-flat'],
      flatmonthly: ['f-flat', 'f-monthly'],
      uk:          ['f-ukbase']
    };
    var all = ['f-monthly', 'f-annual', 'f-flat', 'f-proration', 'f-ukbase'];
    var on = map[method] || [];
    all.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) el.hidden = on.indexOf(id) === -1;
    });
  }

  function run() { syncFields(); calc(); }

  // Default the "as of" date to today, due date to 30 days ago.
  var today = new Date();
  function iso(d) { return d.toISOString().slice(0, 10); }
  var asOfEl = document.getElementById('asOfDate');
  var dueEl  = document.getElementById('dueDate');
  if (asOfEl && !asOfEl.value) asOfEl.value = iso(today);
  if (dueEl && !dueEl.value) dueEl.value = iso(new Date(today.getTime() - 30 * DAY));

  FF.live('calcForm', run);
  FF.initCopy('copyBtn', 'result');
  FF.initReset('resetBtn', 'calcForm', function () {
    if (asOfEl) asOfEl.value = iso(new Date());
    if (dueEl) dueEl.value = iso(new Date(Date.now() - 30 * DAY));
    run();
  });
})();
