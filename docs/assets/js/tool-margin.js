/* Profit margin and markup calculator */
(function () {
  'use strict';
  function calc() {
    var mode = FF.val('mode') || 'price';
    var cost = FF.num('cost', 0);
    var warn = document.getElementById('warn');

    if (cost <= 0) {
      warn.hidden = false;
      warn.textContent = 'Enter what the work or the goods cost you.';
      document.getElementById('result').hidden = true;
      return;
    }

    var price, margin, markup, profit;

    if (mode === 'price') {
      price = FF.num('price', 0);
      if (price <= 0) {
        warn.hidden = false;
        warn.textContent = 'Enter the price you charge.';
        document.getElementById('result').hidden = true;
        return;
      }
    } else if (mode === 'margin') {
      margin = FF.num('targetMargin', 0) / 100;
      if (margin >= 1) {
        warn.hidden = false;
        warn.textContent = 'A margin of 100% or more is impossible — margin is a share of the price.';
        document.getElementById('result').hidden = true;
        return;
      }
      price = cost / (1 - margin);
    } else {
      markup = FF.num('targetMarkup', 0) / 100;
      price = cost * (1 + markup);
    }
    warn.hidden = true;

    profit = price - cost;
    margin = price > 0 ? profit / price : 0;
    markup = cost > 0 ? profit / cost : 0;

    FF.set('outMain', FF.money(price));
    FF.set('outSub', 'Margin and markup are not the same number. A 50% markup is only a 33.3% margin.');
    FF.set('outProfit', FF.money(profit));
    FF.set('outMargin', (margin * 100).toFixed(1) + '%');
    FF.set('outMarkup', (markup * 100).toFixed(1) + '%');

    FF.set('bCost',   FF.money(cost));
    FF.set('bProfit', FF.money(profit));
    FF.set('bPrice',  FF.money(price));
    FF.set('bMargin', (margin * 100).toFixed(1) + '%');
    FF.set('bMarkup', (markup * 100).toFixed(1) + '%');
    FF.show('result');
  }

  function syncFields() {
    var mode = FF.val('mode') || 'price';
    [['f-price', 'price'], ['f-margin', 'margin'], ['f-markup', 'markup']].forEach(function (p) {
      var el = document.getElementById(p[0]);
      if (el) el.hidden = mode !== p[1];
    });
  }
  function run() { syncFields(); calc(); }

  FF.live('calcForm', run);
  FF.initCopy('copyBtn', 'result');
  FF.initReset('resetBtn', 'calcForm', run);
})();
