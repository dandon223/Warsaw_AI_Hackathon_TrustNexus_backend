import re
import pandas as pd
from read_mails import read_mails_data


def parse_sender(sender_string):
    """
    Parse sender string into name and email.
    
    Args:
        sender_string (str): Sender string in format "Name <email@domain.com>" or "email@domain.com"
    
    Returns:
        tuple: (name, email) or (None, email) if no name found
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
        nadawca_raw = sender_match.group(1).strip() if sender_match else None
        
        # Parse sender into name and email
        nadawca_nazwa, nadawca_mail = parse_sender(nadawca_raw) if nadawca_raw else (None, None)
        
        # Extract date (data)
        date_match = re.search(r'Wysłano:\s+(.+?)(?:\n|$)', message_text, re.MULTILINE)
        data = date_match.group(1).strip() if date_match else None
        
        # Extract recipient (odbiorca)
        recipient_match = re.search(r'Do:\s+(.+?)(?:\n|$)', message_text, re.MULTILINE)
        odbiorca_raw = recipient_match.group(1).strip() if recipient_match else None
        
        # Handle multiple recipients (comma-separated) - take the first one
        if odbiorca_raw:
            # Split by comma and take the first recipient
            first_recipient = odbiorca_raw.split(',')[0].strip()
            odbiorca_nazwa, odbiorca_mail = parse_sender(first_recipient)
        else:
            odbiorca_nazwa, odbiorca_mail = None, None
        
        # Extract subject (temat)
        subject_match = re.search(r'Temat:\s+(.+?)(?:\n|$)', message_text, re.MULTILINE)
        temat = subject_match.group(1).strip() if subject_match else None
        
        # Extract main content (message_content)
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
        if nadawca_nazwa or nadawca_mail or odbiorca_nazwa or odbiorca_mail:
            messages.append({
                'sender_name': nadawca_nazwa,
                'sender_email': nadawca_mail,
                'recipient_name': odbiorca_nazwa,
                'recipient_email': odbiorca_mail,
                'subject': temat,
                'date': data,
                'message_content': tresc
            })
    
    return messages


def parse_mails_to_dataframe(data_dir=None):
    """
    Parse all mail data from .txt files into a pandas DataFrame.
    
    Args:
        data_dir (str, optional): Path to the directory containing mail .txt files.
                                 If None, uses default from read_mails_data().
    
    Returns:
        pd.DataFrame: DataFrame with columns: 'sender_name', 'sender_email', 'recipient_name', 'recipient_email', 
                     'subject', 'date', 'message_content'
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
        print(f"\nSender name: {df.iloc[0]['sender_name']}")
        print(f"Sender email: {df.iloc[0]['sender_email']}")
        print(f"Recipient name: {df.iloc[0]['recipient_name']}")
        print(f"Recipient email: {df.iloc[0]['recipient_email']}")
        print(f"Subject: {df.iloc[0]['subject']}")
        print(f"Date: {df.iloc[0]['date']}")
        print(f"Message content (first 200 chars): {df.iloc[0]['message_content'][:200] if pd.notna(df.iloc[0]['message_content']) else 'N/A'}...")

