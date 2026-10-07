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

i picked the corpus campus_life. As stated in corpus_info.py -> BLURBS, (or if you run `python app.py corpora`) That corpus contains "Short posts about student life. ~88 documents of 1–3 paragraphs." (Actually 7 documents contain 4 paragraphs: housing_aldridge_hall.txt, housing_calder_dannexe.txt, housing_fenwick_court.txt, housing_innisfree_hall.txt, housing_morrow_house.txt, housing_old_brewhouse.txt, and housing_tamsin_court.txt.) such as The system answers questions on student life such as when to declare a major and thoughts on certain classes, dining halls and housing. 

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

**Chunk size:** 350 characters — the `MIN_SPLIT` threshold in `chunker.py`. Documents at or above it are split one chunk per paragraph; documents below it stay whole. The chunks this produces are 63 to 397 characters, 213 on average, 138 in total, produced by `chunker.py::split_documents`. This is not a fixed chunk size and not same definition as the default function. 

**Overlap:** 0 characters of body text. Neighbouring chunks share no sentences. They do share the document heading — 10 to 40 characters, copied onto every chunk of a split document — which is a deliberate constant overlap doing the job overlap normally does: keeping a chunk readable once it has been cut away from its neighbours.

**What I noticed that motivated these numbers.** My longest document is 549 characters and the default `CHUNK_SIZE` is 800, so `fallback_split` never cut anything — 88 documents in, 88 identical chunks out, every label ending `#0`, and the 120-character overlap never triggered once. Length-based splitting was a no-op on this corpus. That is why I split on structure instead: every campus_life document is a short heading followed by one to four paragraphs, and the fact that answers a question is usually a single sentence sitting in one of them.

The heading prefix exists because paragraphs here don't name their own subject. The second paragraph of `course_cs_210_workload.txt` reads "It's front-loaded — the first month is heavier than the rest," which never says CS 210. Split without the heading, that chunk is unreachable by anyone asking about the course.

**I changed my mind partway through.** My first version split every document on paragraphs, giving 183 chunks. That made retrieval worse on "Which halls are quiet?". The seven `housing_*_noise.txt` files each contain a verdict paragraph plus a paragraph about the library being open until 2am, and that second paragraph is byte-identical across all seven. Split apart, the library paragraph embeds closer to the question than the verdict does — rank 4 versus rank 13 for Tamsin Court — so the top five filled up with near-duplicate lures and the actual answer never reached the model. The answer named one hall; the starter's chunker had named three.

Keeping short documents whole fixes it, because the lure and the verdict stay in the same chunk. I set the threshold at 350 by measuring: the seven affected files are 266 to 324 characters, and the documents that genuinely need splitting start at 396. 350 sits in that gap rather than being a round number I liked. After the change, the same question returns five distinct halls at top-5 with no lure chunks at all. Not splitting all the documents and having a char count gives us 138 chunks, 213 characters on average (shortest 63, longest 397), produced by chunker.py::split_documents. 

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

```
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

```

Later changes in code (adding the Min_split into the function during milestone 4) produced these chunks. (I kept the previous sample chunks above so you can see the differences in sample chunks) The above always produces one paragraph each while the below can have multiple paragraphs per chunk: 

```
python app.py chunks
138 chunks total. Showing 5, spread across the corpus.

Paste these into your README under Sample Chunks. The rubric asks
for the source file and the function that produced them — both are
printed for you below.

======================================================================
Chunk 1  |  source: admin_add_drop_deadline.txt#0  |  produced by: chunker.py::split_documents
======================================================================
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.

======================================================================
Chunk 2  |  source: course_cs_340.txt#0  |  produced by: chunker.py::split_documents
======================================================================
CS 340 Databases

I'm a junior and I've done this twice now. Format is lecture twice a week plus a project that runs the whole term. Assessment: one midterm and a final, both open-book. Lightly curved, usually two or three points.

======================================================================
Chunk 3  |  source: course_phys_130.txt#2  |  produced by: chunker.py::split_documents
======================================================================
PHYS 130 Mechanics

The one piece of advice: the lab practical is worth 20% and almost nobody prepares for it.

======================================================================
Chunk 4  |  source: dining_verrill_street_grill_followup.txt#0  |  produced by: chunker.py::split_documents
======================================================================
Re: Verrill Street Grill

Adding to what people have said about Verrill Street Grill. The wait figure of up to 30 minutes on Friday evenings matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

======================================================================
Chunk 5  |  source: housing_innisfree_hall_noise.txt#0  |  produced by: chunker.py::split_documents
======================================================================
Noise levels in Innisfree Hall

Asked about this a lot so writing it down. Moderate; the building is l-shaped and the short wing is much quieter.

If you're someone who needs quiet to work, the library is open until 2am during term and that's what most people in this building end up doing.
```

## Milestone 4 commentary 

Here is what  `python app.py ask "Which halls are quiet?"` when it uses chunker.py::split_documents (return fallback_split(documents) is commented out )

