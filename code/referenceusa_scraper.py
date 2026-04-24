"""
Reference USA historical business-data scraper for academic research.

Access is assumed to go through your institution's library proxy and single
sign-on portal. Edit code/config.py once to point at your SSO logout URL.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

import config

class ReferenceUSAScraper:
    def __init__(self, wait_time=30):
        """
        Initialize scraper for ReferenceUSA
        
        Args:
            wait_time: Seconds to wait between page clicks (default 30)
        """
        self.wait_time = wait_time
        self.data = []
        self.page_count = 0  # Track current page for status updates
        
        # Set up Chrome options
        options = webdriver.ChromeOptions()
        # Keep browser visible so you can see what's happening
        options.add_argument('--start-maximized')
        
        # Initialize Chrome driver with auto-installation
        print("Setting up Chrome driver...")
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def wait_for_login(self, result_url):
        """
        Navigate to URL and wait for user to log in if needed
        """
        print(f"\nNavigating to: {result_url}")
        self.driver.get(result_url)
        
        print("\n" + "="*60)
        print("AUTHENTICATION CHECK")
        print("="*60)
        print("\nIf you see a login page:")
        print("  1. Log in with your institutional credentials (SSO / campus portal)")
        print("  2. Navigate to your results page")
        print("  3. Press Enter in this terminal when ready")
        print("\nIf you're already on the results page:")
        print("  Just press Enter to continue")
        print("="*60 + "\n")
        
        input("Press Enter when you're on the results page...")
        print("\n✓ Ready to start scraping!\n")
        
    def scrape_current_page(self):
        """
        Scrape the table from the current ReferenceUSA results page
        """
        try:
            # Wait a moment for page to fully load (additional buffer)
            time.sleep(2)
            
            print("  📊 Reading table data...")
            
            # Try multiple table selectors
            table_selectors = [
                'table',
                'table.results',
                'table[id*="result"]',
                'table[class*="result"]',
                'div.results table',
                'div[id*="result"] table'
            ]
            
            table = None
            for selector in table_selectors:
                try:
                    table = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    print(f"  Found table using: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not table:
                print("  ⚠ Could not find table with standard selectors")
                return 0
            
            # Extract rows from table
            rows = table.find_elements(By.TAG_NAME, 'tr')
            rows_added = 0
            
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if not cells:  # Try header cells if no data cells
                    cells = row.find_elements(By.TAG_NAME, 'th')
                
                if cells:
                    row_data = [cell.text.strip() for cell in cells]
                    # Only add if row has data
                    if any(row_data):
                        self.data.append(row_data)
                        rows_added += 1
            
            print(f"  ✓ Scraped {rows_added} rows")
            return rows_added
            
        except Exception as e:
            print(f"  ✗ Error scraping page: {e}")
            return 0
    
    def click_next(self):
        """
        Click the next button on ReferenceUSA
        Handles text buttons, image buttons, div buttons, and arrow symbols
        
        Returns:
            bool: True if next button was clicked, False otherwise
        """
        # Try ReferenceUSA-specific selectors FIRST (div with role="button")
        referenceusa_selectors = [
            'div[role="button"][aria-label*="next"]',
            'div.next.button',
            'div[aria-label="Go to next page"]',
            'div.next[role="button"]',
            'div[title*="scroll through records"]',
            'div.mousedown-enterkey.next'
        ]
        
        for selector in referenceusa_selectors:
            try:
                next_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                # Check if disabled
                button_class = next_button.get_attribute('class') or ''
                if 'disabled' in button_class.lower():
                    print("  Next button is disabled (last page)")
                    return False
                
                # Scroll into view and click
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5)
                next_button.click()
                
                print(f"  ✓ Clicked next (ReferenceUSA div button)")
                return True
                
            except (TimeoutException, NoSuchElementException):
                continue
        
        # Try CSS selectors for text-based next buttons
        next_selectors = [
            'a[title*="Next"]',
            'button[title*="Next"]',
            'a.next',
            'button.next',
            'a[id*="next"]',
            'button[id*="next"]',
            'a[class*="next"]',
            'button[class*="next"]',
            '.pagination .next',
            'a[rel="next"]'
        ]
        
        for selector in next_selectors:
            try:
                next_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                
                # Check if disabled
                button_class = next_button.get_attribute('class') or ''
                if 'disabled' in button_class.lower():
                    print("  Next button is disabled (last page)")
                    return False
                
                # Scroll into view and click
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5)
                next_button.click()
                
                print(f"  ✓ Clicked next (selector: {selector})")
                return True
                
            except (TimeoutException, NoSuchElementException):
                continue
        
        # Try finding image-based next buttons
        image_selectors = [
            'a img[alt*="next"]',
            'a img[alt*="Next"]',
            'a img[src*="next"]',
            'a img[src*="arrow"]',
            'a img[src*="forward"]',
            'button img[alt*="next"]',
            'button img[src*="arrow"]'
        ]
        
        for selector in image_selectors:
            try:
                img = self.driver.find_element(By.CSS_SELECTOR, selector)
                # Click the parent link/button
                parent = img.find_element(By.XPATH, '..')
                
                # Check if disabled
                parent_class = parent.get_attribute('class') or ''
                if 'disabled' in parent_class.lower():
                    print("  Next button is disabled (last page)")
                    return False
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", parent)
                time.sleep(0.5)
                parent.click()
                print(f"  ✓ Clicked next (image button: {selector})")
                return True
            except:
                continue
        
        # Try finding by partial link text
        try:
            next_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, 'Next')
            if next_links:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", next_links[0])
                time.sleep(0.5)
                next_links[0].click()
                print("  ✓ Clicked next (found by text)")
                return True
        except:
            pass
        
        # Try XPath for text-based buttons
        xpath_text_selectors = [
            "//div[@role='button' and contains(@aria-label, 'next')]",
            "//div[@role='button' and contains(@aria-label, 'Next')]",
            "//div[contains(@class, 'next') and @role='button']",
            "//a[contains(text(), 'Next')]",
            "//button[contains(text(), 'Next')]",
            "//a[contains(@title, 'Next')]",
            "//button[contains(@title, 'Next')]"
        ]
        
        for xpath in xpath_text_selectors:
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                element.click()
                print("  ✓ Clicked next (XPath text)")
                return True
            except:
                continue
        
        # Try XPath for image-based buttons (arrow images)
        xpath_image_selectors = [
            "//a[.//img[contains(@alt, 'next')]]",
            "//a[.//img[contains(@alt, 'Next')]]",
            "//a[.//img[contains(@src, 'next')]]",
            "//a[.//img[contains(@src, 'arrow')]]",
            "//a[.//img[contains(@src, 'forward')]]",
            "//button[.//img[contains(@alt, 'next')]]",
            "//button[.//img[contains(@src, 'arrow')]]"
        ]
        
        for xpath in xpath_image_selectors:
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                
                # Check if disabled
                element_class = element.get_attribute('class') or ''
                if 'disabled' in element_class.lower():
                    print("  Next button is disabled (last page)")
                    return False
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                element.click()
                print("  ✓ Clicked next (XPath image)")
                return True
            except:
                continue
        
        # Try finding pagination container and clicking last enabled link
        try:
            pagination_containers = [
                '.pagination',
                'div[class*="paging"]',
                'div[class*="navigation"]',
                'div[id*="paging"]',
                'ul.pagination'
            ]
            
            for container_selector in pagination_containers:
                try:
                    container = self.driver.find_element(By.CSS_SELECTOR, container_selector)
                    # Find all clickable elements (links or buttons)
                    links = container.find_elements(By.TAG_NAME, 'a')
                    buttons = container.find_elements(By.TAG_NAME, 'button')
                    
                    # Try the last enabled link/button (often the next button)
                    for element in reversed(links + buttons):
                        element_class = element.get_attribute('class') or ''
                        if 'disabled' not in element_class.lower():
                            # Check if it contains an arrow symbol
                            text = element.text
                            if any(arrow in text for arrow in ['>', '→', '›', '»', '▶']):
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                time.sleep(0.5)
                                element.click()
                                print("  ✓ Clicked next (arrow in pagination)")
                                return True
                except:
                    continue
        except:
            pass
        
        # Try finding elements containing arrow symbols
        try:
            arrow_xpath = "//a[contains(text(), '→') or contains(text(), '>') or contains(text(), '›') or contains(text(), '»') or contains(text(), '▶')]"
            elements = self.driver.find_elements(By.XPATH, arrow_xpath)
            if elements:
                element = elements[0]
                element_class = element.get_attribute('class') or ''
                if 'disabled' not in element_class.lower():
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(0.5)
                    element.click()
                    print("  ✓ Clicked next (arrow symbol)")
                    return True
        except:
            pass
        
        print("  ⚠ Could not find next button (may be last page)")
        return False
    
    def scrape_all_pages(self, result_url, max_pages=None):
        """
        Scrape all pages of results
        
        Args:
            result_url: The ReferenceUSA result page URL
            max_pages: Maximum number of pages to scrape (None for all)
        """
        # Navigate and handle login
        self.wait_for_login(result_url)
        
        # NOW ask about page limit after they've logged in and can see the results
        print("\n" + "="*60)
        print("How many pages do you want to scrape?")
        limit_input = input("  (Press Enter for ALL pages, or type a number): ").strip()
        
        if limit_input.isdigit():
            max_pages = int(limit_input)
            print(f"  → Will scrape {max_pages} pages")
        else:
            print("  → Will scrape ALL pages")
        
        self.page_count = 1
        print("="*60)
        print(f"STARTING SCRAPE - {self.wait_time} second wait after clicking")
        print("="*60)
        print("\n💡 TIP: Press Ctrl+C at any time to stop scraping")
        print("         You'll be asked if you want to save partial data\n")
        
        while True:
            print(f"Page {self.page_count}:")
            
            # If not first page, we already clicked and waited - just scrape
            # If first page, scrape immediately
            rows_scraped = self.scrape_current_page()
            
            if rows_scraped == 0:
                print("  ⚠ No data found on this page (continuing anyway)")
            
            # Check if we've hit max pages
            if max_pages and self.page_count >= max_pages:
                print(f"\n✓ Reached maximum pages ({max_pages})")
                break
            
            # Try to click next
            if self.click_next():
                # Wait for page to fully load BEFORE scraping next page
                print(f"  ⏳ Waiting {self.wait_time} seconds for page to load...")
                time.sleep(self.wait_time)
                self.page_count += 1
                print()  # Blank line between pages
            else:
                print("\n✓ No more pages available")
                break
        
        print("\n" + "="*60)
        print("SCRAPING COMPLETE")
        print("="*60)
        print(f"Pages scraped: {self.page_count}")
        print(f"Total rows: {len(self.data)}")
        
    def save_data(self, filename='referenceusa_data.csv'):
        """Save scraped data to CSV"""
        if not self.data:
            print("\n⚠ No data to save")
            return
        
        df = pd.DataFrame(self.data)
        df = df.drop_duplicates()  # Remove duplicates
        df.to_csv(filename, index=False, header=False)
        
        print(f"\n✓ Saved to: {filename}")
        print(f"✓ Total rows: {len(df)}")
        
        # Show preview
        print("\nFirst 5 rows:")
        print(df.head())
        
    def logout_and_clear(self):
        """
        Log out and clear session data
        """
        print("\nClearing session...")

        # Try to navigate to the institutional SSO logout page, if configured
        if config.SSO_LOGOUT_URL:
            try:
                print(f"  Logging out of {config.INSTITUTION_NAME}...")
                self.driver.get(config.SSO_LOGOUT_URL)
                time.sleep(2)
            except:
                print("  (Could not access logout page - will clear cookies instead)")
        else:
            print("  (No SSO_LOGOUT_URL configured - skipping IdP logout)")
        
        # Clear all cookies
        try:
            self.driver.delete_all_cookies()
            print("  ✓ Cleared all cookies")
        except:
            print("  (Could not clear cookies)")
        
        # Clear browser cache/local storage
        try:
            self.driver.execute_script("window.localStorage.clear();")
            self.driver.execute_script("window.sessionStorage.clear();")
            print("  ✓ Cleared browser storage")
        except:
            pass
        
        print("  ✓ Session cleared")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()


def main():
    """Main execution"""
    print("""
