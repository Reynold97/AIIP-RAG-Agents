import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome WebDriver with headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
#chrome_service = Service('path_to_chromedriver')  # Update this path

driver = webdriver.Chrome(options=chrome_options)

visited_urls = set()  # To track visited URLs

def wait_for_page_to_load(timeout=10):
    """Wait for the page to load completely by checking for the presence of body."""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
    except TimeoutException:
        print("Timeout waiting for page to load")

def scrape_page(url):
    """Scrape a single page and return the structured data."""
    if url in visited_urls:
        return None

    visited_urls.add(url)
    driver.get(url)
    wait_for_page_to_load()  # Ensure the page loads completely
    time.sleep(2)  # Wait for JavaScript-rendered elements to load

    page_data = {"url": url, "content": []}

    try:
        # Extract all visible text elements and code snippets
        text_elements = driver.find_elements(By.XPATH, "//p | //h1 | //h2 | //h3 | //h4 | //h5 | //h6 | //span")
        code_elements = driver.find_elements(By.XPATH, "//pre | //code")

        # Add text content with retry logic
        for element in text_elements:
            try:
                text = element.text.strip()
                if text:
                    page_data['content'].append({"tag": element.tag_name, "text": text})
            except StaleElementReferenceException:
                print("Stale element encountered, retrying...")
                driver.refresh()
                wait_for_page_to_load()
                # Retry locating the element
                new_element = driver.find_element(By.XPATH, f"//{element.tag_name}")
                if new_element:
                    text = new_element.text.strip()
                    if text:
                        page_data['content'].append({"tag": new_element.tag_name, "text": text})

        # Add code snippets with retry logic
        for element in code_elements:
            try:
                code = element.text.strip()
                if code:
                    page_data['content'].append({"tag": element.tag_name, "code": code})
            except StaleElementReferenceException:
                print("Stale element encountered, retrying for code...")
                driver.refresh()
                wait_for_page_to_load()
                # Retry locating the element
                new_element = driver.find_element(By.XPATH, f"//{element.tag_name}")
                if new_element:
                    code = new_element.text.strip()
                    if code:
                        page_data['content'].append({"tag": new_element.tag_name, "code": code})

    except NoSuchElementException:
        pass

    return page_data

def get_internal_links():
    """Get all internal links from the current page."""
    links = []
    try:
        link_elements = driver.find_elements(By.TAG_NAME, "a")
        for element in link_elements:
            href = element.get_attribute("href")
            # Ensure the link is internal and not visited
            if href and href.startswith("http") and "chainlit.io" in href and href not in visited_urls:
                links.append(href)
    except NoSuchElementException:
        pass
    return links

def scrape_site(url, depth=5):
    """Recursively scrape the site starting from a given URL."""
    all_data = []
    pages_to_scrape = [url]
    
    while pages_to_scrape and depth > 0:
        current_url = pages_to_scrape.pop(0)
        page_data = scrape_page(current_url)
        if page_data:
            all_data.append(page_data)
            subpage_links = get_internal_links()
            for link in subpage_links:
                if link not in visited_urls:  # Avoid revisiting URLs
                    pages_to_scrape.append(link)
        depth -= 1  # Limit recursion depth to avoid infinite loops

    return all_data

# Starting URL to scrape
start_url = "https://docs.chainlit.io/"  # Update this to the target page
scraped_data = scrape_site(start_url)

# Save the scraped data to a JSON file
output_file = "tests/scraped_data.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(scraped_data, f, ensure_ascii=False, indent=4)

print(f"Scraped data saved to {output_file}")

# Close the browser
driver.quit()
