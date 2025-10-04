import re
from datetime import date, datetime
from dateutil import parser as date_parser
from typing import Optional, List
from urllib.parse import urlparse


def extract_date_from_url(url: str) -> Optional[date]:
    """Extract date from URL path or query parameters."""
    parsed = urlparse(url)
    
    # Check path segments for date patterns
    path_segments = parsed.path.split('/')
    for segment in path_segments:
        date_obj = parse_date_string(segment)
        if date_obj:
            return date_obj
    
    # Check query parameters
    if parsed.query:
        query_parts = parsed.query.split('&')
        for part in query_parts:
            if '=' in part:
                key, value = part.split('=', 1)
                if 'date' in key.lower() or 'year' in key.lower():
                    date_obj = parse_date_string(value)
                    if date_obj:
                        return date_obj
    
    return None


def parse_date_string(date_str: str) -> Optional[date]:
    """Parse various date string formats."""
    if not date_str:
        return None
    
    # Clean the string
    date_str = re.sub(r'[^\w\s\-/]', '', date_str.strip())
    
    # Common patterns
    patterns = [
        r'\b(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})\b',  # YYYY/MM/DD
        r'\b(\d{1,2})[-\/](\d{1,2})[-\/](\d{4})\b',  # DD/MM/YYYY
        r'\b(\d{4})\b',  # Just year
        r'\b(\d{1,2})[-\/](\d{4})\b',  # MM/YYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_str)
        if match:
            try:
                if len(match.groups()) == 3:
                    year, month, day = match.groups()
                    return date(int(year), int(month), int(day))
                elif len(match.groups()) == 2:
                    month, year = match.groups()
                    return date(int(year), int(month), 1)
                elif len(match.groups()) == 1:
                    year = int(match.group(1))
                    if 1900 <= year <= 2030:  # Reasonable year range
                        return date(year, 1, 1)
            except (ValueError, TypeError):
                continue
    
    # Try dateutil parser as fallback
    try:
        parsed_date = date_parser.parse(date_str, fuzzy=True)
        if parsed_date:
            return parsed_date.date()
    except (ValueError, TypeError):
        pass
    
    return None


def extract_circular_number(text: str) -> Optional[str]:
    """Extract circular/notification number from text."""
    if not text:
        return None
    
    # Common patterns for circular numbers
    patterns = [
        r'Circular\s+No\.?\s*([A-Z0-9/\-]+)',
        r'Notification\s+No\.?\s*([A-Z0-9/\-]+)',
        r'Circular\s+([A-Z0-9/\-]+)',
        r'No\.?\s*([A-Z0-9/\-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def extract_topic_tags(text: str, title: str = "") -> List[str]:
    """Extract topic tags from text and title."""
    tags = []
    
    # Combine text and title for analysis
    combined_text = f"{title} {text}".lower()
    
    # Financial topic keywords
    topic_keywords = {
        'mutual_funds': ['mutual fund', 'mf', 'nav', 'amc', 'sip'],
        'equity': ['equity', 'stock', 'share', 'nse', 'bse', 'sensex', 'nifty'],
        'taxation': ['tax', 'income tax', 'gst', 'tds', 'itr', 'assessment'],
        'gold': ['gold', 'sgb', 'sovereign gold bond', 'precious metal'],
        'insurance': ['insurance', 'policy', 'premium', 'claim'],
        'banking': ['bank', 'rbi', 'loan', 'credit', 'deposit'],
        'regulatory': ['sebi', 'rbi', 'circular', 'regulation', 'compliance'],
        'education': ['education', 'awareness', 'investor', 'guide', 'handbook'],
    }
    
    for topic, keywords in topic_keywords.items():
        if any(keyword in combined_text for keyword in keywords):
            tags.append(topic)
    
    return tags[:5]  # Limit to 5 tags
