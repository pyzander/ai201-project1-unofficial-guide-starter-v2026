"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE # 800 # defined in config.py # characters per chunk
    overlap = overlap or config.CHUNK_OVERLAP # 120 # characters shared between neighbouring chunks

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


# ─── The starter's version of split_documents, kept for reference ───────────
#
# def split_documents(documents: list[Document]) -> list[Chunk]:
#     """
#     Split documents into chunks. ⚠️ REPLACE THE BODY OF THIS IN MILESTONE 3.

#     Right now it just calls the fallback. That is the plain, generic behaviour
#     the brief is talking about.

#     When you write your own strategy, set `produced_by` to
#     "chunker.py::split_documents" so your README's Sample Chunks section names
#     the right function. `app.py chunks` prints that string for you.

#     Things worth thinking about before you write any code:
#       - Are your documents short posts or long guides?
#       - Is the useful information in one sentence, or spread over a paragraph?
#       - Would splitting on paragraph breaks keep more thoughts intact than
#         splitting on a character count?
#     """
#     return fallback_split(documents)


TITLE_MAX = 80   # a heading line, not a sentence


def split_documents(documents: list[Document]) -> list[Chunk]:
    # return fallback_split(documents)
    """
    A document contains 1-3 paragraphs. 
    Chunk = Heading + Paragraph. 
    Adding the Heading to each paragraph allows the chunk to stand on its own. 
    According to `python app.py index`, 183 chunks, 167 characters on average (shortest 63, longest 397)

    One chunk per paragraph, with the document's heading carried onto each.

    Followed fallback_split() as reference for writing this function 

    campus_life documents are a short heading followed by one to four
    paragraphs, and the fact that answers a question is usually a single
    sentence. Splitting on the blank lines isolates that sentence. Prefixing
    the heading is what makes it retrievable: "Expect 8 to 10 hours a week
    outside class." names no course on its own, and four different courses
    have a near-identical line.

    Short paragraphs are deliberately left alone rather than merged into their
    neighbours. 124 of the 183 body paragraphs here are under 150 characters,
    and the shortest of them are the most answerable chunks in the corpus.
    """
    chunks: list[Chunk] = []

    for doc in documents:
        blocks = [b.strip() for b in doc.text.split("\n\n") if b.strip()]

        first = blocks[0]
        is_heading = (
            len(blocks) > 1 and len(first) <= TITLE_MAX and not first.endswith(".")
        )
        title = first if is_heading else ""
        bodies = blocks[1:] if is_heading else blocks

        for index, body in enumerate(bodies):
            chunks.append(
                Chunk(
                    text=f"{title}\n\n{body}" if title else body, # use ternary operator and include title with spacing if there is one and just body if there is no title  
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
