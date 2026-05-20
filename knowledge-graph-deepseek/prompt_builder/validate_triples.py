#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱三元组验证和修复工具
"""

import os
import csv
import logging
import json
from prompt_builder.kg_builder import KnowledgeGraphBuilder
from tqdm import tqdm

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_csv_file(file_path, builder, output_dir):
    """
    验证和修复CSV文件中的三元组
    
    Args:
        file_path: CSV文件路径
        builder: KnowledgeGraphBuilder实例
        output_dir: 输出目录
    """
    try:
        # 准备输出文件
        basename = os.path.basename(file_path).split('_')[0]
        output_file = os.path.join(output_dir, f"{basename}_validated.csv")
        
        # 读取CSV文件
        with open(file_path, 'r', encoding='utf-8', newline='') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            # 读取标题行
            header = next(csv_reader)
            
            # 读取所有行
            rows = list(csv_reader)
            
            # 分组处理同一个输入文本的三元组
            text_triples = {}
            for row in rows:
                if len(row) < 7:
                    logger.warning(f"行格式错误: {row}")
                    continue
                    
                input_text = row[0]
                
                if input_text not in text_triples:
                    text_triples[input_text] = []
                
                # 解析三元组
                subject = row[1]
                subject_type = row[2]
                data_object = row[3]  # "data" 或 "object"
                relation = row[4]
                obj = row[5]
                object_type = row[6]
                
                # 添加到对应文本的三元组列表
                text_triples[input_text].append({
                    "subject": subject,
                    "subject_type": subject_type,
                    "predicate": relation,
                    "object": obj,
                    "object_type": object_type,
                    "data_object": data_object
                })
        
        # 创建输出CSV文件
        with open(output_file, 'w', encoding='utf-8', newline='') as output_csv:
            csv_writer = csv.writer(output_csv)
            
            # 写入标题行
            csv_writer.writerow(header)
            
            # 处理每个文本的三元组
            for text, triples in tqdm(text_triples.items(), desc=f"验证 {basename}"):
                try:
                    # 验证三元组
                    validated_triples = builder.step5_validate_triples(text, triples, max_iterations=3)
                    
                    # 写入验证后的三元组
                    for triple in validated_triples:
                        subject = triple.get("subject", "")
                        subject_type = triple.get("subject_type", "")
                        predicate = triple.get("predicate", "")
                        obj = triple.get("object", "")
                        object_type = triple.get("object_type", "")
                        data_object = triple.get("data_object", "data" if predicate in builder.attribute_relations else "object")
                        
                        # 写入CSV行
                        csv_writer.writerow([text, subject, subject_type, data_object, predicate, obj, object_type])
                
                except Exception as e:
                    logger.error(f"验证三元组时出错: {str(e)}")
        
        logger.info(f"文件 {file_path} 验证完成，结果保存至 {output_file}")
        
    except Exception as e:
        logger.error(f"处理文件 {file_path} 时出错: {str(e)}")

def main():
    # 创建知识图谱构建工具实例
    builder = KnowledgeGraphBuilder()
    
    # 设置输入和输出目录
    input_dir = os.path.join("output", "csv")
    output_dir = os.path.join("output", "validated")
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 获取所有CSV文件
    csv_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('_output.csv')]
    
    # 处理每个CSV文件
    for csv_file in csv_files:
        logger.info(f"开始验证文件: {csv_file}")
        validate_csv_file(csv_file, builder, output_dir)
    
    logger.info("所有文件验证完成！")

if __name__ == "__main__":
    main() 