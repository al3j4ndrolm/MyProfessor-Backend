from configs import DEEPSEEK_SYSTEM_PROMPT, DEEPSEEK_MODEL, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from logger import logger
from openai import OpenAI

def get_summary(reviews_data: list[dict], deepseek_client):

    response = deepseek_client.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT},
            {"role": "user", "content": reviews_data},
        ],
        stream=False
    )
    try:
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error: {e}")
        return "Error: " + str(e)

def create_deepseek_client():
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL).chat.completions

    