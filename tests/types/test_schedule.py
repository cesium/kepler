import copy
import pytest

from kepler.types.course import Course
from kepler.types.schedule import Schedule, ScheduleError
from kepler.types.shift import Shift, ShiftType

def test_init_no_shifts() -> None:
    schedule_shifts: list[tuple[Course, Shift]] = []
    schedule = Schedule(schedule_shifts)

    assert schedule.shifts == schedule_shifts
    assert schedule.shifts is not schedule_shifts

def test_init_different_shift_types() -> None:
    shift = Shift(ShiftType.T, 1, 100, [])
    course1 = Course('J301N1', 1, [shift])
    course2 = Course('J301N2', 1, [shift])

    schedule_shifts = [(course1, shift), (course2, shift)]
    schedule = Schedule(schedule_shifts)

    assert schedule.shifts == schedule_shifts
    assert schedule.shifts is not schedule_shifts
    assert schedule.shifts[0][0] is course1
    assert schedule.shifts[0][1] is shift

def test_init_repeated_shift_type() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.T, 2, 100, [])
    course = Course('J301N1', 1, [shift1, shift2])

    with pytest.raises(ScheduleError):
        schedule = Schedule([(course, shift1), (course, shift2)])

def test_init_shift_not_in_course_same_type() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.T, 2, 100, [])
    course = Course('J301N1', 1, [shift1])

    with pytest.raises(ScheduleError):
        schedule = Schedule([(course, shift2)])

def test_init_shift_not_in_course_different_types() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.TP, 1, 100, [])
    course = Course('J301N1', 1, [shift1])

    with pytest.raises(ScheduleError):
        schedule = Schedule([(course, shift2)])

def test_eq_none() -> None:
    assert Schedule([]) != None

def test_eq_equals() -> None:
    shift = Shift(ShiftType.TP, 1, 40, [])
    course = Course('J303N6', 2, [shift])

    schedule1 = Schedule([(course, shift)])
    schedule2 = Schedule([(course, shift)])
    assert schedule1 == schedule2

def test_eq_same() -> None:
    shift = Shift(ShiftType.TP, 1, 40, [])
    course = Course('J303N6', 2, [shift])
    schedule = Schedule([(course, shift)])

    assert schedule == schedule

def test_eq_different_shifts_length() -> None:
    shift = Shift(ShiftType.TP, 1, 40, [])
    course = Course('J303N6', 2, [shift])

    schedule1 = Schedule([(course, shift)])
    schedule2 = Schedule([])

    assert schedule1 != schedule2

def test_copy() -> None:
    shift = Shift(ShiftType.PL, 2, 30, [])
    course = Course('J306N4', 3, [shift])

    original_schedule = Schedule([(course, shift)])
    copied_schedule = copy.copy(original_schedule)

    assert copied_schedule is original_schedule

def test_repr() -> None:
    shift = Shift(ShiftType.PL, 2, 30, [])
    course = Course('J303N6', 2, [shift])
    schedule = Schedule([(course, shift)])

    assert repr(schedule) == f'Schedule(shifts=[({course!r}, {shift!r})])'
