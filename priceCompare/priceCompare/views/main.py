from __future__ import absolute_import
from priceCompare import app, mysql
from flask import render_template, request, jsonify
from collections import defaultdict
import json, mpld3, matplotlib, numpy
from threading import Lock


matplotlib.use('agg', warn=False, force=True)
import matplotlib.pyplot as plt
retailers_to_table = {'Dollar General': 'dollargeneral_products',
                      'Target': 'target_products_unique',
                      'Walmart': 'walmart_products_unique'}
lock = Lock()
plt.ioff()
matplotlib.rcParams.update({
  "lines.linewidth": 2.0,
  "axes.edgecolor": "#bcbcbc",
  "patch.linewidth": 0.5,
  "legend.fancybox": True,
  "axes.facecolor": "#eeeeee",
  "axes.labelsize": "x-large",
  "axes.grid": True,
  "grid.color":"white",
  "grid.linestyle":"solid",
  "patch.edgecolor": "#eeeeee",
  "axes.titlesize": "x-large",
})


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html', retailers=retailers_to_table.keys())


def get_categories_from_retailer(retailer):
    q = """SELECT category FROM categories WHERE
        retailer=%s ORDER BY num_items DESC"""
    if retailer == 'Walmart':
        q += " LIMIT 100, 200"
    cursor = mysql.connection.cursor()
    cursor.execute(q, (retailer,))
    return ['Select A Category'] + sorted([x[0] for x in cursor.fetchall()])


def get_prices(retailer, category):
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT price FROM %s WHERE category="%s"
                    AND PRICE IS NOT NULL AND price > 0""" % (retailers_to_table[retailer], category))
    prices = [float(x[0]) for x in cursor.fetchall()]
    mean = numpy.mean(prices, axis=0)
    prices = [x for x in prices if (x < mean * 5)]
    with lock:
        fig, ax = plt.subplots()
        n, bins, patches = ax.hist(prices, bins='auto')
        plt.xlabel('Price ($)', fontsize=20)
        plt.xticks(size = 15)
        plt.yticks(size = 15)
        plt.ylabel('Count', fontsize=20)
        plt.title(category, fontsize=20)
    return mpld3.fig_to_html(fig)


@app.route("/get/categories", methods=['GET', 'POST'])
def get_categories():
    retailer = request.form['retailer']
    return jsonify({'categories': get_categories_from_retailer(retailer)})


@app.route("/get/category/histogram", methods=['GET', 'POST'])
def get_category_histogram():
    retailer = request.form['retailer']
    category = request.form['category']
    return get_prices(retailer, category)


def join_products():
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT p.name, p.category, CAST(p.price as char(50)),
                    CAST(w.price as char(50)), CAST(p.rating as char(50)), 
                    CAST(w.rating as char(50)), p.num_ratings, w.num_ratings, p.img_url,
                    w.product_url, p.url, p.id
                    FROM target_products_unique p 
                    JOIN walmart_products_unique w
                    ON p.upc=w.upc
                    AND p.upc IS NOT NULL""")
    return cursor.fetchall()


@app.route("/price/compare", methods=['GET', 'POST'])
def compare():
    categories = defaultdict(list)
    products = {}
    items = join_products()
    for product, category, tPrice, wPrice, tRating, pRating, tRatings, wRatings, imgUrl, wURL, tURL, pId in items:
        product = product.decode('utf8')
        categories[category].append((product, pId))
        products[pId] = (tPrice, wPrice, tRating, pRating, tRatings, wRatings, imgUrl, wURL, tURL)
    return render_template('price_compare.html', categories=categories, products=products)
