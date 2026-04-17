#!/usr/bin/env python3
"""
Link Crawler — Crawls root URLs to a configurable depth, checks each link
is active (HTTP 200 + non-trivial content), and outputs grouped results as JSON.

Usage:
    python crawl_links.py --input config.json [--timeout 10]

config.json format:
{
    "topics": [
        {
            "topic": "Python Docs",
            "root_links": ["https://docs.python.org/3/"],
            "depth": 1
        }
    ],
    "filter_groups": null  // null = all, or ["group1", "keyword"]
}

Output: JSON to stdout with grouped active/dead link lists.
"""

import argparse
import json
import sys
import re
import time
import urllib.request
import urllib.error
import urllib.parse
from html.parser import HTMLParser
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed


class LinkExtractor(HTMLParser):
    """Extract href links from HTML content."""
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr_name, attr_val in attrs:
                if attr_name == "href" and attr_val:
                    self.links.append(attr_val)


def is_real_content(html_text: str) -> bool:
    """Check if a page has real content (not an empty/error/placeholder page)."""
    if not html_text or len(html_text.strip()) < 256:
        return False

    lower = html_text.lower()

    # Common error/placeholder patterns
    error_patterns = [
        r"<title>\s*(404|403|500|502|503|not found|error|page not found|access denied)",
        r"<h1>\s*(404|not found|error|oops|page not found|forbidden)",
        r"the page you.*(looking for|requested).*(not|cannot|doesn.t)",
        r"this page (doesn.t|does not) exist",
        r"nothing (was )?found here",
        r"under construction",
        r"coming soon",
    ]
    for pat in error_patterns:
        if re.search(pat, lower):
            return False

    # Strip tags and check remaining text length
    text_only = re.sub(r"<[^>]+>", " ", html_text)
    text_only = re.sub(r"\s+", " ", text_only).strip()
    if len(text_only) < 100:
        return False

    return True


def normalize_url(url: str, base_url: str) -> str | None:
    """Resolve relative URLs and normalize. Returns None for non-HTTP URLs."""
    try:
        resolved = urllib.parse.urljoin(base_url, url)
        parsed = urllib.parse.urlparse(resolved)
        if parsed.scheme not in ("http", "https"):
            return None
        # Remove fragments
        clean = urllib.parse.urlunparse(parsed._replace(fragment=""))
        return clean
    except Exception:
        return None


def fetch_page(url: str, timeout: int = 10) -> tuple[int, str]:
    """Fetch a URL. Returns (status_code, body_text). Returns (-1, "") on error."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; LinkCrawler/1.0)"
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.getcode()
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "text/plain" not in content_type:
                # Non-HTML resource — treat as active if 200
                return (status, "<non-html-resource>")
            body = resp.read(500_000).decode("utf-8", errors="replace")
            return (status, body)
    except urllib.error.HTTPError as e:
        return (e.code, "")
    except Exception:
        return (-1, "")


def extract_links(html: str, base_url: str) -> list[str]:
    """Extract and normalize all links from HTML."""
    parser = LinkExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass

    results = []
    seen = set()
    for raw in parser.links:
        norm = normalize_url(raw, base_url)
        if norm and norm not in seen:
            seen.add(norm)
            results.append(norm)
    return results


def crawl(root_url: str, max_depth: int, timeout: int, max_links: int = 500) -> dict:
    """
    Crawl starting from root_url up to max_depth levels.
    Returns dict with 'active' and 'dead' link lists.
    """
    visited = {}  # url -> {"status": int, "active": bool}
    to_visit = [(root_url, 0)]  # (url, depth)
    queued = {root_url}

    while to_visit and len(visited) < max_links:
        batch = to_visit[:20]
        to_visit = to_visit[20:]

        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = {pool.submit(fetch_page, url, timeout): (url, depth) for url, depth in batch}
            for fut in as_completed(futures):
                url, depth = futures[fut]
                status, body = fut.result()
                is_active = status == 200 and (body == "<non-html-resource>" or is_real_content(body))
                visited[url] = {"status": status, "active": is_active}

                # Extract child links if within depth
                if is_active and depth < max_depth and body != "<non-html-resource>":
                    children = extract_links(body, url)
                    for child in children:
                        if child not in queued and len(queued) < max_links:
                            queued.add(child)
                            to_visit.append((child, depth + 1))

        # Small delay to be polite
        time.sleep(0.2)

    active = [url for url, info in visited.items() if info["active"]]
    dead = [{"url": url, "status": info["status"]} for url, info in visited.items() if not info["active"]]
    return {"active": active, "dead": dead}


def main():
    parser = argparse.ArgumentParser(description="Crawl links and check activity")
    parser.add_argument("--input", required=True, help="Path to config JSON file")
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout in seconds")
    args = parser.parse_args()

    with open(args.input) as f:
        config = json.load(f)

    results = {}
    for topic_cfg in config["topics"]:
        topic = topic_cfg["topic"]
        depth = topic_cfg.get("depth", 1)
        all_active = []
        all_dead = []

        for root_url in topic_cfg["root_links"]:
            print(f"[crawling] {topic} -> {root_url} (depth={depth})", file=sys.stderr)
            data = crawl(root_url, max_depth=depth, timeout=args.timeout)
            all_active.extend(data["active"])
            all_dead.extend(data["dead"])

        # Deduplicate
        seen = set()
        deduped_active = []
        for u in all_active:
            if u not in seen:
                seen.add(u)
                deduped_active.append(u)

        results[topic] = {
            "active_count": len(deduped_active),
            "dead_count": len(all_dead),
            "active_links": deduped_active,
            "dead_links": all_dead,
        }

    # Apply group filter if specified
    filter_groups = config.get("filter_groups")
    if filter_groups:
        filtered = {}
        for key in results:
            if any(fg.lower() in key.lower() for fg in filter_groups):
                filtered[key] = results[key]
        results = filtered if filtered else results  # Fallback to all if no match

    json.dump(results, sys.stdout, indent=2)


if __name__ == "__main__":
    main()
