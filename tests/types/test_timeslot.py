import copy
import pytest

from kepler.types.time import ScheduleTime
from kepler.types.timeslot import TimeslotError, Timeslot
from kepler.types.weekday import Weekday

def test_init_valid() -> None:
    timeslot = Timeslot(Weekday.THURSDAY, ScheduleTime(14, 0), ScheduleTime(16, 0))

    assert timeslot.day == Weekday.THURSDAY
    assert timeslot.start == ScheduleTime(14, 0)
    assert timeslot.end == ScheduleTime(16, 0)

def test_init_invalid_start_after_end() -> None:
    with pytest.raises(TimeslotError):
        Timeslot(Weekday.THURSDAY, ScheduleTime(16, 0), ScheduleTime(14, 0))

def test_init_invalid_start_equals_end() -> None:
    with pytest.raises(TimeslotError):
        Timeslot(Weekday.THURSDAY, ScheduleTime(14, 0), ScheduleTime(14, 0))

def test_overlaps_no_overlap() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(9, 0), ScheduleTime(11, 0))
    timeslot2 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(14, 0), ScheduleTime(16, 0))

    assert not timeslot1.overlaps(timeslot2)
    assert not timeslot2.overlaps(timeslot1)

def test_overlaps_different_day() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(9, 0), ScheduleTime(11, 0))
    timeslot2 = Timeslot(Weekday.TUESDAY, ScheduleTime(10, 0), ScheduleTime(12, 0))

    assert not timeslot1.overlaps(timeslot2)
    assert not timeslot2.overlaps(timeslot1)

def test_overlaps_sequence() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(9, 0), ScheduleTime(11, 0))
    timeslot2 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(11, 0), ScheduleTime(13, 0))

    assert not timeslot1.overlaps(timeslot2)
    assert not timeslot2.overlaps(timeslot1)

def test_overlaps_inside() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(9, 0), ScheduleTime(11, 0))
    timeslot2 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(9, 30), ScheduleTime(10, 30))

    assert timeslot1.overlaps(timeslot2)
    assert timeslot2.overlaps(timeslot1)

def test_overlaps_partial_overlap() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(9, 0), ScheduleTime(11, 0))
    timeslot2 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(10, 0), ScheduleTime(12, 0))

    assert timeslot1.overlaps(timeslot2)
    assert timeslot2.overlaps(timeslot1)

def test_eq_none() -> None:
    assert Timeslot(Weekday.MONDAY, ScheduleTime(11, 0), ScheduleTime(13, 0)) != None

def test_eq_same() -> None:
    timeslot = Timeslot(Weekday.MONDAY, ScheduleTime(11, 0), ScheduleTime(13, 0))
    assert timeslot == timeslot

def test_eq_equals() -> None:
    timeslot1 = Timeslot(Weekday.MONDAY, ScheduleTime(11, 0), ScheduleTime(13, 0))
    timeslot2 = Timeslot(Weekday.MONDAY, ScheduleTime(11, 0), ScheduleTime(13, 0))

    assert timeslot1 == timeslot2

def test_eq_different_day() -> None:
    timeslot1 = Timeslot(Weekday.MONDAY, ScheduleTime(11, 0), ScheduleTime(13, 0))
    timeslot2 = Timeslot(Weekday.FRIDAY, ScheduleTime(11, 0), ScheduleTime(13, 0))

    assert timeslot1 != timeslot2

def test_eq_different_start() -> None:
    timeslot1 = Timeslot(Weekday.MONDAY, ScheduleTime(11, 0), ScheduleTime(13, 0))
    timeslot2 = Timeslot(Weekday.MONDAY, ScheduleTime(11, 30), ScheduleTime(13, 0))

    assert timeslot1 != timeslot2

def test_eq_different_end() -> None:
    timeslot1 = Timeslot(Weekday.MONDAY, ScheduleTime(11, 0), ScheduleTime(13, 0))
    timeslot2 = Timeslot(Weekday.MONDAY, ScheduleTime(11, 0), ScheduleTime(12, 0))

    assert timeslot1 != timeslot2

def test_order_equals() -> None:
    timeslot = Timeslot(Weekday.WEDNESDAY, ScheduleTime(13, 0), ScheduleTime(15, 0))

    assert not timeslot < timeslot
    assert timeslot <= timeslot
    assert timeslot >= timeslot
    assert not timeslot > timeslot

def test_order_different_day() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(13, 0), ScheduleTime(15, 0))
    timeslot2 = Timeslot(Weekday.FRIDAY, ScheduleTime(13, 0), ScheduleTime(15, 0))

    assert timeslot1 < timeslot2
    assert timeslot1 <= timeslot2
    assert not timeslot1 >= timeslot2
    assert not timeslot1 > timeslot2

def test_order_different_start() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(13, 0), ScheduleTime(15, 0))
    timeslot2 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(14, 0), ScheduleTime(15, 0))

    assert timeslot1 < timeslot2
    assert timeslot1 <= timeslot2
    assert not timeslot1 >= timeslot2
    assert not timeslot1 > timeslot2

def test_order_different_end() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(13, 0), ScheduleTime(15, 0))
    timeslot2 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(13, 0), ScheduleTime(14, 0))

    assert not timeslot1 < timeslot2
    assert not timeslot1 <= timeslot2
    assert timeslot1 >= timeslot2
    assert timeslot1 > timeslot2

def test_copy() -> None:
    original_timeslot = Timeslot(Weekday.TUESDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))
    copied_timeslot = copy.copy(original_timeslot)

    assert copied_timeslot is original_timeslot

def test_hash_same() -> None:
    timeslot = Timeslot(Weekday.THURSDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))
    assert hash(timeslot) == hash(timeslot)

def test_hash_equals() -> None:
    timeslot1 = Timeslot(Weekday.THURSDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))
    timeslot2 = Timeslot(Weekday.THURSDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))

    assert hash(timeslot1) == hash(timeslot2)

def test_hash_different_day() -> None:
    timeslot1 = Timeslot(Weekday.THURSDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))
    timeslot2 = Timeslot(Weekday.FRIDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))

    assert hash(timeslot1) != hash(timeslot2)

def test_hash_different_start() -> None:
    timeslot1 = Timeslot(Weekday.THURSDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))
    timeslot2 = Timeslot(Weekday.THURSDAY, ScheduleTime(16, 30), ScheduleTime(18, 0))

    assert hash(timeslot1) != hash(timeslot2)

def test_hash_different_end() -> None:
    timeslot1 = Timeslot(Weekday.THURSDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))
    timeslot2 = Timeslot(Weekday.THURSDAY, ScheduleTime(16, 0), ScheduleTime(17, 0))

    assert hash(timeslot1) != hash(timeslot2)

def test_repr() -> None:
    timeslot = Timeslot(Weekday.THURSDAY, ScheduleTime(14, 0), ScheduleTime(16, 0))

    assert repr(timeslot) == (
        'Timeslot('
        'day=Weekday.THURSDAY, '
        'start=ScheduleTime(hour=14, minute=0), '
        'end=ScheduleTime(hour=16, minute=0))'
    )
