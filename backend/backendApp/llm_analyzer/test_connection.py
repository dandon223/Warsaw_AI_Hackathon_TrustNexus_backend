from openai import OpenAI

client = OpenAI(
    base_url="https://llmlab.plgrid.pl/api/v1",
)

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct",
    messages=[{"role": "user", "content": f"Hej jak sie nazywasz?"}],
)

print(response.choices[0].message.content)
