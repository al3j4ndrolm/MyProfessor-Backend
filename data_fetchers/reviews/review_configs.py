import requests

RMP_BASE_URL = "https://www.ratemyprofessors.com"

SESSION = requests.Session()
SESSION.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    })

REVIEW_LIMIT = 100