```
python app.py index
python app.py ask "Which halls are quiet?"             
  (best distance 0.362, cutoff 0.6)

According to housing_innisfree_hall_noise.txt, Innisfree Hall has moderate noise levels, but the short wing of the l-shaped building is much quieter.

Sources retrieved: housing_aldridge_hall_noise.txt, housing_fenwick_court_noise.txt, housing_innisfree_hall_noise.txt, housing_tamsin_court_noise.txt

1 model calls this session, 438 tokens (401 in, 37 out)
```

The original code uses the chunker.py::fallback_split() 
(return fallback_split(documents) is NOT commented out )

```
python app.py index
python app.py ask "Which halls are quiet?"
  (best distance 0.370, cutoff 0.6)

Based on the provided documents:
- **Tamsin Court** is described as quiet structurally due to concrete floors between units (`housing_tamsin_court_noise.txt`).
- **Aldridge Hall** has quiet floors on levels 3 and 4 that are genuinely enforced (`housing_aldridge_hall_noise.txt`).
- **Innisfree Hall** is described as having moderate noise levels, with the short wing being much quieter (`housing_innisfree_hall_noise.txt`).

Sources retrieved: housing_aldridge_hall_noise.txt, housing_fenwick_court_noise.txt, housing_innisfree_hall_noise.txt, housing_old_brewhouse_noise.txt, housing_tamsin_court_noise.txt

1 model calls this session, 641 tokens (534 in, 107 out)
```

My above answer is incomplete as compared to the answer given orignally. Why is this the case? I wondered. 

So I know `app.py` gives us `python app.py retrieve "question"    show distances, no answer (Milestone 4)`
so I ran `python3 app.py retrieve "Which halls are quiet?"` and got 

```
Question: Which halls are quiet?

#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.3623     housing_innisfree_hall_noise.txt Noise levels in Innisfree Hall  If you're someone wh...
2   0.3876     housing_aldridge_hall_noise.txt  Noise levels in Aldridge Hall  If you're someone who...
3   0.4106     housing_innisfree_hall_noise.txt Noise levels in Innisfree Hall  Asked about this a l...
4   0.4478     housing_tamsin_court_noise.txt   Noise levels in Tamsin Court  If you're someone who ...
5   0.4525     housing_fenwick_court_noise.txt  Noise levels in Fenwick Court  If you're someone who...

Gate: best distance 0.362 is under the 0.6 cutoff

Lower is better. 0.3 is a close match, 0.9 is unrelated.
Milestone 4: run your five questions, then the five in OUT_OF_SCOPE
that your documents clearly don't cover, and look for the gap
between the two groups. Your cutoff goes in that gap.
```

This shows duplicate sources ate up my top-5 slows because top_k counts chunks which are now paragraphs instead of documents. 
Under fallback_split, one document = one chunk, so five slots meant 5 different halls. 
Each of my chunks carried less text. 
My code is better at precise questiosn found in one sentence such as How many hours of work a week is CS 210 (distance of .3222 instead of .3713) instead of questions that cover multiple documents such as "Which halls are quiet?"

The original code gave us: 

```
python3 app.py retrieve "Which halls are quiet?"

Question: Which halls are quiet?

#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.3703     housing_innisfree_hall_noise.txt Noise levels in Innisfree Hall  Asked about this a l...
2   0.4023     housing_old_brewhouse_noise.txt  Noise levels in Old Brewhouse  Asked about this a lo...
3   0.4316     housing_fenwick_court_noise.txt  Noise levels in Fenwick Court  Asked about this a lo...
4   0.4343     housing_tamsin_court_noise.txt   Noise levels in Tamsin Court  Asked about this a lot...
5   0.4524     housing_aldridge_hall_noise.txt  Noise levels in Aldridge Hall  Asked about this a lo...
```

Fortunately, my distance did get better which means retrieval got more precise. 

`python3 app.py retrieve "Which halls are quiet?" --top-k 10`
takes in more chunks 

```
python3 app.py retrieve "Which halls are quiet?" --top-k 16                  

Question: Which halls are quiet?

#   distance   source                           preview
----------------------------------------------------------------------------------------------------
1   0.3623     housing_innisfree_hall_noise.txt Noise levels in Innisfree Hall  If you're someone wh...
2   0.3876     housing_aldridge_hall_noise.txt  Noise levels in Aldridge Hall  If you're someone who...
3   0.4106     housing_innisfree_hall_noise.txt Noise levels in Innisfree Hall  Asked about this a l...
4   0.4478     housing_tamsin_court_noise.txt   Noise levels in Tamsin Court  If you're someone who ...
5   0.4525     housing_fenwick_court_noise.txt  Noise levels in Fenwick Court  If you're someone who...
6   0.4526     housing_old_brewhouse_noise.txt  Noise levels in Old Brewhouse  Asked about this a lo...
7   0.4558     housing_old_brewhouse_noise.txt  Noise levels in Old Brewhouse  If you're someone who...
8   0.4633     housing_morrow_house_noise.txt   Noise levels in Morrow House  If you're someone who ...
9   0.4734     housing_aldridge_hall_noise.txt  Noise levels in Aldridge Hall  Asked about this a lo...
10  0.4743     housing_fenwick_court_noise.txt  Noise levels in Fenwick Court  Asked about this a lo...
```

