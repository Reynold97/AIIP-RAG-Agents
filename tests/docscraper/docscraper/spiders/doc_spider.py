import scrapy
from urllib.parse import urljoin

class DocSpider(scrapy.Spider):
    name = "docspider"
    start_urls = ['https://docs.chainlit.io/']  # Replace with your actual starting URL

    visited_urls = set()  # Track visited URLs to avoid duplicates

    def parse(self, response):
        # Add current URL to visited set to avoid re-scraping it
        if response.url in self.visited_urls:
            return
        self.visited_urls.add(response.url)

        # Extract visible content, excluding scripts, styles, etc.
        page_content = response.xpath(
            "//body//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::head) and not(ancestor::noscript)]"
        ).getall()

        clean_content = ' '.join([text.strip() for text in page_content if text.strip()])

        # Yield the cleaned content with the URL
        if clean_content:
            yield {
                'url': response.url,
                'content': clean_content
            }

        # Follow all links on the page, filter duplicates and ignore fragments (like #section)
        for href in response.xpath("//a/@href").getall():
            full_url = urljoin(response.url, href)
            
            # Ignore fragments and ensure we don't revisit the same URL
            full_url = full_url.split('#')[0]
            if full_url not in self.visited_urls and full_url.startswith(self.start_urls[0]):
                yield scrapy.Request(full_url, callback=self.parse)


