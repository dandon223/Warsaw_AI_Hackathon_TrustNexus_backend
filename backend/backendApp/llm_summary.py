"""
Module for extracting key information and generating summaries from email messages using LLM.
"""

import pandas as pd
import logging
from datetime import datetime
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

from .test_connection import llm


# Configure logging to both console and file
def setup_logging(log_dir=None):
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Configure logging with both file and console handlers
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),  # Also output to console
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized.")
    return logger


# Initialize logging
logger = setup_logging()


class EmailInput(BaseModel):
    subject: str = Field(..., description="Subject of the email")
    content: str = Field(..., description="Content/body of the email")


class EmailSummary(BaseModel):
    summary: str = Field(..., description="Concise summary of the email")
    category: str | None = Field(
        None,
        description="Category of the email - you can choose widely used categories",
    )


parser = JsonOutputParser(pydantic_object=EmailSummary)
template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You analyze emails and return structured JSON.
TASK:
Extract key information and create a concise summary of the following email.
Focus on:
- Main topic or project
- Key requirements or specifications
- Important decisions or action items
- Risks or concerns mentioned
- Technical details (APIs, systems, integrations)

Return only valid JSON, nothing else. If a field has no information, use null or empty array.
""",
        ),
        (
            "human",
            """
Email:

SUBJECT: {subject}
CONTENT: {content}

Return ONLY JSON:
{format_instructions}
""",
        ),
    ]
).partial(
    format_instructions=parser.get_format_instructions(),
    input_variables=["subject", "content"],
)

chain = template | llm | parser


def enhance_subject_or_content(subject_or_content) -> str:
    return subject_or_content if subject_or_content else "N/A"


def merge_model_results_with_skipped(skipped_indices, results):
    total_rows = len(skipped_indices) + len(results)
    skipped = set(skipped_indices)
    res_iter = iter(results)

    return [None if i in skipped else next(res_iter) for i in range(total_rows)]


def add_model_results_to_df(df, merged_results):
    """
    Adds model results (like EmailSummary) to a DataFrame, preserving skipped rows.

    Args:
        df (pd.DataFrame): Original DataFrame.
        merged_results (list): List of EmailSummary or None, aligned with df.
        prefix (str): Optional prefix for new column names.

    Returns:
        pd.DataFrame: DataFrame with new columns for each field in EmailSummary.
    """
    records = []
    for res in merged_results:
        if res is None:
            records.append(
                {
                    "summary": None,
                    "project_name": None,
                    "key_requirements": [],
                    "risks": [],
                    "decisions": [],
                    "technical_details": [],
                    "stakeholders": [],
                    "timeline": None,
                    "category": None,
                }
            )
        else:
            records.append(res)

    result_df = pd.DataFrame(records)

    return pd.concat([df.reset_index(drop=True), result_df], axis=1)


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

    total_emails = len(df)
    logger.info(f"Starting to add summaries to DataFrame with {total_emails} emails")
    logger.info(f"Using model: {model_name}, max_tokens: {max_tokens}")

    summaries = []
    skipped_count = 0

    skipped_emails_indices = []
    tasks = []
    for idx, row in df.iterrows():
        current_num = len(summaries) + 1
        progress_pct = (current_num / total_emails) * 100

        subject = row.get(subject_column)
        content = row.get(content_column)

        # Skip if both subject and content are empty
        if pd.isna(subject) and pd.isna(content):
            logger.debug(
                f"Email {current_num}/{total_emails} ({progress_pct:.1f}%): Skipping - empty subject and content"
            )
            skipped_emails_indices.append(idx)
            skipped_count += 1
        else:
            tasks.append(
                {
                    "subject": enhance_subject_or_content(subject),
                    "content": enhance_subject_or_content(content),
                }
            )

    result = chain.batch(tasks)

    merged_results = merge_model_results_with_skipped(
        skipped_indices=skipped_emails_indices, results=result
    )

    df_with_summaries = add_model_results_to_df(df, merged_results)

    successful_count = sum(1 for s in summaries if s is not None)
    logger.info(f"Summary generation completed!")
    logger.info(f"  Total emails: {total_emails}")
    logger.info(f"  Successful: {successful_count}")
    logger.info(f"  Skipped (empty): {skipped_count}")
    logger.info(f"  Failed: {total_emails - successful_count - skipped_count}")

    return df_with_summaries