I went from 88 chunks to 183. Top-5 was 5.7% of the corpus before; it's 2.7% now. I halved my chunk size and had to raise top-k to compensate.
But when I asked "Which halls are quiet?" I noticed my answer didn't include - `**Tamsin Court** is quiet structurally due to concrete floors between units (`housing_tamsin_court_noise.txt`)`. and to include it, I would have to change my top_k from 10 to 13 to compensate. Raising it to 13 fixes it but it takes in noise and uses more tokens. 905 tokens (802 in, 103 out).
Originally, it took in 642 tokens (534 in, 108 out)

My second option is to split documents above a length threshold. The _noise files are short two-paragraph documents that were already coherent single chunks — splitting them gained nothing and cost the me the paragraph with the relevant information The 4-paragraph housing files genuinely needed splitting. A rule like "split only if the document exceeds N characters" keeps both behaviors. Noise files top out at 324, the four-paragraph files start at 396. A threshold at 350 separates them so I used that so files above that size would get split up into paragraphs and files below that size wouldn't. To adjust the top-k accordingly after this change, i changed the top-k to 8.

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

` python app.py ask "What do students say about CS 210?" `

**Question:**
What do students say about CS 210?

**Answer:**

```
(best distance 0.391, cutoff 0.6)

Based on the provided documents, students say the following about CS 210:
* You should do the labs even though they are only worth 10%, because the exams reuse the lab problems (*course_cs_210.txt* and *course_cs_210_exams.txt*).
* You should expect 8 to 10 hours a week outside of class, which is "real time, not optimistic time," and the workload is front-loaded with the first month being heavier (*course_cs_210.txt* and *course_cs_210_workload.txt*).

Sources retrieved: course_cs_210.txt, course_cs_210_exams.txt, course_cs_210_workload.txt, course_cs_340.txt, course_cs_340_exams.txt, course_engl_205.txt

1 model calls this session, 789 tokens (654 in, 135 out)
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question                                    | In corpus? | Best distance |
| ------------------------------------------- | ---------- | ------------- |
|                                             |            |               |
| Which halls are quiet?                      | yes        | 0.370         |
| Which halls are loud?                       | yes        | 0.422         |
| What do students say about CS 210?          | yes        | 0.391         |
| What time is dinner served in dining halls? | yes        | 0.385         |
| What do students say about the libary?      | yes        | 0.496         |

| Question                                                    | In corpus? | Best distance |
| ----------------------------------------------------------- | ---------- | ------------- |
| What is the capital of Mongolia?                            | No         | 0.825         |
| How do I change the oil in a diesel engine?                 | No         | 0.923         |
| Who won the 1994 World Cup?                                 | No         | 0.886         |
| What is the recommended dosage of ibuprofen for a headache? | No         | 0.849         |
| How do I write a for loop in Rust?                          | No         | 0.8635        |

After changing the top-k, I tested the above, then I used that information to check the relevance cutoff. 
The 0.6 is well placed but if I wanted to be more stringent, I can do 0.5. 

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

## Notes 

Now we will do the testing portion of the project. We will find out how good our acceptance criteria is. 

**Stretch feaure achieved**: multiple measured improvements were made but put in the same run log. 

## Set up 

Info taken from [RUNNING.md](RUNNING.md) for easy access 

```py
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your key into .env
python test.py

python app.py corpora                     # see what's available
python app.py index                       # build the search index
python app.py ask "is the housing lottery random?"

python run_eval.py --label before #| Runs every test question three times, puts every `OUT_OF_SCOPE` question through the gate, and writes a run log — **unit 2** |

python run_eval.py --label before # you can do it without the label but i think they want it to differenciate your runs 
python run_eval.py --label after
#  Unit 2 | Run the test, fix one thing, re-run | `

```

I decided not to create a scorer.py file at first becaue I was a little confused on the differences between the two tables and needed to develop my understanding on how to score so I manually filled it out but I may go back in change it. 

## Run Log — Before (Milestone 1) 

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

1. For at least 4 of my 5 test questions, the retrieved chunks include one that contains the answer.
2. Every answer the system produces names at least one source document.
3. When I ask a question my documents clearly don't cover, the relevance gate stops it and the system returns "I don't have enough information about that" — in at least 4 of 5 tries.
4. All chunk sizes should be above 50 characters.
5. For at least 4 of my 5 test questions, if it generates an answer, the all the documents the answer names is one that actually contains the answer

| Criterion                              | Target | Run 1          | Run 2   | Run 3   | Verdict |
| -------------------------------------- | ------ | -------------- | ------- | ------- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5            | 5/5     | 5/5     | MET     |
| 2. Every answer names a source         | 5 of 5 | 5/5            | 4/5     | 5/5     | MISSED  |
| 3. Gate stops out-of-corpus questions  | 4 of 5 | 5/5            | 5/5     | 5/5     | MET     |
| 4. Limit too small chunk size          | 5 of 5 | 138/138 chunks | 138/138 | 138/138 | MET     |
| 5. Named sources are the right sources | 4 of 5 | 4/5            | 4/5     | 4/5     | MET     |

Criterion 2: it is MISSED because run 2 had 4 of 5 answers naming a source. The Q5 refusal named none.

Criterion 4: the target says "5 of 5", but the criterion is about chunks, so I used 138/138 instead.

Criterion 5: run 2 shows 4/5 because I counted the Q5 refusal as not applicable. If you count it as a pass, it would be 5/5, and the verdict stays MET.

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

All text below is copied from `results/run_2026-10-07_0434_before.md`, written by `run_eval.py::main` (cutoff 0.6, top-k 8, caching off). Retrieval comes from `store.py::search`, the gate from `gate.py::check`, and the answer text from `generate.py::answer_from_chunks`.

**Criterion 1: retrieved chunks contain the answer.** Question: "What do students say about wait times at Commons during lunch?", run 1.

```
- Best distance: 0.3080 (passed the gate)
- Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons.txt, dining_kestrel_commons_followup.txt, dining_north_kitchen_followup.txt, dining_pellew_dining_hall_followup.txt, dining_the_atrium_followup.txt, dining_the_ridgeway_cafe_followup.txt, dining_verrill_street_grill_followup.txt

