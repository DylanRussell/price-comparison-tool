# walmart.com web crawler

Scrapy web crawler for walmart.com. Logic for following links, extracting listings is in spiders/__init__.py file. A listing is represented by a ProductItem object, defined in items.py. Listings, once extracted, are processed by the MySQLPipeline class defined in pipelines.py. Crawl speed, database connection settings, pipeline settings are all defined in settings.py.