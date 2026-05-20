# 知识图谱构建与实体对齐工具

本工具用于从CSV三元组构建知识图谱，并执行内部实体对齐任务，识别知识图谱中表示相同概念的不同实体。该工具将流程分为三个独立的部分，也可以通过主流程一键执行所有步骤。

## 功能特点

1. **知识图谱构建**：从CSV三元组数据构建完整的知识图谱
2. **图谱可视化**：生成知识图谱的可视化表示
3. **候选实体筛选**：基于名称相似度和向量嵌入相似度筛选候选对齐实体
4. **实体对齐**：
   - 启发式属性和关系选择：基于可识别性指标选择特征
   - 多轮投票机制：多次独立推理并投票确定最终对齐结果
   - 知识图谱更新：合并对齐实体，优化知识图谱结构

## 目录结构

```
Align/
├── build_kg.py             # 第一部分：构建知识图谱并保存
├── find_candidates.py      # 第二部分：读取知识图谱并筛选候选对齐实体
├── alignment.py            # 第三部分：进行实体对齐并修改知识图谱
├── run_pipeline.py         # 完整流程执行脚本
├── requirements.txt        # 依赖列表
└── README.md               # 说明文档
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 一键执行完整流程

```bash
python run_pipeline.py --csv_dir /path/to/csv/files --output_dir /path/to/output
```

### 分步执行

1. 第一步：构建知识图谱

```bash
python build_kg.py --csv_dir /path/to/csv/files --output_dir /path/to/output
```

2. 第二步：筛选候选对齐实体

```bash
python find_candidates.py --kg_path /path/to/knowledge_graph.json --output_dir /path/to/output
```

3. 第三步：执行实体对齐并更新知识图谱

```bash
python alignment.py --kg_path /path/to/knowledge_graph.json --candidates_path /path/to/candidate_pairs.json --output_dir /path/to/output
```

## 参数说明

### 通用参数

- `--output_dir`: 输出目录，默认为`/root/autodl-tmp/knowledge-graph-deepseek/Align/output`

### 知识图谱构建参数

- `--csv_dir`: CSV三元组文件目录，默认为`/root/autodl-tmp/knowledge-graph-deepseek/output/test`
- `--visualize`: 是否生成知识图谱可视化（不需要参数值）

### 候选实体筛选参数

- `--kg_path`: 知识图谱JSON文件路径
- `--name_sim_threshold`: 名称相似度阈值，默认为0.5
- `--emb_sim_threshold`: 嵌入相似度阈值，默认为0.6
- `--max_candidates`: 最大候选对齐实体对数量，默认为500

### 实体对齐参数

- `--kg_path`: 知识图谱JSON文件路径
- `--candidates_path`: 候选对齐实体对文件路径
- `--llm_api_url`: 大语言模型API URL（可选）
- `--llm_api_key`: 大语言模型API密钥（可选）
- `--confidence_threshold`: 置信度阈值，默认为0.7
- `--top_k_features`: 选择的Top-K特征数量，默认为3
- `--num_rounds`: 多轮投票的轮数，默认为3

### 完整流程参数

除了上述所有参数外，还支持：

- `--skip_build`: 跳过知识图谱构建阶段（不需要参数值）
- `--skip_candidates`: 跳过候选实体筛选阶段（不需要参数值）
- `--skip_alignment`: 跳过实体对齐阶段（不需要参数值）

## 输出结果

程序输出将包含以下内容：

1. **知识图谱构建阶段**：
   - `knowledge_graph.json`: 构建的知识图谱
   - `kg_stats.json`: 知识图谱统计信息
   - `knowledge_graph_visualization.png`: 知识图谱可视化图像（如启用）

2. **候选实体筛选阶段**：
   - `candidate_pairs.json`: 候选对齐实体对列表

3. **实体对齐阶段**：
   - `entity_alignment_results.json`: 实体对齐结果
   - `equivalence_clusters.json`: 等价类信息
   - `updated_knowledge_graph.json`: 更新后的知识图谱
   - `alignment_stats.json`: 对齐统计信息

4. **完整流程**：
   - `pipeline_summary.json`: 流程执行总结信息

## 实体对齐方法

本工具实现了一个综合实体对齐流程，包括：

1. **候选对齐选择**：使用名称模糊匹配和语义嵌入相似度选择候选对齐实体。

2. **启发式属性和关系选择**：通过计算属性和关系的可识别性（函数度和频率）来选择最重要的特征。
   - 属性可识别性：`ident_att(a, C_e) = fun_att(a) × freq_att(a, C_e)`
   - 关系可识别性：`ident_rel(r, C_e) = fun_rel(r) × freq_rel(r, C_e)`

3. **对齐提示构建**：基于选择的特征构建实体对齐提示。

4. **多轮投票机制**：多次独立推理，通过投票确定最终对齐结果。

5. **知识图谱更新**：合并对齐实体，优化知识图谱结构。 