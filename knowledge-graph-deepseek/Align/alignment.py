#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
第三部分：进行实体对齐并修改知识图谱
读取候选对齐实体，执行对齐算法，修改知识图谱并保存
"""

import os
import json
import logging
import networkx as nx
import argparse
import random
from tqdm import tqdm
from collections import Counter, defaultdict
import re
import requests
from openai import OpenAI

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EntityAligner:
    """实体对齐器"""
    
    def __init__(self, kg_path, candidates_path, output_dir=None, 
                 llm_api_url=None, llm_api_key=None, model_name="deepseek-chat"):
        """
        初始化实体对齐器
        
        Args:
            kg_path: 知识图谱JSON文件路径
            candidates_path: 候选对齐实体对文件路径
            output_dir: 输出目录
            llm_api_url: 大语言模型API URL（可从环境变量DEEPSEEK_API_URL获取）
            llm_api_key: 大语言模型API密钥（可从环境变量DEEPSEEK_API_KEY获取）
            model_name: 大语言模型名称（默认使用deepseek-chat）
        """
        self.kg_path = kg_path
        self.candidates_path = candidates_path
        self.output_dir = output_dir or os.path.dirname(kg_path)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # LLM配置
        self.llm_api_url = llm_api_url or os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com")
        self.llm_api_key = llm_api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        self.model_name = model_name
        # 如果有API密钥，则默认使用LLM
        self.use_llm = bool(self.llm_api_key)
        
        # 加载知识图谱
        self.graph = self._load_knowledge_graph()
        
        # 加载候选对齐实体对
        self.candidate_pairs = self._load_candidates()
        
        # 关系类型分类
        self.attribute_relations = [
            "被定义为", "内容", "英文名", "目标", "作用", 
            "特点", "方法", "缺点", "语法", "链接"
        ]
        
        self.entity_relations = [
            "包含", "由组成", "实例", "等价", "发展为", "前提", "实现", "习题"
        ]
        
        # 对齐结果
        self.aligned_entities = []
        
        # 等价关系集合
        self.equivalence_clusters = defaultdict(set)
    
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
    
    def _load_candidates(self):
        """加载候选对齐实体对"""
        logger.info(f"从 {self.candidates_path} 加载候选对齐实体对...")
        
        try:
            with open(self.candidates_path, 'r', encoding='utf-8') as f:
                candidates = json.load(f)
            
            logger.info(f"候选对齐实体对加载成功，共有 {len(candidates)} 对")
            return candidates
        except Exception as e:
            logger.error(f"加载候选对齐实体对时出错: {str(e)}")
            raise
    
    def compute_attribute_identifiability(self, attribute, candidate_entities):
        """计算属性的可识别性"""
        # 计算属性的函数度
        attr_heads = set()
        attr_head_value_pairs = set()
        
        for entity in self.graph.nodes():
            if attribute in self.graph.nodes[entity]:
                attr_heads.add(entity)
                values = self.graph.nodes[entity][attribute]
                if isinstance(values, list):
                    for value in values:
                        attr_head_value_pairs.add((entity, value))
                else:
                    attr_head_value_pairs.add((entity, values))
        
        # 避免除以零
        fun_att = 1.0
        if attr_head_value_pairs:
            fun_att = len(attr_heads) / len(attr_head_value_pairs)
        
        # 计算属性的频率
        freq_att = 0.0
        if candidate_entities:
            count = sum(1 for e in candidate_entities if attribute in self.graph.nodes[e])
            freq_att = count / len(candidate_entities)
        
        # 计算属性的可识别性
        ident_att = fun_att * freq_att
        
        return ident_att
    
    def compute_relation_identifiability(self, relation, candidate_entities):
        """计算关系的可识别性"""
        # 计算关系的函数度
        rel_heads = set()
        rel_head_tail_pairs = set()
        
        for u, v, data in self.graph.edges(data=True):
            if data.get('relation') == relation:
                rel_heads.add(u)
                rel_head_tail_pairs.add((u, v))
        
        # 避免除以零
        fun_rel = 1.0
        if rel_head_tail_pairs:
            fun_rel = len(rel_heads) / len(rel_head_tail_pairs)
        
        # 计算关系的频率
        freq_rel = 0.0
        if candidate_entities:
            count = sum(1 for e in candidate_entities if any(
                data.get('relation') == relation for _, v, data in self.graph.out_edges(e, data=True)
            ))
            freq_rel = count / len(candidate_entities)
        
        # 计算关系的可识别性
        ident_rel = fun_rel * freq_rel
        
        return ident_rel
    
    def select_informative_features(self, entity, candidate_entities, top_k=3):
        """选择最具信息量的特征（属性和关系）"""
        # 计算所有属性的可识别性
        attribute_idents = {}
        for attr in self.graph.nodes[entity]:
            if attr != 'type':
                ident = self.compute_attribute_identifiability(attr, candidate_entities)
                attribute_idents[attr] = ident
        
        # 找出实体参与的所有关系
        involved_relations = set()
        for _, _, data in self.graph.out_edges(entity, data=True):
            if 'relation' in data:
                involved_relations.add(data['relation'])
        
        # 计算所有关系的可识别性
        relation_idents = {}
        for rel in involved_relations:
            ident = self.compute_relation_identifiability(rel, candidate_entities)
            relation_idents[rel] = ident
        
        # 合并并排序
        all_features = {**attribute_idents, **relation_idents}
        
        # 选择top-k特征
        top_features = sorted(all_features.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return [f[0] for f in top_features]
    
    def generate_prompt(self, entity1, entity2, features):
        """生成对齐提示"""
        # 构建源实体信息
        entity1_info = f"实体A: {entity1}"
        if 'type' in self.graph.nodes[entity1]:
            entity1_info += f"\n类型: {self.graph.nodes[entity1]['type']}"
        
        # 添加特征信息
        for feature in features:
            if feature in self.graph.nodes[entity1]:
                values = self.graph.nodes[entity1][feature]
                if isinstance(values, list):
                    entity1_info += f"\n{feature}: {', '.join(values[:3])}"
                else:
                    entity1_info += f"\n{feature}: {values}"
            else:
                # 检查是否为关系特征
                rel_info = []
                for _, v, data in self.graph.out_edges(entity1, data=True):
                    if data.get('relation') == feature:
                        rel_info.append(v)
                
                if rel_info:
                    entity1_info += f"\n关系[{feature}]: {', '.join(rel_info[:3])}"
        
        # 构建目标实体信息
        entity2_info = f"实体B: {entity2}"
        if 'type' in self.graph.nodes[entity2]:
            entity2_info += f"\n类型: {self.graph.nodes[entity2]['type']}"
        
        # 添加特征信息
        for feature in features:
            if feature in self.graph.nodes[entity2]:
                values = self.graph.nodes[entity2][feature]
                if isinstance(values, list):
                    entity2_info += f"\n{feature}: {', '.join(values[:3])}"
                else:
                    entity2_info += f"\n{feature}: {values}"
            else:
                # 检查是否为关系特征
                rel_info = []
                for _, v, data in self.graph.out_edges(entity2, data=True):
                    if data.get('relation') == feature:
                        rel_info.append(v)
                
                if rel_info:
                    entity2_info += f"\n关系[{feature}]: {', '.join(rel_info[:3])}"
        
        # 构建完整提示
        prompt = f"""
