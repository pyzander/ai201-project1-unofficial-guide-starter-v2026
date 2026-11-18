# Running this project

Everything about how the starter works and how to use it.

---

## Before your first class

Setup happens **before class**, not during it. The
[environment setup page](../pages/ide_setup) has the per-operating-system
commands, the exact versions, and where to get your API key.

The short version, from inside this repo after you've forked and cloned it:

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then paste your key into .env
python test.py
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env         # then paste your key into .env
python test.py
```

**You're ready when `python test.py` passes.** The first run is slow — it
downloads the embedding model, about 80 MB. That's exactly why this happens
before class rather than during it.

The model comes down from Chroma's own servers, not from Hugging Face, and
embedding runs entirely on your machine. If your network blocks one of those
and not the other, this is the one that has to get through:
`chroma-onnx-models.s3.amazonaws.com`.

If it doesn't pass and you've made one honest attempt at the error, post the
**whole** output in the help channel. Setup problems are normal and nobody has
ever been judged for having one.

> **Activate the virtual environment every time you open a new terminal.** You
> should see `(.venv)` at the start of your prompt. Installing into your system
> Python instead is the single most common cause of "it worked yesterday."

---

## Your first five minutes

```bash
python app.py corpora                     # see what's available
python app.py index                       # build the search index
python app.py ask "is the housing lottery random?"
```

That's the whole pipeline running end to end. The answer won't be great yet —
you're checking that it runs at all and that your key works.

To use a different corpus:

```bash
python app.py --corpus city_guides index
python app.py --corpus city_guides ask "how do I get to Kestrelford?"
```

Or set `CORPUS` in `config.py` once and stop typing it. **Re-run `index` after
switching corpora.**

---

## Every command

| Command                             | What it does                                                                                         |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `python test.py`                    | Checks your environment. Run it whenever something feels off                                         |
| `python app.py corpora`             | Lists the provided corpora with a one-line description                                               |
| `python app.py index`               | Loads, chunks, embeds and stores your corpus. Run after any change to chunking                       |
| `python app.py ask "question"`      | Asks one question, end to end                                                                        |
| `python app.py ask`                 | Keeps asking until you press Enter on an empty line                                                  |
| `python app.py chunks`              | Prints sample chunks — **Milestone 3**                                                               |
| `python app.py retrieve "question"` | Shows distances without spending a model call — **Milestone 4**                                      |
| `python run_eval.py --label before` | Runs every test question three times, puts every `OUT_OF_SCOPE` question through the gate, and writes a run log — **unit 2** |

Useful flags:

| Flag              | Works on                   | What it does                                                   |
| ----------------- | -------------------------- | -------------------------------------------------------------- |
| `--corpus NAME`   | all                        | Use a different corpus without editing `config.py`             |
| `--variant NAME`  | `index`, `ask`, `retrieve` | Keep two different indexes of the same corpus side by side     |
| `-n 5`            | `chunks`                   | How many chunks to print                                       |
| `--top-k 8`       | `ask`, `retrieve`          | Retrieve more or fewer chunks                                  |
| `--threshold 0.7` | `ask`                      | Try a different relevance cutoff without editing `config.py`   |
| `--label before`  | `run_eval.py`              | Names the output file, so before and after are distinguishable |

---

## Which command goes with which milestone

| Milestone | What you're doing                   | Command                                                       |
| --------- | ----------------------------------- | ------------------------------------------------------------- |
| 1         | Pick a corpus and see it work       | `app.py corpora`, `app.py index`, `app.py ask "..."`          |
| 2         | Write your acceptance criteria      | Edit `criteria.md` and `questions.py`                         |
| 3         | Swap in your own chunker            | Edit `chunker.py`, then `app.py index` and `app.py chunks`    |
| 4         | Tune retrieval, set your cutoff     | `app.py retrieve "..."`, then edit `THRESHOLD` in `config.py` |
| 5         | Write it up                         | Fill in `README.md`                                           |
| Unit 2    | Run the test, fix one thing, re-run | `run_eval.py --label before` … `run_eval.py --label after`    |

`app.py chunks` prints each chunk with its **source file and the function that
produced it** — both of which your README has to name. Copy them straight
across.

`run_eval.py` also runs the five questions in `OUT_OF_SCOPE` at the bottom of
`questions.py` through retrieval and the relevance gate, and puts what happened
in the run log under its own heading. That's the evidence for criterion 3, and
it costs you nothing: a question the gate refuses never reaches the model, so
there is no API call. It runs them once rather than three times, because
retrieval is deterministic and the gate is a comparison against a fixed
number — three passes would produce the same three answers.

---

## Where everything lives

| File           | What it does                                                                                         |
| -------------- | ---------------------------------------------------------------------------------------------------- |
| `config.py`    | Every setting worth changing: chunk size, overlap, top-k, the relevance cutoff                       |
| `ingest.py`    | Loads documents off disk and cleans them — **stage 1**                                               |
| `chunker.py`   | Splits documents into chunks — **stage 2, and the file you replace in Milestone 3**                  |
| `store.py`     | Embeds chunks, stores them, retrieves them with distances — **stages 3 and 4**                       |
| `gate.py`      | The relevance gate. Refuses questions nothing came back close enough for                             |
| `generate.py`  | Writes the answer — **stage 5**. The only thing that calls out to a service                          |
| `app.py`       | The command line                                                                                     |
| `serve.py`     | The same pipeline behind HTTP, for when it has to run as a service — **unit 9**                      |
| `run_eval.py`  | Runs your questions repeatedly and writes the run log                                                |
| `questions.py` | Your five test questions, and the five out-of-corpus ones the gate should refuse. **You fill in the first five** |
| `criteria.md`  | Your five acceptance criteria. **You fill this in**                                                  |
| `README.md`    | Your submission                                                                                      |
| `corpora/`     | The provided documents, and `corpora/README.md` describing each                                      |
| `results/`     | Run logs, written by `run_eval.py`. **Commit these** — they're your evidence                         |

The five stages matter more than they look. In unit 2 you diagnose each failure
by naming which stage caused it, so it's worth knowing now which file is which.

---

## About rate limits

The free tier allows a small number of calls per minute. `generate.py` handles
this for you:

- **It paces its own requests** and prints a message when it's waiting. **A
  pause is the starter doing its job, not a bug.**
- **It caches repeated prompts** while you're building, so re-running the same
  question twenty times while debugging costs one call.
- **Caching turns itself off during evaluation runs.** Three runs of the same
  question have to be three real answers, not one answer repeated.
- **It stops if a session makes an unreasonable number of calls**, rather than
  silently draining your whole day's allowance. If you hit that, you almost
  certainly have a loop running away — look for it before raising the limit in
  `config.py`.
- **It prints how many calls and tokens you've used** when you exit. The
  token counts come off the responses themselves, so they're a measurement of
  what a run cost rather than an estimate.

If you see a `429` or "resource exhausted" error, that's a rate limit and not a
broken key. Wait a minute and re-run.

---

## When something goes wrong

| What you see                                            | What it means                                                                                        |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `No index called '...'. Run python app.py index first.` | You haven't indexed, or you switched corpus without re-indexing                                      |
| `No GEMINI_API_KEY found`                               | No `.env` file, or the key wasn't pasted in. On Windows check it didn't save as `.env.txt`           |
| `No corpus at ...`                                      | The corpus name is wrong. `python app.py corpora` lists the real ones                                |
| The system refuses everything                           | Your cutoff is too low for this corpus. Try `--threshold 0.75` to confirm, then set it properly in Milestone 4 |
| The system never refuses anything                       | Your cutoff is too high. Same process in reverse                                                     |
| `[rate limit] ... Waiting 34s`                          | Working as intended. Leave it                                                                        |
| `QuotaGuard: This session has made 300 requests`        | A loop is running away. Find it before raising the budget                                            |
| Indexing is very slow                                   | Expected on the first run — it's downloading the embedding model. Later runs are much faster         |

Still stuck after one honest attempt? Post in the help channel with the full
error, what you ran, and what you expected. You are not expected to debug your
own machine alone.

---

## Running it somewhere else — **unit 9**

Unit 1 doesn't need this. It's here because the file it describes ships in the
starter, and finding out in unit 9 that it exists is worse than reading one
table now.

`serve.py` puts the same pipeline behind HTTP, so it can run as a service that
stays up instead of a command that exits.

```bash
python serve.py                    # locally, on port 5000
gunicorn serve:app                 # the way a host starts it
```

| Thing           | What it does                                                                    |
| --------------- | ------------------------------------------------------------------------------- |
| `POST /ask`     | Send `{"question": "..."}`, get the answer and its sources back as JSON         |
| `GET /health`   | Says whether the service is up and whether an index exists to search            |
| `PORT`          | The port to listen on. Hosts set it for you; on your laptop it defaults to 5000 |
| `AI201_DEBUG=1` | Flask's reloader and debugger. Local only — never set it on a deployed service  |

> The free hosting tier sleeps after about fifteen minutes with no traffic, so
> the first request after a quiet spell waits roughly a minute for it to wake
> up. That's the tier, not your code.

`serve.py` writes one structured JSON line per request, with a timestamp, what came in, what came out and how long it took. Each time the server starts it opens a new log named for the moment it started, like `logs/requests_2026-11-18_105410.jsonl` (`requests_YYYY-MM-DD_HHMMSS.jsonl`). Set `AI201_LOG_FILE` to use a fixed file name instead, or set `AI201_LOG=0` to turn logging off.

---

## Stretch features

Optional, for extra credit. **Say what you're adding in your README before you
start** — a feature the README never claims earns nothing.

- **Metadata filtering** — let people narrow results by source or date. Chroma
  supports a `where` clause on `collection.query`; `store.py::search` is where
  it would go.
- **Conversational memory** — let the next question build on the last.
- **A second embedding model** — swap `EMBEDDING_MODEL` in `config.py`, index
  into a different `--variant`, and write down what moved. This is the one
  option that needs a package the default install doesn't have:
  `pip install 'sentence-transformers>=3.4,<3.5'` first. It's a large install
  (it brings PyTorch), so do it before class, not during. Expect your
  threshold to move too — a different model means different distances, and
  the 0.6 you measured in Milestone 4 was measured against this one.

`rank-bm25` is already installed for unit 2's hybrid-search option. The
dependency ships; the implementation is yours.

---

## A note on committing

Commit as you go — at least four new commits in unit 1, at least four more in
unit 2. Your commit history is what shows your criteria existed before your
results did.

**Do not delete and recreate this repository.** You submit the same URL both
units.

`results/` is deliberately **not** in `.gitignore`. Your run logs are evidence
that the test actually happened, and they're part of what gets graded.

> [!NOTE]
>
> Most of the above notes were from the starter code. Below is where the running notes I wrote begin. 

# Capstone Running Notes 

## TLDR: 

** Commands for Mac/Linux.**

See [Running on a Windows machine](#running-on-a-windows-machine) for the Windows commands.

### Terminal 1 (server): 

```bash
# within the project folder # recommends terminal windows over VS Code terminals for visibility

