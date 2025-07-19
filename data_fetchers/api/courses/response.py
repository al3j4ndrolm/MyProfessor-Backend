
import json

def create_courses_data(department_name: str, courses_full_name_list: list) -> dict:
    """
    Example of return value:
    {
    "ACCT - Accounting": [
        "ACCT 64 - Payroll and Business Tax Accounting",
        "ACCT 1C - Managerial Accounting",
        "ACCT 58 - Auditing",
        ], ...
    }
    """

    return {
        department_name: courses_full_name_list
    }


if __name__ == "__main__":  
    print(json.dumps(create_courses_data("ACCT - Accounting", ["ACCT 64 - Payroll and Business Tax Accounting", "ACCT 1C - Managerial Accounting"]), indent=2))

