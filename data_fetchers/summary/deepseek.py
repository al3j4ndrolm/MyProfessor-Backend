from .configs import DEEPSEEK_SYSTEM_PROMPT, DEEPSEEK_MODEL, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from data_fetchers.rmp.reviews.reviews import get_reviews, get_session
from logger import logger
from openai import OpenAI
import json

class DeepSeekSession:
    def __init__(self):
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL).chat.completions
        self.model = DEEPSEEK_MODEL
        self.conversation_history = [{"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT}]
    
    def get_summary(self, reviews_data: list[dict]) -> dict:
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user", 
            "content": json.dumps(reviews_data)
        })
        
        response = self.client.create(
            model=self.model,
            messages=self.conversation_history,
            stream=False
        )
        
        # Add assistant response to conversation
        self.conversation_history.append({
            "role": "assistant",
            "content": response.choices[0].message.content
        })

        if isinstance(response.choices[0].message.content, str):
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return {"error": "Failed to parse response " + response.choices[0].message.content}
        else:
            return response.choices[0].message.content
    
    def reset_conversation(self):
        """Reset conversation but keep system prompt"""
        self.conversation_history = [
            {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT}
        ]
