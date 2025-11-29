import os
import glob

# Get the base directory of the project (three levels up from this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def read_mails_data(data_dir=DATA_DIR):
    """
    Read mail data from .txt files in the specified directory.
    
    Recursively searches for all .txt files in the directory and subdirectories.
    
    Args:
        data_dir (str): Path to the directory containing mail .txt files.
    
    Returns:
        list: List of mail contents (strings) from all .txt files found.
    """
    mails = []
    
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
                    mails.append(content)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue
    
    if not mails:
        print(f"No .txt files found in {data_dir}")
    
    return mails

mails = read_mails_data()
if mails:
    print(f"Loaded {len(mails)} mail(s)")
    if len(mails) > 0:
        print(f"\nFirst mail preview:\n{mails[0][:200]}...")
else:
    print("No data loaded. Please check the directory path and file structure.")