from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Optional, Tuple


def extract_html_links(content: bytes, base_url: str) -> List[str]:
    """Extract links from HTML content."""
    try:
        soup = BeautifulSoup(content, 'lxml')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        
        return links
    except Exception:
        return []


def extract_html_title(content: bytes) -> Optional[str]:
    """Extract page title from HTML content."""
    try:
        soup = BeautifulSoup(content, 'lxml')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return None
    except Exception:
        return None


def extract_html_meta_description(content: bytes) -> Optional[str]:
    """Extract meta description from HTML content."""
    try:
        soup = BeautifulSoup(content, 'lxml')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        return None
    except Exception:
        return None
