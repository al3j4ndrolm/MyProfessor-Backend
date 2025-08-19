from configs import DEEPSEEK_CLIENT, DEEPSEEK_SYSTEM_PROMPT, DEEPSEEK_MODEL

def get_summary(reviews_data: list[dict]):

    response = DEEPSEEK_CLIENT.create(
        model=DEEPSEEK_MODEL,
        messages=[
            {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT},
            {"role": "user", "content": reviews_data},
        ],
        stream=False
    )
    
    return response.choices[0].message.content