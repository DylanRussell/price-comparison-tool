#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy, json, redis, re
from scrapy import Request
from walmart.items import WalmartItem
from walmart.settings import REDIS_PORT, REDIS_HOST, IS_PARENT
from urlparse import urlparse, parse_qs
from urllib import urlencode


class Walmart(scrapy.Spider):
    name = 'walmart.com'
    seed = base = 'https://www.walmart.com/browse?'  # base url for all requests. only the query string changes
    seed_depts_key = 'departments'  # key for shared redis queue
    conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    allowed_domains = ['walmart.com']
    domain = 'https://www.walmart.com'
    products_harvested = set()  # prevent duplicates
    sortHigh = "price_high"
    sortLow = "price_low"
    allSort = ['best_seller', 'rating_high', 'new', 'price_low', 'price_high']  # all sorting options
    itemsPerPage = 40
    numPages = 25  # can't go further than page 25
    targetSize = 1500  # ideal product grouping size
    maxSize = 2500  # maximum product grouping size
    # start_urls = ['https://www.walmart.com/browse?cat_id=4171_4191_133123']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        from_crawler = super(Walmart, cls).from_crawler
        spider = from_crawler(crawler, *args, **kwargs)
        # when spider idle, call this spider's idle function
        crawler.signals.connect(spider.idle, signal=scrapy.signals.spider_idle)
        return spider

    def start_requests(self):
        if IS_PARENT:
            yield Request(self.seed, self.parse)

    def idle(self):
        # safe to clear product IDs, spider finished crawling a department
        self.products_harvested.clear()
        self.logger.info('Spider idle, fetching a top level department from redis...')
        url = self.conn.rpop(self.seed_depts_key)
        if url:
            self.logger.info('Retrieved department url from redis: %s' % url)
            self.crawler.engine.crawl(Request(url, self.parse_category), self)

    def parse(self, response):
        """Get top level department urls, push them onto redis queue"""
        obj = response.text.partition('window.__WML_REDUX_INITIAL_STATE__ = ')[2].partition('};')[0] + '}'
            
        departments = obj['preso']['facets'][0]['values']
        numDepartments = len(departments)
        departments = [(d['itemCount'], d['url']) for d in departments]
        # sort ascending order so biggest departments are crawled first
        for itemCount, catId in sorted(departments):
            url = self.base + catId
            self.conn.rpush(self.seed_depts_key, url)
        self.logger.info('%s department links found from all departments page' % numDepartments)

    def generate_listing_requests(self, catId, oldFacet, numItems):
        """Generate the listing requests, sort in multiple ways if necessary"""
        params = {x: y for x, y in [('cat_id', catId), ('facet', oldFacet)] if y}
        if numItems < 1000:
            sort = [self.sortLow]
        elif numItems < 2000:
            sort = [self.sortLow, self.sortHigh]
        else:
            sort = self.allSort
        for page in range(1, 1 + min(self.numPages, numItems / 40)):
            params['page'] = page
            for s in sort:
                params['sort'] = s
                url = self.base + urlencode(params)
                yield Request(url, self.parse_listings)

    def parse_walmart_qs(self, url):
        # get the category id and facet from the query string
        parsed_url = urlparse(url)
        qs = parse_qs(parsed_url.query)
        return qs.get('cat_id', [''])[0], qs.get('facet', [''])[0].decode('utf-8', 'ignore')

    def parse_category(self, response):
        # load json object containing facets
        obj = response.text.partition('window.__WML_REDUX_INITIAL_STATE__ = ')[2].partition('};')[0] + '}'
        try:
            obj = json.loads(obj)
        except ValueError:
            self.logger.error('URL: %s did not have the json object' % response.url)
            raise StopIteration
        catId, oldFacet = self.parse_walmart_qs(response.url)
        numItems = obj['preso']['requestContext']['itemCount']['total']
        if numItems > self.maxSize:  # category too big, try to add a facet
            existing = set(re.findall(r'([a-z_A-Z]*):', oldFacet))
            for facet in obj['preso']['facets']:
                name = facet['type']
                # special case here - don't need to apply a facet yet,
                # can recurse into a more narrow category
                if name == 'cat_id':
                    for f in facet['values']:
                        url = self.base + f['url'].decode('utf-8', 'ignore')
                        yield Request(url, self.parse_category)
                    raise StopIteration
                total = sum(x.get('itemCount', 0) for x in facet['values'])
                # apply facet as long as it hasn't been applied already
                # and contains most of the category
                if numItems * .75 < total < numItems * 1.4 and name not in existing:
                    params = {'cat_id': catId}
                    filters = sorted([(x.get('itemCount', 0), x['name']) for x in facet['values']])
                    cur = 0
                    group = []
                    while filters:
                        count, facet = filters.pop()
                        group.append(facet)
                        cur += count
                        if cur > self.targetSize or not filters:
                            new = [name + ':' + x for x in group]
                            if oldFacet:
                                new.append(oldFacet)
                            params['facet'] = '||'.join(new).decode('utf-8', 'ignore')
                            url = self.base + urlencode(params)
                            yield Request(url, self.parse_category)
                            cur = 0
                            group = []
                    raise StopIteration
            self.logger.info('Unable to reduce number of items below %s for url: %s,' % (numItems, response.url))
        # all facets have already been applied,
        # or the category has been filtered to a small enough amount
        for req in self.generate_listing_requests(catId, oldFacet, numItems):
            yield req

    def parse_listings(self, response):
        """Parses all Items found in JSON object, filters out duplicates."""
        obj = response.text.partition('window.__WML_REDUX_INITIAL_STATE__ = ')[2].partition('};')[0] + '}'
        try:
            obj = json.loads(obj)
        except ValueError:
            self.logger.error('URL: %s did not have the json object' % response.url)
            raise StopIteration
        for item in obj['preso']['items']:
            prodId = item['productId']
            if prodId not in self.products_harvested:
                self.products_harvested.add(prodId)
                i = WalmartItem()
                i['img_url'] = item.get('imageUrl')
                i['external_id'] = item['productId']
                i['name'] = item['title']
                i['product_url'] = self.domain + item['productPageUrl']
                i['upc'] = item.get('upc')
                i['department'] = item.get('department')
                i['rating'] = float(item.get('customerRating', 0))
                i['num_ratings'] = int(item.get('numReviews', 0))
                i['seller'] = item.get('sellerName')
                offer = item['primaryOffer']
                if offer.get('showMinMaxPrice'):
                    try:
                        i['price'] = (float(offer['minPrice']) + float(offer['maxPrice'])) / 2.0
                    except KeyError:
                        i['price'] = None
                else:
                    i['price'] = float(offer.get('offerPrice', 0))
                i['description'] = item.get('description')
                i['category'] = item.get('seeAllName')
                i['brand'] = item['brand'][0] if item.get('brand') else None
                i['quantity'] = item.get('quantity')
                yield i