Based on the documents, students state that the wait time at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00, and under 5 minutes before 11:45 (from `dining_kestrel_commons.txt`).
```

**Criterion 2: every answer names a source.** The answer in the first block above names `dining_kestrel_commons.txt`. The one answer that named none, "What is the parking situation like near student housing?", run 2:

```
Based on the provided documents, there is no information about the parking situation near student housing. I don't have enough information to answer the question.
```

**Criterion 3: the gate stops out-of-corpus questions.** Produced by `run_eval.py::check_out_of_scope` (cutoff 0.6). Refused 5 of 5.

```
| Out-of-scope question                                       | Best distance | Gate    |
| ----------------------------------------------------------- | ------------- | ------- |
| What is the capital of Mongolia?                            | 0.825         | refused |
| How do I change the oil in a diesel engine?                 | 0.923         | refused |
| Who won the 1994 World Cup?                                 | 0.886         | refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.849         | refused |
| How do I write a for loop in Rust?                          | 0.864         | refused |
```

**Criterion 4: chunk size.** Output of `ingest.py::describe` and `chunker.py::describe` (the same lines `python app.py index` prints) for `chunker.py::split_documents`:

```
Corpus: campus_life
  loaded   88 documents, 27,908 characters, ~317 characters per document
  chunked  138 chunks, 213 characters on average (shortest 63, longest 397), produced by chunker.py::split_documents
```

**Criterion 5: the named sources are the right sources.** "What do students say about CS 210?", run 1, where every named file contains what it is cited for:

```
Based on the provided documents, students say the following about CS 210:
* You should do the labs even though they are only worth 10%, because the exams reuse the lab problems (*course_cs_210_exams.txt*, *course_cs_210.txt*).
* You should expect 8 to 10 hours of work a week outside class (*course_cs_210.txt*, *course_cs_210_workload.txt*). 
* The workload is front-loaded, meaning the first month is heavier than the rest (*course_cs_210_workload.txt*).
```

The miss, "What is the parking situation like near student housing?", run 1, which names 7 files when only `admin_parking_permits.txt` mentions parking:

```
Based on the provided documents, there is no information about the parking situation near student housing. 

