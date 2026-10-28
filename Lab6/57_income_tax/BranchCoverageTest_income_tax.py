"""Branch coverage tests for income_tax.py.

Extends the code coverage tests so that every if/elif/else decision is
taken both ways, and adds boundary values.

Run:
    coverage run --branch -m pytest BranchCoverageTest_income_tax.py
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


# ---------- extra cases for branch coverage ----------
def test_old_regime_investments_below_cap():
    # investments <= 150000 are used as they are -> deduction 50000 + 100000
    assert taxable_income(1000000, "old", 100000) == 850000


def test_old_regime_investments_exactly_at_cap():
    # 150000 is not "greater than" the cap, so no capping happens
    assert taxable_income(1000000, "old", 150000) == 800000


def test_old_regime_income_below_deduction_gives_zero():
    # deduction is 50000 + 100000 = 150000, income is lower
    assert taxable_income(100000, "old", 100000) == 0


def test_zero_income_is_valid():
    assert taxable_income(0, "new", 0) == 0


def test_income_equal_to_deduction_gives_zero():
    assert taxable_income(75000, "new", 0) == 0


# ---------- tax_due boundaries ----------
def test_zero_taxable_amount():
    assert tax_due(0, 30) == 0


def test_exactly_at_exemption_limit_regular():
    assert tax_due(250000, 30) == 0


def test_just_above_exemption_limit_regular():
    assert tax_due(250001, 30) == 0  # 1 * 5 // 100 rounds down to 0


def test_age_59_is_regular():
    assert tax_due(300001, 59) == 2500


def test_age_60_is_senior():
    assert tax_due(300000, 60) == 0
    assert tax_due(400000, 60) == 5000


def test_age_79_is_senior():
    assert tax_due(500000, 79) == 10000


def test_age_80_is_super_senior():
    assert tax_due(500000, 80) == 0


def test_slab_boundary_exactly_250000():
    # slab is exactly 250000 -> still the 5% band
    assert tax_due(500000, 30) == 12500


def test_slab_boundary_just_above_250000():
    # slab 250001 -> 12500 + 20% of 1 (= 0)
    assert tax_due(500001, 30) == 12500
    assert tax_due(500005, 30) == 12501


def test_upper_slab_for_senior_and_super_senior():
    assert tax_due(800000, 65) == 12500 + (500000 - 250000) * 20 // 100
    assert tax_due(1000000, 85) == 12500 + (500000 - 250000) * 20 // 100


# ---------- refund_status: both outcomes of every decision ----------
def test_zero_paid_nothing_due_is_settled():
    assert refund_status(0, 0, False) == "settled"


def test_settled_does_not_depend_on_filing_date():
    assert refund_status(50000, 50000, False) == "settled"
