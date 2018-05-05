# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy, json, logging, random
from urllib import urlencode
from scrapy.shell import inspect_response
from scrapy import Request
from target.items import TargetItem


numListings = 95 #anything > 95 throws an error
# top level categories
categories = ['0htu7', '5xtd3', '55b0t', '5xtbp', '5xtly', '5xtvd', 'hz89j', '5xtnr', '5xtq9', '5xtg6', '5xsxe', '5xtg5', '5xtb0', '5xt85', '5xtz1', '5xsxr', '55r1x', '5xtzq', '5xu1n', '5xt1a', '5xsz1', '5xt44', '5xt3c', '5q0ga', '4xw74', '5o5g7', '5xsxu', '4ydi5']

class TargetSpider(scrapy.Spider):
    name = 'target.com'
    search_url = 'https://redsky.target.com/v1/plp/search?'
    upcs = set()
    visited = set()
    dupes = 0
    sort_by = ["Featured", "price-high to low", "price-low to high", "average ratings", "best seller", "newest"]

    def start_requests(self):
        params = {'count': numListings, 'channel': 'web', 'pageId': '/c/', 'offset': '0'}
        for cat in categories:
            self.visited.add(cat)
            params['category'] = cat
            yield Request(self.search_url + urlencode(params), callback = self.parse_category2, meta = {'category' : cat})


    def parse_category2(self, response):
        items = json.loads(response.body_as_unicode())
        if not items.get('search_response'):
            raise StopIteration
        cat = response.meta['category']
        params = {'count': numListings, 'category': cat, 'channel': 'web', 'pageId': '/c/'}
        params['sort_by'] = random.choice(self.sort_by)
        totalListings = int(items['search_response']['metaData'][1]['value'])
        totalPages = int(items['search_response']['metaData'][4]['value'])
        for offset in range(totalPages):
            params['offset'] = numListings * offset
            yield Request(self.search_url + urlencode(params), callback = self.parse_listing, dont_filter=True)
        if numListings * totalPages < totalListings:
            params['offset'] = 0
            subcat = set()
            for x in items['search_response'].get('facet_list', []):
                for y in x['details']:
                    if 'url' in y:
                        subcat.add(y['url'].split('-/N-')[1])
            for newcat in subcat - self.visited:
                params['category'] = newcat
                self.visited.add(newcat)
                yield Request(self.search_url + urlencode(params), callback = self.parse_category2, meta = {'category' : cat})


    def parse_listing(self, response):
        try:
            items = json.loads(response.body_as_unicode())['search_response']['items']['Item']
        except ValueError:
            yield Request(response.url, dont_filter=True, callback=self.parse_listing)
            raise StopIteration
        for listing in items:
            if listing['tcin'] not in self.upcs and not listing.get('error_message'):
                self.upcs.add(listing['tcin'])
                item = TargetItem()
                if listing['offer_price'].get('formatted_price'):
                    price = listing['offer_price']['formatted_price'].replace('$', '').replace(',', '')
                    if '-' in price:
                        p1, p2 = price.split('-')[0].strip(), price.split('-')[1].strip()
                        price = (float(p1) + float(p2)) / 2.0
                    else:
                        try:
                            price = float(price.strip())
                        except ValueError:
                            price = None
                    item['price'] = price
                else:
                    item['price'] = listing['offer_price'].get('min_price', 0)
                item['external_id'] = listing['tcin']
                item['brand'] = listing.get('brand', None)
                item['avail'] = listing.get('availability_status', None)
                item['category'] = listing['merch_class']
                item['in_store'] = listing.get('pick_up_in_store', False)
                item['description'] = listing.get('title', None)
                item['url'] = 'www.target.com' + listing['url']
                item['rating'] = listing.get('average_rating', None)
                item['num_ratings'] = listing.get('total_reviews', 0)
                item['name'] = listing.get('title', None)
                item['img_url'] = listing['images'][0]['base_url'] + listing['images'][0]['primary']
                yield item
            elif listing['tcin'] in self.upcs:
                self.dupes += 1
                if not self.dupes % 10000:
                    self.logger.info('%s dupes seen so far' % self.dupes)
