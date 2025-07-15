from __future__ import annotations
from collections.abc import Iterable, Mapping
import typing

from .course import Course
from .shift import Shift, ShiftType

if typing.TYPE_CHECKING: # pragma: no coverage
    from .student import Student

class ScheduleError(Exception):
    pass

class Schedule:
    def __init__(self, shifts: Iterable[tuple[Course, Shift]]) -> None:
        self.__courses: dict[str, Course] = {}
        self.__shifts: dict[tuple[str, ShiftType], Shift] = {}

        for course, shift in shifts:
            full_shift_type = course.id, shift.type

            if full_shift_type in self.__shifts:
                raise ScheduleError(f'Shift {course.id}-{shift.type} multiple times in schedule')
            elif course.shifts.get(shift.type, {}).get(shift.number) is not shift:
                raise ScheduleError(f'Shift {shift.name} does not belong to course {course.id}')
            elif self.__courses.get(course.id, course) is not course:
                raise ScheduleError(f'Different course with the same id: {course.id}')

            self.__courses[course.id] = course
            self.__shifts[course.id, shift.type] = shift

    def is_valid_for_student(self, student: Student) -> bool:
        return all(
            student.enrollments.get(course.id) is course for course in self.__courses.values()
        )

    def is_complete_for_student(self, student: Student) -> bool:
        mandatory_shift_types = {
            (course.id, shift) for course, shift in student.list_mandatory_shift_types()
        }

        return set(self.__shifts) == mandatory_shift_types

    @property
    def shifts(self) -> Mapping[tuple[str, ShiftType], Shift]:
        return self.__shifts

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Schedule):
            return False

        return self.__shifts == other.shifts

    def __copy__(self) -> Schedule:
        return self # NOTE: Schedule and all its fields are immutable

    def __repr__(self) -> str:
        presentable_shifts = sorted(
            (self.__courses[course_id], shift) for (course_id, _), shift in self.__shifts.items()
        )

        return f'Schedule(shifts={presentable_shifts!r})'
