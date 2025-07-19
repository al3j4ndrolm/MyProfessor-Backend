
import json

<<<<<<< Updated upstream
<<<<<<< Updated upstream

=======
=======
>>>>>>> Stashed changes
<<<<<<< HEAD
=======

>>>>>>> d59aa3e62d23c8e501e9418a7b7cc76a80c770b1
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
=======

>>>>>>> Stashed changes
    print(json.dumps(create_courses_data("ACCT - Accounting", ["ACCT 64 - Payroll and Business Tax Accounting", "ACCT 1C - Managerial Accounting"]), indent=2))