Source: *admin_parking_permits.txt*, *housing_fenwick_court.txt*, *housing_aldridge_hall.txt*, *housing_old_brewhouse.txt*, *housing_tamsin_court.txt*, *transit_shuttle.txt*, and *admin_housing_lottery.txt*.
```

Note: Milestone one took me approximatley 3 hours instead of the estimated 45 minutes :( 

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| #   | Criterion                                    | Verdict | How I decided                                                                                        |
| --- | -------------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------- |
| 1   | Retrieved chunks contain the answer (4 of 5) | MET     | 5/5 in all three runs, scored by hand. Q5 only held after I stopped reading "near student housing" as a claim the documents make, and Q3 answers give closing times rather than dinner hours, so it is less close than it looks. |
| 2   | Every answer names a source (5 of 5)         | MISSED  | 5/5, 4/5, 5/5. In run 2 the Q5 answer was a refusal that named no file. The target is every answer, so one miss in one run is a miss. Runs 1 and 3 only passed Q5 by listing all 7 retrieved files. |
| 3   | Gate stops out-of-corpus questions (4 of 5)  | MET     | 5 of 5 refused, with best distances 0.825 to 0.923 against a 0.6 cutoff. One deterministic pass, so the same result in all three runs. Not close, though only far-off questions were tested. |
| 4   | All chunks above 50 characters               | MET     | 0 of 138 chunks are under 50 characters (shortest 63, longest 397, average 213). The shortest is only 13 over the line, and the target does not test for cut-off sentences. |
| 5   | Named sources are the right sources (4 of 5) | MET     | 4/5 in all three runs, so it meets the target exactly with no room to spare. Q5 is the miss: it names 7 files and only `admin_parking_permits.txt` mentions parking. Q5 run 2 named none and was counted as not applicable. Hand-scored, with Q3 and Q4 as judgement calls. |

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

**Miss: criterion 2 (every answer names a source), Q5 run 2. Stage: generation.**

Q5 asks "What is the parking situation like near student housing?" Retrieval did its job: `admin_parking_permits.txt` was retrieved at a best distance of 0.531, under the 0.6 cutoff, so the gate passed it. But that file never says the lots are near student housing, so the model had nothing to confirm the "near student housing" part. The model then followed the rule in `GROUNDING_INSTRUCTION` (`generate.py`) to say it doesn't have enough information. The instruction to name the document is a separate sentence in the same prompt, and nothing in code checks for it or adds a source afterward. In run 2 the model followed the refusal rule and dropped the filename: "Based on the provided documents, there is no information about the parking situation near student housing. I don't have enough information to answer the question." In runs 1 and 3 it did the opposite and pasted all 7 retrieved files as the source. Caching was off, so the same prompt gave three different behaviours.

The mechanism is that citing a source depends on the model complying with a prompt instruction, and that instruction is least reliable when the model is refusing, because there is no claim to attach a file to. The failure is not in loading, chunking, embedding or retrieval.

**Pattern.** The criterion 2 miss and the weak spot in criterion 5 are the same problem. Both are Q5, and both come from a question whose wording the corpus doesn't support. When I reworded it to "Where can students park?", it gave one correct source (`admin_parking_permits.txt`) in 3 of 3 tries. So a fix should target how the system cites sources when it refuses, not the retrieval.

**Targets I'd tighten.** Criterion 4 was set low: 50 characters is below a heading plus one short sentence (shortest chunk is 63), and it doesn't test for cut-off sentences. I'd change it to a count of chunks that end mid-sentence, with a target of 0. Criterion 3 passes 5 of 5, but all five questions are far off topic. The five near-miss questions I added (best distance 0.431 to 0.583) all get past the 0.6 gate, so I'd test the model's refusal on those and tighten the target from 4 of 5 to 5 of 5.

## The Improvement

See the above section and the before run file [results/run_2026-10-07_0434_before.md](results/run_2026-10-07_0434_before.md) for more info! 

**Fix 1**: I fixed question 5 so it is less ambiguous. 

 Q5: What is the parking situation like near student housing? -> Where can students park?

See change at: [questions.py line 30](questions.py#L30)

Why I picked it: The vagueness was giving RAG a hard time answering. And it produced a no info found answer despite there being info found which messed up Criteria 2: Every answer the system produces names at least one source document because one of the runs had no source document. It also messed up criteria 5: For at least 4 of my 5 test questions, if it generates an answer, the all the documents the answer names is one that actually contains the answer but it sitll passed due to my 4/5 threshold. The answers say there is no information while citing `admin_parking_permits.txt`, which does have parking information.

More info on the process of figuring out a new question here: [results/run_2026-10-07_0434_before.md, Q5](results/run_2026-10-07_0434_before.md#q5-what-is-the-parking-situation-like-near-student-housing)

I picked it because the question was confusing the RAG for the "student housing" part so it was hard to evaluate pass or fail. I first changed it to "Where can students park near student housing?" Then ultimatedly I realized that RAG was getting tripped up on the student housing part so I changed the question to "Where can students park?"

**Fix 2:**  Criteria 4 - Change target for chunks 

Issue: Criterion 4 was set low: 50 characters is below a heading plus one short sentence (shortest chunk is 63), and it doesn't test for cut-off sentences. This target is likely too weak and easy. The target also doesn't test what my reasoning claims, which is not cutting off sentences. A stricter and more meaningful check would be a count of chunks that end mid-sentence. I'd change it to a count of chunks that end mid-sentence, with a target of 0. 

Why: For the old criteria, my shortest chunk is 63 characters, so every chunk already passed, and the criterion said nothing about chunk quality. Counting chunks that end mid-sentence is something I can check the same way every time.

New Criteria 4: No chunk ends mid-sentence. Out of all chunks, the count whose text doesn't end in `.`, `!`, `?` (or a closing quote or parenthesis) should be 0. This should pass 5/5 of the time. 

**Fix 3** Criteria 3: on stopping out of gate questions 

Change target from 4/5 to 5/5 

I addressed near miss questions in the section below. In this section, since the example out of scope questions are entirely out of scope, I think I should raise the criteria to 5/5 because they are just so out of scope. Their distances are approx .8 which is way above .6 so none of them get past the gate. 

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — Before 

For reference, here is the old information:

1. For at least 4 of my 5 test questions, the retrieved chunks include one that contains the answer.
2. Every answer the system produces names at least one source document.
3. When I ask a question my documents clearly don't cover, the relevance gate stops it and the system returns "I don't have enough information about that" — in at least 4 of 5 tries.
4. All chunk sizes should be above 50 characters.
5. For at least 4 of my 5 test questions, if it generates an answer, the all the documents the answer names is one that actually contains the answer

| Criterion                              | Target | Run 1          | Run 2   | Run 3   | Verdict |
| -------------------------------------- | ------ | -------------- | ------- | ------- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5            | 5/5     | 5/5     | MET     |
| 2. Every answer names a source         | 5 of 5 | 5/5            | 4/5     | 5/5     | MISSED  |
| 3. Gate stops out-of-corpus questions  | 4 of 5 | 5/5            | 5/5     | 5/5     | MET     |
| 4. Limit too small chunk size          | 5 of 5 | 138/138 chunks | 138/138 | 138/138 | MET     |
| 5. Named sources are the right sources | 4 of 5 | 4/5            | 4/5     | 4/5     | MET     |

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

### Run Log - After 

 For reference, here is the **new** information:

1. For at least 4 of my 5 test questions, the retrieved chunks include one that contains the answer.
2. Every answer the system produces names at least one source document.
3. When I ask a question my documents clearly don't cover, the relevance gate stops it and the system returns "I don't have enough information about that" — in at least **5 of 5** tries.
4. ~~All chunk sizes should be above 50 characters.~~ No chunk ends mid-sentence. Out of all chunks, the count whose text doesn't end in `.`, `!`, `?` (or a closing quote or parenthesis) should be 0. This should pass 5/5 of the time. 
5. For at least 4 of my 5 test questions, if it generates an answer, the all the documents the answer names is one that actually contains the answer

| Criterion                              | Target | Run 1           | Run 2           | Run 3           | Verdict |
| -------------------------------------- | ------ | --------------- | --------------- | --------------- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5             | 5/5             | 5/5             | MET     |
| 2. Every answer names a source         | 5 of 5 | 5/5             | 5/5             | 5/5             | MET     |
| 3. Gate stops out-of-corpus questions  | 5 of 5 | 5/5             | 5/5             | 5/5             | MET     |
| 4. No chunk should end mid sentence    | 5 of 5 | 0 of 138 chunks | 0 of 138 chunks | 0 of 138 chunks | MET     |
| 5. Named sources are the right sources | 4 of 5 | 5/5             | 5/5             | 5/5             | MET     |

Scored by hand from `results/run_2026-10-07_0849_after.md`. Criterion 3 is deterministic, so it is the same in every run. Criterion 4 was checked with `python check_chunks.py`, and the chunks do not change between runs. Criterion 5 has two judgement calls: the dinner answers name files that give closing times rather than dinner hours, and the library answers name housing noise files that mention the library only in passing.

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

Partly. 

Criterion 2 went from MISSED (5/5, 4/5, 5/5) to MET (5/5 in all three runs). I got there by rewording Q5 from "What is the parking situation like near student housing?" to "Where can students park?", which removed the refusal that named no source. That fixes the symptom, not the cause: the system still depends on the model remembering to cite a file when it refuses, so a different question could miss again.

The other changes made my criteria better rather than my system better. Criterion 3 was already 5/5, so raising its target to 5/5 only tightens the bar. I also made Criterion 4 relevant. Criterion 4's old 50-character rule passed every chunk (shortest is 63), so the new check, 0 of 138 chunks ending mid-sentence, tests what I meant. All five criteria are now MET, scored by hand, with two judgement calls on criterion 5.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

As stated in the [results/run_2026-10-07_0434_before.md](results/run_2026-10-07_0434_before.md), there are a lot of things I need to fix mainly on more specific wording. I ran out of time and energy to fix basically everything. 

I need to decide whether "I don't have enough information"  counts as an answer. If it does, it needs a source document (criteria 2). 

For critieria 3, When I ask a question my documents clearly don't cover, the relevance gate stops it and the system returns "I don't have enough information about that" — in at least 4 of 5 tries., the relevance gate doesn't stop near miss questions about campus life so it needs to rephrase it . 

For critiera 1 and 5, more well defined pass or fail if only part of the information is included is included in the returned answer and answer is not totally complete based on the documents. 

**Near miss questions** 

I wanted to add some near miss questions to the questions.py to show the output and within the out of scope questions but I kept hitting a rate limit. I think I just need to replace the questions so I won't get rate limited instead of having 10 questions each and adding it to QUESTIONS and Out_of_scope. I added it to questions too so you can see the output. 

So instead of this original code in [questions.py](questions.py): 

```py
QUESTIONS = [
    # {"question": "...", "expects": "..."},
    {"question": "What do students say about wait times at Commons during lunch?", "expects": "food"},
    {"question": "What do students say about CS 210?", "expects": "CS 210"},
    {"question": "What time is dinner served in dining halls?", "expects": "pm"},
    {"question": "What do students say about the library?", "expects": "text"},
    {"question": "What is the parking situation like near student housing?", "expects": "parking"},
]

