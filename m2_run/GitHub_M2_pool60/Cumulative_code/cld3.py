"""Stand-in for the pycld3 package (needs the protobuf compiler, which is not
installable here). Analyzer2.is_english() returns True on every code path, so the
value returned here can never change the pipeline's output."""
from types import SimpleNamespace
def get_language(text):
    return SimpleNamespace(language="und", is_reliable=False, probability=0.0)
