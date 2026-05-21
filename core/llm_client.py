import os
import json

class LLMClient:
    def __init__(self, mock=True):
        # mock: 默认使用 Mock 模式，便于离线演示
        self.mock = mock or (os.environ.get("LLM_MOCK", "1") != "0")
        # 若用户希望使用真实 OpenAI-like API，可在环境变量设置 OPENAI_API_KEY 并传入 mock=False
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def chat_reply(self, prompt: str, context: dict = None) -> str:
        if self.mock:
            # 简单的 Mock 实现：基于 prompt 返回示例回答
            return self._mock_reply(prompt, context)
        # 真实调用（简化）：使用 openai.ChatCompletion 或对应 SDK
        try:
            import openai
            openai.api_key = self.api_key
            resp = openai.ChatCompletion.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[{"role":"user","content": prompt}],
                max_tokens=512,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"[ERROR] LLM 调用失败：{e}"

    def evaluate_exercise(self, question: str, standard: str, answer: str) -> dict:
        if self.mock:
            # 返回结构化的示例 JSON
            return {
                "score": 85,
                "issues": ["表达不够精确: 未明确区分本体与描述逻辑"],
                "suggestions": ["补充描述逻辑的定义并举例说明", "对比本体与描述逻辑的用途差异"],
            }
        try:
            # 在真实场景中，这里会调用 LLM 并解析 JSON 输出
            reply = self.chat_reply(f"请以 JSON 格式评判：题目：{question} 标准答案：{standard} 学生答案：{answer}")
            return json.loads(reply)
        except Exception:
            return {"score": 0, "issues": ["解析错误"], "suggestions": []}

    def _mock_reply(self, prompt: str, context: dict = None) -> str:
        # 简单示例：如果 prompt 中包含关键词则返回带有该关键词的示例回答
        if context and "entities" in context:
            names = [e.get("name") for e in context.get("entities", [])]
            return f"这是基于图谱的启发式回答，相关实体：{', '.join(names)}。示例解释：..."
        return "这是一个示例回复，用于离线演示。"
