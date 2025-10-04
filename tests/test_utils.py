import pytest
from finance_crawler.utils import (
    url_filetype, canonical_url, short_title_from_url, 
    generate_document_id, exponential_backoff, is_allowed_filetype,
    extract_domain_from_url, normalize_url
)


def test_url_filetype():
    """Test URL filetype extraction."""
    assert url_filetype("https://example.com/document.pdf") == "pdf"
    assert url_filetype("https://example.com/data.csv") == "csv"
    assert url_filetype("https://example.com/spreadsheet.xlsx") == "xlsx"
    assert url_filetype("https://example.com/old.xls") == "xls"
    assert url_filetype("https://example.com/page.html") == "html"
    assert url_filetype("https://example.com/page.htm") == "html"
    assert url_filetype("https://example.com/noextension") is None
    assert url_filetype("https://example.com/unknown.xyz") is None


def test_canonical_url():
    """Test URL canonicalization."""
    base = "https://example.com/path/"
    
    assert canonical_url("/relative", base) == "https://example.com/relative"
    assert canonical_url("relative", base) == "https://example.com/path/relative"
    assert canonical_url("https://other.com/absolute", base) == "https://other.com/absolute"
    assert canonical_url("../parent", base) == "https://example.com/parent"


def test_short_title_from_url():
    """Test short title generation from URL."""
    assert short_title_from_url("https://example.com/document.pdf") == "document"
    assert short_title_from_url("https://example.com/path/to/long-document-name.pdf") == "long-document-name"
    assert short_title_from_url("https://example.com/") == "document"
    assert short_title_from_url("https://example.com/special-chars!@#.pdf") == "special-chars"
    
    # Test length limit
    long_name = "a" * 100
    result = short_title_from_url(f"https://example.com/{long_name}.pdf")
    assert len(result) <= 50


def test_generate_document_id():
    """Test document ID generation."""
    url1 = "https://example.com/doc1.pdf"
    title1 = "Document 1"
    
    url2 = "https://example.com/doc2.pdf"
    title2 = "Document 2"
    
    id1 = generate_document_id(url1, title1)
    id2 = generate_document_id(url2, title2)
    
    # IDs should be different for different inputs
    assert id1 != id2
    
    # IDs should be consistent for same inputs
    id1_again = generate_document_id(url1, title1)
    assert id1 == id1_again
    
    # IDs should be hex strings
    assert all(c in "0123456789abcdef" for c in id1)
    assert len(id1) == 40  # SHA1 hex length


def test_exponential_backoff():
    """Test exponential backoff calculation."""
    # Test base delay
    assert exponential_backoff(0) == 1.0
    
    # Test exponential growth
    assert exponential_backoff(1) == 2.0
    assert exponential_backoff(2) == 4.0
    assert exponential_backoff(3) == 8.0
    
    # Test max delay
    large_attempt = exponential_backoff(10)
    assert large_attempt <= 60.0  # max_delay


def test_is_allowed_filetype():
    """Test filetype filtering."""
    allowed_types = {"pdf", "csv", "xlsx"}
    
    assert is_allowed_filetype("https://example.com/doc.pdf", allowed_types) is True
    assert is_allowed_filetype("https://example.com/data.csv", allowed_types) is True
    assert is_allowed_filetype("https://example.com/sheet.xlsx", allowed_types) is True
    assert is_allowed_filetype("https://example.com/page.html", allowed_types) is False
    assert is_allowed_filetype("https://example.com/noext", allowed_types) is False


def test_extract_domain_from_url():
    """Test domain extraction from URL."""
    assert extract_domain_from_url("https://example.com/path") == "example.com"
    assert extract_domain_from_url("http://subdomain.example.org/path") == "subdomain.example.org"
    assert extract_domain_from_url("https://EXAMPLE.COM/path") == "example.com"  # lowercase


def test_normalize_url():
    """Test URL normalization."""
    # Test fragment removal
    assert normalize_url("https://example.com/path#fragment") == "https://example.com/path"
    
    # Test query parameter handling (basic)
    url_with_query = "https://example.com/path?param=value"
    normalized = normalize_url(url_with_query)
    assert "param=value" in normalized
    assert "#" not in normalized
