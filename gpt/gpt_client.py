from openai import OpenAI
from config.config import GPT_TOKEN


def create_client() -> OpenAI:
    client = OpenAI(
        api_key=GPT_TOKEN,
        base_url='https://api.avalai.ir/v1'
    )
    return client


gpt_client = create_client()
