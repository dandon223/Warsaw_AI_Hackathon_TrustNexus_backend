import glob
import json
import os
import pathlib
import re
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .models import Email, LLMAnalysis


def read_files_data(data_dir: pathlib.Path) -> List[str]:
	"""
	Read mail data from .txt files in the specified directory.
	"""
	files_data = []

	# Search for all .txt files recursively
	path = os.path.join(data_dir, '**', '*.txt')
	files = glob.glob(path, recursive=True)

	# If no files found with recursive search, try non-recursive
	if not files:
		path = os.path.join(data_dir, '*.txt')
		files = glob.glob(path)

	# Read all .txt files
	for file_path in files:
		try:
			with open(file_path, 'r', encoding='utf-8') as mail:
				content = mail.read().strip()
				if content:  # Only add non-empty files
					files_data.append(content)
		except Exception as e:
			print(f'Error reading file {file_path}: {e}')
			continue

	if not files_data:
		print(f'No .txt files found in {data_dir}')

	return files_data


def parse_sender(sender_string: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
	"""
	Parse sender string into name and email.
	"""
	if not sender_string:
		return None, None

	# Pattern: "Name <email@domain.com>" or just "email@domain.com"
	match = re.match(r'^(.+?)\s*<(.+?)>$', sender_string.strip())
	if match:
		name = match.group(1).strip()
		email = match.group(2).strip()
		return name, email
	else:
		# Check if it's just an email
		email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
		if re.match(email_pattern, sender_string.strip()):
			return None, sender_string.strip()
		else:
			# Assume it's a name without email
			return sender_string.strip(), None


def parse_single_file(file_content: str) -> List[Dict[str, Any]]:
	"""
	Parse a single mail content string into individual email messages.
	"""
	messages: List[Dict[str, Any]] = []

	# Split by "Od: " to separate individual messages
	message_parts = re.split(r'(?=^Od: )', file_content, flags=re.MULTILINE)

	# Skip the first part if it's empty or doesn't contain a message
	for part in message_parts:
		if not part.strip():
			continue

		# Extract sender
		sender_match = re.search(r'^Od:\s+(.+?)(?:\n|$)', part, re.MULTILINE)
		sender_raw = sender_match.group(1).strip() if sender_match else None

		# Parse sender into name and email
		sender_name, sender_email = parse_sender(sender_raw) if sender_raw else (None, None)

		# Extract date
		date_match = re.search(r'Wysłano:\s+(.+?)(?:\n|$)', part, re.MULTILINE)
		date = date_match.group(1).strip() if date_match else None

		# Extract recipient
		recipient_match = re.search(r'Do:\s+(.+?)(?:\n|$)', part, re.MULTILINE)
		recipient_raw = recipient_match.group(1).strip() if recipient_match else None

		# Handle multiple recipients (comma-separated) - take the first one
		if recipient_raw:
			# Split by comma and take the first recipient
			first_recipient = recipient_raw.split(',')[0].strip()
			recipient_name, recipient_email = parse_sender(first_recipient)
		else:
			recipient_name, recipient_email = None, None

		# Extract subject
		subject_match = re.search(r'Temat:\s+(.+?)(?:\n|$)', part, re.MULTILINE)
		subject = subject_match.group(1).strip() if subject_match else None

		# Extract main content
		# Find the line after "Temat:" and extract everything until the next "Od:" or end
		content_match = re.search(r'Temat:\s+.+?\n\n(.+?)(?=\n\nOd:\s+|$)', part, re.DOTALL)
		if not content_match:
			# Try to find content after the last header field
			content_match = re.search(r'Temat:\s+.+?\n\n(.+)', part, re.DOTALL)

		if content_match:
			content = content_match.group(1).strip()
			# Remove signature (everything after "--")
			content = re.split(r'\n--\n', content)[0].strip()
		else:
			content = None

		# Only add message if we have at least one of the folowing
		if sender_name or sender_email or recipient_name or recipient_email or content:
			messages.append(
				{
					'sender_name': sender_name,
					'sender_email': sender_email,
					'recipient_name': recipient_name,
					'recipient_email': recipient_email,
					'subject': subject,
					'date': date,
					'message_content': content,
				}
			)

	return messages


def parse_mails_to_dataframe(data_dir: pathlib.Path) -> pd.DataFrame:
	"""
	Parse all mail data from .txt files into a pandas DataFrame.
	"""
	files_data = read_files_data(data_dir)
	all_messages = []

	# Parse each mail file
	for file_data in files_data:
		messages = parse_single_file(file_data)
		all_messages.extend(messages)

	df = pd.DataFrame(all_messages)

	return df


def emails_to_csv(data_dir=pathlib.Path) -> None:
	"""
	Saves parsed emails to csv
	"""
	emails = Email.objects.all()

	# Convert queryset to list of dictionaries
	email_list = []
	for e in emails:
		email_dict = {
			'id': str(e.id),  # UUID to string
			'sender_name': e.sender_name,
			'sender_email': e.sender_email,
			'recipient_name': e.recipient_name,
			'recipient_email': e.recipient_email,
			'subject': e.subject,
			'date': e.date,
			'message_content': e.message_content,
			'summary': e.summary,
			'created_at': e.created_at.isoformat() if e.created_at else None,
		}
		email_list.append(email_dict)

	# Save to JSON file
	with open(data_dir + '/emails.json', 'w', encoding='utf-8') as f:
		json.dump(email_list, f, ensure_ascii=False, indent=4)


def analysis_to_csv(data_dir=pathlib.Path) -> None:
	analysis = LLMAnalysis.objects.all()
	analysis_list = []
	for e in analysis:
		analysis_dict = {
			'id': str(e.id),  # UUID to string
			'question': e.question,
			'answer': e.answer,
		}
		analysis_list.append(analysis_dict)

	# Save to JSON file
	with open(data_dir + '/analysis.json', 'w', encoding='utf-8') as f:
		json.dump(analysis_list, f, ensure_ascii=False, indent=4)
