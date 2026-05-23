// 班级学情分析模块
window.initAnalytics = async function() {
  const root = document.getElementById('analytics-root');

  // 模拟学情数据
  const mockData = {
    kpi: {
      activeRate: 87,
      avgQuestions: 12.3,
      homeworkRate: 78,
      forumResponseTime: 2.4
    },
    knowledgeBlindSpots: [
      { name: 'SPARQL属性路径', score: 52, count: 23 },
      { name: 'OWL约束推理', score: 58, count: 19 },
      { name: '本体对齐算法', score: 61, count: 17 },
      { name: 'TransE损失函数', score: 65, count: 15 },
      { name: '知识融合策略', score: 68, count: 14 },
      { name: 'RDF Schema语义', score: 70, count: 13 },
      { name: '实体链接消歧', score: 72, count: 12 },
      { name: 'SPARQL FILTER子句', score: 74, count: 11 },
      { name: '本体推理规则', score: 75, count: 10 },
      { name: '知识图谱嵌入', score: 77, count: 9 },
      { name: 'Levenshtein距离', score: 78, count: 8 },
      { name: 'Jaccard相似度', score: 80, count: 7 }
    ],
    knowledgeHotSpots: [
      { name: 'RDF三元组', views: 78, label: 'RDF数据模型' },
      { name: '实体消歧方法', views: 71, label: '知识抽取' },
      { name: 'DBpedia构建', views: 64, label: '开放知识图谱' },
      { name: 'TransE算法', views: 58, label: '知识表示学习' },
      { name: 'SPARQL基础查询', views: 49, label: 'SPARQL查询' }
    ],
    weeklyTrend: [
      { week: '第1周', usage: 3.2, score: 65 },
      { week: '第2周', usage: 4.8, score: 68 },
      { week: '第3周', usage: 6.5, score: 72 },
      { week: '第4周', usage: 8.2, score: 75 },
      { week: '第5周', usage: 9.8, score: 78 },
      { week: '第6周', usage: 11.5, score: 82 },
      { week: '第7周', usage: 12.3, score: 85 }
    ],
    errorCategories: [
      { category: '概念理解模糊', count: 45, percentage: 38 },
      { category: 'SPARQL语法错误', count: 32, percentage: 27 },
      { category: '算法计算错误', count: 28, percentage: 23 },
      { category: '逻辑推理不足', count: 14, percentage: 12 }
    ],
    intentDistribution: [
      { intent: '概念解释', percentage: 40, color: '#93c5fd' },
      { intent: '代码Debug', percentage: 35, color: '#86efac' },
      { intent: '作业确认', percentage: 15, color: '#fcd34d' },
      { intent: '扩展延伸', percentage: 10, color: '#c4b5fd' }
    ],
    forumKeywords: [
      { word: 'SPARQL', size: 48 },
      { word: 'FILTER', size: 42 },
      { word: 'OPTIONAL', size: 38 },
      { word: '知识抽取', size: 36 },
      { word: 'margin', size: 34 },
      { word: '实体对齐', size: 32 },
      { word: 'TransE', size: 30 },
      { word: 'OWL', size: 28 },
      { word: '本体推理', size: 26 },
      { word: 'DBpedia', size: 24 },
      { word: 'RDF', size: 22 },
      { word: '三元组', size: 20 }
    ]
  };

  // 渲染页面结构
  root.innerHTML = `
    <!-- 核心学情大盘 KPI -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="kpi-card kpi-card-blue">
        <div class="kpi-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="kpi-content">
          <div class="kpi-label">活跃度</div>
          <div class="kpi-value">${mockData.kpi.activeRate}%</div>
          <div class="kpi-desc">周均活跃率</div>
        </div>
      </div>

      <div class="kpi-card kpi-card-green">
        <div class="kpi-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            <path d="M8 10h.01M12 10h.01M16 10h.01"/>
          </svg>
        </div>
        <div class="kpi-content">
          <div class="kpi-label">互动频次</div>
          <div class="kpi-value">${mockData.kpi.avgQuestions}</div>
          <div class="kpi-desc">人均提问次数/周</div>
        </div>
      </div>

      <div class="kpi-card kpi-card-amber">
        <div class="kpi-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="9" y1="15" x2="15" y2="15"/>
          </svg>
        </div>
        <div class="kpi-content">
          <div class="kpi-label">作业进度</div>
          <div class="kpi-value">${mockData.kpi.homeworkRate}%</div>
          <div class="kpi-desc">当前批次提交率</div>
        </div>
      </div>

      <div class="kpi-card kpi-card-purple">
        <div class="kpi-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="kpi-content">
          <div class="kpi-label">答疑效率</div>
          <div class="kpi-value">${mockData.kpi.forumResponseTime}h</div>
          <div class="kpi-desc">平均响应时长</div>
        </div>
      </div>
    </div>

    <!-- 知识图谱盲区热力图 + 高频检索 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- 知识盲区排行 -->
      <div class="card p-6">
        <div class="section-title mb-4">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M12 9v4m0 4h.01M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/>
          </svg>
          知识盲区排行
        </div>
        <div class="subtle mb-4">基于习题评判反馈，统计得分率最低的知识点</div>
        <div id="blind-spots-chart" class="chart-container"></div>
      </div>

      <!-- 高频检索知识点 -->
      <div class="card p-6">
        <div class="section-title mb-4">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
          </svg>
          高频检索知识点 Top 5
        </div>
        <div class="subtle mb-4">图谱节点被查看次数最多的知识点</div>
        <div id="hot-spots-list" class="space-y-3"></div>
      </div>
    </div>

    <!-- 错题原因分析 + 提问意图分布 + 论坛热点词云 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- 错题原因维度 -->
      <div class="card p-6">
        <div class="section-title mb-4">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          错题原因维度分析
        </div>
        <div class="subtle mb-4">帮助识别学生卡在理论理解还是工程实践</div>
        <div id="error-chart" class="chart-container"></div>
      </div>

      <!-- 提问意图分类 -->
      <div class="card p-6">
        <div class="section-title mb-4">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          学生提问意图分类
        </div>
        <div class="subtle mb-4">AI助手交互文本的意图分布</div>
        <div id="intent-chart" class="chart-container"></div>
      </div>

      <!-- 论坛热点词云 -->
      <div class="card p-6">
        <div class="section-title mb-4">
          <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          论坛高频关键词
        </div>
        <div class="subtle mb-4">近一周论坛讨论的热点话题</div>
        <div id="word-cloud" class="word-cloud-container"></div>
      </div>
    </div>
  `;

  // 渲染知识盲区柱状图
  renderBlindSpotsChart(mockData.knowledgeBlindSpots);

  // 渲染高频检索列表
  renderHotSpotsList(mockData.knowledgeHotSpots);

  // 渲染错题原因堆叠图
  renderErrorChart(mockData.errorCategories);

  // 渲染提问意图饼图
  renderIntentChart(mockData.intentDistribution);

  // 渲染词云
  renderWordCloud(mockData.forumKeywords);
};

