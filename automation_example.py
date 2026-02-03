"""
Simple AI-powered automation example.
"""

from text_generation import generate_text

def automated_reply(topic: str) -> str:
    prompt = f"Generate a professional explanation about {topic}."
    return generate_text(prompt)


if __name__ == "__main__":
    print(automated_reply("Generative AI in business"))
