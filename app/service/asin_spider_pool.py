#!python3
import urllib
import requests
import re
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from datetime import datetime


class AsinSpiderPool(object):

    def __init__(self):
        self.url = 'https://www.amazon.{marketplace}/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords' \
                   '={keyword}&page={page}'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        self.cookies = {
            'session-id': '261-0736516-5154937',
            'ubid-acbfr': '262-1047786-1092163'
        }
        self.maxRecord = 20
        self.asins = []

    # {'marketplace':'com','keywords':'bbb','asin':'aaa'}
    def get_asin(self, params: '参数内容为json对象'):
        start_time = datetime.now()
        final_res = []
        marketplace = params['marketplace']
        asin = params['asin']
        keywords = params['keywords']
        self.url = self.url.replace('{marketplace}', marketplace)
        for item in asin.split(','):
            item = item.replace(r'/\s/', '')
            if len(item) >= 4:
                self.asins.append(item)

        keywords_list = keywords.split(',')
        pool = ThreadPool(10)
        for item in keywords_list:
            if len(item) >= 1:
                keywordplus = item.replace(r'/\s/', '+')
                keywordplus = urllib.parse.quote_plus(keywordplus)
                curl = self.url.replace('{keyword}', keywordplus)
                args = [(item, curl.replace('{page}', str(i)), i) for i in range(1, self.maxRecord + 1)]
                res = pool.starmap(self.getrankings, args)
                ens = False
                for sub in res:
                    if len(sub) > 0:
                        ens = True
                        final_res.append(sub[0])
                if not ens:
                    final_res.append({
                        'KeyWord': item,
                        'ASIN': '',
                        'Position': 'Not Found'
                    })
        pool.close()
        pool.join()
        ens = False
        for item in self.asins:
            for rs in final_res:
                if rs['ASIN'] == item:
                    ens = True
            if not ens:
                final_res.append({
                    'KeyWord': '',
                    'ASIN': item,
                    'Position': 'Not Found'
                })
        end_time = datetime.now()
        seconds = (end_time - start_time).seconds
        print('耗时：%s 秒' % seconds)
        return final_res

    def getrankings(self, keyword: str, url: str, page: int):
        print('page: ' + str(page))
        res = []
        rep = requests.get(url, headers=self.headers, cookies=self.cookies)
        if rep.status_code == 200:
            self.cookies['session-id'] = rep.cookies['session-id']
            self.cookies['ubid-acbfr'] = rep.cookies['ubid-acbfr']
            bs = BeautifulSoup(rep.text, 'lxml')
            atf_results = bs.find_all(name='li', id=re.compile('result_'))
            asins_found = []
            for item in atf_results:
                if 'AdHolder' not in item['class']:
                    asins_found.append(item['data-asin'])
            asins_per_page = len(asins_found)
            for j in range(len(self.asins)):
                if self.asins[j] in asins_found:
                    position = asins_found.index(self.asins[j])
                    position = (page - 1) * asins_per_page + position + 1
                    res.append({
                        'KeyWord': keyword,
                        'ASIN': self.asins[j],
                        'Position': position
                    })
        return res
