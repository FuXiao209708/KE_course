import streamlit as st
from core import data_manager
from core.llm_client import LLMClient
from core.prompt_templates import EVAL_TEMPLATE
import json

def render():
    st.header("习题演练与诊断")
    exs = data_manager.get_exercises()
    emap = {e.get("title"): e for e in exs}
    sel = st.selectbox("选择习题", options=[e.get("title") for e in exs])
    ex = emap.get(sel)
    st.markdown("**题目描述**")
    st.write(ex.get("description"))
    answer = st.text_area("你的答案")
    if st.button("提交评判"):
        llm = LLMClient()
        if llm.mock:
            res = llm.evaluate_exercise(ex.get("title"), ex.get("standard_answer"), answer)
        else:
            prompt = EVAL_TEMPLATE.format(question=ex.get("title"), standard=ex.get("standard_answer"), answer=answer)
            reply = llm.chat_reply(prompt)
            try:
                res = json.loads(reply)
            except Exception:
                res = {"score": 0, "issues": ["解析失败"], "suggestions": []}
        st.metric("得分", res.get("score"))
        st.markdown("**思维误区**")
        for i in res.get("issues", []):
            st.warning(i)
        st.markdown("**建议**")
        for s in res.get("suggestions", []):
            st.info(s)
