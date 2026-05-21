import streamlit as st
from importlib import import_module
from pathlib import Path

st.set_page_config(page_title="知识工程智能助教 Demo", layout="wide")

ROOT = Path(__file__).parent

st.title("知识工程智能助教 — Demo")

pages = {
    "启发式答疑": "pages.1_启发式答疑",
    "习题演练与诊断": "pages.2_习题演练诊断",
}

choice = st.sidebar.selectbox("选择页面", list(pages.keys()))

module_name = pages[choice]
module = import_module(module_name)
if hasattr(module, "render"):
    module.render()
else:
    st.error("页面实现缺少 render() 方法")
