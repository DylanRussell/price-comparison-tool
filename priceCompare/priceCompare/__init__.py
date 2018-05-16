from __future__ import absolute_import
from flask import Flask
from priceCompare.flask_mysql import MySQL
from flask_bootstrap import Bootstrap


application = Flask(__name__)
app = application
app.config.from_object('priceCompare.config_safe')
Bootstrap(app)
mysql = MySQL(app)

import priceCompare.views.main
