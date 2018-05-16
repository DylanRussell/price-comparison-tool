from twisted.enterprise import adbapi


class MySQLPipeline(object):
    """A pipeline to store the item in a MySQL database.
    This implementation uses Twisted's asynchronous database API.
    """

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbargs = dict(
            host=settings['MYSQL_HOST'],
            db='scrapedb',
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PWORD'],
            charset='utf8',
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbargs)
        return cls(dbpool)

    def process_item(self, item, spider):
        # run db query in the thread pool
        d = self.dbpool.runInteraction(self.insert_item, item, spider)
        d.addErrback(self._handle_error, item, spider)
        # at the end return the item in case of success or failure
        d.addBoth(lambda _: item)
        # return the deferred instead the item. This makes the engine to
        # process next item (according to CONCURRENT_ITEMS setting) after this
        # operation (deferred) has finished.
        return d

    def _handle_error(self, failure, item, spider):
        """Handle occurred on db interaction."""
        # do nothing, just log
        spider.logger.error(failure)

    def insert_item(self, conn, item, spider):
        keys = ['price', 'external_item_id', 'img_url', 'subcategory', 'category', 'brand']
        vals = [item.get(k) for k in keys]
        conn.execute("""INSERT INTO dollargeneral_products 
                        (price, external_id, img_url, department, category, brand) 
                        VALUES (%s, %s, %s, %s, %s, %s)""", vals)
