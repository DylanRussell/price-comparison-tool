from target.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PWORD
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
        self.file = open('output.csv', 'w+b')
        self.exporter = CsvItemExporter(self.file, quoting=csv.QUOTE_ALL, lineterminator="\n")
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
        for tableName in ['target_products', 'target_products_unique']:
            cursor.execute("""LOAD DATA LOCAL INFILE 'output.csv' INTO TABLE %s
                            FIELDS TERMINATED BY ','
                            OPTIONALLY ENCLOSED BY '"'
                            LINES TERMINATED BY '\n'
                            IGNORE 1 LINES
                            (category,num_ratings,description,rating,url,img_url,brand,upc,available,
                            available_in_store,external_id,price,name);""" % tableName)
        conn.commit()
        conn.close()
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
