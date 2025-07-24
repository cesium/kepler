from __future__ import annotations
from enum import Enum
import functools

@functools.total_ordering
class SortedEnum(Enum):
    def __lt__(self, other: SortedEnum) -> bool:
        if type(self) is not type(other):
            self_type_name = type(self).__name__
            other_type_name = type(other).__name__

            raise TypeError(f'Failed to compare {self_type_name} and {other_type_name}')

        ordered_values = list(type(self))
        self_index = ordered_values.index(self)
        other_index = ordered_values.index(other)

        return self_index < other_index

    def __repr__(self) -> str:
        return f'{type(self).__name__}.{self.name}'

    def __str__(self) -> str:
        return str(self.value)
