import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import MarkdownifyTransformer
from loguru import logger

from metadata.extractor import MetadataManager
from models.document import Document
from models.metadata import ArticleMetadata
from utils.text_utils import extract_title_from_content
from utils.url_utils import get_directory_from_url


class HtmlConverter:
    def __init__(self, output_dir: Optional[Path] = None, skip_existing: bool = True):
        self._set_default_user_agent()
        self.output_dir = output_dir
        self.metadata_manager = (
            MetadataManager(output_dir, skip_existing) if output_dir else None
        )

    def _set_default_user_agent(self):
        if not os.getenv("USER_AGENT"):
            os.environ["USER_AGENT"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            logger.info("Set default USER_AGENT for requests")

    def convert_urls(self, urls: List[str], **markdownify_kwargs) -> List[Document]:
        """Convert a list of URLs to Document objects with markdown content."""
        if not urls:
            return []

        # Filter URLs based on metadata
        urls_to_process, skipped_urls = self._filter_urls(urls)

        # Log processing summary
        total = len(urls)
        skipped = len(skipped_urls)
        to_process = len(urls_to_process)

        if skipped:
            logger.debug(f"Skipping {skipped} already processed URLs\n:{skipped_urls}")

        if not urls_to_process:
            logger.info("No new URLs to process")
            return []

        logger.info(f"Processing {to_process} new URLs out of {total} total")

        try:
            # Process all URLs in one batch
            documents = self._process_urls_batch(urls_to_process, **markdownify_kwargs)
            return documents
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            return []

    def _filter_urls(self, urls: List[str]) -> Tuple[List[str], List[str]]:
        """Filter out already processed URLs based on metadata.

        Returns:
            Tuple of (urls_to_process, skipped_urls)
        """
        if not self.metadata_manager:
            return urls, []

        urls_to_process = []
        skipped_urls = []

        for url in urls:
            domain = get_directory_from_url(url)
            if self.metadata_manager.should_process_url(url, domain):
                urls_to_process.append(url)
            else:
                skipped_urls.append(url)

        return urls_to_process, skipped_urls

    def _process_urls_batch(
        self, urls: List[str], **markdownify_kwargs
    ) -> List[Document]:
        """Process a batch of URLs together."""
        # Load HTML content for all URLs at once
        loader = AsyncHtmlLoader(urls)
        docs = loader.load()

        # Set default markdownify options
        default_options = {
            "heading_style": "ATX",
            "bullets": "*",
            "strip": ["script", "style"],
        }
        markdownify_kwargs = {**default_options, **markdownify_kwargs}

        # Convert all to markdown
        md_transformer = MarkdownifyTransformer()
        converted_docs = md_transformer.transform_documents(docs, **markdownify_kwargs)

        documents = []
        successful_metadata = []
        failed_urls = []
        rate_limited_urls = []

        # Process each converted document
        for i, doc in enumerate(converted_docs):
            try:
                url = urls[i]
                content = doc.page_content

                # Check for rate limiting or error pages
                if (
                    "too many requests" in content.lower()
                    or "rate limit" in content.lower()
                ):
                    rate_limited_urls.append(url)
                    continue

                # Process content
                content = re.sub(r"\[\[(.*?)\]\](\(.*?\))", r"[\1]\2", content)

                # Create document
                domain = get_directory_from_url(url)
                title = extract_title_from_content(content)

                document = Document(
                    url=url,
                    content=content,
                    title=title,
                    directory=domain,
                )
                documents.append(document)

                # Create metadata but don't save yet
                if self.metadata_manager and self.output_dir:
                    metadata = ArticleMetadata(
                        path=Path(f"{title}.md"),
                        title=title,
                        url=url,
                        domain=domain,
                    )
                    successful_metadata.append(metadata)

            except Exception as e:
                logger.error(f"Error processing {urls[i]}: {e}")
                failed_urls.append(urls[i])

        # Log processing results
        total = len(urls)
        successful = len(successful_metadata)
        rate_limited = len(rate_limited_urls)
        failed = len(failed_urls)

        logger.info(
            f"Processing complete: {successful} successful, "
            f"{rate_limited} rate limited, {failed} failed"
        )

        if rate_limited_urls:
            logger.warning("Rate limited URLs:")
            for url in rate_limited_urls:
                logger.warning(f"  - {url}")
                self._handle_error(
                    url, "Rate limited - too many requests", "rate_limited"
                )

        if failed_urls:
            logger.error("Failed URLs:")
            for url in failed_urls:
                logger.error(f"  - {url}")
                self._handle_error(url, "Processing failed")

        # Update metadata for all successful conversions at once
        if self.metadata_manager:
            for metadata in successful_metadata:
                self.metadata_manager.add_metadata(metadata)

        return documents

    def _handle_error(self, url: str, error_msg: str, status: str = "failed") -> None:
        """Handle and record errors."""
        if not self.metadata_manager:
            return

        domain = get_directory_from_url(url)
        metadata = self.metadata_manager.create_error_metadata(
            url=url,
            domain=domain,
            error=error_msg,
            status=status,
        )
        self.metadata_manager.add_metadata(metadata)
