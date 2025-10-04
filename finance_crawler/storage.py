import json
import os
from pathlib import Path
from datetime import date
from typing import Optional, Dict, Any
from .schema import DocumentRecord
from .utils import short_title_from_url


class DocumentStorage:
    """Handles file storage and catalog management."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.catalog_path = self.output_dir / "catalog.jsonl"
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_storage_path(self, record: DocumentRecord) -> str:
        """Generate storage path for document."""
        # Format: <domain>/<source_org>/<YYYY>/<type>__<short-title>__<YYYY-MM-DD|undated>.<ext>
        
        domain = record.domain
        source_org = record.source_org.lower().replace(' ', '_')
        
        # Get year from published_date or current year
        year = str(record.published_date.year) if record.published_date else str(date.today().year)
        
        # Generate short title
        short_title = short_title_from_url(record.source_url)
        if len(short_title) > 30:
            short_title = short_title[:30]
        
        # Format date
        date_str = record.published_date.strftime("%Y-%m-%d") if record.published_date else "undated"
        
        # File extension
        ext = record.file_type
        
        filename = f"{record.file_type}__{short_title}__{date_str}.{ext}"
        
        return f"{domain}/{source_org}/{year}/{filename}"
    
    def save_document(self, record: DocumentRecord, content: bytes, dry_run: bool = False) -> bool:
        """Save document file and catalog entry."""
        if dry_run:
            print(f"DRY RUN: Would save {record.source_url} to {record.storage_path}")
            return True
        
        # Generate storage path
        storage_path = self._generate_storage_path(record)
        record.storage_path = storage_path
        
        # Create full file path
        file_path = self.output_dir / storage_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file already exists with same size
        if file_path.exists() and file_path.stat().st_size == len(content):
            print(f"File already exists with same size: {file_path}")
            # Still add to catalog
            self._append_to_catalog(record)
            return True
        
        try:
            # Write file
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Add to catalog
            self._append_to_catalog(record)
            
            print(f"Saved: {file_path}")
            return True
            
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")
            return False
    
    def _append_to_catalog(self, record: DocumentRecord):
        """Append record to catalog.jsonl."""
        try:
            with open(self.catalog_path, 'a', encoding='utf-8') as f:
                json.dump(record.model_dump(), f, ensure_ascii=False, default=str)
                f.write('\n')
        except Exception as e:
            print(f"Error writing to catalog: {e}")
    
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get statistics from catalog."""
        if not self.catalog_path.exists():
            return {"total_documents": 0, "by_source": {}, "by_domain": {}}
        
        stats = {
            "total_documents": 0,
            "by_source": {},
            "by_domain": {}
        }
        
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        record_data = json.loads(line)
                        stats["total_documents"] += 1
                        
                        # Count by source
                        source = record_data.get("source_org", "unknown")
                        stats["by_source"][source] = stats["by_source"].get(source, 0) + 1
                        
                        # Count by domain
                        domain = record_data.get("domain", "unknown")
                        stats["by_domain"][domain] = stats["by_domain"].get(domain, 0) + 1
                        
        except Exception as e:
            print(f"Error reading catalog stats: {e}")
        
        return stats
