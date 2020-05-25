#!python3
from urllib.parse import quote_plus
import requests
import json
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime


class LongTailSpider(object):

    def __init__(self):
        self.url = '/search/complete?method=completion&mkt={mkt}&p=Search&l={lan}&b2b=0&fresh=0&sv=desktop&' \
                   'client=amazon-search-ui&x=String&search-alias=aps&q={q}&qs={qs}&cf=1&fb=1&sc=1&'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        self.domains = {
            "US": {"plid": "com", "domain": "https://completion.amazon.com", "mkt": "1", "lan": "en_US"},
            "CN": {"plid": "cn", "domain": "https://completion.amazon.cn", "mkt": "3240", "lan": "zh_CN"},
            "BR": {"plid": "com.br", "domain": "https://completion.amazon.com", "mkt": "526970", "lan": "pt_BR"},
            "CA": {"plid": "ca", "domain": "https://completion.amazon.com", "mkt": "7", "lan": "en_CA"},
            "MX": {"plid": "com.mx", "domain": "https://completion.amazon.com", "mkt": "771770", "lan": "es_MX"},
            "JP": {"plid": "co.jp", "domain": "https://completion.amazon.co.jp", "mkt": "6", "lan": "ja_JP"},
            "AU": {"plid": "com.au", "domain": "https://completion.amazon.co.jp", "mkt": "111172", "lan": "en_AU"},
            "UK": {"plid": "co.uk", "domain": "https://completion.amazon.co.uk", "mkt": "3", "lan": "en_GB"},
            "DE": {"plid": "de", "domain": "https://completion.amazon.co.uk", "mkt": "4", "lan": "de_DE"},
            "ES": {"plid": "es", "domain": "https://completion.amazon.co.uk", "mkt": "44551", "lan": "es_ES"},
            "FR": {"plid": "fr", "domain": "https://completion.amazon.co.uk", "mkt": "5", "lan": "fr_FR"},
            "IN": {"plid": "in", "domain": "https://completion.amazon.co.uk", "mkt": "44571", "lan": "en_IN"},
            "IT": {"plid": "it", "domain": "https://completion.amazon.co.uk", "mkt": "35691", "lan": "it_IT"},
            "NL": {"plid": "nl", "domain": "https://completion.amazon.co.uk", "mkt": "328451", "lan": "nl_NL"}
        }

    # json对象 {'godeep': True, 'whereat': 3, 'keyword': 'usb', 'marketplace': 'US'}
    def get_long_tail(self, params: '参数内容为json对象'):
        start_time = datetime.now()
        lt_marketplace = params['marketplace']
        keyword = params['keyword']
        whereat = params['whereat']
        godeep = params['godeep']
        country = self.domains[lt_marketplace]
        plids = country['plid']
        country_url = self.url.replace('{lan}', country['lan'])
        country_url = country_url.replace('{mkt}', country['mkt'])
        country_url = country['domain'] + country_url
        if not godeep:
            chars = [" "]
        else:
            chars = ["", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s",
                     "t", "u", "v", "w", "x", "y", "z"]
        req_params = []
        for item in chars:
            if whereat == 1 or whereat == 3:
                req_params.append(country_url.replace('{q}', quote_plus(keyword + ' ' + item)).replace('{qs}', ""))
            if whereat == 2 or whereat == 3:
                req_params.append(
                    country_url.replace('{q}', "%23" + quote_plus(item)).replace('{qs}', '%23' + quote_plus(keyword)))
        pool = ThreadPool(10)
        ltres = []
        res = pool.map(self.ajax_req, req_params)
        for item in res:
            ltres = ltres + item
        pool.close()
        pool.join()
        end_time = datetime.now()
        seconds = (end_time - start_time).seconds
        print('耗时：%s 秒' % seconds)
        return {
            'op': 'LT',
            'plid': plids,
            'keyword': keyword,
            'context': '\r\n'.join(ltres)
        }

    def ajax_req(self, url: str):
        ltres = []
        rep = requests.get(url, headers=self.headers)
        rep_text = rep.text.replace('completion = ', '').replace(';String();', '')
        for kw in json.loads(rep_text)[1]:
            ltres.append(kw)
        return ltres
