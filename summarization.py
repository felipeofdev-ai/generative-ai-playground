"""
Text summarization example.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize(text: str) -> str:
    prompt = f"Summarize the following text:\n{text}"
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    return response.output_text


if __name__ == "__main__":
    sample = (
        "Generative AI systems can create text, images, audio, "
        "and other content based on learned patterns."
    )
    print(summarize(sample))
