#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
第二部分：读取知识图谱并筛选候选对齐实体
读取保存的知识图谱，计算实体嵌入，筛选候选对齐实体对
"""

import os
import json
import logging
import networkx as nx
import argparse
import jieba
import numpy as np
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EntityCandidateFinder:
    """实体候选对齐发现器"""
    
    def __init__(self, kg_path, output_dir=None):
        """
        初始化实体候选对齐发现器
        
        Args:
            kg_path: 知识图谱JSON文件路径
            output_dir: 输出目录
        """
        self.kg_path = kg_path
        self.output_dir = output_dir or os.path.dirname(kg_path)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 加载知识图谱
        self.graph = self._load_knowledge_graph()
        
        # 实体嵌入模型
        self.model = SentenceTransformer('all-mpnet-base-v2')
        
        # 实体嵌入
        self.entity_embeddings = {}
        
        # 候选对齐实体对
        self.candidate_pairs = []
    
    def _load_knowledge_graph(self):
        """加载知识图谱"""
        logger.info(f"从 {self.kg_path} 加载知识图谱...")
        
        try:
            with open(self.kg_path, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            
            graph = nx.node_link_graph(graph_data)
            
            logger.info(f"知识图谱加载成功，共有 {graph.number_of_nodes()} 个节点和 {graph.number_of_edges()} 条边")
            return graph
        except Exception as e:
            logger.error(f"加载知识图谱时出错: {str(e)}")
            raise
    
    def compute_entity_embeddings(self):
        """计算实体嵌入"""
        logger.info("计算实体嵌入...")
        
        entities = list(self.graph.nodes())
        
        for entity in tqdm(entities, desc="生成实体嵌入"):
            # 获取实体文本特征
            entity_text = entity  # 实体名称
            
            # 附加实体属性信息
            attributes = []
            for attr, value in self.graph.nodes[entity].items():
                if attr != 'type' and isinstance(value, list):
                    attributes.extend(value)
                elif attr != 'type' and isinstance(value, str):
                    attributes.append(value)
            
            # 构建富文本表示
            rich_text = entity_text
            if attributes:
                rich_text += ": " + " ".join(attributes[:5])  # 限制属性数量
            
            # 计算嵌入
            embedding = self.model.encode(rich_text)
            self.entity_embeddings[entity] = embedding
        
        logger.info(f"完成实体嵌入计算，共 {len(self.entity_embeddings)} 个实体")
    
    def compute_name_similarity(self, entity1, entity2):
        """计算实体名称相似度"""
        # 使用jieba分词+Jaccard系数
        words1 = set(jieba.cut(entity1))
        words2 = set(jieba.cut(entity2))
        
        if not (words1 and words2):
            return 0.0
        
        jaccard_sim = len(words1.intersection(words2)) / len(words1.union(words2))
        return jaccard_sim
    
    def compute_embedding_similarity(self, entity1, entity2):
        """计算实体嵌入相似度"""
        if entity1 in self.entity_embeddings and entity2 in self.entity_embeddings:
            emb_sim = cosine_similarity(
                [self.entity_embeddings[entity1]], 
                [self.entity_embeddings[entity2]]
            )[0][0]
            return float(emb_sim)
        return 0.0
    
    def find_candidates(self, name_similarity_threshold=0.5, embedding_similarity_threshold=0.6, max_candidates=500):
        """寻找候选对齐实体对"""
        logger.info("开始寻找候选对齐实体对...")
        
        # 确保已计算实体嵌入
        if not self.entity_embeddings:
            self.compute_entity_embeddings()
        
        entities = list(self.graph.nodes())
        candidate_pairs = []
        
        # 生成候选对
        for i in tqdm(range(len(entities)-1), desc="对比实体对"):
            for j in range(i+1, len(entities)):
                entity1 = entities[i]
                entity2 = entities[j]
                
                # 如果实体类型不同，跳过
                if (self.graph.nodes[entity1].get('type') != self.graph.nodes[entity2].get('type') and 
                    self.graph.nodes[entity1].get('type') and self.graph.nodes[entity2].get('type')):
                    continue
                
                # 计算名称相似度
                name_sim = self.compute_name_similarity(entity1, entity2)
                
                if name_sim >= name_similarity_threshold:
                    # 计算嵌入相似度
                    emb_sim = self.compute_embedding_similarity(entity1, entity2)
                    
                    if emb_sim >= embedding_similarity_threshold:
                        # 计算综合得分
                        combined_score = 0.4 * name_sim + 0.6 * emb_sim
                        
                        # 收集候选实体对信息
                        candidate_info = {
                            "entity1": entity1,
                            "entity2": entity2,
                            "entity1_type": self.graph.nodes[entity1].get('type', "未知"),
                            "entity2_type": self.graph.nodes[entity2].get('type', "未知"),
                            "name_similarity": float(name_sim),
                            "embedding_similarity": float(emb_sim),
                            "combined_score": float(combined_score)
                        }
                        
                        candidate_pairs.append(candidate_info)
        
        # 按综合得分排序
        candidate_pairs.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # 限制候选对数量
        if max_candidates and len(candidate_pairs) > max_candidates:
            candidate_pairs = candidate_pairs[:max_candidates]
        
        self.candidate_pairs = candidate_pairs
        
        logger.info(f"找到 {len(candidate_pairs)} 对候选实体对齐")
        return candidate_pairs
    
    def save_candidates(self, filename="candidate_pairs.json"):
        """保存候选对齐实体对"""
        if not self.candidate_pairs:
            logger.warning("没有候选对齐实体对可保存")
            return
        
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.candidate_pairs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"候选对齐实体对已保存至 {output_path}")
    
    def get_entity_attributes(self, entity, max_attrs=3):
        """获取实体的主要属性"""
        attrs = {}
        
        if entity in self.graph:
            node_data = self.graph.nodes[entity]
            
            # 优先获取重要属性
            priority_attrs = ["被定义为", "内容", "英文名", "作用", "特点"]
            
            # 按优先级收集属性
            for attr in priority_attrs:
                if attr in node_data and len(attrs) < max_attrs:
                    attrs[attr] = node_data[attr]
            
            # 如果还没收集够，添加其他属性
            for attr, value in node_data.items():
                if attr != "type" and attr not in attrs and len(attrs) < max_attrs:
                    attrs[attr] = value
        
        return attrs
    
    def summarize_candidates(self, top_n=10):
        """总结候选对齐实体对"""
        if not self.candidate_pairs:
            logger.warning("没有候选对齐实体对可总结")
            return
        
        logger.info(f"Top {min(top_n, len(self.candidate_pairs))} 候选对齐实体对:")
        
        for i, candidate in enumerate(self.candidate_pairs[:top_n]):
            entity1 = candidate["entity1"]
            entity2 = candidate["entity2"]
            score = candidate["combined_score"]
            
            # 获取实体属性
            entity1_attrs = self.get_entity_attributes(entity1)
            entity2_attrs = self.get_entity_attributes(entity2)
            
            logger.info(f"{i+1}. 得分: {score:.4f}, 实体对: {entity1} - {entity2}")
            
            if entity1_attrs:
                attrs_str = ", ".join([f"{k}: {v[:30]}..." if isinstance(v, str) and len(v) > 30 
                                      else f"{k}: {v}" for k, v in entity1_attrs.items()])
                logger.info(f"   实体1属性: {attrs_str}")
            
            if entity2_attrs:
                attrs_str = ", ".join([f"{k}: {v[:30]}..." if isinstance(v, str) and len(v) > 30 
                                      else f"{k}: {v}" for k, v in entity2_attrs.items()])
                logger.info(f"   实体2属性: {attrs_str}")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="第二部分：读取知识图谱并筛选候选对齐实体")
    
    parser.add_argument(
        "--kg_path", 
        type=str, 
        default="/root/autodl-tmp/knowledge-graph-deepseek/Align/output/knowledge_graph.json",
        help="知识图谱JSON文件路径"
    )
    
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="/root/autodl-tmp/knowledge-graph-deepseek/Align/output",
        help="输出目录"
    )
    
    parser.add_argument(
        "--name_sim_threshold", 
        type=float, 
        default=0.5,
        help="名称相似度阈值"
    )
    
    parser.add_argument(
        "--emb_sim_threshold", 
        type=float, 
        default=0.6,
        help="嵌入相似度阈值"
    )
    
    parser.add_argument(
        "--max_candidates", 
        type=int, 
        default=500,
        help="最大候选对齐实体对数量"
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 实例化实体候选对齐发现器
    finder = EntityCandidateFinder(args.kg_path, args.output_dir)
    
    # 计算实体嵌入
    finder.compute_entity_embeddings()
    
    # 寻找候选对齐实体对
    finder.find_candidates(
        name_similarity_threshold=args.name_sim_threshold,
        embedding_similarity_threshold=args.emb_sim_threshold,
        max_candidates=args.max_candidates
    )
    
    # 保存候选对齐实体对
    finder.save_candidates()
    
    # 总结候选对齐实体对
    finder.summarize_candidates(top_n=10)
    
    logger.info("候选对齐实体筛选完成")

if __name__ == "__main__":
    main() 