source .venv/bin/activate 
PORT=5001 AI201_CACHE=0 python serve.py

```

### Terminal 2 (client): 

```bash
# within the project folder 
# start after starting the server terminal 1 
# automatically logs in /logs for each server start
# 10 questions in scope, 5 questions out of scope 
# running python pretty_log.py at end turns the .jsonl file into a pretty .json file 


source .venv/bin/activate 

curl http://localhost:5001/health

questions=(
  "Is the housing lottery random?"
  "Which halls are quiet?"
  "Which halls are loud?"
  "What do students say about wait times at Commons during lunch?"
  "What time is dinner served in dining halls?"
  "What do students say about CS 210?"
  "What is the deadline to add or drop a class?"
  "What do students say about the library?"
  "How do I book a study group room?"
  "Where can students park?"
  "What is the capital of Mongolia?"
  "How do I change the oil in a diesel engine?"
  "Who won the 1994 World Cup?"
  "What is the recommended dosage of ibuprofen for a headache?"
  "How do I write a for loop in Rust?"
)

for q in "${questions[@]}"; do
  echo "Q: $q"
  curl -s -X POST http://localhost:5001/ask \
    -H 'Content-Type: application/json' \
    -d "{\"question\": \"$q\"}" | python -m json.tool
  echo
done

