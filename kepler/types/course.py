from __future__ import annotations
from collections.abc import Iterable, Mapping
import functools
import itertools

from .shift import Shift, ShiftType

class CourseError(Exception):
    pass

@functools.total_ordering # NOTE: total order exists if no two courses share the same id
class Course:
    def __init__(self, id_: str, year: int, shifts: Iterable[Shift]) -> None:
        self.__id = id_
        self.__year = year
        self.__shifts: dict[ShiftType, dict[int, Shift]] = {}

        if year <= 0:
            raise CourseError(f'Non-positive year {year} in course {id_}')

        for shift in shifts:
            self.__shifts.setdefault(shift.type, {})
            if shift.number in self.__shifts[shift.type]:
                raise CourseError(f'Shifts with the same name ({shift.name}) in course {id_}')

            self.__shifts[shift.type][shift.number] = shift

    @property
    def id(self) -> str:
        return self.__id

    @property
    def year(self) -> int:
        return self.__year

    @property
    def shifts(self) -> Mapping[ShiftType, Mapping[int, Shift]]:
        return self.__shifts

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Course):
            return False

        return self.__id == other.id

    def __lt__(self, other: Course) -> bool:
        return self.__id < other.id

    def __copy__(self) -> Course:
        return self # NOTE: Course and all its fields are immutable

    def __hash__(self) -> int:
        return hash(self.__id)

    def __repr__(self) -> str:
        presentable_shifts = sorted(
            itertools.chain(*(type_shifts.values() for type_shifts in self.__shifts.values()))
        )

        return (
            'Course('
            f'id_={self.__id!r}, '
            f'year={self.__year!r}, '
            f'shifts={presentable_shifts!r})'
        )
