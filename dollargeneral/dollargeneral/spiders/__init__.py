#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy, json, re
from dollargeneral.items import DGListing
from dollargeneral.loaders import DGLoader
from scrapy import Selector


class DGSpider(scrapy.Spider):
    name = 'dgspider'
    start_urls = ['http://www.dollargeneral.com']
    seen = set()

    def parse(self, response):
        """Follows all category links from DGs Homepage. Links are loaded from a json object
        loadMore... below is a Scrapy Contract mingled with this docstring..

        @url http://www.dollargeneral.com
        @returns requests 150 200
        """
        categories = json.loads(response.text.partition('var loadMore = ')[2].partition('};')[0] + '}')
        for c in categories:
            for text in categories[c]:
                for url in set(Selector(text=text).xpath('//a/@href').extract()):
                    if not re.search('sale', url, re.I):
                        yield scrapy.Request(response.urljoin(url), self.parse_category)
            
    def parse_category(self, response):
        """Parses a DG product category page."""
        productsPerPage = 24
        try:
            numProducts = int(response.xpath('//span[@class="toolbar-number"]/text()').extract_first())
            for page in range(1, numProducts/productsPerPage + 2):
                yield scrapy.Request(response.url + '?p=%s' % page, self.parse_category2)
        except TypeError:
            for url in response.xpath('//a[@class="view-all"]/@href').extract():
                yield scrapy.Request(url, self.parse_category)

    def parse_category2(self, response):
        products = json.loads(response.text.partition('var impressionData = ')[2].partition('}, payload')[0] + '}')
        for product in products['ecommerce']['impressions']:
            pId = product['id']
            if pId not in self.seen:
                self.seed.add(pId)
                loader = DGLoader(item=DGListing(), response=response)
                loader.add_value('category', product['category'])
                loader.add_value('external_item_id', product['id'])
                loader.add_value('description', product['name'])
                loader.add_value('price', product['price'])
                loader.add_value('brand', product['brand'])
                loader.add_xpath('img_url', '//a[@data-id="%s"]//img/@data-src' % product['id'])
                yield loader.load_item()
