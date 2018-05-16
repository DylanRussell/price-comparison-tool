# -*- coding: utf-8 -*-

from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose
from HTMLParser import HTMLParser
import re, string, datetime


def replace_tm_and_r(x):
    return re.sub(r'[™®]', '', x)


class DGLoader(ItemLoader):
    default_output_processor = TakeFirst()

    linkedPromotion_in = MapCompose(unicode.strip, lambda x: None if u'shipping' in x.lower() else x)
    description_in = MapCompose(HTMLParser().unescape, replace_tm_and_r)
    brand_in = MapCompose(replace_tm_and_r)
    amount_off_in = MapCompose(str)
    sku_in = MapCompose(lambda x: re.search(r'\d{5,10}', x).group(0))
