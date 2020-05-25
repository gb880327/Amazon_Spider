#!python3
import requests
from bs4 import BeautifulSoup
from app.util.browser_util import get_browser, get_cookies, write_cookies
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from app.conf import config
from selenium.common.exceptions import NoSuchElementException

login_url = 'https://sellercentral.amazon.{marketplace}/'
header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/json; charset=UTF-8'
}


def check_login(marketplace: str):
    header['Referer'] = 'https://sellercentral.amazon.' + marketplace
    header['Host'] = 'sellercentral.amazon.' + marketplace
    cookies = get_cookies(marketplace)
    _url = login_url.replace('{marketplace}', marketplace)
    if len(cookies) > 0:
        rep = requests.get(_url, headers=header, cookies=cookies)
        if rep.status_code == 200:
            bs = BeautifulSoup(rep.text, 'lxml')
            node = bs.select_one('.a-declarative')
            if node is not None:
                print('Is logged in')
            else:
                login(_url, marketplace)
    else:
        login(_url, marketplace)


def login(url: str, marketplace: str):
    browser = get_browser(True)
    browser.get(url)
    for key, value in get_cookies('com').items():
        browser.add_cookie({'name': key, 'value': value})
    try:
        try:
            browser.find_element_by_id('ap_email')
        except NoSuchElementException:
            browser.find_element_by_id('signInSubmit').click()
            WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.ID, 'ap_email'))
            )
        browser.find_element_by_id('ap_email').send_keys(config.AMAZON_USER)
        browser.find_element_by_id('ap_password').send_keys(config.AMAZON_PWD)
        browser.find_element_by_id('signInSubmit').click()

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'a-declarative'))
        )
        # select = input('Is logged?(y/n)')
        # if select == 'y':
        write_cookies(marketplace, browser.get_cookies())
    finally:
        browser.close()
        # browser.quit()
