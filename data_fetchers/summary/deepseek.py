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
        
        try:
            result = response.choices[0].message.content
        except Exception as e:
            logger.error(f"Failed to get summary from DeepSeek: {e}")
            return None
        
        # Add assistant response to conversation
        self.conversation_history.append({
            "role": "assistant",
            "content": result
        })

        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse response: {result}")
                return None
        else:
            return result
    
    def reset_conversation(self):
        """Reset conversation but keep system prompt"""
        self.conversation_history = [
            {"role": "system", "content": DEEPSEEK_SYSTEM_PROMPT}
        ]

if __name__ == "__main__":
    deepseek_session = DeepSeekSession()
    session = get_session()
    reviews = get_reviews(professor_rmp_link="professor/89065", school_name="", session=session)
    summary = deepseek_session.get_summary(reviews)
    print(summary)