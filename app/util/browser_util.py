#!python3
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from app.conf import config
import os


def get_browser(load_image=False):
    chrome_options = Options()
    # 不显示界面
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    if not load_image:
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
    if config.CHROME is not '':
        chrome_options.binary_location = config.CHROME
    if config.CHROME_DRIVER is not '':
        driver = webdriver.Chrome(config.CHROME_DRIVER, chrome_options=chrome_options)
    else:
        driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver


def get_cookies(marketplace: str):
    cookie_path = './app/cookies/{0}_cookies.pkl'.format(marketplace)
    cookies = {}
    if os.path.exists(cookie_path):
        with open(cookie_path, 'r') as f:
            for line in f.read().split(';'):
                if line is '':
                    continue
                name, value = line.strip().split('=', 1)
                cookies[name] = value
            f.close()
    return cookies


def write_cookies(marketplace: str, cookies: []):
    cookie_path = './app/cookies/{0}_cookies.pkl'.format(marketplace)
    cookie = [item['name'] + '=' + item['value'] for item in cookies]
    cookiestr = ';'.join(item for item in cookie)
    with open(cookie_path, 'w') as f:
        f.write(cookiestr)
        f.close()
