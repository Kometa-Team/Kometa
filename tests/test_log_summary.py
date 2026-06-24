import ast
from pathlib import Path


def _load_helper_from_kometa():
    source = Path(__file__).resolve().parents[1].joinpath("kometa.py").read_text(encoding="utf-8")
    module = ast.parse(source)

    helper_nodes = []
    for node in module.body:
        if isinstance(node, ast.Import) and any(alias.name == "re" for alias in node.names):
            helper_nodes.append(node)
        if isinstance(node, ast.Assign):
            target_names = {target.id for target in node.targets if isinstance(target, ast.Name)}
            if target_names & {"ASSET_WARNING_KEY", "ASSET_WARNING_PATTERN"}:
                helper_nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name == "summarize_asset_warnings":
            helper_nodes.append(node)

    helper_module = ast.Module(body=helper_nodes, type_ignores=[])
    code = compile(helper_module, str(Path(__file__).resolve().parents[1] / "kometa.py"), "exec")
    namespace = {}
    exec(code, namespace)
    return namespace["summarize_asset_warnings"]


def test_summarize_asset_warnings_counts_and_deduplicates_folders_in_order():
    summarize_asset_warnings = _load_helper_from_kometa()
    log_lines = [
        "Asset Warning: Unable to find asset folder: 'Mind-FK'",
        "Asset Warning: Unable to find asset folder: 'Streaming Collections'",
        "Asset Warning: Unable to find asset folder: 'Mind-FK'",
        "Some other warning",
        "Asset Warning: Unable to find asset folder: 'Apple TV Movies'",
    ]

    count, folders = summarize_asset_warnings(log_lines)

    assert count == 4
    assert folders == ["Mind-FK", "Streaming Collections", "Apple TV Movies"]
