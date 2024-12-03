from dataclasses import dataclass


@dataclass
class Document:
    """Represents a document with its content and metadata."""

    url: str
    content: str
    title: str = None
    directory: str = None
