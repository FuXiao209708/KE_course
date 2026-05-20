#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱构建与实体对齐完整流程
调用三个模块完成完整的流程：构建知识图谱、筛选候选对齐实体、执行实体对齐
"""

import os
import argparse
import logging
import time
from datetime import datetime
import subprocess
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("kg_alignment_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="知识图谱构建与实体对齐完整流程")
    
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
        "--llm_api_url", 
        type=str, 
        default=None,
        help="大语言模型API URL（可选）"
    )
    
    parser.add_argument(
        "--llm_api_key", 
        type=str, 
        default=None,
        help="大语言模型API密钥（可选）"
    )
    
    parser.add_argument(
        "--visualize", 
        action="store_true",
        help="是否可视化知识图谱"
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
        "--confidence_threshold", 
        type=float, 
        default=0.7,
        help="实体对齐置信度阈值"
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
    
    parser.add_argument(
        "--skip_build", 
        action="store_true",
        help="跳过知识图谱构建阶段"
    )
    
    parser.add_argument(
        "--skip_candidates", 
        action="store_true",
        help="跳过候选实体筛选阶段"
    )
    
    parser.add_argument(
        "--skip_alignment", 
        action="store_true",
        help="跳过实体对齐阶段"
    )
    
    return parser.parse_args()

def create_timestamped_dir(base_dir):
    """创建带时间戳的目录"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, f"run_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def run_step(script_path, args_dict, step_name):
    """运行单个步骤"""
    logger.info(f"开始执行步骤：{step_name}")
    start_time = time.time()
    
    # 构建命令行参数
    cmd_args = [sys.executable, script_path]
    for arg_name, arg_value in args_dict.items():
        if arg_value is not None:
            if isinstance(arg_value, bool):
                if arg_value:
                    cmd_args.append(f"--{arg_name}")
            else:
                cmd_args.extend([f"--{arg_name}", str(arg_value)])
    
    # 执行命令
    try:
        logger.info(f"运行命令: {' '.join(cmd_args)}")
        result = subprocess.run(cmd_args, check=True, text=True, capture_output=True)
        
        if result.stdout:
            logger.info(f"输出:\n{result.stdout}")
        
        if result.stderr:
            logger.warning(f"错误输出:\n{result.stderr}")
        
        logger.info(f"步骤 {step_name} 执行完成，耗时: {time.time() - start_time:.2f}秒")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"步骤 {step_name} 执行失败: {str(e)}")
        if e.stdout:
            logger.error(f"输出:\n{e.stdout}")
        if e.stderr:
            logger.error(f"错误输出:\n{e.stderr}")
        return False

def main():
    """主函数"""
    args = parse_args()
    
    # 创建带时间戳的输出目录
    output_dir = create_timestamped_dir(args.output_dir)
    logger.info(f"将结果输出到：{output_dir}")
    
    # 记录开始时间
    start_time = time.time()
    pipeline_success = True
    
    # 构建文件路径
    kg_path = os.path.join(output_dir, "knowledge_graph.json")
    candidates_path = os.path.join(output_dir, "candidate_pairs.json")
    
    try:
        # 步骤1：构建知识图谱
        if not args.skip_build:
            build_args = {
                "csv_dir": args.csv_dir,
                "output_dir": output_dir,
                "visualize": args.visualize
            }
            
            if not run_step("build_kg.py", build_args, "构建知识图谱"):
                logger.error("构建知识图谱失败，终止流程")
                return 1
            
            logger.info(f"知识图谱已保存至 {kg_path}")
        else:
            logger.info("跳过知识图谱构建阶段")
            
        # 步骤2：筛选候选对齐实体
        if not args.skip_candidates:
            candidates_args = {
                "kg_path": kg_path,
                "output_dir": output_dir,
                "name_sim_threshold": args.name_sim_threshold,
                "emb_sim_threshold": args.emb_sim_threshold
            }
            
            if not run_step("find_candidates.py", candidates_args, "筛选候选对齐实体"):
                logger.error("筛选候选对齐实体失败，终止流程")
                return 1
            
            logger.info(f"候选对齐实体已保存至 {candidates_path}")
        else:
            logger.info("跳过候选实体筛选阶段")
        
        # 步骤3：执行实体对齐
        if not args.skip_alignment:
            alignment_args = {
                "kg_path": kg_path,
                "candidates_path": candidates_path,
                "output_dir": output_dir,
                "llm_api_url": args.llm_api_url,
                "llm_api_key": args.llm_api_key,
                "confidence_threshold": args.confidence_threshold,
                "top_k_features": args.top_k_features,
                "num_rounds": args.num_rounds
            }
            
            if not run_step("alignment.py", alignment_args, "执行实体对齐"):
                logger.error("执行实体对齐失败，终止流程")
                return 1
            
            logger.info("实体对齐已完成")
        else:
            logger.info("跳过实体对齐阶段")
        
        # 记录总体执行信息
        total_time = time.time() - start_time
        
        summary = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execution_time": total_time,
            "output_dir": output_dir,
            "csv_dir": args.csv_dir,
            "parameters": {
                "name_sim_threshold": args.name_sim_threshold,
                "emb_sim_threshold": args.emb_sim_threshold,
                "confidence_threshold": args.confidence_threshold,
                "top_k_features": args.top_k_features,
                "num_rounds": args.num_rounds,
                "visualize": args.visualize,
                "use_llm": bool(args.llm_api_url and args.llm_api_key)
            },
            "steps_executed": {
                "build_kg": not args.skip_build,
                "find_candidates": not args.skip_candidates,
                "alignment": not args.skip_alignment
            }
        }
        
        # 保存总结信息
        summary_path = os.path.join(output_dir, "pipeline_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"流程执行完成，总耗时: {total_time:.2f}秒")
        logger.info(f"流程总结已保存至：{summary_path}")
        
        return 0
    
    except Exception as e:
        logger.error(f"执行流程时出错: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 