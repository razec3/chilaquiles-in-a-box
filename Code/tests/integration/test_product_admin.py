"""Integration tests for the Product model and its Django admin registration.

CLAUDE.md business rules 6-8: unique article number, package quantity and
purchase price greater than zero. The Product table itself is standalone
for now (see plan.md) — not yet wired into the Working Skeleton flow.
"""

import pytest
from django.contrib.admin.sites import site
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.urls import reverse

from event_in_a_box.models import Product

pytestmark = [pytest.mark.integration, pytest.mark.django_db]


def _product(**overrides):
    defaults = {
        "article_number": "TG-1",
        "name": "Kalbsgeschnetzeltes",
        "package_quantity": "1",
        "measured_in": "KILOGRAM",
        "sold_in": "BAG",
        "purchase_price_per_package": "45.00",
    }
    defaults.update(overrides)
    return Product(**defaults)


def test_product_is_registered_in_admin():
    assert Product in site._registry


def test_admin_login_page_is_reachable(client):
    response = client.get(reverse("admin:login"))

    assert response.status_code == 200


def test_article_number_must_be_unique():
    _product().save()

    with pytest.raises(IntegrityError):
        _product(name="Duplicate").save()


def test_package_quantity_must_be_greater_than_zero():
    product = _product(package_quantity="0")

    with pytest.raises(ValidationError):
        product.full_clean()


def test_purchase_price_must_be_greater_than_zero():
    product = _product(purchase_price_per_package="0")

    with pytest.raises(ValidationError):
        product.full_clean()


def test_valid_product_saves_successfully():
    product = _product()
    product.full_clean()
    product.save()

    assert Product.objects.count() == 1
