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
from typing import Tuple, List, Iterable
import settings

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

def map_anchors_to_url(unqiue_urls: list) -> dict[str, Iterable[dict]]:
    """
    Get and map anchors to their respective URLs.

    Parameters
    ----------
    unique_urls : list
        A list of unique URLs.

    Returns
    -------
    dict[str, Iterable[dict]]
        A dictionary mapping each URL to an iterable of its associated anchor tags.

    Notes
    -----
    This function makes use of the 'requests' library to fetch the content of each URL and
    'BeautifulSoup' for parsing HTML to extract anchor tags.

    Examples
    --------
    >>> unique_urls = ['https://example.com', 'https://example.com/page1']
    >>> url_anchors_map = map_anchors_to_url(unique_urls)
    >>> isinstance(url_anchors_map, dict)
    True

    >>> len(url_anchors_map) == len(unique_urls)
    True

    >>> all(isinstance(anchors, Iterable) for anchors in url_anchors_map.values())
    True

    >>> all(isinstance(anchor, dict) for anchors in url_anchors_map.values() for anchor in anchors)
    True

    >>> 'https://example.com' in url_anchors_map
    True

    >>> 'https://example.com/nonexistent' in url_anchors_map
    False
    """
    print('\n', '#' * 10, '\n', '#', '\t', 'Mapping Anchors To URL', '\n', '#' * 10, '\n')
    
    count = 0
    length_list = len(unqiue_urls)
    url_map = dict()
    
    # get and map the anchors to a given url
    for url in unqiue_urls:
        count = count + 1
        request = requests.get(url, headers=settings.USER_AGENT)
        content = request.content
        soup = BeautifulSoup(content, 'lxml')
        url_anchors = soup.find_all("a") # returns iterable
        url_map[f'{url}'] = url_anchors
        print('-------> ', count, "pages checked out of ", length_list, "\n")
    
    print('\n', '#' * 10, '\n', '#', '\t', '!!!End Maping Anchors To URL!!!', '\n', '#' * 10, '\n')
    return url_map

def create_link_lists(domain_name: str, url: str, page_anchors: Iterable[dict]) -> Tuple[List[list], List[list]]:
    """
    Create lists of internal and external links for a given URL.

    Parameters
    ----------
    domain_name : str
        The domain name to filter internal links.
    url : str
        The URL of the webpage.
    page_anchors : Iterable[dict]
        Iterable containing dictionaries representing anchor tags with 'href' attributes.

    Returns
    -------
    Tuple[List[list], List[list]]
        A tuple containing lists of internal and external links.

    Examples
    --------
    >>> domain_name = "example.com"
    >>> url = "https://example.com/page1"
    >>> page_anchors = [{'href': 'https://example.com/internal1', 'text': 'Internal Link 1'}, {'href': 'https://external.com', 'text': 'External Link'}]
    >>> internal_links, external_links = create_link_lists(domain_name, url, page_anchors)
    
    >>> isinstance(internal_links, list)
    True
    
    >>> isinstance(external_links, list)
    True
    
    >>> all(isinstance(link, list) for link in internal_links)
    True
    
    >>> all(isinstance(link, list) for link in external_links)
    True
    
    >>> internal_links
    [['https://example.com/page1', 'https://example.com/internal1', 'Internal Link 1']]
    
    >>> external_links
    [['https://example.com/page1', 'https://external.com', 'External Link']]
    """
    print('\n', '#' * 50, '\n', '#', '\t\t', 'Creating Link Lists For: ', url, '\n', '#' * 50, '\n')
    
    page_external_links = [] # container for exrernal links
    page_internal_links= [] # container for internal links
    
    # seperate internal and external links for a given url/webpage
    for a in page_anchors:
        try:
            if (domain_name in a["href"]) and ("http" in a["href"]):
                page_internal_links.append([url, a["href"], a.text])
            elif "http" not in a["href"]:
                pass
            else:
                page_external_links.append([url, a["href"], a.text])
        except:
            pass  

    print('\n', '#' * 10, '\n', '#', '\t\t', '!!!End Creating Link Lists!!!', '\n', '#' * 10, '\n')
    return page_internal_links, page_external_links

