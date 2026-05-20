#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
单个JSON文件处理工具
"""

import os
import logging
import argparse
from batch_processor import BatchProcessor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description="单个JSON文件处理工具")
    parser.add_argument("--file", type=str, required=True, help="JSON文件路径")
    parser.add_argument("--api_key", type=str, help="DeepSeek API密钥")
    parser.add_argument("--api_url", type=str, help="DeepSeek API URL")
    parser.add_argument("--samples", type=str, default="output/synthetic_samples.json", help="合成样本保存路径")
    parser.add_argument("--regenerate", action="store_true", help="强制重新生成合成样本")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.file):
        logger.error(f"文件不存在: {args.file}")
        return
    
    # 创建批处理器
    processor = BatchProcessor(
        llm_api_key=args.api_key,
        llm_api_url=args.api_url,
        synthetic_samples_path=args.samples
    )
    
    # 生成合成样本
    if args.regenerate:
        processor.generate_synthetic_samples(force_regenerate=True)
    else:
        processor.generate_synthetic_samples()
    
    # 处理单个文件
    logger.info(f"开始处理文件: {args.file}")
    csv_output = processor.process_json_file(args.file)
    
    if csv_output:
        # 验证三元组
        logger.info(f"开始验证三元组")
        validated_output = processor.validate_csv(csv_output)
        
        if validated_output:
            logger.info(f"处理完成，结果保存至: {validated_output}")
        else:
            logger.error("验证三元组失败")
    else:
        logger.error("处理文件失败")

if __name__ == "__main__":
    main() 