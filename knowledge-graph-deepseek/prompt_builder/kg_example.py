#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱构建工具使用示例
"""

from kg_builder import KnowledgeGraphBuilder
import json

def main():
    # 示例文本（这里用一个简短的知识工程相关文本）
    sample_text = """
    知识图谱是一种用于表示知识的语义网络，由节点和边组成，节点代表实体，边代表实体间的关系。
    知识图谱的构建过程包括知识抽取、知识表示、知识融合和知识推理等步骤。
    知识抽取的目标是从非结构化文本中提取实体和关系，形成结构化的知识三元组。
    知识表示研究如何将抽取的知识以计算机可处理的形式保存，常见的方法包括基于符号的表示和基于向量的表示。
    知识融合解决来自不同数据源的知识整合问题，包括实体对齐、关系对齐和模式对齐等任务。
    知识推理是在已有知识的基础上推导出新的知识，增强知识图谱的完备性。
    语义搜索是知识图谱的一个重要应用，它利用知识图谱提供的语义信息改进传统关键词搜索。
    """

    # 创建知识图谱构建工具实例
    # 注意：实际使用时需要提供有效的LLM API密钥和URL
    builder = KnowledgeGraphBuilder()
    
    # 为演示目的，我们只生成少量合成样本
    print("1. 生成合成样本示例...")
    samples = builder.step1_generate_synthetic_samples("被定义为", k=2)
    print(f"为'被定义为'关系生成的合成样本:")
    print(json.dumps(samples, ensure_ascii=False, indent=2))
    print()
    
    # 抽取实体
    print("2. 实体抽取示例...")
    entities = builder.step2_extract_entities(sample_text)
    print(f"从文本中抽取的实体: {entities}")
    print()
    
    # 抽取属性三元组
    print("3. 属性三元组抽取示例...")
    attribute_triples = builder.step3_extract_attribute_triples(
        sample_text, entities, "被定义为"
    )
    print(f"抽取的'被定义为'属性三元组:")
    print(json.dumps(attribute_triples, ensure_ascii=False, indent=2))
    print()
    
    # 抽取关系三元组
    print("4. 关系三元组抽取示例...")
    relation_triples = builder.step4_extract_relation_triples(
        sample_text, entities, "包含"
    )
    print(f"抽取的'包含'关系三元组:")
    print(json.dumps(relation_triples, ensure_ascii=False, indent=2))
    print()
    
    # 完整处理
    print("5. 完整文本处理示例...")
    # 注意：这会生成所有关系的合成样本，时间可能较长
    # 为了演示，我们在这里只处理几个关系
    builder.attribute_relations = ["被定义为", "目标"]
    builder.entity_relations = ["包含"]
    results = builder.process_text(sample_text)
    print(f"完整处理结果:")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 