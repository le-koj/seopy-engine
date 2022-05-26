from usp.tree import sitemap_tree_for_homepage

tree = sitemap_tree_for_homepage('https://lekoj.com/')

if __name__ == "__main__":
    #print(tree)
    # all_pages() returns an Iterator
    PAGE_COUNT = 1
    for page in tree.all_pages():
        print(f"\n-----\nPage-{PAGE_COUNT}: {page}\n-----\n")
        PAGE_COUNT += 1