/* Salary to freelance rate converter */
(function () {
  'use strict';
  function calc() {
    var salary     = FF.num('salary', 0);
    var benefits   = FF.num('benefitsPct', 0) / 100;
    var employerTax= FF.num('employerTaxPct', 0) / 100;
    var ptoDays    = FF.num('ptoDays', 0);
    var expenses   = FF.num('freelanceExpenses', 0);
    var hours      = FF.num('billableHours', 0);
    var weeksOff   = FF.num('weeksOff', 0);

    var warn = document.getElementById('warn');
    var workWeeks  = 52 - weeksOff;
    var billableYr = hours * workWeeks;
    if (salary <= 0 || billableYr <= 0) {
      warn.hidden = false;
      warn.textContent = 'Enter a salary and the hours you expect to bill each week.';
      document.getElementById('result').hidden = true;
      return;
    }
    warn.hidden = true;

    var benefitValue  = salary * benefits;
    var employerTaxes = salary * employerTax;
    var ptoValue      = salary * (ptoDays / 260);   // 260 working days in a year
    var totalPackage  = salary + benefitValue + employerTaxes;

    var rate   = (totalPackage + expenses) / billableYr;
    var naive  = salary / 2080;
    var mult   = naive > 0 ? rate / naive : 0;
    var dayRate = rate * 8;

    FF.set('outRate', FF.money(rate));
    FF.set('outSub', 'That is ' + mult.toFixed(1) + '× the naive "salary ÷ 2080" figure of '
      + FF.money(naive) + ' — and the gap is what your employer was quietly paying for.');
    FF.set('outDay',    FF.money0(dayRate));
    FF.set('outPackage', FF.money0(totalPackage));
    FF.set('outNaive',  FF.money(naive));
    FF.set('outHours',  Math.round(billableYr).toLocaleString('en-US') + ' hrs');

    FF.set('bSalary',   FF.money0(salary));
    FF.set('bBenefits', FF.money0(benefitValue));
    FF.set('bTaxes',    FF.money0(employerTaxes));
    FF.set('bPto',      FF.money0(ptoValue));
    FF.set('bPackage',  FF.money0(totalPackage));
    FF.set('bExp',      FF.money0(expenses));
    FF.set('bBillable', Math.round(billableYr).toLocaleString('en-US') + ' hrs');
    FF.set('bRate',     FF.money(rate));
    FF.show('result');
  }
  FF.live('calcForm', calc);
  FF.initCopy('copyBtn', 'result');
  FF.initReset('resetBtn', 'calcForm', calc);
})();
