"""Event input validation. Message wording per spec.md's "Business Rules" note."""

from decimal import Decimal

from django import forms

GUEST_COUNT_MESSAGE = "Bitte geben Sie eine positive Anzahl Gäste ein."
BUDGET_MESSAGE = "Bitte geben Sie ein Budget grösser als CHF 0.00 ein."


class EventInputForm(forms.Form):
    guest_count = forms.IntegerField(
        min_value=1,
        error_messages={
            "required": GUEST_COUNT_MESSAGE,
            "invalid": GUEST_COUNT_MESSAGE,
            "min_value": GUEST_COUNT_MESSAGE,
        },
    )
    budget = forms.DecimalField(
        min_value=Decimal("0.01"),
        max_digits=10,
        decimal_places=2,
        error_messages={
            "required": BUDGET_MESSAGE,
            "invalid": BUDGET_MESSAGE,
            "min_value": BUDGET_MESSAGE,
        },
    )
