import pytest
from celery_uncovered.toyex.dummy import add, div


def test_add():
    assert add(12, 13) == 25
    assert add(1, 1) == 2


def test_div():
    assert div(12, 3) == 4
    x = 12
    with pytest.raises(ZeroDivisionError):
        div(x, 0)

