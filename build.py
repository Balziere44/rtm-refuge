# -*- coding: utf-8 -*-
"""Build the whole site, in the order the steps depend on each other.

    python build.py

The order is not cosmetic: build_meta and build_search both READ the pages the
earlier scripts produce, so they have to run after them or they describe a
site that no longer exists.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    "build_codex.py",     # the glossary, and the term table the others use
    "build.py",           # home and the short pages
    "build_docs.py",      # start / mechanics / gear / world
    "build_classes.py",   # the tree and every class page
    "build_database.py",  # the item and monster database
    "build_meta.py",      # sitemap, robots, llms.txt
    "build_search.py",    # the search index
    "check.py",           # and refuse to finish if anything is wrong
    "check_i18n.py",
]

for step in STEPS:
    print("==", step)
    result = subprocess.call([sys.executable, os.path.join(HERE, "tools", step)])
    if result:
        sys.exit(result)
