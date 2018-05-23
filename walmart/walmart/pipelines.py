from walmart.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PWORD
import pymysql, csv
from scrapy import signals
from scrapy.exporters import CsvItemExporter


class MySQLPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.file = open('output2.csv', 'w+b')
        self.exporter = CsvItemExporter(self.file,  quoting=csv.QUOTE_ALL, lineterminator="\n")
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.file.close()
        conn = pymysql.connect(host=MYSQL_HOST,
                               db='scrapedb',
                               user=MYSQL_USER,
                               passwd=MYSQL_PWORD,
                               charset='utf8',
                               use_unicode=True,
                               local_infile=True)
        cursor = conn.cursor()
        for tableName in ['walmart_latest_crawl', 'walmart_products_unique', 'walmart_products']:
            cursor.execute("""LOAD DATA LOCAL INFILE 'output2.csv' INTO TABLE %s
                                FIELDS TERMINATED BY ','
                                ENCLOSED BY '"'
                                LINES TERMINATED BY '\n'
                                IGNORE 1 LINES
                                (category,product_url,description,rating,img_url,brand,upc,seller,num_ratings,
                                department,quantity,external_id,price,name);""" % tableName)
        conn.commit()
        conn.close()
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

