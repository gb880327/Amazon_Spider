#!python3
from bs4 import BeautifulSoup
import requests
import re


class ReviewSpider(object):

    def __init__(self):
        self.url = 'https://www.amazon.{marketplace}/product-reviews/{asin}/ref=cm_cr_arp_d_paging_btm?' \
                   'ie=UTF8&reviewerType=all_reviews&pageNumber={page}'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        }
        self.pageSize = 10

    # 获取评论 参数为json格式 [{'marketplace':'com', 'asin':'aaaaa', 'start':1, 'end': 100}]
    def get_review(self, params: '参数内容为json对象'):
        result = []
        for item in params:
            result.append(self.get_single_asin(item['marketplace'], item['asin'], item['start'], item['end']))
        return result

    def get_single_asin(self, marketplace: '站点', asin: 'ASIN', start: '评论数起点', end: '评论数终点'):
        _url = self.url.replace('{marketplace}', marketplace)
        _url = _url.replace('{asin}', asin)
        result = {'ASIN': asin, 'marketplace': marketplace, 'start': start, 'end': end}
        start_page = 1 if start <= self.pageSize else (
                start // self.pageSize + (0 if start % self.pageSize == 0 else 1))
        end_page = end // self.pageSize + (0 if end % self.pageSize == 0 else 1)
        self.parse_review(_url, start_page, start, self.pageSize if end >= self.pageSize else end, result,
                          marketplace, asin)
        if end_page > start_page:
            for i in range(start_page + 1, end_page + 1):
                self.parse_review(_url, i, 1,
                                  end % self.pageSize if i == end_page and end % self.pageSize != 0 else self.pageSize,
                                  result, marketplace, asin)
        return result

    # 解析html获取数据
    def parse_review(self, url: 'url地址', page: '评论页码', start: '当前页评论起始标记', end: '当前页评论结束标记', result: '结果',
                     marketplace: '站点', asin: 'ASIN'):
        try:
            url = url.replace('{page}', str(page))
            rep = requests.get(url, headers=self.headers)
            if rep.status_code == 200:
                bs = BeautifulSoup(rep.text, 'lxml')
                review_div = bs.find(id='cm_cr-review_list')
                if page == 1:
                    pages = bs.find_all(attrs={'data-reftag': 'cm_cr_arp_d_paging_btm'})
                    result["total_page"] = int(pages[len(pages) - 1].a.text)
                review_list = review_div.find_all(attrs={'data-hook': 'review'})
                result["reviews"] = [] if 'reviews' not in result else result["reviews"]
                count = 0
                for item in review_list:
                    count += 1
                    if count < start:
                        continue
                    if count > end:
                        break
                    review = item.find(attrs={'data-hook': 'review-body'}).text
                    star = item.find(attrs={'data-hook': 'review-star-rating'}).span.text[:3]
                    author = item.find(attrs={'data-hook': 'review-author'}).a
                    date = item.find(attrs={'data-hook': 'review-date'}).text.replace('on', '')
                    result["reviews"].append({
                        "index": (page - 1) * self.pageSize + count,
                        "id": item.attrs['id'],
                        "star": float(star),
                        "author": author.text,
                        "author_href":
                            re.split(r'\/gp\/profile\/(\S*)\/ref=cm_cr_arp_d_pdp\?ie=UTF8', author.attrs['href'])[1],
                        "date": date,
                        "content": review,
                        "marketplace": marketplace,
                        "asin": asin
                    })
                    print((page - 1) * self.pageSize + count)
        except ConnectionError as err:
            print(err)
        return result
