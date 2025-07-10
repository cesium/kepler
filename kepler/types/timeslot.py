from __future__ import annotations
import functools

from .time import ScheduleTime
from .weekday import Weekday

class TimeslotError(Exception):
    pass

@functools.total_ordering
class Timeslot:
    def __init__(self, day: Weekday, start: ScheduleTime, end: ScheduleTime) -> None:
        if end <= start:
            raise TimeslotError(f'Timeslot\'s start ({start!r}) must precede its end ({end!r})')

        self.__day = day
        self.__start = start
        self.__end = end

    def overlaps(self, other: Timeslot) -> bool:
        return self.__day == other.day and self.__start < other.end and other.start < self.__end

    @property
    def day(self) -> Weekday:
        return self.__day

    @property
    def start(self) -> ScheduleTime:
        return self.__start

    @property
    def end(self) -> ScheduleTime:
        return self.__end

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timeslot):
            return False

        return self.__day == other.day and self.__start == other.start and self.__end == other.end

    def __lt__(self, other: Timeslot) -> bool:
        if self.__day != other.day:
            return self.__day < other.day
        elif self.__start != other.start:
            return self.__start < other.start
        else:
            return self.__end < other.end

    def __copy__(self) -> Timeslot:
        return self # NOTE: Timeslot and all its fields are immutable

    def __hash__(self) -> int:
        return hash((self.__day, self.__start, self.__end))

    def __repr__(self) -> str:
        return f'Timeslot(day={self.__day!r}, start={self.__start!r}, end={self.__end!r})'
