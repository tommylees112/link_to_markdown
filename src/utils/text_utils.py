import re


def to_snake_case(title: str) -> str:
    """Convert a string to snake case."""
    # Remove special characters and convert to lowercase
    title = re.sub(r"[^\w\s-]", "", title)
    # Replace spaces and hyphens with underscores
    return re.sub(r"[-\s]+", "_", title).strip().lower()


def extract_title_from_content(content: str, max_lines: int = 20) -> str:
    """Extract the article title from markdown content.

    Args:
        content: The markdown content to parse
        max_lines: Maximum number of lines to check before falling back
    """
    # Only split the first N lines to avoid parsing the entire document
    lines = content.split("\n", max_lines)[:max_lines]

    # First try: Look for a clean h1 heading (most common case)
    for line in lines:
        if line.startswith("# ") and "[" not in line:
            return to_snake_case(line[2:])

    # Quick fallback: First non-empty, non-link line
    for line in lines:
        line = line.strip()
        if line and "[" not in line and "]" not in line:
            return to_snake_case(line)

    # Final fallback if nothing found in first N lines
    return to_snake_case(lines[0].strip())
