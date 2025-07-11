from __future__ import annotations
from collections.abc import Iterable, Set
import enum
import functools

from .enum import SortedEnum
from .timeslot import Timeslot

class ShiftError(Exception):
    pass

@enum.unique
class ShiftType(SortedEnum):
    T = 'T'
    TP = 'TP'
    PL = 'PL'
    OT = 'OT'

# NOTE: total order only exists inside a Course (no shifts with the same type and number)
@functools.total_ordering
class Shift:
    def __init__(
        self,
        type_: ShiftType,
        number: int,
        capacity: int,
        timeslots: Iterable[Timeslot]) -> None:

        self.__type = type_
        self.__number = number
        self.__capacity = capacity
        self.__timeslots: set[Timeslot] = set()

        if number <= 0:
            raise ShiftError(f'Non-positive number {number} in shift {self.name}')
        if capacity <= 0:
            raise ShiftError(f'Non-positive capacity {capacity} in shift {self.name}')

        for timeslot in timeslots:
            if self.overlaps(timeslot):
                raise ShiftError(f'Overlapping timeslots in shift {self.name}')

            self.__timeslots.add(timeslot)

    def overlaps(self, other: Shift | Timeslot) -> bool:
        if isinstance(other, Timeslot):
            return any(other.overlaps(timeslot) for timeslot in self.__timeslots)
        elif isinstance(other, Shift): # pragma: no branch
            return any(self.overlaps(timeslot) for timeslot in other.timeslots)

    @property
    def type(self) -> ShiftType:
        return self.__type

    @property
    def number(self) -> int:
        return self.__number

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def timeslots(self) -> Set[Timeslot]:
        return self.__timeslots

    @property
    def name(self) -> str:
        return f'{self.__type}{self.__number}'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Shift):
            return False

        return self.__type == other.type and self.__number == other.number

    def __lt__(self, other: Shift) -> bool:
        if self.__type != other.type:
            return self.__type < other.type
        else:
            return self.__number < other.number

    def __copy__(self) -> Shift:
        return self # NOTE: Shift and all its fields are immutable

    def __hash__(self) -> int:
        return hash((self.__type, self.__number))

    def __repr__(self) -> str:
        return (
            'Shift('
            f'type_={self.__type!r}, '
            f'number={self.__number!r}, '
            f'capacity={self.__capacity!r}, '
            f'timeslots={sorted(self.__timeslots)!r})'
        )