// 知识盲区柱状图
function renderBlindSpotsChart(data) {
  const container = document.getElementById('blind-spots-chart');
  const maxCount = Math.max(...data.map(d => d.count));

  container.innerHTML = data.map(item => `
    <div class="blind-spot-item">
      <div class="blind-spot-header">
        <span class="blind-spot-name">${item.name}</span>
        <span class="blind-spot-score">${item.score}分</span>
      </div>
      <div class="blind-spot-bar-bg">
        <div class="blind-spot-bar" style="width: ${(item.count / maxCount) * 100}%">
          <span class="blind-spot-count">${item.count}人错误</span>
        </div>
      </div>
    </div>
  `).join('');
}

// 高频检索列表
function renderHotSpotsList(data) {
  const container = document.getElementById('hot-spots-list');
  const maxViews = Math.max(...data.map(d => d.views));

  container.innerHTML = data.map((item, index) => `
    <div class="hot-spot-item">
      <div class="hot-spot-rank">${index + 1}</div>
      <div class="hot-spot-content">
        <div class="hot-spot-header">
          <span class="hot-spot-name">${item.name}</span>
          <span class="hot-spot-views">${item.views} 次</span>
        </div>
        <div class="hot-spot-label">${item.label}</div>
        <div class="hot-spot-bar-bg">
          <div class="hot-spot-bar" style="width: ${(item.views / maxViews) * 100}%"></div>
        </div>
      </div>
    </div>
  `).join('');
}

