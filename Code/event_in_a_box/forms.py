"""Event input validation. Message wording per spec.md's "Business Rules" note."""

from decimal import Decimal

from django import forms

from .models import EventType, Preference

GUEST_COUNT_MESSAGE = "Bitte geben Sie eine positive Anzahl Gäste ein."
BUDGET_MESSAGE = "Bitte geben Sie ein Budget grösser als CHF 0.00 ein."
MAX_PREFERENCES = 4
PREFERENCES_MESSAGE = f"Bitte wählen Sie höchstens {MAX_PREFERENCES} Präferenzen aus."


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
    event_type = forms.ModelChoiceField(
        queryset=EventType.objects.all(),
        required=False,
        empty_label="Keine Angabe",
        label="Anlassart",
    )
    preferences = forms.ModelMultipleChoiceField(
        queryset=Preference.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Persönliche Präferenzen",
    )

    def clean_preferences(self):
        preferences = self.cleaned_data.get("preferences")
        if preferences and preferences.count() > MAX_PREFERENCES:
            raise forms.ValidationError(PREFERENCES_MESSAGE)
        return preferences
