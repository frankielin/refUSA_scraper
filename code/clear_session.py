"""
Clear browser sessions — standalone tool.

Use after scraping to sign out of your institution's SSO and drop cookies
for the current browser profile. The SSO URL comes from code/config.py;
leave it blank there if you only want the cookie/storage wipe.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

import config


def clear_all_sessions():
    """
    Clear browser cookies, local/session storage, and (optionally) hit the
    institutional SSO logout endpoint.
    """
    print("""
╔════════════════════════════════════════════════════════════╗
║                   Session Cleanup Tool                     ║
║           Clear Cookies & Log Out of SSO                   ║
╚════════════════════════════════════════════════════════════╝
    """)

    print("Opening browser to clear sessions...")

    options = webdriver.ChromeOptions()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Step 1: institutional SSO logout, if configured
        if config.SSO_LOGOUT_URL:
            print(f"\n1. Logging out of {config.INSTITUTION_NAME} SSO...")
            try:
                driver.get(config.SSO_LOGOUT_URL)
                time.sleep(3)
                print("   ✓ Visited SSO logout page")
            except Exception as e:
                print(f"   ⚠ Could not access logout page: {e}")
        else:
            print("\n1. No SSO_LOGOUT_URL configured in config.py — skipping.")

        # Step 2: wipe cookies and storage on the current origin
        print("\n2. Clearing browser cookies and storage...")
        try:
            driver.delete_all_cookies()
            print("   ✓ Cleared cookies")
        except Exception as e:
            print(f"   ⚠ Error clearing cookies: {e}")

        try:
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            print("   ✓ Cleared local/session storage")
        except Exception as e:
            print(f"   ⚠ Error clearing storage: {e}")

        print("\n" + "=" * 60)
        print("✓ Session cleanup complete!")
        print("=" * 60)
        print("\nYou'll need to log in again next time you use Reference USA.")

        input("\nPress Enter to close browser...")

    finally:
        driver.quit()
        print("\n✓ Done!")


if __name__ == "__main__":
    clear_all_sessions()
