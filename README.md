# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments

> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

i picked the corpus campus_life. As stated in corpus_info.py -> BLURBS, (or if you run `python app.py corpora`) That corpus contains "Short posts about student life. ~88 documents of 1–3 paragraphs." (Actually 7 documents contain 4 paragraphs: housing_aldridge_hall.txt, housing_calder_annexe.txt, housing_fenwick_court.txt, housing_innisfree_hall.txt, housing_morrow_house.txt, housing_old_brewhouse.txt, and housing_tamsin_court.txt.) such as The system answers questions on student life such as when to declare a major and thoughts on certain classes, dining halls and housing. 

You can run this by doing 

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

This creates a virtual environment and your .env file. You need to add to .env your environment your Google Gemini Key which can be copied and pasted from https://aistudio.google.com/api-keys
Then run `python test.py` to test the environment and then `python app.py index` and after that you can ask it questions like below. 

```
python test.py

python app.py index
python app.py ask "is the housing lottery random?"


```

## Chunking Strategy

For campus_life, I split on paragraphs instead of documents. According to `python app.py index`, 183 chunks, 167 characters on average (shortest 63, longest 397), produced by chunker.py::split_documents
Because I know that a document is way under 800 characters and each document contains 1-4 paragraphs of a couple sentences each, bounding chunk size and overlap wasn't necessary. But if I did have one, perhaps 60 and and 10 would be good. The chunk size and overlap variables aren't really relevant for campus_life. I should have chose a different corpus. 
<!-- 
     **Chunk size:**
     **Overlap:**

     What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->



## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

The below was produced by `python app.py chunks` which prints out 5 sample chunks and asks `For each one, ask: could someone answer a question using only this, without reading what came before or after?`. 

== Chunk 1  |  source: admin_add_drop_deadline.txt#0  |  produced by: 
chunker.py::split_documents == On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.

== Chunk 2  |  source: course_cs_340_exams.txt#1  |  produced by: chun
ker.py::split_documents == CS 340 Databases — assessment

Start the term project in week three, not week eight; everyone learns this the hard way.

== Chunk 3  |  source: course_phys_130_workload.txt#0  |  produced by:
chunker.py::split_documents == Workload for PHYS 130 Mechanics

People keep asking so: 7 hours a week, plus 3 on lab weeks. That's real time, not optimistic time.

== Chunk 4  |  source: dining_verrill_street_grill_followup.txt#1  |  
produced by: chunker.py::split_documents == Re: Verrill Street Grill

Also worth saying: one register, so the queue is a single line no matter how busy. Nobody tells you this at orientation.

== Chunk 5  |  source: housing_morrow_house.txt#1  |  produced by: chu
nker.py::split_documents == Morrow House — what it's actually like

The good: cheapest housing tier by about $900 a year, and the singles are real singles.

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**

**Answer:**

```
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
| -------- | ---------- | ------------- |
|          |            |               |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**

I asked Claude how to check the size of each chunk. This was before I reached that part in the readme. it said use 'python chunker.py	' It also said  "2. Per-chunk sizes There's nothing built in for this, so a one-liner. Let me run it on your corpus." And I let it run this bash command 

```

python3 -c "

from ingest import load_documents

from chunker import split_documents, describe

chunks = split_documents(load_documents())

print(describe(chunks)); print()

for c in sorted(chunks, key=lambda c: len(c.text))[:5]:

    print(f'{len(c.text):5d}  {c.label}')

print('  ...')

for c in sorted(chunks, key=lambda c: len(c.text))[-5:]:

    print(f'{len(c.text):5d}  {c.label}')

"

```

which produced 

```

88 chunks, 317 characters on average (shortest 178, longest 549), produced by chunker.py::fallback_split

  178  course_hist_118_exams.txt#0

  186  course_math_220_exams.txt#0

  191  course_biol_160_exams.txt#0

  194  course_phys_130_exams.txt#0

  205  course_engl_205_exams.txt#0

  ...

  426  course_cs_340.txt#0

  430  housing_calder_annexe.txt#0

  461  housing_morrow_house.txt#0

  516  housing_innisfree_hall.txt#0

  549  housing_old_brewhouse.txt#0

```

It also said a bunch of super irrelevant considerations I didn't understand. 

I wish it just told me to do `python app.py index`

**2.**

I asked Claude how to print out chunks. 

It told me (part of the reply copied below):

That prints 4 chunks spread across the corpus, each with its source label and the produced_by string — both of which the README's Sample Chunks section asks for.

This doesn't need the index rebuilt. cmd_chunks calls load_documents() and split_documents() directly and never touches Chroma, so it reflects your new chunker right now. (app.py retrieve and app.py ask do need app.py index first, since those query the stored vectors.)

Three variants:

| Command                                                    | What you get                              |
| ---------------------------------------------------------- | ----------------------------------------- |
| python app.py chunks -n 10                                 | 10 chunks sampled across the whole corpus |
| python app.py chunks --from-doc course_cs_210_workload.txt | every chunk from one document             |
| python app.py chunks --indices 0,4,8                       | the chunks at those exact positions       |

The --from-doc one is the most useful to you right now — it's how you show the before/after on a single document for Milestone 3. That file should now give you two chunks (#0 and #1) where the starter gave one, with the heading on both.

For the size numbers rather than the text:

python chunker.py

That prints the one-line summary — count, mean, shortest, longest. You should see 183 chunks, 167 characters on average and produced by chunker.py::split_documents. If it still says 88 chunks or names fallback_split, the new code isn't being reached.

I wish it plainly told me `python app.py chunks` as stated in RUNNING.md

Honestly, I need to stop asking Claude how to run stuff because it overcomplicates it and it is easier to go look at RUNNING.md myself. I think since there are so many files, it doesn't know that the best place to look is RUNNING.md

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion | Verdict | How I decided |
| --- | --------- | ------- | ------------- |
| 1   |           |         |               |
| 2   |           |         |               |
| 3   |           |         |               |
| 4   |           |         |               |
| 5   |           |         |               |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->