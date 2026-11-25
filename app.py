import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from scraper import validate_query, discover_websites, scrape_websites_concurrently
from parser import parse_scraped_pages, match_products_across_sites
from digest_generator import filter_and_sort_products, build_comparison_matrix, generate_summary_digest


def render_page(query="", sort_by="price_asc", min_rating="0", only_stock=False, show_digest=False):
    status_html = digest_html = cards_html = matrix_html = ""

    if query:
        ok, msg, params = validate_query(query)
        if not ok:
            status_html = f'<div class="alert error">{html.escape(msg)}</div>'
        else:
            sites = discover_websites(params, "sources.json")
            successes, failures = scrape_websites_concurrently(sites, max_workers=6, timeout=2.0)
            records = parse_scraped_pages(successes, params["tokens"])
            filtered = filter_and_sort_products(
                records,
                max_price=params["max_price"],
                min_rating=float(min_rating or 0),
                only_in_stock=only_stock,
                sort_by=sort_by,
            )
            grouped = match_products_across_sites(filtered)
            matrix = build_comparison_matrix(grouped)

            status_html = (
                f'<div class="alert info">Found {len(sites)} matching website(s); '
                f'scraped {len(successes)} successfully ({len(failures)} unreachable). '
                f'Showing {len(filtered)} product listing(s) across {len(matrix)} unique product(s).</div>'
            )

            if show_digest:
                digest_text = generate_summary_digest(filtered, matrix, failures)
                digest_html = f'<section class="card digest"><h2>Summary Digest (FR9)</h2><p>{html.escape(digest_text)}</p></section>'

            card_items = []
            for r in filtered:
                card_items.append(f"""
                <div class="product-card">
                  <h3>{html.escape(r.title)}</h3>
                  <p class="desc">{html.escape(r.description)}</p>
                  <p><strong>Price:</strong> Rs. {r.price:.0f} | <strong>Rating:</strong> {r.rating} &#9733; ({r.reviews} reviews) | <strong>Availability:</strong> {html.escape(r.availability)}</p>
                  <a href="{html.escape(r.source_url)}" target="_blank" rel="noopener noreferrer">View original page at {html.escape(r.source_name)}</a>
                </div>""")
            cards_html = f'<section><h2>Scraped Products (FR3, FR7, FR10)</h2><div class="grid">{"".join(card_items) or "<p>No matching products.</p>"}</div></section>'

            rows = []
            for item in matrix:
                vendor_cells = "<br>".join(
                    f'{html.escape(o["source_name"])}: Rs. {o["price"]:.0f} ({o["rating"]}&#9733;, {html.escape(o["availability"])})'
                    for o in item["offers"]
                )
                rows.append(f"""
                <tr>
                  <td>{html.escape(item["product_title"])}</td>
                  <td>Rs. {item["lowest_price"]:.0f} ({html.escape(item["lowest_price_vendor"])})</td>
                  <td>{item["highest_rating"]} &#9733; ({html.escape(item["highest_rating_vendor"])})</td>
                  <td>{vendor_cells}</td>
                </tr>""")
            if rows:
                matrix_html = f"""
                <section>
                  <h2>Cross-Site Comparison Matrix (FR4, FR5, FR8)</h2>
                  <table>
                    <thead><tr><th>Product</th><th>Best Price</th><th>Top Rating</th><th>Vendor Breakdown</th></tr></thead>
                    <tbody>{"".join(rows)}</tbody>
                  </table>
                </section>"""

    stock_checked = "checked" if only_stock else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"><title>Product Search, Comparison &amp; Digest Generator</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0f172a; color: #e2e8f0; max-width: 1120px; margin: 0 auto; padding: 24px 18px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 14px; margin-bottom: 20px; }}
    .topbar h1 {{ margin: 0; font-size: 22px; color: #38bdf8; letter-spacing: 0.5px; }}
    .badge {{ background: #1e293b; color: #34d399; border: 1px solid #34d399; padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: bold; }}
    form {{ display: grid; grid-template-columns: 2fr 1fr 1fr auto auto auto; gap: 10px; background: #1e293b; padding: 16px; border-radius: 12px; border: 1px solid #334155; align-items: center; }}
    input[type="text"], select {{ background: #0f172a; color: #f8fafc; border: 1px solid #475569; padding: 10px; border-radius: 8px; }}
    label {{ font-size: 13px; color: #cbd5e1; white-space: nowrap; }}
    button {{ background: #0284c7; color: #fff; border: none; padding: 10px 14px; border-radius: 8px; font-weight: 600; cursor: pointer; }}
    button[value="1"] {{ background: #059669; }}
    .alert {{ padding: 12px 16px; border-radius: 8px; margin: 16px 0; font-size: 14px; }}
    .info {{ background: #172554; border: 1px solid #3b82f6; color: #93c5fd; }}
    .error {{ background: #450a0a; border: 1px solid #ef4444; color: #fca5a5; }}
    .digest {{ background: #064e3b; border: 1px solid #10b981; padding: 14px 18px; border-radius: 10px; margin: 16px 0; }}
    .digest h2 {{ margin-top: 0; color: #6ee7b7; font-size: 17px; }}
    h2 {{ color: #38bdf8; font-size: 18px; margin-top: 26px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 14px; }}
    .product-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 15px; transition: border-color 0.2s; }}
    .product-card h3 {{ margin-top: 0; color: #f1f5f9; font-size: 16px; }}
    .product-card a {{ display: inline-block; margin-top: 8px; color: #38bdf8; text-decoration: none; font-weight: 600; }}
    table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 10px; overflow: hidden; }}
    th, td {{ border-bottom: 1px solid #334155; padding: 11px 12px; text-align: left; vertical-align: top; font-size: 14px; }}
    th {{ background: #020617; color: #38bdf8; text-transform: uppercase; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="topbar">
    <h1>&#9889; Product Search, Comparison &amp; Digest Generator</h1>
    <span class="badge">LIVE PARALLEL SCRAPER</span>
  </div>
  <form method="GET" action="/">
    <input type="text" name="q" value="{html.escape(query)}" placeholder="Search products (e.g. Smartphone under 30000, Air Fryer)..." required />
    <select name="sort">
      <option value="price_asc" {"selected" if sort_by=="price_asc" else ""}>Sort: Lowest Price</option>
      <option value="price_desc" {"selected" if sort_by=="price_desc" else ""}>Sort: Highest Price</option>
      <option value="rating_desc" {"selected" if sort_by=="rating_desc" else ""}>Sort: Highest Rating</option>
      <option value="recommended" {"selected" if sort_by=="recommended" else ""}>Sort: Recommended</option>
    </select>
    <select name="min_rating">
      <option value="0" {"selected" if min_rating=="0" else ""}>Rating: All</option>
      <option value="4.0" {"selected" if min_rating=="4.0" else ""}>Rating &ge; 4.0 &#9733;</option>
      <option value="4.5" {"selected" if min_rating=="4.5" else ""}>Rating &ge; 4.5 &#9733;</option>
    </select>
    <label><input type="checkbox" name="in_stock" value="1" {stock_checked}/> In Stock</label>
    <button type="submit" name="digest" value="0">Analyze</button>
    <button type="submit" name="digest" value="1">Generate Digest</button>
  </form>
  {status_html}
  {digest_html}
  {cards_html}
  {matrix_html}
</body>
</html>"""


class DigestRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        page = render_page(
            query=qs.get("q", [""])[0],
            sort_by=qs.get("sort", ["price_asc"])[0],
            min_rating=qs.get("min_rating", ["0"])[0],
            only_stock=qs.get("in_stock", ["0"])[0] == "1",
            show_digest=qs.get("digest", ["0"])[0] == "1",
        )
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), DigestRequestHandler)
    print("Server running at http://127.0.0.1:8000")
    server.serve_forever()
