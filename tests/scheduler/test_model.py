import pulp
import pytest

from kepler.scheduler import config
from kepler.scheduler.model import SchedulingProblemModel, SchedulingProblemModelError
from kepler.types import *

def __decompose_model(model: SchedulingProblemModel) -> tuple[str, list[str]]:
    pulp_model = model._SchedulingProblemModel__model # type: ignore

    objective = str(pulp_model.objective)
    constraints = sorted(str(constraint) for constraint in pulp_model.constraints.values())
    return objective, constraints

def test_empty() -> None:
    problem = SchedulingProblem([], [])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == '0.0'
    assert constraints == []

    solution = model.solve()
    assert solution.problem is problem
    assert solution.final_schedules == {}

def test_single_student_no_shifts() -> None:
    student = Student('A100', 1, [], Schedule([]))

    problem = SchedulingProblem([], [student])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == '0.0'
    assert constraints == []

    solution = model.solve()
    assert solution.problem is problem
    assert solution.final_schedules == {
        'A100': Schedule([])
    }

def test_single_student_single_shift() -> None:
    shift = Shift(ShiftType.TP, 1, 10, [])
    course = Course('J301N1', 1, [shift])

    student = Student('A100', 1, [course], Schedule([]))

    problem = SchedulingProblem([course], [student])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == '0.0'
    assert constraints == []

    solution = model.solve()
    assert solution.problem is problem
    assert solution.final_schedules == {
        'A100': Schedule([(course, shift)])
    }

def test_single_student_multiple_shifts() -> None:
    shift1 = Shift(ShiftType.TP, 1, 10, [])
    shift2 = Shift(ShiftType.TP, 2, 10, [])
    course = Course('J301N1', 1, [shift1, shift2])

    student = Student('A100', 1, [course], Schedule([]))

    problem = SchedulingProblem([course], [student])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == 'J301N1_TP1_OVERCROWD + J301N1_TP2_OVERCROWD'
    assert constraints == [
        '-A100_J301N1_TP1 + J301N1_TP1_OVERCROWD >= -10',
        '-A100_J301N1_TP2 + J301N1_TP2_OVERCROWD >= -10',
        'A100_J301N1_TP1 + A100_J301N1_TP2 = 1'
    ]

    solution = model.solve()
    assert solution.problem is problem
    assert solution.final_schedules in [
        {
            'A100': Schedule([(course, shift1)])
        },
        {
            'A100': Schedule([(course, shift2)])
        },
    ]

def test_existing_schedule() -> None:
    shift1 = Shift(ShiftType.TP, 1, 10, [])
    shift2 = Shift(ShiftType.TP, 2, 10, [])
    course = Course('J301N1', 1, [shift1, shift2])

    student1 = Student('A100', 1, [course], Schedule([(course, shift1)]))
    student2 = Student('A200', 1, [course], Schedule([]))

    problem = SchedulingProblem([course], [student1, student2])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == 'J301N1_TP1_OVERCROWD + J301N1_TP2_OVERCROWD'
    assert constraints == [
        '-A200_J301N1_TP1 + J301N1_TP1_OVERCROWD >= -9',
        '-A200_J301N1_TP2 + J301N1_TP2_OVERCROWD >= -10',
        'A200_J301N1_TP1 + A200_J301N1_TP2 = 1'
    ]

def test_no_overlap() -> None:
    timeslot = Timeslot(Weekday.MONDAY, ScheduleTime(9, 0), ScheduleTime(11, 0))
    shift1 = Shift(ShiftType.TP, 1, 10, [timeslot])
    shift2 = Shift(ShiftType.TP, 2, 10, [timeslot])
    course = Course('J301N1', 1, [shift1, shift2])

    student = Student('A100', 1, [course], Schedule([]))

    problem = SchedulingProblem([course], [student])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == 'J301N1_TP1_OVERCROWD + J301N1_TP2_OVERCROWD'
    assert constraints == [
        '-A100_J301N1_TP1 + J301N1_TP1_OVERCROWD >= -10',
        '-A100_J301N1_TP2 + J301N1_TP2_OVERCROWD >= -10',
        'A100_J301N1_TP1 + A100_J301N1_TP2 = 1'
    ]

def test_inevitable_overlap() -> None:
    timeslot = Timeslot(Weekday.MONDAY, ScheduleTime(9, 0), ScheduleTime(11, 0))
    shift1 = Shift(ShiftType.T, 1, 10, [timeslot])
    shift2 = Shift(ShiftType.TP, 1, 10, [timeslot])
    course = Course('J301N1', 1, [shift1, shift2])

    student = Student('A100', 1, [course], Schedule([]))

    problem = SchedulingProblem([course], [student])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == '0.0'
    assert constraints == []

