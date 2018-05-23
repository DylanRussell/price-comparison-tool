from __future__ import absolute_import
from priceCompare import app, mysql
from flask import render_template, request, jsonify
from collections import defaultdict
import json, mpld3, matplotlib, numpy


matplotlib.use('agg', warn=False, force=True)
import matplotlib.pyplot as plt
retailers_to_table = {'Dollar General': 'dollargeneral_products',
                      'Target': 'target_products_unique',
                      'Walmart': 'walmart_products_unique'}
plt.ioff()
matplotlib.rcParams.update({
    "lines.linewidth": 4.0,
    "axes.edgecolor": "#bcbcbc",
    # "patch.linewidth": 0.5,
    "legend.fancybox": True,
    # "axes.facecolor": "#eeeeee",
    # "axes.labelsize": "x-large",
    # "axes.grid": True,
    # "grid.color":"white",
    # "grid.linestyle":"solid",
    # "patch.edgecolor": "#eeeeee",
    # "axes.titlesize": "x-large",
    "figure.figsize": (10, 5)
})


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('home.html', retailers=retailers_to_table.keys())


def get_categories_from_retailer(retailer):
    q = """SELECT category FROM categories WHERE
        retailer=%s ORDER BY num_items DESC"""
    if retailer == 'Walmart':
        q += " LIMIT 200, 300"
    cursor = mysql.connection.cursor()
    cursor.execute(q, (retailer,))
    return ['Select A Category'] + sorted([x[0] for x in cursor.fetchall()])


def get_prices(retailer, category, retailer2, category2):
    cursor = mysql.connection.cursor()
    prices = []
    plt.style.use('seaborn-deep')
    for ret, cat in [(retailer, category), (retailer2, category2)]:
        if retailers_to_table.get(ret) and category:
            cursor.execute("""SELECT price FROM %s WHERE category="%s"
                            AND PRICE IS NOT NULL AND price > 0
                            """ % (retailers_to_table[ret], cat))
            price = [float(x[0]) for x in cursor.fetchall()]
            mean = numpy.mean(price, axis=0)
            price = [x for x in price if (x < mean * 5)]
            prices.append(price)
    labels = [cat + ' (' + ret + ')' for cat, ret in [(category, retailer), (category2, retailer2)] if cat]
    fig, ax = plt.subplots()
    colors = ['b']
    if len(prices) == 2:
        colors.append('g')
    ax.hist(prices, bins='auto', label=labels, color=colors)
    plt.xlabel('Price ($)', fontsize=20)
    plt.xticks(size=15)
    plt.yticks(size=15)
    plt.ylabel('Count', fontsize=20)
    plt.legend(loc='upper right')
    return mpld3.fig_to_html(fig)


@app.route("/get/categories", methods=['GET', 'POST'])
def get_categories():
    retailer = request.form['retailer']
    return jsonify({'categories': get_categories_from_retailer(retailer)})


@app.route("/get/category/histogram", methods=['GET', 'POST'])
def get_category_histogram():
    retailer = request.form['retailer1']
    category = request.form['category1']
    retailer2 = request.form['retailer2']
    category2 = request.form['category2']
    return get_prices(retailer, category, retailer2, category2)


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


@app.route("/slides", methods=['GET'])
def slide_deck():
    return render_template('deck.html')
