import copy
import pytest

from kepler.types.course import Course
from kepler.types.problem import SchedulingProblem, SchedulingProblemError
from kepler.types.schedule import Schedule
from kepler.types.student import Student

def test_init_empty() -> None:
    problem = SchedulingProblem([], [])

    assert problem.courses == {}
    assert problem.students == {}

def test_init_valid_data() -> None:
    course = Course('J301N1', 1, [])
    student = Student('A100', [course], Schedule([]))
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
    student1 = Student('A100', [], Schedule([]))
    student2 = Student('A100', [], Schedule([]))

    with pytest.raises(SchedulingProblemError):
        SchedulingProblem([], [student1, student2])

def test_init_bad_course_reference() -> None:
    course = Course('J301N1', 1, [])
    student = Student('A100', [course], Schedule([]))

    with pytest.raises(SchedulingProblemError):
        SchedulingProblem([], [student])

def test_eq_none() -> None:
    assert SchedulingProblem([], []) != None

def test_eq_equals() -> None:
    course = Course('J301N1', 1, [])
    student = Student('A100', [course], Schedule([]))

    problem1 = SchedulingProblem([course], [student])
    problem2 = SchedulingProblem([course], [student])

    assert problem1 == problem2

def test_eq_same() -> None:
    course = Course('J301N1', 1, [])
    student = Student('A100', [course], Schedule([]))
    problem = SchedulingProblem([course], [student])

    assert problem == problem

def test_eq_different_courses() -> None:
    course = Course('J301N1', 1, [])
    student = Student('A100', [], Schedule([]))

    problem1 = SchedulingProblem([course], [student])
    problem2 = SchedulingProblem([], [student])

    assert problem1 != problem2

def test_eq_different_students() -> None:
    course = Course('J301N1', 1, [])
    student = Student('A100', [course], Schedule([]))

    problem1 = SchedulingProblem([course], [student])
    problem2 = SchedulingProblem([course], [])

    assert problem1 != problem2

def test_copy() -> None:
    original_problem = SchedulingProblem([], [])
    copied_problem = copy.copy(original_problem)

    assert copied_problem is original_problem

def test_repr() -> None:
    course1 = Course('J301N2', 1, [])
    course2 = Course('J301N1', 1, [])
    student1 = Student('A200', [course1], Schedule([]))
    student2 = Student('A100', [course2], Schedule([]))
    problem = SchedulingProblem([course1, course2], [student1, student2])

    assert repr(problem) == (
        'SchedulingProblem('
        f'courses=[{course2!r}, {course1!r}], '
        f'students=[{student2!r}, {student1!r}])'
    )
