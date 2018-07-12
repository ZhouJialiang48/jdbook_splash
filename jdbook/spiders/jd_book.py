# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
from ..items import BookItem

lua_script = """
function main(splash)
    splash:go(splash.args.url)
    splash:wait(2)
    splash:runjs("document.getElementsByClassName('page')[0].scrollIntoView(true)")
    splash:wait(2)
    return splash:html()
end
"""

class JdBookSpider(scrapy.Spider):
    name = 'jd_book'
    allowed_domains = ['search.jd.com']
    page_url = 'https://search.jd.com/Search?keyword={keyword}&page={page}'
    keyword = 'python'
    page_total = 100

    def start_requests(self):
        for page in range(1, self.page_total*2+1, 2):
            url = self.page_url.format(keyword=self.keyword, page=page)
            yield SplashRequest(url=url,
                                endpoint='execute',
                                args={'lua_source': lua_script},
                                cache_args=['lua_source'],
                                callback=self.parse)

    def parse(self, response):
        items = response.css('.gl-warp .gl-item')
        print(len(items))
        if items:
            for item in items:
                book = BookItem()
                book['data_sku'] = item.xpath('./@data-sku').extract_first()
                book['name'] = item.css('.p-name').xpath('string(.//em)').extract_first()
                book['price'] = item.css('.p-price').xpath('string(.//strong)').extract_first()
                book['author'] = item.css('.p-bookdetails').xpath('string(.//span[@class="p-bi-name"])').extract_first()
                book['publishing_house'] = item.css('.p-bookdetails').xpath('string(.//span[@class="p-bi-store"])').extract_first()
                book['date'] = item.css('.p-bookdetails').xpath('string(.//span[@class="p-bi-date"])').extract_first()
                book['comments_count'] = item.css('.p-commit').xpath('string(.//strong)').extract_first()
                yield book