python pretty_log.py   

```

You can also do a question line by line such as: 

```bash
curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "Is the housing lottery random?"}' | python -m json.tool
```

See [Example Questions](#example-questions) section below if you want the individual curl commands for all the questions above. 

When done, Kill the server on Terminal 1 by pressing: 

```
Ctrl + C 
```

## How to Run it (detailed): 

You need two terminals, both in the project folder.

### How to start a terminal:

In VS Code, press **Ctrl+`** (the backtick key, left of the 1). (Note: Use Ctrl not Cmd.) You can also use the menu **Terminal > New Terminal**. It opens at the bottom, already in your project folder.

For the **second terminal**, click the **+** icon at the top right of the terminal panel, or use the split button next to it to see both side by side. The dropdown in the panel lets you switch between terminals. Use one for the server and one for the `curl` commands.

> [!TIP]
>
> For maximum screen space and visibility, use the terminal app. 
>
> If you'd rather use the Mac Terminal app, open it with Cmd+Space, type "Terminal" and press Enter. Then `cd` to the project folder. You can do this by grabbing the absolute path from right clicking on your project folder in the explorer panel on vs code and then in the terminal, type in `cd` followed by whatever the project name is. It should look something like this: 

```bash
cd ~/Documents/CodePath2026/ai201/ai201-project1-unofficial-guide-starter-v2026
```

