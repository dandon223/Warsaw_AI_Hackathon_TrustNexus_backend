import re
import pandas as pd
from read_mails import read_mails_data


def parse_single_mail(mail_content):
    """
    Parse a single mail content string into individual email messages.
    
    Args:
        mail_content (str): Raw mail content from a .txt file.
    
    Returns:
        list: List of dictionaries, each containing parsed email data.
    """
    messages = []
    
    # Split by "Od: " to separate individual messages
    # Pattern: "Od: " at the start of a line (possibly after whitespace/newline)
    message_parts = re.split(r'(?:\n\s*)?Od:\s+', mail_content)
    
    # Skip the first part if it's empty or doesn't contain a message
    for part in message_parts:
        if not part.strip():
            continue
            
        # Add "Od: " back to the beginning for easier parsing
        message_text = "Od: " + part.strip()
        
        # Extract sender (nadawca)
        sender_match = re.search(r'^Od:\s+(.+?)(?:\n|$)', message_text, re.MULTILINE)
        nadawca = sender_match.group(1).strip() if sender_match else None
        
        # Extract date (data)
        date_match = re.search(r'Wysłano:\s+(.+?)(?:\n|$)', message_text, re.MULTILINE)
        data = date_match.group(1).strip() if date_match else None
        
        # Extract recipient (odbiorca)
        recipient_match = re.search(r'Do:\s+(.+?)(?:\n|$)', message_text, re.MULTILINE)
        odbiorca = recipient_match.group(1).strip() if recipient_match else None
        
        # Extract subject (temat)
        subject_match = re.search(r'Temat:\s+(.+?)(?:\n|$)', message_text, re.MULTILINE)
        temat = subject_match.group(1).strip() if subject_match else None
        
        # Extract main content (główna treść wiadomości)
        # Find the line after "Temat:" and extract everything until the next "Od:" or end
        content_match = re.search(r'Temat:\s+.+?\n\n(.+?)(?=\n\nOd:\s+|$)', message_text, re.DOTALL)
        if not content_match:
            # Try to find content after the last header field
            content_match = re.search(r'Temat:\s+.+?\n\n(.+)', message_text, re.DOTALL)
        
        if content_match:
            tresc = content_match.group(1).strip()
            # Remove signature (everything after "--")
            tresc = re.split(r'\n--\n', tresc)[0].strip()
        else:
            tresc = None
        
        # Only add message if we have at least sender or recipient
        if nadawca or odbiorca:
            messages.append({
                'nadawca': nadawca,
                'odbiorca': odbiorca,
                'temat': temat,
                'data': data,
                'główna treść wiadomości': tresc
            })
    
    return messages


def parse_mails_to_dataframe(data_dir=None):
    """
    Parse all mail data from .txt files into a pandas DataFrame.
    
    Args:
        data_dir (str, optional): Path to the directory containing mail .txt files.
                                 If None, uses default from read_mails_data().
    
    Returns:
        pd.DataFrame: DataFrame with columns: 'nadawca', 'odbiorca', 'temat', 'data', 
                     'główna treść wiadomości'
    """
    # Read all mail data
    mails = read_mails_data(data_dir) if data_dir else read_mails_data()
    
    all_messages = []
    
    # Parse each mail file
    for mail_content in mails:
        messages = parse_single_mail(mail_content)
        all_messages.extend(messages)
    
    # Create DataFrame
    df = pd.DataFrame(all_messages)
    
    return df


if __name__ == "__main__":
    # Test the parsing
    df = parse_mails_to_dataframe()
    
    print(f"Parsed {len(df)} email messages")
    print(f"\nDataFrame shape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    print(f"\nData types:")
    print(df.dtypes)
    print(f"\nSample message:")
    if len(df) > 0:
        print(f"\nNadawca: {df.iloc[0]['nadawca']}")
        print(f"Odbiorca: {df.iloc[0]['odbiorca']}")
        print(f"Temat: {df.iloc[0]['temat']}")
        print(f"Data: {df.iloc[0]['data']}")
        print(f"Treść (first 200 chars): {df.iloc[0]['główna treść wiadomości'][:200] if pd.notna(df.iloc[0]['główna treść wiadomości']) else 'N/A'}...")

