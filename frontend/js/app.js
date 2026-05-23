document.addEventListener('DOMContentLoaded', () => {
  const pages = Array.from(document.querySelectorAll('.page[data-page]'));
  const sidebar = document.getElementById('sidebar');
  const sidebarNavButtons = Array.from(document.querySelectorAll('.sidebar-nav .sb-item[data-route]'));
  const routeTriggers = Array.from(document.querySelectorAll('[data-route]'));

  const assistantRoot = document.getElementById('assistant-root');
  const exercisesRoot = document.getElementById('exercises-root');
  const forumRoot = document.getElementById('forum-root');
  const analyticsRoot = document.getElementById('analytics-root');
  const kgContainer = document.getElementById('kg-graph');
  const kgHint = document.getElementById('kg-hint');

  const loaded = {
    assistant: false,
    exercises: false,
    knowledgeGraph: false,
    forum: false,
    analytics: false,
  };

  function setActiveNav(route) {
    sidebarNavButtons.forEach((btn) => {
      btn.classList.toggle('is-active', btn.dataset.route === route);
    });
  }

  function showPage(route) {
    pages.forEach((p) => {
      p.classList.toggle('hidden', p.dataset.page !== route);
    });
  }

  async function loadModuleInto(container, moduleFile) {
    const res = await fetch('/static/' + moduleFile);
    const html = await res.text();
    container.innerHTML = html;
  }

  async function ensureAssistantLoaded() {
    if (loaded.assistant) return;
    if (!assistantRoot) return;
    await loadModuleInto(assistantRoot, 'qa_module.html');
    loaded.assistant = true;
    if (window.initQA) window.initQA();
  }

  async function ensureExercisesLoaded() {
    if (loaded.exercises) return;
    if (!exercisesRoot) return;
    await loadModuleInto(exercisesRoot, 'quiz_module.html');
    loaded.exercises = true;
    if (window.initQuiz) window.initQuiz();
  }

  async function ensureForumLoaded() {
    if (loaded.forum) return;
    if (!forumRoot) return;
    await loadModuleInto(forumRoot, 'forum_module.html');
    loaded.forum = true;
    if (window.initForum) window.initForum();
  }

  async function ensureAnalyticsLoaded() {
    if (loaded.analytics) return;
    if (!analyticsRoot) return;
    loaded.analytics = true;
    if (window.initAnalytics) window.initAnalytics();
  }

  async function ensureKnowledgeGraphLoaded() {
    if (loaded.knowledgeGraph) return;
    if (!kgContainer) return;

    // 添加图谱选择器按钮事件监听
    const kgButtons = document.querySelectorAll('.kg-selector-btn');
    kgButtons.forEach(btn => {
      btn.addEventListener('click', async () => {
        // 移除所有按钮的选中状态
        kgButtons.forEach(b => b.classList.remove('is-active'));
        // 设置当前按钮为选中状态
        btn.classList.add('is-active');

        // 加载图谱（目前所有按钮都加载相同的图谱）
        await loadKnowledgeGraph();
      });
    });

    loaded.knowledgeGraph = true;
  }

  async function loadKnowledgeGraph() {
    if (!kgContainer) return;

    try {
      const res = await fetch('/api/graph');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const graph = await res.json();
      const entities = graph.entities || [];
      const relations = graph.relations || [];

      if (!window.vis) {
        kgContainer.textContent = JSON.stringify(graph, null, 2);
        if (kgHint) kgHint.textContent = '未检测到 vis-network，已降级为 JSON 展示。';
        return;
      }

      const nodes = new vis.DataSet(
        entities.map((e) => ({
          id: e.id,
          label: e.name,
          color: e.color,
          size: e.size || 22,
          title: e.description || e.name,
        }))
      );
      const edges = new vis.DataSet(
        relations.map((r) => ({
          from: r.source,
          to: r.target,
          label: r.type || r.label || '',
          arrows: 'to',
          width: 2,
          font: { align: 'middle' },
        }))
      );

      const data = { nodes, edges };
      const options = {
        physics: { stabilization: true },
        interaction: { hover: true },
      };

      // 清空容器并渲染图谱
      kgContainer.innerHTML = '';
      kgContainer.classList.remove('flex', 'items-center', 'justify-center', 'text-slate-400');
      new vis.Network(kgContainer, data, options);
      if (kgHint) kgHint.textContent = `已加载：${entities.length} 个实体，${relations.length} 条关系。`;
    } catch (e) {
      kgContainer.innerHTML = `<div class="notice notice-danger">知识图谱加载失败：${String(e.message || e)}</div>`;
      if (kgHint) kgHint.textContent = '提示：需要后端提供 /api/graph 接口返回完整图谱。';
    }
  }

  async function routeTo(route) {
    showPage(route);
    setActiveNav(route);

    if (route === 'home') {
      document.body.classList.add('is-home');
    } else {
      document.body.classList.remove('is-home');
    }

    if (route === 'assistant') await ensureAssistantLoaded();
    if (route === 'exercises') await ensureExercisesLoaded();
    if (route === 'knowledge-graph') await ensureKnowledgeGraphLoaded();
    if (route === 'forum') await ensureForumLoaded();
    if (route === 'analytics') await ensureAnalyticsLoaded();
  }

  routeTriggers.forEach((el) => {
    el.addEventListener('click', (ev) => {
      const route = el.dataset.route;
      if (!route) return;
      ev.preventDefault();

      routeTo(route);
    });
  });

  // 意见反馈弹窗
  const feedbackBtn = document.getElementById('feedback-btn');
  const feedbackModal = document.getElementById('feedback-modal');
  const feedbackClose = document.getElementById('feedback-close');
  const feedbackCancel = document.getElementById('feedback-cancel');
  const feedbackSubmit = document.getElementById('feedback-submit');

  function openFeedback() {
    feedbackModal.classList.remove('hidden');
    setTimeout(() => feedbackModal.classList.add('is-open'), 10);
  }

  function closeFeedback() {
    feedbackModal.classList.remove('is-open');
    setTimeout(() => feedbackModal.classList.add('hidden'), 200);
  }

  if (feedbackBtn) feedbackBtn.addEventListener('click', openFeedback);
  if (feedbackClose) feedbackClose.addEventListener('click', closeFeedback);
  if (feedbackCancel) feedbackCancel.addEventListener('click', closeFeedback);
  if (feedbackSubmit) {
    feedbackSubmit.addEventListener('click', () => {
      const input = document.getElementById('feedback-input');
      if (input && input.value.trim()) {
        input.value = '';
        closeFeedback();
      }
    });
  }
  if (feedbackModal) {
    feedbackModal.querySelector('.feedback-modal-overlay').addEventListener('click', closeFeedback);
  }

  // 默认进入首页
  routeTo('home');
});
