---
name: link-crawler
description: >
  Crawl active URLs from user-provided topics and root links, verify they are live (HTTP 200 with real content),
  and output a grouped markdown list of active links. Use this skill whenever the user asks to crawl links,
  harvest URLs, find active pages from a website, collect links from a page, check which links are alive/dead,
  scrape a sitemap or link tree, or audit links on a site. Also trigger when the user provides a list of URLs
  and asks to verify, validate, or check them. Trigger even if the user says "grab all links", "get me the URLs",
  "find pages on this site", "check these links", or similar casual phrasing about link collection or validation.
---

# Link Crawler

Crawl root URLs to a configurable depth, verify each discovered link is active (HTTP 200 + real page content),
and present results as a grouped markdown list.

## Workflow

### Step 1: Gather Inputs

Ask the user for:

1. **Topics and root links** — One or more topics, each with one or more starting URLs.
   Example input from user:
   ```
   Topic: Python Docs
   - https://docs.python.org/3/library/
   - https://docs.python.org/3/tutorial/

   Topic: FastAPI
   - https://fastapi.tiangolo.com/
   ```

2. **Crawl depth** — How many levels deep to follow links from each root page.
   - Depth 1 = only links found directly on the root page
   - Depth 2 = links on the root page + links on those pages
   - Default to 1 if user doesn't specify. Higher depths take longer and find more links.
   - Max recommended: 3 (beyond that, results explode and crawl time is very long)

If the user already provided topics and links in their message, skip asking and proceed.

### Step 2: Ask About Filtering

Before crawling, ask the user:

> "I can crawl **all links** from these pages, or focus on **specific groups/keywords**.
> Which do you prefer?"

Options:
- **All** — return every active link found
- **Specific groups** — user provides keywords or categories to filter (e.g., "only tutorial pages", "API reference only")

This determines the `filter_groups` value in the config. If "all", set to `null`.

### Step 3: Build Config and Run Crawler

Create a JSON config file at `/home/claude/crawl_config.json`:

```json
{
    "topics": [
        {
            "topic": "Topic Name",
            "root_links": ["https://example.com/page1", "https://example.com/page2"],
            "depth": 1
        }
    ],
    "filter_groups": null
}
```

Then run the crawler script:

```bash
python3 /path/to/skill/scripts/crawl_links.py --input /home/claude/crawl_config.json --timeout 10 2>/home/claude/crawl_log.txt
```

The script outputs JSON to stdout. Capture it:

```bash
python3 /path/to/skill/scripts/crawl_links.py --input /home/claude/crawl_config.json --timeout 10 > /home/claude/crawl_results.json 2>/home/claude/crawl_log.txt
```

The crawl log (stderr) shows progress. If the user is waiting, you can check the log to give status updates.

**Important constraints:**
- The script caps at 500 links per root URL to prevent runaway crawls
- Uses 10 concurrent threads with polite delays
- Checks that pages return HTTP 200 AND have real content (not error pages, empty pages, or placeholder pages)

### Step 4: Present Results

Read the JSON output and format as a **grouped markdown list** in chat.

**Format template:**

```
## 🔗 Crawl Results

### Topic Name
**X active links found** (Y dead/unreachable)

- https://example.com/page1
- https://example.com/page2
- https://example.com/page3
...

### Another Topic
**X active links found** (Y dead/unreachable)

- https://example.com/other1
- https://example.com/other2
...
```

**Formatting rules:**
- Group links under their topic heading
- Show count of active and dead links per topic
- List only active links (don't list dead ones unless the user asks)
- If a topic has more than 50 active links, show the first 50 and note how many more exist
- If the user asked for specific groups/keywords, mention what filter was applied

### Step 5: Offer Follow-up

After presenting results, offer:
- "Want me to save these to a file (markdown, CSV, or JSON)?"
- "Want me to crawl deeper on any of these topics?"
- "Want to see the dead/unreachable links?"

## Edge Cases

- **Timeouts**: Some sites are slow. If many links timeout, note it and suggest increasing the timeout.
- **Blocked by site**: Some sites block crawlers. If you see many 403s, let the user know.
- **No links found**: If a root page yields zero links, check if the URL is correct and accessible.
- **Duplicate links**: The script deduplicates automatically — same URL won't appear twice.
- **Non-HTML resources**: PDFs, images, etc. that return 200 are counted as active but won't be crawled deeper.

## Network Note

This skill requires network access to the domains being crawled. If domain access is restricted,
inform the user that their network settings may need to be updated by contacting an organization owner.
