from typing import Dict, List
from .base import SourceConfig


def get_builtin_sources() -> Dict[str, SourceConfig]:
    """Get built-in source configurations."""
    
    sources = {
        "sebi": SourceConfig(
            name="SEBI",
            domain_tag="stock_equity",
            source_org="SEBI",
            start_urls=[
                "https://www.sebi.gov.in/investors.html",
                "https://www.sebi.gov.in/investors/educational-booklets.html",
                "https://www.sebi.gov.in/legal/circulars/"
            ],
            allow_patterns=[
                r"sebi\.gov\.in/.+\.(pdf|csv|xlsx)$"
            ],
            deny_patterns=[
                r"login|careers"
            ],
            max_depth=2,
            max_pages=250
        ),
        
        "nse": SourceConfig(
            name="NSE",
            domain_tag="stock_equity", 
            source_org="NSE",
            start_urls=[
                "https://www.nseindia.com/invest",
                "https://www.nseindia.com/education/ncfm"
            ],
            allow_patterns=[
                r"nseindia\.com/.+\.(pdf|csv|xlsx)$"
            ],
            deny_patterns=[
                r"live market"
            ],
            max_depth=2,
            max_pages=200
        ),
        
        "amfi": SourceConfig(
            name="AMFI",
            domain_tag="mutual_fund_etf",
            source_org="AMFI", 
            start_urls=[
                "https://www.amfiindia.com/investor-corner",
                "https://www.amfiindia.com/investor-awareness"
            ],
            allow_patterns=[
                r"amfiindia\.com/.+\.(pdf|csv|xlsx)$"
            ],
            deny_patterns=[],
            max_depth=2,
            max_pages=200
        ),
        
        "rbi_sgb": SourceConfig(
            name="RBI_SGB",
            domain_tag="gold",
            source_org="RBI",
            start_urls=[
                "https://www.rbi.org.in/Scripts/FAQsView.aspx?Id=138",
                "https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?Id=5223"
            ],
            allow_patterns=[
                r"rbi\.org\.in/.+\.(pdf|csv|xlsx)$"
            ],
            deny_patterns=[],
            max_depth=2,
            max_pages=200
        ),
        
        "income_tax": SourceConfig(
            name="INCOME_TAX",
            domain_tag="taxation",
            source_org="CBDT",
            start_urls=[
                "https://incometaxindia.gov.in/Pages/communications/circulars.aspx",
                "https://incometaxindia.gov.in/Pages/communications/notifications.aspx",
                "https://www.incometax.gov.in/iec/foportal/help/income-tax-slabs"
            ],
            allow_patterns=[
                r"(incometax|incometaxindia)\.(gov)\.in/.+\.(pdf|csv|xlsx)$"
            ],
            deny_patterns=[],
            max_depth=2,
            max_pages=200
        )
    }
    
    return sources


def get_source_names() -> List[str]:
    """Get list of available source names."""
    return list(get_builtin_sources().keys())
