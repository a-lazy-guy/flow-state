# 团队分工与职责说明书

本文档详细界定了“心境 (Flow State)”项目 6 人团队的角色分配、职责范围及模块归属。

---

## 1. 团队角色概览

| 角色 | 人数 | 核心职责 | 关键词 |
| :--- | :---: | :--- | :--- |
| **产品体验官 ** | 1 | 需求分析、质量验收 | 方向、验收 |
| **TPM** | 1 | 架构设计、核心胶水代码、DevOps | 架构、兜底 |
| **AI 算法工程师** | 2 | 视觉算法、OCR、状态判定模型 | 智能、识别 |
| **后端/数据工程师** | 2 | 数据库设计、数据统计、API 开发 | 存储、统计 |


---

## 2. 详细职责与模块分配

### 2.2 系统集成工程师 (Tech Lead - 你)
*   **职责**:
    *   **架构把控**: 维护项目结构 (`PROJECT_STRUCTURE.md`)，制定代码规范。
    *   **核心串联**: 负责将 AI、数据、UI 模块组装在一起。
    *   **基础设施**: 负责 `app/core/` 配置管理、`app/main.py` 入口逻辑。
    *   **监控服务**: 维护 `app/services/monitor_service.py` 线程逻辑。
    *   **发布运维**: 负责 Python 环境管理、打包 (PyInstaller) 与发布。
*   **核心模块**:
    *   `app/core/` (Config)
    *   `app/main.py` (App Entry)
    *   `app/services/monitor_service.py` (Monitor Thread)
    *   `run.py`

### 2.3 AI 算法工程师
*   **职责**:
    *   **状态检测**: 优化疲劳/专注/娱乐的判定算法（引入人脸/视线检测）。
    *   **视觉分析**: 维护 `app/services/ai/vision.py`，处理摄像头帧流。
    *   **OCR 识别**: 实现屏幕文字识别功能，清洗 OCR 结果。
    *   **智能总结**: 利用 LLM 生成日报/周报的自然语言评语。
*   **核心模块**:
    *   `app/services/ai/vision.py` (Camera Analyzer)
    *   `app/services/ai/inference.py` (Logic & Classification)
    *   `app/services/reminder/generator.py` (Smart Content Gen)

### 2.4 后端/数据工程师
*   **职责**:
    *   **数据存储**: 设计与维护 SQLite 表结构 (`app/core/database.py`)。
    *   **DAO 层开发**: 编写高效的 SQL 操作 (`app/data/dao/`)。
    *   **统计分析**: 编写复杂 SQL 聚合查询（日报/周报数据源）。
    *   **数据清理**: 开发磁盘清理策略，防止截图占满硬盘。
    *   **API 服务**: (如有云同步需求) 开发 Flask/FastAPI 接口。
*   **核心模块**:
    *   `app/data/base.py` (DB Init)
    *   `app/data/dao/` (All DAOs)
    *   `app/data/history.py` (Business Logic for Data)
    *   `app/services/ai/inference.py` (User Auth API parts)

<!-- ### 2.5 UI 工程师 A (交互方向)
*   **职责**:
    *   **悬浮球交互**: 开发悬浮球的拖拽、吸附、状态切换逻辑。
    *   **功能弹窗**: 负责番茄钟、疲劳提醒、设置界面的逻辑实现。
    *   **用户流程**: 确保用户点击流畅，无交互死角。
*   **核心模块**:
    *   `app/ui/widgets/float_ball.py`
    *   `app/ui/views/popup_view.py`
    *   `app/ui/widgets/dialogs/` (Tomato, Fatigue, Settings)
    *   `app/ui/widgets/focus_card.py` (Interaction logic) -->

<!-- ### 2.6 UI 工程师 B (视觉/报表方向)
*   **职责**:
    *   **数据可视化**: 将后端提供的统计数据渲染为图表 (Matplotlib/PyQtGraph)。
    *   **视觉特效**: 开发粒子系统、星空背景、呼吸动效。
    *   **主题管理**: 负责深色/浅色模式切换及全局样式。
*   **核心模块**:
    *   `app/ui/widgets/report/` (Daily, Weekly, Monthly Reports)
    *   `app/ui/widgets/visuals/` (Particle Systems, Effects)
    *   `app/ui/widgets/report/theme.py` -->

---

## 3. 关键跨部门协作流程

### 3.1 日报/周报功能开发
1.  **PM**: 定义报表里要展示哪些数据（如：专注时长、拉回次数）。
2.  **后端**: 在 `StatsDAO` 中写好 SQL 查询，提供 `get_daily_summary()` 接口。
3.  **AI**: (可选) 提供 `generate_comment()` 接口生成智能评语。
4.  **UI (B)**: 调用上述接口，画出图表并展示评语。
5.  **集成 (你)**: 确保数据流转通畅，无卡顿。

### 3.2 疲劳检测优化
1.  **AI**: 升级 `vision.py` 算法，增加“闭眼检测”逻辑。
2.  **后端**: 提供 `get_recent_focus_time()` 接口，辅助 AI 判断（专注太久更容易疲劳）。
3.  **集成 (你)**: 在 `monitor_service.py` 中串联逻辑，触发提醒信号。
4.  **UI (A)**: 优化疲劳提醒弹窗 (`fatigue.py`) 的展示效果。

### 3.3 数据清理与存储
1.  **集成 (你)**: 制定策略（如：截图只存 7 天）。
2.  **后端**: 编写清理脚本，并在 `app/data/` 中实现。
3.  **PM**: 确认该策略不会引起用户投诉。
