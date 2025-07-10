from __future__ import annotations
import enum

from .enum import SortedEnum

@enum.unique
class Weekday(SortedEnum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
