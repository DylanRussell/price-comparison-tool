# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TargetItem(scrapy.Item):
    price = scrapy.Field()
    brand = scrapy.Field()
    avail = scrapy.Field()
    category = scrapy.Field()
    in_store = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    rating = scrapy.Field()
    num_ratings = scrapy.Field()
    name = scrapy.Field()
    img_url = scrapy.Field()
    external_id = scrapy.Field()
