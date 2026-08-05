from concurrent.futures import ThreadPoolExecutor
import requests
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--url",help="Target URL",required=True)
    parser.add_argument("-w","--wordlist",help="Directory wordlist",required=False)

    args = parser.parse_args()
    url = args.url
    wordlist = args.wordlist

    try: 
        with open(wordlist, 'r') as f:
            with ThreadPoolExecutor(max_workers=10) as threads:
                threads.map(lambda dir: test_directory(dir, url), f)
    except KeyboardInterrupt:
        exit()

def test_directory(directory, target_url):
    r = requests.get(target_url + '/' + directory, timeout=5)
    if r.status_code == 200:
        print(f"[+] Directory found! /{directory} | {r.status_code}")


if __name__ == "__main__":
    main()


