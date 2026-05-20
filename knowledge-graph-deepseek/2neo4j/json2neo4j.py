#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱JSON导入Neo4j脚本
将实体对齐后的知识图谱JSON文件导入Neo4j数据库进行可视化
"""

import os
import json
import argparse
import logging
from neo4j import GraphDatabase

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeGraphImporter:
    def __init__(self, uri, user, password):
        """
        初始化Neo4j连接
        
        Args:
            uri: Neo4j数据库URI
            user: 用户名
            password: 密码
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        """关闭Neo4j连接"""
        self.driver.close()
        
    def clear_database(self):
        """清空数据库"""
        with self.driver.session() as session:
            logger.info("清空Neo4j数据库...")
            session.run("MATCH ()-[r]->() DELETE r")
            session.run("MATCH (n) DELETE n")
    
    def check_node_exists(self, session, node_name, node_type):
        """
        检查节点是否存在
        
        Args:
            session: Neo4j会话
            node_name: 节点名称
            node_type: 节点类型
            
        Returns:
            bool: 节点是否存在
        """
        result = session.run(
            "MATCH (n:`" + node_type + "` {name: $name}) RETURN COUNT(n) AS count", 
            name=node_name
        )
        count = result.single()["count"]
        return count > 0
    
    def check_relation_exists(self, session, start_node, end_node, relation):
        """
        检查关系是否存在
        
        Args:
            session: Neo4j会话
            start_node: 起始节点名称
            end_node: 终止节点名称
            relation: 关系类型
            
        Returns:
            bool: 关系是否存在
        """


        result = session.run(
            "MATCH (start)-[r:" + relation + "]->(end) "
            "WHERE start.name = $start_name AND end.name = $end_name "
            "RETURN COUNT(r) AS count",
            start_name=start_node, end_name=end_node
        )
        count = result.single()["count"]
        return count > 0
    
    def create_node(self, session, node_name, node_type, attributes=None):
        """
        创建节点
        
        Args:
            session: Neo4j会话
            node_name: 节点名称
            node_type: 节点类型
            attributes: 节点属性
        """
        # 基本节点属性
        node_props = {"name": node_name}
        
        # 添加其他属性
        if attributes:
            for key, value in attributes.items():
                if key != "type" and key != "id" and key != "name":
                    # 处理列表类型的属性
                    if isinstance(value, list):
                        node_props[key] = ";".join([str(v) for v in value])
                    else:
                        node_props[key] = value
        
        # 构建属性字符串
        props_str = ", ".join([f"`{k}`: ${k}" for k in node_props.keys()])
        
        # 创建节点
        query = f"CREATE (n:`{node_type}` {{{props_str}}})"
        session.run(query, **node_props)
    
    def create_relation(self, session, start_node, end_node, start_type, end_type, relation):
        """
        创建关系
        
        Args:
            session: Neo4j会话
            start_node: 起始节点名称
            end_node: 终止节点名称
            start_type: 起始节点类型
            end_type: 终止节点类型
            relation: 关系类型
        """
        query = (
            f"MATCH (start:`{start_type}`), (end:`{end_type}`) "
            f"WHERE start.name = $start_name AND end.name = $end_name "
            f"CREATE (start)-[r:{relation}]->(end)"
        )
        session.run(query, start_name=start_node, end_name=end_node)
    
    def import_json_to_neo4j(self, json_path):
        """
        导入JSON到Neo4j
        
        Args:
            json_path: JSON文件路径
        """
        # 加载JSON文件
        logger.info(f"加载知识图谱JSON文件: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        # 定义属性关系和实体关系
        attribute_relations = [
            "被定义为", "内容", "英文名", "目标", "作用", 
            "特点", "方法", "缺点", "语法", "链接"
        ]
        
        # 判断JSON格式
        if "nodes" in graph_data and "links" in graph_data:
            # NetworkX的node_link_data格式
            self._import_from_node_link_format(graph_data, attribute_relations)
        else:
            logger.error("不支持的JSON格式")
            return False
        
        return True
    
    def _import_from_node_link_format(self, graph_data, attribute_relations):
        """
        从NetworkX的node_link_data格式导入
        
        Args:
            graph_data: 图谱数据
            attribute_relations: 属性关系列表
        """
        with self.driver.session() as session:
            # 清空数据库
            self.clear_database()
            
            # 1. 导入所有节点
            logger.info(f"导入节点中，共 {len(graph_data['nodes'])} 个节点...")
            for node in graph_data['nodes']:
                node_id = node.get('id')
                node_name = node_id  # 节点ID即为节点名称
                
                # 获取节点类型，默认为"知识点"
                node_type = node.get('type')
                print(node_type)
                if not node_type:
                    node_type = "知识点"
                
                # 过滤节点属性
                node_attrs = {k: v for k, v in node.items() if k not in ['id']}
                
                # 检查节点是否存在
                if not self.check_node_exists(session, node_name, node_type):
                    self.create_node(session, node_name, node_type, node_attrs)
            
            # 2. 导入所有关系
            logger.info(f"导入关系中，共 {len(graph_data['links'])} 个关系...")
            for link in graph_data['links']:
                source = link.get('source')
                target = link.get('target')
                relation = link.get('relation')
                
                # 跳过自环关系
                if source == target:
                    continue
                
                # 获取源节点和目标节点的类型
                source_type = None
                target_type = None
                
                for node in graph_data['nodes']:
                    if node.get('id') == source:
                        source_type = node.get('type')
                        if not source_type:
                            source_type = "知识点"
                    if node.get('id') == target:
                        target_type = node.get('type')
                        if not target_type:
                            target_type = "知识点"
                
                # 如果找不到类型，使用默认类型
                source_type = source_type or "知识点"
                target_type = target_type or "知识点"
                
                # 检查关系是否存在
                if not self.check_relation_exists(session, source, target, relation):
                    self.create_relation(session, source, target, source_type, target_type, relation)
            
            logger.info("知识图谱导入完成")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="知识图谱JSON导入Neo4j脚本")
    
    parser.add_argument(
        "--input", 
        type=str, 
        default="D:\Desktop\knowledge-graph-deepseek\\2neo4j\json\\updated_knowledge_graph.json",
        help="知识图谱JSON文件路径"
    )
    
    parser.add_argument(
        "--uri", 
        type=str, 
        default="bolt://localhost:7687",
        help="Neo4j数据库URI"
    )
    
    parser.add_argument(
        "--user", 
        type=str, 
        default="neo4j",
        help="Neo4j用户名"
    )
    
    parser.add_argument(
        "--password", 
        type=str, 
        default="123456",
        help="Neo4j密码"
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 实例化导入器
    importer = KnowledgeGraphImporter(args.uri, args.user, args.password)
    
    try:
        # 导入JSON到Neo4j
        success = importer.import_json_to_neo4j(args.input)
        
        if success:
            logger.info("知识图谱已成功导入Neo4j")
        else:
            logger.error("知识图谱导入失败")
    finally:
        # 关闭连接
        importer.close()

if __name__ == "__main__":
    main() 