你是一个专业的知识图谱实体对齐专家，你需要判断下面的两个实体是否表示相同的概念。请分析以下信息:

{entity1_info}

{entity2_info}

问题: 实体A和实体B是否表示相同的概念？请回答"是"或"否"，不要有任何额外解释。
"""
        return prompt
    
    def call_llm_api(self, prompt):
        """调用大语言模型API"""
        try:
            if not self.use_llm:
                logger.warning("LLM API未配置，无法调用")
                return None
            
            # 使用OpenAI类调用API
            client = OpenAI(api_key=self.llm_api_key, base_url=self.llm_api_url)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的知识图谱实体对齐助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 低温度，更确定性的回答
                max_tokens=50  # 只需要简短回答
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"调用LLM API时出错: {str(e)}")
            return None
    
    def multi_round_voting(self, entity1, entity2, top_k_features=3, num_rounds=3):
        """多轮投票对齐"""
        candidates = [entity2]
        
        # 选择信息量最大的特征
        features = self.select_informative_features(entity1, candidates, top_k_features)
        
        # 如果使用大模型
        if self.use_llm:
            # 多轮投票
            votes = []
            for _ in range(num_rounds):
                prompt = self.generate_prompt(entity1, entity2, features)
                response = self.call_llm_api(prompt)
                
                # 解析响应
                if response:
                    if "是" in response or "相同" in response or "表示同一概念" in response:
                        votes.append(True)
                    else:
                        votes.append(False)
            
            # 统计投票结果
            if votes:
                is_aligned = sum(votes) > len(votes) / 2
                confidence = sum(votes) / len(votes) if is_aligned else 1 - sum(votes) / len(votes)
                return is_aligned, confidence
        
        # 如果没有使用大模型，基于相似度得分判断
        score = next((c["combined_score"] for c in self.candidate_pairs 
                      if c["entity1"] == entity1 and c["entity2"] == entity2), 0.0)
        
        is_aligned = score >= 0.8  # 使用较高阈值作为直接对齐的标准
        return is_aligned, score
    
    def align_entities(self, confidence_threshold=0.7, top_k_features=3, num_rounds=3):
        """执行实体对齐"""
        logger.info("开始执行实体对齐...")
        
        aligned_results = []
        
        for pair in tqdm(self.candidate_pairs, desc="实体对齐"):
            entity1 = pair["entity1"]
            entity2 = pair["entity2"]
            
            # 多轮投票
            is_aligned, confidence = self.multi_round_voting(
                entity1, entity2, top_k_features, num_rounds
            )
            
            # 如果对齐且置信度足够高
            if is_aligned and confidence >= confidence_threshold:
                aligned_results.append({
                    "entity1": entity1,
                    "entity2": entity2,
                    "confidence": float(confidence),
                    "features": self.select_informative_features(entity1, [entity2], top_k_features)
                })
                
                # 将对齐实体添加到同一等价类中
                self.equivalence_clusters[entity1].add(entity2)
                self.equivalence_clusters[entity2].add(entity1)
        
        # 传递等价关系（如果A=B且B=C，则A=C）
        self._propagate_equivalence()
        
        # 保存结果
        self.aligned_entities = aligned_results
        
        logger.info(f"实体对齐完成，找到 {len(aligned_results)} 对对齐实体")
        return aligned_results
    
    def _propagate_equivalence(self):
        """传递等价关系"""
        # 标记是否有新的等价关系
        has_new_relations = True
        
        while has_new_relations:
            has_new_relations = False
            
            # 复制当前等价关系，避免在迭代过程中修改
            current_clusters = {k: set(v) for k, v in self.equivalence_clusters.items()}
            
            # 对每个实体，传递其等价关系
            for entity, equivalents in current_clusters.items():
                for equivalent in equivalents:
                    # 获取equivalent的等价实体
                    indirect_equivalents = current_clusters.get(equivalent, set())
                    
                    # 添加传递关系
                    for indirect in indirect_equivalents:
                        if indirect != entity and indirect not in self.equivalence_clusters[entity]:
                            self.equivalence_clusters[entity].add(indirect)
                            has_new_relations = True
    
    def update_knowledge_graph(self):
        """基于对齐结果更新知识图谱"""
        logger.info("开始更新知识图谱...")
        
        # 为每个等价类选择一个代表实体
        entity_representatives = {}
        
        # 按名称长度和连接度排序，选择最具代表性的实体
        for entity, equivalents in self.equivalence_clusters.items():
            if entity not in entity_representatives:
                # 将entity及其所有等价实体作为一个等价类
                equiv_class = {entity} | equivalents
                
                # 选择最具代表性的实体（连接度最高，名称最短）
                representative = max(
                    equiv_class, 
                    key=lambda e: (self.graph.degree(e), -len(e))
                )
                
                # 将该等价类中的所有实体映射到代表实体
                for e in equiv_class:
                    entity_representatives[e] = representative
        
        # 创建修改后的图
        new_graph = nx.DiGraph()
        
        # 复制节点和属性
        for node, attrs in self.graph.nodes(data=True):
            # 如果节点有代表实体，使用代表实体
            rep = entity_representatives.get(node, node)
            
            # 如果代表实体已存在，合并属性
            if rep in new_graph:
                for attr, value in attrs.items():
                    if attr in new_graph.nodes[rep]:
                        if isinstance(new_graph.nodes[rep][attr], list):
                            if isinstance(value, list):
                                new_graph.nodes[rep][attr].extend(value)
                            else:
                                new_graph.nodes[rep][attr].append(value)
                        else:
                            if isinstance(value, list):
                                new_graph.nodes[rep][attr] = [new_graph.nodes[rep][attr]] + value
                            else:
                                new_graph.nodes[rep][attr] = [new_graph.nodes[rep][attr], value]
                    else:
                        new_graph.nodes[rep][attr] = value
            else:
                new_graph.add_node(rep, **attrs)
                
                # 为等价实体添加等价关系属性
                if node in self.equivalence_clusters and node == rep:
                    new_graph.nodes[rep]['equivalent_entities'] = list(self.equivalence_clusters[node])
        
        # 复制边和关系
        for u, v, attrs in self.graph.edges(data=True):
            # 获取源和目标节点的代表实体
            rep_u = entity_representatives.get(u, u)
            rep_v = entity_representatives.get(v, v)
            
            # 添加边（避免自环）
            if rep_u != rep_v:
                if not new_graph.has_edge(rep_u, rep_v):
                    new_graph.add_edge(rep_u, rep_v, **attrs)
                else:
                    # 合并边属性
                    for attr, value in attrs.items():
                        new_graph[rep_u][rep_v][attr] = value
        
        # 添加等价关系边
        for entity, equivalents in self.equivalence_clusters.items():
            rep = entity_representatives.get(entity, entity)
            
            for equiv in equivalents:
                equiv_rep = entity_representatives.get(equiv, equiv)
                
                # 避免在代表实体之间添加等价边
                if rep != equiv_rep:
                    new_graph.add_edge(rep, equiv_rep, relation="等价")
        
        logger.info(f"知识图谱更新完成，节点数从 {self.graph.number_of_nodes()} 减少到 {new_graph.number_of_nodes()}")
        
        # 更新图谱
        self.graph = new_graph
        return new_graph
    
    def save_results(self):
        """保存对齐结果和更新后的图谱"""
        # 保存对齐实体结果
        alignment_file = os.path.join(self.output_dir, "entity_alignment_results.json")
        with open(alignment_file, 'w', encoding='utf-8') as f:
            json.dump(self.aligned_entities, f, ensure_ascii=False, indent=2)
        
        logger.info(f"实体对齐结果已保存至 {alignment_file}")
        
        # 保存等价类
        equivalence_file = os.path.join(self.output_dir, "equivalence_clusters.json")
        equivalence_data = {k: list(v) for k, v in self.equivalence_clusters.items()}
        with open(equivalence_file, 'w', encoding='utf-8') as f:
            json.dump(equivalence_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"等价类已保存至 {equivalence_file}")
        
        # 保存更新后的知识图谱
        updated_kg_file = os.path.join(self.output_dir, "updated_knowledge_graph.json")
        graph_data = nx.node_link_data(self.graph)
        with open(updated_kg_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"更新后的知识图谱已保存至 {updated_kg_file}")
        
        # 保存统计信息
        stats = {
            "original_nodes_count": len(self.candidate_pairs),
            "aligned_entities_count": len(self.aligned_entities),
            "equivalence_clusters_count": len(self.equivalence_clusters),
            "updated_nodes_count": self.graph.number_of_nodes(),
            "updated_edges_count": self.graph.number_of_edges()
        }
        
        stats_file = os.path.join(self.output_dir, "alignment_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        logger.info(f"统计信息已保存至 {stats_file}")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="第三部分：进行实体对齐并修改知识图谱")
    
    parser.add_argument(
        "--kg_path", 
        type=str, 
        default="/root/autodl-tmp/knowledge-graph-deepseek/Align/output/knowledge_graph.json",
        help="知识图谱JSON文件路径"
    )
    
    parser.add_argument(
        "--candidates_path", 
        type=str, 
        default="/root/autodl-tmp/knowledge-graph-deepseek/Align/output/candidate_pairs.json",
        help="候选对齐实体对文件路径"
    )
    
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="/root/autodl-tmp/knowledge-graph-deepseek/Align/output",
        help="输出目录"
    )
    
    parser.add_argument(
        "--llm_api_url", 
        type=str, 
        default=None,
        help="大语言模型API URL（默认从环境变量DEEPSEEK_API_URL获取）"
    )
    
    parser.add_argument(
        "--llm_api_key", 
        type=str, 
        default=None,
        help="大语言模型API密钥（默认从环境变量DEEPSEEK_API_KEY获取）"
    )
    
    parser.add_argument(
        "--model_name", 
        type=str, 
        default="deepseek-chat",
        help="大语言模型名称（默认为deepseek-chat）"
    )
    
    parser.add_argument(
        "--confidence_threshold", 
        type=float, 
        default=0.7,
        help="置信度阈值"
    )
    
    parser.add_argument(
        "--top_k_features", 
        type=int, 
        default=3,
        help="选择的Top-K特征数量"
    )
    
    parser.add_argument(
        "--num_rounds", 
        type=int, 
        default=3,
        help="多轮投票的轮数"
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 检查环境变量
    if not args.llm_api_key and not os.environ.get("DEEPSEEK_API_KEY"):
        logger.warning("未提供API密钥，将不使用大语言模型进行对齐。请设置环境变量DEEPSEEK_API_KEY或使用--llm_api_key参数提供API密钥。")
        logger.warning("示例: export DEEPSEEK_API_KEY=your_api_key")
    
    if not args.llm_api_url and not os.environ.get("DEEPSEEK_API_URL"):
        logger.info("未提供API URL，将使用默认的DeepSeek API URL: https://api.deepseek.com/v1")
        logger.info("可通过设置环境变量DEEPSEEK_API_URL或使用--llm_api_url参数提供自定义API URL。")
    
    # 实例化实体对齐器
    aligner = EntityAligner(
        args.kg_path, 
        args.candidates_path, 
        args.output_dir,
        args.llm_api_url,
        args.llm_api_key,
        args.model_name
    )
    
    # 提示当前使用的模式
    if aligner.use_llm:
        logger.info(f"将使用大语言模型 {aligner.model_name} 进行实体对齐")
    else:
        logger.info("将使用基于相似度的方法进行实体对齐")
    
    # 执行实体对齐
    aligner.align_entities(
        confidence_threshold=args.confidence_threshold,
        top_k_features=args.top_k_features,
        num_rounds=args.num_rounds
    )
    
    # 更新知识图谱
    aligner.update_knowledge_graph()
    
    # 保存结果
    aligner.save_results()
    
    logger.info("实体对齐和知识图谱更新完成")

if __name__ == "__main__":
    main() 