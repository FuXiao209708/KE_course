#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
第一部分：知识图谱构建与保存
从CSV三元组构建知识图谱，并将其保存为JSON格式
"""

import os
import csv
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from tqdm import tqdm
import json
import logging
import argparse

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    """知识图谱构建工具"""
    
    def __init__(self, csv_dir, output_dir=None):
        """
        初始化知识图谱构建工具
        
        Args:
            csv_dir: CSV三元组文件目录
            output_dir: 输出目录
        """
        self.csv_dir = csv_dir
        self.output_dir = output_dir or os.path.join(os.path.dirname(csv_dir), "knowledge_graph")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 图谱相关变量
        self.graph = nx.DiGraph()
        self.entity_info = defaultdict(dict)  # 存储实体信息
        self.entity_types = defaultdict(str)  # 存储实体类型
        self.triples = []  # 存储所有三元组
        
        # 关系类型和描述
        self.relation_schema = {
            # 属性schema
            "被定义为": "表示一个实体或概念的定义或解释",
            "内容": "表示一个实体或概念的具体内容",
            "英文名": "表示一个实体或概念的英文名称或缩写",
            "目标": "表示一个实体或概念的目标或意图",
            "作用": "表示一个实体或概念的功能或用途",
            "特点": "表示一个实体或概念的特征或特性",
            "方法": "表示一个实体或概念的实现方法或技术",
            "缺点": "表示一个实体或概念的不足或局限性",
            "语法": "表示一个实体或概念的语法规则或格式",
            "链接": "表示一个实体或概念的相关网络资源链接",
            
            # 实体间的relation
            "包含": "表示主语知识点有宾语的分支",
            "由组成":"表示主语知识点由宾语知识点组成",
            "实例": "表示主语知识点是宾语的一种具体体现",
            "等价": "表示两个知识点含义相同",
            "发展为": "表示主语知识点发展成为宾语知识点（因果关系）",
            "前提": "表示主语知识点需要宾语作为前提",
            "实现": "表示主语知识点可以实现宾语的要求/达成宾语",
            "习题": "表示主语知识点有宾语的习题"
        }
        
        # 属性关系和实体间关系的分类
        self.attribute_relations = [
            "被定义为", "内容", "英文名", "目标", "作用", 
            "特点", "方法", "缺点", "语法", "链接"
        ]
        
        self.entity_relations = [
            "包含", "由组成", "实例", "等价", "发展为", "前提", "实现", "习题"
        ]
    
    def load_csv_files(self):
        """加载所有CSV文件中的三元组数据"""
        logger.info(f"开始加载CSV文件...")
        
        csv_files = [f for f in os.listdir(self.csv_dir) if f.endswith('.csv')]
        
        for csv_file in tqdm(csv_files, desc="加载CSV文件"):
            file_path = os.path.join(self.csv_dir, csv_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'subject' in row and 'relation' in row and 'object' in row:
                            subject = row['subject'].strip()
                            relation = row['relation'].strip()
                            object_ = row['object'].strip()
                            
                            # 获取实体类型信息
                            if 'subject_type' in row:
                                self.entity_types[subject] = row['subject_type'].strip()
                            
                            if 'object_type' in row:
                                self.entity_types[object_] = row['object_type'].strip()
                            
                            # 存储三元组
                            self.triples.append((subject, relation, object_))
                            
                            # 添加到图中
                            if relation in self.attribute_relations:
                                # 属性三元组
                                if relation not in self.entity_info[subject]:
                                    self.entity_info[subject][relation] = []
                                self.entity_info[subject][relation].append(object_)
                            else:
                                # 实体关系三元组
                                self.graph.add_edge(subject, object_, relation=relation)
            except Exception as e:
                logger.error(f"处理文件 {csv_file} 时出错: {str(e)}")
        
        logger.info(f"共加载 {len(self.triples)} 个三元组，包含 {len(self.entity_types)} 个不同实体")
    
    def build_knowledge_graph(self):
        """构建知识图谱"""
        logger.info("构建知识图谱...")
        
        # 加载CSV文件中的三元组
        self.load_csv_files()
        
        # 添加实体属性到图中
        for entity, attributes in self.entity_info.items():
            if entity not in self.graph:
                self.graph.add_node(entity)
            
            # 设置节点属性
            self.graph.nodes[entity]['type'] = self.entity_types.get(entity, "未知")
            
            for attr_key, attr_values in attributes.items():
                self.graph.nodes[entity][attr_key] = attr_values
        
        logger.info(f"知识图谱构建完成，共有 {self.graph.number_of_nodes()} 个节点和 {self.graph.number_of_edges()} 条边")
        
        return self.graph
    
    def save_knowledge_graph(self, format='json'):
        """保存知识图谱"""
        logger.info(f"保存知识图谱，格式: {format}")
        
        if format == 'json':
            graph_data = nx.node_link_data(self.graph)
            output_file = os.path.join(self.output_dir, 'knowledge_graph.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            logger.info(f"知识图谱已保存至 {output_file}")
        
        # 图谱统计信息
        kg_stats = {
            "nodes_count": self.graph.number_of_nodes(),
            "edges_count": self.graph.number_of_edges(),
            "entity_types_count": len(set(self.entity_types.values())),
            "relation_types_count": len(set([d.get('relation') for _, _, d in self.graph.edges(data=True)])),
            "attribute_triples_count": sum(len(attrs.values()) for attrs in self.entity_info.values())
        }
        
        stats_file = os.path.join(self.output_dir, 'kg_stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(kg_stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"知识图谱统计信息已保存至 {stats_file}")
    
    def visualize_graph(self, max_nodes=100):
        """可视化知识图谱（节点数量限制）"""
        logger.info("正在可视化知识图谱...")
        
        # 如果节点太多，随机取一部分
        if self.graph.number_of_nodes() > max_nodes:
            logger.info(f"节点数量过多，随机选择 {max_nodes} 个节点进行可视化")
            subgraph_nodes = list(self.graph.nodes())[:max_nodes]
            subgraph = self.graph.subgraph(subgraph_nodes)
        else:
            subgraph = self.graph
        
        plt.figure(figsize=(20, 20))
        pos = nx.spring_layout(subgraph)
        
        # 绘制节点
        nx.draw_networkx_nodes(subgraph, pos, node_size=500, alpha=0.8)
        
        # 绘制边
        edge_labels = {(u, v): d['relation'] for u, v, d in subgraph.edges(data=True)}
        nx.draw_networkx_edges(subgraph, pos, width=1.0, alpha=0.5)
        nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels, font_size=12)
        
        # 绘制节点标签
        nx.draw_networkx_labels(subgraph, pos, font_size=12, font_family='SimHei')
        
        plt.axis('off')
        plt.tight_layout()
        
        # 保存图像
        output_file = os.path.join(self.output_dir, 'knowledge_graph_visualization.png')
        plt.savefig(output_file, dpi=300)
        plt.close()
        
        logger.info(f"知识图谱可视化已保存至 {output_file}")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="第一部分：构建知识图谱并保存")
    
    parser.add_argument(
        "--csv_dir", 
        type=str, 
        default="/root/autodl-tmp/knowledge-graph-deepseek/output/test",
        help="CSV三元组文件目录"
    )
    
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="/root/autodl-tmp/knowledge-graph-deepseek/Align/output",
        help="输出目录"
    )
    
    parser.add_argument(
        "--visualize", 
        action="store_true",
        help="是否可视化知识图谱"
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 构建知识图谱
    builder = KnowledgeGraphBuilder(args.csv_dir, args.output_dir)
    graph = builder.build_knowledge_graph()
    builder.save_knowledge_graph()
    
    # 可视化（如果需要）
    if args.visualize:
        builder.visualize_graph(max_nodes=100)
    
    logger.info("知识图谱构建完成")

if __name__ == "__main__":
    main() 