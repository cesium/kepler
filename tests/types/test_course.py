import copy
import pytest

from kepler.types.course import Course, CourseError
from kepler.types.shift import Shift, ShiftType

def test_init_no_shifts() -> None:
    course = Course('J301N1', 1, [])

    assert course.id == 'J301N1'
    assert course.year == 1
    assert course.shifts == {}

def test_init_compatible_shifts() -> None:
    shift = Shift(ShiftType.T, 1, 60, [])
    course = Course('J301N1', 1, [shift])

    assert course.id == 'J301N1'
    assert course.year == 1
    assert course.shifts == {ShiftType.T: {1: shift}}
    assert course.shifts[ShiftType.T][1] is shift

def test_init_non_positive_year() -> None:
    with pytest.raises(CourseError):
        Course('J301N1', 0, [])

def test_init_incompatible_shifts() -> None:
    shift1 = Shift(ShiftType.T, 1, 60, [])
    shift2 = Shift(ShiftType.T, 1, 80, [])

    with pytest.raises(CourseError):
        Course('J301N1', 1, [shift1, shift2])

def test_eq_none() -> None:
    assert Course('J302N1', 2, []) != None

def test_eq_same() -> None:
    course = Course('J302N1', 2, [])
    assert course == course

def test_eq_equals() -> None:
    course1 = Course('J302N1', 2, [])
    course2 = Course('J302N1', 2, [])

    assert course1 == course2

def test_eq_different_id() -> None:
    course1 = Course('J304N1', 2, [])
    course2 = Course('J304N2', 2, [])

    assert course1 != course2

def test_eq_different_year() -> None:
    course1 = Course('J304N1', 2, [])
    course2 = Course('J304N1', 3, [])

    assert course1 == course2 # NOTE: comparison only checks id

def test_eq_different_shifts() -> None:
    course1 = Course('J304N1', 2, [])
    course2 = Course('J304N1', 2, [Shift(ShiftType.T, 1, 120, [])])

    assert course1 == course2 # NOTE: comparison only checks id

def test_order_equals() -> None:
    course = Course('J302N1', 2, [])

    assert not course < course
    assert course <= course
    assert course >= course
    assert not course > course

def test_order_different_id() -> None:
    course1 = Course('J302N1', 2, [])
    course2 = Course('J303N1', 2, [])

    assert course1 < course2
    assert course1 <= course2
    assert not course1 >= course2
    assert not course1 > course2

def test_copy() -> None:
    original_course = Course('J305N4', 3, [Shift(ShiftType.T, 1, 120, [])])
    copied_course = copy.copy(original_course)

    assert copied_course is original_course

def test_hash_same() -> None:
    course = Course('J303N5', 2, [])
    assert hash(course) == hash(course)

def test_hash_equals() -> None:
    course1 = Course('J303N5', 2, [])
    course2 = Course('J303N5', 2, [])

    assert hash(course1) == hash(course2)

def test_hash_different_id() -> None:
    course1 = Course('J303N5', 2, [])
    course2 = Course('J303N6', 2, [])

    assert hash(course1) != hash(course2)

def test_hash_different_year() -> None:
    course1 = Course('J303N5', 2, [])
    course2 = Course('J303N5', 3, [])

    assert hash(course1) == hash(course2) # NOTE: only id influences the hash

def test_hash_different_shifts() -> None:
    course1 = Course('J303N5', 2, [])
    course2 = Course('J303N5', 2, [Shift(ShiftType.T, 1, 120, [])])

    assert hash(course1) == hash(course2) # NOTE: only id influences the hash

def test_repr() -> None:
    shift1 = Shift(ShiftType.TP, 1, 120, [])
    shift2 = Shift(ShiftType.T, 1, 40, [])
    course = Course('J303N5', 2, [shift1, shift2])

    assert repr(course) == f'Course(id_=\'J303N5\', year=2, shifts=[{shift2!r}, {shift1!r}])'
