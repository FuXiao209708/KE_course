#!/bin/bash

# 知识图谱批量处理工具运行脚本

# 设置API密钥和URL（请替换为实际的值）
export DEESEEK_API_KEY="your_api_key_here"
export DEESEEK_API_URL="your_api_url_here"

# 创建输出目录
mkdir -p output/csv
mkdir -p output/validated

echo "================================================================"
echo "知识图谱批量处理工具"
echo "================================================================"

# 显示菜单
echo "请选择操作："
echo "1. 生成合成样本"
echo "2. 处理所有JSON文件"
echo "3. 处理单个JSON文件"
echo "4. 验证CSV文件"
echo "5. 运行完整流程"
echo "0. 退出"
echo "================================================================"

read -p "请输入选项（0-5）: " choice

case $choice in
    1)
        echo "开始生成合成样本..."
        python batch_processor.py --regenerate
        ;;
    2)
        echo "开始处理所有JSON文件..."
        python batch_processor.py
        ;;
    3)
        echo "可用的JSON文件："
        ls -1 dataset/json/*.json
        echo "----------------------------------------------------------------"
        read -p "请输入要处理的文件名（例如：1.json）: " filename
        if [ -f "dataset/json/$filename" ]; then
            echo "开始处理文件 $filename..."
            python process_single_file.py --file "dataset/json/$filename"
        else
            echo "文件不存在: dataset/json/$filename"
        fi
        ;;
    4)
        echo "可用的CSV文件："
        ls -1 output/csv/*_output.csv 2>/dev/null
        echo "----------------------------------------------------------------"
        read -p "请输入要验证的CSV文件名（例如：1_output.csv）: " csvname
        if [ -f "output/csv/$csvname" ]; then
            echo "开始验证文件 $csvname..."
            # 创建临时脚本进行验证
            cat > validate_temp.py << EOF
from batch_processor import BatchProcessor
processor = BatchProcessor()
processor.validate_csv("output/csv/$csvname")
EOF
            python validate_temp.py
            rm validate_temp.py
        else
            echo "文件不存在: output/csv/$csvname"
        fi
        ;;
    5)
        echo "开始运行完整流程..."
        python batch_processor.py
        ;;
    0)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效的选项"
        ;;
esac

echo "================================================================"
echo "操作完成！"
echo "处理结果保存在output目录中"
echo "================================================================" 