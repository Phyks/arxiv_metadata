"""
This file contains all the arXiv-specific functions.
"""
import bbl
import io
import requests
import tarfile


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


def get_dois(eprint):
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
