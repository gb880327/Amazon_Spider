#!python3
import requests
import base64
import re
import json
import math


class Roi(object):

    def __init__(self):
        self.price_url = 'https://www.amazon.com/gp/aw/ybh/handlers/rvi-faceouts.html?asins={asin}&types' \
                         '=CustomerViewedItems&positions=1&deviceType=desktop'
        self.url = 'https://sellercentral.amazon.com/fba/profitabilitycalculator/productmatches?searchKey={asin}' \
                   '&language=en_US'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        self.JAN_SEP_STD_STORAGE = 0.69
        self.JAN_SEP_OVS_STORAGE = 0.48
        self.OCT_DEC_STD_STORAGE = 2.40
        self.OCT_DEC_OVS_STORAGE = 1.20

    def start(self, asin: str):
        base64_str = base64.b64encode(asin.encode(encoding='utf-8'))
        _url = self.price_url.replace('{asin}', str(base64_str, encoding='utf-8'))
        rep = requests.get(_url)
        if rep.status_code == 200:
            r = re.compile(r'\$([0-9\.]+)').search(rep.text).groups()
            if len(r) >= 1:
                self.get_data(asin, r[0])
        else:
            print('asin is not found!')

    def get_data(self, asin: str, price: float):
        result = {}
        _url = self.url.replace('{asin}', asin)
        rep = requests.get(_url, headers=self.headers)
        if rep.status_code == 200 or rep.status_code == 201:
            rep_json = json.loads(rep.text)
            data = 'Error: ASIN not found...'
            for item in rep_json['data']:
                if item['asin'] == asin:
                    data = item
            if type(data) == 'str':
                print(data)
                return
            print(data)
            result['asin'] = asin
            result['asin_link'] = data['link']
            result['img'] = data['imageUrl'].replace('_SL120_', '_SL150_')

            temp = [float(data['length']), float(data['width']), float(data['height'])]
            temp.sort(reverse=True)
            length = temp[0]
            width = temp[1]
            height = temp[2]
            weight = data['weight']
            print(temp)
            storage = 6;
            if length < 15 and width < 12 and height < 0.75 and weight < 1:
                storage = 1
            elif length < 18 and width < 14 and height < 8 and weight < 20:
                storage = 2
            elif length < 60 and width < 30 and height * 2 + width * 2 + length < 130 and weight < 70:
                storage = 3
            elif length < 108 and width * 2 + height * 2 + length < 130 and weight < 150:
                storage = 4
            elif length < 108 and width * 2 + height * 2 + length < 165 and weight < 150:
                storage = 5
            else:
                storage = 6

            if storage == 1:
                tier = "Small Standard-Size"
            elif storage == 2:
                tier = "Large Standard-Size"
            elif storage == 3:
                tier = "Small Overize"
            elif storage == 4:
                tier = "Medium Overize"
            elif storage == 5:
                tier = "Large Overize"
            else:
                tier = "Special Oversize"

            if storage == 1 or storage == 2:
                jansep = round(self.JAN_SEP_STD_STORAGE * length * width * height / 12 / 12 / 12 * 100) / 100
                octdec = round(self.OCT_DEC_STD_STORAGE * length * width * height / 12 / 12 / 12 * 100) / 100
            else:
                jansep = round(self.JAN_SEP_OVS_STORAGE * length * width * height / 12 / 12 / 12 * 100) / 100
                octdec = round(self.OCT_DEC_OVS_STORAGE * length * width * height / 12 / 12 / 12 * 100) / 100
            maxweight = round(width * height * length / 139 * 100) / 100
            if weight > maxweight or storage == 1 or (storage == 2 and weight <= 1):
                maxweight = weight
            extraweight = 0.25
            if storage >= 3:
                extraweight = 1
            shipping_weight = math.ceil(maxweight + extraweight)

            if storage == 1:
                pickpack = 2.41
            elif storage == 2 and shipping_weight <= 1:
                pickpack = 3.19
            elif storage == 2 and shipping_weight <= 2:
                pickpack = 4.71
            elif storage == 2:
                pickpack = 4.71 + (shipping_weight - 2) * 0.38
            elif storage == 3 and shipping_weight <= 2:
                pickpack = 8.13
            elif storage == 3:
                pickpack = 8.13 + (shipping_weight - 2) * 0.38
            elif storage == 4 and shipping_weight <= 2:
                pickpack = 9.44
            elif storage == 4:
                pickpack = 9.44 + (shipping_weight - 2) * 0.38
            elif storage == 5 and shipping_weight <= 90:
                pickpack = 73.18
            elif storage == 5:
                pickpack = 73.18 + (shipping_weight - 90) * 0.79
            elif storage == 6 and shipping_weight <= 90:
                pickpack = 137.32
            elif storage == 6:
                pickpack = 137.32 + (shipping_weight - 90) * 0.91
            pickpack = round(pickpack * 100) / 100

        else:
            self.get_data(asin, price)
