from .configs import DEEPSEEK_SYSTEM_PROMPT, DEEPSEEK_MODEL, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from data_fetchers.rmp.reviews.reviews import get_reviews, get_session
from logger import logger
from openai import OpenAI
import json

def get_summary(reviews_data: list[dict], deepseek_client) -> dict:
    response = deepseek_client.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(reviews_data)},
        ],
        stream=False
    )
    try:
        return response.choices[0].message.content 
    except Exception as e:
        logger.error(f"Unable to get summary from DeepSeek: {e}")
        return {}

def create_deepseek_client():
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL).chat.completions
