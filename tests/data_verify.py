def verify_data_structure_classes_all_departments(classes_all_departments: dict):
    """
    Verify the structure of the schedules for all departments.
    """
    for department, classes_per_department in classes_all_departments.items():
        assert isinstance(department, str)
        assert isinstance(classes_per_department, dict)
        verify_data_structure_classes_per_department(classes_per_department)

def verify_data_structure_classes_per_department(classes_per_department: dict):
    """
    Verify the structure of the classes per department.
    """
    for course, classes_per_course in classes_per_department.items():
        assert isinstance(course, str)
        assert isinstance(classes_per_course, dict)
        verify_data_structure_classes_per_course(classes_per_course)

def verify_data_structure_classes_per_course(classes_per_course: dict):
    """
    Verify the structure of the classes per course.
    """
    for professor_identifier, professor_data in classes_per_course.items():
        assert isinstance(professor_identifier, str)
        assert " email:" in professor_identifier
        assert isinstance(professor_data, dict)
        verify_data_structure_classes_per_professor(professor_data)

def verify_data_structure_classes_per_professor(professor_data: dict):
    """
    Verify the structure of professor data.
    """
    assert isinstance(professor_data["hasEmail"], bool)
    assert isinstance(professor_data["classes"], list)
    for class_data in professor_data["classes"]:
        verify_data_structure_per_class(class_data)
    
def verify_data_structure_per_class(class_data: dict):
    """
    Verify the structure of class data.
    """
    assert isinstance(class_data["classCrn"], str)
    assert isinstance(class_data["meetings"], list)
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