# Questions from a different world entirely. Your gate should refuse all five.
#
# There are five of these because criterion 3 in criteria.md names a target of
# "at least 4 of 5" — you need five things to try before you can report 4 of 5.
# `run_eval.py` runs these through retrieval and the gate on every eval and
# records what happened, so criterion 3 has evidence in the run log alongside
# the others. They cost no model calls: a refusal never reaches the model.
OUT_OF_SCOPE = [
    "What is the capital of Mongolia?",
    "How do I change the oil in a diesel engine?",
    "Who won the 1994 World Cup?",
    "What is the recommended dosage of ibuprofen for a headache?",
    "How do I write a for loop in Rust?",
]
```

Or this code which adds the questions which kept getting me rate limited: 

```py
QUESTIONS = [
    # {"question": "...", "expects": "..."},
    {"question": "What do students say about wait times at Commons during lunch?", "expects": "food"},
    {"question": "What do students say about CS 210?", "expects": "CS 210"},
    {"question": "What time is dinner served in dining halls?", "expects": "pm"},
    {"question": "What do students say about the library?", "expects": "text"},
    {"question": "What is the parking situation like near student housing?", "expects": "parking"},
    {"question": "What time does the gym close?", "expects": "pm"},
    {"question": "How much does a meal plan cost?", "expects": "$"},
    {"question": "What do students say about CS 999?", "expects": "CS 999"},
    {"question": "What are the library hours on Sundays?", "expects": "Sunday"},
    {"question": "What are the available clubs to join?", "expects": "club"},
]

