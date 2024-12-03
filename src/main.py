import os
from pathlib import Path
from typing import List

import click
from loguru import logger

from converters.html_converter import HtmlConverter
from converters.markdown_converter import MarkdownWriter


def convert_urls_to_markdown(urls: List[str], output_dir: str = None) -> None:
    # If no output directory is provided, use OBSIDIAN_PATH environment variable
    if output_dir is None:
        output_dir = os.getenv("OBSIDIAN_PATH")
        if not output_dir:
            output_dir = click.prompt(
                "Please enter the output directory path",
                type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
            )

    # Show directory and ask for confirmation
    logger.info(f"Files will be saved to: {output_dir}")
    if not click.confirm("Do you want to continue?", default=True):
        logger.info("Operation cancelled by user")
        return

    # Convert URLs to documents
    converter = HtmlConverter()
    documents = converter.convert_urls(urls)

    # Save documents to markdown files
    writer = MarkdownWriter(Path(output_dir))
    writer.save_documents(documents)


@click.command()
@click.argument(
    "urls",
    nargs=-1,
    required=True,
    metavar="URLS...",  # Makes the help output clearer
)
@click.option(
    "--output-dir",
    "-o",
    help="Output directory for markdown files. Defaults to OBSIDIAN_PATH from environment variables",
)
def main(urls, output_dir):
    """Convert URLs to markdown files.

    Takes one or more URLs and converts them to markdown files, using the last part
    of the URL path as the filename (in snake_case).
    """
    convert_urls_to_markdown(list(urls), output_dir)


if __name__ == "__main__":
    main()
