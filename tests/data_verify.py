def verify_data_structure_schedules_all_departments(schedules_all_departments: dict):
    """
    Verify the structure of the schedules for all departments.
    """
    for department, schedules_per_department in schedules_all_departments.items():
        assert isinstance(department, str)
        assert isinstance(schedules_per_department, dict)
        verify_data_structure_schedules_per_department(schedules_per_department)

def verify_data_structure_schedules_per_department(schedules_per_department: dict):
    """
    Verify the structure of the schedules per department.
    """
    for course, course_schedules in schedules_per_department.items():
        assert isinstance(course, str)
        assert isinstance(course_schedules, dict)
        verify_data_structure_schedules_per_course(course_schedules)

def verify_data_structure_schedules_per_course(course_schedules: dict):
    """
    Verify the structure of the schedules per course.
    """
    for professor, professor_schedules in course_schedules.items():
        assert isinstance(professor, str)
        assert isinstance(professor_schedules, dict)
        verify_data_structure_schedules_per_professor(professor_schedules)

def verify_data_structure_schedules_per_professor(professor_schedules: dict):
    """
    Verify the structure of the schedules per professor.
    """
    assert isinstance(professor_schedules["hasEmail"], bool)
    assert isinstance(professor_schedules["classes"], list)
    if "email" in professor_schedules:
        assert isinstance(professor_schedules["email"], str)
    for class_schedules in professor_schedules["classes"]:
        verify_data_structure_schedules_per_class(class_schedules)
    
def verify_data_structure_schedules_per_class(class_schedules: dict):
    """
    Verify the structure of the schedules per class.
    """
    assert isinstance(class_schedules["classCrn"], str)
    assert isinstance(class_schedules["meetings"], list)
    for meeting in class_schedules["meetings"]:
        verify_data_structure_schedules_per_meeting(meeting)

def verify_data_structure_schedules_per_meeting(meeting: dict):
    """
    Verify the structure of the schedules per meeting.
    """
    assert isinstance(meeting["tag"], str)
    assert isinstance(meeting["days"], str)
    assert isinstance(meeting["time"], str)
    assert isinstance(meeting["location"], str)