# Questions from a different world entirely. Your gate should refuse all five.
#
# There are five of these because criterion 3 in criteria.md names a target of
# "at least 4 of 5" — you need five things to try before you can report 4 of 5.
# `run_eval.py` runs these through retrieval and the gate on every eval and
# records what happened, so criterion 3 has evidence in the run log alongside
# the others. They cost no model calls: a refusal never reaches the model.
OUT_OF_SCOPE = [
    "What is the capital of Mongolia?",
    "How do I change the oil in a diesel engine?",
    "Who won the 1994 World Cup?",
    "What is the recommended dosage of ibuprofen for a headache?",
    "How do I write a for loop in Rust?",
    # near-miss questions: on-topic for campus life, but the answer isn't in the documents
    "What time does the gym close?",
    "How much does a meal plan cost?",
    "What do students say about CS 999?",
    "What are the library hours on Sundays?",
    "What are the available clubs to join?",
]

'''
AI suggested near-miss questions for the corpus: and I added some of my own near-miss questions.
"What time does the gym close?" The corpus covers dining, housing, courses, and the library, but may have no gym documents. It would match other "hours" chunks.
"How much does a meal plan cost?" It is a dining question, but the documents may only cover wait times and closing hours, not prices.
"What do students say about CS 999?" It looks like the CS 210 and CS 340 documents, with a course that doesn't exist.
"What are the library hours on Sundays?" The documents give term-time and reading-week hours, not Sunday hours.
'''
```

I should just replace this questions to this just for the near miss test run: 

```py
QUESTIONS = [
    # {"question": "...", "expects": "..."},
    {"question": "What time does the gym close?", "expects": "pm"},
    {"question": "How much does a meal plan cost?", "expects": "$"},
    {"question": "What do students say about CS 999?", "expects": "CS 999"},
    {"question": "What are the library hours on Sundays?", "expects": "Sunday"},
    {"question": "What are the available clubs to join?", "expects": "club"},
]

