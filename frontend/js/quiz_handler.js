window.initQuiz = async function(){
  const resp = await fetch('/api/exercises');
  const data = await resp.json();
  const list = data.exercises || [];
  const quizList = document.getElementById('quiz-list');
  quizList.innerHTML = list.map(q=>`<div class=\"list-card\"><h4 class=\"font-semibold\">${q.title}</h4><p class=\"text-sm text-slate-600\">${q.description}</p><button data-id=\"${q.id}\" class=\"mt-3 btn-soft select-question\">选择</button></div>`).join('');

  document.querySelectorAll('.select-question').forEach(btn=>{
    btn.onclick = ()=>{
      const id = btn.dataset.id;
      const q = list.find(x=>x.id===id);
      document.getElementById('selected-question').innerHTML = `<h4 class=\"font-semibold\">${q.title}</h4><p class=\"text-sm text-slate-600\">${q.description}</p>`;
      document.getElementById('submit-quiz').dataset.qid = q.id;
    };
  });

  document.getElementById('submit-quiz').onclick = async ()=>{
    const qid = document.getElementById('submit-quiz').dataset.qid;
    const ans = document.getElementById('student-answer').value;
    if(!qid) return alert('请选择题目');
    const res = await fetch('/api/grade', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question_id: qid, student_answer: ans})});
    const j = await res.json();
    const diag = document.getElementById('diagnostic');
    diag.innerHTML = `
      <div class=\"mb-3\"><div class=\"progress-bar\"><div class=\"inner\" style=\"width:${j.score}%\"></div></div></div>
      <div class=\"mb-2\"><h4 class=\"font-semibold\">思维误区</h4>${j.issues.map(i=>`<div class=\"notice notice-danger mt-2\">${i}</div>`).join('')}</div>
      <div><h4 class=\"font-semibold\">建议</h4>${j.suggestions.map(s=>`<div class=\"notice notice-success mt-2\">${s}</div>`).join('')}</div>
    `;
    // trigger progress bar animation
    setTimeout(()=>{
      const inner = diag.querySelector('.inner');
      if(inner) inner.style.width = j.score + '%';
    }, 50);
  };
};
