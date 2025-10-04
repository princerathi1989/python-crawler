import re
import asyncio
from typing import List, Set, Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import urlparse
from ..schema import DocumentRecord, Domain, QualityFlags
from ..fetcher import AsyncFetcher
from ..robots import RobotsChecker
from ..parser_html import extract_html_links, extract_html_title
from ..parser_pdf import extract_pdf_metadata
from ..extractor import extract_date_from_url, extract_circular_number, extract_topic_tags
from ..utils import url_filetype, canonical_url, generate_document_id, is_allowed_filetype


@dataclass
class SourceConfig:
    """Configuration for a data source."""
    name: str
    domain_tag: Domain
    source_org: str
    start_urls: List[str]
    allow_patterns: List[str]
    deny_patterns: List[str]
    max_depth: int = 2
    max_pages: int = 200
    filetypes: Set[str] = None
    
    def __post_init__(self):
        if self.filetypes is None:
            self.filetypes = {'pdf', 'csv', 'xlsx', 'xls', 'html'}
        
        # Compile regex patterns
        self._allow_regex = [re.compile(pattern) for pattern in self.allow_patterns]
        self._deny_regex = [re.compile(pattern) for pattern in self.deny_patterns]
    
    def is_url_allowed(self, url: str) -> bool:
        """Check if URL matches allow patterns."""
        if not self._allow_regex:
            return True
        
        return any(regex.search(url) for regex in self._allow_regex)
    
    def is_url_denied(self, url: str) -> bool:
        """Check if URL matches deny patterns."""
        if not self._deny_regex:
            return False
        
        return any(regex.search(url) for regex in self._deny_regex)
    
    def should_process_url(self, url: str) -> bool:
        """Check if URL should be processed."""
        return self.is_url_allowed(url) and not self.is_url_denied(url)


class GenericSpider:
    """Generic spider for crawling sources."""
    
    def __init__(self, config: SourceConfig, fetcher: AsyncFetcher, robots_checker: RobotsChecker):
        self.config = config
        self.fetcher = fetcher
        self.robots_checker = robots_checker
        self.visited_urls: Set[str] = set()
        self.processed_count = 0
    
    async def crawl(self, max_pages: Optional[int] = None) -> List[DocumentRecord]:
        """Crawl the source and return document records."""
        max_pages = max_pages or self.config.max_pages
        documents = []
        
        # BFS queue: (url, depth)
        queue = [(url, 0) for url in self.config.start_urls]
        
        while queue and self.processed_count < max_pages:
            url, depth = queue.pop(0)
            
            if url in self.visited_urls or depth > self.config.max_depth:
                continue
            
            # Check robots.txt
            if not self.robots_checker.is_allowed(url):
                continue
            
            # Check URL patterns
            if not self.config.should_process_url(url):
                continue
            
            self.visited_urls.add(url)
            
            try:
                response = await self.fetcher.fetch(url)
                if not response or response['status_code'] != 200:
                    continue
                
                content = response['content']
                if not content:
                    continue
                
                filetype = url_filetype(url)
                
                if filetype == 'html':
                    # Extract links for further crawling
                    links = extract_html_links(content, url)
                    for link in links:
                        canonical_link = canonical_url(link, url)
                        if canonical_link not in self.visited_urls:
                            queue.append((canonical_link, depth + 1))
                
                elif filetype in self.config.filetypes:
                    # Process document
                    document = await self._create_document_record(url, content, filetype)
                    if document:
                        documents.append(document)
                        self.processed_count += 1
                
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
        
        return documents
    
    async def _create_document_record(self, url: str, content: bytes, filetype: str) -> Optional[DocumentRecord]:
        """Create DocumentRecord from URL and content."""
        try:
            # Extract title
            title = None
            published_date = None
            circular_no = None
            
            if filetype == 'pdf':
                title, date_str = extract_pdf_metadata(content)
                if date_str:
                    published_date = extract_date_from_url(date_str)
                if title:
                    circular_no = extract_circular_number(title)
            
            if not title:
                title = url.split('/')[-1] or 'Document'
            
            # Extract date from URL if not found
            if not published_date:
                published_date = extract_date_from_url(url)
            
            # Generate document ID
            doc_id = generate_document_id(url, title)
            
            # Extract topic tags
            topic_tags = extract_topic_tags(title)
            
            # Create quality flags
            quality_flags = QualityFlags(
                is_official=True,
                has_methodology=False,
                within_24_months=None,
                has_downloadable_file=True
            )
            
            # Determine copyright
            copyright_status = "public" if self.config.source_org in ["SEBI", "NSE", "AMFI", "RBI", "CBDT"] else "unknown"
            
            record = DocumentRecord(
                id=doc_id,
                title=title,
                domain=self.config.domain_tag,
                source_org=self.config.source_org,
                source_url=url,
                file_type=filetype,
                published_date=published_date,
                topic_tags=topic_tags,
                copyright=copyright_status,
                quality_flags=quality_flags,
                version_or_circular_no=circular_no
            )
            
            return record
            
        except Exception as e:
            print(f"Error creating document record for {url}: {e}")
            return None
