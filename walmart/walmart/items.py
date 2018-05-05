# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WalmartItem(scrapy.Item):
    external_id = scrapy.Field()
    name = scrapy.Field()
    img_url = scrapy.Field()
    product_url = scrapy.Field()
    upc = scrapy.Field()
    department = scrapy.Field()
    rating = scrapy.Field()
    num_ratings = scrapy.Field()
    seller = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    category = scrapy.Field()
    brand = scrapy.Field()
    quantity = scrapy.Field()
