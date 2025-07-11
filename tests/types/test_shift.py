import copy
import pytest

from kepler.types.shift import Shift, ShiftError, ShiftType
from kepler.types.time import ScheduleTime
from kepler.types.timeslot import Timeslot
from kepler.types.weekday import Weekday

def test_init_no_timeslots() -> None:
    shift_timeslots: set[Timeslot] = set()
    shift = Shift(ShiftType.TP, 5, 50, shift_timeslots)

    assert shift.type == ShiftType.TP
    assert shift.number == 5
    assert shift.capacity == 50
    assert shift.name == 'TP5'
    assert shift.timeslots == shift_timeslots
    assert shift.timeslots is not shift_timeslots

def test_init_single_timeslot() -> None:
    timeslot = Timeslot(Weekday.FRIDAY, ScheduleTime(10, 0), ScheduleTime(12, 0))
    shift_timeslots = {timeslot}
    shift = Shift(ShiftType.TP, 5, 50, shift_timeslots)

    assert shift.type == ShiftType.TP
    assert shift.number == 5
    assert shift.capacity == 50
    assert shift.name == 'TP5'
    assert shift.timeslots == shift_timeslots
    assert shift.timeslots is not shift_timeslots
    assert next(iter(shift.timeslots)) is timeslot

def test_init_multiple_compatible_timeslots() -> None:
    timeslot1 = Timeslot(Weekday.MONDAY, ScheduleTime(10, 0), ScheduleTime(12, 0))
    timeslot2 = Timeslot(Weekday.FRIDAY, ScheduleTime(10, 0), ScheduleTime(12, 0))
    shift_timeslots = {timeslot1, timeslot2}
    shift = Shift(ShiftType.TP, 5, 50, shift_timeslots)

    assert shift.type == ShiftType.TP
    assert shift.number == 5
    assert shift.capacity == 50
    assert shift.name == 'TP5'
    assert shift.timeslots == shift_timeslots
    assert shift.timeslots is not shift_timeslots
    assert next(iter(shift.timeslots)) is timeslot1 or next(iter(shift.timeslots)) is timeslot2

def test_init_non_positive_number() -> None:
    with pytest.raises(ShiftError):
        Shift(ShiftType.TP, -5, 50, [])

def test_init_non_positive_capacity() -> None:
    with pytest.raises(ShiftError):
        Shift(ShiftType.TP, 5, 0, [])

def test_init_multiple_incompatible_timeslots() -> None:
    timeslot1 = Timeslot(Weekday.TUESDAY, ScheduleTime(10, 0), ScheduleTime(12, 0))
    timeslot2 = Timeslot(Weekday.TUESDAY, ScheduleTime(11, 0), ScheduleTime(13, 0))

    with pytest.raises(ShiftError):
        Shift(ShiftType.TP, 5, 50, [timeslot1, timeslot2])

def test_overlaps_shift_false() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(15, 0), ScheduleTime(16, 0))
    timeslot2 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(16, 0), ScheduleTime(17, 0))
    timeslot3 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(10, 0), ScheduleTime(12, 0))

    shift1 = Shift(ShiftType.PL, 1, 30, [timeslot1, timeslot2])
    shift2 = Shift(ShiftType.PL, 2, 30, [timeslot3])

    assert not shift1.overlaps(shift2)
    assert not shift2.overlaps(shift1)

def test_overlaps_shift_true() -> None:
    timeslot1 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(15, 0), ScheduleTime(16, 0))
    timeslot2 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(16, 0), ScheduleTime(17, 0))
    timeslot3 = Timeslot(Weekday.WEDNESDAY, ScheduleTime(15, 30), ScheduleTime(17, 30))

    shift1 = Shift(ShiftType.PL, 1, 30, [timeslot1, timeslot2])
    shift2 = Shift(ShiftType.PL, 2, 30, [timeslot3])

    assert shift1.overlaps(shift2)
    assert shift2.overlaps(shift1)

def test_eq_none() -> None:
    assert Shift(ShiftType.T, 1, 130, []) != None

def test_eq_same() -> None:
    shift = Shift(ShiftType.T, 1, 130, [])
    assert shift == shift

