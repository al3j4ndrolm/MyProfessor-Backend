from data_fetchers.api.terms.configs import TERM_NAME_KEY, TERM_CODE_KEY
import json

def create_term_response_data(term_name: str, term_code: str) -> dict:
    """
    Example of return value: {
        "term_name": "Fall 2025",
        "term_code": "F2025"
    }
    """

    return {    
        TERM_NAME_KEY: term_name,
        TERM_CODE_KEY: term_code,
    }

if __name__ == "__main__":
    print(json.dumps(create_term_response_data("Fall 2025", "F2025"), indent=2))
