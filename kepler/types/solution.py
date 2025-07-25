from __future__ import annotations
from collections.abc import Mapping
import pprint

from .problem import SchedulingProblem
from .schedule import Schedule

class SchedulingProblemSolutionError(Exception):
    pass

class SchedulingProblemSolution:
    def __init__(self, problem: SchedulingProblem, final_schedules: Mapping[str, Schedule]) -> None:
        self.__problem = problem
        self.__final_schedules: dict[str, Schedule] = dict(final_schedules)

        for student_number in final_schedules:
            if student_number not in problem.students:
                raise SchedulingProblemSolutionError(
                    f'Schedule for unknown student {student_number}'
                )

        for student in problem.students.values():
            schedule = final_schedules.get(student.number)

            if schedule is None:
                raise SchedulingProblemSolutionError(
                    f'Missing schedule for student {student.number}'
                )
            elif not schedule.is_valid_for_student(student):
                raise SchedulingProblemSolutionError(
                    f'Invalid schedule for student {student.number}'
                )
            elif not schedule.is_complete_for_student(student):
                raise SchedulingProblemSolutionError(
                    f'Incomplete schedule for student {student.number}'
                )

    @property
    def problem(self) -> SchedulingProblem:
        return self.__problem

    @property
    def final_schedules(self) -> Mapping[str, Schedule]:
        return self.__final_schedules

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SchedulingProblemSolution):
            return False

        return self.__problem == other.problem and self.__final_schedules == other.final_schedules

    def __copy__(self) -> SchedulingProblemSolution:
        return self # NOTE: SchedulingProblemSolution and all its fields are immutable

    def __repr__(self) -> str:
        schedules_formatted = pprint.pformat(self.__final_schedules, indent=0, sort_dicts=True)

        return (
            'SchedulingProblemSolution('
            f'problem={self.__problem!r}, '
            f'final_schedules={schedules_formatted})'
        )