See the [Windows section](#running-on-a-windows-machine) for more information on running on a Windows machine. 

### Terminal 1: start the server 

```bash
source .venv/bin/activate 
PORT=5001 AI201_CACHE=0 python serve.py

```

`AI201_CACHE=0` turns the cache off, so each answered question makes a real model call and the token counts are real. The server prints the URL (`http://localhost:5001`) and keeps running. Every request is also printed here as a JSON line.

> [!NOTE]
>
> When you do `AI201_CACHE=0 python serve.py` Apps usually start on port 5000 but on Macs that is usually in use by the AirPlay Receiver. It is an endpoint that accepts and plays back audio, video, or screen-mirroring streams sent wirelessly from an Apple device (like an iPhone, iPad, or Mac) over a Wi-Fi network. Use `lsof -i :5000` see what's using the port. The output shows the program name and its PID. If it's ControlCenter, that's AirPlay. If it's in use, you get the  "Address already in use" error when starting the server. 
>
> You have two ways to fix the issue :
>
> * Use a different port. This is the easiest fix. The server reads the PORT setting: `PORT=5001 AI201_CACHE=0 python serve.py `Then use `localhost:5001` in your curl commands.
> * Free the port. If an old copy of your own server is still running, stop it with `kill <PID>` using the PID from `lsof -i :5000`. To turn AirPlay off, go to System Settings > General > AirDrop & Handoff and turn off AirPlay Receiver.
>
> Thus, let's just not run into the issue and start our command on port 5001. 
>
> Remember to Press *Ctrl+C* on the terimal where the server is running when you are done. That's terminal 1, the one printing the log lines. 

### Optional: Turning automatic saving of logs off

I added a logging off switch to [serve.py](serve.py). Set `AI201_LOG=0` when you start the server:

```bash
PORT=5001 AI201_CACHE=0 AI201_LOG=0 python serve.py
```

On Windows PowerShell, use `$env:AI201_LOG = "0"` first, then `python serve.py`.

With it set to 0, the server writes nothing to the console or to a log file, and it doesn't create the `logs/` folder. Logging stays on by default, so nothing changes unless you set the variable. 

When logging is off, the `/ask` route still counts tokens and times each stage. It's just not recorded. 

### Terminal 2: send requests

```bash
# make sure you are in the project folder 

source .venv/bin/activate 

curl -s http://localhost:5001/health | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "Is the housing lottery random?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "How do I bake sourdough bread?"}' | python -m json.tool
```

The first `/ask` should be answered, and the second should be refused. 

`python -m json.tool` at the end of each request just prettifies the output. 

The only link you can access in the browser right now is the GET request link `http://localhost:5001/health` which gives you something like `{"corpus":"campus_life","detail":"ready","index_ready":true,"status":"ok"}`. The answer to the POST ask shows up in terminal 2. 

### Example Questions 

| Group               | Questions                                                                                            |
| ------------------- | ---------------------------------------------------------------------------------------------------- |
| **Housing**         | Is the housing lottery random? · Which halls are quiet? · Which halls are loud?                      |
| **Dining**          | Wait times at Commons during lunch · What time is dinner served in dining halls?                     |
| **Academics**       | What do students say about CS 210? · What is the deadline to add or drop a class?                    |
| **Campus services** | What do students say about the library? · How do I book a study group room? · Where can students park? |
| **Out of scope**    | the same five as before, at the end                                                                  |

Here is the list of 15 questions if you want to copy and paste all at once. 3 + 5 + 2 = 10 in scope, plus 5 out of scope.

The in scope questions are grouped by topic (housing, dining, academics and campus services), followed by the 5 out of scope ones. "Is the housing lottery random?" is the sample question. "Which halls are quiet?" and "Which halls are loud?" are the broad questions mentioned in Unit 1 that my chunking does better with than the original. The Commons wait times, CS 210, dinner, library and parking questions and the 5 out of scope ones are from Unit 2. The add/drop deadline and study group room questions are new for the capstone. 

Rate limiting not applied - to be safe, copy and paste a question at a time or a couple questions at a time.

See [Terminal 2 (client)](#terminal-2-client) in the TLDR section above if you want the more readable loop of commands 

```bash
# make sure you are in the project folder # start after starting the server terminal 1. # automatically logs in /logs for each server 

source .venv/bin/activate 

curl -s http://localhost:5001/health | python -m json.tool

# Housing
curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "Is the housing lottery random?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "Which halls are quiet?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "Which halls are loud?"}' | python -m json.tool

# Dining
curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "What do students say about wait times at Commons during lunch?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "What time is dinner served in dining halls?"}' | python -m json.tool

# Academics
curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "What do students say about CS 210?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "What is the deadline to add or drop a class?"}' | python -m json.tool

# Campus services
curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "What do students say about the library?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "How do I book a study group room?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "Where can students park?"}' | python -m json.tool

# Out of scope
curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "What is the capital of Mongolia?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "How do I change the oil in a diesel engine?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "Who won the 1994 World Cup?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "What is the recommended dosage of ibuprofen for a headache?"}' | python -m json.tool

curl -s -X POST http://localhost:5001/ask -H 'Content-Type: application/json' -d '{"question": "How do I write a for loop in Rust?"}' | python -m json.tool
```

**Order:** the ten in-scope questions come first, so the log shows answered requests, then the five refusals. The first ten should be answered, and the last five should come back `"refused": true`.

**Timing:** the answered ones take a few seconds each, and the refusals finish almost instantly. You can paste the commands one at a time or all together.

Terminal 1 is the server and terminal 2 is the client.

- **Terminal 1 (server):** it runs `python serve.py` and keeps running, waiting for requests. It's also where each request's log line is printed.
- **Terminal 2 (client):** it's where you run `curl`. Each `curl` command sends a request to the server, and the server's reply is printed in terminal 2.

The two terminals don't talk to each other directly. The client sends HTTP requests to `http://localhost:5001`, and the server answers them. That's why the server has to be running before you send anything. If it isn't, `curl` fails with "connection refused".

The browser can also be a client, but it only sends simple `GET` requests. That's why you can open `http://localhost:5001/health` in a browser, but not `/ask`, which needs a `POST` with a question.

### Additional Information: Logging 

Logs are saved automatically. Each server start writes its own log file, named for the time it started, like `logs/requests_2026-11-18_105410.jsonl`. If you can't find it visually, list the files to find yours:

```bash
ls logs
```

Print the newest one:

```bash
cat "$(ls -t logs/requests_*.jsonl | head -1)"
```

Each request should be one line. Look for `timestamp`, `in`, `out` and `latency_ms`, plus `tokens` and `cache_hit: false` on answered questions. To read it more easily in the terminal, type in the same terminal. (No file is saved):

```bash
python -c "import json,glob; f=sorted(glob.glob('logs/requests_*.jsonl'))[-1]; [print(json.dumps(json.loads(l), indent=2)) for l in open(f)]"
```

You can also write the newest log to a pretty JSON file with [pretty_log.py](../pretty_log.py). It saves a copy next to the log, like `logs/requests_2026-11-18_105410.pretty.json`:

```bash
python pretty_log.py                          # newest logs/requests_*.jsonl
python pretty_log.py logs/requests_X.jsonl    # a specific log
python pretty_log.py logs/requests_2026-11-18_105410.jsonl # example of logging to a specific log 
python pretty_log.py SRC.jsonl DST.json       # choose the output file too

```

### Killing Your Server 

**Kill your server in terminal 1 when you are done.** 

Press **Ctrl+C** in the terminal where the server is running. That's terminal 1, the one printing the log lines. The server stops and you get your prompt back.

If Ctrl+C doesn't work, or you closed that terminal and the server is still running in the background, find and stop it by port:

```bash
lsof -ti :5001 | xargs kill
```

`lsof -ti :5001` prints the process ID using port 5001, and `kill` stops it. To check that it worked, run `lsof -i :5001` again. It should print nothing.

If the process is still there after that, force it with `lsof -ti :5001 | xargs kill -9`.

### Practice run 

If you want a practice run first, add `AI201_LOG_FILE=logs/practice.jsonl` before `python serve.py`. Delete `logs/practice.jsonl` afterwards.

You can also use this method to write to a different file name besides the default, `logs/requests_<start time>.jsonl`.

Here's the full command for a practice run on port 5001, with the cache off and the log going to a separate file:

```bash
cd ~/Documents/CodePath2026/ai201/ai201-project1-unofficial-guide-starter-v2026 # replace this with the path to your folder 
source .venv/bin/activate # or .venv\Scripts\Activate.ps1 on Windows
PORT=5001 AI201_CACHE=0 AI201_LOG_FILE=logs/practice.jsonl python serve.py
```

Then send requests with `curl` in a second terminal, as before. To look at the log:

```bash
cat logs/practice.jsonl

# output in terminal 
python -c "import json; [print(json.dumps(json.loads(l), indent=2)) for l in open('logs/practice.jsonl')]"

# after the previous cat command, you can output the jsonl file prettily in a json file 
python -c "import json; rows=[json.loads(l) for l in open('logs/practice.jsonl') if l.strip()]; json.dump(rows, open('logs/requests.pretty.json','w'), indent=2, ensure_ascii=False)"
```

When you're done, stop the server with Ctrl+C. Then delete the practice file so it doesn't get mixed up with your real log:

```bash
rm logs/practice.jsonl
```

Nothing ignores `logs/practice.jsonl` yet. If you forget to delete it, `git status` will list it as untracked. For the real run, drop the `AI201_LOG_FILE=...` part, and the log goes to `logs/requests_<start time>.jsonl`, named for when the server started.

## Running on a Windows machine

### Terminal 1 (Server):

**Open the terminal app:** press the Windows key, type "PowerShell", and press Enter. In VS Code, Ctrl+` works the same on Windows.

**Go to the project folder:** in VS Code, right-click the project folder in the Explorer panel and choose **Copy Path**. Then in PowerShell type `cd` and paste the path in quotes:

```powershell
cd "C:\Users\YourName\Documents\CodePath2026\ai201\ai201-project1-unofficial-guide-starter-v2026"
```

You need the quotes if any part of the path has a space.

**Start the server:** the macOS commands won't work as written. Windows activates the environment differently, and it sets environment variables in a separate step, because `PORT=5001 python ...` isn't valid in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
$env:PORT = "5001"
$env:AI201_CACHE = "0"
python serve.py
```

For the practice run, add `$env:AI201_LOG_FILE = "logs/practice.jsonl"` before `python serve.py`.

**Optional: Turning automatic saving of logs off**

I added a logging off switch to [serve.py](serve.py). Set `AI201_LOG=0` when you start the server: On Windows PowerShell, use `$env:AI201_LOG = "0"` first, then `python serve.py`.

With it set to 0, the server writes nothing to the console or to a log file, and it doesn't create the `logs/` folder. Logging stays on by default, so nothing changes unless you set the variable. 

When logging is off, the `/ask` route still counts tokens and times each stage. It's just not recorded. 

**Stop the server when done:** press Ctrl+C. If it's stuck, find it by port and kill it:

```powershell
netstat -ano | findstr :5001
taskkill /PID <PID> /F
```

The PID is the last number on the line `netstat` prints.

**Environment variables:** `$env:` values last only for that terminal window. If you close it and open a new one, set them again.

### Terminal 2 (client):

**Curl:** use `curl.exe`, because plain `curl` in PowerShell is an alias for a different command. The quoting also differs, so `curl.exe -X POST ... -d "{\"question\": \"...\"}"` is how you'd write it there.

I can't run Windows here, so I haven't tested these. They're written from how PowerShell handles quotes. The exact commands depend on your PowerShell version, so I've given three options.

**Check the server is up (this works everywhere):**

```powershell
curl.exe http://localhost:5001/health
```

**Option 1: `Invoke-RestMethod` (the most reliable)**

This is a built-in PowerShell command, so you don't have to escape quotes:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "Is the housing lottery random?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "How do I bake sourdough bread?"}'
```

**Option 2: `curl.exe` with the question in a file**

Writing the JSON to a file avoids quote problems:

```powershell
'{"question": "Is the housing lottery random?"}' | Set-Content body.json
curl.exe -X POST http://localhost:5001/ask -H "Content-Type: application/json" -d "@body.json"
```

For each new question, run the first line again with different text. When you're done, delete `body.json` so it doesn't show up in `git status`.

**Option 3: `curl.exe` inline (Windows PowerShell 5.1 only)**

The inner quotes must be escaped with a backslash:

```powershell
curl.exe -X POST http://localhost:5001/ask -H "Content-Type: application/json" -d '{\"question\": \"Is the housing lottery random?\"}'
```

This one can fail on PowerShell 7.3 or newer, which handles the backslashes differently. If you get a 400 error or "invalid JSON", use Option 1 or 2. To see which version you have, run `$PSVersionTable.PSVersion`.

I'd use Option 1. The server's log should look the same whichever one sends the request.

### Asking Questions in Terminal 2 

These are the Windows versions as `Invoke-RestMethod` commands for PowerShell, on port 5001. I haven't tested them on Windows. Start the server first with `$env:PORT = "5001"` and `$env:AI201_CACHE = "0"` set, as in the Windows steps I gave earlier.

```powershell
# Housing
Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "Is the housing lottery random?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "Which halls are quiet?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "Which halls are loud?"}'

# Dining
Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "What do students say about wait times at Commons during lunch?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "What time is dinner served in dining halls?"}'

# Academics
Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "What do students say about CS 210?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "What is the deadline to add or drop a class?"}'

# Campus services
Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "What do students say about the library?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "How do I book a study group room?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "Where can students park?"}'

