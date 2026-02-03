"""
Prompt engineering basic examples.
"""

def simple_prompt():
    return "Explain Generative AI in simple terms."


def role_prompt():
    return (
        "You are a senior software engineer. "
        "Explain why clean code is important."
    )


if __name__ == "__main__":
    print(simple_prompt())
    print(role_prompt())
