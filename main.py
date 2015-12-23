#!/usr/bin/env python3
import io
import math
import os
import re
import requests
import subprocess
import sys
import tarfile


regex_urls = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
regex_bibitems = re.compile(r"\\bibitem\{.+?\}")
regex_endthebibliography = re.compile(r"\\end\{thebibliography}")

regex_doi = re.compile('(?<=doi)/?:?\s?[0-9\.]{7}/\S*[0-9]', re.IGNORECASE)
regex_doi_pnas = re.compile('(?<=doi).?10.1073/pnas\.\d+', re.IGNORECASE)
regex_doi_jsb = re.compile('10\.1083/jcb\.\d{9}', re.IGNORECASE)
regex_clean_doi = re.compile('^/')
regex_clean_doi_fabse = re.compile('^10.1096')
regex_clean_doi_jcb = re.compile('^10.1083')
regex_clean_doi_len = re.compile(r'\d\.\d')
regex_arXiv = re.compile(r'arXiv:\s*([\w\.\/\-]+)', re.IGNORECASE)


def replaceAll(text, dic):
    """Replace all the dic keys by the associated item in text"""
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def clean_whitespaces(text):
    """
    Remove double whitespaces and trailing . and , from text.
    """
    return ' '.join(text.strip().rstrip(".,").split())


def oa_from_doi(doi):
    """
    Get an OA version for a given DOI.
    """
    # http://beta.dissem.in/api/10.1088/1367-2630/17/9/093036
    pass


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
    output = clean_whitespaces(output)
    return output


def parse_bbl(bbl):
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
    bibitems = regex_bibitems.split(bbl_content)[1:]
    bibitems = [regex_endthebibliography.sub("",
                                             i).strip() for i in bibitems]
    cleaned_bbl = []
    # Clean every bibitem
    for bibitem in bibitems:
        cleaned_bbl.append(clean_bibitem(bibitem))
    return cleaned_bbl


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
        extractID = regex_doi.search(text.replace('&#338;', '-'))
        if not extractID:
            # PNAS fix
            extractID = regex_doi_pnas.search(text.
                                              replace('pnas', '/pnas'))
            if not extractID:
                # JSB fix
                extractID = regex_doi_jsb.search(text)
        if extractID:
            # If DOI extracted, clean it and return it
            cleanDOI = False
            cleanDOI = extractID.group(0).replace(':', '').replace(' ', '')
            if regex_clean_doi.search(cleanDOI):
                cleanDOI = cleanDOI[1:]
            # FABSE J fix
            if regex_clean_doi_fabse.search(cleanDOI):
                cleanDOI = cleanDOI[:20]
            # Second JCB fix
            if regex_clean_doi_jcb.search(cleanDOI):
                cleanDOI = cleanDOI[:21]
            if len(cleanDOI) > 40:
                cleanDOItemp = regex_clean_doi_len.sub('000', cleanDOI)
                reps = {'.': 'A', '-': '0'}
                cleanDOItemp = replaceAll(cleanDOItemp[8:], reps)
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
        extractID = regex_arXiv.search(text)
        if extractID:
            return ("arXiv", extractID.group(1))
    return None


def dois_from_bbl(bbl):
    """
    Get the papers cited by the paper identified by the given DOI.

    Params:
        - bbl is either the path to the .bbl file or the content of a bbl file.

    Returns a dict of cleaned plaintext citations and their associated doi.
    """
    cleaned_citations_with_URLs = parse_bbl(bbl)
    dois = {}
    cleaned_citations = []
    # Try to get the DOI directly from the citation
    for citation in cleaned_citations_with_URLs[:]:
        # Get all the urls in the citation
        raw_urls = regex_urls.findall(citation)
        urls = [u.lower() for u in raw_urls]
        # Remove URLs in citation
        for url in raw_urls:
            citation = citation.replace(url, "")
        citation = clean_whitespaces(citation)
        # Try to find an arXiv link
        arxiv_url = extract_arxiv_links(urls)
        if arxiv_url:
            dois[citation] = arxiv_url
        # Try to find a DOI link
        doi_url = extract_doi_links(urls)
        if doi_url:
            dois[citation] = doi_url
        # Try to find a direct match using a regex if links search failed
        if not doi_url and not arxiv_url:
            regex_match = match_doi_or_arxiv(citation)
            if regex_match:
                print(regex_match)
                citation = citation.replace(regex_match[1], "")
                if regex_match[0] == "DOI":
                    dois[citation] = "http://dx.doi.org/%s" % (regex_match[1],)
                else:
                    dois[citation] = (
                        "http://arxiv.org/abs/%s" %
                        (regex_match[1].replace("arxiv:", ""),)
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


def sources_from_arxiv(eprint):
    """
    Download sources on arXiv for a given preprint.

    Params:
        - eprint is the arXiv id (e.g. 1401.2910 or 1401.2910v1).

    Returns a TarFile object of the sources of the arXiv preprint.
    """
    r = requests.get("http://arxiv.org/e-print/%s" % (eprint,))
    file_object = io.BytesIO(r.content)
    return tarfile.open(fileobj=file_object)


def bbl_from_arxiv(eprint):
    """
    Get the .bbl files (if any) of a given preprint.

    Params:
        - eprint is the arXiv id (e.g. 1401.2910 or 1401.2910v1).

    Returns a list of the .bbl files as text (if any) or None.
    """
    tf = sources_from_arxiv(eprint)
    bbl_files = [i for i in tf.getmembers() if i.name.endswith(".bbl")]
    bbl_files = [tf.extractfile(member).read().decode(tarfile.ENCODING)
                 for member in bbl_files]
    return bbl_files


def dois_from_arxiv(eprint):
    """
    Get the .bbl files (if any) of a given preprint.

    Params:
        - eprint is the arXiv id (e.g. 1401.2910 or 1401.2910v1).

    Returns a dict of cleaned plaintext citations and their associated doi.
    """
    bbl_files = bbl_from_arxiv(eprint)
    dois = {}
    for bbl in bbl_files:
        dois.update(dois_from_bbl(bbl))
    return dois


if __name__ == "__main__":
    import pprint
    if len(sys.argv) < 2:
        sys.exit("Usage: " + sys.argv[0] + " BBL_FILE|ARXIV_EPRINT.")

    if os.path.isfile(sys.argv[1]):
        pprint.pprint(dois_from_bbl(sys.argv[1]))
    else:
        pprint.pprint(dois_from_arxiv(sys.argv[1]))
