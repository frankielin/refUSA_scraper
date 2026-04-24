# Reference USA Scraper

A minimal Selenium scraper for paginated business-data tables on ReferenceUSA (the business-records product formerly sold as ReferenceUSA, now part of Data Axle). Most universities license it through their library, behind a proxy and an SSO login.

The script opens a Chrome window, you log in through your campus portal in that window, navigate to your results page, and hand control back to the terminal. The script then scrapes each page, clicks the "next" arrow, waits a configurable number of seconds, and writes a timestamped CSV.

Intended for academic research within the bounds of your library's license.

## Requirements

- Python 3.9+
- Google Chrome
- Institutional access to Reference USA via your library proxy (if your library doesn't subscribe, this tool cannot help you)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup

1. Clone this repo.
2. (Optional) Edit `code/config.py` to set your institution's SSO logout URL and a display name. Both are optional — leaving them at the defaults means the scraper will just clear cookies on exit rather than redirecting through your IdP. See [Configuration](#configuration) below for examples.

## Usage

1. In your normal browser, log in to Reference USA via your library, run your search, and copy the **results-page URL** from the address bar.
2. From the repo root, run the scraper:

   ```bash
   python code/referenceusa_scraper.py
   ```

3. Follow the prompts:
   - Paste the URL and press Enter.
   - A Chrome window opens. Log in with your institutional credentials if prompted, then navigate to your results page.
   - Press Enter in the terminal; the script takes over.
   - Enter the number of pages to scrape (or press Enter for all).
4. When it finishes, answer `y` to the logout prompt to clear the session.

Output file: `referenceusa_data_<timestamp>.csv` in the current directory.

## Verifying selectors (optional)

If your results page layout differs from the defaults (Reference USA has shipped several table layouts over the years), run the interactive selector tester first:

```bash
python code/test_selectors.py
```

Paste the URL, log in, then enter CSS or XPath selectors to confirm they match the table and the "next" button.

## Stopping early

Press **Ctrl+C** in the terminal at any time. The script will ask whether to save the rows scraped so far; answer `y` to write a partial CSV.

## Logging out

The scraper offers to log out and clear cookies when it finishes. To log out manually at any other time:

```bash
python code/clear_session.py
```

This opens Chrome, visits your configured SSO logout URL (if set), clears cookies and local storage, and closes the browser.

## Configuration

`code/config.py` exposes two values:

| Constant | What it does |
|---|---|
| `SSO_LOGOUT_URL` | The URL your campus IdP uses to terminate a session. Hitting it at the end of scraping signs you out of SSO in that browser profile, not just out of Reference USA. Leave as `""` to skip. |
| `INSTITUTION_NAME` | Display string used in banners and prompts. Cosmetic only. |

A few real examples to show the pattern:

```python
# UW-Madison (Shibboleth)
SSO_LOGOUT_URL  = "https://login.wisc.edu/logout"
INSTITUTION_NAME = "UW-Madison"

# Harvard (Shibboleth)
SSO_LOGOUT_URL  = "https://www.pin1.harvard.edu/logout"
INSTITUTION_NAME = "Harvard"

# Generic CAS
SSO_LOGOUT_URL  = "https://sso.example.edu/cas/logout"
INSTITUTION_NAME = "Example University"
```

If you don't know your institution's SSO logout URL and don't want to go hunting for it, leave both at their defaults — the cookie/storage wipe is usually enough.

## Troubleshooting

| Problem | Fix |
|---|---|
| "No table found" | Run `python code/test_selectors.py` and try a different CSS selector; update the `table_selectors` list near the top of `code/referenceusa_scraper.py`. |
| Session expired mid-scrape | Get a fresh results-page URL and re-run; the default inter-page delay is already conservative. |
| Pages load slowly on your connection | Increase `wait_time` when constructing `ReferenceUSAScraper(wait_time=30)` in `referenceusa_scraper.py` (the `main()` function). |
| "Next" arrow not clicked | The scraper tries ~15 patterns including the `<div role="button">` variant Reference USA has used recently. If it still fails, use `test_selectors.py` to find the right selector and add it to the `referenceusa_selectors` or `next_selectors` list. |
| Script crashed, data lost | Partial data is saved on Ctrl+C but not on unhandled exceptions. Re-run and start from the page you left off. |

## Files

```
refUSA_pull/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
└── code/
    ├── config.py                 institution-specific URLs (edit once)
    ├── referenceusa_scraper.py   main scraper
    ├── test_selectors.py         interactive selector tester
    └── clear_session.py          standalone logout tool
```

## Notes

Intended for academic research. Respect your library's terms of service and Data Axle's rate limits — the default 30-second inter-page delay is deliberate. Many institutional licenses prohibit redistribution of extracted records; check your library's license before sharing scraped data, and do not post raw output to public repositories.

## License

MIT — see [LICENSE](LICENSE).
