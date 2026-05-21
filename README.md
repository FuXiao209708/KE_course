# KE_course

## 知识工程智能助教 Demo

这是一个前后端分离版本的 Demo。后端使用 Starlette + Uvicorn，前端通过浏览器直接访问 `http://127.0.0.1:8000/`。

## 运行方式

### 1. 激活 CDKG 环境

```powershell
conda activate CDKG
```

### 2. 安装依赖

```powershell
pip install -r requirements.txt
```

### 3. 启动后端

```powershell
python -m uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

### 4. 打开前端

浏览器访问：

```text
http://127.0.0.1:8000/
```

### 5. 说明

- 默认使用 Mock LLM，不需要配置 API Key。
- 如果你希望使用真实大模型，再设置 `OPENAI_API_KEY` 和 `LLM_MOCK=0`。
- 如果页面样式更新不明显，使用 `Ctrl+F5` 强制刷新浏览器缓存。

## 常见问题

- 如果直接执行 `python -m uvicorn ...` 提示 `No module named uvicorn`，说明当前解释器不是 `CDKG` 环境，需要先激活环境。
- 如果终端里出现旧的 `fastapi` 导入报错，通常是之前的旧进程输出，不代表当前 `backend.app` 还在使用 FastAPI。当前后端已切换为 Starlette。
