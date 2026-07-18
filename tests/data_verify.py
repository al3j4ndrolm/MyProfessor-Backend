_EMPTY_VALUES_ALLOWED_KEYS = {"tag", "time", "location"}

def _assert_no_empty_values(data: dict) -> None:
    """
    Assert that no string/list/dict value in the given dict is empty, except under the "tag",
    "time", or "location" keys (some meetings genuinely have no fixed time/room, e.g. async
    online sections).
    """
    for key, value in data.items():
        if key in _EMPTY_VALUES_ALLOWED_KEYS:
            continue
        if isinstance(value, (str, list, dict)):
            assert value, f"'{key}' should not be empty, got {value!r}"

def verify_data_structure_classes_all_departments(classes_all_departments: dict):
    """
    Verify the structure of the schedules for all departments.
    """
    for department, classes_per_department in classes_all_departments.items():
        assert isinstance(department, str)
        assert department, "department should not be empty"
        assert isinstance(classes_per_department, dict)
        assert classes_per_department, f"classes for department '{department}' should not be empty"
        verify_data_structure_classes_per_department(classes_per_department)

def verify_data_structure_classes_per_department(classes_per_department: dict):
    """
    Verify the structure of the classes per department.
    """
    for course, classes_per_course in classes_per_department.items():
        assert isinstance(course, str)
        assert course, "course should not be empty"
        assert isinstance(classes_per_course, dict)
        assert classes_per_course, f"classes for course '{course}' should not be empty"
        verify_data_structure_classes_per_course(classes_per_course)

def verify_data_structure_classes_per_course(classes_per_course: dict):
    """
    Verify the structure of the classes per course.
    """
    for professor_identifier, professor_data in classes_per_course.items():
        assert isinstance(professor_identifier, str)
        assert " email:" in professor_identifier
        assert isinstance(professor_data, dict)
        assert professor_data, f"professor data for '{professor_identifier}' should not be empty"
        verify_data_structure_classes_per_professor(professor_data)

def verify_data_structure_classes_per_professor(professor_data: dict):
    """
    Verify the structure of professor data.
    """
    assert isinstance(professor_data["hasEmail"], bool)
    assert isinstance(professor_data["classes"], list)
    assert professor_data["classes"], "'classes' should not be empty"
    for class_data in professor_data["classes"]:
        verify_data_structure_per_class(class_data)

def verify_data_structure_per_class(class_data: dict):
    """
    Verify the structure of class data.
    """
    assert isinstance(class_data["classCrn"], str)
    assert isinstance(class_data["meetings"], list)
    _assert_no_empty_values(class_data)
    for meeting in class_data["meetings"]:
        verify_data_structure_per_meeting(meeting)

def verify_data_structure_per_meeting(meeting: dict):
    """
    Verify the structure of meeting data.
    """
    assert isinstance(meeting["tag"], str)
    assert isinstance(meeting["days"], str)
    assert isinstance(meeting["time"], str)
    assert isinstance(meeting["location"], str)
    _assert_no_empty_values(meeting)

def verify_data_structure_courses_set(courses_set: set):
    """
    Verify the structure of courses set.
    Each course should be in format "COURSE_CODE - Course Title"
    """
    
    for course in courses_set:
        assert isinstance(course, str)
        assert " - " in course, f"Course '{course}' should contain ' - ' separator"
        
        # Split by " - " to get course code and title
        parts = course.split(" - ", 1)
        assert len(parts) == 2, f"Course '{course}' should have exactly one ' - ' separator"
        
        course_code = parts[0].strip()
        course_title = parts[1].strip()
        
        # Verify course code is not empty
        assert course_code, f"Course code should not be empty in '{course}'"
        
        # Verify course title is not empty
        assert course_title, f"Course title should not be empty in '{course}'"
        
        # Verify course code format (should contain department code and number)
        assert " " in course_code, f"Course code '{course_code}' should contain space between department and number"

def verify_data_structure_courses_map(courses_map: dict):
    """
    Verify the structure of courses map.
    Each key should be a course code and each value should be a list of course strings.
    Each course string should be in format "COURSE_CODE - Course Title"
    """
    assert isinstance(courses_map, dict)
    
    for course_code, courses_list in courses_map.items():
        # Verify course code is a string
        assert isinstance(course_code, str)
        assert course_code, f"Course code should not be empty"
        
        # Verify courses_list is a list
        assert isinstance(courses_list, set) 
        verify_data_structure_courses_set(courses_list)

