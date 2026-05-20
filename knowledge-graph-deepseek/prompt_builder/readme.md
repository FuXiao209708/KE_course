# 知识图谱构建工具

基于大语言模型的知识图谱构建工具，用于从《知识工程》领域文本中自动构建知识图谱。

## 功能描述

该工具实现了一种利用大语言模型构建《知识工程》教材知识图谱的方法，能够从非结构化文本中自动提取知识点的三元组（S-P-O），用于构建知识工程课程知识点的知识图谱。

工具包含六个主要步骤：

1. **关系同义词与合成样本生成**：为每种关系类型生成同义词和包含该关系的示例句子
2. **知识点实体抽取**：从文本中提取知识工程相关的术语和概念
3. **属性三元组抽取**：抽取实体的属性信息，如定义、特点、作用等
4. **关系三元组抽取**：抽取实体之间的关系，如包含、等价、实现等
5. **知识三元组迭代验证**：验证和修正抽取的三元组
6. **知识融合与实体对齐**：合并表达同一概念的实体，补全知识图谱

## 安装与依赖

1. 克隆本仓库：
```bash
git clone <repository-url>
cd knowledge-graph-builder
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

依赖包括：
- requests
- tqdm
- json
- re
- logging

## 使用方法

### 命令行使用

```bash
python kg_builder.py --input 文本文件路径.txt --output 输出结果.json --api_key YOUR_API_KEY --api_url YOUR_API_URL
```

参数说明：
- `--input`：输入文本文件路径（必需）
- `--output`：输出结果文件路径（默认为kg_output.json）
- `--api_key`：大语言模型API密钥（可选）
- `--api_url`：大语言模型API URL（可选）

### 作为模块导入

```python
from kg_builder import KnowledgeGraphBuilder

# 创建知识图谱构建工具实例
builder = KnowledgeGraphBuilder(llm_api_key="YOUR_API_KEY", llm_api_url="YOUR_API_URL")

# 处理文本
with open("文本文件.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 处理文本并获取结果
results = builder.process_text(text)

# 保存结果
builder.save_results(results, "output.json")
```

### 运行示例

```bash
python kg_example.py
```

## 实体类型与关系模式

### 属性关系

- 被定义为：表示一个实体或概念的定义或解释
- 内容：表示一个实体或概念的具体内容
- 英文名：表示一个实体或概念的英文名称或缩写
- 目标：表示一个实体或概念的目标或意图
- 作用：表示一个实体或概念的功能或用途
- 特点：表示一个实体或概念的特征或特性
- 方法：表示一个实体或概念的实现方法或技术
- 缺点：表示一个实体或概念的不足或局限性
- 语法：表示一个实体或概念的语法规则或格式
- 链接：表示一个实体或概念的相关网络资源链接

### 实体间关系

- 包含：表示主语知识点有宾语的分支
- 实例：表示主语知识点是宾语的一种具体体现
- 等价：表示两个知识点含义相同
- 发展为：表示主语知识点发展成为宾语知识点（因果关系）
- 前提：表示主语知识点需要宾语作为前提
- 实现：表示主语知识点可以实现宾语的要求/达成宾语
- 习题：表示主语知识点有宾语的习题

## 输出结果格式

输出结果为JSON格式，包含以下字段：

```json
{
  "entities": ["实体1", "实体2", ...],
  "attribute_triples": [
    {"subject": "实体1", "predicate": "被定义为", "object": "定义内容"},
    ...
  ],
  "relation_triples": [
    {"subject": "实体1", "predicate": "包含", "object": "实体2"},
    ...
  ],
  "validated_triples": [...]
}
```

## 自定义与扩展

您可以通过修改以下部分来自定义工具的行为：

1. 修改`relation_schema`字典来添加或修改关系类型和描述
2. 调整`attribute_relations`和`entity_relations`列表来更改关系分类
3. 实现自己的`call_llm_api`方法来使用不同的大语言模型API

# 知识图谱批量处理工具

本工具用于批量处理JSON文件，从中提取知识点、关系，并构建知识图谱。

## 功能介绍

该工具实现流程，主要包括以下功能：

1. **批量处理JSON文件** - 处理dataset/json目录中的JSON文件，每个文件包含多条JSON记录，记录格式为`{"text": "文本内容"}`
2. **知识点提取** - 从文本中提取知识点实体及其类型
3. **属性关系提取** - 提取知识点的属性关系，如"被定义为"、"目标"等
4. **实体关系提取** - 提取知识点之间的关系，如"包含"、"实例"等
5. **三元组验证** - 验证和修复提取的三元组

## 使用说明

### 环境准备

1. 确保已安装所需依赖：
   ```
   pip install -r requirements.txt
   ```

2. 配置大语言模型API：
   - 设置环境变量`DEESEEK_API_KEY`和`DEESEEK_API_URL`
   - 或在代码中直接设置`llm_api_key`和`llm_api_url`

### 执行批处理

1. 批量处理JSON文件，生成初步三元组：
   ```
   python batch_process.py
   ```
   处理结果将保存在`output/csv`目录中

2. 验证和修复三元组：
   ```
   python validate_triples.py
   ```
   验证结果将保存在`output/validated`目录中

## 注意事项

1. 处理大量文件可能需要较长时间，请耐心等待
2. 每次调用API都会消耗配额，请确保有足够的额度
3. 为提高效率，已将合成样本生成限制为每种关系3个

## 可能的改进

1. 添加多线程/多进程处理功能，提高效率
2. 实现断点续传功能，避免中断后需要重新处理
3. 添加更详细的进度和统计信息
4. 增加参数配置功能，可以自定义处理的文件和关系类型

## 输出格式

最终输出的CSV文件格式如下：

| 列名 | 说明 |
| --- | --- |
| input | 原始输入文本 |
| subject | 主语实体 |
| subject_type | 主语实体类型 |
| data/object | 标识宾语是数据还是实体 |
| relation | 关系类型 |
| object | 宾语内容或实体 |
| object_type | 宾语实体类型（若宾语为实体） |

## 示例

输入：
```json
{"text": "知识图谱是一种用图模型来描述知识和建模世界万物之间的关联关系的技术方法。"}
```

输出：
```
input,subject,subject_type,data/object,relation,object,object_type
知识图谱是一种用图模型来描述知识和建模世界万物之间的关联关系的技术方法。,知识图谱,知识图谱,data,被定义为,一种用图模型来描述知识和建模世界万物之间的关联关系的技术方法,
``` 
