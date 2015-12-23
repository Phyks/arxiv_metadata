#!/usr/bin/env python3
import os
import sys

# Local import
import arxiv
import bbl


def oa_from_doi(doi):
    """
    Get an OA version for a given DOI.
    """
    # http://beta.dissem.in/api/10.1088/1367-2630/17/9/093036
    pass


if __name__ == "__main__":
    import pprint
    if len(sys.argv) < 2:
        sys.exit("Usage: " + sys.argv[0] + " BBL_FILE|ARXIV_EPRINT.")

    if os.path.isfile(sys.argv[1]):
        pprint.pprint(bbl.get_dois(sys.argv[1]))
    else:
        pprint.pprint(arxiv.get_dois(sys.argv[1]))
