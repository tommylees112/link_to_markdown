from dataclasses import dataclass
from pathlib import Path


@dataclass
class ArticleMetadata:
    """Metadata for tracking article download and conversion status."""

    path: Path  # Path to the markdown file relative to domain directory
    title: str  # Article title
    url: str  # Original URL
    domain: str  # Domain from URL
    status: str = "success"  # success, failed, rate_limited
    error_str: str = ""  # Error message if status is not success

    def to_dict(self) -> dict:
        """Convert to dictionary for CSV writing."""
        return {
            "path": str(self.path),
            "title": self.title,
            "url": self.url,
            "domain": self.domain,
            "status": self.status,
            "error_str": self.error_str,
        }

    @classmethod
    def from_dict(cls, data: dict, domain_dir: Path) -> "ArticleMetadata":
        """Create metadata from dictionary and domain directory."""
        return cls(
            path=Path(data["path"]),
            title=data["title"],
            url=data["url"],
            domain=data["domain"],
            status=data["status"],
            error_str=data["error_str"],
        )
