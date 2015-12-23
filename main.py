#!/usr/bin/env python3
import math
import os
import re
import requests
import subprocess
import sys


def oa_from_doi(doi):
    """
    Get an OA version for a given DOI.
    """
    # http://beta.dissem.in/api/10.1088/1367-2630/17/9/093036
    pass


def clean_bibitem(bibitem):
    """
    Return a plaintext representation of the bibitem from the bbl file.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output = subprocess.check_output([script_dir + "/opendetex/delatex", "-s"],
                                     input=bibitem.encode("utf-8"))
    output = output.decode("utf-8")
    output = ' '.join(output.strip().rstrip(".,").split())
    return output


def parse_bbl(bbl_file):
    with open(bbl_file, 'r') as fh:
        bbl_content = fh.read()
    bibitems = re.split(r"\\bibitem\{.+?\}", bbl_content)[1:]
    bibitems = [re.sub(r"\\end\{thebibliography}",
                       "",
                       i).strip() for i in bibitems]
    cleaned_bbl = []
    for bibitem in bibitems:
        cleaned_bbl.append(clean_bibitem(bibitem))
    return cleaned_bbl


def dois_from_bbl(bbl_file):
    """
    Get the papers cited by the paper identified by the given DOI.
    """
    cleaned_citations = parse_bbl(bbl_file)
    dois = {}
    for i in range(math.ceil(len(cleaned_citations) / 10)):
        lower_bound = 10 * i
        upper_bound = min(10 * (i + 1), len(cleaned_citations))
        r = requests.post("http://search.crossref.org/links",
                          json=cleaned_citations[lower_bound:upper_bound])
        for result in r.json()["results"]:
            if "doi" not in result:
                dois[result["text"]] = None
            else:
                dois[result["text"]] = result["doi"]
    return dois


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: " + sys.argv[0] + " BBL_FILE.")

    import pprint
    pprint.pprint(dois_from_bbl(sys.argv[1]))
