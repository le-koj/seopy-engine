from usp.tree import sitemap_tree_for_homepage
import requests
#import settings
import pandas as pd
from bs4 import BeautifulSoup
from typing import Tuple, List

DOMAIN_NAME = "" #settings.DOMAIN_NAME
USER_AGENT = {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'}

# Find and Parse Sitemaps to Create List of all website's pages
def get_pages_from_sitemap(domain_url: str) -> list:
    """
    Returns a list of all the pages present on a website.

    Args:
        domain_url (str): A string representing the website address, ex. 'https://example.com/'.

    Returns:
        list: returns a raw list of pages found.
    """
    list_pages_raw = [] # list of pages url
    
    tree = sitemap_tree_for_homepage(domain_url)
    for page in tree.all_pages():
        list_pages_raw.append(page.url)
     
    #print(f"\n----\nRaw Pages:\n{list_pages_raw}\n-----\n")    
    return list_pages_raw

def get_list_unique_pages(domain_url: str) -> list:
    """
    Return a list of unique pages links from list of raw pages links.

    Args:
        domain_url (str): A string representing the website address, ex. 'https://example.com/'.

    Returns:
        list: returns a unique list of pages links found.
    """
    list_pages_raw = get_pages_from_sitemap(domain_url)
    list_pages = []
    
    for page in list_pages_raw:
        if page in list_pages:
            pass
        else:
            list_pages.append(page)
    
    print(f'Number Of Pages: {len(list_pages)}')
    return list_pages

# Get external link list raw
def link_list(list_pages: list) -> Tuple[List[list], List[list]]:
    """
    Return two list items. one containing all the internal links and the other 
    all the external links, along with their location and associated text.

    Args:
        list_pages (list): a list of all the unique page urls for a website

    Returns:
        Tuple[List[list], List[list]]: tuple of 2 lists containing internal and external link information, respectfully
    """
    external_link_list_raw = []
    internal_link_list_raw = []
    count = 0
    length_list = len(list_pages)
    
    print(f"\n-----\nDomain URL: {DOMAIN_NAME}\n-----\n")
            
    def _create_link_lists(list_of_links):
        for link in list_of_links:
            try:
                if DOMAIN_NAME in link["href"] and "http" in link["href"]:
                    internal_link_list_raw.append([url, link["href"], link.text])
                elif "http" not in link["href"]:
                    pass
                else:
                    external_link_list_raw.append([url, link["href"], link.text])
            except:
                pass
    
    for url in list_pages:
        count = count + 1
        request = requests.get(url, headers=USER_AGENT)
        content = request.content
        soup = BeautifulSoup(content, 'lxml')
        list_of_links = soup.find_all("a")
        
        _create_link_lists(list_of_links=list_of_links)
        print(count, "pages checked out of ", length_list, ".")
    
    return internal_link_list_raw, external_link_list_raw

def get_unique_links(link_list_raw: List[list]) -> list:
    """
    Return a unique list of links from a raw list of links

    Args:
        link_list_raw (List[list]): A list containing a list of link information

    Returns:
        list: A list of urls
    """
    unique_links = []
    for link in link_list_raw:
        if link[1] in unique_links:
            pass 
        else:
            unique_links.append(link[1])
    
    return unique_links

# go through each unique link to identify broken ones
def identify_broken_links(unique_links: list) -> List[list]:
    """
    Ping each link and return a list of broken links.

    Args:
        unique_links (list): List of unique links.

    Returns:
        List[list]: A list of broken links and their status code.
    """
    count = 0
    broken_link_list = []
    
    for link in unique_links:
        count += 1
        print(f"Checking unique link #{count} out of {len(unique_links)}")
        
        try:
            status_code = requests.get(link, headers=USER_AGENT).status_code
            if status_code != 200:
                broken_link_list.append([link, status_code])
                #broken_link_list.append(link)
            else:
                #print(f"\n-----\n{link}: {status_code}\n-----\n")
                pass 
        except:
            broken_link_list.append([link, 0])
            
    return broken_link_list

# Identify unique broken links and matches them to original list of all links
def match_broken_links(broken_links_list: List[list], link_list_raw: List[list]) -> List[list]:
    """_summary_

    Args:
        broken_links_list (List[list]): _description_
        link_list_raw (List[list]): _description_

    Returns:
        List[list]: _description_
    """
    broken_link_location = []
    
    for link in link_list_raw:
        for broken_link in broken_links_list:
            if link[1] in broken_link:
                broken_link_location.append([link[0], link[1], link[2], broken_link[1]])
            else:
                pass
         
    #for link in link_list_raw:
       # if link[1] in broken_links_list:
        #    broken_link_location.append([link[0], link[1], link[2]])
        #else:
         #   pass

    pd.set_option('display.max_rows', 100)
    dataframe_final = pd.DataFrame(broken_link_location, columns=["URL", "Broken Link URL", "Anchor Text", "Status Code"])
    return dataframe_final
         
                

if __name__ == "__main__":
    pages = get_list_unique_pages(settings.WEBSITE_URL)
    internal_links_raw, external_links_raw = link_list(pages)
    internal_unique_links = get_unique_links(internal_links_raw)
    external_unique_links = get_unique_links(external_links_raw)
    
    internal_broken_links = identify_broken_links(internal_unique_links)
    external_broken_links = identify_broken_links(external_unique_links)
    print(f'\n-----\n')
    print(f"{len(internal_broken_links)} Internal Broken Links:\n{internal_broken_links}")
    print(f'\n-----\n')
    print(f"{len(external_broken_links)} External Broken Links:\n{external_broken_links}\n\n")
    print(match_broken_links(internal_broken_links, internal_links_raw))
    print(f'\n-----\n')
    print(match_broken_links(external_broken_links, external_links_raw))