from __future__ import annotations
from collections.abc import Iterable, Mapping

from .course import Course
from .schedule import Schedule

class StudentError(Exception):
    pass

class Student:
    def __init__(self, number: str, courses: Iterable[Course], previous_schedule: Schedule) -> None:
        self.__number = number
        self.__courses: dict[str, Course] = {}
        self.__previous_schedule = previous_schedule

        for course in courses:
            if course.id in self.__courses:
                raise StudentError(f'Courses with the same id ({course.id}) in student {number}')

            self.__courses[course.id] = course

        for course, _ in previous_schedule.shifts:
            if self.__courses.get(course.id) is not course:
                raise StudentError(
                    f'Student {number}\'s schedule references course {course.id} the student is '
                    'not enrolled in'
                )

    @property
    def number(self) -> str:
        return self.__number

    @property
    def courses(self) -> Mapping[str, Course]:
        return self.__courses

    @property
    def previous_schedule(self) -> Schedule:
        return self.__previous_schedule

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return False

        return (
            self.__number == other.number and
            self.__courses == other.courses and
            self.__previous_schedule == other.previous_schedule
        )

    def __copy__(self) -> Student:
        return self # NOTE: Student and all its fields are immutable

    def __hash__(self) -> int:
        return hash(self.__number)

    def __repr__(self) -> str:
        return (
            'Student('
            f'number={self.__number!r}, '
            f'courses={list(self.__courses.values())!r}, '
            f'previous_schedule={self.__previous_schedule!r})'
        )
