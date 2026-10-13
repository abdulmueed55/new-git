/* Project quote calculator */
(function () {
  'use strict';
  function calc() {
    var hours      = FF.num('hours', 0);
    var rate       = FF.num('rate', 0);
    var complexity = FF.num('complexity', 1);
    var revision   = FF.num('revisionBuffer', 0) / 100;
    var rush       = FF.num('rushFee', 0) / 100;
    var expenses   = FF.num('expenses', 0);
    var discount   = FF.num('discount', 0) / 100;
    var tax        = FF.num('taxRate', 0) / 100;
    var deposit    = FF.num('depositPct', 0) / 100;

    var warn = document.getElementById('warn');
    if (hours <= 0 || rate <= 0) {
      warn.hidden = false;
      warn.textContent = 'Enter the estimated hours and your hourly rate.';
      document.getElementById('result').hidden = true;
      return;
    }
    warn.hidden = true;

    var base       = hours * rate * complexity;
    var revAmount  = base * revision;
    var rushAmount = (base + revAmount) * rush;
    var subtotal   = base + revAmount + rushAmount + expenses;
    var discAmount = subtotal * discount;
    var afterDisc  = subtotal - discAmount;
    var taxAmount  = afterDisc * tax;
    var total      = afterDisc + taxAmount;

    var depositAmt = total * deposit;
    var realHours  = hours * complexity * (1 + revision);
    var effective  = realHours > 0 ? afterDisc / realHours : 0;

    FF.set('outTotal', FF.money(total));
    FF.set('outSub', 'Quote this as one number. Send the breakdown only if the client asks for it.');
    FF.set('outDeposit',   FF.money0(depositAmt));
    FF.set('outBalance',   FF.money0(total - depositAmt));
    FF.set('outEffective', FF.money(effective));
    FF.set('outHours',     realHours.toFixed(1) + ' hrs');

    FF.set('bBase',     FF.money(base));
    FF.set('bBaseNote', hours + ' hrs × ' + FF.money(rate) + ' × ' + complexity.toFixed(2) + ' complexity');
    FF.set('bRev',      FF.money(revAmount));
    FF.set('bRush',     FF.money(rushAmount));
    FF.set('bExp',      FF.money(expenses));
    FF.set('bSub',      FF.money(subtotal));
    FF.set('bDisc',     '−' + FF.money(discAmount));
    FF.set('bTax',      FF.money(taxAmount));
    FF.set('bTotal',    FF.money(total));
    FF.show('result');
  }
  FF.live('calcForm', calc);
  FF.initCopy('copyBtn', 'result');
  FF.initReset('resetBtn', 'calcForm', calc);
})();
