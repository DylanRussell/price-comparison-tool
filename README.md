# price-comparison-tool

Summary

For my insight project I built a web crawler using the Python web scraping framework Scrapy to scrape product listings from Dollar General, Walmart, Target, and Amazon. I stored the listings in a MySQL database, and used redis to scale the crawl across nodes. A small web app to display histograms and compare products across retailers was built with Flask.

URL: www.spideycents.com

Set Up

The code was tested and run on Python v2.7.

Required Libraries for running the Web Crawler:

scrapy==1.5.0
redis==2.10.6
pymysql==0.8.0

pymysql only necessary if storing product listings in a MySQL db. Table definitions can be found in the tables.sql file.
redis only necessary if crawling from multiple nodes. 
Crawlers can be run without these libraries by commenting out a few lines in the spider code and in the settings.py files.

The remaining required libraries are included in most Python distributions (i.e. json, re, urllib, urlparse).

Required Libraries for running the Web App:

Flask==1.0.2
Flask-Bootstrap==3.3.7.1
matplotlib==2.2.2
mpld3==0.3
MySQL-python==1.2.5
numpy==1.14.3


Crawling Strategy:

My high level goal was to maximize the number of listings retrieved while minimizing the number of requests made. 

Most e-commerce websites are structured in a similar way. A user can navigate the product code tree and apply filters (by price, shipping terms etc.). There is usually a cap on the number of items per page, and the number of pages and an option to sort by price low to high, and high to low.

So if a category contains a million products, I need to reduce that into chunks of size: Items per Page * Number of Pages * 2.

To reach this chunk size, I have a recursive function which:

1. Navigates to the bottom level of the product code tree
2. Then applies one filter at a time, keeping track of which filters have already been applied

The recursion ends once I reach the target chunk size or I have reached the bottom of the product tree and exhausted all filters.


Usage of Redis:

The Dollar General / Target crawls did not require Redis, as they were realtively small.

My first attempt at using Redis can be seen in the Amazon web crawler. One node marked as the 'parent' node discovers the top level sub category URLs
and pushes them onto a redis LIFO queue. Each node (including the parent node) then continuously pops links from this queue, and pushes newly discovered links onto it until the queue is empty and the crawl has ended. Product IDs are checked against a LRU cache in Redis and added if they haven't been seen before.

This approach resulted in a lot of time spent pushing to / popping from the queue. My second approach starts the same way, with a parent node pushing the top level categories onto a Redis LIFO queue. This time though, a crawler only pops a link off the queue when it reaches an idle state. It then crawls that category to completion before becoming idle again. By only following links that go deeper into the category I avoid colliding with the other crawls. Seen Product IDs can now be stored in a set internally and don't need to be shared across nodes. Top level categories are placed on the queue in order of increasing category size, so that the largest categories are popped off the queue first.

An example of my second approach can be seen in the Walmart crawler.


