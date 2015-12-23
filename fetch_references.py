#!/usr/bin/env python3
import os
import sys

# Local import
from ..reference_fetcher import arxiv
from ..reference_fetcher import bbl


if __name__ == "__main__":
    import pprint
    if len(sys.argv) < 2:
        sys.exit("Usage: " + sys.argv[0] + " BBL_FILE|ARXIV_EPRINT.")

    if os.path.isfile(sys.argv[1]):
        pprint.pprint(bbl.get_dois(sys.argv[1]))
    else:
        pprint.pprint(arxiv.get_dois(sys.argv[1]))
