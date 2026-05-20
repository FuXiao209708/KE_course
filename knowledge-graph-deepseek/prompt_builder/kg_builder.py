#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱构建工具
这个脚本实现了使用大语言模型从《知识工程》教材中构建知识图谱的六个步骤
"""

import json
import os
import requests
from typing import List, Dict, Tuple, Any, Optional
import logging
from openai import OpenAI
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    """知识图谱构建工具"""
    
    def __init__(self, llm_api_key: str = None, llm_api_url: str = None, api_version: str = "v1"):
        """
        初始化知识图谱构建工具
        
        Args:
            llm_api_key: DeepSeek API密钥
            llm_api_url: DeepSeek API URL
        """
        self.llm_api_key = llm_api_key or os.getenv("DEESEEK_API_KEY")
        self.llm_api_url = llm_api_url or os.getenv("DEESEEK_API_URL")
        
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
            "包含", "由组成","实例", "等价", "发展为", "前提", "实现", "习题"
        ]
        
        # 存储合成样本
        self.synthetic_samples = {}
        
        # 实体类型
        self.entity_types = [
            "知识图谱", "知识表示", "知识存储", "知识抽取", "知识融合", 
            "知识推理", "语义搜索", "知识问答", "链接", "知识图谱项目","属性文本"
        ]
        
    def call_llm_api(self, prompt: str) -> str:
        """
        调用DeepSeek API
        
        Args:
            prompt: 提示词
            
        Returns:
            DeepSeek的响应文本
        """
        try:
            # 使用DeepSeek的API调用方式
            client = OpenAI(api_key=self.llm_api_key, base_url=self.llm_api_url)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"调用DeepSeek API时出错: {str(e)}")
            return ""
    
    def step1_generate_synthetic_samples(self, relation: str, k: int = 5) -> Dict[str, List[str]]:
        """
        步骤1: 生成合成样本
        
        Args:
            relation: 关系类型
            k: 生成数量
            
        Returns:
            包含同义词、句子和重述句子的字典
        """
        description = self.relation_schema.get(relation, "")
        if not description:
            logger.warning(f"未找到关系 '{relation}' 的描述")
            return {"synonyms": [], "sentences": [], "rewritten": []}
        
        # 第一轮对话：生成同义词
        synonyms_prompt = f"""
给定一个关系类型：{relation}，你的任务是为这个关系生成 {k} 个同义词或语义相关的表达。
这个关系的描述是：{description}。生成的同义词需要满足以下要求：
1. 同义词应明确或隐含地与知识工程领域的关系 {relation} 一致。
2. 不同的同义词之间应具有多样性。
3. 同义词可以是一个单词或短语。

请按照 Python 列表的格式输出：[synonyms1, synonyms2, ..., synonyms{k}]
"""
        synonyms_response = self.call_llm_api(synonyms_prompt)
        
        # 提取同义词列表（简化处理，实际使用时需要更健壮的解析）
        try:
            # 尝试解析返回的JSON列表
            synonyms = json.loads(synonyms_response.strip())
        except json.JSONDecodeError:
            # 如果不是有效的JSON，尝试其他方式提取
            synonyms_match = re.search(r'\[(.*?)\]', synonyms_response, re.DOTALL)
            if synonyms_match:
                synonyms_str = synonyms_match.group(1)
                # 分割并清理引号和空格
                synonyms = [s.strip().strip('"\'') for s in synonyms_str.split(',')]
            else:
                logger.warning(f"无法从响应中提取同义词列表: {synonyms_response}")
                synonyms = []
        
        # 第二轮对话：生成包含该关系的句子
        sentences_prompt = f"""
假设你是一个高级的语言模型，专门用于生成《知识工程》领域的文本数据。你的任务是生成 {k} 个包含特定关系的合成句子，关系类型为：{relation}。这个关系的描述是：{description}。

生成的句子需要明确或隐含地展示这种关系，并且具有信息性。请按照以下格式输出：
句子：[你生成的句子]
关系：[(entity1, {relation}, entity2), (entity3, {relation}, entity4), ...]

