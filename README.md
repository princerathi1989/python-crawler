# Finance Crawler

A polite, config-driven crawler to harvest authoritative Indian finance documents (PDF/CSV/XLS/XLSX/HTML) from Tier-1 sources including SEBI, NSE, AMFI, RBI, and Income Tax departments.

## Features

- **Async HTTP with httpx**: HTTP/2 support with efficient concurrent requests
- **Smart Caching**: ETag/Last-Modified caching with SQLite backend (304 handling)
- **Robots.txt Compliance**: Respects robots.txt rules for polite crawling
- **BFS Crawling**: Breadth-first search with configurable depth and page limits
- **Exponential Backoff**: Automatic retry with backoff on 429/5xx errors
- **Document Processing**: Extracts metadata from PDFs and HTML pages
- **Structured Storage**: Organized file storage with JSONL catalog
- **CLI Interface**: Easy-to-use Typer CLI with progress bars

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Harvest all sources
python -m finance_crawler.cli harvest --source all --out ./data --since 2024-01-01 --max-pages 400

# Harvest specific sources
python -m finance_crawler.cli harvest --source sebi,nse,amfi --out ./data --dry-run

# Get help
python -m finance_crawler.cli harvest --help
```

## Built-in Sources

The crawler comes with pre-configured sources for major Indian financial institutions:

- **SEBI** (`sebi`): Securities and Exchange Board of India
- **NSE** (`nse`): National Stock Exchange
- **AMFI** (`amfi`): Association of Mutual Funds in India
- **RBI SGB** (`rbi_sgb`): Reserve Bank of India - Sovereign Gold Bonds
- **Income Tax** (`income_tax`): Central Board of Direct Taxes

## CLI Options

- `--source`: Comma-separated source names or 'all' (default: all)
- `--out`: Output directory (default: ./data)
- `--since`: Skip documents older than YYYY-MM-DD
- `--max-pages`: Global page limit (default: 400)
- `--dry-run`: Don't write files, just log what would be saved

## Project Structure

```
finance-crawler/
├── README.md
├── requirements.txt
├── config/
│   └── sources.yaml                # Optional config overrides
├── finance_crawler/
│   ├── __init__.py
│   ├── cli.py                      # Typer CLI entrypoint
│   ├── schema.py                   # Pydantic models
│   ├── utils.py                    # URL tools, hashing, backoff
│   ├── robots.py                   # robots.txt utility
│   ├── fetcher.py                  # Async HTTP client + caching
│   ├── parser_html.py              # HTML link/title extraction
│   ├── parser_pdf.py               # PDF metadata extraction
│   ├── extractor.py                # Date parsing heuristics
│   ├── storage.py                  # File storage + catalog
│   └── sources/
│       ├── base.py                 # SourceConfig + GenericSpider
│       └── builtin.py             # Built-in source presets
└── tests/
    ├── test_schema.py
    ├── test_utils.py
    └── test_source_config.py
```

## Data Schema

Documents are stored with rich metadata including:

- **Document ID**: SHA1 hash of URL + title for deduplication
- **Title**: Extracted from PDF metadata or URL
- **Domain**: Financial domain (stock_equity, mutual_fund_etf, etc.)
- **Source Organization**: SEBI, NSE, AMFI, RBI, CBDT
- **Publication Date**: Extracted from PDF or URL
- **File Type**: pdf, csv, xlsx, xls, html
- **Quality Flags**: Official status, methodology presence, etc.
- **Topic Tags**: Auto-extracted financial topics

## Storage Convention

- **Catalog**: `<out>/catalog.jsonl` (one JSON per line)
- **Files**: `<out>/<domain>/<source_org>/<YYYY>/<type>__<title>__<date>.<ext>`

Example: `./data/stock_equity/sebi/2024/pdf__circular_123__2024-01-15.pdf`

## Legal and Politeness Notes

- **Respects robots.txt**: All requests check robots.txt before crawling
- **Rate Limiting**: Built-in exponential backoff on server errors
- **Caching**: Uses ETag/Last-Modified to avoid re-downloading unchanged files
- **User Agent**: Identifies as `finance-crawler-mvp/0.1`
- **Public Data Only**: Focuses on publicly available regulatory documents

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_schema.py -v
```

## Roadmap

- [ ] Playwright support for JavaScript-rendered content
- [ ] Custom source configuration via YAML files
- [ ] Advanced PDF text extraction and analysis
- [ ] Document similarity detection
- [ ] Web interface for browsing catalog
- [ ] Scheduled crawling with cron integration

## Contributing

This is a focused MVP implementation. The codebase is designed to be:
- **Small**: ~800 LOC excluding tests
- **Readable**: Clear separation of concerns
- **Testable**: Comprehensive test coverage
- **Extensible**: Easy to add new sources and parsers

## License

This project is for educational and research purposes. Please respect the terms of service of the websites being crawled and use responsibly.