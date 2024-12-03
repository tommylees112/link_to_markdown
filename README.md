# 🔗 Link to Markdown

Convert web articles to beautifully formatted Markdown files! Perfect for your Obsidian vault or any markdown-based note-taking system. 📚

## 🌟 Features

- 🔄 Convert any web article to clean Markdown
- 📁 Automatically organize files by domain
- 📝 Smart title extraction from content
- 🎨 Clean and consistent formatting
- 🔧 Configurable output directory
- 🚀 Async processing for better performance

## 🚀 Quick Start

```bash
# Install dependencies
uv sync

# Convert a single URL
uv run src/main.py "https://example.com/article"

# Convert multiple URLs
uv run src/main.py "https://example.com/article1" "https://example.com/article2"

# Specify output directory
uv run src/main.py -o ./notes "https://example.com/article"
```

## 🏗️ Code Structure

The project is organized into modular components for better maintainability and testing:

```
src/
├── main.py                 # CLI interface and main orchestration
├── models/
│   └── document.py        # Document data model
├── converters/
│   ├── html_converter.py  # HTML to Markdown conversion
│   └── markdown_converter.py  # Markdown file writing
└── utils/
    ├── text_utils.py      # Text processing utilities
    └── url_utils.py       # URL parsing utilities
```

### 🧩 Components

- **Document Model** (`models/document.py`): Represents an article with its content and metadata
- **HTML Converter** (`converters/html_converter.py`): Handles fetching and converting web content to Markdown
- **Markdown Writer** (`converters/markdown_converter.py`): Manages file organization and writing
- **Utilities** (`utils/`): Common functions for text processing and URL handling

## 🌍 Environment Variables

- `OBSIDIAN_PATH`: Default output directory for Markdown files
- `USER_AGENT`: Custom user agent for web requests (optional)

## 📝 License

MIT License - Feel free to use and modify!
