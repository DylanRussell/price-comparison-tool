# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy, redis, time
from amazon_crawler.items import ProductItem
from amazon_crawler.settings import REDIS_PORT, REDIS_HOST, IS_PARENT
from scrapy.shell import inspect_response
from urllib import urlencode
from urlparse import urlparse, urlunparse, parse_qs
from twisted.internet import reactor, defer




def sleep_for(secs):
  d = defer.Deferred()
  reactor.callLater(secs, d.callback, None)
  return d


class AmazonSpider(scrapy.Spider):
    name = 'amazon.com'
    domain = 'https://www.amazon.com'
    conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    seenKey = 'products_seen'
    urlFrontierKey = 'url_frontier'
    seeds = [
        'https://www.amazon.com/Televisions-Video/b/ref=sd_allcat_tv?ie=UTF8&node=1266092011',
        'https://www.amazon.com/Home-Audio-Electronics/b/ref=sd_allcat_hat?ie=UTF8&node=667846011',
        'https://www.amazon.com/Camera-Photo-Film-Canon-Sony/b/ref=sd_allcat_p?ie=UTF8&node=502394',
        'https://www.amazon.com/cell-phones-service-plans-accessories/b/ref=sd_allcat_wi?ie=UTF8&node=2335752011',
        'https://www.amazon.com/Headphones-Accessories-Supplies/b/ref=sd_allcat_headphones?ie=UTF8&node=172541'
    ]

    def start_requests( self ):
        for seed in self.seeds:
            if IS_PARENT:
                yield scrapy.Request(seed, self.parse)
        sleep = .5
        while True:
            url = self.conn.spop(self.urlFrontierKey)
            if url:
                sleep = .5
                yield scrapy.Request(url, self.parse_subcat)
            else:
                sleep *= 2
            if sleep >= 256:
                raise StopIteration 
            sleep_for(sleep)

    def parse(self, response):
        # possible xpath: '//div[@id="leftNav"]/ul[1]/ul//a/@href'
        s1 = set(response.xpath('//div[@id="leftNav"]//a/@href').extract())
        s2 = set(response.xpath('//div[@class="a-section acs_dNav__carousels-container"]//a/@href').extract())
        s3 = set(response.xpath('//span[@class="category-link__text"]/../@href').extract())
        subcategories = s1 | s2 | s3
        for subcat in subcategories:
            url = format_url(self.domain + subcat)
            self.conn.sadd(self.urlFrontierKey, url)
            if subcat in s3:
                yield scrapy.Request(url, callback=self.parse)
        self.logger.info("category link {} yielded {} sub categories".format(response.url, len(subcategories)))

    def parse_subcat(self, response):
        for div in response.xpath('//div[@class="s-item-container"]'):
            if not div.xpath('./*') or not div.xpath('.//img/@src').extract_first():
                continue
            productId = div.xpath('./../@data-asin').extract_first()
            if not productId or self.conn.sismember(self.seenKey, productId):
                continue
            self.conn.sadd(self.seenKey, productId)
            item = ProductItem()
            item['product_id'] = productId
            item['img'] = div.xpath('.//img/@src').extract_first()
            item['name'] = div.xpath('.//h2/text()').extract_first()
            try:
                dollars = int(div.xpath('.//span[@class="sx-price-whole"]/text()').extract_first().replace(',', ''))
                cents = float(div.xpath('.//sup[@class="sx-price-fractional"]/text()').extract_first()) / 100
                item['price'] = str(dollars + cents)
            except (TypeError, AttributeError) as e:
                item['price'] = div.xpath('.//span[@class="a-size-base a-color-base"]/text()').extract_first()
            rating = div.xpath('.//i[contains(@class, "a-icon-star")]/span/text()').extract_first()
            item['rating'] = rating.split()[0] if rating else '0'
            numRatings = div.xpath('.//a[@class="a-size-small a-link-normal a-text-normal"]/text()').extract_first()
            item['num_ratings'] = '0' if not numRatings else numRatings.replace(',', '')
            item['listing_url'] = div.xpath('.//a[contains(@class, "s-access-detail-page")]/@href').extract_first()
            item['page_url'] = response.url
            yield item
        next_link = response.xpath('//a[@id="pagnNextLink"]/@href').extract_first()
        if next_link:
            next_link = format_url(self.domain + next_link)
            self.conn.sadd(self.urlFrontierKey, next_link)


def format_url(url):
    allowed_params = {"node", "rh", "page"}
    u = urlparse(url)
    query = parse_qs(u.query)
    query = {k:v for k, v in query.items() if k in allowed_params}
    u = u._replace(query=urlencode(query, True))
    return urlunparse(u)