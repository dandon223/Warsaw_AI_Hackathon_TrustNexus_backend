from openai import OpenAI

from .models import Email
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://llmlab.plgrid.pl/api/v1",
)

# response = client.chat.completions.create(
#     model="meta-llama/Llama-3.3-70B-Instruct",
#     messages=[{"role": "user", "content": f"Hej jak sie nazywasz?"}],
# )

# print(response.choices[0].message.content)


def query_llm(prompt: str, emails: list[Email]) -> str:
    prompt = f"""
You are an expert assistant analyzing internal email data.
Use ONLY the provided email context.


### EMAIL CONTEXT
emails = {emails}


### USER REQUEST
{prompt}


### REQUIREMENTS
- Provide accurate factual analysis.
- Do not fabricate missing data.
- Cite email IDs in your explanation.
"""
    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content