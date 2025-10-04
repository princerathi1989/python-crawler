import pytest
from datetime import date
from finance_crawler.schema import DocumentRecord, QualityFlags, Domain


def test_quality_flags_creation():
    """Test QualityFlags model creation."""
    flags = QualityFlags()
    assert flags.is_official is True
    assert flags.has_methodology is False
    assert flags.within_24_months is None
    assert flags.has_downloadable_file is True


def test_quality_flags_custom():
    """Test QualityFlags with custom values."""
    flags = QualityFlags(
        is_official=False,
        has_methodology=True,
        within_24_months=True
    )
    assert flags.is_official is False
    assert flags.has_methodology is True
    assert flags.within_24_months is True


def test_document_record_minimal():
    """Test DocumentRecord creation with minimal fields."""
    flags = QualityFlags()
    
    record = DocumentRecord(
        id="test123",
        title="Test Document",
        domain="stock_equity",
        source_org="SEBI",
        source_url="https://example.com/test.pdf",
        file_type="pdf",
        quality_flags=flags
    )
    
    assert record.id == "test123"
    assert record.title == "Test Document"
    assert record.domain == "stock_equity"
    assert record.source_org == "SEBI"
    assert record.source_url == "https://example.com/test.pdf"
    assert record.file_type == "pdf"
    assert record.jurisdiction == "IN"
    assert record.source_tier == 1
    assert record.copyright == "unknown"
    assert record.language == "en"
    assert record.intended_audience == "education"


def test_document_record_full():
    """Test DocumentRecord creation with all fields."""
    flags = QualityFlags(
        is_official=True,
        has_methodology=True,
        within_24_months=True
    )
    
    record = DocumentRecord(
        id="test456",
        title="Full Test Document",
        summary="This is a test document",
        domain="mutual_fund_etf",
        topic_tags=["mutual_funds", "education"],
        jurisdiction="IN",
        source_tier=1,
        source_org="AMFI",
        source_url="https://example.com/full-test.pdf",
        file_type="pdf",
        published_date=date(2024, 1, 15),
        last_checked=date(2024, 1, 20),
        version_or_circular_no="CIR/2024/001",
        copyright="public",
        language="en",
        intended_audience="investor",
        quality_flags=flags,
        storage_path="/data/mutual_fund_etf/amfi/2024/pdf__full_test__2024-01-15.pdf"
    )
    
    assert record.summary == "This is a test document"
    assert record.topic_tags == ["mutual_funds", "education"]
    assert record.published_date == date(2024, 1, 15)
    assert record.version_or_circular_no == "CIR/2024/001"
    assert record.copyright == "public"
    assert record.intended_audience == "investor"
    assert record.storage_path is not None


def test_domain_validation():
    """Test domain field validation."""
    flags = QualityFlags()
    
    valid_domains = [
        "stock_equity", "mutual_fund_etf", "real_estate", "fd_rd",
        "retirement", "gold", "forex", "loans_credit", "insurance", "taxation"
    ]
    
    for domain in valid_domains:
        record = DocumentRecord(
            id="test",
            title="Test",
            domain=domain,
            source_org="Test",
            source_url="https://example.com/test.pdf",
            file_type="pdf",
            quality_flags=flags
        )
        assert record.domain == domain


def test_model_serialization():
    """Test model serialization to dict."""
    flags = QualityFlags()
    
    record = DocumentRecord(
        id="test789",
        title="Serialization Test",
        domain="taxation",
        source_org="CBDT",
        source_url="https://example.com/serialization-test.pdf",
        file_type="pdf",
        published_date=date(2024, 2, 1),
        quality_flags=flags
    )
    
    data = record.model_dump()
    assert isinstance(data, dict)
    assert data["id"] == "test789"
    assert data["title"] == "Serialization Test"
    assert data["domain"] == "taxation"
    assert data["published_date"] == date(2024, 2, 1)