关系列表可以包含一到三个关系元组。生成的样本需要满足以下要求：
1. 关系必须与之前定义的关系一致。
2. 头实体和尾实体必须出现在原始句子中。
3. 将头实体和尾实体拆分为多个具有相同关系的元组。
4. 生成不同长度和复杂度的句子，包括简单句、复合句和复杂句。
5. 确保头实体和尾实体的类型具有广泛且现实的多样性，以反映真实场景。
6. 句子内容应与《知识工程》领域的知识点相关。
"""
        sentences_response = self.call_llm_api(sentences_prompt)
        
        # 解析句子和关系（简化处理，实际实现需要更复杂的解析）
        sentences = []
        sentences_with_relations = []
        
        # 简单的解析示例，实际情况可能需要更复杂的解析
        for line in sentences_response.split('\n'):
            if line.startswith("句子："):
                sentences.append(line.replace("句子：", "").strip())
            elif line.startswith("关系："):
                sentences_with_relations.append(line)
        
        # 第三轮对话：句子重述
        rewritten_sentences = []
        for sentence in sentences[:min(len(sentences), k)]:
            # 为简化起见，我们只使用第一个句子进行重述
            rewrite_prompt = f"""
给定一个句子：{sentence}，以及其关系标注：{relation}，你的任务是生成 {k} 个改写的句子。这些句子需要巧妙地隐含原始句子中明确表达的关系，同时增强语义深度并多样化句子结构。请按照以下格式输出：

原句：{sentence}
改写句子：[改写后的句子1, 改写后的句子2, ..., 改写后的句子{k}]

