import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from czbankcn.items import Article


class czbankcnSpider(scrapy.Spider):
    name = 'czbankcn'
    start_urls = ['http://www.czbank.com/cn/pub_info/Outside_reports/',
                  'http://www.czbank.com/cn/pub_info/important_notice/']
    outside_page = 1
    notice_page = 1

    def parse(self, response):
        links = response.xpath('//div[@class="list_content"]//dd/a/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)

            if 'Outside_reports' in response.url:
                self.outside_page += 1
                next_page = f'http://www.czbank.com/cn/pub_info/Outside_reports/index_{self.outside_page - 1}.shtml?page={self.outside_page}'
                yield response.follow(next_page, self.parse)
            else:
                self.notice_page += 1
                next_page = f'http://www.czbank.com/cn/pub_info/important_notice/index_{self.notice_page - 1}.shtml?page={self.notice_page}'
                yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h5/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="date"]/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="TRS_Editor"]//text()').getall() or response.xpath('//div[@class="main"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
