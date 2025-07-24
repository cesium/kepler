import copy
import pytest

from kepler.types.course import Course
from kepler.types.schedule import Schedule, ScheduleError
from kepler.types.shift import Shift, ShiftType
from kepler.types.student import Student

def test_init_no_shifts() -> None:
    schedule = Schedule([])
    assert schedule.shifts == {}

def test_init_different_shift_types() -> None:
    shift = Shift(ShiftType.T, 1, 100, [])
    course1 = Course('J301N1', 1, [shift])
    course2 = Course('J301N2', 1, [shift])
    schedule = Schedule([(course1, shift), (course2, shift)])

    assert schedule.shifts == {
        ('J301N1', ShiftType.T): shift,
        ('J301N2', ShiftType.T): shift
    }

def test_init_repeated_shift_type() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.T, 2, 100, [])
    course = Course('J301N1', 1, [shift1, shift2])

    with pytest.raises(ScheduleError):
        Schedule([(course, shift1), (course, shift2)])

def test_init_shift_not_in_course_same_type() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.T, 2, 100, [])
    course = Course('J301N1', 1, [shift1])

    with pytest.raises(ScheduleError):
        Schedule([(course, shift2)])

def test_init_shift_not_in_course_different_types() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.TP, 1, 100, [])
    course = Course('J301N1', 1, [shift1])

    with pytest.raises(ScheduleError):
        Schedule([(course, shift2)])

def test_init_shift_not_in_course_not_same() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.T, 1, 150, [])
    course = Course('J301N1', 1, [shift1])

    with pytest.raises(ScheduleError):
        Schedule([(course, shift2)])

def test_init_courses_with_same_id() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.TP, 1, 100, [])
    course1 = Course('J301N1', 1, [shift1])
    course2 = Course('J301N1', 2, [shift2])

    with pytest.raises(ScheduleError):
        Schedule([(course1, shift1), (course2, shift2)])

def test_is_valid_for_student_true() -> None:
    shift = Shift(ShiftType.OT, 1, 30, [])
    course = Course('J302N2', 1, [shift])
    student = Student('A100', 1, [course], Schedule([]))

    assert Schedule([(course, shift)]).is_valid_for_student(student)

def test_is_valid_for_student_false() -> None:
    shift = Shift(ShiftType.OT, 1, 30, [])
    course = Course('J302N2', 1, [shift])
    student = Student('A100', 1, [], Schedule([]))

    assert not Schedule([(course, shift)]).is_valid_for_student(student)

def test_is_valid_for_student_courses_same_id() -> None:
    shift = Shift(ShiftType.OT, 1, 30, [])
    course1 = Course('J302N2', 1, [shift])
    course2 = Course('J302N2', 2, [shift])
    student = Student('A100', 1, [course1], Schedule([]))

    assert not Schedule([(course2, shift)]).is_valid_for_student(student)

def test_is_complete_for_student_true_empty() -> None:
    course = Course('J302N2', 1, [])
    student = Student('A100', 1, [course], Schedule([]))

    assert Schedule([]).is_complete_for_student(student)

def test_is_complete_for_student_true_multiple() -> None:
    shift1 = Shift(ShiftType.T, 1, 150, [])
    shift2 = Shift(ShiftType.OT, 1, 30, [])
    shift3 = Shift(ShiftType.OT, 2, 30, [])
    course = Course('J302N2', 1, [shift1, shift2, shift3])
    student = Student('A100', 1, [course], Schedule([]))

    assert Schedule([(course, shift1), (course, shift2)]).is_complete_for_student(student)

def test_is_complete_for_student_false() -> None:
    shift1 = Shift(ShiftType.T, 1, 150, [])
    shift2 = Shift(ShiftType.OT, 1, 30, [])
    course = Course('J302N2', 1, [shift1, shift2])
    student = Student('A100', 1, [course], Schedule([]))

    assert not Schedule([(course, shift1)]).is_complete_for_student(student)

def test_eq_none() -> None:
    assert Schedule([]) != None

def test_eq_same() -> None:
    schedule = Schedule([])
    assert schedule == schedule

def test_eq_equals() -> None:
    schedule1 = Schedule([])
    schedule2 = Schedule([])

    assert schedule1 == schedule2

def test_eq_different_shifts() -> None:
    shift = Shift(ShiftType.TP, 1, 40, [])
    course = Course('J303N6', 2, [shift])

    schedule1 = Schedule([(course, shift)])
    schedule2 = Schedule([])

    assert schedule1 != schedule2

def test_eq_same_shifts_different_order() -> None:
    shift = Shift(ShiftType.TP, 1, 40, [])
    course1 = Course('J303N6', 2, [shift])
    course2 = Course('J303N7', 2, [shift])

    schedule1 = Schedule([(course1, shift), (course2, shift)])
    schedule2 = Schedule([(course2, shift), (course1, shift)])

    assert schedule1 == schedule2

def test_copy() -> None:
    shift = Shift(ShiftType.PL, 2, 30, [])
    course = Course('J306N4', 3, [shift])

    original_schedule = Schedule([(course, shift)])
    copied_schedule = copy.copy(original_schedule)

    assert copied_schedule is original_schedule

def test_repr() -> None:
    shift = Shift(ShiftType.PL, 2, 30, [])
    course1 = Course('J304N6', 2, [shift])
    course2 = Course('J303N6', 2, [shift])
    schedule = Schedule([(course1, shift), (course2, shift)])

    assert repr(schedule) == \
        f'Schedule(shifts=[({course2!r}, {shift!r}), ({course1!r}, {shift!r})])'
