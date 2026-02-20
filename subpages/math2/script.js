document.addEventListener('DOMContentLoaded', () => {
    const studyPlan = [
        // Week 1: 函数、极限、连续 & 一元函数微分学
        { 
            day: 1, 
            title: '函数、极限与连续', 
            topics: ['函数的概念与性质', '极限的计算', '函数的连续性'],
            resources: [
                { title: '知乎专栏：考研数学-函数概念与性质梳理', url: 'https://zhuanlan.zhihu.com/p/91333551' },
                { title: '勤学365：极限的计算方法总结', url: 'https://www.qinxue365.com/gaoshu/2613.html' },
                { title: '知乎专栏：函数连续与间断点，这一篇就够了！', url: 'https://zhuanlan.zhihu.com/p/359994801' },
                { title: 'Bilibili视频：极限的概念与求法', url: 'https://www.bilibili.com/video/BV1GJ411x7h1' }
            ]
        },
        { day: 2, title: '导数与微分', topics: ['导数的定义与几何意义', '基本求导公式与法则', '高阶导数'] },
        { day: 3, title: '微分中值定理与导数应用(一)', topics: ['罗尔、拉格朗日、柯西中值定理', '洛必达法则'] },
        { day: 4, title: '导数应用(二)', topics: ['函数单调性与凹凸性', '函数极值与最值'] },
        { day: 5, title: '导数应用(三)', topics: ['函数图形的描绘', '曲率与曲率半径'] },
        { day: 6, title: '第一周复习与总结', topics: ['复习本周所有内容', '完成配套练习题'] },
        { day: 7, title: '休息或查漏补缺', topics: ['自由安排'] },

        // Week 2: 一元函数积分学
        { day: 8, title: '不定积分', topics: ['不定积分的概念与性质', '第一类与第二类换元法'] },
        { day: 9, title: '分部积分法', topics: ['分部积分公式的应用', '常见积分形式'] },
        { day: 10, title: '定积分', topics: ['定积分的定义与性质', '牛顿-莱布尼茨公式'] },
        { day: 11, title: '定积分的计算', topics: ['换元积分法与分部积分法', '反常积分'] },
        { day: 12, title: '定积分的应用', topics: ['几何应用：面积、体积', '物理应用：功、压力'] },
        { day: 13, title: '第二周复习与总结', topics: ['复习一元函数积分学', '强化积分计算能力'] },
        { day: 14, title: '休息或查漏补缺', topics: ['自由安排'] },

        // Week 3: 常微分方程 & 线性代数
        { day: 15, title: '常微分方程', topics: ['可分离变量、齐次方程', '一阶线性微分方程'] },
        { day: 16, title: '行列式', topics: ['行列式的性质', '按行(列)展开定理'] },
        { day: 17, title: '矩阵(一)', topics: ['矩阵的运算', '逆矩阵'] },
        { day: 18, title: '矩阵(二)', topics: ['初等变换与初等矩阵', '矩阵的秩'] },
        { day: 19, title: '向量', topics: ['向量的线性相关与无关', '向量组的秩'] },
        { day: 20, title: '第三周复习与总结', topics: ['复习微分方程与线性代数初步', '进行综合练习'] },
        { day: 21, title: '休息或查漏补缺', topics: ['自由安排'] },

        // Week 4: 线性代数 & 总复习
        { day: 22, title: '线性方程组', topics: ['克拉默法则', '非齐次与齐次线性方程组的解'] },
        { day: 23, title: '特征值与特征向量', topics: ['特征值与特征向量的计算', '相似矩阵'] },
        { day: 24, title: '二次型', topics: ['二次型及其矩阵表示', '化二次型为标准型'] },
        { day: 25, title: '总复习(一)：高等数学', topics: ['极限、导数、积分的重点和难点回顾'] },
        { day: 26, title: '总复习(二)：线性代数', topics: ['矩阵、向量、方程组、特征值的串联复习'] },
        { day: 27, title: '模拟考试(一)', topics: ['进行一套完整的模拟题', '分析错题'] },
        { day: 28, title: '模拟考试(二)', topics: ['进行第二套模拟题', '总结解题技巧'] },
        { day: 29, title: '考前冲刺', topics: ['回顾所有错题', '记忆核心公式'] },
        { day: 30, title: '最后准备', topics: ['调整心态', '准备考试用品'] }
    ];

    const sidebar = document.getElementById('plan-sidebar');
    const contentArea = document.getElementById('content-area');
    const initialContent = contentArea.innerHTML;

    let progress = JSON.parse(localStorage.getItem('math2Progress')) || {};

    function renderPlan() {
        sidebar.innerHTML = '';
        studyPlan.forEach(item => {
            const isCompleted = progress[item.day];
            const planItem = document.createElement('div');
            planItem.className = `plan-item ${isCompleted ? 'completed' : ''}`;
            planItem.dataset.day = item.day;

            planItem.innerHTML = `
                <input type="checkbox" ${isCompleted ? 'checked' : ''}>
                <div class="day-info">
                    <div class="day-number">第 ${item.day} 天</div>
                    <div class="day-title">${item.title}</div>
                </div>
            `;

            // 点击整个条目来显示内容
            planItem.querySelector('.day-info').addEventListener('click', () => {
                renderContent(item);
                updateActiveState(item.day);
            });

            // 点击 checkbox 更新进度
            planItem.querySelector('input[type="checkbox"]').addEventListener('change', (e) => {
                progress[item.day] = e.target.checked;
                localStorage.setItem('math2Progress', JSON.stringify(progress));
                planItem.classList.toggle('completed', e.target.checked);
            });

            sidebar.appendChild(planItem);
        });
    }

    function renderContent(item) {
        let resourcesHtml = '';
        if (item.resources && item.resources.length > 0) {
            resourcesHtml = `
                <div class="content-section">
                    <h3>推荐资源</h3>
                    <div class="resource-links">
                        ${item.resources.map(resource => `
                            <a href="${resource.url}" target="_blank" class="resource-link-item">${resource.title}</a>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            resourcesHtml = `
                <div class="content-section">
                    <h3>核心概念</h3>
                    <div class="example"><p>暂无在线资源，请自行查阅资料。</p></div>
                </div>
            `;
        }

        contentArea.innerHTML = `
            <div class="content-header">
                <h2>第 ${item.day} 天: ${item.title}</h2>
            </div>
            <div class="content-section">
                <h3>学习要点</h3>
                <ul>
                    ${item.topics.map(topic => `<li>${topic}</li>`).join('')}
                </ul>
            </div>
            ${resourcesHtml}
        `;
    }
    
    function updateActiveState(day) {
        document.querySelectorAll('.plan-item').forEach(el => {
            el.classList.remove('active');
        });
        const activeItem = document.querySelector(`.plan-item[data-day='${day}']`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    renderPlan();
});
