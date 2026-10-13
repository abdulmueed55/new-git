/* US self-employment tax calculator */
(function () {
  'use strict';
  var THRESHOLDS = { single: 200000, mfj: 250000, mfs: 125000, hoh: 200000 };

  function calc() {
    var profit   = FF.num('netProfit', 0);
    var w2       = FF.num('w2Wages', 0);
    var status   = FF.val('filingStatus') || 'single';
    var wageBase = FF.num('wageBase', 0);
    var ssRate   = FF.num('ssRate', 12.4) / 100;
    var medRate  = FF.num('medRate', 2.9) / 100;

    var warn = document.getElementById('warn');
    if (profit <= 0) {
      warn.hidden = false;
      warn.textContent = 'Enter your net profit (business income minus business expenses) to see the tax.';
      document.getElementById('result').hidden = true;
      return;
    }
    warn.hidden = true;

    // Only 92.35% of net profit is subject to SE tax.
    var seBase = profit * 0.9235;

    // Social Security stops at the wage base, and W-2 wages use it up first.
    var ssRoom     = Math.max(0, wageBase - w2);
    var ssTaxable  = Math.min(seBase, ssRoom);
    var ssTax      = ssTaxable * ssRate;

    // Medicare has no cap.
    var medTax = seBase * medRate;

    // Additional Medicare: 0.9% above the filing-status threshold.
    var threshold = THRESHOLDS[status] || 200000;
    var addlBase  = Math.max(0, (seBase + w2) - threshold);
    var addlTax   = addlBase * 0.009;

    var total = ssTax + medTax + addlTax;
    // Half of the regular SE tax is an income-tax deduction (not the 0.9% surtax).
    var deduction = (ssTax + medTax) / 2;
    var effective = (total / profit) * 100;

    FF.set('outTotal',   FF.money(total, 'USD'));
    FF.set('outSub',     'That is ' + effective.toFixed(1) + '% of your net profit, on top of federal and state income tax.');
    FF.set('outQuarter', FF.money0(total / 4, 'USD'));
    FF.set('outDeduct',  FF.money0(deduction, 'USD'));
    FF.set('outEff',     effective.toFixed(1) + '%');

    FF.set('bProfit',   FF.money0(profit, 'USD'));
    FF.set('bSeBase',   FF.money0(seBase, 'USD'));
    FF.set('bSsTaxable', FF.money0(ssTaxable, 'USD'));
    FF.set('bSs',       FF.money(ssTax, 'USD'));
    FF.set('bMed',      FF.money(medTax, 'USD'));
    FF.set('bAddl',     FF.money(addlTax, 'USD'));
    FF.set('bTotal',    FF.money(total, 'USD'));

    var capRow = document.getElementById('capNote');
    if (capRow) {
      capRow.hidden = seBase <= ssRoom;
      if (!capRow.hidden) {
        capRow.textContent = 'Your Social Security portion is capped: only ' +
          FF.money0(ssTaxable, 'USD') + ' of your ' + FF.money0(seBase, 'USD') +
          ' SE base is taxed for Social Security. Everything above the wage base pays Medicare only.';
      }
    }
    FF.show('result');
  }
  FF.live('calcForm', calc);
  FF.initCopy('copyBtn', 'result');
  FF.initReset('resetBtn', 'calcForm', calc);
})();
