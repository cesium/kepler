import copy
import pytest

from kepler.types.course import Course
from kepler.types.problem import SchedulingProblem, SchedulingProblemError
from kepler.types.shift import Shift, ShiftType
from kepler.types.schedule import Schedule
from kepler.types.student import Student

def test_init_empty() -> None:
    problem = SchedulingProblem([], [])

    assert problem.courses == {}
    assert problem.students == {}

def test_init_valid_data() -> None:
    course = Course('J301N1', 1, [])
    student = Student('A100', 2, [course], Schedule([]))
    problem = SchedulingProblem([course], [student])

    assert problem.courses == {'J301N1': course}
    assert problem.courses['J301N1'] is course
    assert problem.students == {'A100': student}
    assert problem.students['A100'] is student

def test_init_repeated_courses() -> None:
    course1 = Course('J301N1', 1, [])
    course2 = Course('J301N1', 1, [])

    with pytest.raises(SchedulingProblemError):
        SchedulingProblem([course1, course2], [])

def test_init_repeated_students() -> None:
    student1 = Student('A100', 2, [], Schedule([]))
    student2 = Student('A100', 2, [], Schedule([]))

    with pytest.raises(SchedulingProblemError):
        SchedulingProblem([], [student1, student2])

def test_init_bad_course_reference() -> None:
    course = Course('J301N1', 1, [])
    student = Student('A100', 2, [course], Schedule([]))

    with pytest.raises(SchedulingProblemError):
        SchedulingProblem([], [student])

def test_init_bad_course_reference_same_id() -> None:
    course1 = Course('J301N1', 1, [])
    course2 = Course('J301N1', 2, [])
    student = Student('A100', 2, [course1], Schedule([]))

    with pytest.raises(SchedulingProblemError):
        SchedulingProblem([course2], [student])

def test_list_possible_students_by_shift() -> None:
    shift1 = Shift(ShiftType.T, 1, 100, [])
    shift2 = Shift(ShiftType.T, 2, 100, [])
    shift3 = Shift(ShiftType.PL, 1, 30, [])
    shift4 = Shift(ShiftType.PL, 2, 30, [])
    course1 = Course('J305N1', 3, [shift1, shift2, shift3, shift4])

    shift5 = Shift(ShiftType.TP, 1, 50, [])
    course2 = Course('J305N2', 3, [shift5])

    student1 = Student('A100', 3, [course1], Schedule([(course1, shift3)]))
    student2 = Student('A200', 3, [course1], Schedule([]))

    problem = SchedulingProblem([course1, course2], [student1, student2])

    possible_students = problem.list_possible_students_by_shift()
    assert possible_students == {
        ('J305N1', ShiftType.T, 1): {student1, student2},
        ('J305N1', ShiftType.T, 2): {student1, student2},
        ('J305N1', ShiftType.PL, 1): {student1, student2},
        ('J305N1', ShiftType.PL, 2): {student2},
        ('J305N2', ShiftType.TP, 1): set(),
    }

def test_eq_none() -> None:
    assert SchedulingProblem([], []) != None

def test_eq_same() -> None:
    problem = SchedulingProblem([], [])
    assert problem == problem

def test_eq_equals() -> None:
    problem1 = SchedulingProblem([], [])
    problem2 = SchedulingProblem([], [])

    assert problem1 == problem2

def test_eq_different_courses() -> None:
    course = Course('J301N1', 1, [])

    problem1 = SchedulingProblem([course], [])
    problem2 = SchedulingProblem([], [])

    assert problem1 != problem2

def test_eq_different_courses_same_keys() -> None:
    course1 = Course('J301N1', 1, [])
    course2 = Course('J301N1', 2, [])

    problem1 = SchedulingProblem([course1], [])
    problem2 = SchedulingProblem([course2], [])

    assert problem1 == problem2 # NOTE: comparison does not check course contents

def test_eq_different_students() -> None:
    student = Student('A100', 2, [], Schedule([]))

    problem1 = SchedulingProblem([], [student])
    problem2 = SchedulingProblem([], [])

    assert problem1 != problem2

def test_eq_different_students_same_keys() -> None:
    student1 = Student('A100', 1, [], Schedule([]))
    student2 = Student('A100', 2, [], Schedule([]))

    problem1 = SchedulingProblem([], [student1])
    problem2 = SchedulingProblem([], [student2])

    assert problem1 == problem2 # NOTE: comparison does not check student contents

def test_copy() -> None:
    original_problem = SchedulingProblem([], [])
    copied_problem = copy.copy(original_problem)

    assert copied_problem is original_problem

def test_repr() -> None:
    course1 = Course('J301N2', 1, [])
    course2 = Course('J301N1', 1, [])
    student1 = Student('A200', 2, [course1], Schedule([]))
    student2 = Student('A100', 2, [course2], Schedule([]))
    problem = SchedulingProblem([course1, course2], [student1, student2])

    assert repr(problem) == (
        'SchedulingProblem('
        f'courses=[{course2!r}, {course1!r}], '
        f'students=[{student2!r}, {student1!r}])'
    )
