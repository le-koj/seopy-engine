# Find and Parse Sitemaps to Create List of all website's pages
from usp.tree import sitemap_tree_for_homepage
import requests
import pandas as pd
from bs4 import BeautifulSoup

DOMAIN_URL = "lazarinastoy.com"
USER_AGENT = {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'}

def get_pages_from_sitemap(domain_url):
    list_pages_raw = [] # list of pages url
    
    tree = sitemap_tree_for_homepage(domain_url)
    for page in tree.all_pages():
        list_pages_raw.append(page.url)
     
    #print(f"\n----\nRaw Pages:\n{list_pages_raw}\n-----\n")    
    return list_pages_raw

# Output unique pages links from list pages raw
def get_list_unique_pages(domain_url):
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
def link_list(list_pages):
    external_link_list_raw = []
    internal_link_list_raw = []
    count = 0
    length_list = len(list_pages)
    
    print(f"\n-----\nDomain URL: {DOMAIN_URL}\n-----\n")
            
    def _create_link_lists(list_of_links):
        for link in list_of_links:
            try:
                if DOMAIN_URL in link["href"] and "http" in link["href"]:
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

# Get link list unique values
def get_unique_links(link_list_raw):
    unique_links = []
    for link in link_list_raw:
        if link[1] in unique_links:
            pass 
        else:
            unique_links.append(link[1])
    
    return unique_links

# go through each unique link to identify broken ones
def identify_broken_links(unique_links: str):
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
def match_broken_links(broken_links_list, link_list_raw):
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
    pages = get_list_unique_pages('https://lazarinastoy.com/')
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