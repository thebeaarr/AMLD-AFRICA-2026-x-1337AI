# content_loader.py - Extract content from URL or text
import requests
from bs4 import BeautifulSoup


def extract_from_url(url: str) -> str:
    """Extract text content from a URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text(separator='\n', strip=True)
        return text
    except Exception as e:
        raise Exception(f"Failed to extract content from URL: {e}")


def extract_from_text(text: str) -> str:
    """Return cleaned text content."""
    return text.strip()


def load_content(source: str) -> str:
    """Load content from URL or raw text."""
    if source.startswith("http://") or source.startswith("https://"):
        return extract_from_url(source)
    return extract_from_text(source)