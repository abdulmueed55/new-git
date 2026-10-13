/* Freelance take-home pay calculator */
(function () {
  'use strict';
  function calc() {
    var gross      = FF.num('grossRevenue', 0);
    var expenses   = FF.num('businessExpenses', 0);
    var seRate     = FF.num('seRate', 15.3) / 100;
    var fedRate    = FF.num('federalRate', 0) / 100;
    var stateRate  = FF.num('stateRate', 0) / 100;
    var retirePct  = FF.num('retirementPct', 0) / 100;
    var healthMo   = FF.num('healthMonthly', 0);

    var warn = document.getElementById('warn');
    if (gross <= 0) {
      warn.hidden = false;
      warn.textContent = 'Enter the revenue you expect to invoice this year.';
      document.getElementById('result').hidden = true;
      return;
    }
    warn.hidden = true;

    var netProfit = gross - expenses;
    if (netProfit < 0) netProfit = 0;

    var seTax      = netProfit * 0.9235 * seRate;
    var retirement = netProfit * retirePct;
    var health     = healthMo * 12;

    // Rough taxable income: net profit less half the SE tax, retirement and health premiums.
    var taxable  = Math.max(0, netProfit - seTax / 2 - retirement - health);
    var fedTax   = taxable * fedRate;
    var stateTax = taxable * stateRate;

    var totalTax = seTax + fedTax + stateTax;
    var takeHome = netProfit - totalTax - retirement - health;
    var monthly  = takeHome / 12;
    var effRate  = netProfit > 0 ? (totalTax / netProfit) * 100 : 0;
    var keepPct  = gross > 0 ? (takeHome / gross) * 100 : 0;

    FF.set('outMonthly', FF.money0(monthly));
    FF.set('outSub', 'You keep ' + keepPct.toFixed(0) + '¢ of every dollar you invoice, before retirement savings are counted as yours again.');
    FF.set('outYear',    FF.money0(takeHome));
    FF.set('outTax',     FF.money0(totalTax));
    FF.set('outEff',     effRate.toFixed(1) + '%');
    FF.set('outRetire',  FF.money0(retirement));

    FF.set('bGross',    FF.money0(gross));
    FF.set('bExp',      '−' + FF.money0(expenses));
    FF.set('bNet',      FF.money0(netProfit));
    FF.set('bSe',       '−' + FF.money0(seTax));
    FF.set('bFed',      '−' + FF.money0(fedTax));
    FF.set('bState',    '−' + FF.money0(stateTax));
    FF.set('bRetire',   '−' + FF.money0(retirement));
    FF.set('bHealth',   '−' + FF.money0(health));
    FF.set('bTake',     FF.money0(takeHome));
    FF.show('result');
  }
  FF.live('calcForm', calc);
  FF.initCopy('copyBtn', 'result');
  FF.initReset('resetBtn', 'calcForm', calc);
})();
