from pathlib import Path
from typing import List

from loguru import logger

from models.document import Document


class MarkdownWriter:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using output directory: {self.output_dir}")

    def save_documents(self, documents: List[Document]) -> None:
        """Save documents to markdown files in their respective directories."""
        for doc in documents:
            # Create subdirectory if needed
            full_dir_path = self.output_dir / doc.directory
            full_dir_path.mkdir(parents=True, exist_ok=True)

            # Save the document
            output_file = full_dir_path / f"{doc.title}.md"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(doc.content)
            logger.success(f"Created: {output_file}")
