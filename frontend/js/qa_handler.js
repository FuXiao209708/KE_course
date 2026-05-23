window.initQA = async function() {
  const demoQs = [
    {
      question: '请解释语义网络中的三元组结构及其在知识图谱中的作用',
      keywords: ['语义网络', '三元组', '知识图谱'],
      isDemo: true,
      demoData: {
        reply: '语义网络是知识图谱的重要组成部分，它通过节点和弧来表示概念及其关系。语义网络的基本单元是三元组，其结构为（节点1，联想弧，节点2），这种表示方式也被称为主语-谓语-宾语或头实体-关系-尾实体的形式。\n\n在知识图谱中，三元组是最基础的知识表示单元。每个三元组描述了两个实体之间的一种语义关系，例如（知识图谱，包含，语义网络）表示知识图谱包含语义网络这一概念。通过大量三元组的组合，我们可以构建出复杂的知识网络，支持知识推理、问答系统等多种应用。\n\n值得注意的是，三元组不仅存在于抽象的语义网络中，在RDF图等具体实现中也采用了RDF三元组的形式，这使得知识的存储、查询和推理都有了统一的基础。',
        graph: {
          entities: [
            {id: 'e003', name: '知识图谱', color: '#93c5fd', size: 42},
            {id: 'e004', name: '语义网络', color: '#86efac', size: 36},
            {id: 'e005', name: '三元组', color: '#86efac', size: 32},
            {id: 'e021', name: '节点1', color: '#86efac', size: 24},
            {id: 'e022', name: '联想弧', color: '#86efac', size: 24},
            {id: 'e023', name: '节点2', color: '#cbd5e1', size: 24},
            {id: 'e016', name: '节点', color: '#93c5fd', size: 28},
            {id: 'e017', name: '弧', color: '#86efac', size: 28}
          ],
          relations: [
            {source: 'e003', target: 'e004', label: '包含'},
            {source: 'e003', target: 'e005', label: '包含'},
            {source: 'e004', target: 'e005', label: '由组成'},
            {source: 'e004', target: 'e016', label: '由组成'},
            {source: 'e004', target: 'e017', label: '由组成'},
            {source: 'e005', target: 'e021', label: '由组成'},
            {source: 'e005', target: 'e022', label: '由组成'},
            {source: 'e005', target: 'e023', label: '由组成'}
          ]
        },
        source: {
          chapter: '第1章 知识图谱概述 & 第2章 知识表示',
          excerpt: '【教材原文】图1-1知识图谱：事物关系的可计算模型。知识图谱并非突然出现的新技术，而是历史上很多相关技术相互影响和继承发展的结果，包括语义网络、知识表示、本体论、Semantic Web、自然语言处理等，有着来自人工智能和自然语言处理等多方面的技术基因。\n\n【教材原文】语义网络的单元是三元组：（节点1，联想弧，节点2）。'
        }
      }
    },
    {
      question: 'RDF图和SPARQL查询语言是什么关系？它们在知识图谱中如何协同工作？',
      keywords: ['RDF', 'SPARQL', '查询语言'],
      isDemo: true,
      demoData: {
        reply: 'RDF图（Resource Description Framework Graph）是知识图谱的主要数据模型之一，它采用RDF三元组作为基本存储单元，将知识表示为主语-谓语-宾语的形式。RDF图为知识的结构化存储提供了标准化的框架。\n\nSPARQL是专门为RDF图设计的声明式查询语言，是RDF图上的标准查询工具。SPARQL支持多种查询形式，包括SELECT（选择查询）、ASK（布尔查询）、CONSTRUCT（构造查询）和DESCRIBE（描述查询），还支持图匹配等高级功能。\n\n两者的协同工作体现在：RDF图负责知识的存储和组织，而SPARQL提供了强大的查询能力，使用户能够从RDF图中检索所需的知识。这种组合在图数据库中得到了广泛实现，支撑了语义网、知识问答等众多应用场景。与之对应的是，属性图通常使用Cypher或Gremlin作为查询语言。',
        graph: {
          entities: [
            {id: 'e003', name: '知识图谱', color: '#93c5fd', size: 42},
            {id: 'e006', name: 'RDF图', color: '#86efac', size: 36},
            {id: 'e030', name: 'RDF三元组', color: '#86efac', size: 28},
            {id: 'e008', name: 'SPARQL', color: '#fcd34d', size: 32},
            {id: 'e032', name: '查询语言', color: '#86efac', size: 28},
            {id: 'e033', name: 'SELECT', color: '#cbd5e1', size: 24},
            {id: 'e034', name: 'ASK', color: '#fcd34d', size: 24},
            {id: 'e035', name: 'CONSTRUCT', color: '#fcd34d', size: 24},
            {id: 'e036', name: 'DESCRIBE', color: '#fcd34d', size: 24},
            {id: 'e037', name: '图匹配', color: '#cbd5e1', size: 24},
            {id: 'e038', name: '图数据库', color: '#fcd34d', size: 30}
          ],
          relations: [
            {source: 'e003', target: 'e006', label: '包含'},
            {source: 'e006', target: 'e030', label: '由组成'},
            {source: 'e006', target: 'e008', label: '包含'},
            {source: 'e008', target: 'e006', label: '查询'},
            {source: 'e008', target: 'e032', label: '实例'},
            {source: 'e008', target: 'e033', label: '包含'},
            {source: 'e008', target: 'e034', label: '包含'},
            {source: 'e008', target: 'e035', label: '包含'},
            {source: 'e008', target: 'e036', label: '包含'},
            {source: 'e008', target: 'e037', label: '包含'},
            {source: 'e008', target: 'e038', label: '实现'}
          ]
        },
        source: {
          chapter: '第1章 知识图谱概述 & 第3章 知识存储',
          excerpt: '【教材原文】知识图谱的主要数据模型有RDF图（RDF_graph）和属性图（Property_Graph）两种；知识图谱查询语言可分为声明式（Declarative）和导航式（Navigational）两类。\n\n【教材原文】目前，RDF图上的查询语言是SPARQL；属性图上的查询语言常用的是Cypher和Gremlin。'
        }
      }
    },
    {
      question: '请推荐知识图谱方向的学习路线规划',
      keywords: ['研究生', '学习路线']
    }
  ];

  const demoContainer = document.getElementById('demo-questions');
  demoContainer.innerHTML = demoQs.map(q => `<button type="button" class="demo-q qa-chip" data-kw="${q.keywords.join(',')}">${q.question}</button>`).join('');

  document.querySelectorAll('.demo-q').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const txt = document.getElementById('qa-input');
      txt.value = btn.textContent;
      txt.dataset.keywords = btn.dataset.kw;
      // 查找对应的demo数据
      const q = demoQs.find(dq => dq.question === btn.textContent);
      if (q && q.isDemo) {
        txt.dataset.demoData = JSON.stringify(q.demoData);
      } else {
        delete txt.dataset.demoData;
      }
    });
  });

  const sendBtn = document.getElementById('qa-send');
  const input = document.getElementById('qa-input');
  const chatWindow = document.getElementById('chat-window');
  const sourceChapter = document.getElementById('source-chapter');
  const sourceExcerpt = document.getElementById('source-excerpt');

  const defaultRobotSvg = `
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
      <rect x="4" y="7" width="16" height="10" rx="3" />
      <path d="M9 7V5a3 3 0 0 1 6 0v2" />
      <path d="M8 17v2" />
      <path d="M16 17v2" />
      <circle cx="9.5" cy="12" r="1" />
      <circle cx="14.5" cy="12" r="1" />
    </svg>
  `;

  function addMessage(role, text, options = {}){
    const el = document.createElement('div');
    el.className = `qa-msg ${role === 'user' ? 'qa-msg-user' : 'qa-msg-ai'}`;
    const bubbleClass = role === 'user' ? 'qa-bubble qa-bubble-user' : 'qa-bubble qa-bubble-ai';
    const avatarHtml = role === 'user'
      ? `<img class="qa-avatar" src="/assets/user_avatar.png" alt="用户头像" />`
      : `<div class="qa-avatar qa-avatar-ai">${options.avatarSvg || defaultRobotSvg}</div>`;
    const tags = (options.tags || []).map(t => `<span class="qa-tag">${t}</span>`).join('');
    const tagHtml = tags ? `<div class="qa-tags">${tags}</div>` : '';
    const bodyHtml = `<div class="qa-msg-body">${tagHtml}<div class="${bubbleClass}" id="${options.bubbleId || ''}">${text}</div></div>`;
    el.innerHTML = role === 'user' ? `${bodyHtml}${avatarHtml}` : `${avatarHtml}${bodyHtml}`;
    chatWindow.appendChild(el);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return el;
  }

  // 流式输出：逐字符/词渲染，模拟模型生成
  async function streamText(bubbleEl, fullText) {
    bubbleEl.textContent = '';
    // 按词（2~4字符）分块，模拟流式
    const chunks = [];
    let i = 0;
    while (i < fullText.length) {
      const len = Math.floor(Math.random() * 3) + 1;
      chunks.push(fullText.slice(i, i + len));
      i += len;
    }
    for (const chunk of chunks) {
      await new Promise(r => setTimeout(r, 28 + Math.random() * 30));
      bubbleEl.textContent += chunk;
      chatWindow.scrollTop = chatWindow.scrollHeight;
    }
  }

  function seedInitialConversation(){
    addMessage('user', '你好，可以帮我做什么？');
    addMessage('assistant', '你好！我是您的知识工程课程智能导学助手。我基于本课程的核心知识图谱构建，能够为您解析核心概念、指引学习路线，并实时追踪您的学术反馈。您可以直接在下方输入框开始提问。', {
      tags: ['模型状态：良好', '知识库连接：正常', '检索引擎: GraphRAG'],
    });
    // 标记初始对话已显示状态标签
    window.qaStatusTagsShown = true;
  }

  sendBtn.onclick = async ()=>{
    const question = input.value.trim();
    if (!question) return;
    const keywords = (input.dataset.keywords || '').split(',').filter(Boolean);
    const demoDataStr = input.dataset.demoData;
    input.value = '';
    input.dataset.keywords = '';
    delete input.dataset.demoData;

    addMessage('user', question);

    // 检查是否是无关问题
    if (question.includes('天气') || question.includes('今天') && question.includes('如何')) {
      const loadingEl = addMessage('assistant', `<span class='dot-flash'><span></span><span></span><span></span></span> 正在思考...`);
      await new Promise(r => setTimeout(r, 600));
      chatWindow.removeChild(loadingEl);
      const bubbleId = 'bubble-' + Date.now();
      addMessage('assistant', '', { bubbleId });
      const bubbleEl = document.getElementById(bubbleId);
      if (bubbleEl) {
        await streamText(bubbleEl, '抱歉，我是知识工程课程的智能导学助手，专注于为您解答课程相关的问题。您可以询问关于知识图谱、本体、描述逻辑、RDF、SPARQL等课程核心概念，或者咨询学习路线规划、平台功能使用等问题。请尝试提出与课程内容或平台使用相关的问题，我会竭诚为您解答。');
      }
      return;
    }

    // 如果是demo问题，直接使用预设数据
    if (demoDataStr) {
      const demoData = JSON.parse(demoDataStr);

      // 加载占位气泡
      const loadingEl = addMessage('assistant', `<span class='dot-flash'><span></span><span></span><span></span></span> 正在思考...`);

      // 模拟延迟
      await new Promise(r => setTimeout(r, 800));

      // 移除加载气泡，创建流式气泡（不显示状态标签）
      chatWindow.removeChild(loadingEl);
      const bubbleId = 'bubble-' + Date.now();
      addMessage('assistant', '', { bubbleId });
      const bubbleEl = document.getElementById(bubbleId);
      if (bubbleEl) {
        await streamText(bubbleEl, demoData.reply);
      }

      // 渲染右侧知识图谱
      if(window.vis && demoData.graph){
        const nodes = new vis.DataSet(demoData.graph.entities.map(e=>({id:e.id,label:e.name,color:e.color,size:e.size})));
        const edges = new vis.DataSet(demoData.graph.relations.map(r=>({from:r.source,to:r.target,label:r.label, width:2})));
        const container = document.getElementById('graph');
        new vis.Network(container, {nodes, edges}, {physics:{stabilization:false}});
      }

      // 渲染知识溯源
      if (demoData.source) {
        if (sourceChapter) sourceChapter.textContent = demoData.source.chapter;
        if (sourceExcerpt) sourceExcerpt.textContent = demoData.source.excerpt;
      }

      return;
    }

    // 非demo问题，走原有API流程
    // 加载占位气泡
    const loadingEl = addMessage('assistant', `<span class='dot-flash'><span></span><span></span><span></span></span> 正在思考...`);

    const resp = await fetch('/api/qa', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({question, keywords})});
    const j = await resp.json();

    // 移除加载气泡，创建流式气泡（不显示状态标签）
    chatWindow.removeChild(loadingEl);
    const bubbleId = 'bubble-' + Date.now();
    addMessage('assistant', '', { bubbleId });
    const bubbleEl = document.getElementById(bubbleId);
    if (bubbleEl) {
      await streamText(bubbleEl, j.reply);
    }

    // 渲染右侧小图谱
    if(window.vis){
      const nodes = new vis.DataSet(j.graph.entities.map(e=>({id:e.id,label:e.name,color:e.color,size:e.size})));
      const edges = new vis.DataSet(j.graph.relations.map(r=>({from:r.source,to:r.target,label:r.label, width:2})));
      const container = document.getElementById('graph');
      new vis.Network(container, {nodes, edges}, {physics:{stabilization:false}});
    }
  };

  const mockSource = {
    source_chapter: '第三章 描述逻辑形式化体系',
    excerpt_content: '这里是对应的教材原文出处占位文本。系统后续接入真实接口后，此处将自动渲染与当前图谱节点匹配的教材段落、核心定理或文献摘要。'
  };
  if (sourceChapter) sourceChapter.textContent = mockSource.source_chapter;
  if (sourceExcerpt) sourceExcerpt.textContent = mockSource.excerpt_content;

  seedInitialConversation();
};
