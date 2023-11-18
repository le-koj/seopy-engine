"""
SEO LINK AUDITOR USER INTERFACE

This script provides a Streamlit interface to audit a website for broken internal and external links. It leverages functions from the 'links_check' module, utilizes Pandas for data presentation, and relies on user input through the Streamlit app.

Usage:
- Ensure 'settings', 'pandas', 'streamlit', and 'links_check' are properly installed in your environment.
- RUN `streamlit run streamlit_app.py`
- Open web browser at `http://localhost:8501/`

Examples:
    1. Set the domain name:
        >>> st.text_input("Domain Name", '', placeholder='example.com')
        'example.com'
    
    2. Set the homepage URL:
        >>> st.text_input("Full website url", '', placeholder='https://example.com')
        'https://example.com'

    3. Fetch unique website pages:
        >>> unique_website_pages = lc.filter_unique_urls('https://example.com')
        >>> len(unique_website_pages) > 0
        True

    4. Get unique internal and external links:
        >>> internal_links, external_links = lc.get_all_links('example.com', unique_website_pages)
        >>> len(internal_links) > 0
        True

        >>> len(external_links) > 0
        True

    5. Filter unique internal and external link hrefs:
        >>> internal_links_filtered = lc.filter_unique_hrefs(internal_links)
        >>> len(internal_links_filtered) > 0
        True

        >>> external_links_filtered = lc.filter_unique_hrefs(external_links)
        >>> len(external_links_filtered) > 0
        True

    6. Identify and match broken internal and external links:
        >>> internal_broken_links = lc.identify_broken_links(internal_links_filtered)
        >>> len(internal_broken_links) >= 0
        True

        >>> data_internal = lc.match_broken_links(internal_broken_links, internal_links)
        >>> len(data_internal) >= 0
        True

        >>> external_broken_links = lc.identify_broken_links(external_links_filtered)
        >>> len(external_broken_links) >= 0
        True

        >>> data_external = lc.match_broken_links(external_broken_links, external_links)
        >>> len(data_external) >= 0
        True
"""
import streamlit as st 
import links_check as lc
import pandas as pd
import settings

# Define page H1 and H2
st.title('SEO LINK AUDITOR')
st.header('Audit Your Website For Broken Links')

# Input domain name for website
DOMAIN_NAME = st.text_input("Domain Name", '', placeholder='example.com')
settings.DOMAIN_NAME = DOMAIN_NAME
if not settings.DOMAIN_NAME:
    domain_name_error = '<p style="font-family:Courier; color:Red; font-size: 12px;">Please provide the registered  domain name for your website ^^^</p>'
    st.write(domain_name_error, unsafe_allow_html=True)
else:
    domain_name_log = f'<p> The current domain name is <span  style="color:rgb(46, 154, 255);">{settings.DOMAIN_NAME}</span></p>'
    st.write(domain_name_log, unsafe_allow_html=True)

# Input homepage url for website
WEBSITE_URL = st.text_input("Full website url", '', placeholder='https://example.com')
settings.WEBSITE_URL = WEBSITE_URL
if not settings.WEBSITE_URL:
    web_url_error = '<p style="font-family:Courier; color:Red; font-size: 12px;">Please provide the homepage url for website ^^^</p>'
    st.write(web_url_error, unsafe_allow_html=True)
else:
    web_url_log = f'<p> The current website url is <span  style="color:rgb(46, 154, 255);">{settings.WEBSITE_URL}</span></p>'
    st.write(web_url_log, unsafe_allow_html=True)

# get unique urls / pages on website
try:
    unique_website_pages = lc.filter_unique_urls(settings.WEBSITE_URL)
    if len(unique_website_pages) == 0:
        error_message = '<p style="font-family:Courier; color:Red; font-size: 20px;">Unable to read sitemap</p>'
        st.markdown(error_message, unsafe_allow_html=True)
    else:
        dataframe = pd.DataFrame(list(unique_website_pages))
        print(type(unique_website_pages))
        st.write('WEBSITE PAGES - ', len(unique_website_pages))
        st.write(dataframe)
except Exception:
    st.write('Waiting for WEBSITE URL ...')

# get unique links in webpages
try:
    internal_links, external_links = lc.get_all_links(settings.DOMAIN_NAME, unique_website_pages)
    internal_links_filtered = lc.filter_unique_hrefs(internal_links)
    st.write('UNIQUE INTERNAL LINKS', len(internal_links_filtered))
    st.write(pd.DataFrame(internal_links_filtered))
    
    external_links_filtered = lc.filter_unique_hrefs(external_links)
    st.write('UNIQUE EXTERNAL LINKS', len(external_links_filtered))
    st.write(pd.DataFrame(external_links_filtered))
except Exception:
    st.write('Waiting for website pages...')

try:
    internal_broken_links = lc.identify_broken_links(internal_links_filtered)
    data = lc.match_broken_links(internal_broken_links, internal_links)
    st.write('INTERNAL BROKEN LINKS', len(internal_broken_links))
    st.write(data)
    
    external_broken_links = lc.identify_broken_links(external_links_filtered)
    data = lc.match_broken_links(external_broken_links, external_links)
    st.write('INTERNAL BROKEN LINKS', len(external_broken_links))
    st.write(data)
except Exception:
    st.write('Waiting for links...')
