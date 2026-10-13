/* Freelance hourly rate calculator */
(function () {
  'use strict';
  function calc() {
    var target   = FF.num('targetIncome', 0);
    var expenses = FF.num('expenses', 0);
    var hours    = FF.num('billableHours', 0);
    var vacation = FF.num('vacationWeeks', 0);
    var holidays = FF.num('holidayDays', 0);
    var sick     = FF.num('sickDays', 0);
    var taxRate  = FF.num('taxRate', 0);
    var profit   = FF.num('profitMargin', 0);

    var weeksOff    = vacation + (holidays + sick) / 5;
    var workWeeks   = 52 - weeksOff;
    var billableYr  = hours * workWeeks;

    var warn = document.getElementById('warn');
    if (billableYr <= 0 || taxRate >= 100) {
      warn.hidden = false;
      warn.textContent = billableYr <= 0
        ? 'Add some billable hours and working weeks to see a rate.'
        : 'Tax rate must be below 100%.';
      document.getElementById('result').hidden = true;
      return;
    }
    warn.hidden = true;

    // Target income is take-home, so gross it up for tax, then cover expenses.
    var revenueForPay  = target / (1 - taxRate / 100);
    var revenueNeeded  = revenueForPay + expenses;
    var withProfit     = revenueNeeded * (1 + profit / 100);

    var rate      = withProfit / billableYr;
    var minRate   = revenueNeeded / billableYr;
    var dayRate   = rate * 8;
    var weekRate  = rate * hours;
    var monthRate = withProfit / 12;
    var util      = (hours / 40) * 100;

    FF.set('outRate',  FF.money(rate));
    FF.set('outSub',   'Round up to ' + FF.money0(Math.ceil(rate / 5) * 5) +
                       ' when you quote — nobody ever won work by being 3% cheaper.');
    FF.set('outDay',   FF.money0(dayRate));
    FF.set('outWeek',  FF.money0(weekRate));
    FF.set('outMonth', FF.money0(monthRate));
    FF.set('outHours', Math.round(billableYr).toLocaleString('en-US') + ' hrs');

    FF.set('bTarget',   FF.money0(target));
    FF.set('bTaxUp',    FF.money0(revenueForPay - target));
    FF.set('bExpenses', FF.money0(expenses));
    FF.set('bProfit',   FF.money0(withProfit - revenueNeeded));
    FF.set('bTotal',    FF.money0(withProfit));
    FF.set('bWeeks',    workWeeks.toFixed(1) + ' weeks');
    FF.set('bUtil',     util.toFixed(0) + '% of a 40-hour week');
    FF.set('bMin',      FF.money(minRate));
    FF.show('result');
  }
  FF.live('calcForm', calc);
  FF.initCopy('copyBtn', 'result');
  FF.initReset('resetBtn', 'calcForm', calc);
})();
