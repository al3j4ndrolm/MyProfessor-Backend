
import json

def create_courses_data(department_name: str, courses_names: set) -> dict:
    """
    Example of return value:
    {
        "ACCT - Accounting": [
            "ACCT 64 - Payroll and Business Tax Accounting",
            "ACCT 1C - Managerial Accounting",
            ...
        ],
        "BIO - Biology": [
            "BIO 10 - Introduction to Biology",
            "BIO 11 - Introduction to Biology Lab",
            ...
        ],  
        ...
    } 
    """

    return {
        department_name: sorted(list(courses_names))
    }


if __name__ == "__main__":  
    print(json.dumps(create_courses_data("ACCT - Accounting", ["ACCT 64 - Payroll and Business Tax Accounting", "ACCT 1C - Managerial Accounting"]), indent=2))

