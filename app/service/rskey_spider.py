#!python3
from app.service.amazon_login import check_login
from app.util.browser_util import get_cookies
import requests
import json


# 深简诊断
class RskeySpider(object):

    def __init__(self):
        self.cookies = {}
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json; charset=UTF-8'}

        self.score_url = 'https://ams.amazon.{marketplace}/campaigns/sponsored-products/suggested-keywords/?asins='
        self.volume_url = 'https://sellercentral.amazon.{marketplace}/sspa/hsa/cb/keywords/keywordPower'

    # {'marketplace': 'com', 'asin':'aaaaaa'}
    def start(self, params: '参数内容为json对象'):
        marketplace = params['marketplace']
        asin = params['asin']
        check_login(marketplace)
        self.header['Referer'] = 'https://sellercentral.amazon.' + marketplace
        self.header['Host'] = 'sellercentral.amazon.' + marketplace
        result = {
            'trafficscore': 0,
            'Result': []
        }
        asins = asin.split(',')
        rskey_kw = []
        relevance_scores = {}
        self.cookies = get_cookies(marketplace)
        for item in asins:
            self.get_score(self.score_url.replace('{marketplace}', marketplace) + item, rskey_kw, relevance_scores)
            self.get_volumes(self.volume_url.replace('{marketplace}', marketplace), item, rskey_kw, relevance_scores,
                             result)
        result['trafficscore'] = result['trafficscore'] / 100
        result['marketplace'] = marketplace
        result['asin'] = asin
        return result

    def get_score(self, url: str, rskey_kw: [], relevance_scores: {}):
        rep = requests.get(url, cookies=self.cookies, headers=self.header)
        if rep.status_code == 200:
            for item in json.loads(rep.text)['aaData']:
                keyword = item['keyword']
                rskey_kw.append({
                    'keyword': keyword,
                    'score': item['score']
                })
                relevance_scores[keyword] = item['score']

    def get_volumes(self, url: str, asin: str, rskey_kw: [], relevance_scores: {}, result):
        klist = []
        for item in rskey_kw:
            klist.append({
                'key': item['keyword'],
                'matchType': 'EXACT'
            })
        rep = requests.post(url, data=json.dumps({
            'keywordList': klist
        }), cookies=self.cookies, headers=self.header)
        if rep.status_code == 200:
            kw_json = json.loads(rep.text)
            final_data = []
            for item in kw_json:
                relevance = relevance_scores[item['keyword']]
                traffic = round(item['impression'] * 30.41)
                final_data.append({
                    'asin': asin,
                    'keyword': item['keyword'],
                    'traffic': traffic,
                    'relevance': relevance
                })
                if relevance >= 90:
                    result['trafficscore'] += relevance * traffic
            result['Result'][len(result['Result']):len(result['Result'])] = final_data
