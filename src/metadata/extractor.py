import csv
from pathlib import Path
from typing import Dict, Set

from loguru import logger

from src.models.metadata import ArticleMetadata


class MetadataManager:
    """Manages article metadata in domain-specific CSV files."""

    CSV_FILENAME = "meta.csv"
    FIELDNAMES = ["path", "title", "url", "domain", "status", "error_str"]

    def __init__(self, output_dir: Path, skip_existing: bool = True):
        self.output_dir = output_dir
        self.skip_existing = skip_existing
        # Track processed URLs by domain
        self.processed_urls: Dict[str, Set[str]] = {}

    def get_domain_csv_path(self, domain: str) -> Path:
        """Get path to the metadata CSV file for a domain."""
        return self.output_dir / domain / self.CSV_FILENAME

    def load_domain_metadata(self, domain: str) -> None:
        """Load metadata for a specific domain."""
        csv_path = self.get_domain_csv_path(domain)
        if not csv_path.exists():
            self.processed_urls[domain] = set()
            return

        try:
            with open(csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                # Only track URLs that were successfully processed
                self.processed_urls[domain] = {
                    row["url"] for row in reader if row["status"] == "success"
                }
        except Exception as e:
            logger.warning(f"Error loading metadata from {csv_path}: {e}")
            self.processed_urls[domain] = set()

    def should_process_url(self, url: str, domain: str) -> bool:
        """Check if a URL should be processed."""
        if domain not in self.processed_urls:
            self.load_domain_metadata(domain)

        # If skip_existing is True, skip URLs that were successfully processed
        return not self.skip_existing or url not in self.processed_urls[domain]

    def add_metadata(self, metadata: ArticleMetadata) -> None:
        """Add or update metadata for a URL."""
        csv_path = self.get_domain_csv_path(metadata.domain)

        # Read existing entries
        existing: Dict[str, dict] = {}
        if csv_path.exists():
            try:
                with open(csv_path, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    existing = {row["url"]: row for row in reader}
            except Exception as e:
                logger.warning(f"Error reading {csv_path}: {e}")

        # Update with new entry
        existing[metadata.url] = metadata.to_dict()

        # Ensure directory exists
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        # Write all entries back to CSV
        try:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
                writer.writeheader()
                writer.writerows(existing.values())

            # Update processed URLs if status is success
            if metadata.status == "success":
                if metadata.domain not in self.processed_urls:
                    self.processed_urls[metadata.domain] = set()
                self.processed_urls[metadata.domain].add(metadata.url)

        except Exception as e:
            logger.error(f"Error writing to {csv_path}: {e}")

    def create_error_metadata(
        self, url: str, domain: str, error: str, status: str = "failed"
    ) -> ArticleMetadata:
        """Create metadata entry for a failed download."""
        return ArticleMetadata(
            path=Path("failed_downloads.md"),
            title="failed_download",
            url=url,
            domain=domain,
            status=status,
            error_str=error,
        )