╔════════════════════════════════════════════════════════════╗
║              Reference USA Academic Scraper                ║
╚════════════════════════════════════════════════════════════╝

IMPORTANT: Use only for legitimate academic research, within the
terms of your library's Reference USA / Data Axle license.
""")
    
    # Get URL from user
    RESULT_URL = input("Enter your ReferenceUSA result URL: ").strip()
    
    if not RESULT_URL:
        print("Error: No URL provided")
        return
    
    # Set parameters
    WAIT_TIME = 30  # Seconds between pages
    
    # Create scraper
    scraper = ReferenceUSAScraper(wait_time=WAIT_TIME)
    
    try:
        # Run the scraper (max_pages will be asked after login)
        scraper.scrape_all_pages(result_url=RESULT_URL)
        
        # Save data
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f'referenceusa_data_{timestamp}.csv'
        scraper.save_data(filename)
        
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("⚠ SCRAPING STOPPED (Ctrl+C pressed)")
        print("="*60)
        print(f"\nYou scraped {scraper.page_count} pages before stopping.")
        print(f"Total rows collected: {len(scraper.data)}")
        
        if len(scraper.data) > 0:
            save = input("\nSave partial data? (y/n): ").strip().lower()
            if save == 'y':
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f'referenceusa_partial_{timestamp}.csv'
                scraper.save_data(filename)
            else:
                print("Data not saved.")
        else:
            print("No data collected yet.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Ask about logging out
        print("\n" + "="*60)
        logout_choice = input("Log out and clear session? (y/n): ").strip().lower()
        
        if logout_choice == 'y':
            scraper.logout_and_clear()
        else:
            print("Skipping logout (session will remain active)")
        
        print("\nClosing browser...")
        scraper.close()
        print("✓ Done!")


if __name__ == "__main__":
    main()