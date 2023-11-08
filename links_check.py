"""Website Link Auditor

This script allows the user to automate the inspection of all
the internal and external links on a website. The script allows
the user to audit a website for broken links.

This script uses the following libraries:
    ultimate sitemap parser
    requests library
    pandas
    BeautifulSoup
    typing

This file can also be imported as a module and contains the following
functions:

    * get_pages_from_sitemap - Returns a list of all the pages present on a website.
    * filter_unique_urls - Return a set of unique urls from list of raw urls.

    
"""
from usp.tree import sitemap_tree_for_homepage
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import Tuple, List
import settings

DOMAIN_NAME = "" 

def get_pages_from_sitemap(domain_url: str) -> list:
    """
    Retrieves a list of URLs from the sitemap of the provided domain.

    Parameters
    ----------
    domain_url : str
        The URL of the domain for which the sitemap is to be fetched.

    Returns
    -------
    list
        A list of URLs extracted from the sitemap.

    Notes
    -----
    This function depends on the 'sitemap_tree_for_homepage' function, which is assumed to
    return an iterator object representing the pages in the sitemap.

    Examples
    --------
    >>> domain_url = "https://example.com"
    >>> pages = get_pages_from_sitemap(domain_url)
    >>> len(pages) > 0
    True

    >>> all(isinstance(url, str) for url in pages)
    True

    >>> 'https://example.com/page1' in pages
    True

    >>> 'https://example.com/nonexistent' in pages
    False
    """
    
    sitemap_pages = sitemap_tree_for_homepage(domain_url).all_pages() # returns iterator object
    url_raw_list = [page.url for page in sitemap_pages] # list of urls
    return url_raw_list

def filter_unique_urls(domain_url: str) -> set:
    """
    Filter out duplicate URLs from the sitemap of the provided domain.

    Parameters
    ----------
    domain_url : str
        The URL of the domain for which the sitemap is to be fetched.

    Returns
    -------
    set
        A set of unique URLs extracted from the sitemap.

    Notes
    -----
    This function relies on the 'get_pages_from_sitemap' function, which retrieves a list
    of URLs from the sitemap and removes duplicates by converting them to a set.

    Examples
    --------
    >>> domain_url = "https://example.com"
    >>> unique_urls = filter_unique_urls(domain_url)
    >>> len(unique_urls) > 0
    True

    >>> isinstance(unique_urls, set)
    True

    >>> 'https://example.com/page1' in unique_urls
    True

    >>> 'https://example.com/page1' in filter_unique_urls(domain_url + '/duplicate-sitemap/')
    False
    """
    
    # filter out duplicate urls
    unqiue_urls = set(get_pages_from_sitemap(domain_url))
    return unqiue_urls

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
        request = requests.get(url, headers=settings.USER_AGENT)
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


def match_broken_links(broken_links_list: List[list], link_list_raw: List[list]) -> List[list]:
    """Identify unique broken links and matches them to original list of all links

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
         
    pd.set_option('display.max_rows', 100)
    dataframe_final = pd.DataFrame(broken_link_location, columns=["URL", "Broken Link URL", "Anchor Text", "Status Code"])
    return dataframe_final
         
                

if __name__ == "__main__":
    import sys

    try:
        print('getting info')
        DOMAIN_NAME = sys.argv[1]
        WEBSITE_URL = sys.argv[2] # full website url with protocol ex. "https://example.com"
    except IndexError as ie:
        sys.exit(f"\n----\nERROR: please provide both the DOMAIN NAME and the FULL WEBSITE URL\n-----\n")
        
    website_pages = get_pages_from_sitemap(WEBSITE_URL)
    print(f"-------\nWebsite Pages:\n{pd.Series(website_pages)}\n-------\n")
    
    filtered_pages = filter_unique_urls(WEBSITE_URL)
    print(f"-------\nFiltered Pages:\n{pd.Series(list(filtered_pages))}\n-------\n")
    #pages = get_list_unique_pages(WEBSITE_URL)
    #internal_links_raw, external_links_raw = link_list(pages)
    #internal_unique_links = get_unique_links(internal_links_raw)
    #external_unique_links = get_unique_links(external_links_raw)
    
    #internal_broken_links = identify_broken_links(internal_unique_links)
    #external_broken_links = identify_broken_links(external_unique_links)
    #print(f'\n-----\n')
    #print(f"{len(internal_broken_links)} Internal Broken Links:\n{internal_broken_links}")
    #print(f'\n-----\n')
    #print(f"{len(external_broken_links)} External Broken Links:\n{external_broken_links}\n\n")
    #print(match_broken_links(internal_broken_links, internal_links_raw))
    #print(f'\n-----\n')
    #print(match_broken_links(external_broken_links, external_links_raw))