改写的句子需要满足以下要求：
1. 保留实体：确保原始句子中的头实体和尾实体出现在每个改写的版本中。
2. 多样性和真实性：改写的句子应涵盖广泛的句子结构和场景，反映真实且多样化的场景。
3. 句子内容应与《知识工程》领域的知识点相关。
"""
            rewrite_response = self.call_llm_api(rewrite_prompt)
            
            # 提取重写的句子
            rewritten_match = re.search(r'改写句子：\[(.*?)\]', rewrite_response, re.DOTALL)
            if rewritten_match:
                rewritten_str = rewritten_match.group(1)
                # 分割并清理
                current_rewritten = [s.strip().strip('"\'') for s in rewritten_str.split(',')]
                rewritten_sentences.extend(current_rewritten)
            else:
                # 如果没有匹配到格式化的输出，尝试按行分割
                for line in rewrite_response.split('\n'):
                    if not line.startswith("原句：") and line.strip():
                        rewritten_sentences.append(line.strip())
        
        # 保存合成样本
        self.synthetic_samples[relation] = {
            "synonyms": synonyms,
            "sentences": sentences,
            "sentences_with_relations": sentences_with_relations,
            "rewritten": rewritten_sentences
        }
        
        return self.synthetic_samples[relation]
    
    def generate_all_synthetic_samples(self, k: int = 5):
        """
        为所有关系类型生成合成样本
        
        Args:
            k: 每种类型生成的样本数量
        """
        for relation in self.relation_schema.keys():
            logger.info(f"为关系 '{relation}' 生成合成样本")
            self.step1_generate_synthetic_samples(relation, k)
        
        logger.info(f"合成样本生成完成，共 {len(self.synthetic_samples)} 种关系类型")
    
    def step2_extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        步骤2: 从文本中抽取知识点实体及其类型
        
        Args:
            text: 输入文本
            
        Returns:
            抽取出的实体及其类型的列表
        """
        prompt = f"""
你是一名知识工程领域的专家，专门负责从文本中抽取核心概念和术语及其类型，以构建结构化的知识体系。请遵循以下要求，从输入文本中精准识别知识工程相关的专业术语（即知识点实体）及其类型：
1. 仅提取知识工程相关术语。
2. 术语应以名词或名词短语形式呈现，确保修饰词的完整性，避免拆分和缺失。例如，应提取"本体映射"而非单独提取"本体"或"映射"；应提取"语义网络中的节点"而非单独提取"节点"或"语义网络"。
3. 术语需符合领域标准表达。
4. 每个提取的术语必须分配一个类型，绝不允许类型字段为空。如果难以确定具体类型，则使用最接近的类型。
5. 输出格式：所有术语及其类型以JSON格式输出，格式为：[{{"entity": "术语", "type": "类型"}}, ...]
6. 若输入文本不包含有效术语，返回空列表 []，不输出无关内容。

可用的实体类型包括：{', '.join(self.entity_types)}

文本：{text}
"""
        response = self.call_llm_api(prompt)
        
        # 处理响应，将JSON格式的术语及其类型转换为列表
        try:
            # 尝试直接解析JSON
            entities = json.loads(response)
            if not isinstance(entities, list):
                entities = []
        except json.JSONDecodeError:
            # 如果不是有效的JSON，尝试提取JSON部分
            json_match = re.search(r'```json\n(.*?)```', response, re.DOTALL)
            if json_match:
                try:
                    entities_str = json_match.group(1)
                    entities = json.loads(entities_str)
                except json.JSONDecodeError:
                    logger.error(f"无法解析实体及其类型响应: {response}")
                    entities = []
            else:
                logger.error(f"无法提取实体及其类型JSON: {response}")
                entities = []
        
        return entities
    
    def step3_extract_attribute_triples(self, text: str, entities: List[Dict[str, str]], relation: str) -> List[Dict[str, str]]:
        """
        步骤3: 抽取知识点属性三元组
        
        Args:
            text: 输入文本
            entities: 已识别的实体及其类型
            relation: 属性关系类型
            
        Returns:
            属性三元组列表
        """
        if relation not in self.attribute_relations:
            logger.warning(f"'{relation}' 不是有效的属性关系")
            return []
        
        # 获取该关系的合成样本
        synthetic_samples = self.synthetic_samples.get(relation, {})
        sample_sentences = synthetic_samples.get("sentences", [])
        if not sample_sentences:
            logger.warning(f"未找到关系 '{relation}' 的合成样本")
            sample_sentences = ["该关系没有合成样本供参考"]
        
        # 构建合成样本字符串
        samples_str = "\n".join(sample_sentences[:5])  # 最多使用5个样本
        
        prompt = f"""
你是一名知识工程领域的专家，专门负责从文本中提取结构化的属性信息，并构建符合知识图谱标准的SPO（主谓宾）三元组。请遵循以下要求，从输入文本中抽取属性类型的三元组：
主语（Subject）： 必须是文本中已经识别出的知识工程相关术语。
谓语（Predicate）：判断是否存在"{relation}"的关系。
宾语（Object）： 提取主语对应的具体描述信息。

为了帮助你更好地理解该属性关系，我们提供以下合成样本作为参考：
合成样本：
{samples_str}

数据处理要求： 
1. 若无对应关系，则返回空值。确保不要强行构建文本中不存在的关系。
2. 确保所有输出符合 JSON 格式，便于自动化解析。
3. 每个实体对于相同属性关系，提取一个完整且精确的三元组。不要为同一关系生成多个相似的三元组。
4. 宾语应该是完整且精确的文本描述，不要截断或拆分为多个片段。
5. 如果文本中有多个实体，请正确区分每个实体对应的属性，不要混淆。
6. 确保提取的三元组在文本中有明确的依据，不要通过推断生成文本中未明确表达的关系。

重要提示：仅在非常确定文本中明确表达了该关系时才提取三元组。如果关系模糊或需要推断，则不提取。质量比数量更重要。

输出格式：[{{"subject": "实体1", "subject_type": "类型1", "predicate": "{relation}", "object": "描述1", "object_type": "类型2"}}, ...]

文本：{text}

已识别的知识点实体及其类型：{json.dumps(entities, ensure_ascii=False)}
"""
        response = self.call_llm_api(prompt)
        
        # 解析JSON响应
        try:
            # 尝试直接解析JSON
            triples = json.loads(response)
            if not isinstance(triples, list):
                triples = []
        except json.JSONDecodeError:
            # 如果不是有效的JSON，尝试提取JSON部分
            json_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if json_match:
                try:
                    triples_str = json_match.group(0)
                    triples = json.loads(triples_str)
                except json.JSONDecodeError:
                    logger.error(f"无法解析属性三元组响应: {response}")
                    triples = []
            else:
                logger.error(f"无法提取属性三元组JSON: {response}")
                triples = []
        
        return triples
    
    def step4_extract_relation_triples(self, text: str, entities: List[Dict[str, str]], relation: str) -> List[Dict[str, str]]:
        """
        步骤4: 抽取关系三元组
        
        Args:
            text: 输入文本
            entities: 已识别的实体及其类型
            relation: 实体间关系类型
            
        Returns:
            关系三元组列表
        """
        if relation not in self.entity_relations:
            logger.warning(f"'{relation}' 不是有效的实体间关系")
            return []
        
        # 获取该关系的合成样本
        synthetic_samples = self.synthetic_samples.get(relation, {})
        sample_sentences = synthetic_samples.get("sentences", [])
        if not sample_sentences:
            logger.warning(f"未找到关系 '{relation}' 的合成样本")
            sample_sentences = ["该关系没有合成样本供参考"]
        
        # 构建合成样本字符串
        samples_str = "\n".join(sample_sentences[:5])  # 最多使用5个样本
        
        prompt = f"""
你是一名知识工程领域的专家，专门负责从文本中抽取非属性类型的SPO三元组，以构建知识点之间的结构化关系。请遵循以下要求，从输入文本中抽取知识点关系三元组：
主语（Subject）：必须是输入文本中已识别出的知识工程相关术语。
谓语（Predicate）：判断是否存在"{relation}"的关系
宾语（Object）：必须是输入文本中已识别出的知识工程相关术语，不能是具体的文本描述。

为了帮助你更好地理解这些关系，我们提供该关系的合成样本作为参考：
合成样本：
{samples_str}

数据处理要求： 
1. 若某个知识点之间不存在该关系，则返回空值。确保不要强行构建文本中不存在的关系。
2. 确保所有输出符合JSON格式，以便于自动化解析。
3. 对于两个实体之间的关系，只提取有确切文本依据的关系，避免推测或过度解释。
4. 关系的提取必须严格忠于文本内容，不要推测文本未明确表达的关系。
5. 确保主语和宾语正确对应关系，不要混淆多个实体之间的关系。
6. 质量比数量更重要，宁可少提取，也要确保提取的关系准确无误。

重要提示：仅在文本明确表达了实体间关系时才提取三元组。如果关系模糊或需要推断，则不提取。

输出格式：[{{"subject": "实体1", "subject_type": "类型1", "predicate": "{relation}", "object": "实体2", "object_type": "类型2"}}, ...]

文本：{text}

已识别的知识点实体及其类型：{json.dumps(entities, ensure_ascii=False)}
"""
        response = self.call_llm_api(prompt)
        
        # 解析JSON响应
        try:
            # 尝试直接解析JSON
            triples = json.loads(response)
            if not isinstance(triples, list):
                triples = []
        except json.JSONDecodeError:
            # 如果不是有效的JSON，尝试提取JSON部分
            json_match = re.search(r'\[(.*?)\]', response, re.DOTALL)
            if json_match:
                try:
                    triples_str = json_match.group(0)
                    triples = json.loads(triples_str)
                except json.JSONDecodeError:
                    logger.error(f"无法解析关系三元组响应: {response}")
                    triples = []
            else:
                logger.error(f"无法提取关系三元组JSON: {response}")
                triples = []
        
        return triples
    
    def step5_validate_triples(self, text: str, triples: List[Dict[str, str]], max_iterations: int = 3) -> List[Dict[str, str]]:
        """
        步骤5: 知识三元组迭代验证
        优化逻辑:
        1. 使用合成样本增强验证提示
        2. 按关系类型验证每个三元组的正确性
        3. 对全局关系进行去重，避免不同关系类型表达相同内容
        
        Args:
            text: 原始文本
            triples: 待验证的三元组
            max_iterations: 最大迭代次数
            
        Returns:
            验证后的三元组
        """
        if not triples:
            return []
        
        # 预处理：规范三元组格式
        standardized_triples = []
        for triple in triples:
            # 确保所有字段都存在
            standardized_triple = {
                "subject": triple.get("subject", "").strip(),
                "subject_type": triple.get("subject_type", "知识图谱").strip(),
                "predicate": triple.get("predicate", "").strip(),
                "object": triple.get("object", "").strip(),
                "object_type": triple.get("object_type", "").strip()
            }
            
            # 修正谓语，确保符合schema
            if standardized_triple["predicate"] not in self.relation_schema:
                # 尝试匹配最接近的关系
                for relation in self.relation_schema:
                    if relation in standardized_triple["predicate"]:
                        standardized_triple["predicate"] = relation
                        break
                else:
                    # 如果无法匹配，使用最通用的关系
                    standardized_triple["predicate"] = "内容"  # 默认使用"内容"关系
            
            # 根据谓语确定object_type
            if standardized_triple["predicate"] in self.attribute_relations:
                if not standardized_triple["object_type"]:
                    standardized_triple["object_type"] = "文本"
            else:
                if not standardized_triple["object_type"]:
                    standardized_triple["object_type"] = "知识图谱"
            
            standardized_triples.append(standardized_triple)
        
        # 预处理：删除完全相同的三元组（精确匹配）
        unique_triples = []
        seen = set()
        for triple in standardized_triples:
            # 创建三元组的标识字符串
            triple_id = f"{triple.get('subject', '')}__{triple.get('predicate', '')}__{triple.get('object', '')}"
            if triple_id not in seen:
                seen.add(triple_id)
                unique_triples.append(triple)
        
        logger.info(f"删除完全相同的三元组后，从 {len(triples)} 个减少到 {len(unique_triples)} 个")
        
        # 第一阶段：按关系类型分组进行单个三元组验证
        validated_triples = []
        
        # 按照关系类型对三元组进行分组
        relation_triples_map = {}
        for triple in unique_triples:
            relation = triple.get("predicate", "")
            if relation not in relation_triples_map:
                relation_triples_map[relation] = []
            relation_triples_map[relation].append(triple)
        
        # 对每种关系类型的三元组单独进行验证
        for relation, relation_triples in relation_triples_map.items():
            logger.info(f"验证关系类型 '{relation}' 的 {len(relation_triples)} 个三元组")
            
            # 获取关系描述和合成样本
            relation_desc = self.relation_schema.get(relation, "未知关系")
            is_attribute = relation in self.attribute_relations
            relation_category = "属性关系" if is_attribute else "实体关系"
            
            # 获取该关系的合成样本
            synthetic_samples = self.synthetic_samples.get(relation, {})
            sample_sentences = synthetic_samples.get("sentences", [])
            if not sample_sentences:
                logger.warning(f"未找到关系 '{relation}' 的合成样本")
                sample_sentences = ["该关系没有合成样本供参考"]
            
            # 构建合成样本字符串（最多使用3个样本避免提示词过长）
            samples_str = "\n".join(sample_sentences[:3])
            
            # 迭代验证每个三元组
            for triple in relation_triples:
                # 记录该三元组是否已被验证为正确
                is_valid = False
                
                # 对单个三元组进行迭代验证
                for iteration in range(max_iterations):
                    # 将三元组转换为JSON字符串
                    triple_json = json.dumps(triple, ensure_ascii=False)
                    
                    prompt = f"""
作为知识工程专家，验证以下"{relation}"关系的三元组是否正确表达了文本中的知识。

原始文本: {text}

待验证三元组: {triple_json}

关系"{relation}"的说明: {relation_desc}
关系类别: {relation_category}

该关系的示例:
{samples_str}

请检查:
1. 三元组与原文一致性: 该三元组是否在原文中有明确依据
2. 关系使用是否恰当: "{relation}"是否是表达主语和宾语间关系的最佳选择
3. 实体提取是否准确: 主语和宾语是否正确识别文本中的概念/实体

请直接回答:
1. 这个三元组是否正确? (回答"正确"或"不正确")
2. 若不正确，请提供修正后的三元组:
{{"subject": "修正后主语", "subject_type": "主语类型", "predicate": "修正后关系", "object": "修正后宾语", "object_type": "宾语类型"}}

注意:
- 若修正关系类型，必须使用系统定义的关系类型
- 请直接回答，不要添加解释说明
"""
                    response = self.call_llm_api(prompt)
                    
                    # 检查三元组是否正确
                    if "正确" in response[:100]:
                        validated_triples.append(triple)
                        is_valid = True
                        break
                    
                    # 尝试解析修正内容
                    try:
                        # 尝试从响应中提取JSON
                        json_match = re.search(r'\{.*\}', response, re.DOTALL)
                        if json_match:
                            corrected_triple_json = json_match.group(0)
                            corrected_triple = json.loads(corrected_triple_json)
                            
                            # 检查修正的三元组是否包含必要字段
                            if all(key in corrected_triple for key in ["subject", "predicate", "object"]):
                                logger.info(f"三元组已修正: {triple.get('subject')} - {relation} - {triple.get('object')} => "
                                          f"{corrected_triple.get('subject')} - {corrected_triple.get('predicate')} - {corrected_triple.get('object')}")
                                validated_triples.append(corrected_triple)
                                is_valid = True
                                break
                            else:
                                logger.warning(f"修正的三元组缺少必要字段")
                        else:
                            # 如果未找到JSON格式，但响应表明需要修改
                            if iteration == max_iterations - 1:
                                logger.warning(f"未能修正三元组，将保留原始三元组")
                                validated_triples.append(triple)  # 在最后一次迭代，如果无法修正则保留原始三元组
                                is_valid = True
                    except Exception as e:
                        logger.error(f"解析验证响应时出错: {str(e)}")
                        if iteration == max_iterations - 1:
                            logger.warning(f"由于解析错误，将保留原始三元组")
                            validated_triples.append(triple)  # 在最后一次迭代，如果发生错误则保留原始三元组
                            is_valid = True
                
                # 如果经过所有迭代后仍然没有被验证为有效，则记录警告
                if not is_valid:
                    logger.warning(f"三元组验证失败，将被丢弃")
        
        # 第二阶段：全局去重，解决跨关系类型的内容重复问题
        if len(validated_triples) > 1:
            logger.info(f"开始全局去重检查，处理跨关系类型的内容重复问题...")
            
            # 按照主语分组，同一主语的三元组可能存在内容重复
            subject_triples_map = {}
            for triple in validated_triples:
                subject = triple.get("subject", "")
                if subject not in subject_triples_map:
                    subject_triples_map[subject] = []
                subject_triples_map[subject].append(triple)
            
            # 只检查有多个三元组的主语组
            global_validated_triples = []
            for subject, subject_triples in subject_triples_map.items():
                if len(subject_triples) <= 1:
                    global_validated_triples.extend(subject_triples)
                    continue
                
                # 获取所有涉及的关系类型，用于构建示例
                relation_examples = {}
                for triple in subject_triples:
                    relation = triple.get("predicate", "")
                    if relation not in relation_examples and relation in self.synthetic_samples:
                        # 为每种关系类型添加一个合成样本示例
                        samples = self.synthetic_samples.get(relation, {}).get("sentences", [])
                        if samples:
                            relation_examples[relation] = samples[0]
                
                # 构建合成样本示例字符串
                examples_str = ""
                for relation, example in relation_examples.items():
                    examples_str += f"关系'{relation}'示例: {example}\n"
                
                # 对每个主语组进行全局冗余检测，让大语言模型自行判断保留最准确的三元组
                prompt_global = f"""
作为知识工程专家，分析以下同一实体的多个三元组，去除冗余信息，保留最准确的表达。

实体: {subject}

三元组列表:
{json.dumps(subject_triples, ensure_ascii=False, indent=2)}

关系说明:
{", ".join([f"'{r}': {self.relation_schema.get(r, '')}" for r in set(t.get("predicate", "") for t in subject_triples)])}

合成样本:
{examples_str}

任务:
1. 分析所有三元组，识别表达相似或重复内容的三元组
2. 对于内容相似的三元组组，选择最准确的一个保留
3. 自行判断最合适的表达，不必拘泥于预设的关系优先级
4. 确保不同含义的三元组都被保留

返回格式:
[保留的三元组列表]

请直接返回JSON数组，不要添加任何解释。
"""
                response_global = self.call_llm_api(prompt_global)
                
                try:
                    # 尝试从响应中提取JSON数组
                    json_match = re.search(r'\[.*\]', response_global, re.DOTALL)
                    if json_match:
                        kept_triples_json = json_match.group(0)
                        kept_triples = json.loads(kept_triples_json)
                        
                        if len(kept_triples) < len(subject_triples):
                            logger.info(f"实体'{subject}'的三元组从 {len(subject_triples)} 个减少到 {len(kept_triples)} 个")
                            logger.info(f"保留的三元组: {json.dumps(kept_triples, ensure_ascii=False)}")
                        
                        global_validated_triples.extend(kept_triples)
                    else:
                        # 如果无法解析，保留原三元组
                        logger.warning(f"无法解析全局去重响应，保留原有三元组")
                        global_validated_triples.extend(subject_triples)
                except Exception as e:
                    logger.error(f"解析全局去重响应时出错: {str(e)}")
                    global_validated_triples.extend(subject_triples)
            
            # 最终的精确去重
            final_triples = []
            seen = set()
            
            for triple in global_validated_triples:
                triple_id = f"{triple.get('subject', '')}__{triple.get('predicate', '')}__{triple.get('object', '')}"
                if triple_id not in seen:
                    seen.add(triple_id)
                    final_triples.append(triple)
            
            logger.info(f"最终验证后共有 {len(final_triples)} 个三元组")
            return final_triples
        else:
            return validated_triples
    
    def step6_entity_alignment_and_completion(self, entity1: Dict[str, str], entity2: Dict[str, str]) -> Dict[str, Any]:
        """
        步骤6: 知识融合、实体对齐以及知识图谱补全
        
        Args:
            entity1: 第一个实体的属性
            entity2: 第二个实体的属性
            
        Returns:
            包含对齐结果和补充关系的字典
        """
        # 构建提示中的实体属性
        entity1_attrs = {key: entity1.get(key, "") for key in self.attribute_relations}
        entity2_attrs = {key: entity2.get(key, "") for key in self.attribute_relations}
        
        # 构建属性字符串
        entity1_str_parts = []
        entity2_str_parts = []
        
        for attr in self.attribute_relations:
            entity1_str_parts.append(f"{attr}：{entity1_attrs.get(attr, '')}")
            entity2_str_parts.append(f"{attr}：{entity2_attrs.get(attr, '')}")
        
        entity1_str = "\n".join(entity1_str_parts)
        entity2_str = "\n".join(entity2_str_parts)
        
        prompt = f"""
作为知识工程领域的专家，你的任务是判断以下两个实体是否表示同一概念，并在判断为同一概念时进行知识融合。具体而言，你需要判断两个实体是否表示同一概念，如果是，则以实体1作为最终名称，合并它们的属性信息，避免冗余并保留最完整和最有信息量的描述。若属性内容存在冲突，如定义、内容或目标不一致，需基于领域知识进行整合，以确保描述的准确性和清晰性。

如果实体对不表示同一概念，则需进行知识图谱补全。根据提供的已知知识点三元组信息，推理潜在的缺失关系，并严格按照指定的关系Schema进行补全，确保输出结果遵循指定的JSON格式。

输出格式：
1. 如果两个实体表示同一概念，返回:
{{"is_same": true, "merged_entity": {{"name": "实体1的名称", "attributes": {{"被定义为": "...", "内容": "...", ...}}}}}}

2. 如果两个实体不表示同一概念，但存在潜在关系，返回:
{{"is_same": false, "relations": [{{"subject": "实体1", "predicate": "关系类型", "object": "实体2"}}]}}

3. 若两个实体不对齐且没有潜在关系，则返回:
{{"is_same": false, "relations": []}}

两个实体分别为：
实体1：
{entity1_str}

实体2：
{entity2_str}

可用的关系类型包括：{", ".join(self.entity_relations)}
"""
        response = self.call_llm_api(prompt)
        
        # 解析响应
        try:
            # 尝试从响应中提取JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result_json = json_match.group(0)
                result = json.loads(result_json)
                return result
            else:
                logger.warning("未能从实体对齐响应中提取JSON结果")
                return {"is_same": False, "relations": []}
        except Exception as e:
            logger.error(f"解析实体对齐响应时出错: {str(e)}")
            return {"is_same": False, "relations": []}
    
    def process_text(self, text: str) -> Dict[str, Any]:
        """
        处理文本，执行完整的知识图谱构建流程
        
        Args:
            text: 输入文本
            
        Returns:
            包含实体和三元组的结果字典
        """
        result = {
            "entities": [],
            "attribute_triples": [],
            "relation_triples": [],
            "validated_triples": []
        }
        
        # 步骤1：如果还没有生成合成样本，先生成
        if not self.synthetic_samples:
            logger.info("生成合成样本")
            self.generate_all_synthetic_samples()
        
        # 步骤2：抽取实体及其类型
        logger.info("开始抽取实体及其类型")
        entities_with_types = self.step2_extract_entities(text)
        result["entities"] = entities_with_types
        logger.info(f"抽取了 {len(entities_with_types)} 个实体及其类型")
        
        if not entities_with_types:
            logger.warning("未抽取到实体，流程终止")
            return result
        
        # 步骤3：抽取属性三元组
        logger.info("开始抽取属性三元组")
        all_attribute_triples = []
        for relation in self.attribute_relations:
            logger.info(f"抽取 '{relation}' 属性关系")
            triples = self.step3_extract_attribute_triples(text, entities_with_types, relation)
            all_attribute_triples.extend(triples)
        
        result["attribute_triples"] = all_attribute_triples
        logger.info(f"抽取了 {len(all_attribute_triples)} 个属性三元组")
        
        # 步骤4：抽取关系三元组
        logger.info("开始抽取关系三元组")
        all_relation_triples = []
        for relation in self.entity_relations:
            logger.info(f"抽取 '{relation}' 实体关系")
            triples = self.step4_extract_relation_triples(text, entities_with_types, relation)
            all_relation_triples.extend(triples)
        
        result["relation_triples"] = all_relation_triples
        logger.info(f"抽取了 {len(all_relation_triples)} 个关系三元组")
        
        # 步骤5：验证三元组
        logger.info("开始验证三元组")
        all_triples = all_attribute_triples + all_relation_triples
        validated_triples = self.step5_validate_triples(text, all_triples)
        result["validated_triples"] = validated_triples
        logger.info(f"验证后有 {len(validated_triples)} 个三元组")
        
        return result
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """
        保存结果到文件
        
        Args:
            results: 处理结果
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"结果已保存到 {output_file}")


def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="知识图谱构建工具")
    parser.add_argument('--input', type=str, required=True, help="输入文本文件路径")
    parser.add_argument('--output', type=str, default="kg_output.json", help="输出结果文件路径")
    parser.add_argument('--api_key', type=str, help="DeepSeek API密钥")
    parser.add_argument('--api_url', type=str, help="DeepSeek API URL")
    parser.add_argument('--api_version', type=str, default="v1", help="DeepSeek API版本")
    
    args = parser.parse_args()
    
    # 读取输入文本
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        logger.error(f"读取输入文件时出错: {str(e)}")
        return
    
    # 创建知识图谱构建工具
    builder = KnowledgeGraphBuilder(
        llm_api_key=args.api_key,
        llm_api_url=args.api_url,
        api_version=args.api_version
    )
    
    # 处理文本
    results = builder.process_text(text)
    
    # 保存结果
    builder.save_results(results, args.output)
    
    logger.info("知识图谱构建完成")


if __name__ == "__main__":
    main() 