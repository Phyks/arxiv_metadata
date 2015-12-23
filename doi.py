"""
This file contains all the DOI-related functions.
"""
import requests

import regex
import tools


def extract_doi_links(urls):
    """
    Try to find a DOI from a given list of URLs.
    """
    doi_urls = [url for url in urls if "/doi/" in url]
    if len(doi_urls) > 0:
        return ("http://dx.doi.org" +
                doi_urls[0][doi_urls[0].find("/doi/") + 4:])
    else:
        return None


def extract_arxiv_links(urls):
    """
    Try to find an arXiv link from a given list of URLs.
    """
    arxiv_urls = [url for url in urls if "://arxiv.org" in url]
    if len(arxiv_urls) > 0:
        return arxiv_urls[0]
    else:
        return None


def match_doi_or_arxiv(text, only=["DOI", "arXiv"]):
    """
    Search for a valid article ID (DOI or ArXiv) in the given text
    (regex-based).

    Returns a tuple (type, first matching ID) or None if not found.
    From : http://en.dogeno.us/2010/02/release-a-python-script-for-organizing-scientific-papers-pyrenamepdf-py/
    and https://github.com/minad/bibsync/blob/3fdf121016f6187a2fffc66a73cd33b45a20e55d/lib/bibsync/utils.rb
    """
    text = text.lower()
    # Try to extract DOI
    if "DOI" in only:
        extractID = regex.doi.search(text.replace('&#338;', '-'))
        if not extractID:
            # PNAS fix
            extractID = regex.doi_pnas.search(text.
                                              replace('pnas', '/pnas'))
            if not extractID:
                # JSB fix
                extractID = regex.doi_jsb.search(text)
        if extractID:
            # If DOI extracted, clean it and return it
            cleanDOI = False
            cleanDOI = extractID.group(0).replace(':', '').replace(' ', '')
            if regex.clean_doi.search(cleanDOI):
                cleanDOI = cleanDOI[1:]
            # FABSE J fix
            if regex.clean_doi_fabse.search(cleanDOI):
                cleanDOI = cleanDOI[:20]
            # Second JCB fix
            if regex.clean_doi_jcb.search(cleanDOI):
                cleanDOI = cleanDOI[:21]
            if len(cleanDOI) > 40:
                cleanDOItemp = regex.clean_doi_len.sub('000', cleanDOI)
                reps = {'.': 'A', '-': '0'}
                cleanDOItemp = tools.replaceAll(cleanDOItemp[8:], reps)
                digitStart = 0
                for i in range(len(cleanDOItemp)):
                    if cleanDOItemp[i].isdigit():
                        digitStart = 1
                        if cleanDOItemp[i].isalpha() and digitStart:
                            break
                cleanDOI = cleanDOI[0:(8+i)]
            return ("DOI", cleanDOI)
    # Else, try to extract arXiv
    if "arXiv" in only:
        extractID = regex.arXiv.search(text)
        if extractID:
            return ("arXiv", extractID.group(1))
    return None


def get_oa_version(doi):
    """
    Get an OA version for a given DOI.

    Params:
        - doi is a DOI or a dx.doi.org link.

    Returns the URL of the OA version of the given DOI, or None.
    """
    # If DOI is a link, truncate it
    if "dx.doi.org" in doi:
        doi = doi[doi.find("dx.doi.org") + 11:]
    r = requests.get("http://beta.dissem.in/api/%s" % (doi,))
    oa_url = None
    if r.status_code == requests.codes.ok:
        result = r.json()
        if("status" in result and
           "paper" in result and
           result["status"] == "ok" and
           "pdf_url" in result["paper"]):
            oa_url = result["paper"]["pdf_url"]
    return oa_url
