"""Code (line) coverage tests for income_tax.py.

Run:
    coverage run -m pytest CodeCoverageTest_income_tax.py
    coverage report -m
"""
import pytest
from income_tax import taxable_income, tax_due, refund_status


# ---------- taxable_income ----------
def test_new_regime():
    assert taxable_income(1000000, "new", 0) == 925000


def test_negative_income_rejected():
    with pytest.raises(ValueError, match="invalid income"):
        taxable_income(-1, "new", 0)


def test_old_regime_investments_are_capped():
    # investments above 150000 count only as 150000 -> deduction 200000
    assert taxable_income(1000000, "old", 200000) == 800000


def test_unknown_regime_rejected():
    with pytest.raises(ValueError, match="unknown regime"):
        taxable_income(500000, "flat", 0)


def test_income_below_deduction_gives_zero():
    assert taxable_income(50000, "new", 0) == 0


# ---------- tax_due ----------
def test_below_exemption():
    assert tax_due(200000, 30) == 0


def test_negative_amount_rejected():
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-100, 30)


def test_super_senior_citizen():
    # exempt 500000 -> slab 100000 at 5%
    assert tax_due(600000, 85) == 5000


def test_senior_citizen():
    # exempt 300000 -> slab 200000 at 5%
    assert tax_due(500000, 65) == 10000


def test_regular_taxpayer_lower_slab():
    # exempt 250000 -> slab 250000 at 5%
    assert tax_due(500000, 30) == 12500


def test_regular_taxpayer_upper_slab():
    # slab 550000 -> 12500 + 20% of 300000
    assert tax_due(800000, 30) == 72500


# ---------- refund_status ----------
def test_refund_on_time():
    assert refund_status(60000, 50000, True) == "refund"


def test_refund_late():
    assert refund_status(60000, 50000, False) == "refund delayed"


def test_pay_balance_on_time():
    assert refund_status(40000, 50000, True) == "pay balance"


def test_pay_balance_late():
    assert refund_status(40000, 50000, False) == "pay balance with penalty"


def test_settled():
    assert refund_status(50000, 50000, True) == "settled"
