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

## 许可证

[MIT License](LICENSE)

## 联系方式

如有问题或建议，请提交Issue或联系项目维护者。
