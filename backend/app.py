from starlette.applications import Starlette
from starlette.responses import JSONResponse, FileResponse, PlainTextResponse
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
from starlette.requests import Request
from pathlib import Path
import json

from backend.core.llm_client import LLMClient
from backend.core.graph_query import query_graph_by_keywords, load_graph

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT.parent / "frontend"
ASSETS_DIR = ROOT.parent / "assets"

llm = LLMClient(mock=True)


async def get_demo_questions(request):
    path = ROOT / "data" / "script_config.json"
    try:
        return JSONResponse(content=json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return JSONResponse(content={"demo_questions": []})


async def get_exercises(request):
    path = ROOT / "data" / "mock_exercises.json"
    try:
        return JSONResponse(content=json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return JSONResponse(content={"exercises": []})


async def api_qa(request: Request):
    body = await request.json()
    question = body.get("question", "")
    keywords = body.get("keywords", [])
    graph = query_graph_by_keywords(keywords)
    reply = llm.chat_reply(question, context=graph)
    return JSONResponse(content={"reply": reply, "graph": graph})


async def api_grade(request: Request):
    body = await request.json()
    question_id = body.get("question_id")
    student_answer = body.get("student_answer", "")
    ex_path = ROOT / "data" / "mock_exercises.json"
    exs = json.loads(ex_path.read_text(encoding="utf-8")).get("exercises", [])
    ex = next((e for e in exs if e.get("id") == question_id or e.get("title") == question_id), exs[0])
    res = llm.evaluate_exercise(ex.get("title"), ex.get("standard_answer"), student_answer)
    return JSONResponse(content=res)


async def api_graph(request: Request):
    g = load_graph()
    return JSONResponse(content={"entities": g.get("entities", []), "relations": g.get("relations", [])})


async def index(request):
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return PlainTextResponse("Index not found", status_code=404)


routes = [
    Route("/api/demo_questions", get_demo_questions, methods=["GET"]),
    Route("/api/exercises", get_exercises, methods=["GET"]),
    Route("/api/qa", api_qa, methods=["POST"]),
    Route("/api/grade", api_grade, methods=["POST"]),
    Route("/api/graph", api_graph, methods=["GET"]),
    Route("/", index, methods=["GET"]),
    Mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets"),
    Mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static"),
]

app = Starlette(debug=True, routes=routes)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

