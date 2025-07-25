import copy
import pytest

from kepler.types.course import Course
from kepler.types.problem import SchedulingProblem
from kepler.types.schedule import Schedule
from kepler.types.shift import Shift, ShiftType
from kepler.types.solution import SchedulingProblemSolution, SchedulingProblemSolutionError
from kepler.types.student import Student

def test_init_empty() -> None:
    problem = SchedulingProblem([], [])
    final_schedules: dict[str, Schedule] = {}
    solution = SchedulingProblemSolution(problem, final_schedules)

    assert solution.problem is problem
    assert solution.final_schedules == final_schedules
    assert solution.final_schedules is not final_schedules

def test_init_valid_data() -> None:
    shift = Shift(ShiftType.T, 1, 120, [])
    course = Course('J301N1', 1, [shift])
    student = Student('A100', 1, [course], Schedule([]))
    problem = SchedulingProblem([course], [student])
    schedule = Schedule([(course, shift)])
    final_schedules = {'A100': schedule}
    solution = SchedulingProblemSolution(problem, final_schedules)

    assert solution.problem is problem
    assert solution.final_schedules == final_schedules
    assert solution.final_schedules is not final_schedules
    assert solution.final_schedules['A100'] is schedule

def test_init_unknown_student() -> None:
    student = Student('A100', 1, [], Schedule([]))
    problem = SchedulingProblem([], [student])
    final_schedules = {'A200': Schedule([])}

    with pytest.raises(SchedulingProblemSolutionError):
        SchedulingProblemSolution(problem, final_schedules)

def test_init_missing_schedule() -> None:
    student = Student('A100', 1, [], Schedule([]))
    problem = SchedulingProblem([], [student])

    with pytest.raises(SchedulingProblemSolutionError):
        SchedulingProblemSolution(problem, {})

def test_init_invalid_schedule() -> None:
    shift = Shift(ShiftType.T, 1, 120, [])
    course = Course('J301N1', 1, [shift])
    student = Student('A100', 1, [], Schedule([]))
    problem = SchedulingProblem([course], [student])
    schedule = Schedule([(course, shift)])
    final_schedules = {'A100': schedule}

    with pytest.raises(SchedulingProblemSolutionError):
        SchedulingProblemSolution(problem, final_schedules)

def test_init_incomplete_schedule() -> None:
    shift = Shift(ShiftType.T, 1, 120, [])
    course = Course('J301N1', 1, [shift])
    student = Student('A100', 1, [course], Schedule([]))
    problem = SchedulingProblem([course], [student])
    schedule = Schedule([])
    final_schedules = {'A100': schedule}

    with pytest.raises(SchedulingProblemSolutionError):
        SchedulingProblemSolution(problem, final_schedules)

def test_eq_none() -> None:
    assert SchedulingProblemSolution(SchedulingProblem([], []), {}) != None

def test_eq_same() -> None:
    solution = SchedulingProblemSolution(SchedulingProblem([], []), {})
    assert solution == solution

def test_eq_equals() -> None:
    solution1 = SchedulingProblemSolution(SchedulingProblem([], []), {})
    solution2 = SchedulingProblemSolution(SchedulingProblem([], []), {})

    assert solution1 == solution2

def test_eq_different_problem() -> None:
    course = Course('J301N1', 1, [])

    solution1 = SchedulingProblemSolution(SchedulingProblem([course], []), {})
    solution2 = SchedulingProblemSolution(SchedulingProblem([], []), {})

    assert solution1 != solution2

def test_eq_different_final_schedules() -> None:
    shift1 = Shift(ShiftType.T, 1, 120, [])
    shift2 = Shift(ShiftType.T, 2, 120, [])
    course = Course('J301N1', 1, [shift1, shift2])

    student = Student('A100', 1, [course], Schedule([]))
    problem = SchedulingProblem([course], [student])

    schedule1 = Schedule([(course, shift1)])
    schedule2 = Schedule([(course, shift2)])

    solution1 = SchedulingProblemSolution(problem, {'A100': schedule1})
    solution2 = SchedulingProblemSolution(problem, {'A100': schedule2})

    assert solution1 != solution2

def test_copy() -> None:
    original_solution = SchedulingProblemSolution(SchedulingProblem([], []), {})
    copied_solution = copy.copy(original_solution)

    assert copied_solution is original_solution

def test_repr() -> None:
    student1 = Student('A200', 2, [], Schedule([]))
    student2 = Student('A100', 1, [], Schedule([]))
    problem = SchedulingProblem([], [student1, student2])
    schedule = Schedule([])
    solution = SchedulingProblemSolution(problem, {'A200': schedule, 'A100': schedule})

    assert repr(solution) == (
        'SchedulingProblemSolution('
        f'problem={problem!r}, '
        f'final_schedules={{\'A100\': {schedule!r}, \'A200\': {schedule!r}}})'
    )
