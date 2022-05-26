from email import header
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

ROOT_DOMAIN = "lekoj.com"

def get_broken_links(url, headers=None):
    print(f"-----------\nInitiating broken links function\n-----------")
    
    # initialize list for broken links
    broken_links = []
    
    # internal function for validating http status code.
    def _validate_url(url):
        r = requests.head(url)
        if r.status_code == 404:
            broken_links.append(url)
            
    # make request to url
    data = requests.get(url, headers=headers).text
    print(f"-----------\nDATA: {data}\n-----------")
    
    # parse HTML from request
    soup = BeautifulSoup(data, features="html.parser")
    
    # create a list containing all links with the root domain
    internal_links = [link.get("href") for link in soup.find_all("a") if f"//{ROOT_DOMAIN}" in link.get("href")]
    links = [link.get("href") for link in soup.find_all("a")]
    print(f"-----------\n{ROOT_DOMAIN} LINKS: \n{links}\n-----------")
    
    # loop through links checking for 404 responsese, and append to list
    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(_validate_url, internal_links)
    
    print(broken_links)    
    return broken_links

if __name__ == "__main__":
    url = 'https://lekoj.com'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36'
    headers = {'User-Agent': user_agent,
               'referer': 'https://...'}
    get_broken_links(url)