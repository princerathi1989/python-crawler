from typing import Literal, List, Optional
from datetime import date
from pydantic import BaseModel


Domain = Literal[
    "stock_equity",
    "mutual_fund_etf", 
    "real_estate",
    "fd_rd",
    "retirement",
    "gold",
    "forex",
    "loans_credit",
    "insurance",
    "taxation"
]


class QualityFlags(BaseModel):
    is_official: bool = True
    has_methodology: bool = False
    within_24_months: Optional[bool] = None
    has_downloadable_file: bool = True


class DocumentRecord(BaseModel):
    id: str
    title: str
    summary: Optional[str] = None
    domain: Domain
    topic_tags: List[str] = []
    jurisdiction: str = "IN"
    source_tier: int = 1
    source_org: str
    source_url: str
    file_type: str  # pdf|html|csv|xlsx|xls
    published_date: Optional[date] = None
    last_checked: Optional[date] = None
    version_or_circular_no: Optional[str] = None
    copyright: Literal["public", "restricted", "unknown"] = "unknown"
    language: str = "en"
    intended_audience: Literal["investor", "policy", "education", "research", "general"] = "education"
    quality_flags: QualityFlags
    storage_path: Optional[str] = None
