import csv
import os
import sys
from pathlib import Path


def convert_txt_to_csv(input_file, output_file):
    """
    将单个TXT文件转换为CSV文件
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as txt_file:
            lines = [line.strip().split('\t') for line in txt_file if line.strip()]

        with open(output_file, 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(lines)

        print(f"转换成功: {input_file} → {output_file}")
        return True
    except Exception as e:
        print(f"转换失败 {input_file}: {str(e)}")
        return False


def batch_convert(input_dir, output_dir):
    """
    批量转换目录中的所有TXT文件
    """
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 统计信息
    total_files = 0
    success_files = 0

    # 遍历输入目录
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.txt'):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + '.csv'
            output_path = os.path.join(output_dir, output_filename)

            total_files += 1
            if convert_txt_to_csv(input_path, output_path):
                success_files += 1

    print(f"\n转换完成: 共处理 {total_files} 个文件，成功 {success_files} 个")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python batch_txt_to_csv.py <输入目录> <输出目录>")
        print("示例: python batch_txt_to_csv.py ./txt_files ./csv_files")
    else:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]

        if not os.path.isdir(input_dir):
            print(f"错误: 输入目录不存在 {input_dir}")
        else:
            batch_convert(input_dir, output_dir)