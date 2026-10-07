"""
Criterion 4 check: no chunk ends mid-sentence.

Counts chunks whose text doesn't end in sentence-ending punctuation (or a
closing quote/parenthesis). Re-run after any change to chunker.py:

    python check_chunks.py

Exits 0 if every chunk passes, 1 otherwise.
"""

import sys

from chunker import split_documents
from ingest import load_documents

ENDINGS = (".", "!", "?", '"', "'", ")", "”", "’")


def main() -> int:
    chunks = split_documents(load_documents())
    bad = [c for c in chunks if not c.text.rstrip().endswith(ENDINGS)]

    print(f"{len(chunks)} chunks; {len(bad)} end mid-sentence")
    for c in bad:
        print(f"  {c.source}: ...{c.text.rstrip()[-60:]!r}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

'''
It printed `138 chunks; 0 end mid-sentence` and exited 0.

Run it with `python check_chunks.py` from the project root, ideally after any change to chunker.py. 
If any chunk fails, it lists the source file and the last 60 characters of that chunk, and exits 1.
'''