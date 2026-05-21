import os
import json

class LLMClient:
    def __init__(self, mock=True):
        self.mock = mock or (os.environ.get("LLM_MOCK", "1") != "0")

    def chat_reply(self, prompt: str, context: dict = None) -> str:
        if self.mock:
            names = []
            if context and "entities" in context:
                names = [e.get("name") for e in context.get("entities", [])]
            return f"[MOCK] 基于图谱的启发式回答，相关实体：{', '.join(names)}。示例解释：这是一个演示回答。"
        # 真实调用留空（可扩展）
        return ""

    def evaluate_exercise(self, question: str, standard: str, answer: str) -> dict:
        if self.mock:
            return {"score": 82, "issues": ["未明确给出定义"], "suggestions": ["补充定义并举例"]}
        return {"score": 0, "issues": ["未启用真实模型"], "suggestions": []}
