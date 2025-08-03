from kepler.scheduler.config import (
    calculate_room_overcrowd_weight,
    calculate_schedule_overlap_weight
)
from kepler.types import *

def __calculate_schedule_overlap_weight(
    student_year: int,
    course1_year: int,
    course2_year: int) -> float:

    shift = Shift(ShiftType.T, 1, 150, [])
    course1 = Course('C1', course1_year, [shift])
    course2 = Course('C2', course2_year, [shift])

    student = Student('A100', student_year, [course1, course2], Schedule([]))
    return calculate_schedule_overlap_weight(student, course1, shift, course2, shift)

def test_calculate_schedule_overlap_weight_same_year() -> None:
    assert __calculate_schedule_overlap_weight(3, 3, 3) == 10000.0
    assert __calculate_schedule_overlap_weight(2, 2, 2) == 10000.0
    assert __calculate_schedule_overlap_weight(1, 1, 1) == 10000.0

def test_calculate_schedule_overlap_weight_single_one_year_behind() -> None:
    assert __calculate_schedule_overlap_weight(3, 3, 2) == 10.0
    assert __calculate_schedule_overlap_weight(3, 2, 3) == 10.0
    assert __calculate_schedule_overlap_weight(2, 2, 1) == 10.0
    assert __calculate_schedule_overlap_weight(2, 1, 2) == 10.0

def test_calculate_schedule_overlap_weight_both_one_year_behind() -> None:
    assert __calculate_schedule_overlap_weight(3, 2, 2) == 1.0
    assert __calculate_schedule_overlap_weight(2, 1, 1) == 1.0

def test_calculate_schedule_overlap_weight_single_more_than_one_year_behind() -> None:
    assert __calculate_schedule_overlap_weight(3, 3, 1) == 1.0
    assert __calculate_schedule_overlap_weight(3, 1, 3) == 1.0
    assert __calculate_schedule_overlap_weight(3, 2, 1) == 1.0
    assert __calculate_schedule_overlap_weight(3, 1, 2) == 1.0

def test_calculate_schedule_overlap_weight_both_more_than_one_year_behind() -> None:
    assert __calculate_schedule_overlap_weight(3, 1, 1) == 1.0

def test_calculate_schedule_overlap_weight_single_years_ahead() -> None:
    assert __calculate_schedule_overlap_weight(1, 2, 1) == 1.0
    assert __calculate_schedule_overlap_weight(1, 1, 2) == 1.0
    assert __calculate_schedule_overlap_weight(1, 3, 1) == 1.0
    assert __calculate_schedule_overlap_weight(1, 1, 3) == 1.0

def test_calculate_schedule_overlap_weight_both_years_ahead() -> None:
    assert __calculate_schedule_overlap_weight(1, 2, 2) == 1.0
    assert __calculate_schedule_overlap_weight(1, 3, 3) == 1.0

def test_calculate_schedule_overlap_weight_single_year_ahead_single_year_behind() -> None:
    assert __calculate_schedule_overlap_weight(2, 1, 3) == 1.0
    assert __calculate_schedule_overlap_weight(2, 3, 1) == 1.0

def test_calculate_room_overcrowd_weight_theoretical() -> None:
    shift = Shift(ShiftType.T, 1, 150, [])
    course = Course('J301N1', 1, [shift])
    assert calculate_room_overcrowd_weight(course, shift) == 0.1

def test_calculate_room_overcrowd_weight_practical() -> None:
    shift = Shift(ShiftType.PL, 1, 30, [])
    course = Course('J301N1', 1, [shift])
    assert calculate_room_overcrowd_weight(course, shift) == 1.0
