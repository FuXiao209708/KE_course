import json
from pathlib import Path
from typing import List, Dict

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"


def _load_json(name: str) -> Dict:
    path = DATA_DIR / name
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_demo_questions() -> List[Dict]:
    cfg = _load_json("demo_config.json")
    return cfg.get("demo_questions", [])


def get_exercises() -> List[Dict]:
    data = _load_json("mock_exercises.json")
    return data.get("exercises", [])


def get_graph() -> Dict:
    return _load_json("knowledge_graph.json")


def query_graph_by_keywords(keywords: List[str]) -> Dict:
    """基于关键词在本地 JSON 图谱中过滤实体与关系，返回子图"""
    graph = get_graph()
    ents = graph.get("entities", [])
    rels = graph.get("relations", [])
    matched = []
    for e in ents:
        if any(k in (e.get("name", "") or "") for k in keywords):
            matched.append(e)
    # 如果没有直接匹配实体，尝试基于关键词在 description 中匹配
    if not matched:
        for e in ents:
            if any(k in (e.get("description", "") or "") for k in keywords):
                matched.append(e)
    # 选择与匹配实体相关的关系
    matched_ids = {e.get("id") for e in matched}
    matched_rels = [r for r in rels if r.get("source") in matched_ids or r.get("target") in matched_ids]
    return {"entities": matched, "relations": matched_rels}
