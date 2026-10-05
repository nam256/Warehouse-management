import pytest

from app.services.ccp import evaluate_ccp1, evaluate_ccp2


@pytest.mark.parametrize(
    "c14,expected",
    [
        (None, "pending"),
        (13.02, "pass"),
        (14.39, "pass"),
        (13.5, "pass"),
        (12.0, "fail"),
        (15.0, "fail"),
    ],
)
def test_ccp1(c14, expected):
    assert evaluate_ccp1(c14) == expected


@pytest.mark.parametrize(
    "t_top,t_ca,expected",
    [
        (None, None, "pending"),
        (108, 99.5, "pass"),
        (107, 99.01, "pass"),
        (110, 100, "pass"),
        (106, 99.5, "fail"),
        (108, 98.5, "fail"),
        (108, None, "pending"),
    ],
)
def test_ccp2(t_top, t_ca, expected):
    assert evaluate_ccp2(t_top, t_ca) == expected