// 学习趋势双轴图（简化版SVG实现）
function renderTrendChart(data) {
  const container = document.getElementById('trend-chart');
  const width = 800;
  const height = 300;
  const padding = { top: 20, right: 60, bottom: 40, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const maxUsage = Math.max(...data.map(d => d.usage));
  const maxScore = Math.max(...data.map(d => d.score));
  const minScore = Math.min(...data.map(d => d.score));

  const xStep = chartWidth / (data.length - 1);

  // 生成折线路径
  const usagePath = data.map((d, i) => {
    const x = padding.left + i * xStep;
    const y = padding.top + chartHeight - (d.usage / maxUsage) * chartHeight;
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');

  const scorePath = data.map((d, i) => {
    const x = padding.left + i * xStep;
    const y = padding.top + chartHeight - ((d.score - minScore) / (maxScore - minScore)) * chartHeight;
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ');

  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" class="trend-svg">
      <!-- 网格线 -->
      ${[0, 1, 2, 3, 4].map(i => {
        const y = padding.top + (chartHeight / 4) * i;
        return `<line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="#e2e8f0" stroke-width="1"/>`;
      }).join('')}

      <!-- 柱状图（使用时长） -->
      ${data.map((d, i) => {
        const x = padding.left + i * xStep - 15;
        const barHeight = (d.usage / maxUsage) * chartHeight;
        const y = padding.top + chartHeight - barHeight;
        return `<rect x="${x}" y="${y}" width="30" height="${barHeight}" fill="#93c5fd" opacity="0.6" rx="4"/>`;
      }).join('')}

      <!-- 折线（平均分） -->
      <path d="${scorePath}" fill="none" stroke="#d97706" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>

      <!-- 数据点 -->
      ${data.map((d, i) => {
        const x = padding.left + i * xStep;
        const y = padding.top + chartHeight - ((d.score - minScore) / (maxScore - minScore)) * chartHeight;
        return `<circle cx="${x}" cy="${y}" r="5" fill="#d97706" stroke="#fff" stroke-width="2"/>`;
      }).join('')}

      <!-- X轴标签 -->
      ${data.map((d, i) => {
        const x = padding.left + i * xStep;
        return `<text x="${x}" y="${height - 10}" text-anchor="middle" font-size="12" fill="#64748b">${d.week}</text>`;
      }).join('')}

      <!-- Y轴标签（左侧：使用时长） -->
      <text x="10" y="15" font-size="12" fill="#64748b" font-weight="600">使用时长(h)</text>

      <!-- Y轴标签（右侧：平均分） -->
      <text x="${width - 50}" y="15" font-size="12" fill="#d97706" font-weight="600">平均分</text>

      <!-- 图例 -->
      <rect x="${padding.left}" y="5" width="20" height="12" fill="#93c5fd" opacity="0.6" rx="2"/>
      <text x="${padding.left + 25}" y="15" font-size="12" fill="#64748b">周均使用时长</text>

      <line x1="${padding.left + 120}" y1="11" x2="${padding.left + 140}" y2="11" stroke="#d97706" stroke-width="3"/>
      <text x="${padding.left + 145}" y="15" font-size="12" fill="#64748b">班级平均分</text>
    </svg>
  `;
}

// 错题原因堆叠图
function renderErrorChart(data) {
  const container = document.getElementById('error-chart');
  const total = data.reduce((sum, d) => sum + d.count, 0);

  const colors = ['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6'];

  container.innerHTML = `
    <div class="error-bars">
      ${data.map((item, index) => `
        <div class="error-bar-item">
          <div class="error-bar-label">
            <span class="error-dot" style="background: ${colors[index]}"></span>
            <span>${item.category}</span>
          </div>
          <div class="error-bar-bg">
            <div class="error-bar" style="width: ${item.percentage}%; background: ${colors[index]}">
              <span class="error-bar-text">${item.count}次 (${item.percentage}%)</span>
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

// 提问意图饼图（简化为环形进度条）
function renderIntentChart(data) {
  const container = document.getElementById('intent-chart');

  container.innerHTML = `
    <div class="intent-rings">
      ${data.map(item => `
        <div class="intent-ring-item">
          <div class="intent-ring-wrapper">
            <svg viewBox="0 0 100 100" class="intent-ring-svg">
              <circle cx="50" cy="50" r="40" fill="none" stroke="#e2e8f0" stroke-width="12"/>
              <circle cx="50" cy="50" r="40" fill="none" stroke="${item.color}" stroke-width="12"
                stroke-dasharray="${item.percentage * 2.51} 251.2"
                stroke-dashoffset="0"
                transform="rotate(-90 50 50)"/>
            </svg>
            <div class="intent-ring-label">${item.percentage}%</div>
          </div>
          <div class="intent-ring-name">${item.intent}</div>
        </div>
      `).join('')}
    </div>
  `;
}

// 词云渲染（纵横交错布局）
function renderWordCloud(data) {
  const container = document.getElementById('word-cloud');

  // 将词语分成多行，实现纵横交错的效果
  const rows = [
    data.slice(0, 3),   // 第一行：3个词
    data.slice(3, 7),   // 第二行：4个词
    data.slice(7, 10),  // 第三行：3个词
    data.slice(10)      // 第四行：剩余的词
  ];

  const colors = ['#065f46', '#0ea5e9', '#d97706', '#7c3aed', '#059669'];

  const rowsHTML = rows.map((row, rowIndex) => {
    const words = row.map((item, index) => {
      const color = colors[(rowIndex * 3 + index) % colors.length];
      return `<span class="word-cloud-item" style="font-size: ${item.size}px; color: ${color}">${item.word}</span>`;
    }).join('');
    return `<div class="word-cloud-row">${words}</div>`;
  }).join('');

  container.innerHTML = rowsHTML;
}
