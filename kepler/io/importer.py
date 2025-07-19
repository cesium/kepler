import json
import typing

from ..types import *

class JsonImporterError(Exception):
    pass

def import_json_problem_file(path: str) -> SchedulingProblem: # pragma: no coverage
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            root_json = json.load(f)
    except IOError as e:
        raise JsonImporterError(f'Failed to read JSON file {path}: {e}') from e
    except json.JSONDecodeError as e:
        raise JsonImporterError(f'Failed to parse JSON file {path}: {e}') from e

    return import_json_problem_object(root_json)

def import_json_problem_string(json_string: str) -> SchedulingProblem:
    try:
        root_json = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise JsonImporterError(f'Failed to parse JSON string: {e}') from e

    return import_json_problem_object(root_json)

def import_json_problem_object(root_json: object) -> SchedulingProblem:
    __assert_dict_with_keys(root_json, {'students', 'courses'}, 'the JSON\'s root')
    root_json = typing.cast(dict[str, object], root_json)

    courses = __parse_courses(root_json['courses'])
    courses_dict = {course.id: course for course in courses}
    students = __parse_students(root_json['students'], courses_dict)

    try:
        return SchedulingProblem(courses, students)
    except SchedulingProblemError as e:
        raise JsonImporterError(f'Invalid scheduling problem: {e}') from e

def __parse_courses(courses_json: object) -> list[Course]:
    __assert_type(courses_json, list, 'courses')
    courses_json = typing.cast(list[object], courses_json)

    return [__parse_course(course_json) for course_json in courses_json]

def __parse_course(course_json: object) -> Course:
    __assert_dict_with_keys(course_json, {'id', 'year', 'shifts'}, 'course')
    course_json = typing.cast(dict[str, object], course_json)

    id_ = __parse_string(course_json['id'], 'course id')
    year = __parse_integer(course_json['year'], 'course year')
    shifts = __parse_shifts(course_json['shifts'])

    try:
        return Course(id_, year, shifts)
    except CourseError as e:
        raise JsonImporterError(f'Invalid course {id_}: {e}') from e

def __parse_shifts(shifts_json: object) -> list[Shift]:
    __assert_type(shifts_json, list, 'course shifts')
    shifts_json = typing.cast(list[object], shifts_json)

    return [__parse_shift(shift_json) for shift_json in shifts_json]

def __parse_shift(shift_json: object) -> Shift:
    __assert_dict_with_keys(shift_json, {'type', 'number', 'capacity', 'timeslots'}, 'shift')
    shift_json = typing.cast(dict[str, object], shift_json)

    type_ = __parse_shift_type(shift_json['type'])
    number = __parse_integer(shift_json['number'], 'shift number')
    capacity = __parse_integer(shift_json['capacity'], 'shift capacity')
    timeslots = __parse_timeslots(shift_json['timeslots'])

    try:
        return Shift(type_, number, capacity, timeslots)
    except ShiftError as e:
        raise JsonImporterError(f'Invalid shift {type_}{number}: {e}') from e

def __parse_shift_type(type_json: object) -> ShiftType:
    __assert_type(type_json, str, 'type')
    type_json = typing.cast(str, type_json)

    try:
        return ShiftType(type_json.upper())
    except ValueError as e:
        raise JsonImporterError(f'Invalid shift type "{type_json}"') from e

def __parse_timeslots(timeslots_json: object) -> list[Timeslot]:
    __assert_type(timeslots_json, list, 'timeslots')
    timeslots_json = typing.cast(list[object], timeslots_json)

    return [__parse_timeslot(timeslot_json) for timeslot_json in timeslots_json]

def __parse_timeslot(timeslot_json: object) -> Timeslot:
    __assert_dict_with_keys(timeslot_json, {'day', 'start', 'end'}, 'timeslot')
    timeslot_json = typing.cast(dict[str, object], timeslot_json)

    day = __parse_day(timeslot_json['day'])
    start = __parse_time(timeslot_json['start'], 'timeslot start')
    end = __parse_time(timeslot_json['end'], 'timeslot end')

    try:
        return Timeslot(day, start, end)
    except TimeslotError as e:
        raise JsonImporterError(f'Invalid timeslot {json.dumps(timeslot_json)}: {e}') from e

def __parse_day(day_json: object) -> Weekday:
    __assert_type(day_json, str, 'timeslot day')
    day_json = typing.cast(str, day_json)

    try:
        return Weekday(day_json.capitalize())
    except ValueError as e:
        raise JsonImporterError(f'Invalid day "{day_json}"') from e

def __parse_time(time_json: object, property_name: str) -> ScheduleTime:
    __assert_type(time_json, str, property_name)
    time_json = typing.cast(str, time_json)

    try:
        return ScheduleTime.parse(time_json)
    except ScheduleTimeError as e:
        raise JsonImporterError(f'Failed to parse time "{time_json}"') from e

