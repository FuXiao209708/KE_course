function askQuestion() {
    const question = document.getElementById('question').value.trim();
    if (!question) {
        document.getElementById('answer').innerText = '请输入问题';
        return;
    }
    document.getElementById('answer').innerText = '正在查询，请稍候...';
    document.getElementById('kg').innerText = '';
    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('answer').innerText = data.error;
        } else {
            document.getElementById('answer').innerText = data.answer;
            document.getElementById('kg').innerText = '知识图谱相关内容：' + JSON.stringify(data.kg, null, 2);
        }
    })
    .catch(err => {
        document.getElementById('answer').innerText = '查询失败，请重试';
    });
} 