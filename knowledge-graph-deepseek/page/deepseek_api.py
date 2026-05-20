import os
from openai import OpenAI
import json
import re

# 允许的关系集合
ALLOWED_RELATIONS = [
    "被定义为", "内容", "英文名", "目标", "作用", "特点", "方法", "缺点", "语法", "链接",
    "包含", "实例", "等价", "发展为", "前提", "实现", "习题"
]

def get_keywords(question):
    """调用DeepSeek API提取关键词，返回JSON格式，包含entities和relation"""
    api_url = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com")
    api_key = os.environ.get("DEEPSEEK_API_KEY", "sk-d368a8bcf4ef4356a2b0f37a5fec7258")
    model_name = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    if not api_key:
        # 本地模拟
        return {"entities": [question], "relation": []}
    prompt = (
        "请从以下用户问题中提取核心关键词（实体、关系），输出JSON格式,要求如下：\n"
        "1. 确保输出JSON格式，示例：{\"entities\": [\"知识表示\"],  \"relation\": [\"被定义为\"]}\n"
        "2. 保留原文本中的术语表达\n"
        "3. 关系应该是以下关系中的一种：" + ",".join(ALLOWED_RELATIONS) + "\n"
        f"用户问题：{question}"
    )
    client = OpenAI(api_key=api_key, base_url=api_url)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "你是一个专业的中文关键词提取助手。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=128
    )
    content = response.choices[0].message.content.strip()
    print(content)
    # 尝试解析为JSON
    '''
    try:
        result = json.loads(content)
        # 只保留允许的关系
        if "relation" in result:
            result["relation"] = [r for r in result["relation"] if r in ALLOWED_RELATIONS]
        return result
    except Exception:
        # 兜底：返回entities为原问题，relation为空
        return {"entities": [question], "relation": []}
    '''
    try:
        result = json.loads(content)
        # 只保留允许的关系
        if "relation" in result:
            result["relation"] = [r for r in result["relation"] if r in ALLOWED_RELATIONS]
        return result
    except json.JSONDecodeError:
        # 如果不是有效的JSON，尝试提取JSON部分
        try:
            # 尝试提取被```json包裹的内容
            json_match = re.search(r'```json\n?(.*?)\n?```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1).strip()
                result = json.loads(json_str)

                # 结构验证和关系过滤
                if "relation" in result:
                    result["relation"] = [r for r in result["relation"] if r in ALLOWED_RELATIONS]
                return {
                    "entities": result.get("entities", [question]),
                    "relation": result.get("relation", [])
                }

            # 尝试提取最像JSON的部分（无代码块标记的情况）
            json_candidate = re.search(r'\{.*\}', content, re.DOTALL)
            if json_candidate:
                result = json.loads(json_candidate.group())
                return {
                    "entities": result.get("entities", [question]),
                    "relation": [r for r in result.get("relation", []) if r in ALLOWED_RELATIONS]
                }

        except Exception as e:
            print(f"JSON提取失败: {str(e)}")


def generate_answer(context):
    """调用DeepSeek API生成自然语言答案"""
    api_url = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com")
    api_key = os.environ.get("DEEPSEEK_API_KEY", "sk-d368a8bcf4ef4356a2b0f37a5fec7258")
    model_name = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
    if not api_key:
        return f"[模拟答案] {context}"
    prompt = f"请根据以下内容，生成对用户问题的简明、准确的中文回答。\n{context}"
    client = OpenAI(api_key=api_key, base_url=api_url)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "你是一个专业的知识工程课程问答助手。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=512
    )
    return response.choices[0].message.content.strip()
