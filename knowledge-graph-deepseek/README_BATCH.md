# 知识图谱批量处理工具

该工具用于批量处理JSON文件并构建知识图谱，实现了从文本中提取实体、关系和属性的完整流程。

## 功能介绍

该工具实现了以下五个步骤的流程：

1. **合成样本生成**：为schema中定义的每种关系类型生成合成样本，包括同义词、示例句子和重述句子，作为后续提取的提示。
2. **实体提取**：从每条记录中提取知识点实体及其类型。
3. **属性三元组提取**：提取实体的属性关系，如"被定义为"、"英文名"等。
4. **关系三元组提取**：提取实体之间的关系，如"包含"、"实例"等。
5. **三元组验证**：验证并修正提取的三元组，确保其准确性和符合schema定义。

## 最新优化改进

1. **增强的合成样本生成**：
   - 每生成一个关系的合成样本后立即保存，避免中断导致重复生成
   - 检测和补充缺失的关系合成样本
   - 添加延迟，避免API调用过于频繁

2. **动态关系处理**：
   - 在处理文本时实时检查是否存在关系的合成样本
   - 自动为缺失的关系生成合成样本
   - 支持处理单个文件或整个目录

3. **健壮性增强**：
   - 异常处理和错误恢复机制
   - 支持不同的工作目录和路径配置

## 使用说明

### 环境准备

1. 确保已安装所需依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 配置DeepSeek API（或其他LLM API）：
   - 设置环境变量：`DEESEEK_API_KEY`和`DEESEEK_API_URL`
   - 或在运行时通过命令行参数指定

### 运行方式

基本运行命令：
```bash
python batch_processor.py
```

可用的命令行参数：
- `--api_key`：指定API密钥
- `--api_url`：指定API URL
- `--json_dir`：指定JSON文件目录（默认为`dataset/json`）
- `--samples`：指定合成样本保存路径（默认为`output/synthetic_samples.json`）
- `--regenerate`：强制重新生成合成样本

示例：
```bash
# 使用自定义API密钥和URL
python batch_processor.py --api_key=your_api_key --api_url=your_api_url

# 处理特定目录的JSON文件
python batch_processor.py --json_dir=path/to/json/files

# 处理单个JSON文件
python batch_processor.py --json_dir=path/to/json/file.json

# 强制重新生成合成样本
python batch_processor.py --regenerate
```

## 输出结果

处理结果将保存在以下目录：
- `output/csv/`：包含初步提取的三元组数据
- `output/validated/`：包含验证后的三元组数据
- `output/synthetic_samples.json`：生成的合成样本数据

输出的CSV文件格式如下（以制表符分隔）：
```
input   subject   subject_type   data/object   relation   object   object_type
```

字段说明：
- `input`：原始输入文本
- `subject`：主语实体
- `subject_type`：主语实体类型
- `data/object`：标识宾语是属性值（data）还是实体（object）
- `relation`：关系类型
- `object`：宾语（属性值或实体）
- `object_type`：宾语的实体类型（仅当宾语是实体时）

## 数据Schema

### 实体类型
- 知识图谱、知识表示、知识存储、知识抽取、知识融合
- 知识推理、语义搜索、知识问答、链接、知识图谱项目

### 属性关系
- 被定义为、内容、英文名、目标、作用
- 特点、方法、缺点、语法、链接
- 创建时间、创建者

### 实体关系
- 包含：表示主语知识点有宾语的分支
- 实例：表示主语知识点是宾语的一种具体体现
- 等价：表示两个知识点含义相同
- 发展为：表示主语知识点发展成为宾语知识点（因果关系）
- 前提：表示主语知识点需要宾语作为前提
- 实现：表示主语知识点可以实现宾语的要求/达成宾语
- 习题：表示主语知识点有宾语的习题

## 注意事项

1. 处理大量文本可能需要较长时间，请耐心等待。
2. API调用可能会产生费用，请注意控制API请求数量。
3. 合成样本生成完成后会保存到文件，后续运行时可以直接加载，避免重复生成。
4. 如需处理大型文件，建议增加内存配置或分批处理。
5. 在处理过程中如果遇到缺失的关系样本，脚本会自动生成并保存。
6. 可以通过修改代码中的`time.sleep()`参数来调整API调用的间隔时间。 