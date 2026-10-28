"""
Step 4 - Ask the same model, with the same prompt and settings, to revise every case
in every condition. One raw output file per (case, condition) is saved and never edited.

The model is reached through an OpenAI-compatible chat endpoint. The default in
config.json is a local Ollama server (free, no API key, model pinned by digest).

Usage:
    python scripts/run_model.py --pilot     # first case only, all 3 conditions (Lab 4 pipeline check)
    python scripts/run_model.py             # all cases; already-saved outputs are skipped
Output: results/raw_outputs/<condition>/<case>.json, results/model_info.json
"""
import argparse
import datetime as dt
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "config.json"), encoding="utf-8"))["model"]
TEMPLATE = open(os.path.join(ROOT, "prompt_template.txt"), encoding="utf-8").read()


def post(url, payload, key=None):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def safe(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def record_model_info():
    info = {"recorded_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "settings": CFG}
    if "11434" in CFG["base_url"]:  # Ollama: record the exact model digest
        try:
            tags_url = CFG["base_url"].replace("/v1", "") + "/api/tags"
            with urllib.request.urlopen(tags_url, timeout=30) as r:
                tags = json.loads(r.read())
            info["ollama_model"] = [m for m in tags.get("models", []) if m.get("name") == CFG["name"]]
        except Exception as e:
            info["ollama_model_error"] = str(e)
    json.dump(info, open(os.path.join(ROOT, "results", "model_info.json"), "w"), indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    record_model_info()
    rows = [json.loads(l) for l in open(os.path.join(ROOT, "data", "conditions.jsonl"), encoding="utf-8")]
    if args.pilot:
        first = rows[0]["case_id"]
        rows = [r for r in rows if r["case_id"] == first]
    key = os.environ.get(CFG.get("api_key_env") or "", "") or None
    for r in rows:
        out = os.path.join(ROOT, "results", "raw_outputs", r["condition"], safe(r["case_id"]) + ".json")
        if os.path.exists(out):
            print("skip (already saved):", r["condition"], r["case_id"])
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        prompt = TEMPLATE.format(code=r["input_code"], comment=r["input_comment"],
                                 line=r["commented_line_text"])
        payload = {"model": CFG["name"], "messages": [{"role": "user", "content": prompt}],
                   "temperature": CFG["temperature"], "max_tokens": CFG["max_tokens"]}
        if CFG.get("seed") is not None:
            payload["seed"] = CFG["seed"]
        t0 = dt.datetime.now(dt.timezone.utc)
        resp = post(CFG["base_url"].rstrip("/") + "/chat/completions", payload, key)
        json.dump({"case_id": r["case_id"], "condition": r["condition"],
                   "request_utc": t0.isoformat(), "request": payload, "response": resp},
                  open(out, "w", encoding="utf-8"), indent=1)
        print("saved:", r["condition"], r["case_id"])


if __name__ == "__main__":
    main()
