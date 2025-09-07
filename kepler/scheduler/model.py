from collections.abc import Set
import itertools
import typing

import pulp

from . import config
from ..types import *

class SchedulingProblemModelError(Exception):
    pass

class SchedulingProblemModel:
    def __init__(self, problem: SchedulingProblem) -> None:
        self.__model = pulp.LpProblem(sense=pulp.LpMinimize)
        self.__model.objective = pulp.LpAffineExpression()

        self.__problem = problem
        self.__solution: dict[tuple[str, str, ShiftType, int], pulp.LpVariable | bool] = {}

        for student in problem.students.values():
            self.__prepare_solution_for_student(student)
            self.__add_student_enrollments(student)
            self.__add_student_overlaps(student)

        shift_students = problem.list_possible_students_by_shift()
        for (course_id, shift_type, shift_number), students in shift_students.items():
            course = problem.courses[course_id]
            shift = course.shifts[shift_type][shift_number]

            self.__add_shift_capacity(course, shift, students)

    def solve(self) -> SchedulingProblemSolution:
        try:
            status = self.__model.solve(config.SOLVER)
        except pulp.PulpSolverError as e:
            raise SchedulingProblemModelError(f'Solver error: {e}') from e

        if status != pulp.constants.LpStatusOptimal:
            raise SchedulingProblemModelError(
                f'Failed to solve scheduling problem. Status: {pulp.constants.LpSolution[status]}'
            )

        student_shifts: dict[str, list[tuple[Course, Shift]]] = {}
        for variable_id, variable in self.__solution.items():
            if SchedulingProblemModel.__get_solution_variable_value(variable):
                student_number, course_id, shift_type, shift_number = variable_id

                course = self.__problem.courses[course_id]
                shift = course.shifts[shift_type][shift_number]

                student_shifts.setdefault(student_number, [])
                student_shifts[student_number].append((course, shift))

        for student_number in self.__problem.students:
            student_shifts.setdefault(student_number, [])

        try:
            final_schedules = {
                number: Schedule(shifts) for number, shifts in student_shifts.items()
            }

            return SchedulingProblemSolution(self.__problem, final_schedules)
        except (ScheduleError, SchedulingProblemSolutionError) as e: # pragma: no cover
            raise SchedulingProblemModelError(f'Invalid problem solution: {e}') from e

    def __prepare_solution_for_student(self, student: Student) -> None:
        for course, shift in student.list_assigned_shifts():
            variable_id = student.number, course.id, shift.type, shift.number
            self.__solution[variable_id] = True
        for course, shift in student.list_unassignable_shifts_in_enrolled_courses():
            variable_id = student.number, course.id, shift.type, shift.number
            self.__solution[variable_id] = False

        for course, shift in student.list_possible_shifts():
            variable_id = student.number, course.id, shift.type, shift.number

            if variable_id not in self.__solution:
                variable_name = f'{student.number}_{course.id}_{shift.name}'
                variable = pulp.LpVariable(variable_name, cat=pulp.LpBinary)
                self.__solution[variable_id] = variable

    def __add_student_enrollments(self, student: Student) -> None:
        for course in student.enrollments.values():
            for type_shifts in course.shifts.values():

                restriction_variables: list[pulp.LpVariable | bool] = []
                for shift in type_shifts.values():
                    variable_id = student.number, course.id, shift.type, shift.number
                    restriction_variables.append(self.__solution[variable_id])

                self.__model += sum(restriction_variables) == 1

    def __add_student_overlaps(self, student: Student) -> None:
        possible_shifts = sorted(student.list_possible_shifts())

        for (course1, shift1), (course2, shift2) in itertools.combinations(possible_shifts, 2):
            if not (course1 is course2 and shift1.type == shift2.type) and shift1.overlaps(shift2):

                shift1_variable_id = student.number, course1.id, shift1.type, shift1.number
                shift2_variable_id = student.number, course2.id, shift2.type, shift2.number
                shift1_variable = self.__solution[shift1_variable_id]
                shift2_variable = self.__solution[shift2_variable_id]

                variable_count = (
                    isinstance(shift1_variable, pulp.LpVariable) +
                    isinstance(shift2_variable, pulp.LpVariable)
                )

                overlap_weight = config.calculate_schedule_overlap_weight(
                    student, course1, shift1, course2, shift2
                )

                if variable_count == 1:
                    if shift1_variable is True:
                        self.__model.objective += overlap_weight * shift2_variable
                    else:
                        self.__model.objective += overlap_weight * shift1_variable
                elif variable_count == 2:
                    overlap_variable_name = \
                        f'{student.number}_{course1.id}_{shift1.name}_{course2.id}_{shift2.name}'
                    overlap_variable = pulp.LpVariable(overlap_variable_name, cat=pulp.LpBinary)

                    self.__model += overlap_variable >= shift1_variable + shift2_variable - 1
                    self.__model.objective += overlap_weight * overlap_variable

    def __add_shift_capacity(
        self,
        course: Course,
        shift: Shift,
        students: Set[Student]) -> None:

        shift_capacity = shift.capacity
        restriction_variables: list[pulp.LpVariable] = []
        for student in students:
            variable_id = student.number, course.id, shift.type, shift.number
            variable = self.__solution[variable_id]

            if isinstance(variable, pulp.LpVariable):
                restriction_variables.append(variable)
            else:
                # Possible students only: variable is True
                shift_capacity -= 1

        if restriction_variables:
            overcrowd_variable_name = f'{course.id}_{shift.name}_OVERCROWD'
            overcrowd_variable = pulp.LpVariable(overcrowd_variable_name, 0)

            overcrowd_weight = config.calculate_room_overcrowd_weight(course, shift)
            self.__model += overcrowd_variable >= sum(restriction_variables) - shift_capacity
            self.__model.objective += overcrowd_weight * overcrowd_variable

    @staticmethod
    def __get_solution_variable_value(variable: pulp.LpVariable | bool) -> bool:
        if isinstance(variable, bool):
            return variable
        else:
            return typing.cast(bool, pulp.value(variable))
