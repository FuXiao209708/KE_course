window.initQuiz = async function(){
  const resp = await fetch('/api/exercises');
  const data = await resp.json();
  const list = data.exercises || [];
  const quizList = document.getElementById('quiz-list');
  quizList.innerHTML = list.map(q=>`<div class="list-card"><h4 class="font-semibold">${q.title}</h4><button data-id="${q.id}" class="mt-3 btn-soft select-question">选择</button></div>`).join('');

  document.querySelectorAll('.select-question').forEach(btn=>{
    btn.onclick = ()=>{
      const id = btn.dataset.id;
      const q = list.find(x=>x.id===id);
      document.getElementById('selected-question').innerHTML =
        `<h4 class="quiz-q-title">${q.title}</h4><p class="quiz-q-desc">${q.description}</p>`;
      document.getElementById('submit-quiz').dataset.qid = q.id;
      document.getElementById('diagnostic').innerHTML = '';
      document.getElementById('student-answer').value = '';
    };
  });

  document.getElementById('submit-quiz').onclick = async ()=>{
    const qid = document.getElementById('submit-quiz').dataset.qid;
    const ans = document.getElementById('student-answer').value;
    if(!qid) return alert('请选择题目');
    const diag = document.getElementById('diagnostic');

    // 检查是否是demo答案
    const demoResults = {
      'ex01': {
        trigger: '全局消歧比局部消歧更稳健',
        score: 92,
        issues: [],
        suggestions: [
          '✓ 准确指出了局部消歧只关注单个mention的局限性',
          '✓ 正确阐述了全局消歧利用多实体间语义一致性的核心思想',
          '✓ 举例说明了全局约束如何避免局部最优但全局不一致的问题',
          '建议：可以进一步提及全局消歧的具体算法（如图模型、联合推理等）会更完整'
        ]
      },
      'ex002': {
        trigger: '首先需要对Web表格进行预处理',
        score: 45,
        issues: [
          '✗ 未明确指出三步核心流程：实体链接、列类型识别、关系抽取',
          '✗ 将预处理、分词等通用NLP步骤误认为是三元组抽取的主要环节',
          '✗ 缺少对"mention → KB entity"这一实体链接关键步骤的理解',
          '✗ 未提及列类型识别（column → class/type）的作用'
        ],
        suggestions: [
          '建议重点掌握：Entity Linking + Column Typing + Relation Extraction 三步流水线',
          '建议理解每一步的具体目标：实体链接解决"指向谁"，列类型识别解决"属于什么类"，关系抽取解决"两列是什么关系"'
        ]
      }
    };

    const demoResult = demoResults[qid];
    const isDemoAnswer = demoResult && ans.includes(demoResult.trigger);

    // 加载动画
    diag.innerHTML = `
      <div class="quiz-loading">
        <div class="quiz-loading-dots">
          <span></span><span></span><span></span>
        </div>
        <div class="quiz-loading-text">AI 正在评判中...</div>
      </div>`;

    let j;
    if (isDemoAnswer) {
      // 使用预设的demo结果
      await new Promise(r => setTimeout(r, 1200));
      j = demoResult;
    } else {
      // 调用真实API
      const res = await fetch('/api/grade', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question_id: qid, student_answer: ans})});
      j = await res.json();
      await new Promise(r => setTimeout(r, 600));
    }

    // 找到当前题目的参考答案
    const q = list.find(x => x.id === qid);
    const stdAnswer = q ? (q.standard_answer || '暂无参考答案') : '暂无参考答案';

    diag.innerHTML = `
      <div class="mb-4">
        <div class="progress-bar"><div class="inner" style="width:0%"></div></div>
        <div class="mt-1 text-sm text-slate-500">得分：${j.score} 分</div>
      </div>
      <div class="mb-4">
        <div class="section-title mb-2" style="font-size:0.95rem;">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M9 11l3 3L22 4"/></svg>
          智能评价
        </div>
        ${j.issues.map(i=>`<div class="notice notice-danger mt-2">${i}</div>`).join('')}
        ${j.suggestions.map(s=>`<div class="notice notice-success mt-2">${s}</div>`).join('')}
      </div>
      <div>
        <div class="section-title mb-2" style="font-size:0.95rem;">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
          参考答案
        </div>
        <div class="notice notice-info mt-2">${stdAnswer}</div>
      </div>
    `;
    setTimeout(()=>{
      const inner = diag.querySelector('.inner');
      if(inner) inner.style.width = j.score + '%';
    }, 50);
  };

  // 选项卡切换（仅UI效果）
  document.querySelectorAll('.quiz-tab').forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll('.quiz-tab').forEach(t => t.classList.remove('is-active'));
      tab.classList.add('is-active');
    };
  });
};
