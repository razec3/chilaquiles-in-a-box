from django import template

register = template.Library()

_UNIT_LABELS = {
    "PIECE": "Stk.",
    "GRAM": "g",
    "KILOGRAM": "kg",
    "MILLILITRE": "ml",
    "LITRE": "L",
}

_PACKAGE_LABELS = {
    "TUBE": "Tube",
    "BOTTLE": "Flasche",
    "BAG": "Beutel",
    "BOX": "Karton",
    "CAN": "Dose",
    "PACKAGE": "Packung",
    "PIECE": "Stück",
}


@register.filter
def unit_label(measurement_unit):
    value = getattr(measurement_unit, "value", measurement_unit)
    return _UNIT_LABELS.get(value, value)


@register.filter
def package_label(package_type):
    value = getattr(package_type, "value", package_type)
    return _PACKAGE_LABELS.get(value, value)
