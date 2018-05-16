# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DGListing(scrapy.Item):
    description = scrapy.Field()
    price = scrapy.Field()
    sku = scrapy.Field()
    external_item_id = scrapy.Field()
    img_url = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    brand = scrapy.Field()
    amount_off = scrapy.Field()
    linkedPromotion = scrapy.Field()
    image = scrapy.Field()
