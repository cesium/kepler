import enum

@enum.unique
class Weekday(enum.StrEnum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'

    def __repr__(self) -> str:
        return f'Weekday.{self.upper()}'
