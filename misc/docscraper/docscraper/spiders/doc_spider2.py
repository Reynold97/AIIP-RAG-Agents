import scrapy
from urllib.parse import urljoin

class DocSpider(scrapy.Spider):
    name = "docspider2"
    start_urls = ['https://docs.chainlit.io/']  # Replace with your actual starting URL

    visited_urls = set()  # Track visited URLs to avoid duplicates

    def parse(self, response):
        self.visited_urls.add(response.url)

        # Extract main content (excluding scripts, styles, etc.)
        page_content = response.xpath(
            "//body//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::head) and not(ancestor::noscript)]"
        ).getall()

        # Extract <pre> and <code> blocks (specifically for code examples)
        code_blocks = response.xpath("//pre//text() | //code//text()").getall()

        # Clean up the regular text content
        clean_content = ' '.join([text.strip() for text in page_content if text.strip()])
        
        # Clean up and format the code blocks correctly
        clean_code = '\n'.join([code.strip() for code in code_blocks if code.strip()])

        # Combine text content with code examples
        combined_content = f"{clean_content}\n\nCode Examples:\n{clean_code}"

        if combined_content.strip():
            yield {
                'url': response.url,
                'content': combined_content
            }

        # Follow all links on the page, ignore fragments, and avoid revisiting URLs
        for href in response.xpath("//a/@href").getall():
            full_url = urljoin(response.url, href)
            
            # Ignore fragments and ensure we don't revisit the same URL
            full_url = full_url.split('#')[0]
            if full_url not in self.visited_urls and full_url.startswith(self.start_urls[0]):
                yield scrapy.Request(full_url, callback=self.parse)
