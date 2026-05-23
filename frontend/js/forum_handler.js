const MOCK_POSTS = [
  {
    id: 6,
    user: '图灵的猫',
    avatar: '图',
    avatarColor: '#be185d',
    time: '2026-05-08 22:41',
    content: 'SPARQL 查询里 OPTIONAL 和 FILTER 的执行顺序有点困惑，有时候 FILTER 放在 OPTIONAL 里面和外面结果不一样，这是为什么？',
    likes: 3,
  },
  {
    id: 5,
    user: 'KG_Explorer',
    avatar: 'K',
    avatarColor: '#0891b2',
    time: '2026-05-07 19:22',
    content: '分享一个学习资源：斯坦福 CS520 Knowledge Graphs 课程的讲义在网上可以找到，里面对知识图谱的构建流程讲得很系统，和我们课程内容互补，推荐大家参考。',
    likes: 15,
  },
  {
    id: 4,
    user: '助教-liu',
    avatar: '助',
    avatarColor: '#7c3aed',
    time: '2026-05-06 10:40',
    content: '关于 TransE 的 margin 参数：一般建议从 1~5 之间调参，具体取值取决于数据集的规模和实体/关系的数量。对于小规模数据集，margin=1 通常已经足够；大规模数据集可以适当增大。建议结合验证集上的 MRR 指标来选择最优值。',
    likes: 20,
    isTA: true,
  },
  {
    id: 3,
    user: '王森',
    avatar: '王',
    avatarColor: '#1d4ed8',
    time: '2026-05-06 09:15',
    content: '关于知识图谱补全的作业，TransE 模型的损失函数里正负样本的 margin 参数怎么选比较合适？我试了 margin=1 和 margin=5，效果差别挺大的。',
    likes: 5,
  },
  {
    id: 2,
    user: 'ontology',
    avatar: 'O',
    avatarColor: '#b45309',
    time: '2026-05-05 15:10',
    content: 'RDF 只能表示简单的三元组（主语-谓语-宾语），而 OWL 在 RDF 基础上增加了类的层次关系、属性约束、基数限制等，表达能力更强，可以支持自动推理。简单来说，RDF 是数据模型，OWL 是本体语言。',
    likes: 8,
  },
  {
    id: 1,
    user: '李同学',
    avatar: '李',
    avatarColor: '#065f46',
    time: '2026-05-05 14:32',
    content: '请问 OWL 和 RDF 的主要区别是什么？课上讲到 OWL 是基于描述逻辑的，但我对两者的表达能力差异还不太清楚，有同学能解释一下吗？',
    likes: 12,
  },
];

window.initForum = function () {
  const postsContainer = document.getElementById('forum-posts');
  if (!postsContainer) return;

  postsContainer.innerHTML = MOCK_POSTS.map(post => `
    <div class="forum-post">
      <div class="forum-post-header">
        <div class="forum-avatar" style="background:${post.avatarColor}">${post.avatar}</div>
        <div class="forum-post-meta">
          <span class="forum-username${post.isTA ? ' forum-ta' : ''}">${post.user}${post.isTA ? ' <span class="forum-ta-badge">助教</span>' : ''}</span>
          <span class="forum-time">${post.time}</span>
        </div>
        <div class="forum-likes">
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
          <span>${post.likes}</span>
        </div>
      </div>
      <div class="forum-post-body">${post.content}</div>
    </div>
  `).join('');

  const submitBtn = document.getElementById('forum-submit');
  const input = document.getElementById('forum-input');
  if (submitBtn && input) {
    submitBtn.addEventListener('click', () => {
      const text = input.value.trim();
      if (!text) return;
      const newPost = {
        id: Date.now(),
        user: '我',
        avatar: '我',
        avatarColor: '#065f46',
        time: new Date().toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-'),
        content: text,
        likes: 0,
      };
      MOCK_POSTS.unshift(newPost);
      input.value = '';
      window.initForum();
    });
  }
};
