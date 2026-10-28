"""
Runs two of the authors' preprocessing steps VERBATIM from their own source file.

Source: shirinpirouzkhaah/Price-of-Precision, commit d1e96929d2e78a20e65f78422676761411c8b18c,
        Preprocessing/Cumulative_code/Analyzer2.py
(The same two functions are byte-identical in Isolated_code/Analyzer2.py.)

We do not copy-paste or rewrite the authors' code. This module reads their Analyzer2.py,
pulls out only the static methods the two steps need (using Python's ast module), and
executes that exact source. Analyzer2.py cannot simply be imported because its top-level
imports include cld3, which does not install on our machines.

Steps used:
  * Analyzer2.removeComments(s)                              -> "code comment removal"
  * Analyzer2.clean_comment_without_abstraction(comm, idioms) -> "review comment cleaning"

One function is replaced, with no change in behaviour:
  * Analyzer2.is_english(text): every return path in the authors' version returns True
    (including the except branch), so it is replaced by a function that returns True.

Two helper files the code reads are missing from the authors' release (utils/ folder):
  * ./utils/stop-words-english.txt  -> substitute list supplied in this repo (recorded deviation)
  * ./utils/idioms.csv              -> substitute empty file (recorded deviation)
"""
import ast
import hashlib
import os
import re
import textwrap

import regex

EXPECTED_COMMIT = "d1e96929d2e78a20e65f78422676761411c8b18c"

NEEDED = [
    "removeComments",
    "clean_comment_without_abstraction",
    "clean_text",
    "removeEmojis",
    "remove_http",
    "remove_split_punctuation_with_floats",
    "remove_stopwords",
    "lower_text",
    "load_keywords",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def load_authors_analyzer2(analyzer2_path):
    """Return a class object holding the authors' functions, plus the source file's SHA-256."""
    src = open(analyzer2_path, encoding="utf-8").read()
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Analyzer2")

    pieces = []
    found = set()
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name in NEEDED:
            start = min([d.lineno for d in node.decorator_list] + [node.lineno])
            seg = "".join(lines[start - 1: node.end_lineno])
            pieces.append(textwrap.dedent(seg))
            found.add(node.name)
    missing = set(NEEDED) - found
    if missing:
        raise RuntimeError(f"Functions not found in {analyzer2_path}: {sorted(missing)}")

    body = "\n".join(pieces)
    # is_english: authors' version always returns True (see module docstring)
    body += "\n@staticmethod\ndef is_english(text):\n    return True\n"
    class_src = "class Analyzer2:\n" + textwrap.indent(body, "    ")

    namespace = {"re": re, "regex": regex}
    exec(compile(class_src, f"<authors {os.path.basename(analyzer2_path)}>", "exec"), namespace)
    return namespace["Analyzer2"], sha256(analyzer2_path)
