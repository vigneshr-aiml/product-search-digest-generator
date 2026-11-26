# Product Search, Comparison & Digest Generator

A modular Python web application that validates user product queries, discovers relevant vendor sources, scrapes and cleans product data concurrently, compares matching items across vendors, filters and sorts results, generates summary digests, and links back to original source pages.

## Features

- **Query Validation & Parsing:** Validates user search input, handles filler/stop words, and extracts optional price limits (e.g., `under 30000`).
- **Dynamic Source Discovery:** Matches user queries against configurable vendor sources defined in `sources.json`.
- **Concurrent Scraping & Fault Isolation:** Fetches pages across multiple sources concurrently with bounded worker threads and isolates unreachable or timed-out sources without crashing.
- **Multi-Format Parsing & Content Cleaning:** Extracts product details (title, description, price, rating, reviews, availability, and source URL) while stripping navigation, scripts, sidebars, and ad clutter.
- **Cross-Site Comparison, Filtering & Sorting:** Groups matching products across vendors, compares lowest price, top rating, and availability, and supports filtering by price, minimum rating, and stock status along with sorting options (`Lowest Price`, `Highest Price`, `Highest Rating`, `Recommended`).
- **Summary Digest & Source Attribution:** Generates a concise summary digest highlighting best deals, top-rated items, recommendations, and unreachable sources, with direct links to original source pages.
- **Automated Test Suite:** Includes unit and integration tests covering query validation, discovery, concurrency, fault tolerance, parsing, matching, filtering, sorting, and digest generation.

## Project Structure

- `app.py` — Web server and HTML/CSS user interface rendering search results, comparison tables, and digests.
- `scraper.py` — Query validation, source configuration loading, website discovery, and concurrent page fetching.
- `parser.py` — HTML cleaning/parsing, product normalization, relevance scoring, and cross-site product grouping.
- `digest_generator.py` — Filtering, sorting, comparison matrix construction, and summary digest generation.
- `generate_catalog.py` — Script to generate sample vendor HTML pages and `sources.json` catalog data.
- `sources.json` — External configuration of vendor sources, URLs, and keywords.
- `sample_sites/` — Sample multi-vendor HTML pages used for testing and local demonstrations.
- `test_suite.py` — Automated `unittest` suite (`TC01`–`TC10`).

## How to Run Locally (Windows)

1. Open PowerShell inside the `product_digest_app` folder.
2. Run the automated test suite:
   ```powershell
   py test_suite.py## How to Run Locally (Windows)
