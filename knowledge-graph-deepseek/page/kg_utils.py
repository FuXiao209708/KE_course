import os
from idlelib.query import Query

from neo4j import GraphDatabase

# Neo4j数据库连接配置
NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "123456")

def query_kg(keywords_json):
    """
    通过entities和relation在Neo4j中检索相关三元组
    返回格式：[{head, relation, tail}]
    """
    entities = keywords_json.get('entities', [])
    relations = keywords_json.get('relation', [])
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    triples = []
    with driver.session() as session:
        for entity in entities:
            print(entity)
            if relations:
                for rel in relations:
                    print(rel)
                    cypher = (
                        "MATCH (h)-[r]->(t) "
                        "WHERE h.name CONTAINS $entity AND r.relation = $rel "
                        "RETURN h.name AS head, r.relation AS relation, t.name AS tail"
                    )
                    results = session.run(cypher, entity=entity, rel=rel)
                    print(results)
                    records = list(results)
                    print(records)
                    for record in results:

                        triples.append({
                            "head": record["head"],
                            "relation": record["relation"],
                            "tail": record["tail"]
                        })
                    #print(triples)
            else:
                cypher = (
                    "MATCH (h)-[r]->(t) "
                    "WHERE h.name CONTAINS $entity "
                    "RETURN h.name AS head, r.relation AS relation, t.name AS tail"
                )
                results = session.run(cypher, entity=entity)
                for record in results:
                    triples.append({
                        "head": record["head"],
                        "relation": record["relation"],
                        "tail": record["tail"]
                    })
    driver.close()
    # 按三元组格式返回，兼容原有接口
    result = []
    for triple in triples:
        result.append({
            'node': {'name': triple['head']},
            'neighbors': [{
                'relation': triple['relation'],
                'node': {'name': triple['tail']}
            }]
        })
    return result 