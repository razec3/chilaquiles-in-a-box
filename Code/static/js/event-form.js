// Live-updates the "purchase limit" hint (70% of budget) as the user types.
// Server-side validation and calculation remain authoritative; this is a
// convenience preview only.
(function () {
  var budgetInput = document.getElementById("id_budget");
  var hint = document.getElementById("purchase-limit-hint");
  if (!budgetInput || !hint) {
    return;
  }

  function formatChf(amount) {
    return amount.toLocaleString("de-CH", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function update() {
    var budget = parseFloat(budgetInput.value.replace(",", "."));
    if (!isFinite(budget) || budget <= 0) {
      hint.textContent = "Einkaufskosten max. 70% des Budgets";
      return;
    }
    hint.textContent =
      "Einkaufskosten max. 70% des Budgets (CHF " + formatChf(budget * 0.7) + ")";
  }

  budgetInput.addEventListener("input", update);
  update();
})();
