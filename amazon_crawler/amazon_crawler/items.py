# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    img = scrapy.Field()
    product_url = scrapy.Field()
    page_url = scrapy.Field()
    listing_url = scrapy.Field()
    rating = scrapy.Field()
    num_ratings = scrapy.Field()
    product_id = scrapy.Field()
