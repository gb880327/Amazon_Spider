# !python3
import json
from app.db import mongo
from app.service.review_spider import ReviewSpider
from app.service.asin_spider import AsinSpider
from app.service.asin_spider_pool import AsinSpiderPool
from app.service.longtail_spider import LongTailSpider
from app.service.volta_spider import VoltaSpider
from app.service.rskey_spider import RskeySpider
from app.service.amazon_login import check_login

# from app.service.roi import Roi

# spider = ReviewSpider()
# result = spider.get_review([{'marketplace': 'com', 'asin': 'B0179SSDMC', 'start': 1, 'end': 1600}])
# print(result)

# client = mongo().get_collection('review')
# print(client.insert(result))
# print(client.find_one({'reviews.id': 'R1CSYDDLXHCVBP'}))

# asin = AsinSpider()
# res = asin.get_asin({'marketplace': 'com', 'keywords': 'usb', 'asin': 'B00FE2N1WS'})
# print(res)

# asin = AsinSpiderPool()
# res = asin.get_asin({'marketplace': 'fr', 'keywords': 'Lunettes de soleil,Lunettes et Accessoires,soleil',
#                      'asin': 'B06XFK2GWC'})
# print(res)

longtail = LongTailSpider()
# ltres = longtail.get_long_tail({'godeep': True, 'whereat': 3, 'keyword': 'gootium', 'marketplace': 'US'})
# ret = ltres['context'].split("\r\n")
# print(len(ret))
# print(ret)
ltres = longtail.get_long_tail({'godeep': True, 'whereat': 3, 'keyword': 'gootium wallet', 'marketplace': 'US'})
ret = ltres['context'].split("\r\n")
print(len(ret))
print(ret)
# volta = VoltaSpider()
# result = volta.start({'marketplace': 'com', 'keywords': 'usb', 'exact': True, 'broad': True})
# print(result)

# rskey = RskeySpider()
# print(rskey.start('com', 'B00LQEU33S,B01KHODXRK'))

# check_login('com')

# roi = Roi()
# roi.start('B077P6K94Z')
