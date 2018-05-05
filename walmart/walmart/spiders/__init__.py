#!/usr/bin/python
# -*- coding: utf-8 -*-
import scrapy, json, traceback, redis
from walmart.items import WalmartItem
from scrapy.shell import inspect_response
from walmart.settings import REDIS_PORT, REDIS_HOST, IS_PARENT
from urlparse import urlparse
from twisted.internet import reactor, defer


def sleep_for(secs):
	d = defer.Deferred()
	reactor.callLater(secs, d.callback, None)
	return d


class Walmart(scrapy.Spider):
	name = 'walmart.com'
	seed = 'https://www.walmart.com/all-departments'
	conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
	seenKey = 'products_seen'
	urlFrontierKey = 'url_frontier'
	categoriesSeen = 'categories_seen'
	allowed_domains = ['walmart.com']

	def start_requests(self):
		if IS_PARENT:
			yield scrapy.Request(self.seed, self.parse)
		sleep = .05
		while True:
			url = self.conn.rpop(self.urlFrontierKey)
			if url:
				sleep = .05
				yield scrapy.Request(url, self.parse_category)
			else:
				sleep *= 2
			if sleep >= 256:
				raise StopIteration 
			if sleep > .05:
				sleep_for(sleep)

	def parse(self, response):
		"""Follows all category links from Walmarts Homepage. Links are loaded from a json object
		"""
		obj = response.text.partition('window.__WML_REDUX_INITIAL_STATE__ = ')[2].partition('};')[0] + '}'
		obj = json.loads(obj)
		try:
			d1 = obj['header']['quimbyData']['global_header_ny']['headerZone1']['configs']['departments']
		except KeyError:
			d1 = obj['header']['quimbyData']['global_header']['headerZone3']['configs']['departments']
		# get all categories
		links = []
		for d2 in d1:
			for d3 in d2['departments']:
				links += [cat['category']['clickThrough']['value'] for cat in d3.get('categories', [])]
		seeds = 0
		for link in links:
			url = format_url(link).lower()
			if 'www.walmart.com' in url:
				seeds += 1
				self.conn.sadd(self.categoriesSeen, url)
				yield scrapy.Request(url, self.parse_category)
		self.logger.info('%s department links found from all departments page' % seeds)


	def parse_category(self, response):
		"""Parses a walmart category page."""
		# items = obj['topicData']['items']
		# nextPage = obj['topicData'].get('canonicalNext')
		# presoKeyError = True
		obj = response.text.partition('window.__WML_REDUX_INITIAL_STATE__ = ')[2].partition('};')[0] + '}'
		obj = json.loads(obj)		
		try:
			items = obj['preso']['items']
			nextPage = obj['preso']['pageMetadata'].get('canonicalNext')
		except KeyError:
			try:
				left = obj['presoData']['modules']['left']
				links = [y['url'] for x in left for y in x['data']]
				for link in links:
					link = format_url(link)
					if not self.conn.sismember(self.categoriesSeen, link):
						self.conn.sadd(self.categoriesSeen, link)
						self.conn.rpush(self.urlFrontierKey, link)
				raise StopIteration
			except KeyError:
				raise StopIteration
		new = 0
		for item in items:
			prodId = item['productId']
			if not self.conn.sismember(self.seenKey, prodId):
				self.conn.sadd(self.seenKey, prodId)
				new += 1
				i = WalmartItem()
				i['external_id'] = item['productId']
				i['name'] = item['title']
				i['img_url'] = item['imageUrl']
				i['product_url'] = format_url(item['productPageUrl'])
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
		if new > 10 and nextPage:
			yield scrapy.Request(format_url(nextPage), self.parse_category, meta={'pagination': True})
		if not response.meta.get('pagination') and new > 10:
			links = []
			for facet in obj['preso']['facets']:
				links += [(x.get('url'), x.get('itemCount')) for x in facet['values'] if x.get('url')]
			for link, numItems in links:
				if numItems > 25:
					link = format_url(response.url.partition('?')[0] + '?' + link)
					if len(link) < 1000 and not self.conn.sismember(self.categoriesSeen, link):
						self.conn.rpush(self.urlFrontierKey, link)





def format_url(url):
	# make sure URLs aren't relative, also fix invalid urls
	url = url.replace('https//www.walmart.com', '').replace('http//www.walmart.com', '')
	u = urlparse(url)

	scheme = u.scheme or "https"
	host = u.netloc or "www.walmart.com"
	path = u.path
	query = u.query
	return "{scheme}://{host}{path}?{query}".format(**locals())