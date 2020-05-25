#!python3
from urllib.parse import quote_plus
from app.util.browser_util import get_cookies
from app.service.amazon_login import check_login
import requests
import re
import json


class VoltaSpider(object):

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
            'Content-Type': 'application/json; charset=UTF-8'
        }
        self.login_url = 'https://sellercentral.amazon.{marketplace}/'
        self.volume_rul = 'https://sellercentral.amazon.{marketplace}/sspa/hsa/cb/keywords/keywordPower'
        self.domains = {
            'com': 'https://completion.amazon.com/search/complete?method=completion&mkt=1&p=Search&l=en_US&b2b=0&fresh='
                   '0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc=1&',
            'co.uk': 'https://completion.amazon.co.uk/search/complete?method=completion&mkt=3&p=Search&l=en_US&b2b=0&'
                     'fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1'
                     '&sc=1&',
            'es': 'https://completion.amazon.co.uk/search/complete?method=completion&mkt=44551&p=Search&l=en_US&b2b=0&'
                  'fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc='
                  '1&',
            'nl': 'https://completion.amazon.co.uk/search/complete?method=completion&mkt=328451&p=Search&l=en_US&b2b=0&'
                  'fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc='
                  '1&',
            'com.mx': 'https://completion.amazon.com/search/complete?method=completion&mkt=771770&p=Search&l=en_US&b2b='
                      '0&fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb'
                      '=1&sc=1&',
            'co.jp': 'https://completion.amazon.co.jp/search/complete?method=completion&mkt=6&p=Search&l=en_US&b2b=0&'
                     'fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&'
                     'sc=1&',
            'it': 'https://completion.amazon.co.uk/search/complete?method=completion&mkt=35691&p=Search&l=en_US&b2b=0&'
                  'fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc='
                  '1&',
            'in': 'https://completion.amazon.co.uk/search/complete?method=completion&mkt=44571&p=Search&l=en_US&b2b=0&'
                  'fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc='
                  '1&',
            'de': 'https://completion.amazon.co.uk/search/complete?method=completion&mkt=4&p=Search&l=en_US&b2b=0&fresh'
                  '=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc=1&',
            'fr': 'https://completion.amazon.co.uk/search/complete?method=completion&mkt=5&p=Search&l=en_US&b2b=0&fresh'
                  '=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc=1&',
            'cn': 'https://completion.amazon.cn/search/complete?method=completion&mkt=3240&p=Search&l=en_US&b2b=0&fresh'
                  '=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc=1&',
            'ca': 'https://completion.amazon.com/search/complete?method=completion&mkt=7&p=Search&l=en_US&b2b=0&fresh=0'
                  '&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc=1&',
            'com.br': 'https://completion.amazon.com/search/complete?method=completion&mkt=526970&p=Search&l=en_US&b2b='
                      '0&fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb'
                      '=1&sc=1&',
            'com.au': 'https://completion.amazon.com.au/search/complete?method=completion&mkt=111172&p=Search&l=en_US&'
                      'b2b=0&fresh=0&sv=desktop&client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf'
                      '=1&fb=1&sc=1&',
        }
        self.chars = ["", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                      "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", ",",
                      "-"]

    # {'marketplace': 'com', 'keywords':'usb', 'exact': true, 'broad': false}
    def start(self, params: '参数内容为json对象'):
        marketplace = params['marketplace']
        keywords = params['keywords']
        exact = params['exact']
        broad = params['broad']
        check_login(marketplace)
        self.header['Referer'] = 'https://sellercentral.amazon.' + marketplace
        self.header['Host'] = 'sellercentral.amazon.' + marketplace
        searchwords = keywords.split('\n')
        self.cookies = get_cookies(marketplace)
        final_res = []
        for item in searchwords:
            final_res = final_res + self.kw_process(item, marketplace, exact, broad)
        return final_res

    def kw_process(self, searchwords: str, marketplace: str, exact: bool, broad: bool):
        result = []
        for el in self.chars:
            kw = searchwords + ' ' + el
            _url = self.domains[marketplace].replace('{q}', quote_plus(kw)).replace('{qs}', '')
            self.vol_process(_url, result)
        for el in self.chars:
            _url = self.domains[marketplace].replace('{q}', quote_plus(el)).replace('{qs}', quote_plus(searchwords[0]))
            self.vol_process(_url, result)
        words = searchwords.split(' ')
        if len(words) >= 2:
            for i in range(1, len(words) + 1):
                a = ' '.join(words[:i])
                b = ' '.join(words[i: len(words)])
                for el in self.chars:
                    _url = self.domains[marketplace].replace('{q}', quote_plus(a) + '%20' + quote_plus(el)) \
                        .replace('{qs}', quote_plus(b))
                    self.vol_process(_url, result)
        result.append(searchwords[0])
        unique_result = []
        for kw in result:
            if kw not in unique_result:
                unique_result.append(kw)
        _url = self.volume_rul.replace('{marketplace}', marketplace)
        return self.form_chunks(_url, unique_result, exact, broad)

    def form_chunks(self, url: str, unique_result: [], exact: bool, broad: bool):
        results = []
        chunks = []
        chunk = 400
        for i in range(0, len(unique_result), chunk):
            chunks.append(unique_result[i:i + chunk])
        for i in range(len(chunks)):
            klist = []
            for kw in chunks[i]:
                if broad:
                    klist.append({'key': kw, 'matchType': 'BROAD'})
                if exact:
                    klist.append({'key': kw, 'matchType': 'EXACT'})
            rep = requests.post(url, data=json.dumps({
                'keywordList': klist,
                'pageId': 'TOG7TXW0L3H2PS'
            }), cookies=self.cookies, headers=self.header)
            if rep.status_code == 200:
                data = json.loads(rep.text)
                for item in data:
                    results.append({
                        'Keyword': item['keyword'],
                        'MatchType': item['matchType'],
                        'WeeklyImpressions': round(item['impression'] * 30.41)
                    })
        return results

    @staticmethod
    def vol_process(url: str, result: []):
        rep = requests.get(url)
        if ',["' in rep.text:
            kws = re.search(r'\,\[\"(.*?)\"\]\,', rep.text).group(1)
            for k in kws.split('\",\"'):
                result.append(k)
