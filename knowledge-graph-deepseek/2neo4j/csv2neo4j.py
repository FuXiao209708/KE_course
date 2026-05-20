from neo4j import GraphDatabase
import csv
import json
import os
import glob

# 读取配置文件
with open('D:\SEU\毕设\knowledge-graph-deepseek\csv2neo4j\config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)


def check_node_exists(session, node_name, type):
    """检查节点是否存在"""
    result = session.run("MATCH (n: `" + type + "`{name: $name}) RETURN COUNT(n) AS count", name=node_name)
    count = result.single()["count"]
    return count > 0


def check_relation_exists(session, start_node, end_node, relation):
    """检查关系是否存在"""
    result = session.run(
        "MATCH (start)-[r:" + relation + "]->(end) WHERE start.name = $start_name AND end.name = $end_name RETURN COUNT(r) AS count",
        start_name=start_node, end_name=end_node)
    count = result.single()["count"]
    return count > 0


def find_output_csv_files():
    """查找所有x_output.csv文件"""
    csv_dir = 'D:\SEU\毕设\knowledge-graph-deepseek\csv2neo4j\csv'
    pattern = os.path.join(csv_dir, '*_output.csv')
    return glob.glob(pattern)


def process_csv_file(session, file_path):
    """处理单个CSV文件并将数据导入Neo4j"""
    print(f"处理文件: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            # 创建CSV读取器
            data = csv.reader(file)
            headers = next(data)  # 读取表头

            # 解析CSV表头，找到相应的列索引
            subject_idx = headers.index('subject')
            subject_type_idx = headers.index('subject_type')
            relation_idx = headers.index('relation')
            object_idx = headers.index('object')
            object_type_idx = headers.index('object_type')
            data_object_idx = headers.index('data/object')

            for row in data:
                if len(row) <= max(subject_idx, subject_type_idx, relation_idx, object_idx, object_type_idx,
                                   data_object_idx):
                    print(f"跳过无效行: {row}")
                    continue

                subjectt = row[subject_idx]
                subjectt_type = row[subject_type_idx]
                relation = row[relation_idx]
                objectt = row[object_idx]
                objectt_type = row[object_type_idx]
                flag_of_relation = row[data_object_idx]

                # 创建主体节点（如果不存在）
                if not check_node_exists(session, subjectt, subjectt_type):
                    session.run("CREATE (n:`" + subjectt_type + "` {name: $name})",
                                name=subjectt)

                # 对象节点和关系处理
                if flag_of_relation != "data":  # 对象关系
                    # 创建对象节点（如果不存在）
                    if objectt and not check_node_exists(session, objectt, objectt_type):
                        session.run("CREATE (n:`" + objectt_type + "` {name: $name})",
                                    name=objectt)

                    # 创建关系（如果不存在）
                    if subjectt != objectt and objectt and not check_relation_exists(session, subjectt, objectt,
                                                                                     relation):
                        session.run(
                            "MATCH (start:`" + subjectt_type + "`), (end:`" + objectt_type + "`) "
                                                                                             "WHERE start.name = $start_name AND end.name = $end_name "
                                                                                             "CREATE (start)-[r:" + relation + "]->(end)",
                            start_name=subjectt, end_name=objectt)
                else:  # 属性关系
                    # 设置属性值
                    session.run("MATCH (n:`" + subjectt_type + "` {name: $name}) "
                                                               "SET n.`" + relation + "` = COALESCE(n.`" + relation + "`, '') + "
                                                                                                                      "CASE WHEN n.`" + relation + "` IS NULL THEN '' ELSE ';' END + $value",
                                name=subjectt, value=objectt)
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")


def main():
    # 连接到Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", cfg['password']))

    with driver.session() as session:
        # 清空数据库
        print("清空Neo4j数据库...")
        session.run("MATCH ()-[r]->() DELETE r")
        session.run("MATCH (n) DELETE n")

        # 查找所有x_output.csv文件
        csv_files = find_output_csv_files()
        if not csv_files:
            print("未找到任何x_output.csv文件")
            return

        print(f"找到 {len(csv_files)} 个CSV文件")

        # 处理每个CSV文件
        for file_path in csv_files:
            process_csv_file(session, file_path)

    driver.close()
    print("数据导入完成")


if __name__ == "__main__":
    main()
