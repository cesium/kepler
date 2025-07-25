from collections.abc import Iterable, Mapping
import itertools

import pulp

from ..types import *

__SolutionVariableId = tuple[str, str, ShiftType, int]

class SchedulingProblemModel:
    def __init__(self, problem: SchedulingProblem) -> None:
        self.__model = pulp.LpProblem(sense=pulp.LpMinimize)
        self.__model.objective = pulp.LpAffineExpression()

        self.__problem = problem
        self.__solution_variables: dict[__SolutionVariableId, pulp.LpVariable | bool] = {}

        for student in problem.students.values():
            self.__add_student_solution_variables(student)
            self.__add_student_enrollments(student)
            self.__add_student_overlaps(student)

        shift_students = problem.possible_students_by_shift
        for (course_id, shift_type, shift_number), students in shift_students.items():
            course = problem.courses[course_id]
            shift = course.shifts[shift_type][shift_number]

            self.__add_shift_capacity(course, shift, students)

    def solve(self) -> SchedulingProblemSolution:
        solver = pulp.getSolver('HiGHS_CMD', timeLimit=40, threads=4)
        result = self.__model.solve(solver)

        student_shifts: dict[str, list[tuple[Course, Shift]]] = {}
        for variable_id, variable in self.__solution_variables.items():

            variable_value: bool = False
            if isinstance(variable, bool):
                variable_value = variable
            else:
                variable_value = pulp.value(variable)

            if variable_value:
                student_number, course_id, shift_type, shift_number = variable_id

                course = self.__problem.courses[course_id]
                shift = course.shifts[shift_type][shift_number]

                student_shifts.setdefault(student_number, [])
                student_shifts[student_number].append((course, shift))

        for student_number in self.__problem.students:
            student_shifts.setdefault(student_number, [])

        final_schedules = {number: Schedule(shifts) for number, shifts in student_shifts.items()}
        return SchedulingProblemSolution(self.__problem, final_schedules)

    def __add_student_solution_variables(self, student: Student) -> None:
        for course, shift in student.assigned_shifts:
            variable_id = student.number, course.id, shift.type, shift.number
            self.__solution_variables[variable_id] = True

        for course, shift in student.unassignable_enrolled_shifts:
            variable_id = student.number, course.id, shift.type, shift.number
            self.__solution_variables[variable_id] = False

        for course, shift in student.possible_shifts:
            variable_id = student.number, course.id, shift.type, shift.number

            if variable_id not in self.__solution_variables:
                variable_name = f'{student.number}_{course.id}_{shift.name}'
                variable = pulp.LpVariable(variable_name, cat=pulp.LpBinary)
                self.__solution_variables[variable_id] = variable

    def __add_student_enrollments(self, student: Student) -> None:
        for course in student.enrollments.values():
            for shift_type, shifts in course.shifts.items():

                restriction_variables: list[pulp.LpVariable | bool] = []
                for shift in shifts.values():
                    variable_id = student.number, course.id, shift_type, shift.number
                    restriction_variables.append(self.__solution_variables[variable_id])

                self.__model += sum(restriction_variables) == 1

    def __add_student_overlaps(self, student: Student) -> None:
        possible_shifts = student.possible_shifts

        for (course1, shift1), (course2, shift2) in itertools.combinations(possible_shifts, 2):
            if not (course1 is course2 and shift1.type == shift2.type) and shift1.overlaps(shift2):

                shift1_variable_id = student.number, course1.id, shift1.type, shift1.number
                shift1_variable = self.__solution_variables[shift1_variable_id]

                shift2_variable_id = student.number, course2.id, shift2.type, shift2.number
                shift2_variable = self.__solution_variables[shift2_variable_id]

                if isinstance(shift1_variable, bool) and isinstance(shift2_variable, bool):
                    self.__model.objective += shift1_variable and shift2_variable
                else:
                    overlapping_variable_name = \
                        f'{student.number}_{course1.id}_{shift1.name}_{course2.id}_{shift2.name}'
                    overlapping_variable = \
                        pulp.LpVariable(overlapping_variable_name, cat=pulp.LpBinary)

                    self.__model += overlapping_variable >= shift1_variable + shift2_variable - 1
                    self.__model.objective += overlapping_variable

    def __add_shift_capacity(
        self,
        course: Course,
        shift: Shift,
        students: Iterable[Student]) -> None:

        restriction_variables: list[pulp.LpVariable | bool] = []
        for student in students:
            variable_id = student.number, course.id, shift.type, shift.number
            restriction_variables.append(self.__solution_variables[variable_id])

        if restriction_variables:
            overcrowding_variable_name = f'{course.id}_{shift.name}_OVERCROWD'
            overcrowding_variable = pulp.LpVariable(overcrowding_variable_name, 0)

            self.__model += overcrowding_variable >= sum(restriction_variables) - shift.capacity
            self.__model.objective += 0.1 * overcrowding_variable
