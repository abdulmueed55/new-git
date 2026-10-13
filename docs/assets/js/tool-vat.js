/* VAT / sales tax calculator */
(function () {
  'use strict';
  function calc() {
    var amount = FF.num('amount', 0);
    var rate   = FF.num('rate', 0) / 100;
    var mode   = FF.val('mode') || 'add';

    var warn = document.getElementById('warn');
    if (amount <= 0) {
      warn.hidden = false;
      warn.textContent = 'Enter an amount to work from.';
      document.getElementById('result').hidden = true;
      return;
    }
    warn.hidden = true;

    var net, tax, gross;
    if (mode === 'add') {
      net = amount; tax = amount * rate; gross = net + tax;
    } else {
      gross = amount; net = amount / (1 + rate); tax = gross - net;
    }

    FF.set('outMain', FF.money(mode === 'add' ? gross : net));
    FF.set('outSub', mode === 'add'
      ? 'Charge this on the invoice. ' + FF.money(tax) + ' of it belongs to the tax office, not to you.'
      : 'This is the part you actually earned. ' + FF.money(tax) + ' was never your money.');
    FF.set('outNet',   FF.money(net));
    FF.set('outTax',   FF.money(tax));
    FF.set('outGross', FF.money(gross));

    FF.set('bNet',   FF.money(net));
    FF.set('bRate',  (rate * 100).toFixed(2) + '%');
    FF.set('bTax',   FF.money(tax));
    FF.set('bGross', FF.money(gross));
    FF.set('bLabel', mode === 'add' ? 'Tax added to a net price' : 'Tax removed from a gross price');
    FF.show('result');
  }

  // Preset rates fill the rate box.
  var preset = document.getElementById('preset');
  if (preset) {
    preset.addEventListener('change', function () {
      if (preset.value) {
        var el = document.getElementById('rate');
        if (el) el.value = preset.value;
        calc();
      }
    });
  }
  FF.live('calcForm', calc);
  FF.initCopy('copyBtn', 'result');
  FF.initReset('resetBtn', 'calcForm', calc);
})();
