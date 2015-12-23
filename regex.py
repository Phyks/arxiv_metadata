"""
This file contains all the regex used across the app.
"""
import re

urls = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
bibitems = re.compile(r"\\bibitem\{.+?\}")
endthebibliography = re.compile(r"\\end\{thebibliography}")

doi = re.compile('(?<=doi)/?:?\s?[0-9\.]{7}/\S*[0-9]', re.IGNORECASE)
doi_pnas = re.compile('(?<=doi).?10.1073/pnas\.\d+', re.IGNORECASE)
doi_jsb = re.compile('10\.1083/jcb\.\d{9}', re.IGNORECASE)
clean_doi = re.compile('^/')
clean_doi_fabse = re.compile('^10.1096')
clean_doi_jcb = re.compile('^10.1083')
clean_doi_len = re.compile(r'\d\.\d')
arXiv = re.compile(r'arXiv:\s*([\w\.\/\-]+)', re.IGNORECASE)
