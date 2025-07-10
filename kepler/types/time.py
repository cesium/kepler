from __future__ import annotations
import functools
import re

class ScheduleTimeError(Exception):
    pass

@functools.total_ordering
class ScheduleTime:
    def __init__(self, hour: int, minute: int) -> None:
        self.__hour = hour
        self.__minute = minute

        if not ((0 <= hour <= 23 and 0 <= minute <= 59) or (hour == 24 and minute == 0)):
            raise ScheduleTimeError(f'Time {self} has invalid fields')

    @property
    def hour(self) -> int:
        return self.__hour

    @property
    def minute(self) -> int:
        return self.__minute

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ScheduleTime):
            return False

        return self.__hour == other.hour and self.__minute == other.minute

    def __lt__(self, other: ScheduleTime) -> bool:
        if self.__hour != other.hour:
            return self.__hour < other.hour
        else:
            return self.__minute < other.minute

    def __copy__(self) -> ScheduleTime:
        return self # NOTE: ScheduleTime and all its fields are immutable

    def __hash__(self) -> int:
        return hash((self.__hour, self.__minute))

    def __str__(self) -> str:
        return f'{self.__hour:02}:{self.__minute:02}'

    def __repr__(self) -> str:
        return f'ScheduleTime(hour={self.__hour!r}, minute={self.__minute!r})'

    @staticmethod
    def parse(time: str) -> ScheduleTime:
        match = re.match(r'(\d{2}):(\d{2})$', time)
        if match is None:
            raise ScheduleTimeError(f'Failed to parse time \'{time}\'')

        hour = int(match.group(1))
        minute = int(match.group(2))
        return ScheduleTime(hour, minute)
