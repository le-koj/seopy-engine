import streamlit as st 
import links_check as lc

APP_TITLE = st.title('SEOPY ENGINE')
HEAD_TITLE = st.header('Find Broken Links')

DOMAIN_NAME = st.text_input("Domain Name", 'example.com')
st.write('The current domain name is', DOMAIN_NAME)
lc.DOMAIN_NAME = DOMAIN_NAME

WEBSITE_URL = st.text_input("Full website url", 'http://example.com/')
st.write('The current website url is', WEBSITE_URL)

pages = lc.get_list_unique_pages(WEBSITE_URL)
st.write('WEBSITE PAGES', len(pages))
st.write(pages)

internal_links_raw, external_links_raw = lc.link_list(pages)

internal_unique_links = lc.get_unique_links(internal_links_raw)
st.write('UNIQUE INTERNAL LINKS', len(internal_unique_links))
st.write(internal_unique_links)

external_unique_links = lc.get_unique_links(external_links_raw)
st.write('UNIQUE EXTERNAL LINKS', len(external_unique_links))
st.write(external_unique_links)

internal_broken_links = lc.identify_broken_links(internal_unique_links)
st.write('INTERNAL BROKEN LINKS', len(internal_broken_links))
alt_internal_broken_links = lc.match_broken_links(internal_broken_links, internal_links_raw)
st.write(alt_internal_broken_links)

external_broken_links = lc.identify_broken_links(external_unique_links)
st.write('EXTERNAL BROKEN LINKS', len(external_broken_links))
alt_external_broken_links = lc.match_broken_links(external_broken_links, external_links_raw)
st.write(alt_external_broken_links)