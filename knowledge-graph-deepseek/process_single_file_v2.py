#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
处理单个文本文件提取知识图谱
"""

import os
import json
import argparse
import logging
from prompt_builder2.kg_builder import KnowledgeGraphBuilder

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description="单文件知识图谱构建工具")
    parser.add_argument("--api_key", type=str, default=os.getenv("DEESEEK_API_KEY"), help="DeepSeek API密钥")
    parser.add_argument("--api_url", type=str, default=os.getenv("DEESEEK_API_URL"), help="DeepSeek API URL")
    parser.add_argument("--input", type=str, required=True, help="输入文本文件路径或JSON文件")
    parser.add_argument("--output", type=str, default="output/single_output_v2.json", help="输出结果文件路径")
    parser.add_argument("--samples", type=str, default="output/synthetic_samples_v2.json", help="合成样本保存/加载路径")
    
    args = parser.parse_args()
    
    # 创建知识图谱构建工具
    builder = KnowledgeGraphBuilder(
        llm_api_key=args.api_key,
        llm_api_url=args.api_url
    )
    
    # 检查是否有现成的合成样本可以加载
    if os.path.exists(args.samples):
        logger.info(f"加载现有的合成样本: {args.samples}")
        try:
            with open(args.samples, 'r', encoding='utf-8') as f:
                builder.synthetic_samples = json.load(f)
        except Exception as e:
            logger.error(f"加载合成样本时出错: {str(e)}")
            logger.info("将生成新的合成样本")
            builder.generate_all_synthetic_samples()
            # 保存合成样本以供后续使用
            os.makedirs(os.path.dirname(args.samples), exist_ok=True)
            with open(args.samples, 'w', encoding='utf-8') as f:
                json.dump(builder.synthetic_samples, f, ensure_ascii=False, indent=2)
    else:
        logger.info("生成新的合成样本...")
        builder.generate_all_synthetic_samples()
        # 保存合成样本以供后续使用
        os.makedirs(os.path.dirname(args.samples), exist_ok=True)
        with open(args.samples, 'w', encoding='utf-8') as f:
            json.dump(builder.synthetic_samples, f, ensure_ascii=False, indent=2)
    
    # 读取输入文件
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否为JSON格式
        if args.input.endswith('.json'):
            try:
                # 尝试解析为JSON
                data = json.loads(content)
                # 如果是列表，取第一个元素
                if isinstance(data, list) and len(data) > 0:
                    if isinstance(data[0], dict) and 'text' in data[0]:
                        text = data[0]['text']
                    else:
                        text = json.dumps(data[0], ensure_ascii=False)
                # 如果是字典，检查是否有text字段
                elif isinstance(data, dict) and 'text' in data:
                    text = data['text']
                else:
                    # 按行读取
                    lines = content.strip().split('\n')
                    for line in lines:
                        try:
                            record = json.loads(line)
                            if 'text' in record:
                                text = record['text']
                                break
                        except:
                            continue
                    else:
                        text = content  # 如果没有找到有效的text字段，使用原始内容
            except json.JSONDecodeError:
                # 不是有效的JSON，使用原始内容
                text = content
        else:
            # 不是JSON文件，直接使用内容
            text = content
        
        logger.info(f"处理文本: {text[:100]}...")
        
        # 处理文本
        results = builder.process_text(text)
        
        # 保存结果
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        builder.save_results(results, args.output)
        
        logger.info(f"结果已保存到: {args.output}")
        
        # 打印摘要
        logger.info(f"共抽取了 {len(results['entities'])} 个实体")
        logger.info(f"共抽取了 {len(results['attribute_triples'])} 个属性三元组")
        logger.info(f"共抽取了 {len(results['relation_triples'])} 个关系三元组")
        logger.info(f"验证后保留了 {len(results['validated_triples'])} 个三元组")
        
    except Exception as e:
        logger.error(f"处理文件时出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 