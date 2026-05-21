import streamlit as st
from core import data_manager
from core.llm_client import LLMClient
from core.prompt_templates import ANSWER_TEMPLATE
from pyvis.network import Network
import streamlit.components.v1 as components
from pathlib import Path

def _render_pyvis(subgraph: dict, height=450):
    net = Network(height=f"{height}px", width="100%", directed=False)
    for e in subgraph.get("entities", []):
        net.add_node(e.get("id"), label=e.get("name"), title=e.get("description", ""), color=e.get("color", "#97c2fc"), size=e.get("size", 20))
    for r in subgraph.get("relations", []):
        net.add_edge(r.get("source"), r.get("target"), title=r.get("label", ""))
    tmp_path = Path("temp_graph.html")
    net.show(str(tmp_path))
    with open(tmp_path, "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=height+50)

def render():
    st.header("启发式答疑")
    questions = data_manager.get_demo_questions()
    qmap = {q.get("question"): q for q in questions}
    sel = st.selectbox("选择演示问题", options=[q.get("question") for q in questions])
    user_input = st.text_area("或输入你的问题（可修改）", value=sel)
    if st.button("提问"):
        q = qmap.get(sel)
        keywords = q.get("keywords", []) if q else []
        sub = data_manager.query_graph_by_keywords(keywords)
        # 组装 triples 文本
        triples = []
        for r in sub.get("relations", []):
            src = next((e.get("name") for e in sub.get("entities", []) if e.get("id")==r.get("source")), r.get("source"))
            tgt = next((e.get("name") for e in sub.get("entities", []) if e.get("id")==r.get("target")), r.get("target"))
            triples.append(f"{src} -[{r.get('type')}]-> {tgt}: {r.get('label')}")
        prompt = ANSWER_TEMPLATE.format(question=user_input, triples="\n".join(triples))
        llm = LLMClient()
        reply = llm.chat_reply(prompt, context=sub)
        st.markdown("**助教回答：**")
        st.write(reply)
        st.markdown("**相关图谱子图：**")
        _render_pyvis(sub)
