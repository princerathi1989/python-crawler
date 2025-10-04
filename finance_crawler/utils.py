import re
import hashlib
import time
from urllib.parse import urljoin, urlparse
from typing import Optional, Set
from datetime import datetime


def url_filetype(url: str) -> Optional[str]:
    """Extract file type from URL."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    if path.endswith('.pdf'):
        return 'pdf'
    elif path.endswith('.csv'):
        return 'csv'
    elif path.endswith('.xlsx'):
        return 'xlsx'
    elif path.endswith('.xls'):
        return 'xls'
    elif path.endswith(('.html', '.htm')):
        return 'html'
    return None


def canonical_url(url: str, base_url: str) -> str:
    """Convert relative URL to absolute URL."""
    return urljoin(base_url, url)


def short_title_from_url(url: str) -> str:
    """Generate a short title from URL path."""
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    
    # Extract filename without extension
    filename = path.split('/')[-1] if path else 'document'
    filename = re.sub(r'\.[^.]+$', '', filename)
    
    # Clean up the filename
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename[:50]  # Limit length
    
    return filename or 'document'


def generate_document_id(url: str, title: str) -> str:
    """Generate stable document ID from URL and title."""
    content = f"{url}|{title}"
    return hashlib.sha1(content.encode()).hexdigest()


def exponential_backoff(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay."""
    delay = min(base_delay * (2 ** attempt), max_delay)
    return delay


def is_allowed_filetype(url: str, allowed_types: Set[str]) -> bool:
    """Check if URL filetype is in allowed set."""
    filetype = url_filetype(url)
    return filetype in allowed_types if filetype else False


def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc.lower()


def normalize_url(url: str) -> str:
    """Normalize URL by removing fragments and sorting query params."""
    parsed = urlparse(url)
    # Remove fragment
    normalized = parsed._replace(fragment='').geturl()
    return normalized