def test_regular_overlap() -> None:
    timeslot = Timeslot(Weekday.MONDAY, ScheduleTime(9, 0), ScheduleTime(11, 0))
    shift1 = Shift(ShiftType.T, 1, 10, [timeslot])
    shift2 = Shift(ShiftType.T, 2, 10, [])
    shift3 = Shift(ShiftType.TP, 1, 10, [timeslot])
    shift4 = Shift(ShiftType.TP, 2, 10, [])
    course = Course('J301N1', 1, [shift1, shift2, shift3, shift4])

    student = Student('A100', 1, [course], Schedule([]))

    problem = SchedulingProblem([course], [student])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == (
        '10000.0*A100_J301N1_T1_J301N1_TP1 + '
        '0.1*J301N1_T1_OVERCROWD + '
        '0.1*J301N1_T2_OVERCROWD + '
        'J301N1_TP1_OVERCROWD + '
        'J301N1_TP2_OVERCROWD'
    )

    assert constraints == [
        '-A100_J301N1_T1 + A100_J301N1_T1_J301N1_TP1 - A100_J301N1_TP1 >= -1',
        '-A100_J301N1_T1 + J301N1_T1_OVERCROWD >= -10',
        '-A100_J301N1_T2 + J301N1_T2_OVERCROWD >= -10',
        '-A100_J301N1_TP1 + J301N1_TP1_OVERCROWD >= -10',
        '-A100_J301N1_TP2 + J301N1_TP2_OVERCROWD >= -10',
        'A100_J301N1_T1 + A100_J301N1_T2 = 1',
        'A100_J301N1_TP1 + A100_J301N1_TP2 = 1'
    ]

def test_overlap_optimization() -> None:
    timeslot = Timeslot(Weekday.MONDAY, ScheduleTime(9, 0), ScheduleTime(11, 0))
    shift1 = Shift(ShiftType.T, 1, 10, [])
    shift2 = Shift(ShiftType.T, 2, 10, [timeslot])
    shift3 = Shift(ShiftType.TP, 1, 10, [timeslot])
    course = Course('J301N1', 1, [shift1, shift2, shift3])

    student = Student('A100', 1, [course], Schedule([(course, shift3)]))

    problem = SchedulingProblem([course], [student])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == '10000.0*A100_J301N1_T2 + 0.1*J301N1_T1_OVERCROWD + 0.1*J301N1_T2_OVERCROWD'
    assert constraints == [
        '-A100_J301N1_T1 + J301N1_T1_OVERCROWD >= -10',
        '-A100_J301N1_T2 + J301N1_T2_OVERCROWD >= -10',
        'A100_J301N1_T1 + A100_J301N1_T2 = 1'
    ]

def test_inevitable_overcrowded_shift_1() -> None:
    shift = Shift(ShiftType.TP, 1, 1, [])
    course = Course('J301N1', 1, [shift])

    student1 = Student('A100', 1, [course], Schedule([(course, shift)]))
    student2 = Student('A200', 1, [course], Schedule([(course, shift)]))

    problem = SchedulingProblem([course], [student1, student2])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == '0.0'
    assert constraints == []

def test_inevitable_overcrowded_shift_2() -> None:
    shift1 = Shift(ShiftType.TP, 1, 1, [])
    shift2 = Shift(ShiftType.TP, 2, 1, [])
    course = Course('J301N1', 1, [shift1, shift2])

    student1 = Student('A100', 1, [course], Schedule([(course, shift1)]))
    student2 = Student('A200', 1, [course], Schedule([(course, shift1)]))
    student3 = Student('A300', 1, [course], Schedule([]))

    problem = SchedulingProblem([course], [student1, student2, student3])
    model = SchedulingProblemModel(problem)

    objective, constraints = __decompose_model(model)
    assert objective == 'J301N1_TP1_OVERCROWD + J301N1_TP2_OVERCROWD'
    assert constraints == [
        '-A300_J301N1_TP1 + J301N1_TP1_OVERCROWD >= 1',
        '-A300_J301N1_TP2 + J301N1_TP2_OVERCROWD >= -1',
        'A300_J301N1_TP1 + A300_J301N1_TP2 = 1'
    ]

def test_bad_variable_name() -> None:
    shift = Shift(ShiftType.TP, 1, 10, [])
    course = Course('X\0Y\0Z', 1, [shift])

    student = Student('A B C', 1, [course], Schedule([]))

    problem = SchedulingProblem([course], [student])
    model = SchedulingProblemModel(problem)

    solution = model.solve()
    assert solution.problem is problem
    assert solution.final_schedules == {
        'A B C': Schedule([(course, shift)])
    }

def test_solve_more_than_once() -> None:
    shift1 = Shift(ShiftType.TP, 1, 10, [])
    shift2 = Shift(ShiftType.TP, 2, 10, [])
    course = Course('J301N1', 1, [shift1, shift2])

    student = Student('A100', 1, [course], Schedule([]))

    problem = SchedulingProblem([course], [student])
    model = SchedulingProblemModel(problem)

    for _ in range(5):
        solution = model.solve()
        assert solution.final_schedules in [
            {
                'A100': Schedule([(course, shift1)])
            },
            {
                'A100': Schedule([(course, shift2)])
            },
        ]

def test_unknown_solver(monkeypatch: pytest.MonkeyPatch) -> None:
    unavailable_solvers = set(pulp.listSolvers()) - set(pulp.listSolvers(onlyAvailable=True))
    solver_name = next(iter(unavailable_solvers))
    monkeypatch.setattr(config, 'SOLVER', pulp.getSolver(solver_name))

    problem = SchedulingProblem([], [])
    model = SchedulingProblemModel(problem)

    with pytest.raises(SchedulingProblemModelError):
        model.solve()

def test_no_solution_found() -> None:
    problem = SchedulingProblem([], [])
    model = SchedulingProblemModel(problem)
    model._SchedulingProblemModel__model += pulp.LpAffineExpression() == 1.0 # type: ignore

    with pytest.raises(SchedulingProblemModelError):
        model.solve()
