import pytest
from finance_crawler.sources.builtin import get_builtin_sources, get_source_names
from finance_crawler.sources.base import SourceConfig


def test_get_builtin_sources():
    """Test builtin sources configuration."""
    sources = get_builtin_sources()
    
    # Check that we have expected sources
    expected_sources = ["sebi", "nse", "amfi", "rbi_sgb", "income_tax"]
    assert all(source in sources for source in expected_sources)
    
    # Check that all sources are SourceConfig instances
    for source_name, config in sources.items():
        assert isinstance(config, SourceConfig)
        assert config.name
        assert config.domain_tag
        assert config.source_org
        assert config.start_urls
        assert config.allow_patterns
        assert config.max_depth > 0
        assert config.max_pages > 0


def test_sebi_config():
    """Test SEBI source configuration."""
    sources = get_builtin_sources()
    sebi = sources["sebi"]
    
    assert sebi.name == "SEBI"
    assert sebi.domain_tag == "stock_equity"
    assert sebi.source_org == "SEBI"
    assert len(sebi.start_urls) == 3
    assert "sebi.gov.in" in sebi.start_urls[0]
    assert sebi.max_pages == 250


def test_nse_config():
    """Test NSE source configuration."""
    sources = get_builtin_sources()
    nse = sources["nse"]
    
    assert nse.name == "NSE"
    assert nse.domain_tag == "stock_equity"
    assert nse.source_org == "NSE"
    assert len(nse.start_urls) == 2
    assert "nseindia.com" in nse.start_urls[0]


def test_amfi_config():
    """Test AMFI source configuration."""
    sources = get_builtin_sources()
    amfi = sources["amfi"]
    
    assert amfi.name == "AMFI"
    assert amfi.domain_tag == "mutual_fund_etf"
    assert amfi.source_org == "AMFI"
    assert len(amfi.start_urls) == 2
    assert "amfiindia.com" in amfi.start_urls[0]


def test_rbi_sgb_config():
    """Test RBI SGB source configuration."""
    sources = get_builtin_sources()
    rbi_sgb = sources["rbi_sgb"]
    
    assert rbi_sgb.name == "RBI_SGB"
    assert rbi_sgb.domain_tag == "gold"
    assert rbi_sgb.source_org == "RBI"
    assert len(rbi_sgb.start_urls) == 2
    assert "rbi.org.in" in rbi_sgb.start_urls[0]


def test_income_tax_config():
    """Test Income Tax source configuration."""
    sources = get_builtin_sources()
    income_tax = sources["income_tax"]
    
    assert income_tax.name == "INCOME_TAX"
    assert income_tax.domain_tag == "taxation"
    assert income_tax.source_org == "CBDT"
    assert len(income_tax.start_urls) == 3
    assert "incometax" in income_tax.start_urls[0]


def test_source_config_url_filtering():
    """Test URL filtering in SourceConfig."""
    config = SourceConfig(
        name="Test",
        domain_tag="stock_equity",
        source_org="Test",
        start_urls=["https://example.com"],
        allow_patterns=[r"example\.com/.+\.pdf$"],
        deny_patterns=[r"login|admin"]
    )
    
    # Test allowed URLs
    assert config.should_process_url("https://example.com/document.pdf") is True
    assert config.should_process_url("https://example.com/data.pdf") is True
    
    # Test denied URLs
    assert config.should_process_url("https://example.com/login") is False
    assert config.should_process_url("https://example.com/admin") is False
    
    # Test non-matching URLs
    assert config.should_process_url("https://other.com/document.pdf") is False
    assert config.should_process_url("https://example.com/page.html") is False


def test_get_source_names():
    """Test source names list."""
    names = get_source_names()
    
    expected_names = ["sebi", "nse", "amfi", "rbi_sgb", "income_tax"]
    assert names == expected_names
    assert len(names) == 5


def test_source_config_regex_compilation():
    """Test that regex patterns are properly compiled."""
    config = SourceConfig(
        name="Test",
        domain_tag="stock_equity",
        source_org="Test",
        start_urls=["https://example.com"],
        allow_patterns=[r"example\.com/.+\.pdf$"],
        deny_patterns=[r"login"]
    )
    
    # Check that regex objects are created
    assert len(config._allow_regex) == 1
    assert len(config._deny_regex) == 1
    
    # Test regex matching
    assert config._allow_regex[0].search("https://example.com/doc.pdf") is not None
    assert config._deny_regex[0].search("https://example.com/login") is not None