def __parse_students(students_json: object, courses: dict[str, Course]) -> list[Student]:
    __assert_type(students_json, list, 'students')
    students_json = typing.cast(list[object], students_json)

    return [__parse_student(student_json, courses) for student_json in students_json]

def __parse_student(student_json: object, courses: dict[str, Course]) -> Student:
    __assert_dict_with_keys(student_json, {'number', 'year', 'enrollments'}, 'student')
    student_json = typing.cast(dict[str, object], student_json)

    number = __parse_string(student_json['number'], 'student number')
    year = __parse_integer(student_json['year'], 'student year')
    student_courses = __parse_enrollements(student_json['enrollments'], courses)
    schedule = __parse_schedule(student_json.get('schedule'), number, courses)

    try:
        return Student(number, year, student_courses, schedule)
    except StudentError as e:
        raise JsonImporterError(f'Invalid student {number}: {e}') from e

def __parse_enrollements(enrollments_json: object, courses: dict[str, Course]) -> list[Course]:
    __assert_type(enrollments_json, list, 'student enrollments')
    enrollments_json = typing.cast(list[object], enrollments_json)

    return [__parse_enrollment(enrollment_json, courses) for enrollment_json in enrollments_json]

def __parse_enrollment(enrollment_json: object, courses: dict[str, Course]) -> Course:
    __assert_type(enrollment_json, str, 'student enrollement')
    enrollment_json = typing.cast(str, enrollment_json)

    course = courses.get(enrollment_json)
    if course is None:
        raise JsonImporterError(f'Course {enrollment_json} in enrollment was not found')

    return course

def __parse_schedule(
    schedule_json: object,
    student_number: str,
    courses: dict[str, Course]) -> Schedule:

    if schedule_json is None:
        return Schedule([])

    __assert_type(schedule_json, list, 'student schedule')
    schedule_json = typing.cast(list[object], schedule_json)

    shifts = [__parse_schedule_shift(shift_json, courses) for shift_json in schedule_json]

    try:
        return Schedule(shifts)
    except ScheduleError as e:
        raise JsonImporterError(f'{student_number}\'s schedule is invalid: {e}') from e

def __parse_schedule_shift(shift_json: object, courses: dict[str, Course]) -> tuple[Course, Shift]:
    __assert_dict_with_keys(shift_json, {'course', 'shift_type', 'shift_number'}, 'schedule shift')
    shift_json = typing.cast(dict[str, object], shift_json)

    course_id = __parse_string(shift_json['course'], 'course')
    shift_type = __parse_shift_type(shift_json['shift_type'])
    shift_number = __parse_integer(shift_json['shift_number'], 'number')

    course = courses.get(course_id)
    if course is None:
        raise JsonImporterError(
            f'Course {course_id} in schedule shift {json.dumps(shift_json)} was not found'
        )

    shift = course.shifts.get(shift_type, {}).get(shift_number)
    if shift is None:
        raise JsonImporterError(
            f'Shift {shift_type}{shift_number} in schedule shift {json.dumps(shift_json)} was not '
             'found'
        )

    return course, shift

def __parse_string(string_json: object, property_name: str) -> str:
    __assert_type(string_json, str, property_name)
    return typing.cast(str, string_json)

def __parse_integer(integer_json: object, property_name: str) -> int:
    __assert_type(integer_json, int, property_name)
    return typing.cast(int, integer_json)

def __assert_type(value_json: object, expected_type: type, property_name: str) -> None:
    # Don't use isinstance because bool is a subclass of int
    if type(value_json) != expected_type:
        # See https://docs.python.org/3/library/json.html#encoders-and-decoders for more details
        json_type_names = {
            dict: 'object',
            list: 'array',
            str: 'string',
            bool: 'boolean',
            int: 'number (integer)',
            float: 'number (floating-point)',
            type(None): 'null'
        }

        expected_type_name = json_type_names.get(expected_type, str(expected_type))
        got_type_name = json_type_names.get(type(value_json), str(type(value_json)))

        raise JsonImporterError(
            f'Expected {expected_type_name} for {property_name}, got {got_type_name} instead'
        )

def __assert_dict_with_keys(
    value_json: object,
    necessary_keys: set[str],
    property_name: str) -> None:

    __assert_type(value_json, dict, property_name)
    value_json = typing.cast(dict[str, object], value_json)

    got_keys = set(value_json)
    if not necessary_keys.issubset(got_keys):
        missing_keys = necessary_keys - got_keys
        missing_keys_str = ', '.join(sorted(missing_keys))

        raise JsonImporterError(
            f'Missing the following necessary keys for {property_name}: {missing_keys_str}'
        )
