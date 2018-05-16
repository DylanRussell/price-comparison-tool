#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy, json
from urllib import urlencode
from scrapy import Request
from target.items import TargetItem
from urlparse import urlparse, parse_qs


class TargetSpider(scrapy.Spider):
    name = 'target.com'
    search_url = 'https://redsky.target.com/v1/plp/search?'
    find_cats_url = 'https://redoak.target.com/content-publish/pages/v1?'
    upcs = set()
    dupes = 0
    sortHigh = "PriceHigh"
    sortLow = "PriceLow"
    allSorts = ['Featured', 'PriceLow', 'PriceHigh', 'RatingHigh', 'bestselling', 'newest']
    start_urls = ['https://www.target.com']
    itemsPerPage = 96  # anything > 96 throws an error
    numPages = 13  # can only go 13 pages deep
    targetSize = 2000
    maxSize = 3000
    # groupings with inaccurate or insufficient counts, or no distribution
    ignore = ['deals', 'shipping & pickup', 'FPO/APO', 'Category']

    def parse(self, response):
        """extract top level categories from the homepage"""
        params = {'channel': 'web', 'children': True}
        urls = response.xpath('//a[@aria-hidden="true"]/@href').extract()
        for url in urls:
            departmentId = url.partition('-/N-')[2].split('?')[0].strip()
            if departmentId:
                params['url'] = url
                yield Request(self.find_cats_url + urlencode(params), callback=self.get_seed_categories)

    def get_seed_categories(self, response):
        """get children of top level categories"""
        try:
            categories = json.loads(response.body_as_unicode())['metadata']['children']
        except KeyError:
            self.logger.info('url %s did not have the JSON object' % response.url)
            raise StopIteration
        for child in categories:
            nodeId = child['node_id']
            params = (nodeId, child['canonical_url'], child['seo_h1'])
            self.logger.info('Node ID: %s, URL: %s, Name: %s' % params)
            url = self.search_url + urlencode({'category': nodeId, 'channel': 'web'})
            yield Request(url, callback=self.expand_category)

    def parse_target_qs(self, url):
        # get the category id and facet from the query string
        parsed_url = urlparse(url)
        qs = parse_qs(parsed_url.query)
        return qs.get('category', [''])[0], qs.get('faceted_value', [''])[0]

    def generate_listing_requests(self, catId, oldFacet, numItems):
        params = {'count': self.itemsPerPage, 'category': catId}
        if oldFacet:
            params['faceted_value'] = oldFacet
        if numItems > self.maxSize:
            sort = self.allSorts
        elif numItems < 1500:
            sort = [self.sortLow]
        else:
            sort = [self.sortLow, self.sortHigh]
        for s in sort:
            params['sort_by'] = s
            for page in xrange(min(self.numPages, numItems / self.itemsPerPage)):
                params['offset'] = page * self.itemsPerPage
                yield Request(self.search_url + urlencode(params), self.parse_listings)

    def expand_category(self, response):
        """if necessary further reduce category size by recursively adding
        facets, otherwise make the call to get_listings"""
        category, facet_list = self.parse_target_qs(response.url)
        obj = json.loads(response.body_as_unicode())['search_response']
        total = int(obj['metaData'][1]['value'])
        if total > self.maxSize:
            existing = response.meta.get('existing', [])
            for facets in obj['facet_list']:
                name = facets['displayName']
                subset = sum(x.get('count', 0) for x in facets['details'])
                if name in self.ignore + existing or not total * .75 < subset < total * 1.25:
                    continue
                # use first filter that meets critieria
                filters = sorted([(x['count'], x['facetId']) for x in facets['details'] if x.get('facetId')])
                cur = 0
                params = {'category': category}
                group = [facet_list]
                while filters:
                    count, facet = filters.pop()
                    group.append(facet)
                    cur += count
                    if cur > self.targetSize or not filters:
                        params['faceted_value'] = 'Z'.join([x for x in group if x])
                        # store used facets in the meta dict for recursive call
                        yield Request(self.search_url + urlencode(params), self.expand_category,
                                      meta={'existing': existing + [name]})
                        cur = 0
                        group = [facet_list]
                raise StopIteration
            self.logger.info("Unable to reduce url: %s below %s items" % (response.url, total))
        # all filters have already been applied,
        # or the category has been filtered to a small enough amount
        for req in self.generate_listing_requests(category, facet_list, total):
            yield req

    def parse_listings(self, response):
        try:
            items = json.loads(response.body_as_unicode())['search_response']['items']['Item']
        except ValueError:
            # make the same request and the json object usually appears
            yield Request(response.url, dont_filter=True, callback=self.parse_listings)
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
                item['brand'] = listing.get('brand')
                item['avail'] = listing.get('availability_status')
                item['category'] = listing['merch_class']
                item['in_store'] = listing.get('pick_up_in_store', False)
                item['description'] = listing.get('title')
                item['url'] = 'www.target.com' + listing['url']
                item['rating'] = listing.get('average_rating')
                item['num_ratings'] = listing.get('total_reviews', 0)
                item['name'] = listing.get('title')
                item['img_url'] = listing['images'][0]['base_url'] + listing['images'][0]['primary']
                item['upc'] = listing.get('upc')
                yield item
            elif listing['tcin'] in self.upcs:
                self.dupes += 1
                if not self.dupes % 10000:
                    self.logger.info('%s dupes seen so far' % self.dupes)
