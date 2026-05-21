ANSWER_TEMPLATE = """
你是课程助教。请基于以下用户问题和提供的图谱三元组，给出启发式、简洁的回答：

用户问题：{question}

图谱三元组：
{triples}

请以亲切、启发式助教的语气回答，重点指出概念间的联系并给出 1-2 个学习建议。
"""

EVAL_TEMPLATE = """
请以 JSON 格式给出评判，包含字段：score（0-100 整数），issues（字符串列表），suggestions（字符串列表）。
题目：{question}
标准答案：{standard}
学生答案：{answer}
"""
