from __future__ import annotations
from collections.abc import Iterable, Mapping

from .course import Course
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
