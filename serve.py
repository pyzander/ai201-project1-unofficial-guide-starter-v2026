#!/usr/bin/env python3
"""
The Unofficial Guide — the same pipeline, over HTTP.

    python serve.py                          run it locally on port 5000
    gunicorn serve:app                       run it the way a host runs it

Nothing new happens in this file. It is a wrapper: a request comes in, it
hands the question to `app.py::ask_pipeline` — the exact function the command
line uses — and hands the answer back as JSON. Retrieval, the relevance gate
and the grounded prompt all still live where they lived. If you change how
your system answers, you change it in those files and this one follows.

Two routes:

    POST /ask       {"question": "..."} in, the answer and its sources out
    GET  /health    is the service up, and is there an index to search

Why this exists: `app.py` runs once and exits, which is fine on your laptop
and impossible to deploy. A hosted service has to stay up and wait for
requests. This is the smallest thing that does that.

Instrumentation (capstone): every request writes one structured JSON line to
`logs/requests_<start time>.jsonl` (override with AI201_LOG_FILE) and to the
console. Set AI201_LOG=0 to turn logging off. Each record has at least four
fields:

    timestamp    when the request arrived (UTC, ISO 8601)
    in           what came in: method, path and, for /ask, the question
    out          what came out: status code and, for /ask, the answer
    latency_ms   how long the whole request took

/ask records also carry the pieces needed for the cost and debugging sections:
retrieval_ms and generation_ms, whether the gate refused it, the best
distance, the sources, how many model calls it made, and the tokens it used.
"""

import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, g, jsonify, request

import config

app = Flask(__name__)


# ─── Structured log ──────────────────────────────────────────────────────────

# One log file per server start, named for the moment the server started, e.g.
# logs/requests_2026-11-18_093015.jsonl (local time). Set AI201_LOG_FILE to use
# a fixed name instead.
#
# Logging is on by default. Set AI201_LOG=0 to turn it off: nothing is written
# to the file or the console, and no logs/ folder is created.
LOGGING_ENABLED = os.getenv("AI201_LOG", "1") != "0"
_STARTED_AT = datetime.now().strftime("%Y-%m-%d_%H%M%S")
LOG_FILE = Path(
    os.getenv(
        "AI201_LOG_FILE",
        config.ROOT / "logs" / f"requests_{_STARTED_AT}.jsonl",
    )
)


def _build_logger() -> logging.Logger:
    """One logger, two handlers: the JSONL file (the record) and stdout."""
    logger = logging.getLogger("unofficial_guide.requests")
    if logger.handlers:  # already set up; the reloader imports this twice
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not LOGGING_ENABLED:
        logger.addHandler(logging.NullHandler())  # swallow records, write nothing
        return logger

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    for handler in (
        # delay=True: don't create the file until the first request is logged,
        # so a process that never serves one (like the debug reloader's
        # parent) doesn't leave an empty file behind.
        logging.FileHandler(LOG_FILE, encoding="utf-8", delay=True),
        logging.StreamHandler(sys.stdout),
    ):
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger


_log = _build_logger()


@app.before_request
def _start_timer():
    g.started = time.perf_counter()
    g.request_id = uuid.uuid4().hex[:12]
    g.log_in = {}    # extra fields about what came in
    g.log_out = {}   # extra fields about what came out
    g.log_extra = {}  # timings, tokens, gate decision, errors


@app.after_request
def _write_log_record(response):
    """One JSON object per request, written after the response is built.

    Runs for every route, including the 400 and 500 paths, so a failing
    request still leaves a line behind. Does nothing when AI201_LOG=0.
    """
    if not LOGGING_ENABLED:
        return response

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "request_id": g.request_id,
        "in": {"method": request.method, "path": request.path, **g.log_in},
        "out": {"status": response.status_code, **g.log_out},
        "latency_ms": round((time.perf_counter() - g.started) * 1000, 1),
        **g.log_extra,
    }
    _log.info(json.dumps(record, ensure_ascii=False))
    return response


@app.get("/health")
def health():
    """Is the service up, and is there an index to search?

    Two different questions, and the second one is the one that bites. A
    freshly deployed service answers this route happily while every /ask
    returns "no index" — hosts give you no disk that survives a restart, so
    the index has to be built as part of getting the service up. Checking
    here means you find that out in one request instead of five.
    """
    from store import index_exists

    ready = index_exists(config.CORPUS)
    g.log_out["index_ready"] = ready
    return jsonify(
        {
            "status": "ok",
            "corpus": config.CORPUS,
            "index_ready": ready,
            "detail": (
                "ready"
                if ready
                else "no index for this corpus — run `python app.py index`"
            ),
        }
    )


