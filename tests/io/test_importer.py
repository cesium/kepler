import pytest

from kepler.io.importer import JsonImporterError, import_json_problem_string
from kepler.types import *

# Test for successful importation

def test_success() -> None:
    problem = import_json_problem_string('''
        {
            "courses": [
                {
                    "id": "C1",
                    "year": 1,
                    "shifts": [
                        {
                            "type": "T",
                            "number": 1,
                            "capacity": 100,
                            "timeslots": [
                                {
                                    "day": "monday",
                                    "start": "09:00",
                                    "end": "10:00"
                                }
                            ]
                        }
                    ]
                }
            ],
            "students": [
                {
                    "number": "A100",
                    "year": 1,
                    "enrollments": [
                        "C1"
                    ],
                    "schedule": [
                        {
                            "course": "C1",
                            "shift_type": "T",
                            "shift_number": 1
                        }
                    ]
                }
            ]
        }
        ''')

    timeslot = Timeslot(Weekday.MONDAY, ScheduleTime(9, 0), ScheduleTime(10, 0))
    shift = Shift(ShiftType.T, 1, 100, [timeslot])
    course = Course('C1', 1, [shift])

    schedule = Schedule([(course, shift)])
    student = Student('A100', 1, [course], schedule)

    expected_problem = SchedulingProblem([course], [student])
    assert problem == expected_problem

# Tests for schema errors

def test_parse_error() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('[')

def test_root_not_object() -> None:
    with pytest.raises(JsonImporterError) as einfo:
        import_json_problem_string('[]')

    assert str(einfo.value) == 'Expected object for the JSON\'s root, got array instead'

def test_root_missing_keys() -> None:
    with pytest.raises(JsonImporterError) as einfo:
        import_json_problem_string('{}')

    assert 'courses, students' in str(einfo.value)

def test_root_too_many_keys() -> None:
    problem = import_json_problem_string('''
        {
            "courses": [],
            "students": [],
            "hi": 1
        }
        ''')

    assert problem == SchedulingProblem([], [])

def test_courses_not_array() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": {},
                "students": []
            }
            ''')

def test_course_not_object() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    []
                ],
                "students": []
            }
            ''')

def test_course_missing_keys() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 2
                    }
                ],
                "students": []
            }
            ''')

def test_course_id_not_string() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": 1,
                        "year": 2,
                        "shifts": []
                    }
                ],
                "students": []
            }
            ''')

def test_course_year_not_number() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": "1",
                        "shifts": []
                    }
                ],
                "students": []
            }
            ''')

def test_course_year_not_integer() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1.5,
                        "shifts": []
                    }
                ],
                "students": []
            }
            ''')

def test_course_year_not_positive() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": -1,
                        "shifts": []
                    }
                ],
                "students": []
            }
            ''')

def test_course_shifts_not_array() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": 1
                    }
                ],
                "students": []
            }
            ''')

def test_shift_not_object() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            ""
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_shift_missing_keys() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {}
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_shift_type_not_string() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": null,
                                "number": 1,
                                "capacity": 100,
                                "timeslots": []
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_shift_type_not_shift_type() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "Hello, world",
                                "number": 1,
                                "capacity": 100,
                                "timeslots": []
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_shift_number_not_integer() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 12.9,
                                "capacity": 100,
                                "timeslots": []
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_shift_number_not_positive() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": -1,
                                "capacity": 100,
                                "timeslots": []
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_shift_capacity_not_integer() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": true,
                                "timeslots": []
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_shift_capacity_not_positive() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": -1,
                                "timeslots": []
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_timeslots_not_array() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": 100,
                                "timeslots": "Hello"
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_timeslot_not_object() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": -1,
                                "timeslots": [
                                    NaN
                                ]
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_timeslot_missing_keys() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": -1,
                                "timeslots": [
                                    {
                                        "day": "monday",
                                        "end": "10:00"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_timeslot_day_not_string() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": -1,
                                "timeslots": [
                                    {
                                        "day": 42,
                                        "start": "09:00",
                                        "end": "10:00"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_timeslot_unknown_day() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": -1,
                                "timeslots": [
                                    {
                                        "day": "lundi",
                                        "start": "09:00",
                                        "end": "10:00"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_timeslot_start_not_string() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": -1,
                                "timeslots": [
                                    {
                                        "day": "Monday",
                                        "start": null,
                                        "end": "10:00"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_timeslot_end_not_parseable() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": -1,
                                "timeslots": [
                                    {
                                        "day": "Monday",
                                        "start": "09:00",
                                        "end": "24:01"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_students_not_array() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [],
                "students": 42.0
            }
            ''')

def test_student_not_object() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [],
                "students": [
                    true
                ]
            }
            ''')

def test_student_missing_keys() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [],
                "students": [
                    {
                        "number": "A100",
                        "schedule": []
                    }
                ]
            }
            ''')

def test_student_number_not_string() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [],
                "students": [
                    {
                        "number": 100,
                        "year": 1,
                        "enrollments": []
                    }
                ]
            }
            ''')

def test_student_year_not_integer() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [],
                "students": [
                    {
                        "number": "A100",
                        "year": true,
                        "enrollments": []
                    }
                ]
            }
            ''')

def test_student_year_not_positive() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [],
                "students": [
                    {
                        "number": "A100",
                        "year": -1,
                        "enrollments": []
                    }
                ]
            }
            ''')

def test_enrollments_not_array() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": "C1,C2"
                    }
                ]
            }
            ''')

def test_enrollment_not_string() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            {}
                        ]
                    }
                ]
            }
            ''')

