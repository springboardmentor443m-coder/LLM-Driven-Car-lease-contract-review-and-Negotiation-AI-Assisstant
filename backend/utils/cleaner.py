import re

def clean_text(text: str) -> str:
    """
    Removes excessive whitespace and non-printable characters 
    to make the text cheaper for the LLM to process.
    """
    # Replace multiple newlines with single newline
    text = re.sub(r'\n+', '\n', text)
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove non-ascii characters if necessary (optional)
    # text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    return text.strip()