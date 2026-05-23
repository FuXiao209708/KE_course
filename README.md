# KE_course

## 知识工程智能助教 Demo

这是一个前后端分离版本的 Demo。后端使用 Starlette + Uvicorn，前端通过浏览器直接访问 `http://127.0.0.1:8000/`。

## 运行方式

### 1. 安装依赖

```powershell
pip install -r requirements.txt
```

### 2. 启动后端

```powershell
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

### 3. 打开前端

浏览器访问：

```text
http://127.0.0.1:8000/
```

### 4. 说明

- 默认使用 Mock LLM，不需要配置 API Key。
- 如果希望使用真实大模型，再设置 `OPENAI_API_KEY` 和 `LLM_MOCK=0`。
- 如果页面样式更新不明显，使用 `Ctrl+F5` 强制刷新浏览器缓存。

## 常见问题

- 如果直接执行 `python -m uvicorn ...` 提示 `No module named uvicorn`，说明当前 Python 环境尚未安装依赖，请先执行安装命令。
