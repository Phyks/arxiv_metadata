"""
This files contains all the functions to deal with bbl files.
"""
import math
import os
import requests
import subprocess

from . import doi
from . import regex
from . import tools


def clean_bibitem(bibitem):
    """
    Return a plaintext representation of the bibitem from the bbl file.

    Params:
        - bibitem is the text content of the bibitem.

    Returns a cleaned plaintext citation from the bibitem.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output = subprocess.check_output(["%s/opendetex/delatex" % (script_dir,),
                                      "-s"],
                                     input=bibitem.encode("utf-8"))
    output = output.decode("utf-8")
    output = tools.clean_whitespaces(output)
    return output


def parse(bbl):
    """
    Parse a *.bbl file to get a clean list of plaintext citations.

    Params:
        - bbl is either the path to the .bbl file or the content of a bbl file.

    Returns a list of cleaned plaintext citations.
    """
    # Handle path or content
    if os.path.isfile(bbl):
        with open(bbl, 'r') as fh:
            bbl_content = fh.read()
    else:
        bbl_content = bbl
    # Get a list of bibitems
    bibitems = regex.bibitems.split(bbl_content)[1:]
    bibitems = [regex.endthebibliography.sub("",
                                             i).strip() for i in bibitems]
    cleaned_bbl = []
    # Clean every bibitem
    for bibitem in bibitems:
        cleaned_bbl.append(clean_bibitem(bibitem))
    return cleaned_bbl


def get_dois(bbl_input):
    """
    Get the papers cited by the paper identified by the given DOI.

    Params:
        - bbl_input is either the path to the .bbl file or the content of a bbl
        file.

    Returns a dict of cleaned plaintext citations and their associated doi.
    """
    cleaned_citations_with_URLs = parse(bbl_input)
    dois = {}
    cleaned_citations = []
    # Try to get the DOI directly from the citation
    for citation in cleaned_citations_with_URLs[:]:
        # Get all the urls in the citation
        raw_urls = regex.urls.findall(citation)
        urls = [u.lower() for u in raw_urls]
        # Remove URLs in citation
        for url in raw_urls:
            citation = citation.replace(url, "")
        citation = tools.clean_whitespaces(citation)
        # Try to find an arXiv link
        arxiv_url = doi.extract_arxiv_links(urls)
        if arxiv_url:
            dois[citation] = arxiv_url
        # Try to find a DOI link
        doi_url = doi.extract_doi_links(urls)
        if doi_url:
            dois[citation] = doi_url
        # Try to find a direct match using a regex if links search failed
        if not doi_url and not arxiv_url:
            regex.match = doi.match_doi_or_arxiv(citation)
            if regex.match:
                print(regex.match)
                citation = citation.replace(regex.match[1], "")
                if regex.match[0] == "DOI":
                    dois[citation] = "http://dx.doi.org/%s" % (regex.match[1],)
                else:
                    dois[citation] = (
                        "http://arxiv.org/abs/%s" %
                        (regex.match[1].replace("arxiv:", ""),)
                    )
        # If no match found, stack it for next step
        if citation not in dois:
            cleaned_citations.append(citation)
    # Do batch of 10 papers, to prevent from the timeout of crossref
    for i in range(math.ceil(len(cleaned_citations) / 10)):
        lower_bound = 10 * i
        upper_bound = min(10 * (i + 1), len(cleaned_citations))
        r = requests.post("http://search.crossref.org/links",
                          json=cleaned_citations[lower_bound:upper_bound])
        for result in r.json()["results"]:
            if "doi" not in result:
                # If DOI is not found, try a direct query to get a DOI
                # r = requests.get("http://search.crossref.org/dois",
                #                  params={
                #                      'q': result["text"],
                #                      "sort": "score",
                #                      "rows": 1
                #                  })
                # doi_result = r.json()
                # if len(doi_result) > 0:
                #     dois[result["text"]] = doi_result[0]["doi"]
                # else:
                #     dois[result["text"]] = None
                dois[result["text"]] = None
            else:
                dois[result["text"]] = result["doi"]
    return dois