def test_schedule_not_array() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": {}
                    }
                ]
            }
            ''')

def test_schedule_shift_not_object() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": [
                            null
                        ]
                    }
                ]
            }
            ''')

def test_schedule_shift_missing_keys() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": [
                            {
                                "shift_number": 2
                            }
                        ]
                    }
                ]
            }
            ''')

def test_schedule_shift_course_not_string() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": [
                            {
                                "course": [],
                                "shift_type": "T",
                                "shift_number": 2
                            }
                        ]
                    }
                ]
            }
            ''')

def test_schedule_shift_type_not_string() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": [
                            {
                                "course": "C1",
                                "shift_type": 42,
                                "shift_number": 2
                            }
                        ]
                    }
                ]
            }
            ''')

def test_schedule_shift_type_not_shift_type() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": [
                            {
                                "course": "C1",
                                "shift_type": "ASDF",
                                "shift_number": 2
                            }
                        ]
                    }
                ]
            }
            ''')

def test_schedule_shift_number_not_integer() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": [
                            {
                                "course": "C1",
                                "shift_type": "T",
                                "shift_number": 2.0
                            }
                        ]
                    }
                ]
            }
            ''')

# Tests for semantic errors

def test_courses_same_id() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": []
                    },
                    {
                        "id": "2",
                        "year": 2,
                        "shifts": []
                    },
                    {
                        "id": "1",
                        "year": 3,
                        "shifts": []
                    }
                ],
                "students": []
            }
            ''')

def test_students_same_number() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": []
                    },
                    {
                        "number": "A200",
                        "year": 2,
                        "enrollments": []
                    },
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [],
                        "schedule": []
                    }
                ]
            }
            ''')

def test_shifts_same_name() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": 50,
                                "timeslots": []
                            },
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": 100,
                                "timeslots": []
                            },
                            {
                                "type": "TP",
                                "number": 1,
                                "capacity": 50,
                                "timeslots": []
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_shift_overlapping_timeslots() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": 100,
                                "timeslots": [
                                    {
                                        "day": "monday",
                                        "start": "09:00",
                                        "end": "11:00"
                                    },
                                    {
                                        "day": "monday",
                                        "start": "10:00",
                                        "end": "12:00"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_timeslot_start_after_end() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": 100,
                                "timeslots": [
                                    {
                                        "day": "Monday",
                                        "start": "10:00",
                                        "end": "09:00"
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "students": []
            }
            ''')

def test_student_courses_schedule_mismatch() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 1,
                                "capacity": 100,
                                "timeslots": []
                            }
                        ]
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [],
                        "schedule": [
                            {
                                "course": "C1",
                                "shift_type": "T",
                                "shift_number": 1
                            }
                        ]
                    }
                ]
            }
            ''')

def test_enrollments_same_id() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1",
                            "C1"
                        ]
                    }
                ]
            }
            ''')

def test_enrollment_bad_reference() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C2"
                        ]
                    }
                ]
            }
            ''')

def test_schedule_shift_unknown_course() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": [
                            {
                                "course": "C9",
                                "shift_type": "T",
                                "shift_number": 1
                            }
                        ]
                    }
                ]
            }
            ''')

def test_schedule_shift_unknown_shift() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": []
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": [
                            {
                                "course": "C1",
                                "shift_type": "T",
                                "shift_number": 1
                            }
                        ]
                    }
                ]
            }
            ''')

def test_schedule_multiple_shifts() -> None:
    with pytest.raises(JsonImporterError):
        import_json_problem_string('''
            {
                "courses": [
                    {
                        "id": "C1",
                        "year": 1,
                        "shifts": [
                            {
                                "type": "T",
                                "number": 1,
                                "capacity": 100,
                                "timeslots": []
                            },
                            {
                                "type": "T",
                                "number": 2,
                                "capacity": 100,
                                "timeslots": []
                            }
                        ]
                    }
                ],
                "students": [
                    {
                        "number": "A100",
                        "year": 1,
                        "enrollments": [
                            "C1"
                        ],
                        "schedule": [
                            {
                                "course": "C1",
                                "shift_type": "T",
                                "shift_number": 1
                            },
                            {
                                "course": "C1",
                                "shift_type": "T",
                                "shift_number": 2
                            }
                        ]
                    }
                ]
            }
            ''')
