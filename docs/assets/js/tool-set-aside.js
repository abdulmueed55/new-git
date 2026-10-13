/* Quarterly tax set-aside calculator */
(function () {
  'use strict';
  function calc() {
    var mode      = FF.val('mode') || 'annual';
    var rate      = FF.num('taxRate', 30) / 100;
    var alreadyPaid = FF.num('alreadyPaid', 0);
    var annual, perPayment = 0, payments = 0;

    var warn = document.getElementById('warn');

    if (mode === 'invoice') {
      perPayment = FF.num('invoiceAmount', 0);
      payments   = FF.num('invoicesPerYear', 0);
      annual     = perPayment * payments;
      if (perPayment <= 0 || payments <= 0) {
        warn.hidden = false;
        warn.textContent = 'Enter a typical invoice amount and how many you send in a year.';
        document.getElementById('result').hidden = true;
        return;
      }
    } else {
      annual = FF.num('annualProfit', 0);
      if (annual <= 0) {
        warn.hidden = false;
        warn.textContent = 'Enter the net profit you expect this year.';
        document.getElementById('result').hidden = true;
        return;
      }
    }
    warn.hidden = true;

    var totalTax  = annual * rate;
    var remaining = Math.max(0, totalTax - alreadyPaid);
    var perQuarter = remaining / 4;
    var perInvoice = perPayment > 0 ? perPayment * rate : 0;
    var perMonth   = totalTax / 12;

    FF.set('outQuarter', FF.money0(perQuarter));
    FF.set('outSub', 'Move this out of your business account the day the money lands, not the week the bill is due.');
    FF.set('outYear',  FF.money0(totalTax));
    FF.set('outMonth', FF.money0(perMonth));
    FF.set('outPct',   (rate * 100).toFixed(0) + '%');

    var invRow = document.getElementById('invoiceRow');
    if (invRow) {
      invRow.hidden = perInvoice <= 0;
      FF.set('outInvoice', FF.money(perInvoice));
    }

    FF.set('bAnnual',   FF.money0(annual));
    FF.set('bRate',     (rate * 100).toFixed(1) + '%');
    FF.set('bTotal',    FF.money0(totalTax));
    FF.set('bPaid',     '−' + FF.money0(alreadyPaid));
    FF.set('bRemain',   FF.money0(remaining));
    FF.set('bQuarter',  FF.money0(perQuarter));
    FF.show('result');
  }

  function syncFields() {
    var mode = FF.val('mode') || 'annual';
    var annualEl  = document.getElementById('f-annual');
    var invoiceEl = document.getElementById('f-invoice');
    if (annualEl)  annualEl.hidden  = mode !== 'annual';
    if (invoiceEl) invoiceEl.hidden = mode !== 'invoice';
  }
  function run() { syncFields(); calc(); }

  FF.live('calcForm', run);
  FF.initCopy('copyBtn', 'result');
  FF.initReset('resetBtn', 'calcForm', run);
})();
