import re
from urllib.parse import urlparse


def get_directory_from_url(url: str) -> str:
    """Extract just the directory name from the URL domain."""
    domain = urlparse(url).netloc
    domain = re.sub(r"^www\.", "", domain)  # Remove www. if present
    domain = re.sub(r"\.[^.]+$", "", domain)  # Remove TLD
    return domain
