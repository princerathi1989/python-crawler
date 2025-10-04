import re
from typing import Optional, Tuple
from pypdf import PdfReader
from io import BytesIO


def extract_pdf_metadata(content: bytes) -> Tuple[Optional[str], Optional[str]]:
    """Extract title and date from PDF metadata and first page text."""
    try:
        pdf_reader = PdfReader(BytesIO(content))
        
        # Try to get title from metadata
        title = None
        if pdf_reader.metadata and pdf_reader.metadata.title:
            title = pdf_reader.metadata.title.strip()
        
        # If no title in metadata, try to extract from first page
        if not title and len(pdf_reader.pages) > 0:
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            
            # Look for title-like patterns (first few lines, capitalized)
            lines = text.split('\n')[:10]  # First 10 lines
            for line in lines:
                line = line.strip()
                if len(line) > 10 and len(line) < 100:  # Reasonable title length
                    # Check if it looks like a title (has capitals, not all caps)
                    if any(c.isupper() for c in line) and not line.isupper():
                        title = line
                        break
        
        # Extract date from first page text
        date_str = None
        if len(pdf_reader.pages) > 0:
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            date_str = extract_date_from_text(text)
        
        return title, date_str
        
    except Exception:
        return None, None


def extract_date_from_text(text: str) -> Optional[str]:
    """Extract date from text using regex patterns."""
    if not text:
        return None
    
    # Common date patterns
    date_patterns = [
        r'\b(\d{1,2})[-\/](\d{1,2})[-\/](\d{4})\b',  # DD/MM/YYYY or DD-MM-YYYY
        r'\b(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})\b',  # YYYY/MM/DD or YYYY-MM-DD
        r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b',  # DD Mon YYYY
        r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})\b',  # Mon DD, YYYY
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None


def extract_pdf_text_preview(content: bytes, max_chars: int = 500) -> Optional[str]:
    """Extract a preview of PDF text content."""
    try:
        pdf_reader = PdfReader(BytesIO(content))
        text_parts = []
        
        for page_num, page in enumerate(pdf_reader.pages[:3]):  # First 3 pages
            if page_num >= 3:
                break
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        full_text = '\n'.join(text_parts)
        if len(full_text) > max_chars:
            return full_text[:max_chars] + "..."
        return full_text
        
    except Exception:
        return None
