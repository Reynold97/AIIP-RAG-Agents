import scrapy
from urllib.parse import urljoin

class SeleniumDocSpider(scrapy.Spider):
    name = "selenium_spider2"
    start_urls = ['https://docs.chainlit.io/']

    visited_urls = set()  # Track visited URLs to avoid duplicates

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'docscraper.middlewares.SeleniumMiddleware': 543,  # Correct reference to your middleware
        }
    }

    def parse(self, response):
        self.visited_urls.add(response.url)

        # Extract the header section using your provided XPath
        header = response.xpath('/html/body/div[1]/main/div/div[2]/div[2]/div/div[1]/header//text()').getall()
        header_content = ' '.join([text.strip() for text in header if text.strip()])

        # Extract the body section using your provided XPath
        body = response.xpath('/html/body/div[1]/main/div/div[2]/div[2]/div/div[1]/div[2]//text()').getall()
        body_content = ' '.join([text.strip() for text in body if text.strip()])

        # Combine the header and body content
        combined_content = f"Header:\n{header_content}\n\nBody:\n{body_content}"

        if combined_content.strip():
            yield {
                'url': response.url,
                'content': combined_content
            }

        # Follow links on the page, ensuring we don't revisit the same URL
        for href in response.xpath("//a/@href").getall():
            full_url = urljoin(response.url, href)
            full_url = full_url.split('#')[0]  # Ignore fragment identifiers
            if full_url not in self.visited_urls and full_url.startswith(self.start_urls[0]):
                yield scrapy.Request(full_url, callback=self.parse)
