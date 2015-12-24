"""
This file contains all the arXiv-specific functions.
"""
import io
import requests
import tarfile
import xml.etree.ElementTree

from . import bbl


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


def get_cited_dois(eprint):
    """
    Get the .bbl files (if any) of a given preprint.

    Params:
        - eprint is the arXiv id (e.g. 1401.2910 or 1401.2910v1).

    Returns a dict of cleaned plaintext citations and their associated doi.
    """
    bbl_files = bbl_from_arxiv(eprint)
    dois = {}
    for bbl_file in bbl_files:
        dois.update(bbl.get_dois(bbl_file))
    return dois


def get_arxiv_eprint_from_doi(doi):
    """
    Get the arXiv eprint id for a given DOI.

    Params:
        - doi is the DOI of the resource to look for.

    Returns the arXiv eprint id, or None if not found.
    """
    r = requests.get("http://export.arxiv.org/api/query",
                     params={
                         "search_query": "doi:%s" % (doi,),
                         "max_results": 1
                     })
    e = xml.etree.ElementTree.fromstring(r.content)
    for entry in e.iter("{http://www.w3.org/2005/Atom}entry"):
        id = entry.find("{http://www.w3.org/2005/Atom}id").text
        return id.replace("http://arxiv.org/abs/", "")
    return None


def get_doi(eprint):
    """
    Get the associated DOI for a given arXiv eprint.

    Params:
        - eprint is the arXiv eprint id.

    Returns the DOI if any, or None.
    """
    r = requests.get("http://export.arxiv.org/api/query",
                     params={
                         "id_list": eprint,
                         "max_results": 1
                     })
    e = xml.etree.ElementTree.fromstring(r.content)
    for entry in e.iter("{http://www.w3.org/2005/Atom}entry"):
        doi = entry.find("{http://arxiv.org/schemas/atom}doi")
        if doi is not None:
            return doi.text
    return None