# Out of scope
Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "What is the capital of Mongolia?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "How do I change the oil in a diesel engine?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "Who won the 1994 World Cup?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "What is the recommended dosage of ibuprofen for a headache?"}'

Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body '{"question": "How do I write a for loop in Rust?"}'
```

If you'd rather send all 15 with one command, use this loop:

```powershell
$questions = @(
  # Housing
  "Is the housing lottery random?",
  "Which halls are quiet?",
  "Which halls are loud?",
  # Dining
  "What do students say about wait times at Commons during lunch?",
  "What time is dinner served in dining halls?",
  # Academics
  "What do students say about CS 210?",
  "What is the deadline to add or drop a class?",
  # Campus services
  "What do students say about the library?",
  "How do I book a study group room?",
  "Where can students park?",
  # Out of scope
  "What is the capital of Mongolia?",
  "How do I change the oil in a diesel engine?",
  "Who won the 1994 World Cup?",
  "What is the recommended dosage of ibuprofen for a headache?",
  "How do I write a for loop in Rust?"
)
foreach ($q in $questions) {
  $body = @{ question = $q } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri http://localhost:5001/ask -ContentType "application/json" -Body $body
}
```

The loop builds the JSON for you, so you don't have to worry about quote escaping. It sends the questions one after another, which is what you want, because the token counts in the log are only reliable when requests don't overlap.

Each command prints the server's reply in the terminal, and the server logs each request to `logs/requests_<start time>.jsonl`.

### To Prettify Jsonl

Run `pretty_log.py` from the project folder:

```bash
python pretty_log.py
```

It reads the newest `logs/requests_*.jsonl` and writes a copy next to it with `.pretty.json` on the end. For `requests_2026-11-18_105410.jsonl`, that's `requests_2026-11-18_105410.pretty.json`. The copy is a JSON array with 2-space indentation, and the original is unchanged. Open the new file in VS Code to read it.

To prettify a specific log, pass its path:

```bash
python pretty_log.py logs/requests_2026-11-18_105410.jsonl
```

If you only want to look at it in the terminal, with no file saved, use this:

```bash
python -c "import json,glob; f=sorted(glob.glob('logs/requests_*.jsonl'))[-1]; [print(json.dumps(json.loads(l), indent=2)) for l in open(f)]"
```

Run it after you've sent your requests, and stop the server first with Ctrl+C or use a second terminal. If you run it before any requests arrive, there's no log file yet and the script tells you to run the server first.

### Killing Your Server

Remember to kill the server when you are done with Ctrl + C. 