def test_eq_equals() -> None:
    shift1 = Shift(ShiftType.T, 1, 130, [])
    shift2 = Shift(ShiftType.T, 1, 130, [])

    assert shift1 == shift2

def test_eq_different_type() -> None:
    shift1 = Shift(ShiftType.T, 1, 130, [])
    shift2 = Shift(ShiftType.TP, 1, 130, [])

    assert shift1 != shift2

def test_eq_different_number() -> None:
    shift1 = Shift(ShiftType.T, 1, 130, [])
    shift2 = Shift(ShiftType.T, 2, 130, [])

    assert shift1 != shift2

def test_eq_different_capacity() -> None:
    shift1 = Shift(ShiftType.T, 1, 130, [])
    shift2 = Shift(ShiftType.T, 1, 150, [])

    assert shift1 == shift2 # NOTE: comparison only checks type and number

def test_eq_different_timeslots() -> None:
    timeslot = Timeslot(Weekday.THURSDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))

    shift1 = Shift(ShiftType.T, 1, 130, [])
    shift2 = Shift(ShiftType.T, 1, 130, [timeslot])

    assert shift1 == shift2 # NOTE: comparison only checks type and number

def test_order_equals() -> None:
    shift = Shift(ShiftType.TP, 2, 40, [])

    assert not shift < shift
    assert shift <= shift
    assert shift >= shift
    assert not shift > shift

def test_order_different_type() -> None:
    shift1 = Shift(ShiftType.T, 1, 40, [])
    shift2 = Shift(ShiftType.TP, 1, 40, [])

    assert shift1 < shift2
    assert shift1 <= shift2
    assert not shift1 >= shift2
    assert not shift1 > shift2

def test_order_different_number() -> None:
    shift1 = Shift(ShiftType.T, 1, 40, [])
    shift2 = Shift(ShiftType.T, 2, 40, [])

    assert shift1 < shift2
    assert shift1 <= shift2
    assert not shift1 >= shift2
    assert not shift1 > shift2

def test_copy() -> None:
    original_shift = Shift(ShiftType.OT, 3, 40, [])
    copied_shift = copy.copy(original_shift)

    assert copied_shift is original_shift

def test_hash_same() -> None:
    shift = Shift(ShiftType.PL, 6, 35, [])
    assert hash(shift) == hash(shift)

def test_hash_equals() -> None:
    shift1 = Shift(ShiftType.PL, 6, 35, [])
    shift2 = Shift(ShiftType.PL, 6, 35, [])

    assert hash(shift1) == hash(shift2)

def test_hash_different_type() -> None:
    shift1 = Shift(ShiftType.PL, 6, 35, [])
    shift2 = Shift(ShiftType.TP, 6, 35, [])

    assert hash(shift1) != hash(shift2)

def test_hash_different_number() -> None:
    shift1 = Shift(ShiftType.PL, 6, 35, [])
    shift2 = Shift(ShiftType.PL, 5, 35, [])

    assert hash(shift1) != hash(shift2)

def test_hash_different_capacity() -> None:
    shift1 = Shift(ShiftType.PL, 6, 35, [])
    shift2 = Shift(ShiftType.PL, 6, 30, [])

    assert hash(shift1) == hash(shift2) # NOTE: only type and number influence the hash

def test_hash_different_timeslots() -> None:
    timeslot = Timeslot(Weekday.MONDAY, ScheduleTime(16, 0), ScheduleTime(18, 0))

    shift1 = Shift(ShiftType.PL, 1, 35, [])
    shift2 = Shift(ShiftType.PL, 1, 35, [timeslot])

    assert hash(shift1) == hash(shift2) # NOTE: only type and number influence the hash

def test_repr() -> None:
    timeslot1 = Timeslot(Weekday.THURSDAY, ScheduleTime(14, 0), ScheduleTime(16, 0))
    timeslot2 = Timeslot(Weekday.MONDAY, ScheduleTime(14, 0), ScheduleTime(16, 0))
    shift = Shift(ShiftType.PL, 3, 28, [timeslot1, timeslot2])

    assert repr(shift) == (
        'Shift('
        'type_=ShiftType.PL, '
        'number=3, '
        'capacity=28, '
        f'timeslots=[{timeslot2}, {timeslot1}])'
    )
