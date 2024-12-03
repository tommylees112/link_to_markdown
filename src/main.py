import csv
import os
from pathlib import Path
from typing import List

import click
from loguru import logger

from converters.html_converter import HtmlConverter
from converters.markdown_converter import MarkdownWriter


def read_urls_from_csv(csv_path: Path, column_name: str) -> List[str]:
    """Read URLs from a CSV file."""
    urls = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        if column_name not in reader.fieldnames:
            available_columns = ", ".join(reader.fieldnames)
            raise click.BadParameter(
                f"Column '{column_name}' not found in CSV. Available columns: {available_columns}"
            )
        urls = [row[column_name] for row in reader if row[column_name]]
    return urls


def convert_urls_to_markdown(urls: List[str], output_dir: str = None) -> None:
    # If no output directory is provided, use OBSIDIAN_PATH environment variable
    if output_dir is None:
        output_dir = os.getenv("OBSIDIAN_PATH")
        if not output_dir:
            output_dir = click.prompt(
                "Please enter the output directory path OR set OBSIDIAN_PATH environment variable",
                type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
            )

    # Show directory and ask for confirmation
    print(f"Files will be saved to: {output_dir}")
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
    required=False,
    metavar="URLS...",  # Makes the help output clearer
)
@click.option(
    "--csv",
    type=click.Path(exists=True, path_type=Path),
    help="CSV file containing URLs to convert",
)
@click.option(
    "--column",
    help="Column name in CSV containing URLs",
)
@click.option(
    "--output-dir",
    "-o",
    help="Output directory for markdown files. Defaults to OBSIDIAN_PATH from environment variables",
)
def main(urls: tuple[str, ...], csv: Path, column: str, output_dir: str):
    """Convert URLs to markdown files.

    Takes URLs either directly as arguments or from a CSV file and converts them to
    markdown files, using the last part of the URL path as the filename (in snake_case).
    """
    if not urls and not csv:
        raise click.UsageError("Either --urls or --csv must be provided")

    if csv and not column:
        raise click.UsageError("--column must be provided when using --csv")

    all_urls = list(urls)

    if csv:
        logger.info(f"Reading URLs from CSV file: {csv}")
        csv_urls = read_urls_from_csv(csv, column)
        logger.info(f"Found {len(csv_urls)} URLs in CSV file")
        all_urls.extend(csv_urls)

    if not all_urls:
        raise click.UsageError("No URLs found to process")

    convert_urls_to_markdown(all_urls, output_dir)


if __name__ == "__main__":
    main()