@app.post("/ask")
def ask():
    """One question in, one grounded answer out.

    A refused question is a 200, not an error. The gate refusing is your
    system working — it is an answer, and the JSON says so with
    `"refused": true` so whatever calls this can tell the two apart.
    """
    from app import ask_pipeline
    import generate

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):  # invalid JSON, no body, or a list/number
        payload = {}

    raw_question = payload.get("question")
    # Only a string can be a question. Calling .strip() on a number or a list
    # raised an AttributeError and came back as an HTML 500 page.
    question = raw_question.strip() if isinstance(raw_question, str) else ""
    g.log_in["question"] = raw_question  # log exactly what was sent

    if not question:
        message = (
            "Send JSON with a question in it, like "
            '{"question": "is the housing lottery random?"}'
        )
        g.log_out["error"] = message
        return jsonify({"error": message}), 400

    # on_gate fires the moment retrieval and the gate have finished, which
    # splits the request into "found the chunks" and "wrote the answer"
    # without touching app.py.
    marks = {}

    def mark_gate(decision):
        marks["gate_done"] = time.perf_counter()

    calls_before = generate.call_count()
    tokens_before = generate.token_counts()

    try:
        outcome = ask_pipeline(question, corpus=config.CORPUS, on_gate=mark_gate)
    except Exception as exc:  # noqa: BLE001 — a reader gets this, not a traceback
        message = f"{type(exc).__name__}: {exc}"
        g.log_out["error"] = message
        g.log_extra["error_type"] = type(exc).__name__
        return jsonify({"error": message}), 500

    ended = time.perf_counter()
    gate_done = marks.get("gate_done", ended)
    calls = generate.call_count() - calls_before
    tokens_after = generate.token_counts()

    g.log_out.update(
        answer=outcome["answer"],
        refused=outcome["refused"],
        sources=outcome["sources"],
    )
    retrieval_ms = round((gate_done - g.started) * 1000, 1)
    generation_ms = round((ended - gate_done) * 1000, 1)
    # An answered question that made no model call came out of the cache.
    cache_hit = (not outcome["refused"]) and calls == 0
    tokens = {
        "prompt": tokens_after["prompt"] - tokens_before["prompt"],
        "output": tokens_after["output"] - tokens_before["output"],
    }

    g.log_extra.update(
        corpus=config.CORPUS,
        best_distance=round(outcome["best_distance"], 4),
        threshold=outcome["threshold"],
        retrieval_ms=retrieval_ms,
        generation_ms=generation_ms,
        model_calls=calls,
        cache_hit=cache_hit,
        tokens=tokens,
    )

    return jsonify(
        {
            "question": question,
            "answer": outcome["answer"],
            "refused": outcome["refused"],
            "sources": outcome["sources"],
            "best_distance": round(outcome["best_distance"], 4),
            "threshold": outcome["threshold"],
            "corpus": config.CORPUS,
            # The same numbers the log records, so the caller can see them too.
            # latency_ms here stops when the answer is ready; the logged
            # latency_ms also counts building this reply, so it is slightly
            # larger.
            "metrics": {
                "latency_ms": round((ended - g.started) * 1000, 1),
                "retrieval_ms": retrieval_ms,
                "generation_ms": generation_ms,
                "model_calls": calls,
                "tokens": tokens,
                "cache_hit": cache_hit,
            },
        }
    )


def main():
    # Hosts tell you which port to listen on through PORT, and they expect you
    # on 0.0.0.0. Binding 127.0.0.1 instead works perfectly on your laptop and
    # then answers nothing at all once deployed, because the host's router
    # can't reach a socket that only accepts connections from inside the
    # container. It is the single most common way a first deploy "succeeds"
    # and is unreachable.
    port = int(os.getenv("PORT", "5000"))

    # Debug mode reloads on save, which is handy, and prints a console that
    # runs arbitrary code, which is not something to leave switched on where
    # strangers can reach it. Off unless you ask for it.
    debug = os.getenv("AI201_DEBUG", "0") == "1"

    print(f"Serving The Unofficial Guide on http://localhost:{port}")
    print(f"Corpus: {config.CORPUS}    (Ctrl-C to stop)\n")
    print("Try it from another terminal:\n")
    print(f"  curl http://localhost:{port}/health")
    print(
        f"  curl -X POST http://localhost:{port}/ask \\\n"
        f"    -H 'Content-Type: application/json' \\\n"
        f"    -d '{{\"question\": \"is the housing lottery random?\"}}'\n"
    )

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":
    main()
