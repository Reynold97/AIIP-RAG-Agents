import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Starting point for the documentation
base_url = "https://docs.chainlit.io/get-started/overview"
visited_urls = set()

# This list will store all the scraped content
scraped_content = []

# Function to scrape a page
def scrape_page(url):
    if url in visited_urls:
        return

    visited_urls.add(url)
    
    # Send an HTTP GET request to fetch the page content
    response = requests.get(url)
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "lxml")
    
    # Extract the main content from the page
    # Assuming documentation content is in <div class="main-content">
    main_content = soup.find("div", class_="main-content")
    
    if main_content:
        scraped_content.append(main_content.get_text(separator="\n", strip=True))
    
    # Find all links on the page and scrape them recursively if internal
    for link in soup.find_all("a", href=True):
        subpage_url = urljoin(base_url, link['href'])
        # Make sure the link belongs to the same documentation section
        if subpage_url.startswith(base_url):
            scrape_page(subpage_url)

# Start scraping from the base documentation page
scrape_page(base_url)

# Store everything into a single document
with open("documentation.txt", "w", encoding="utf-8") as f:
    for content in scraped_content:
        f.write(content + "\n\n")
