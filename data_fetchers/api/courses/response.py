
import json


def create_courses_data(department_name: str, courses_full_name_list: list) -> dict:
    """
    Example of return value:
    {
    "ACCT - Accounting": [
        "ACCT 64 - Payroll and Business Tax Accounting",
        "ACCT 1C - Managerial Accounting",
        "ACCT 58 - Auditing",
        "ACCT 67 - Individual Income Taxation",
        "ACCT 88 - Excel Spreadsheets for Accounting",
        "ACCT 52 - Advanced Accounting",
        "ACCT 1A - Financial Accounting I",
        "ACCT 66 - Cost Accounting",
        "ACCT 74 - Accounting Ethics",
        "ACCT 1B - Financial Accounting II",
        "ACCT 51A - Intermediate Accounting I",
        "ACCT 68 - Advanced Tax Accounting",
        "ACCT 87AI - Computerized Accounting Programs I (Quickbooks)"
        ], ...
    }
    """

    return {
        department_name: courses_full_name_list
    }


if __name__ == "__main__":  
    print(json.dumps(create_courses_data("ACCT - Accounting", ["ACCT 64 - Payroll and Business Tax Accounting", "ACCT 1C - Managerial Accounting"]), indent=2))

