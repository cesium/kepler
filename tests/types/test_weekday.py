from kepler.types.weekday import Weekday

def test_repr() -> None:
    assert repr(Weekday.WEDNESDAY) == 'Weekday.WEDNESDAY'

def test_str() -> None:
    assert str(Weekday.MONDAY) == 'Monday'
