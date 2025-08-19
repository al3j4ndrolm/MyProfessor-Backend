import os

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

DEEPSEEK_SYSTEM_PROMPT = """
You are a helpful assistant that summarizes professor reviews.
"""


# how to do a response example:

# response = DEEPSEEK_CLIENT.create(
#     model=DEEPSEEK_MODEL,
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"}, -> the promp we want to send to the model
#         {"role": "user", "content": "Hello"}, -> data 
#     ],
#     stream=False -> is set to false because we want to get the full response, set to true if we want to get the response in chunks
# )
