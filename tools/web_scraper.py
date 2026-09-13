#!/usr/bin/env python3
"""
Generic Web Scraper for Blog Index Pages

Scrapes articles from blog index pages and saves them as markdown files.
Uses Playwright for browser automation and trafilatura for content extraction.

Usage:
    python tools/web_scraper.py <index_url> <output_dir> [options]

Examples:
    # Basic usage
    python tools/web_scraper.py "https://graphite.io/five-percent" "Library/Graphite-5-Percent/"

    # With custom link selector
    python tools/web_scraper.py "https://site.com/blog" "Library/Site/" --link-selector "article a.title"

    # Limit for testing
    python tools/web_scraper.py "https://site.com" "Library/Test/" --limit 3

    # Substack (auto-navigates to archive)
    python tools/web_scraper.py "https://www.growth-memo.com" "Library/Growth-Memo/" --substack
"""
from __future__ import annotations
# Support both direct scripts and package imports.
if __package__:
    from .optional_dependencies import require_dependency, run_cli, launch_chromium
else:
    from optional_dependencies import require_dependency, run_cli, launch_chromium

import argparse
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse, urljoin



# Default patterns for article links
ARTICLE_URL_PATTERNS = [
    r'/post/',
    r'/p/',
    r'/article/',
    r'/blog/',
    r'/posts/',
    r'/\d{4}/\d{2}/',  # Date-based URLs like /2024/01/
    r'-[a-f0-9]{8,}$',  # Slug with hash suffix
]

# URL patterns to exclude (navigation, categories, etc.)
EXCLUDE_URL_PATTERNS = [
    r'/tag/',
    r'/tags/',
    r'/category/',
    r'/categories/',
    r'/author/',
    r'/page/\d+',
    r'/archive/?$',
    r'/about/?$',
    r'/contact/?$',
    r'/subscribe/?$',
    r'/login/?$',
    r'/signup/?$',
    r'#',
    r'\?utm_',
]


def sanitize_filename(title: str) -> str:
    """
    Convert a page title to a safe filename.

    Args:
        title: The page title

    Returns:
        Sanitized filename (without extension)
    """
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '', title)
    # Replace spaces and multiple dashes
    filename = re.sub(r'\s+', '-', filename)
    filename = re.sub(r'-+', '-', filename)
    # Trim to reasonable length
    filename = filename[:100].strip('-')
    # Fallback for empty titles
    return filename or 'untitled'


def is_article_link(href: str, base_host: str) -> bool:
    """
    Determine if a URL looks like an article link.

    Args:
        href: The URL to check
        base_host: The base hostname for comparison

    Returns:
        True if this looks like an article link
    """
    if not href:
        return False

    # Parse the URL
    parsed = urlparse(href)

    # Must be same host or relative
    if parsed.netloc and parsed.netloc != base_host:
        return False

    path = parsed.path.lower()

    # Check exclusion patterns first
    for pattern in EXCLUDE_URL_PATTERNS:
        if re.search(pattern, href, re.IGNORECASE):
            return False

    # Check inclusion patterns
    for pattern in ARTICLE_URL_PATTERNS:
        if re.search(pattern, path):
            return True

    # Heuristic: URL has a slug-like path (words separated by dashes)
    # e.g., /some-article-title or /blog/some-article-title
    path_parts = [p for p in path.split('/') if p]
    if path_parts:
        last_part = path_parts[-1]
        # Looks like a slug if it has dashes and letters
        if '-' in last_part and re.search(r'[a-z]', last_part):
            # But not too short (likely a category)
            if len(last_part) > 10:
                return True

    return False


