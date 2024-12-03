import os
import re
from typing import List

from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import MarkdownifyTransformer
from loguru import logger

from models.document import Document
from utils.text_utils import extract_title_from_content
from utils.url_utils import get_directory_from_url


class HtmlConverter:
    def __init__(self):
        self._set_default_user_agent()

    def _set_default_user_agent(self):
        if not os.getenv("USER_AGENT"):
            os.environ["USER_AGENT"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            logger.info("Set default USER_AGENT for requests")

    def convert_urls(self, urls: List[str], **markdownify_kwargs) -> List[Document]:
        """Convert a list of URLs to Document objects with markdown content.

        Args:
            urls (List[str]): The URLs to convert
            **markdownify_kwargs: Additional keyword arguments to pass to
                MarkdownifyTransformer. https://github.com/matthewwithanm/python-markdownify

        Returns:
            List[Document]: A list of Document objects
        """
        logger.info(f"Processing {len(urls)} URLs...")

        # Load HTML content
        loader = AsyncHtmlLoader(urls)
        docs = loader.load()

        # Set default markdownify options if not provided
        default_options = {
            "heading_style": "ATX",  # Use # style headings
            "bullets": "*",  # Use * for unordered lists
            "strip": ["script", "style"],  # Remove script and style tags
        }
        markdownify_kwargs = {**default_options, **markdownify_kwargs}

        # Convert to markdown
        md_transformer = MarkdownifyTransformer()
        converted_docs = md_transformer.transform_documents(docs, **markdownify_kwargs)

        # Post-process to fix double bracket links
        processed_docs = []
        for doc in converted_docs:
            content = doc.page_content
            # Convert [[text]](url) to [text](url)
            content = re.sub(r"\[\[(.*?)\]\](\(.*?\))", r"[\1]\2", content)
            doc.page_content = content
            processed_docs.append(doc)

        # Create Document objects
        documents = []
        for i, doc in enumerate(processed_docs):
            directory = get_directory_from_url(urls[i])
            title = extract_title_from_content(doc.page_content)

            documents.append(
                Document(
                    url=urls[i],
                    content=doc.page_content,
                    title=title,
                    directory=directory,
                )
            )

        return documents
