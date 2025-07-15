from __future__ import annotations
from collections.abc import Iterable, Mapping, Set
import functools

from .course import Course
from .schedule import Schedule
from .shift import ShiftType

class StudentError(Exception):
    pass

@functools.total_ordering # NOTE: total order exists if no two students share the same number
class Student:
    def __init__(
        self,
        number: str,
        year: int,
        enrollments: Iterable[Course],
        previous_schedule: Schedule) -> None:

        self.__number = number
        self.__year = year
        self.__enrollments: dict[str, Course] = {}
        self.__previous_schedule = previous_schedule

        if year <= 0:
            raise StudentError(f'Non-positive year {year} in student {number}')

        for course in enrollments:
            if course.id in self.__enrollments:
                raise StudentError(f'Courses with the same id ({course.id}) in student {number}')

            self.__enrollments[course.id] = course

        if not previous_schedule.is_valid_for_student(self):
            raise StudentError(f'Student {number}\'s schedule is not valid for them')

    def list_mandatory_shift_types(self) -> Set[tuple[Course, ShiftType]]:
        mandatory_shift_types: set[tuple[Course, ShiftType]] = set()

        for course in self.__enrollments.values():
            course_shift_types = set(course.shifts)

            for shift_type in course_shift_types:
                mandatory_shift_types.add((course, shift_type))

        return mandatory_shift_types

    @property
    def number(self) -> str:
        return self.__number

    @property
    def year(self) -> int:
        return self.__year

    @property
    def enrollments(self) -> Mapping[str, Course]:
        return self.__enrollments

    @property
    def previous_schedule(self) -> Schedule:
        return self.__previous_schedule

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return False

        return self.__number == other.number

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
            f'year={self.__year!r}, '
            f'enrollments={sorted(list(self.__enrollments.values()))!r}, '
            f'previous_schedule={self.__previous_schedule!r})'
        )