def get_article_links(page: Page, base_url: str, link_selector: Optional[str] = None,
                      max_scrolls: int = 20) -> list[str]:
    """
    Get all article links from an index page.

    Args:
        page: Playwright page object
        base_url: The base URL for resolving relative links
        link_selector: Optional CSS selector for article links
        max_scrolls: Maximum scroll attempts for infinite scroll pages

    Returns:
        List of article URLs
    """
    print("Discovering article links...")

    parsed_base = urlparse(base_url)
    base_host = parsed_base.netloc

    # Wait for initial load
    page.wait_for_load_state('load')
    time.sleep(2)

    # Scroll to load all content (for infinite scroll pages)
    last_count = 0
    stable_count = 0

    for i in range(max_scrolls):
        # Scroll down
        page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(1)

        # Count links to check if more loaded
        if link_selector:
            links = page.query_selector_all(link_selector)
        else:
            links = page.query_selector_all('a[href]')

        current_count = len(links)

        if current_count == last_count:
            stable_count += 1
            if stable_count >= 3:
                print(f"  Content fully loaded after {i+1} scrolls")
                break
        else:
            stable_count = 0
            last_count = current_count

    # Scroll back to top
    page.evaluate('window.scrollTo(0, 0)')
    time.sleep(0.5)

    # Collect all links
    if link_selector:
        print(f"  Using custom selector: {link_selector}")
        links = page.query_selector_all(link_selector)
    else:
        # Use multiple strategies to find article links
        selectors = [
            'article a[href]',
            '.post a[href]',
            '.article a[href]',
            '.entry a[href]',
            'a[href*="/post/"]',
            'a[href*="/p/"]',
            'a[href*="/article/"]',
            'main a[href]',
            'a[href]',  # Fallback to all links
        ]

        links = []
        for selector in selectors:
            found = page.query_selector_all(selector)
            if found:
                links = found
                print(f"  Found {len(found)} links with selector: {selector}")
                if len(found) > 2:  # If we found a reasonable number, use this
                    break

    # Extract and filter URLs
    article_urls = []
    seen = set()

    for link in links:
        href = link.get_attribute('href')
        if not href:
            continue

        # Resolve relative URLs
        full_url = urljoin(base_url, href)

        # Normalize (remove fragments and common query params)
        parsed = urlparse(full_url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        if normalized in seen:
            continue
        seen.add(normalized)

        # Check if it looks like an article
        if link_selector or is_article_link(normalized, base_host):
            article_urls.append(normalized)

    print(f"  Found {len(article_urls)} article links")
    return article_urls


def extract_article_content(page: Page, url: str) -> dict:
    """
    Extract article content using trafilatura.

    Args:
        page: Playwright page with article loaded
        url: The article URL (for metadata)

    Returns:
        Dict with title, author, date, content, and source_url
    """
    trafilatura = require_dependency("trafilatura", "web")
    # Get the full HTML
    html = page.content()

    # Get metadata first (separately from content)
    metadata = trafilatura.extract_metadata(html)

    # Extract content without embedded metadata
    content = trafilatura.extract(
        html,
        url=url,
        include_comments=False,
        include_tables=True,
        include_images=True,
        include_links=True,
        output_format='markdown',
        with_metadata=False,  # Don't include metadata in content
    )

    # Clean up content: strip any leading YAML frontmatter trafilatura might add
    if content:
        # Remove leading --- metadata block if present
        content = re.sub(r'^---\n.*?\n---\n*', '', content, flags=re.DOTALL)
        content = content.strip()

    # Build result dict
    article = {
        'content': content or '',
        'source_url': url,
        'title': None,
        'author': None,
        'date': None,
    }

    # Extract metadata
    if metadata:
        article['title'] = metadata.title
        article['author'] = metadata.author
        article['date'] = metadata.date

    # Fallback title extraction if trafilatura didn't get it
    if not article['title']:
        # Try page title
        title = page.title()
        if title:
            # Clean up common suffixes
            title = re.sub(r'\s*[|\-–—]\s*[^|\-–—]+$', '', title).strip()
            article['title'] = title

        # Try h1
        if not article['title']:
            h1 = page.query_selector('h1')
            if h1:
                article['title'] = h1.inner_text().strip()

    # Final fallback
    if not article['title']:
        article['title'] = 'Untitled'

    return article


def format_markdown_output(article: dict) -> str:
    """
    Format article as markdown with frontmatter.

    Args:
        article: Dict with title, content, author, date, source_url

    Returns:
        Formatted markdown string
    """
    lines = ['---']
    lines.append(f'source: {article["source_url"]}')
    lines.append(f'scraped: {datetime.now().strftime("%Y-%m-%d")}')

    if article.get('title'):
        # Escape quotes in title for YAML
        safe_title = article['title'].replace('"', '\\"')
        lines.append(f'title: "{safe_title}"')

    if article.get('author'):
        safe_author = article['author'].replace('"', '\\"')
        lines.append(f'author: "{safe_author}"')

    if article.get('date'):
        lines.append(f'date: {article["date"]}')

    lines.append('---')
    lines.append('')

    # Add title as H1 if we have it
    if article.get('title'):
        lines.append(f"# {article['title']}")
        lines.append('')

    # Add content
    if article.get('content'):
        lines.append(article['content'])
    else:
        lines.append('*No content extracted*')

    return '\n'.join(lines)


def get_existing_source_urls(output_dir: Path) -> set[str]:
    """
    Get set of source URLs from existing markdown files.

    Args:
        output_dir: Directory to scan

    Returns:
        Set of source URLs already scraped
    """
    existing = set()

    if not output_dir.exists():
        return existing

    for md_file in output_dir.glob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
            # Look for source URL in frontmatter
            match = re.search(r'^source:\s*(.+)$', content, re.MULTILINE)
            if match:
                existing.add(match.group(1).strip())
        except Exception:
            pass

    return existing


def scrape_website(
    index_url: str,
    output_dir: str,
    link_selector: Optional[str] = None,
    limit: Optional[int] = None,
    delay: float = 1.5,
    substack: bool = False,
    skip_existing: bool = True,
) -> dict:
    """
    Scrape articles from a website index page.

    Args:
        index_url: URL of the index/archive page
        output_dir: Directory to save markdown files
        link_selector: Optional CSS selector for article links
        limit: Optional limit on number of articles
        delay: Delay between page loads (seconds)
        substack: If True, navigate to /archive first
        skip_existing: If True, skip URLs already scraped

    Returns:
        Dict with success_count, error_count, files, errors, skipped
    """
    sync_playwright = require_dependency("playwright.sync_api", "web").sync_playwright
    PlaywrightTimeout = require_dependency("playwright.sync_api", "web").TimeoutError
    require_dependency("trafilatura", "web")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = {
        'success_count': 0,
        'error_count': 0,
        'skipped_count': 0,
        'files': [],
        'errors': [],
    }

    # Get existing source URLs for deduplication
    existing_urls = set()
    if skip_existing:
        existing_urls = get_existing_source_urls(output_path)
        if existing_urls:
            print(f"Found {len(existing_urls)} already-scraped URLs")

    with sync_playwright() as p:
        print("Launching browser...")
        browser = launch_chromium(p.chromium, headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Navigate to index page
        target_url = index_url
        if substack:
            # For Substack, the archive is at /archive
            parsed = urlparse(index_url)
            if not parsed.path or parsed.path == '/':
                target_url = f"{parsed.scheme}://{parsed.netloc}/archive"
                print(f"Substack mode: navigating to {target_url}")

        print(f"Navigating to: {target_url}")
        try:
            page.goto(target_url, wait_until='load', timeout=60000)
            time.sleep(3)
        except PlaywrightTimeout:
            print("Warning: Page load timed out, continuing anyway...")

        # Get article links
        article_urls = get_article_links(page, target_url, link_selector)

        if not article_urls:
            print("No article links found. Try specifying a --link-selector")
            browser.close()
            return results

        # Filter out existing URLs
        if skip_existing:
            original_count = len(article_urls)
            article_urls = [url for url in article_urls if url not in existing_urls]
            skipped = original_count - len(article_urls)
            if skipped > 0:
                print(f"Skipping {skipped} already-scraped articles")
                results['skipped_count'] = skipped

        # Apply limit
        if limit:
            article_urls = article_urls[:limit]
            print(f"Limited to {limit} articles")

        print(f"\nProcessing {len(article_urls)} articles...")

        # Process each article
        for idx, article_url in enumerate(article_urls):
            print(f"\n[{idx + 1}/{len(article_urls)}] {article_url[:70]}...")

            try:
                # Navigate to article
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        page.goto(article_url, wait_until='load', timeout=45000)
                        time.sleep(2)
                        break
                    except PlaywrightTimeout:
                        if attempt < max_retries - 1:
                            print(f"  Retry {attempt + 1}/{max_retries}...")
                            time.sleep(2)
                        else:
                            raise

                # Extract content
                article = extract_article_content(page, article_url)
                print(f"  Title: {article['title'][:50]}..." if len(article['title']) > 50 else f"  Title: {article['title']}")

                # Check if we got meaningful content
                if not article['content'] or len(article['content']) < 100:
                    print("  Warning: Very little content extracted")

                # Format as markdown
                markdown = format_markdown_output(article)

                # Generate filename
                filename = sanitize_filename(article['title']) + '.md'
                filepath = output_path / filename

                # Handle duplicate filenames
                counter = 1
                while filepath.exists():
                    filename = f"{sanitize_filename(article['title'])}-{counter}.md"
                    filepath = output_path / filename
                    counter += 1

                # Save file
                filepath.write_text(markdown, encoding='utf-8')
                print(f"  Saved: {filename}")

                results['files'].append(str(filepath))
                results['success_count'] += 1

                # Delay between pages
                if idx < len(article_urls) - 1:
                    time.sleep(delay)

            except PlaywrightTimeout as e:
                error_msg = f"Timeout: {article_url}"
                print(f"  Error: {error_msg}")
                results['errors'].append(error_msg)
                results['error_count'] += 1

            except Exception as e:
                error_msg = f"{str(e)[:80]}: {article_url}"
                print(f"  Error: {error_msg}")
                results['errors'].append(error_msg)
                results['error_count'] += 1

        browser.close()

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Scrape articles from blog index pages to markdown files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://graphite.io/five-percent" "Library/Graphite/"
  %(prog)s "https://growth-memo.com" "Library/Growth-Memo/" --substack
  %(prog)s "https://site.com/blog" "Library/Site/" --link-selector "article a"
  %(prog)s "https://site.com" "Library/Test/" --limit 3
        """
    )
    parser.add_argument(
        'url',
        help='URL of the blog index/archive page'
    )
    parser.add_argument(
        'output_dir',
        help='Directory to save markdown files'
    )
    parser.add_argument(
        '--link-selector',
        help='CSS selector for article links (default: auto-detect)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of articles to scrape'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=1.5,
        help='Delay between page loads in seconds (default: 1.5)'
    )
    parser.add_argument(
        '--substack',
        action='store_true',
        help='Substack mode: navigate to /archive for article list'
    )
    parser.add_argument(
        '--no-skip-existing',
        action='store_true',
        help='Re-scrape articles that already exist in output directory'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Web Scraper")
    print("=" * 60)
    print(f"URL: {args.url}")
    print(f"Output: {args.output_dir}")
    if args.link_selector:
        print(f"Link selector: {args.link_selector}")
    if args.limit:
        print(f"Limit: {args.limit} articles")
    if args.substack:
        print("Mode: Substack")
    print("=" * 60)

    results = scrape_website(
        index_url=args.url,
        output_dir=args.output_dir,
        link_selector=args.link_selector,
        limit=args.limit,
        delay=args.delay,
        substack=args.substack,
        skip_existing=not args.no_skip_existing,
    )

    print("\n" + "=" * 60)
    print("SCRAPE COMPLETE")
    print("=" * 60)
    print(f"Success: {results['success_count']} articles")
    print(f"Errors:  {results['error_count']} articles")
    print(f"Skipped: {results['skipped_count']} (already scraped)")
    print(f"Files saved to: {args.output_dir}")

    if results['errors']:
        print("\nErrors encountered:")
        for error in results['errors'][:10]:  # Show first 10
            print(f"  - {error}")
        if len(results['errors']) > 10:
            print(f"  ... and {len(results['errors']) - 10} more")

    return 0 if results['error_count'] == 0 else 1


if __name__ == '__main__':
    sys.exit(run_cli(main))
