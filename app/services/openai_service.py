from openai import OpenAI
from pydantic import BaseModel
from app.schemas import openai_schemas

"""
Service used primarily to interact with the OpenAI API
and OpenAI's various models.

Much more functionality to be added soon as needed,
along with Anthropic and Gemini services.
"""
class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def handle_message(self, system_prompt: str, user_prompt: str, response_format: type[BaseModel] = openai_schemas.DefaultLLMOutput):
        response = self.client.responses.parse(
            model="gpt-4o",
            input=[
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            text_format=response_format
        )
        return { "input message" : user_prompt, "response" : response.output_parsed }