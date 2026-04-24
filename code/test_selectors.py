"""
Test CSS Selectors - Interactive Tool
Use this FIRST to verify your table and next button selectors work
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_selector(driver, selector, selector_type='CSS'):
    """Test if a selector finds elements"""
    try:
        if selector_type == 'CSS':
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
        else:  # XPath
            elements = driver.find_elements(By.XPATH, selector)
        
        if elements:
            print(f"  ✓ Found {len(elements)} element(s)")
            for i, elem in enumerate(elements[:3], 1):
                try:
                    text = elem.text[:60] if elem.text else '[no text]'
                    tag = elem.tag_name
                    print(f"    {i}. <{tag}> {text}")
                except:
                    print(f"    {i}. [element exists but couldn't read]")
            return True
        else:
            print(f"  ✗ No elements found")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║           Selector Testing Tool                            ║
║              Test Before You Scrape!                       ║
╚════════════════════════════════════════════════════════════╝

This tool helps you find the right selectors for:
  1. The results table
  2. The "Next" button

Once you find selectors that work, you'll use them in the scraper.
    """)
    
    url = input("Enter your ReferenceUSA results URL: ").strip()
    if not url:
        print("Error: No URL provided")
        return
    
    print("\n📌 Setting up Chrome driver...")
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print(f"📌 Navigating to: {url}")
        driver.get(url)
        
        print("\n" + "="*60)
        print("If you need to log in, do so now in the browser window.")
        print("Press Enter when you're on the RESULTS page...")
        print("="*60)
        input()
        
        time.sleep(2)
        
        print("\n✓ Ready to test selectors!")
        print("\nSUGGESTED TEST SEQUENCE:")
        print("-" * 60)
        print("1. Find the table first")
        print("2. Then find the next button")
        print("3. Test clicking the next button to make sure it works")
        print("-" * 60)
        
        # Suggest common table selectors
        print("\n📋 COMMON TABLE SELECTORS TO TRY:")
        print("  table")
        print("  table.results")
        print("  table[id*='result']")
        
        print("\n📋 COMMON NEXT BUTTON SELECTORS TO TRY:")
        print("  Text-based:")
        print("    a[title*='Next']")
        print("    button.next")
        print("    //a[contains(text(), 'Next')]")
        print("\n  ReferenceUSA div buttons:")
        print("    div[role='button'][aria-label*='next']")
        print("    div.next.button")
        print("    //div[@role='button' and contains(@aria-label, 'next')]")
        print("\n  Image/Arrow-based:")
        print("    a img[alt*='next']")
        print("    a img[src*='arrow']")
        print("    //a[.//img[contains(@src, 'arrow')]]")
        print("    //a[contains(text(), '→')]")
        print("    //a[contains(text(), '>')]")
        
        while True:
            print("\n" + "="*60)
            print("Enter a selector to test (or 'quit' to exit):")
            print("="*60)
            
            selector = input("\nSelector: ").strip()
            
            if selector.lower() in ['quit', 'exit', 'q', '']:
                break
            
            # Determine if XPath or CSS
            if selector.startswith('//') or selector.startswith('('):
                print(f"\n🔍 Testing XPath: {selector}")
                found = test_selector(driver, selector, 'XPath')
            else:
                print(f"\n🔍 Testing CSS: {selector}")
                found = test_selector(driver, selector, 'CSS')
            
            # Ask if user wants to try clicking (for buttons)
            if found:
                click = input("\n💡 Try clicking the first element? (y/n): ").strip().lower()
                if click == 'y':
                    try:
                        if selector.startswith('//'):
                            elem = driver.find_element(By.XPATH, selector)
                        else:
                            elem = driver.find_element(By.CSS_SELECTOR, selector)
                        
                        # Scroll into view
                        driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                        time.sleep(0.5)
                        
                        elem.click()
                        print("  ✓ Clicked successfully!")
                        time.sleep(2)
                    except Exception as e:
                        print(f"  ✗ Click failed: {e}")
        
        print("\n" + "="*60)
        print("✓ Testing complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Note down the selectors that worked")
        print("2. Run: python referenceusa_scraper.py")
        print("3. The scraper will try these selectors automatically")
        print("="*60)
        
    finally:
        print("\nClosing browser...")
        driver.quit()
        print("✓ Done!")


if __name__ == "__main__":
    main()