def get_all_links(domain_name: str, unqiue_urls: list) -> Tuple[List[list], List[list]]:
    """
    Get all internal and external links from a list of unique URLs.

    Parameters
    ----------
    domain_name : str
        The domain name to filter internal links.
    unique_urls : list
        A list of unique URLs.

    Returns
    -------
    Tuple[List[list], List[list]]
        A tuple containing lists of all internal and external links.

    Examples
    --------
    >>> domain_name = "example.com"
    >>> unique_urls = ['https://example.com', 'https://example.com/page1']
    >>> all_internal_links, all_external_links = get_all_links(domain_name, unique_urls)
    
    >>> isinstance(all_internal_links, list)
    True
    
    >>> isinstance(all_external_links, list)
    True
    
    >>> all(isinstance(link, list) for link in all_internal_links)
    True
    
    >>> all(isinstance(link, list) for link in all_external_links)
    True
    
    >>> all_internal_links
    [['https://example.com', 'https://example.com/internal1', 'Internal Link 1'], ['https://example.com/page1', 'https://example.com/internal2', 'Internal Link 2']]
    
    >>> all_external_links
    [['https://example.com', 'https://external.com', 'External Link 1'], ['https://example.com/page1', 'https://external2.com', 'External Link 2']]
    """
    all_internal_links = []
    all_external_links = []
    
    url_anchor_maps = map_anchors_to_url(unqiue_urls) # dictionary of urls with anchors
    
    # loop through url_anchor_maps
    # combine all internal and external links
    for url, anchors in url_anchor_maps.items():
        internal_links, external_links = create_link_lists(domain_name=domain_name, url=url, page_anchors=anchors)
        all_internal_links += internal_links
        all_external_links += external_links
    return all_internal_links, all_external_links

def filter_unique_hrefs(link_groups: List[list]) -> list:
    """
    Filter unique hrefs from a list of link groups.

    Parameters
    ----------
    link_groups : List[list]
        A list of link groups, where each group is a list containing URL, href, and text.

    Returns
    -------
    list
        A list of unique hrefs extracted from the link groups.

    Examples
    --------
    >>> link_groups = [['https://example.com', 'https://example.com/internal1', 'Internal Link 1'], ['https://example.com/page1', 'https://example.com/internal2', 'Internal Link 2']]
    >>> unique_hrefs = filter_unique_hrefs(link_groups)
    
    >>> isinstance(unique_hrefs, list)
    True
    
    >>> all(isinstance(href, str) for href in unique_hrefs)
    True
    
    >>> len(unique_hrefs) == len(set(unique_hrefs))
    True
    
    >>> 'https://example.com/internal1' in unique_hrefs
    True
    
    >>> 'https://example.com/unique' in unique_hrefs
    False
    """
    unique_hrefs = []
    for link in link_groups:
        if link[1] in unique_hrefs:
            pass 
        else:
            unique_hrefs.append(link[1])
    
    return unique_hrefs

def identify_broken_links(unique_links: list) -> List[list]:
    """
    Identify broken links from a list of unique links.

    Parameters
    ----------
    unique_links : list
        A list of unique URLs.

    Returns
    -------
    List[list]
        A list of broken links, each containing the link and its HTTP status code.
        
    Notes
    -----
    This function makes use of the 'requests' library to fetch the status code of each link

    Examples
    --------
    >>> unique_links = ['https://example.com', 'https://example.com/page1']
    >>> broken_links = identify_broken_links(unique_links)
    
    >>> isinstance(broken_links, list)
    True
    
    >>> all(isinstance(link, list) for link in broken_links)
    True
    
    >>> all(isinstance(link[0], str) for link in broken_links)
    True
    
    >>> all(isinstance(link[1], int) for link in broken_links)
    True
    
    >>> any(link[1] != 200 for link in broken_links)
    False
    
    >>> 'https://example.com/nonexistent' in unique_links
    False
    
    >>> 'https://example.com/nonexistent' in [link[0] for link in broken_links]
    True
    """
    count = 0
    broken_link_list = []
    
    for link in unique_links:
        count += 1
        print(f"Checking unique link #{count} out of {len(unique_links)}")
        
        try:
            # get http status code for the link
            status_code = requests.get(link, headers=settings.USER_AGENT).status_code
            
            # add link to broken links if request unsuccessful
            if status_code != 200:
                broken_link_list.append([link, status_code])
            else:
                pass 
        except:
            broken_link_list.append([link, 0])
            
    return broken_link_list


