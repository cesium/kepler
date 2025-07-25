import json

from ..types import Schedule, SchedulingProblemSolution, Shift

class JsonExporterError(Exception):
    pass

def export_json_solution_file(
    path: str,
    solution: SchedulingProblemSolution) -> None: # pragma: no coverage

    try:
        with open(path, mode='w', encoding='utf-8') as f:
            json.dump(export_json_solution_object(solution), f)
    except IOError as e:
        raise JsonExporterError(f'Failed to write to JSON file {path}: {e}') from e

def export_json_solution_string(solution: SchedulingProblemSolution) -> str:
    return json.dumps(export_json_solution_object(solution))

def export_json_solution_object(solution: SchedulingProblemSolution) -> object:
    return {
        number: __export_json_schedule(schedule)
        for number, schedule in solution.final_schedules.items()
    }

def __export_json_schedule(schedule: Schedule) -> list[dict[str, object]]:
    return [
        __export_json_shift(course_id, shift) for (course_id, _), shift in schedule.shifts.items()
    ]

def __export_json_shift(course_id: str, shift: Shift) -> dict[str, object]:
    return {
        'course': course_id,
        'shift_type': shift.type.value,
        'shift_number': shift.number
    }
