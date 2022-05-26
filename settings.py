import sys

try:
    DOMAIN_NAME = sys.argv[1]
    WEBSITE_URL = sys.argv[2] # full website url with protocol ex. "https://example.com"
except IndexError as ie:
    sys.exit(f"\n----\nERROR: please provide both the DOMAIN NAME and the FULL WEBSITE URL\n-----\n")
   
USER_AGENT = {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'}