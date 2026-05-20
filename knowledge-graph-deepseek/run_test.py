#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
运行知识图谱测试
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_test():
    """运行测试脚本"""
    logger.info("开始运行知识图谱测试")
    
    # 确保当前工作目录是项目根目录
    project_root = os.path.abspath(os.path.dirname(__file__))
    os.chdir(project_root)
    
    # 运行测试脚本
    test_script = os.path.join(project_root, "prompt_builder2", "test_kg.py")
    logger.info(f"运行测试脚本: {test_script}")
    
    try:
        # 使用Python解释器运行测试脚本
        result = subprocess.run([sys.executable, test_script], capture_output=True, text=True)
        
        # 输出测试结果
        if result.returncode == 0:
            logger.info("测试成功!")
            logger.info(result.stdout)
        else:
            logger.error("测试失败!")
            logger.error(result.stderr)
            return False
    except Exception as e:
        logger.error(f"运行测试时出错: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_test()
    if not success:
        sys.exit(1) 