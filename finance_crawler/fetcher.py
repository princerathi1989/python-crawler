import asyncio
import sqlite3
import httpx
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class CacheEntry:
    """Represents a cache entry for HTTP responses."""
    
    def __init__(self, url: str, etag: Optional[str] = None, 
                 last_modified: Optional[str] = None, 
                 status: int = 200, stored_at: Optional[datetime] = None):
        self.url = url
        self.etag = etag
        self.last_modified = last_modified
        self.status = status
        self.stored_at = stored_at or datetime.now()


class AsyncFetcher:
    """Async HTTP client with ETag/Last-Modified caching."""
    
    def __init__(self, cache_db_path: str = "cache.db", 
                 user_agent: str = "finance-crawler-mvp/0.1",
                 timeout: float = 30.0):
        self.cache_db_path = cache_db_path
        self.user_agent = user_agent
        self.timeout = timeout
        self._init_cache_db()
    
    def _init_cache_db(self):
        """Initialize SQLite cache database."""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                url TEXT PRIMARY KEY,
                etag TEXT,
                last_modified TEXT,
                status INTEGER,
                stored_at TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def _get_cache_entry(self, url: str) -> Optional[CacheEntry]:
        """Get cache entry for URL."""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT etag, last_modified, status, stored_at FROM cache WHERE url = ?",
            (url,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            etag, last_modified, status, stored_at = row
            stored_at_dt = datetime.fromisoformat(stored_at) if stored_at else None
            return CacheEntry(url, etag, last_modified, status, stored_at_dt)
        return None
    
    def _set_cache_entry(self, entry: CacheEntry):
        """Store cache entry."""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO cache (url, etag, last_modified, status, stored_at)
            VALUES (?, ?, ?, ?, ?)
        """, (entry.url, entry.etag, entry.last_modified, entry.status, 
              entry.stored_at.isoformat() if entry.stored_at else None))
        conn.commit()
        conn.close()
    
    async def fetch(self, url: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Fetch URL with caching and retry logic."""
        cache_entry = self._get_cache_entry(url)
        
        headers = {"User-Agent": self.user_agent}
        if cache_entry and cache_entry.etag:
            headers["If-None-Match"] = cache_entry.etag
        if cache_entry and cache_entry.last_modified:
            headers["If-Modified-Since"] = cache_entry.last_modified
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, headers=headers)
                    
                    # Handle 304 Not Modified
                    if response.status_code == 304:
                        return {
                            "url": url,
                            "status_code": 200,
                            "content": None,
                            "headers": dict(response.headers),
                            "cached": True
                        }
                    
                    # Update cache entry
                    etag = response.headers.get("etag")
                    last_modified = response.headers.get("last-modified")
                    new_entry = CacheEntry(url, etag, last_modified, response.status_code)
                    self._set_cache_entry(new_entry)
                    
                    return {
                        "url": url,
                        "status_code": response.status_code,
                        "content": response.content,
                        "headers": dict(response.headers),
                        "cached": False
                    }
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code in [429, 500, 502, 503, 504]:
                    if attempt < max_retries - 1:
                        delay = 2 ** attempt  # Exponential backoff
                        await asyncio.sleep(delay)
                        continue
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = 2 ** attempt
                    await asyncio.sleep(delay)
                    continue
                raise
        
        return None
