import copy
import pytest

from kepler.types.course import Course
from kepler.types.schedule import Schedule
from kepler.types.shift import Shift, ShiftType
from kepler.types.student import Student, StudentError

def test_init_empty() -> None:
    schedule = Schedule([])
    student = Student('A100', [], schedule)

    assert student.number == 'A100'
    assert student.enrollments == {}
    assert student.previous_schedule is schedule

def test_init_valid() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.TP, 1, 100, [])
    course = Course('J301N1', 1, [shift1, shift2])

    schedule = Schedule([(course, shift1), (course, shift2)])
    student = Student('A100', [course], schedule)

    assert student.number == 'A100'
    assert student.enrollments == {'J301N1': course}
    assert student.enrollments['J301N1'] is course
    assert student.previous_schedule is schedule

def test_init_repeated_course() -> None:
    course = Course('J301N1', 1, [])

    with pytest.raises(StudentError):
        Student('A100', [course, course], Schedule([]))

def test_init_invalid_schedule() -> None:
    shift = Shift(ShiftType.T, 1, 100, [])
    course = Course('J301N1', 1, [shift])

    with pytest.raises(StudentError):
        Student('A100', [], Schedule([(course, shift)]))

def test_mandatory_shift_types() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.PL, 1, 30, [])
    course1 = Course('J305N2', 1, [shift1, shift2])
    course2 = Course('J305N3', 1, [shift1])
    student = Student('A100', [course1, course2], Schedule([]))

    assert student.mandatory_shift_types == {
        ('J305N2', ShiftType.T),
        ('J305N2', ShiftType.PL),
        ('J305N3', ShiftType.T)
    }

def test_eq_none() -> None:
    assert Student('A100', [], Schedule([])) != None

def test_eq_same() -> None:
    student = Student('A100', [], Schedule([]))
    assert student == student

def test_eq_equals() -> None:
    student1 = Student('A100', [], Schedule([]))
    student2 = Student('A100', [], Schedule([]))
    assert student1 == student2

def test_eq_different_number() -> None:
    student1 = Student('A100', [], Schedule([]))
    student2 = Student('A200', [], Schedule([]))
    assert student1 != student2

def test_eq_different_courses() -> None:
    student1 = Student('A100', [], Schedule([]))
    student2 = Student('A100', [Course('J301N1', 1, [])], Schedule([]))
    assert student1 != student2

def test_eq_different_schedule() -> None:
    shift = Shift(ShiftType.T, 1, 100, [])
    course = Course('J301N1', 1, [shift])

    student1 = Student('A100', [course], Schedule([]))
    student2 = Student('A100', [course], Schedule([(course, shift)]))
    assert student1 != student2

def test_order_equals() -> None:
    student = Student('A100', [], Schedule([]))

    assert not student < student
    assert student <= student
    assert student >= student
    assert not student > student

def test_order_different_id() -> None:
    student1 = Student('A100', [], Schedule([]))
    student2 = Student('A200', [], Schedule([]))

    assert student1 < student2
    assert student1 <= student2
    assert not student1 >= student2
    assert not student1 > student2

def test_copy() -> None:
    original_student = Student('A100', [], Schedule([]))
    copied_student = copy.copy(original_student)

    assert copied_student is original_student

def test_hash_same() -> None:
    student = Student('A100', [], Schedule([]))
    assert hash(student) == hash(student)

def test_hash_equals() -> None:
    student1 = Student('A100', [], Schedule([]))
    student2 = Student('A100', [], Schedule([]))
    assert hash(student1) == hash(student2)

def test_hash_different_number() -> None:
    student1 = Student('A100', [], Schedule([]))
    student2 = Student('A200', [], Schedule([]))
    assert hash(student1) != hash(student2)

def test_hash_different_courses() -> None:
    student1 = Student('A100', [], Schedule([]))
    student2 = Student('A100', [Course('J301N1', 1, [])], Schedule([]))
    assert hash(student1) == hash(student2) # NOTE: only number influences the hash

def test_hash_different_schedule() -> None:
    shift = Shift(ShiftType.T, 1, 100, [])
    course = Course('J301N1', 1, [shift])

    student1 = Student('A100', [course], Schedule([]))
    student2 = Student('A100', [course], Schedule([(course, shift)]))
    assert hash(student1) == hash(student2) # NOTE: only number influences the hash

def test_repr() -> None:
    shift = Shift(ShiftType.T, 1, 100, [])
    course1 = Course('J301N2', 1, [shift])
    course2 = Course('J301N1', 1, [shift])
    schedule = Schedule([(course1, shift)])
    student = Student('A100', [course1, course2], schedule)

    assert repr(student) == (
        'Student('
        f'number=\'A100\', '
        f'enrollments=[{course2!r}, {course1!r}], '
        f'previous_schedule={schedule!r})'
    )
