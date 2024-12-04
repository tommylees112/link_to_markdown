import csv
import os
from pathlib import Path
from typing import List
from urllib.parse import quote, urlparse

import click
from loguru import logger

from src.converters.html_converter import HtmlConverter
from src.converters.markdown_converter import MarkdownWriter


def read_urls_from_csv(
    csv_path: Path, column: str = None, column_index: int = None
) -> List[str]:
    """Read URLs from a CSV file using either column name or index."""
    urls = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)

        # Validate column specification
        if column and column_index is not None:
            raise click.BadParameter(
                "Please specify either --column or --column-index, not both"
            )

        if column:
            if column not in reader.fieldnames:
                available_columns = ", ".join(reader.fieldnames)
                raise click.BadParameter(
                    f"Column '{column}' not found in CSV. Available columns: {available_columns}"
                )
            get_value = lambda row: row[column]
        elif column_index is not None:
            if column_index >= len(reader.fieldnames):
                raise click.BadParameter(
                    f"Column index {column_index} is out of range. Max index: {len(reader.fieldnames) - 1}"
                )
            get_value = lambda row: list(row.values())[column_index]
        else:
            raise click.BadParameter(
                "Either --column or --column-index must be specified"
            )

        for row in reader:
            url = get_value(row)
            if not url:
                continue

            # Clean and validate URL
            try:
                # Check if it's a full URL
                parsed = urlparse(url)
                if not parsed.scheme:
                    # If no scheme, assume it's a relative path and encode it
                    url = quote(url)
                    logger.warning(
                        f"Found relative path: {url}, you might need to add the base URL"
                    )
                    continue
                urls.append(url)
            except Exception as e:
                logger.warning(f"Skipping invalid URL '{url}': {e}")
                continue

    logger.info(f"Found {len(urls)} valid URLs in CSV file")
    return urls


def convert_urls_to_markdown(
    urls: List[str],
    output_dir: str = None,
    skip_existing: bool = True,
    force: bool = False,
) -> None:
    # If no output directory is provided, use OBSIDIAN_PATH environment variable
    if output_dir is None:
        output_dir = os.getenv("OBSIDIAN_PATH")
        if not output_dir:
            output_dir = click.prompt(
                "Please enter the output directory path OR set OBSIDIAN_PATH environment variable",
                type=click.Path(
                    exists=False, file_okay=False, dir_okay=True, path_type=Path
                ),
            )

    output_path = Path(output_dir)

    # Create directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Show directory and ask for confirmation (unless force is True)
    click.echo(f"\nFiles will be saved to: {output_path}")
    if not force:
        try:
            if not click.confirm("\nDo you want to continue?", default=True):
                logger.info("Operation cancelled by user")
                return
        except click.exceptions.Abort:
            logger.info("Operation cancelled by user")
            return
    else:
        logger.info("Force mode enabled - skipping confirmation prompts")

    # Convert URLs to documents
    converter = HtmlConverter(output_dir=output_path, skip_existing=skip_existing)
    documents = converter.convert_urls(urls)

    # Save documents to markdown files
    writer = MarkdownWriter(output_path)
    writer.save_documents(documents)


@click.command()
@click.argument(
    "urls",
    nargs=-1,
    required=False,
    metavar="URLS...",
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
    "--column-index",
    type=int,
    help="Column index (0-based) in CSV containing URLs",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
    help="Output directory for markdown files. Defaults to OBSIDIAN_PATH from environment variables",
)
@click.option(
    "--no-skip-existing",
    is_flag=True,
    help="Process all URLs even if they've been successfully processed before",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Skip all confirmation prompts",
)
def main(
    urls: tuple[str, ...],
    csv: Path,
    column: str,
    column_index: int,
    output_dir: str,
    no_skip_existing: bool,
    force: bool,
):
    """Convert URLs to markdown files."""
    if not urls and not csv:
        raise click.UsageError("Either URLs or --csv must be provided")

    if csv and not (column or column_index is not None):
        raise click.UsageError(
            "Either --column or --column-index must be provided when using --csv"
        )

    all_urls = list(urls)

    if csv:
        logger.info(f"Reading URLs from CSV file: {csv}")
        try:
            csv_urls = read_urls_from_csv(csv, column=column, column_index=column_index)
            if not csv_urls:
                raise click.UsageError("No valid URLs found in CSV file")
            all_urls.extend(csv_urls)
        except Exception as e:
            raise click.UsageError(f"Error reading CSV file: {e}")

    if not all_urls:
        raise click.UsageError("No URLs found to process")

    convert_urls_to_markdown(
        all_urls,
        output_dir=output_dir,
        skip_existing=not no_skip_existing,
        force=force,
    )


if __name__ == "__main__":
    main()
