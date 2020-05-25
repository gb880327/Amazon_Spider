#!python3
from flask import Blueprint, request, g
from app.util.webutil import error, success
from app.service.asin_spider import AsinSpider


spider_api = Blueprint('api', __name__)


# asin收录 参数为json字符串 {"marketplace": "com", "keywords": "usb,bsc", "asin": "aaaaaa,bbbbb"}
# 多个关键词和asin用逗号隔开
@spider_api.route('/asin', methods=['POST'])
def asin_spider():
    if not request.is_json:
        return error('参数必须为json格式字符串！')
    params = request.json
    if 'asin' not in g:
        asin = AsinSpider()
        g.asin = asin
    else:
        asin = g.asin
    return success(asin.get_asin(params))