def match_broken_links(broken_links: List[list], all_website_links: List[list]) -> pd.DataFrame:
    """
    Match broken links with their corresponding location in the original set of links.

    Parameters
    ----------
    broken_links : List[list]
        A list of broken links, each containing the link and its HTTP status code.
    all_website_links : List[list]
        A list of all website links, each containing URL, href, and text.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing information about the location of broken links, including the original URL,
        broken link URL, anchor text, and HTTP status code.
        
    Notes
    -----
    This function depends on the 'pandas' library for creating the resulting DataFrame.
    Ensure that 'pandas' is installed in your environment before using this function.

    Examples
    --------
    >>> broken_links = [['https://example.com/internal1', 404], ['https://example.com/nonexistent', 404]]
    >>> all_website_links = [['https://example.com/page1', 'https://example.com/internal1', 'Internal Link 1'], ['https://example.com/page2', 'https://external.com', 'External Link']]
    >>> broken_link_dataframe = match_broken_links(broken_links, all_website_links)
    
    >>> isinstance(broken_link_dataframe, pd.DataFrame)
    True
    
    >>> len(broken_link_dataframe) == len(broken_links)
    True
    
    >>> broken_link_dataframe.columns.tolist()
    ['URL', 'Broken Link URL', 'Anchor Text', 'Status Code']
    
    >>> 'https://example.com/page1' in broken_link_dataframe['URL'].tolist()
    True
    
    >>> 404 in broken_link_dataframe['Status Code'].tolist()
    True
    
    >>> 'https://external.com' in broken_link_dataframe['Broken Link URL'].tolist()
    False
    """
    broken_link_location = []
    links_to_skip = set()
    
    for link in all_website_links:
        for broken_link in broken_links:
            if (link[1] in broken_link) and (link[1] not in links_to_skip):
                broken_link_location.append([link[0], link[1], link[2], broken_link[1]])
                
                # add broken link to links_to_skip list to avoid duplicates
                links_to_skip.add(link[1])
            else:
                pass
    
    pd.set_option('display.max_rows', 500)
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
    
    #website_pages = get_pages_from_sitemap(WEBSITE_URL)
    #print(f"-------\nWebsite Pages:\n{pd.Series(website_pages)}\n-------\n")
    
    filtered_pages = filter_unique_urls(WEBSITE_URL)
    #print(f"-------\nFiltered Pages:\n{pd.Series(list(filtered_pages))}\n-------\n")
    
    internal, external = get_all_links(DOMAIN_NAME, filtered_pages)
    #print(f"\n-------\nInternal Links:\n{internal}\n-------\n\n")
    #print(f"\n-------\nExternal Links:\n{external}\n-------\n")
    print(f"\n-------\nList Lenght:\n{len(internal + external)}\n-------\n")
    
    hrefs = filter_unique_hrefs(internal + external)
    print(f"\n-------\nhref Lenght:\n{len(hrefs)}\n-------\n")
    
    b_links = identify_broken_links(hrefs)
    print(f"\n-------\nList Lenght:\n{b_links}\n-------\n")
    print(f"-------\nBroken Links Lenght:\n{len(b_links)}\n-------\n")
    
    pd_links = match_broken_links(broken_links=b_links, all_website_links=(internal + external))
    print(f"\n-------\nDataframe: \n{pd_links}\n-------\n")
    print(f"\n-------\nDataframe Length: \n{len(pd_links)}\n-------\n")
    