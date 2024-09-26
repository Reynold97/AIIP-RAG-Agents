import scrapy
from urllib.parse import urljoin

class SeleniumDocSpider(scrapy.Spider):
    name = "selenium_spider"
    start_urls = ['https://docs.chainlit.io/']

    visited_urls = set()  # Track visited URLs to avoid duplicates

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'docscraper.middlewares.SeleniumMiddleware': 543,  # Correct reference to your middleware
        }
    }

    def parse(self, response):
        self.visited_urls.add(response.url)

        # Extract content as in your previous spider
        page_content = response.xpath(
            "//body//text()[not(ancestor::script) and not(ancestor::style) and not(ancestor::head) and not(ancestor::noscript)]"
        ).getall()

        code_blocks = response.xpath("//pre//text() | //code//text()").getall()

        clean_content = ' '.join([text.strip() for text in page_content if text.strip()])
        clean_code = '\n'.join([code.strip() for code in code_blocks if code.strip()])

        combined_content = f"{clean_content}\n\nCode Examples:\n{clean_code}"

        if combined_content.strip():
            yield {
                'url': response.url,
                'content': combined_content
            }

        for href in response.xpath("//a/@href").getall():
            full_url = urljoin(response.url, href)
            full_url = full_url.split('#')[0]
            if full_url not in self.visited_urls and full_url.startswith(self.start_urls[0]):
                yield scrapy.Request(full_url, callback=self.parse)
