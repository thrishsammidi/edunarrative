import scrapy

class InewsSpider(scrapy.Spider):
    name = "inews"
    allowed_domains = ["indianexpress.com"]

    def start_requests(self):

        for page in range(250, 301):

            if page == 1:
                url = "https://indianexpress.com/section/education/"
            else:
                url = f"https://indianexpress.com/section/education/page/{page}/"

            yield scrapy.Request(
                url=url,
                callback=self.parse
            )

    def parse(self, response):

        for hl in response.xpath("//div[@class='nation']//div[contains(@class,'articles')]"):

            hl_title = hl.xpath(".//a/@title").get()

            article_url = hl.xpath(".//a/@href").get()

            if article_url:
                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article,
                    meta={
                        "hl_title": hl_title,
                        "article_url": article_url
                    }
                )

    def parse_article(self, response):

        yield {
            'hl_title': response.meta.get('hl_title'),
            'article_url': response.meta.get('article_url'),
            'published_date': response.xpath("//span[contains(@class,'date_update')]/@content").get(),
            'content': ' '.join(
                response.xpath(
                    "//div[contains(@class,'full-details')]//p//text()"
                ).getall()
            ),
            'country': 'india',
            'source': 'indianexpress'
        }
