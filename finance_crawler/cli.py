import asyncio
from datetime import date
from typing import List, Optional
import typer
from tqdm import tqdm

from .sources.builtin import get_builtin_sources, get_source_names
from .sources.base import GenericSpider
from .fetcher import AsyncFetcher
from .robots import RobotsChecker
from .storage import DocumentStorage
from .extractor import parse_date_string


def main(
    source: str = typer.Option("all", help="Comma-separated source names or 'all'"),
    out: str = typer.Option("./data", help="Output directory"),
    since: Optional[str] = typer.Option(None, help="Skip documents older than YYYY-MM-DD"),
    max_pages: int = typer.Option(400, help="Global max pages limit"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Don't write files, just log what would be saved")
):
    """Harvest documents from configured sources."""
    
    # Parse since date
    since_date = None
    if since:
        try:
            since_date = parse_date_string(since)
            if not since_date:
                typer.echo(f"Invalid date format: {since}. Use YYYY-MM-DD format.")
                raise typer.Exit(1)
        except Exception as e:
            typer.echo(f"Error parsing date: {e}")
            raise typer.Exit(1)
    
    # Get sources to process
    builtin_sources = get_builtin_sources()
    
    if source.lower() == "all":
        source_names = list(builtin_sources.keys())
    else:
        source_names = [s.strip() for s in source.split(",")]
        # Validate source names
        invalid_sources = [s for s in source_names if s not in builtin_sources]
        if invalid_sources:
            typer.echo(f"Invalid sources: {invalid_sources}")
            typer.echo(f"Available sources: {', '.join(get_source_names())}")
            raise typer.Exit(1)
    
    typer.echo(f"Processing sources: {', '.join(source_names)}")
    typer.echo(f"Output directory: {out}")
    typer.echo(f"Max pages: {max_pages}")
    if since_date:
        typer.echo(f"Since date: {since_date}")
    if dry_run:
        typer.echo("DRY RUN MODE - No files will be written")
    
    # Run async harvest
    asyncio.run(_harvest_async(source_names, builtin_sources, out, since_date, max_pages, dry_run))


async def _harvest_async(
    source_names: List[str],
    builtin_sources: dict,
    output_dir: str,
    since_date: Optional[date],
    max_pages: int,
    dry_run: bool
):
    """Async harvest implementation."""
    
    # Initialize components
    fetcher = AsyncFetcher()
    robots_checker = RobotsChecker()
    storage = DocumentStorage(output_dir)
    
    total_documents = 0
    source_stats = {}
    
    # Process each source
    for source_name in source_names:
        config = builtin_sources[source_name]
        typer.echo(f"\nProcessing {config.name}...")
        
        spider = GenericSpider(config, fetcher, robots_checker)
        
        # Create progress bar
        with tqdm(desc=f"Crawling {config.name}", unit="pages") as pbar:
            documents = await spider.crawl(max_pages)
            
            # Filter by date if specified
            if since_date:
                filtered_docs = [
                    doc for doc in documents 
                    if not doc.published_date or doc.published_date >= since_date
                ]
                typer.echo(f"Filtered {len(documents) - len(filtered_docs)} documents older than {since_date}")
                documents = filtered_docs
            
            # Save documents
            saved_count = 0
            for doc in documents:
                # Fetch document content
                response = await fetcher.fetch(doc.source_url)
                if response and response['content']:
                    success = storage.save_document(doc, response['content'], dry_run)
                    if success:
                        saved_count += 1
                        total_documents += 1
                
                pbar.update(1)
            
            source_stats[config.name] = saved_count
            typer.echo(f"Saved {saved_count} documents from {config.name}")
    
    # Print final statistics
    typer.echo(f"\nHarvest complete!")
    typer.echo(f"Total documents saved: {total_documents}")
    
    if source_stats:
        typer.echo("Breakdown by source:")
        for source, count in source_stats.items():
            typer.echo(f"  {source}: {count} documents")
    
    if not dry_run:
        catalog_stats = storage.get_catalog_stats()
        typer.echo(f"\nCatalog statistics:")
        typer.echo(f"  Total documents in catalog: {catalog_stats['total_documents']}")
        if catalog_stats['by_domain']:
            typer.echo("  By domain:")
            for domain, count in catalog_stats['by_domain'].items():
                typer.echo(f"    {domain}: {count}")


if __name__ == "__main__":
    typer.run(main)