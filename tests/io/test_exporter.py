import json

from kepler.io.exporter import export_json_solution_string
from kepler.types import *

def test_success() -> None:
    shift1 = Shift(ShiftType.T, 1, 120, [])
    shift2 = Shift(ShiftType.TP, 1, 40, [])
    shift3 = Shift(ShiftType.TP, 2, 40, [])

    course = Course('J306N8', 3, [shift1, shift2, shift3])

    student1 = Student('A100', 1, [course], Schedule([]))
    student2 = Student('A200', 3, [course], Schedule([]))

    schedule1 = Schedule([(course, shift1), (course, shift2)])
    schedule2 = Schedule([(course, shift1), (course, shift3)])

    problem = SchedulingProblem([course], [student1, student2])
    final_schedules = {'A100': schedule1, 'A200': schedule2}
    solution = SchedulingProblemSolution(problem, final_schedules)

    solution_json_object = json.loads(export_json_solution_string(solution))

    assert solution_json_object == {
        'A100': [
            {
                'course': 'J306N8',
                'shift_type': 'T',
                'shift_number': 1
            },
            {
                'course': 'J306N8',
                'shift_type': 'TP',
                'shift_number': 1
            }
        ],
        'A200': [
            {
                'course': 'J306N8',
                'shift_type': 'T',
                'shift_number': 1
            },
            {
                'course': 'J306N8',
                'shift_type': 'TP',
                'shift_number': 2
            }
        ]
    }
