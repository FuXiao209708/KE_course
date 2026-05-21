from pathlib import Path
import json

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"


def load_graph():
    p = DATA_DIR / "knowledge_graph.json"
    if not p.exists():
        return {"entities": [], "relations": []}
    return json.loads(p.read_text(encoding="utf-8"))


def query_graph_by_keywords(keywords):
    g = load_graph()
    ents = g.get("entities", [])
    rels = g.get("relations", [])
    matched = []
    for e in ents:
        if any(k.lower() in (e.get("name", "").lower()) for k in keywords):
            matched.append(e)
    matched_ids = {e.get("id") for e in matched}
    matched_rels = [r for r in rels if r.get("source") in matched_ids or r.get("target") in matched_ids]
    return {"entities": matched, "relations": matched_rels}
