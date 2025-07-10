import copy
import pytest

from kepler.types.time import ScheduleTime, ScheduleTimeError

def test_init_valid_normal() -> None:
    time = ScheduleTime(10, 20)

    assert time.hour == 10
    assert time.minute == 20

def test_init_valid_midnight_1() -> None:
    time = ScheduleTime(0, 0)

    assert time.hour == 0
    assert time.minute == 0

def test_init_valid_midnight_2() -> None:
    time = ScheduleTime(24, 0)

    assert time.hour == 24
    assert time.minute == 0

def test_init_invalid_hour_negative() -> None:
    with pytest.raises(ScheduleTimeError):
        ScheduleTime(-1, 0)

def test_init_invalid_hour_positive() -> None:
    with pytest.raises(ScheduleTimeError):
        ScheduleTime(25, 0)

def test_init_invalid_minute_negative() -> None:
    with pytest.raises(ScheduleTimeError):
        ScheduleTime(10, -1)

def test_init_invalid_minute_positive() -> None:
    with pytest.raises(ScheduleTimeError):
        ScheduleTime(10, 60)

def test_init_invalid_hour_and_minute() -> None:
    with pytest.raises(ScheduleTimeError):
        ScheduleTime(24, 1)

def test_eq_none() -> None:
    assert not ScheduleTime(9, 0) == None

def test_eq_same() -> None:
    time = ScheduleTime(9, 0)
    assert time == time

def test_eq_equals() -> None:
    assert ScheduleTime(9, 0) == ScheduleTime(9, 0)

def test_eq_different_hour() -> None:
    time1 = ScheduleTime(9, 0)
    time2 = ScheduleTime(10, 0)

    assert time1 != time2

def test_eq_different_minute() -> None:
    time1 = ScheduleTime(9, 0)
    time2 = ScheduleTime(9, 1)

    assert time1 != time2

def test_order_equals() -> None:
    assert not ScheduleTime(12, 0) < ScheduleTime(12, 0)
    assert ScheduleTime(12, 0) <= ScheduleTime(12, 0)
    assert ScheduleTime(12, 0) >= ScheduleTime(12, 0)
    assert not ScheduleTime(12, 0) > ScheduleTime(12, 0)

def test_order_different_hour() -> None:
    assert ScheduleTime(12, 0) < ScheduleTime(13, 0)
    assert ScheduleTime(12, 0) <= ScheduleTime(13, 0)
    assert not ScheduleTime(12, 0) >= ScheduleTime(13, 0)
    assert not ScheduleTime(12, 0) > ScheduleTime(13, 0)

def test_order_different_minute() -> None:
    assert ScheduleTime(12, 0) < ScheduleTime(12, 10)
    assert ScheduleTime(12, 0) <= ScheduleTime(12, 10)
    assert not ScheduleTime(12, 0) >= ScheduleTime(12, 10)
    assert not ScheduleTime(12, 0) > ScheduleTime(12, 10)

def test_order_different_hour_and_minute() -> None:
    assert ScheduleTime(12, 59) < ScheduleTime(13, 0)
    assert ScheduleTime(12, 59) <= ScheduleTime(13, 0)
    assert not ScheduleTime(12, 59) >= ScheduleTime(13, 0)
    assert not ScheduleTime(12, 59) > ScheduleTime(13, 0)

def test_copy() -> None:
    original_time = ScheduleTime(9, 0)
    copied_time = copy.copy(original_time)

    assert copied_time is original_time

def test_hash_same() -> None:
    time = ScheduleTime(9, 0)
    assert hash(time) == hash(time)

def test_hash_equals() -> None:
    assert hash(ScheduleTime(9, 0)) == hash(ScheduleTime(9, 0))

def test_hash_different_hour() -> None:
    time1 = ScheduleTime(9, 0)
    time2 = ScheduleTime(10, 0)

    assert hash(time1) != hash(time2)

def test_hash_different_minute() -> None:
    time1 = ScheduleTime(9, 0)
    time2 = ScheduleTime(9, 1)

    assert hash(time1) != hash(time2)

def test_str() -> None:
    assert str(ScheduleTime(9, 5)) == '09:05'

def test_repr() -> None:
    assert repr(ScheduleTime(9, 5)) == 'ScheduleTime(hour=9, minute=5)'

def test_parse_valid() -> None:
    assert ScheduleTime.parse('14:00') == ScheduleTime(14, 0)

def test_parse_invalid_structure() -> None:
    with pytest.raises(ScheduleTimeError):
        ScheduleTime.parse('14:000')

def test_parse_invalid_content() -> None:
    with pytest.raises(ScheduleTimeError):
        ScheduleTime.parse('24:01')
