from __future__ import annotations
from collections.abc import Iterable, Mapping, Set

from .course import Course
from .shift import ShiftType
from .student import Student

class SchedulingProblemError(Exception):
    pass

class SchedulingProblem:
    def __init__(self, courses: Iterable[Course], students: Iterable[Student]) -> None:
        self.__courses: dict[str, Course] = {}
        self.__students: dict[str, Student] = {}

        for course in courses:
            if course.id in self.__courses:
                raise SchedulingProblemError(f'Courses with the same id: {course.id}')

            self.__courses[course.id] = course

        for student in students:
            if student.number in self.__students:
                raise SchedulingProblemError(f'Students with the same number: {student.number}')

            for course_id, course in student.enrollments.items():
                if self.__courses.get(course_id) is not course:
                    raise SchedulingProblemError(
                        f'Student {student.number} references unknown course {course.id}'
                    )

            self.__students[student.number] = student

    def list_possible_students_by_shift(self) -> Mapping[tuple[str, ShiftType, int], Set[Student]]:
        possible_students_by_shift: dict[tuple[str, ShiftType, int], set[Student]] = {}

        for student in self.__students.values():
            for course, shift in student.list_possible_shifts():
                shift_id = course.id, shift.type, shift.number
                possible_students_by_shift.setdefault(shift_id, set())
                possible_students_by_shift[shift_id].add(student)

        for course in self.__courses.values():
            for type_shifts in course.shifts.values():
                for shift in type_shifts.values():
                    shift_id = course.id, shift.type, shift.number
                    possible_students_by_shift.setdefault(shift_id, set())

        return possible_students_by_shift

    @property
    def courses(self) -> Mapping[str, Course]:
        return self.__courses

    @property
    def students(self) -> Mapping[str, Student]:
        return self.__students

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SchedulingProblem):
            return False

        return (
            set(self.__courses) == set(other.courses) and
            set(self.__students) == set(other.students)
        )

    def __copy__(self) -> SchedulingProblem:
        return self # NOTE: SchedulingProblem and all its fields are immutable

    def __repr__(self) -> str:
        return (
            'SchedulingProblem('
            f'courses={sorted(self.__courses.values())!r}, '
            f'students={sorted(self.__students.values())!r})'
        )
