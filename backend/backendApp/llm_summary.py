import json
import os
from typing import Any, Dict, Optional

import pandas as pd
from openai import OpenAI

from .test_connection import llm


def extract_key_information_by_llm(
	subject: Optional[str], content: Optional[str], model_name: str = 'meta-llama/Llama-3.3-70B-Instruct'
) -> Dict[str, Any]:
	"""
	Extract structured key information from email content using LLM.
	"""
	api_key = os.getenv('OPEN_AI_TOKEN')

	if not api_key:
		raise ValueError('OPEN_AI_TOKEN environment variable not set')

	client = OpenAI(api_key=api_key, base_url='https://llmlab.plgrid.pl/api/v1')
	text = f'Subject: {subject or "N/A"}\n\nContent: {content or "N/A"}'

	prompt = f"""Extract key information from the following email and return it as JSON with these fields:
- project_name: Name of the project or system (if mentioned)
- key_requirements: Array of key requirements, features, or specifications
- risks: Array of risks, concerns, or issues mentioned
- decisions: Array of decisions made or action items
- technical_details: Array of technical details (APIs, endpoints, databases, architectures)
- stakeholders: Array of people, teams, or departments mentioned
- timeline: Any deadlines, dates, or timeline information (if mentioned)

Email:
{text}

Return only valid JSON, nothing else. If a field has no information, use null or empty array."""

	try:
		response = client.chat.completions.create(
			model=model_name,
			messages=[
				{
					'role': 'system',
					'content': 'You are an expert at extracting structured information from emails. Always return valid JSON.',
				},
				{'role': 'user', 'content': prompt},
			],
			response_format={'type': 'json_object'},
			temperature=0.1,
			max_tokens=100,
		)

		result = json.loads(response.choices[0].message.content)
		return result

	except Exception as e:
		print(f'Error in LLM information extraction: {e}')
		return {}


def add_summary_to_dataframe(
	df: pd.DataFrame,
	subject_column='subject',
	content_column='message_content',
	summary_column='summary',
) -> pd.DataFrame:
	"""
	Add summary column to DataFrame using LLM-based summarization.
	"""
	df = df.copy()
	summaries = []
	skipped_count = 0

	tasks = []

	for _, row in df.iterrows():
		subject = row.get(subject_column)
		content = row.get(content_column)

		if pd.isna(subject) and pd.isna(content):
			summaries.append(None)
			skipped_count += 1
			tasks.append('')
		else:
			tasks.append(
				f"""Extract key information and create a concise summary of the following email.
Focus on:
- Main topic or project
- Key requirements or specifications
- Important decisions or action items
- Risks or concerns mentioned
- Technical details (APIs, systems, integrations)

Email:
{f'Subject: {subject or "N/A"}\n\nContent: {content or "N/A"}'}

Provide a clear, concise summary (2-4 sentences) that captures the essential information."""
			)

	result = llm.batch(tasks)

	summaries: list[str] = [resp.content for resp in result]

	df[summary_column] = summaries

	return df


def add_key_information_to_dataframe(
	df: pd.DataFrame,
	subject_column: str = 'subject',
	content_column: str = 'message_content',
	model_name: str = 'meta-llama/Llama-3.3-70B-Instruct',
) -> pd.DataFrame:
	"""
	Add columns with extracted key information to DataFrame using LLM.
	"""
	df = df.copy()
	df['project_name'] = None
	df['key_requirements'] = None
	df['risks'] = None
	df['decisions'] = None
	df['technical_details'] = None
	df['stakeholders'] = None
	df['timeline'] = None

	for idx, row in df.iterrows():
		subject = row.get(subject_column)
		content = row.get(content_column)

		if pd.isna(subject) and pd.isna(content):
			continue

		extracted = extract_key_information_by_llm(subject, content, model_name=model_name)

		if extracted:
			df.at[idx, 'project_name'] = extracted.get('project_name')
			df.at[idx, 'key_requirements'] = extracted.get('key_requirements', [])
			df.at[idx, 'risks'] = extracted.get('risks', [])
			df.at[idx, 'decisions'] = extracted.get('decisions', [])
			df.at[idx, 'technical_details'] = extracted.get('technical_details', [])
			df.at[idx, 'stakeholders'] = extracted.get('stakeholders', [])
			df.at[idx, 'timeline'] = extracted.get('timeline')

	return df
