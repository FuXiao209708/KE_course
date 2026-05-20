#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量处理知识图谱构建工具
"""

import os
import json
import csv
import logging
import time
from tqdm import tqdm
from prompt_builder.kg_builder import KnowledgeGraphBuilder

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchProcessor:
    """批量处理知识图谱构建工具"""
    
    def __init__(self, llm_api_key=None, llm_api_url=None, synthetic_samples_path=None):
        """
        初始化批处理器
        
        Args:
            llm_api_key: DeepSeek API密钥
            llm_api_url: DeepSeek API URL
            synthetic_samples_path: 合成样本保存路径
        """
        self.builder = KnowledgeGraphBuilder(llm_api_key=llm_api_key or os.getenv("DEESEEK_API_KEY"), llm_api_url=llm_api_url or os.getenv("DEESEEK_API_URL"))
        self.synthetic_samples_path = synthetic_samples_path or os.path.join(os.getcwd(), "output", "synthetic_samples.json")
        
        # 创建输出目录
        os.makedirs(os.path.dirname(self.synthetic_samples_path), exist_ok=True)
        os.makedirs("output/csv", exist_ok=True)
        os.makedirs("output/validated", exist_ok=True)
        os.makedirs("output/test", exist_ok=True)
    
    def generate_synthetic_samples(self, k=5, force_regenerate=False):
        """
        为所有关系生成合成样本
        
        Args:
            k: 每种关系生成的样本数量
            force_regenerate: 是否强制重新生成
        """
        # 检查是否已存在合成样本
        if os.path.exists(self.synthetic_samples_path) and not force_regenerate:
            logger.info(f"加载现有的合成样本: {self.synthetic_samples_path}")
            try:
                with open(self.synthetic_samples_path, 'r', encoding='utf-8') as f:
                    self.builder.synthetic_samples = json.load(f)
                
                # 检查合成样本是否包含所有关系
                missing_relations = []
                for relation in self.builder.attribute_relations + self.builder.entity_relations:
                    if relation not in self.builder.synthetic_samples:
                        missing_relations.append(relation)
                
                if missing_relations:
                    logger.warning(f"发现缺失的合成样本关系: {missing_relations}")
                    logger.info("生成缺失的合成样本...")
                    for relation in tqdm(missing_relations, desc="生成缺失的合成样本"):
                        self.generate_relation_sample(relation, k)
                        # 每次生成后保存，避免中断导致重复生成
                        with open(self.synthetic_samples_path, 'w', encoding='utf-8') as f:
                            json.dump(self.builder.synthetic_samples, f, ensure_ascii=False, indent=2)
                        # 添加延迟，避免API调用过于频繁
                        time.sleep(1)
                
                return
            except Exception as e:
                logger.error(f"加载合成样本时出错: {str(e)}")
                logger.info("将重新生成合成样本")
        
        logger.info("开始生成合成样本...")
        
        # 为所有属性关系生成合成样本
        for relation in tqdm(self.builder.attribute_relations, desc="生成属性关系样本"):
            self.generate_relation_sample(relation, k)
            # 每次生成后保存，避免中断导致重复生成
            with open(self.synthetic_samples_path, 'w', encoding='utf-8') as f:
                json.dump(self.builder.synthetic_samples, f, ensure_ascii=False, indent=2)
            # 添加延迟，避免API调用过于频繁
            time.sleep(1)
        
        # 为所有实体关系生成合成样本
        for relation in tqdm(self.builder.entity_relations, desc="生成实体关系样本"):
            self.generate_relation_sample(relation, k)
            # 每次生成后保存，避免中断导致重复生成
            with open(self.synthetic_samples_path, 'w', encoding='utf-8') as f:
                json.dump(self.builder.synthetic_samples, f, ensure_ascii=False, indent=2)
            # 添加延迟，避免API调用过于频繁
            time.sleep(1)
        
        logger.info(f"合成样本已保存至: {self.synthetic_samples_path}")
    
    def generate_relation_sample(self, relation, k=5):
        """
        为单个关系生成合成样本
        
        Args:
            relation: 关系类型
            k: 生成样本数量
        """
        try:
            logger.info(f"为关系 '{relation}' 生成合成样本")
            samples = self.builder.step1_generate_synthetic_samples(relation, k=k)
            if not samples.get("sentences"):
                logger.warning(f"关系 '{relation}' 生成的样本句子为空，重试...")
                # 重试一次
                samples = self.builder.step1_generate_synthetic_samples(relation, k=k)
        except Exception as e:
            logger.error(f"为关系 '{relation}' 生成样本时出错: {str(e)}")
    
    def process_json_file(self, file_path):
        """
        处理单个JSON文件
        
        Args:
            file_path: JSON文件路径
        """
        try:
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 将整个内容解析为JSON数组
                try:
                    data = json.loads(content)
                    lines = [json.dumps(item, ensure_ascii=False) for item in data]
                except json.JSONDecodeError:
                    # 如果不是JSON数组，则尝试按行解析
                    lines = content.strip().split('\n')
            
            # 准备CSV输出文件
            basename = os.path.basename(file_path).split('.')[0]
            csv_output = os.path.join("output", "test", f"{basename}_output.csv")
            
            # 创建CSV文件并写入标题行
            with open(csv_output, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter='\t')
                writer.writerow(['input', 'subject', 'subject_type', 'data/object', 'relation', 'object', 'object_type'])
            
            # 处理每一行JSON
            for line_idx, line in enumerate(tqdm(lines, desc=f"处理文件 {basename}")):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 解析JSON
                    record = json.loads(line)
                    text = record.get('text', '')
                    
                    if not text:
                        logger.warning(f"文本为空，跳过: {line[:100]}...")
                        continue
                    
                    # 第二步：提取实体及其类型
                    entities = self.builder.step2_extract_entities(text)
                    
                    if not entities:
                        logger.warning(f"未提取到实体，跳过: {text[:100]}...")
                        continue
                    
                    # 存储所有三元组
                    all_triples = []
                    
                    # 第三步：提取属性三元组
                    for relation in self.builder.attribute_relations:
                        # 检查该关系是否有合成样本
                        if relation not in self.builder.synthetic_samples:
                            logger.warning(f"关系 '{relation}' 没有合成样本，将尝试生成")
                            self.generate_relation_sample(relation)
                            # 保存更新后的合成样本
                            with open(self.synthetic_samples_path, 'w', encoding='utf-8') as f:
                                json.dump(self.builder.synthetic_samples, f, ensure_ascii=False, indent=2)
                        
                        triples = self.builder.step3_extract_attribute_triples(text, entities, relation)
                        all_triples.extend(triples)
                    
                    # 第四步：提取关系三元组
                    for relation in self.builder.entity_relations:
                        # 检查该关系是否有合成样本
                        if relation not in self.builder.synthetic_samples:
                            logger.warning(f"关系 '{relation}' 没有合成样本，将尝试生成")
                            self.generate_relation_sample(relation)
                            # 保存更新后的合成样本
                            with open(self.synthetic_samples_path, 'w', encoding='utf-8') as f:
                                json.dump(self.builder.synthetic_samples, f, ensure_ascii=False, indent=2)
                        
                        triples = self.builder.step4_extract_relation_triples(text, entities, relation)
                        all_triples.extend(triples)
                    
                    # 第五步：验证三元组
                    validated_triples = self.builder.step5_validate_triples(text, all_triples)
                    
                    # 打开CSV文件并以追加模式写入，每处理一条记录就保存一次
                    if validated_triples:
                        with open(csv_output, 'a', encoding='utf-8', newline='') as csvfile:
                            writer = csv.writer(csvfile, delimiter='\t')
                            
                            # 写入三元组，格式为：input subject subject_type data/object relation object object_type
                            for triple in validated_triples:
                                subject = triple.get('subject', '')
                                subject_type = triple.get('subject_type', '知识图谱')  # 确保有默认类型
                                predicate = triple.get('predicate', '')
                                obj = triple.get('object', '')
                                object_type = triple.get('object_type', '文本')  # 确保有默认类型
                                
                                # 确保subject和object不为空
                                if not subject or not obj:
                                    continue
                                
                                # 确定是属性还是关系
                                if predicate in self.builder.attribute_relations:
                                    data_object = 'data'
                                else:
                                    data_object = 'object'
                                
                                # 写入一行
                                writer.writerow([
                                    text,
                                    subject,
                                    subject_type,
                                    data_object,
                                    predicate,
                                    obj,
                                    object_type
                                ])
                        
                        logger.info(f"文件 {basename} 的第 {line_idx+1} 条记录处理完成，从 {len(all_triples)} 个三元组验证后保留 {len(validated_triples)} 个")
                    else:
                        logger.warning(f"文件 {basename} 的第 {line_idx+1} 条记录未提取到有效三元组")
                
                except json.JSONDecodeError:
                    logger.error(f"JSON解析错误: {line[:100]}...")
                except Exception as e:
                    logger.error(f"处理记录时出错: {str(e)}")
                    logger.exception(e)  # 打印完整的异常堆栈跟踪
            
            logger.info(f"文件 {file_path} 处理完成，结果保存至 {csv_output}")
            return csv_output
        
        except Exception as e:
            logger.error(f"处理文件 {file_path} 出错: {str(e)}")
            logger.exception(e)  # 打印完整的异常堆栈跟踪
            return None
    
    def process_directory(self, dir_path):
        """
        处理目录中的所有JSON文件
        
        Args:
            dir_path: 目录路径
        """
        # 确保合成样本已生成
        self.generate_synthetic_samples()
        
        # 检查目录路径是否是具体文件
        if os.path.isfile(dir_path):
            logger.info(f"{dir_path} 是文件而非目录，将处理单个文件")
            csv_output = self.process_json_file(dir_path)
            return [csv_output] if csv_output else []
        
        # 确保目录存在
        if not os.path.exists(dir_path):
            logger.error(f"目录不存在: {dir_path}")
            return []
        
        # 获取所有JSON文件
        json_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.json')]
        logger.info(f"找到 {len(json_files)} 个JSON文件")
        
        # 处理所有文件
        csv_outputs = []
        for json_file in json_files:
            csv_output = self.process_json_file(json_file)
            if csv_output:
                csv_outputs.append(csv_output)
        
        return csv_outputs
    
    def validate_csv(self, csv_path):
        """
        验证CSV文件中的三元组
        
        Args:
            csv_path: CSV文件路径
        """
        try:
            # 准备输出文件
            basename = os.path.basename(csv_path).split('_')[0]
            validated_output = os.path.join("output", "validated", f"{basename}_validated.csv")
            
            # 读取CSV文件
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f, delimiter='\t')
                # 读取标题行
                header = next(reader)
                rows = list(reader)
            
            # 按输入文本分组处理
            text_triples_map = {}
            for row in rows:
                if len(row) < 7:
                    continue
                
                text = row[0]
                if text not in text_triples_map:
                    text_triples_map[text] = []
                
                # 解析三元组
                subject = row[1]
                subject_type = row[2]
                data_object = row[3]
                relation = row[4]
                obj = row[5]
                object_type = row[6]
                
                triple = {
                    "subject": subject,
                    "subject_type": subject_type,
                    "predicate": relation,
                    "object": obj,
                    "object_type": object_type
                }
                
                text_triples_map[text].append(triple)
            
            # 写入验证后的CSV
            with open(validated_output, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(header)
                
                # 跟踪总的验证后三元组数量
                total_validated_count = 0
                
                # 处理每个文本的三元组
                for text, triples in tqdm(text_triples_map.items(), desc=f"验证 {basename}"):
                    if not triples:
                        continue
                    
                    # 验证三元组前，记录原始数量
                    original_count = len(triples)
                    
                    # 验证三元组
                    validated_triples = self.builder.step5_validate_triples(text, triples)
                    
                    # 如果验证后三元组数量显著减少，输出警告
                    if len(validated_triples) < original_count * 0.5 and original_count > 2:
                        logger.warning(f"警告：文本 '{text[:30]}...' 的三元组数量从 {original_count} 减少到 {len(validated_triples)}，可能删除了正确的三元组")
                    
                    total_validated_count += len(validated_triples)
                    
                    # 写入CSV
                    for triple in validated_triples:
                        subject = triple.get('subject', '')
                        subject_type = triple.get('subject_type', '知识图谱')  # 确保有默认类型
                        predicate = triple.get('predicate', '')
                        obj = triple.get('object', '')
                        object_type = triple.get('object_type', '文本')  # 确保有默认类型
                        
                        # 确保subject和object不为空
                        if not subject or not obj:
                            continue
                        
                        # 确定是属性还是关系
                        if predicate in self.builder.attribute_relations:
                            data_object = 'data'
                        else:
                            data_object = 'object'
                        
                        # 写入一行
                        writer.writerow([
                            text,
                            subject,
                            subject_type,
                            data_object,
                            predicate,
                            obj,
                            object_type
                        ])
            
            logger.info(f"CSV验证完成，从原始的 {len(rows)} 个三元组验证和去重后保留 {total_validated_count} 个，结果保存至 {validated_output}")
            return validated_output
        
        except Exception as e:
            logger.error(f"验证CSV {csv_path} 出错: {str(e)}")
            return None
    
    def run(self, json_dir=None):
        """
        运行完整的批处理流程
        
        Args:
            json_dir: JSON文件目录
        """
        json_dir = json_dir or os.path.join("dataset", "json")
        
        # 第一步：生成合成样本
        logger.info("步骤1: 生成合成样本")
        self.generate_synthetic_samples()
        
        # 第二到第五步：处理JSON文件
        logger.info("步骤2-5: 处理JSON文件目录")
        csv_outputs = self.process_directory(json_dir)
        
        # 额外的验证步骤
        logger.info("额外步骤: 验证CSV文件")
        for csv_output in csv_outputs:
            self.validate_csv(csv_output)
        
        logger.info("批处理完成！")

def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="知识图谱批量处理工具")
    parser.add_argument("--api_key", type=str, help="DeepSeek API密钥")
    parser.add_argument("--api_url", type=str, help="DeepSeek API URL")
    parser.add_argument("--json_dir", type=str, default="dataset/json", help="JSON文件目录")
    parser.add_argument("--samples", type=str, default="output/synthetic_samples.json", help="合成样本保存路径")
    parser.add_argument("--regenerate", action="store_true", help="强制重新生成合成样本")
    
    args = parser.parse_args()
    
    # 创建批处理器
    processor = BatchProcessor(
        llm_api_key=args.api_key, 
        llm_api_url=args.api_url,
        synthetic_samples_path=args.samples
    )
    
    # 生成合成样本
    if args.regenerate:
        processor.generate_synthetic_samples(force_regenerate=True)
    
    # 运行批处理
    processor.run(json_dir=args.json_dir)

if __name__ == "__main__":
    main() 