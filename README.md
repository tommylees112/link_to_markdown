# 🔗 Link to Markdown

Convert web articles to beautifully formatted Markdown files! Perfect for your Obsidian vault or any markdown-based note-taking system. 📚

## 🌟 Features

- 🔄 Convert any web article to clean Markdown
- 📁 Automatically organize files by domain
- 📝 Smart title extraction from content
- 🎨 Clean and consistent formatting
- 🔧 Configurable output directory
- 🚀 Async processing for better performance
- 🔌 Compatible with Instant Data Scraper Chrome extension for batch URL processing
- 📊 Metadata tracking with CSV files per domain
- ⏸️ Resume support for interrupted downloads
- 🔁 Automatic retry handling for rate limits

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Create command-line alias (add to your ~/.bashrc, ~/.zshrc, or equivalent)
alias l2m='uv run src/main.py'

# Convert a single URL
l2m "https://example.com/article"

# Convert multiple URLs
l2m "https://example.com/article1" "https://example.com/article2"

# Specify output directory
l2m -o ./notes "https://example.com/article"

# Force reprocess existing URLs
l2m --no-skip-existing "https://example.com/article"
```

## 🔌 Chrome Extension Integration

This tool works seamlessly with the [Instant Data Scraper](https://chrome.google.com/webstore/detail/instant-data-scraper/ofaokhiedipichpaobibbnahnkdoiiah) Chrome extension:

1. Use Instant Data Scraper to collect URLs from any website
2. Export the URLs as CSV
3. Extract the URL column and save as a text file
4. Process multiple URLs at once using:

```bash
qsv select -n 1 urls.csv | xargs uv run src/main.py
```

OR

```bash
uv run src/main.py --csv urls.csv --column "relative href"
```

## 📁 Directory Structure

The tool organizes content by domain and tracks metadata:

```
output_dir/
├── example_com/
│   ├── meta.csv          # Metadata tracking for this domain
│   ├── article1.md       # Article content
│   └── article2.md       # Article content
└── another_site/
    ├── meta.csv
    └── article3.md
```

### 📊 Metadata Tracking

Each domain directory contains a `meta.csv` file that tracks:

- `path`: Relative path to the markdown file
- `title`: Article title
- `url`: Original URL
- `domain`: Source domain
- `status`: Download status (success/failed/rate_limited)
- `error_str`: Error message if failed

Example `meta.csv`:

```csv
path,title,url,domain,status,error_str
article1.md,First Article,https://example.com/1,example_com,success,
article2.md,Second Article,https://example.com/2,example_com,rate_limited,"Rate limited - too many requests"
```

### 🔁 Resume and Retry

The tool automatically handles interruptions and rate limits:

- Tracks processed URLs in domain-specific CSV files
- Skips already downloaded content by default
- Records failed downloads with error messages
- Allows forced reprocessing with `--no-skip-existing`

To retry failed downloads:

```bash
# Extract failed URLs from meta.csv
qsv search -s status -v success domain/meta.csv | qsv select url | xargs uv run src/main.py
```

## 🏗️ Code Structure

The project is organized into modular components for better maintainability and testing:

```
src/
├── main.py                 # CLI interface and main orchestration
├── models/
│   ├── document.py        # Document data model
│   └── metadata.py        # Metadata tracking model
├── metadata/
│   └── extractor.py       # Metadata management
├── converters/
│   ├── html_converter.py  # HTML to Markdown conversion
│   └── markdown_converter.py  # Markdown file writing
└── utils/
    ├── text_utils.py      # Text processing utilities
    └── url_utils.py       # URL parsing utilities
```

### 🧩 Components

- **Document Model** (`models/document.py`): Represents an article with its content
- **Metadata Model** (`models/metadata.py`): Tracks article processing status
- **Metadata Manager** (`metadata/extractor.py`): Handles CSV operations and URL tracking
- **HTML Converter** (`converters/html_converter.py`): Handles fetching and converting web content
- **Markdown Writer** (`converters/markdown_converter.py`): Manages file organization and writing
- **Utilities** (`utils/`): Common functions for text processing and URL handling

## 🌍 Environment Variables

- `OBSIDIAN_PATH`: Default output directory for Markdown files
- `USER_AGENT`: Custom user agent for web requests (optional)

## 📝 License

MIT License - Feel free to use and modify!
