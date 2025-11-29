from pprint import pprint
from openai import OpenAI

from .models import Email
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(base_url="https://llmlab.plgrid.pl/api/v1", model="meta-llama/Llama-3.3-70B-Instruct", temperature=0)


def query_llm(prompt: str, emails: list[dict]) -> str:
    context_prompt = ChatPromptTemplate.from_template(
    "You are an expert assistant analyzing internal email data. Use ONLY the provided email context."
    "\n\nRetrieved Context: {context}"
    "\n\nUser Question: {question}"
)
    
    chain = (
    {
        'context': (lambda x: str(emails[:10])) ,
        'question': (lambda x:x)
    }
    | context_prompt
    | llm
    | StrOutputParser()
)
    response = chain.invoke(prompt)

    return response