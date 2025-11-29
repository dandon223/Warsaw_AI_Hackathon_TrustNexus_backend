"""
Module for extracting key information and generating summaries from email messages using LLM.
"""

import os
import pandas as pd
from dotenv import load_dotenv
# load_dotenv()


def summarize_by_llm(subject, content, model_name="meta-llama/Llama-3.3-70B-Instruct", max_tokens=100):
    """
    Generate a summary of email content using LLM (OpenAI).
    
    Args:
        subject: Email subject line
        content: Email message content
        model_name: OpenAI model to use
        max_tokens: Maximum tokens for summary
    
    Returns:
        Summary string
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("openai package is required. Install with: pip install openai")
    
    api_key = os.getenv("OPEN_AI_TOKEN")

    if not api_key:
        raise ValueError("OPEN_AI_TOKEN environment variable not set")
    
    client = OpenAI(api_key=api_key, base_url="https://llmlab.plgrid.pl/api/v1",  timeout=50)
    # client = OpenAI(base_url="https://llmlab.plgrid.pl/api/v1")

    
    # Prepare text
    text = f"Subject: {subject or 'N/A'}\n\nContent: {content or 'N/A'}"
    #print(text)

    # Build prompt for summary
    prompt = f"""Extract key information and create a concise summary of the following email.
Focus on:
- Main topic or project
- Key requirements or specifications
- Important decisions or action items
- Risks or concerns mentioned
- Technical details (APIs, systems, integrations)

Email:
{text}

Provide a clear, concise summary (2-4 sentences) that captures the essential information."""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert at extracting key information from emails and creating concise summaries."},
                {"role": "user", "content": prompt}
                            ],
            temperature=0.3,
            max_tokens=max_tokens
        )
        
        summary = response.choices[0].message.content.strip()
        #print(summary)
        return summary
            
    except Exception as e:
        print(f"Error in LLM summarization: {e}")
        return None


def extract_key_information_by_llm(subject, content, model_name="meta-llama/Llama-3.3-70B-Instruct"):
    """
    Extract structured key information from email content using LLM.
    
    Args:
        subject: Email subject line
        content: Email message content
        model_name: OpenAI model to use
    
    Returns:
        Dictionary with extracted information
    """
    try:
        from openai import OpenAI
        import json
    except ImportError:
        raise ImportError("openai package is required. Install with: pip install openai")
    
    api_key = os.getenv("OPEN_AI_TOKEN")

    if not api_key:
        raise ValueError("OPEN_AI_TOKEN environment variable not set")
    
    client = OpenAI(api_key=api_key, base_url="https://llmlab.plgrid.pl/api/v1")
    
    # Prepare text
    text = f"Subject: {subject or 'N/A'}\n\nContent: {content or 'N/A'}"
    
    # Build prompt for structured extraction
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
                 {"role": "system", "content": "You are an expert at extracting structured information from emails. Always return valid JSON."},
                 {"role": "user", "content": prompt}
                #{"role": "user", "content": "Say Hi to me!"}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=100#500
        )
        
        result = json.loads(response.choices[0].message.content)
        #print(result)
        return result
            
    except Exception as e:
        print(f"Error in LLM information extraction: {e}")
        return {}


def add_summary_to_dataframe(
    df,
    subject_column='subject',
    content_column='message_content',
    summary_column='summary',
    model_name="meta-llama/Llama-3.3-70B-Instruct",
    max_tokens=100
):
    """
    Add summary column to DataFrame using LLM-based summarization.
    
    Args:
        df: DataFrame with email data
        subject_column: Name of subject column
        content_column: Name of content column
        summary_column: Name of summary column to create
        model_name: OpenAI model name to use
        max_tokens: Maximum tokens for summary
    
    Returns:
        DataFrame with added summary column
    """
    df = df.copy()
    
    summaries = []
    for idx, row in df.iterrows():
        subject = row.get(subject_column)
        content = row.get(content_column)
        
        # Skip if both subject and content are empty
        if pd.isna(subject) and pd.isna(content):
            summaries.append(None)
            continue
        
        summary = summarize_by_llm(subject, content, model_name=model_name, max_tokens=max_tokens)
        summaries.append(summary)
    
    df[summary_column] = summaries
    return df


def add_key_information_to_dataframe(
    df,
    subject_column='subject',
    content_column='message_content',
    model_name="meta-llama/Llama-3.3-70B-Instruct"
):
    """
    Add columns with extracted key information to DataFrame using LLM.
    
    Args:
        df: DataFrame with email data
        subject_column: Name of subject column
        content_column: Name of content column
        model_name: OpenAI model name to use
    
    Returns:
        DataFrame with added columns: project_name, key_requirements, risks, 
        decisions, technical_details, stakeholders, timeline
    """
    df = df.copy()
    
    # Initialize new columns
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
        
        # Skip if both subject and content are empty
        if pd.isna(subject) and pd.isna(content):
            continue
        
        extracted = extract_key_information_by_llm(subject, content, model_name=model_name)
        
        # Fill in the extracted information
        if extracted:
            df.at[idx, 'project_name'] = extracted.get('project_name')
            df.at[idx, 'key_requirements'] = extracted.get('key_requirements', [])
            df.at[idx, 'risks'] = extracted.get('risks', [])
            df.at[idx, 'decisions'] = extracted.get('decisions', [])
            df.at[idx, 'technical_details'] = extracted.get('technical_details', [])
            df.at[idx, 'stakeholders'] = extracted.get('stakeholders', [])
            df.at[idx, 'timeline'] = extracted.get('timeline')
    
    return df


# Example usage
if __name__ == "__main__":
    # Import from the same package
    try:
        from .emails import parse_mails_to_dataframe
    except ImportError:
        # Fallback for direct execution
        from emails import parse_mails_to_dataframe
    load_dotenv()
    
    # Parse emails
    print("Parsing emails...")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    df = parse_mails_to_dataframe(DATA_DIR)
    print(f"Parsed {len(df)} messages")

    
    # Add summary column
    print("\nGenerating summaries...")
    df_with_summary = add_summary_to_dataframe(df, model_name="meta-llama/Llama-3.3-70B-Instruct")
    print(f"\nAdded summary column")
    print(df_with_summary[['subject', 'summary']].head())
    
    # Optionally, add structured key information
    # print("\nExtracting key information...")
    # df_with_info = add_key_information_to_dataframe(df, model_name="meta-llama/Llama-3.3-70B-Instruct")
    # print(f"\nAdded key information columns")
    # print(df_with_info[['subject', 'project_name', 'key_requirements']].head())

