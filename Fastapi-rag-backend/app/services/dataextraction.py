import re
from datetime import datetime

def extract_booking_details(text: str):
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    date_pattern = r'\d{4}-\d{2}-\d{2}' # YYYY-MM-DD
    time_pattern = r'\d{2}:\d{2}'       # HH:MM
    name_pattern = r"(?:I am|name is|Name:)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
    email = re.search(email_pattern, text)
    date = re.search(date_pattern, text)
    time = re.search(time_pattern, text)
    name = re.search(name_pattern, text, re.IGNORECASE)
    
    return {
        "name": name.group(1) if name else None,
        "email": email.group(0) if email else None,
        "date": date.group(0) if date else None,
        "time": time.group(0) if time else None
    }