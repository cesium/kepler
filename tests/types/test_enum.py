import pytest

from kepler.types.enum import SortedEnum

class Letters(SortedEnum):
    A = 'A'
    B = 'B'
    C = 'C'

class Numbers(SortedEnum):
    ONE = 1
    TWO = 2
    THREE = 3

def test_eq_none() -> None:
    assert not Letters.A == None

def test_eq_same() -> None:
    assert Letters.A == Letters.A

def test_eq_equals() -> None:
    assert Letters.A == Letters('A')

def test_eq_different() -> None:
    assert Letters.A != Letters.B # type: ignore

def test_eq_different_types() -> None:
    class Letters2(SortedEnum):
        A = 'A'

    assert not Letters.A == Letters2.A # type: ignore

def test_order_equals() -> None:
    assert not Letters.A < Letters.A
    assert Letters.A <= Letters.A
    assert Letters.A >= Letters.A
    assert not Letters.A > Letters.A

def test_order_different() -> None:
    assert Numbers.TWO < Numbers.THREE
    assert Numbers.TWO <= Numbers.THREE
    assert not Numbers.TWO >= Numbers.THREE
    assert not Numbers.TWO > Numbers.THREE

def test_order_type_error() -> None:
    with pytest.raises(TypeError):
        Numbers.TWO < Letters.B

def test_repr() -> None:
    assert repr(Letters.A) == 'Letters.A'
    assert repr(Numbers.ONE) == 'Numbers.ONE'

def test_str() -> None:
    assert str(Letters.A) == 'A'
    assert str(Numbers.ONE) == '1'
