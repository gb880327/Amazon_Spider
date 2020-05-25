#!python3
from flask import Flask
from app.conf import config
from app.api.spider_api import spider_api


app = Flask(__name__)
app.config.from_object(config)
app.debug = app.config.get('DEBUG')
app.register_blueprint(spider_api, url_prefix='/api')


@app.route('/')
def index():
    return 'Welcome!'
