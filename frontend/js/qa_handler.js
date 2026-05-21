window.initQA = async function() {
  // load demo questions
  const dq = await fetch('/api/exercises');
  const data = await dq.json();
  let exercises = data.exercises || [];
  // Also use backend script_config for demo questions
  const resp = await fetch('/api/demo_questions');
  const qdata = await resp.json();
  const demoQs = qdata.demo_questions || [];

  const demoContainer = document.getElementById('demo-questions');
  demoContainer.innerHTML = demoQs.map(q => `<button class=\"w-full text-left p-3 demo-q chip\" data-kw=\"${q.keywords.join(',')}\">${q.question}</button>`).join('');

  document.querySelectorAll('.demo-q').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const txt = document.getElementById('qa-input');
      txt.value = btn.textContent;
      txt.dataset.keywords = btn.dataset.kw;
    });
  });

  const sendBtn = document.getElementById('qa-send');
  const input = document.getElementById('qa-input');
  const chatWindow = document.getElementById('chat-window');

  function addMessage(role, text){
    const el = document.createElement('div');
    el.className = role === 'user' ? 'text-right' : 'text-left';
    const bubbleClass = role === 'user'
      ? 'bg-emerald-800 text-white'
      : 'bg-amber-50 text-slate-800 border border-amber-200';
    el.innerHTML = `<div class=\"inline-block max-w-[85%] p-3 rounded-xl shadow-sm ${bubbleClass}\">${text}</div>`;
    chatWindow.appendChild(el);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  sendBtn.onclick = async ()=>{
    const question = input.value;
    const keywords = (input.dataset.keywords || '').split(',').filter(Boolean);
    addMessage('user', question);
    // loading indicator
    addMessage('assistant', `<span class='dot-flash'><span></span><span></span><span></span></span> 正在思考...`);
    // call backend
    const resp = await fetch('/api/qa', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question, keywords})});
    const j = await resp.json();
    // remove last assistant loading
    chatWindow.removeChild(chatWindow.lastChild);
    addMessage('assistant', j.reply);
    // render graph using vis.js if available
    if(window.vis){
      const nodes = new vis.DataSet(j.graph.entities.map(e=>({id:e.id,label:e.name,color:e.color,size:e.size})));
      const edges = new vis.DataSet(j.graph.relations.map(r=>({from:r.source,to:r.target,label:r.label, width:2})));
      const container = document.getElementById('graph');
      const data = {nodes, edges};
      const options = {physics:{stabilization:false}};
      new vis.Network(container, data, options);
    } else {
      // fallback: show JSON
      const container = document.getElementById('graph');
      container.textContent = JSON.stringify(j.graph, null, 2);
    }
  };
};
