from __future__ import annotations
from collections.abc import Iterable, Mapping, Set
import functools

from .course import Course
from .schedule import Schedule
from .shift import Shift, ShiftType

class StudentError(Exception):
    pass

@functools.total_ordering # NOTE: total order exists if no two students share the same number
class Student:
    def __init__(
        self,
        number: str,
        enrollments: Iterable[Course],
        previous_schedule: Schedule) -> None:

        self.__number = number
        self.__enrollments: dict[str, Course] = {}
        self.__previous_schedule = previous_schedule

        for course in enrollments:
            if course.id in self.__enrollments:
                raise StudentError(f'Courses with the same id ({course.id}) in student {number}')

            self.__enrollments[course.id] = course

        if not previous_schedule.is_valid_for_student(self):
            raise StudentError(f'Student {number}\'s schedule is not valid for them')

    @property
    def number(self) -> str:
        return self.__number

    @property
    def enrollments(self) -> Mapping[str, Course]:
        return self.__enrollments

    @property
    def previous_schedule(self) -> Schedule:
        return self.__previous_schedule

    @property
    def mandatory_shift_types(self) -> Set[tuple[str, ShiftType]]:
        result: set[tuple[str, ShiftType]] = set()

        for course in self.__enrollments.values():
            for shift_type in course.shift_types:
                result.add((course.id, shift_type))

        return result

    @property
    def assigned_shifts(self) -> Set[tuple[Course, Shift]]:
        return {
            (self.__enrollments[course_id], shift)
            for (course_id, _), shift in self.__previous_schedule.shifts.items()
        }

    @property
    def unassignable_enrolled_shifts(self) -> Set[tuple[Course, Shift]]:
        result: set[tuple[Course, Shift]] = set()

        for (course_id, _), assigned_shift in self.__previous_schedule.shifts.items():
            course = self.__enrollments[course_id]

            for other_shift in course.shifts[assigned_shift.type].values():
                if other_shift is assigned_shift:
                    continue

                result.add((course, other_shift))

        return result

    @property
    def possible_shifts(self) -> Set[tuple[Course, Shift]]:
        result: set[tuple[Course, Shift]] = set()

        for course in self.enrollments.values():
            for type_shifts in course.shifts.values():
                for shift in type_shifts.values():
                    if self.__previous_schedule.shifts.get((course.id, shift.type), shift) is shift:
                        result.add((course, shift))

        return result

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return False

        return (
            self.__number == other.number and
            self.__enrollments == other.enrollments and
            self.__previous_schedule == other.previous_schedule
        )

    def __lt__(self, other: Student) -> bool:
        return self.__number < other.number

    def __copy__(self) -> Student:
        return self # NOTE: Student and all its fields are immutable

    def __hash__(self) -> int:
        return hash(self.__number)

    def __repr__(self) -> str:
        return (
            'Student('
            f'number={self.__number!r}, '
            f'enrollments={sorted(list(self.__enrollments.values()))!r}, '
            f'previous_schedule={self.__previous_schedule!r})'
        )
