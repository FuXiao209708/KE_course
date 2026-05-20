#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
独立的合成样本生成脚本

用于为知识图谱构建预先生成所有关系的合成样本
"""

import os
import json
import logging
import argparse
import time
from tqdm import tqdm
from prompt_builder.kg_builder import KnowledgeGraphBuilder

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sample_generation.log')
    ]
)
logger = logging.getLogger(__name__)

class SampleGenerator:
    """合成样本生成器"""
    
    def __init__(self, llm_api_key=None, llm_api_url=None, output_path="output/synthetic_samples.json"):
        """
        初始化合成样本生成器
        
        Args:
            llm_api_key: LLM API密钥
            llm_api_url: LLM API URL
            output_path: 合成样本输出路径
        """
        self.builder = KnowledgeGraphBuilder(
            llm_api_key=llm_api_key or os.getenv("DEESEEK_API_KEY"),
            llm_api_url=llm_api_url or os.getenv("DEESEEK_API_URL")
        )
        self.output_path = output_path
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # 初始化合成样本字典
        self.synthetic_samples = {}
        if os.path.exists(self.output_path):
            try:
                with open(self.output_path, 'r', encoding='utf-8') as f:
                    self.synthetic_samples = json.load(f)
                logger.info(f"已加载现有合成样本，包含 {len(self.synthetic_samples)} 种关系")
            except Exception as e:
                logger.error(f"加载现有合成样本出错: {e}")
    
    def generate_all_samples(self, k=5, force_regenerate=False, delay=1):
        """
        生成所有关系的合成样本
        
        Args:
            k: 每种关系生成的样本数量
            force_regenerate: 是否强制重新生成
            delay: 每次API调用之间的延迟(秒)
        """
        # 获取所有需要处理的关系
        all_relations = self.builder.attribute_relations + self.builder.entity_relations
        logger.info(f"将生成 {len(all_relations)} 种关系的合成样本")
        
        if not force_regenerate:
            # 过滤掉已经生成的关系
            relations_to_generate = [r for r in all_relations if r not in self.synthetic_samples]
            if relations_to_generate:
                logger.info(f"发现 {len(relations_to_generate)} 种关系尚未生成合成样本")
            else:
                logger.info("所有关系的合成样本已经生成，无需重新生成")
                return
        else:
            relations_to_generate = all_relations
            logger.info("将强制重新生成所有关系的合成样本")
        
        # 生成属性关系合成样本
        attribute_relations = [r for r in relations_to_generate if r in self.builder.attribute_relations]
        if attribute_relations:
            logger.info(f"开始生成 {len(attribute_relations)} 种属性关系的合成样本")
            for relation in tqdm(attribute_relations, desc="生成属性关系样本"):
                self._generate_relation_sample(relation, k)
                # 保存当前进度
                self._save_samples()
                # 延迟，避免API调用过于频繁
                time.sleep(delay)
        
        # 生成实体关系合成样本
        entity_relations = [r for r in relations_to_generate if r in self.builder.entity_relations]
        if entity_relations:
            logger.info(f"开始生成 {len(entity_relations)} 种实体关系的合成样本")
            for relation in tqdm(entity_relations, desc="生成实体关系样本"):
                self._generate_relation_sample(relation, k)
                # 保存当前进度
                self._save_samples()
                # 延迟，避免API调用过于频繁
                time.sleep(delay)
        
        logger.info(f"合成样本生成完成，共 {len(self.synthetic_samples)} 种关系")
    
    def _generate_relation_sample(self, relation, k=5, max_retries=3):
        """
        生成单个关系的合成样本
        
        Args:
            relation: 关系类型
            k: 生成样本数量
            max_retries: 最大重试次数
        """
        logger.info(f"生成关系 '{relation}' 的合成样本")
        
        for retry in range(max_retries):
            try:
                # 生成合成样本
                samples = self.builder.step1_generate_synthetic_samples(relation, k=k)
                
                # 检查生成的样本是否有效
                if not samples.get("sentences"):
                    logger.warning(f"关系 '{relation}' 的合成样本句子为空 (尝试 {retry+1}/{max_retries})")
                    time.sleep(1)  # 短暂延迟后重试
                    continue
                
                # 更新合成样本字典
                self.synthetic_samples[relation] = samples
                logger.info(f"关系 '{relation}' 的合成样本生成成功: {len(samples.get('sentences', []))} 个句子")
                return
            
            except Exception as e:
                logger.error(f"生成关系 '{relation}' 的合成样本出错 (尝试 {retry+1}/{max_retries}): {e}")
                time.sleep(2)  # 出错后延迟更长时间
        
        # 所有重试都失败
        logger.error(f"生成关系 '{relation}' 的合成样本失败，已达到最大重试次数")
        # 创建一个空样本避免后续处理出错
        self.synthetic_samples[relation] = {"synonyms": [], "sentences": [], "rewritten": []}
    
    def _save_samples(self):
        """保存当前的合成样本到文件"""
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(self.synthetic_samples, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存合成样本出错: {e}")
    
    def verify_samples(self):
        """验证所有关系的合成样本是否有效"""
        all_relations = self.builder.attribute_relations + self.builder.entity_relations
        missing_relations = []
        invalid_relations = []
        
        # 检查缺失的关系
        for relation in all_relations:
            if relation not in self.synthetic_samples:
                missing_relations.append(relation)
                continue
            
            # 检查样本是否有效
            samples = self.synthetic_samples[relation]
            if not samples.get("sentences"):
                invalid_relations.append(relation)
        
        # 输出验证结果
        if missing_relations:
            logger.warning(f"发现 {len(missing_relations)} 种关系缺失合成样本: {missing_relations}")
        
        if invalid_relations:
            logger.warning(f"发现 {len(invalid_relations)} 种关系的合成样本无效: {invalid_relations}")
        
        if not missing_relations and not invalid_relations:
            logger.info("所有关系的合成样本均有效")
            return True
        return False
    
    def generate_missing_samples(self, k=5, delay=1):
        """生成缺失的合成样本"""
        all_relations = self.builder.attribute_relations + self.builder.entity_relations
        missing_relations = [r for r in all_relations if r not in self.synthetic_samples]
        invalid_relations = [r for r in all_relations 
                             if r in self.synthetic_samples and not self.synthetic_samples[r].get("sentences")]
        
        relations_to_generate = missing_relations + invalid_relations
        
        if not relations_to_generate:
            logger.info("没有缺失的合成样本需要生成")
            return
        
        logger.info(f"将为 {len(relations_to_generate)} 种关系生成合成样本")
        for relation in tqdm(relations_to_generate, desc="生成缺失的合成样本"):
            self._generate_relation_sample(relation, k)
            # 保存当前进度
            self._save_samples()
            # 延迟，避免API调用过于频繁
            time.sleep(delay)
        
        logger.info("缺失的合成样本已生成完成")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="独立的合成样本生成脚本")
    parser.add_argument("--api_key", type=str, help="LLM API密钥")
    parser.add_argument("--api_url", type=str, help="LLM API URL")
    parser.add_argument("--output", type=str, default="output/synthetic_samples.json", help="合成样本输出路径")
    parser.add_argument("--samples", type=int, default=5, help="每种关系生成的样本数量")
    parser.add_argument("--force", action="store_true", help="强制重新生成所有关系的合成样本")
    parser.add_argument("--verify", action="store_true", help="验证现有的合成样本")
    parser.add_argument("--fix", action="store_true", help="修复缺失的合成样本")
    parser.add_argument("--delay", type=float, default=1.0, help="API调用之间的延迟(秒)")
    
    args = parser.parse_args()
    
    # 创建合成样本生成器
    generator = SampleGenerator(
        llm_api_key=args.api_key,
        llm_api_url=args.api_url,
        output_path=args.output
    )
    
    if args.verify:
        # 验证现有的合成样本
        logger.info("验证现有的合成样本...")
        generator.verify_samples()
    elif args.fix:
        # 修复缺失的合成样本
        logger.info("修复缺失的合成样本...")
        generator.generate_missing_samples(k=args.samples, delay=args.delay)
    else:
        # 生成所有关系的合成样本
        logger.info("生成所有关系的合成样本...")
        generator.generate_all_samples(k=args.samples, force_regenerate=args.force, delay=args.delay)
    
    # 最后验证一下
    generator.verify_samples()

if __name__ == "__main__":
    main() 