# Questions from a different world entirely. Your gate should refuse all five.
#
# There are five of these because criterion 3 in criteria.md names a target of
# "at least 4 of 5" — you need five things to try before you can report 4 of 5.
# `run_eval.py` runs these through retrieval and the gate on every eval and
# records what happened, so criterion 3 has evidence in the run log alongside
# the others. They cost no model calls: a refusal never reaches the model.
OUT_OF_SCOPE = [
    # near-miss questions: on-topic for campus life, but the answer isn't in the documents
    "What time does the gym close?",
    "How much does a meal plan cost?",
    "What do students say about CS 999?",
    "What are the library hours on Sundays?",
    "What are the available clubs to join?",
]
```

That worked to not get rate limited. I could not combine these new questions with the old questions or else I would get rate limited. 

You can see the outcome [results/run_2026-10-07_0817_before_with_near_miss_questions.md](results/run_2026-10-07_0817_before_with_near_miss_questions.md) and see it was let through the gate but all the answers are saying there is not enough information or that it's not mentioned. 

So to continue with the fix 3 above,  Criteria 3: on stopping out of gate questions 

Rephrase this question so it either stops out of gate questions above a threshold or it refuses to answer questions out of scope 

 Criterion 3 passes 5 of 5, but all five questions are far off topic. The five near-miss questions I added (best distance 0.431 to 0.583) all get past the 0.6 gate, so I'd test the model's refusal on those and tighten the target from 4 of 5 to 5 of 5.

So I should rephrase critieria 3 to accomodate near miss questions that pass the gate. Fortunately, they still return answer not found. 

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

On the project itself: 

Since the middle of Unit 1, I desperately wished I chose a different corpus. Campus_life was already working well being split by documents but the other two such as the long text of advice documents were not being split well. I don't think my new way of chunking made improvements but it did help me learn more about chunking. I wish I tackled and fixed the chunking on advice_threads but at that point I didn't know the future tasks of changing the chunking and I just chose the default corpus. 

On the five criteria: 

I understand criteria better now so I would write each one more carefully such as defining exactly what an answer is and if answer is not found counts as an answer. 

I also need to figure out how to tackle answers that give part of the answer but not the entire answer.

I would get better at making more measurable criteria so I can write a `scorer.py` next time. 

## How I Used AI for Unit 2 

I created a new section to separate out the section for Unit 1.

1. Asking to run without cache 

- I realized that Unit 1, when I asked the corpus stuff, it said it used a cached answer and the runs in the run log showed me the importance of not having cached answers. So I asked AI: "how to turn off cache when running "python app.py ask "Where can students park near student housing?""  @RUNNING.md"
- It responded: 

RUNNING.md doesn't list a flag for this. I'll check how `generate.py` handles the cache.

...

Set the `AI201_CACHE` environment variable to `0` for that one command:

```bash
AI201_CACHE=0 python app.py ask "Where can students park near student housing?"
```

[config.py:72](config.py#L72) reads it (`CACHE_ENABLED = os.getenv("AI201_CACHE", "1") != "0"`). With it set to `0`, [generate.py:218](generate.py#L218) skips both the cache read and the cache write. The variable only applies to that command. To turn the cache off for the whole terminal session, run `export AI201_CACHE=0` first.

To clear what's already cached, delete the `.cache/` folder in the project root.

`app.py ask` has no `--no-cache` flag. `run_eval.py` already passes `cache=False` itself, as RUNNING.md says.

Then I inquired about the --no-cache flag so it changed some lines in `app.py` to add the flag.

Here are the changes it made: 

The diff shows a `--no-cache` flag added to `app.py`, passed down through the call chain.

**1. CLI flag** in `build_parser()`, on the `ask` subcommand:

```python
p_ask.add_argument(
    "--no-cache",
    action="store_true",
    help="skip the response cache and make a fresh model call",
)
```

**2. `cmd_ask`** converts the flag to a `cache` boolean in both call sites. These are the single-question path and the interactive loop.

```python
cache=not args.no_cache,
```

**3. `_ask_one`** takes a new `cache=True` parameter and forwards it to `ask_pipeline`.

**4. `ask_pipeline`** takes `cache=True` and passes it to the generator:

```python
outcome["answer"] = answer_from_chunks(question, results, cache=cache)
```

Caching stays on by default. `--no-cache` sets `cache=False` all the way down to `answer_from_chunks`.

This diff only touches `app.py`. `answer_from_chunks` has to accept a `cache` keyword, or the call will raise a `TypeError`. `git status` doesn't list `generate.py` as modified, so I haven't checked that. I can look at it if you'd like.

...

Your `app.py` change just wires the CLI flag into that existing parameter, so there's no `TypeError` risk.

**How caching works**

`generate()` hashes the prompt and system prompt into a key. If a response with that key is already in `.cache/`, it returns that response without calling the model. Otherwise it calls the model and saves the result.

**How to use `--no-cache`**

It's a flag on the `ask` subcommand:

```
python app.py ask "your question" --no-cache
```

It also works in interactive mode, where it applies to every question you ask in that session. It forces a fresh model call each time and skips both the cache read and the cache write.

Use it when you want several real, independent answers to the same question. Cached runs return the identical answer every time, and the docstring says unit 2 testing needs this. Cache hits also cost nothing, so a cached rerun doesn't reflect real usage. The session summary printed at the end shows how many calls were "served from cache".

Two related controls exist:

- `run_eval.py` already passes `cache=False`, so evals never use the cache.
- Setting the environment variable `AI201_CACHE=0` turns caching off globally, without the flag.
- So now I have two ways to run without cache 

```
AI201_CACHE=0 python app.py ask "Where can students park near student housing?"
python app.py ask "your question" --no-cache
```

* the code AI created looks legit and doesn't seem to break anything so I left it in

2. For criteria 2, of every answer names of source, I asked AI "Can you review criteria 2 and check if every answer for each of the 5 questions and each of the 3 runs names a source? The answer is found in ``` ```." and it found a fail on a question that said info not found (but 2/3 runs did include sources) and gave me some unprompted suggestions ot edit the criteria. It helped me create the table for criteria 2 but I check all the work and deleted some things they said incorrectly. 
3. most of the writing is mine and all approved by me. I had it help me fill out some of the tables such as if i didn't want to write pass for each one. I labeled suggestions that were suggested by AI.
4. Short scripts for checking things were written by AI [check_chunks.py](check_chunks.py)

## How I would use AI differently for the next project 

* would have it explain all the files and how it works together before I even started and maybe create a chart for me so I would remember 
* Formatting: This unit involved a lot of typing on markdown files. I am a rambler and I also like to walk you through my process. After I was finished, I wanted to asked AI to spellcheck and fix grammer and help me with formatting and let me approve the changes one by one instead of automatically applying it. I didn't want AI to rewrite for me or change my voice. I didn't do this because I lacked energy 
* Used AI as a sounding board earlier 

## Learnings 

* RAG isn't really good at answering the more vague complex questions such as " What is the parking situation like near student housing?" resulted in no information despite there being info becuase AI couldn't confirm the [corpora/admin_parking_permits.txt](corpora/admin_parking_permits.txt) was referring to parking lots near student housing. It answered "Where can students park near student housing?" but specified if it wasn't sure if it was near student housing. The question that was most successful with consistent answers was more simple: "Where can students park?" 
    - Source: [Criteria evaluation in results run_before: Q5: parking situation near student housing](results/run_2026-10-07_0434_before.md#q5-what-is-the-parking-situation-like-near-student-housing)
* Writing criteria is hard. I was confused about critieria throughout Units 1 and 2 but the project definitely helped me understand it more5 5
* tables in markdown are a pain. I use an extension to help with markdown but it doesn't let me edit tables because I'm not paying for it so editing the tables is a pain and since I wrote so much, it's so easy to get lost. 