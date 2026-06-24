import ast
from pathlib import Path


def _load_duplicate_summarizer():
    source = Path(__file__).resolve().parents[1].joinpath("kometa.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    helper_nodes = []
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == "summarize_duplicate_collections":
            helper_nodes.append(node)
            break
    helper_module = ast.Module(body=helper_nodes, type_ignores=[])
    code = compile(helper_module, str(Path(__file__).resolve().parents[1] / "kometa.py"), "exec")
    namespace = {}
    exec(code, namespace)
    return namespace["summarize_duplicate_collections"]


def test_summarize_duplicate_collections_groups_case_insensitive_titles():
    summarize_duplicate_collections = _load_duplicate_summarizer()

    class Collection:
        def __init__(self, title):
            self.title = title

    collections = [
        Collection("Top 250 Movies"),
        Collection("Top 250 Movies"),
        Collection("top 250 movies"),
        Collection("Awards"),
        Collection("Unique"),
        Collection("Awards"),
    ]

    assert summarize_duplicate_collections(collections) == [("Top 250 Movies", 3), ("Awards", 2)]
