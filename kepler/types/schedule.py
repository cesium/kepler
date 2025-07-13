from __future__ import annotations
from collections.abc import Iterable, Sequence

from .course import Course
from .shift import Shift, ShiftType

class ScheduleError(Exception):
    pass

class Schedule:
    def __init__(self, shifts: Iterable[tuple[Course, Shift]]) -> None:
        self.__shifts: list[tuple[Course, Shift]] = []

        shift_types: set[tuple[str, ShiftType]] = set()
        for course, shift in shifts:
            shift_type = course.id, shift.type

            if shift_type in shift_types:
                raise ScheduleError(f'Shift {course.id}-{shift.type} multiple times in schedule')
            elif course.shifts.get(shift.type, {}).get(shift.number) is not shift:
                raise ScheduleError(f'Shift {shift.name} does not belong to course {course.id}')

            shift_types.add(shift_type)
            self.__shifts.append((course, shift))

    @property
    def shifts(self) -> Sequence[tuple[Course, Shift]]:
        return self.__shifts

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Schedule):
            return False

        return self.__shifts == other.shifts

    def __copy__(self) -> Schedule:
        return self # NOTE: Schedule and all its fields are immutable

    def __repr__(self) -> str:
        return f'Schedule(shifts={self.__shifts!r})'
