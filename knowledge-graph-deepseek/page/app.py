from flask import Flask, render_template, request, jsonify
from kg_utils import query_kg
from deepseek_api import get_keywords, generate_answer

app = Flask(__name__, template_folder='templates', static_folder='static')

def triples_to_text(kg_result):
    """将KG检索结果转为自然语言上下文"""
    lines = []
    for item in kg_result:
        head = item['node'].get('name', '')
        for neighbor in item['neighbors']:
            rel = neighbor.get('relation', '')
            tail = neighbor['node'].get('name', '')
            if rel:
                lines.append(f"{head} 的 {rel} 是 {tail}")
            else:
                lines.append(f"{head} 关联 {tail}")
    return '\n'.join(lines)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question', '')
    if not question:
        return jsonify({'error': '问题不能为空'}), 400
    keywords_json = get_keywords(question)
    print(keywords_json)
    kg_result = query_kg(keywords_json)
    #print(kg_result)
    kg_text = triples_to_text(kg_result)
    #print(kg_text)
    context = f"用户问题：{question}\n外部知识：{kg_text}"
    print(context)
    answer = generate_answer(context)
    return jsonify({'answer': answer, 'kg': kg_result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 