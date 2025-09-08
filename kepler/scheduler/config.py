import pulp

from ..types import Course, Shift, ShiftType, Student

SOLVER = pulp.getSolver('COIN_CMD', timeLimit=300)

def calculate_schedule_overlap_weight(
    student: Student,
    course1: Course,
    shift1: Shift,
    course2: Course,
    shift2: Shift) -> float:

    delta1 = student.year - course1.year
    delta2 = student.year - course2.year
    delta_sum = delta1 + delta2

    if delta1 < 0 or delta2 < 0:
        return 1.0       # Student doing courses from higher years
    elif delta_sum == 0:
        return 10000.0   # Courses with the same year as the student
    elif delta_sum == 1:
        return 10.0      # Exactly one course with a one year delay
    else:
        return 1.0       # Greater delay

def calculate_room_overcrowd_weight(course: Course, shift: Shift) -> float:
    return 0.1 if shift.type in [ShiftType.T, ShiftType.OT] else 1.0

def calculate_room_hard_capacity_limit(course: Course, shift: Shift) -> None | int:
    if len(course.shifts[shift.type]) == 1:
        return None
    else:
        return round(shift.capacity * 1.5)
