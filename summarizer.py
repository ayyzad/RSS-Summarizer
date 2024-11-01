import json
from openai import OpenAI
from config import OPENAI_API_KEY, SYSTEM_PROMPT, SUMMARY_PROMPT
from logger import setup_logger

logger = setup_logger(__name__)

class Summarizer:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("Initialized Summarizer")

    def summarize(self, text):
        logger.debug(f"Starting summarization of text (length: {len(text)})")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{SUMMARY_PROMPT}\n\n{text}"}
                ],
                max_tokens=250,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            try:
                result = json.loads(response.choices[0].message.content)
                if not isinstance(result, dict) or 'summary' not in result or 'category' not in result:
                    raise ValueError("Invalid response format")
                logger.debug(f"Successfully generated summary and category: {result['category']}")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error in summarization: {str(e)}")
            return None