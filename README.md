<div align="center">

# 🌙 LuminOS

**Lumin**ous Intelligence + **OS** — 一个面向 AI4S（AI for Science）的本地优先智能体工作台

<p>
  <img src="src/frontend/public/home/luminos-logo.png" alt="LuminOS" width="240">
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/version-0.1.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.11%2B-yellow.svg" alt="Python">
  <img src="https://img.shields.io/badge/typescript-5.9%2B-3178C6.svg" alt="TypeScript">
  <img src="https://img.shields.io/badge/agentscope-2.0-orange.svg" alt="AgentScope">
</p>

<p>
  以持久化任务工作区为核心，把对话、文件、代码执行、知识库、图谱、画布、记忆、自动化任务和科研工具沉淀在同一个可持续演进的工作区里。
</p>

[English](#) · [快速开始](#快速开始) · [文档](#文档) · [路线图](#路线图) · [许可证](#许可证)

</div>

---

## ✨ 为什么用 LuminOS

- **工作区先于会话** — 文件、会话、Notebook、知识库、画布、记忆和产物都沉淀在工作区内，任务可以被回看、继续和复用。
- **多智能体原生** — 基于 [AgentScope 2.0](https://github.com/modelscope/agentscope) 构建，支持完整的多智能体编排、子 Agent 派发和工具市场。
- **MCP 深度集成** — 内置 10+ MCP 服务器（互联网搜索、Skill 管理、Agent 管理、自动化任务、批量执行、图表生成等）。
- **AI4S 科研工具箱** — 借鉴并精选了面向科研场景的 Skill（arxiv 检索、PDF 翻译、文献解析、OCR 等），开箱即用。
- **本地优先** — 单机单用户、本地代码执行、本地存储，可平滑过渡到容器化部署。
- **沙箱隔离** — 本地 Jupyter 与远程 script_runner 双模式，安全执行任意用户代码。

---


## 🚀 快速开始

### 前置要求

- Python 3.11+
- Node.js 22+
- npm 或 pnpm
- (可选) Docker 24+ — 用于容器化部署

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/LuminOS.git
cd LuminOS
```

### 2. 启动后端

```bash
cd src/backend
[ -f .env ] || cp .env.example .env
# 编辑 .env，填入你的 LLM API Key、Embedding Key 等
pip install -r requirements.txt
# 或使用 uv（推荐）
uv sync

# 启动开发服务器
python cli.py serve
# 后端默认监听 http://localhost:13001
```

### 3. 启动前端

```bash
cd src/frontend
npm install
npm run dev
# 前端默认监听 http://localhost:13000
```

### 4. (可选) 容器化部署

```bash
# 完整启动
docker compose up -d

# 仅启动记忆系统 (mem0 + Milvus + Neo4j)
docker compose --profile mem0 up -d

# 仅启动数据库辅助工具
docker compose --profile dbhub up -d
```

服务端口：

| 服务 | 地址 |
|------|------|
| 前端 Web 界面 | http://localhost:13000 |
| 后端 API | http://localhost:13001 |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6380 |
| MCP 服务器 | localhost:9100 |
| Script Runner | localhost:8900 |

---

## 🏗️ 架构概览

```
┌─────────────────────────────────────────────────────────┐
│            LuminOS Frontend (React 19 + Vite 7)         │
│  /workspace · /agent · /knowledge · /automation · ...   │
└────────────────────┬────────────────────────────────────┘
                     │ REST + WebSocket + SSE
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐            ┌─────▼─────┐
    │ Backend │◄──MCP────►│ MCP 集群  │
    │ FastAPI │            │ 10+ 服务器│
    │ Python  │            └───────────┘
    └────┬────┘
         │
   ┌─────┼──────────┬─────────────┐
   │     │          │             │
┌──▼──┐ ┌▼─────┐ ┌──▼──┐  ┌─────▼─────┐
│ PG  │ │Redis │ │Script│  │ AgentScope│
│     │ │     │ │Runner│  │   2.0     │
└─────┘ └──────┘ └──────┘  └───────────┘
```

### 后端技术栈

- **Web 框架**: FastAPI + Uvicorn + Pydantic v2
- **AI 编排**: AgentScope 2.0.0
- **数据库**: PostgreSQL 15 + SQLAlchemy 2.0 + Alembic
- **缓存 / 事件总线**: Redis 7
- **记忆系统** (可选): mem0 + Milvus 2.5 + Neo4j 5
- **多模型支持**: OpenAI / Anthropic / Qwen / Gemini / Ollama / 自定义
- **MCP**: mcp 1.x 标准协议 + 自研 10+ 服务器
- **沙箱**: 本地 Jupyter / 远程 script_runner

### 前端技术栈

- **框架**: React 19 + TypeScript 5.9 + Vite 7
- **UI 库**: Ant Design 6.3
- **编辑器**: CodeMirror 6（代码 + JSON / Markdown）
- **画布**: 自研 Canvas + Univer 表格
- **状态管理**: Zustand
- **可视化**: Marked + Mermaid + KaTeX + html2pdf.js

### 桌面端

- Tauri 2（Rust 内核 + Web 前端）
- 三端支持：Windows / macOS / Linux
- 内置 WebSocket 代理与本地子进程管理

---

## 🧬 AI4S 科研 Skill

LuminOS 在保留原有 Skill 市场框架的基础上，引入了精选科研工具包。这些 Skill 以**自包含包**形式存在（Markdown 文档 + Python 脚本），无需修改宿主代码即可加载。

### 已收录的 Skill（部分）

| Skill | 功能 | 路径 |
|-------|------|------|
| `arxiv-search-skill` | arxiv 论文搜索与下载 | `src/backend/skill_bundles/default/arxiv-search-skill/` |
| `officecli-academic-paper` | 学术论文排版（APA / IEEE / Chicago / MLA） | `src/backend/skill_bundles/default/officecli-academic-paper/` |
| `pdf-editing` | PDF 解析与编辑 | `src/backend/skill_bundles/default/pdf-editing/` |
| `morph-ppt` | 学术 PPT 自动生成 | `src/backend/skill_bundles/default/morph-ppt/` |
| `officecli-data-dashboard` | 数据仪表盘排版 | `src/backend/skill_bundles/default/officecli-data-dashboard/` |

每个 Skill 包含：

- `SKILL.md` — YAML frontmatter + 详细使用文档
- `scripts/` — 可独立运行的 Python 脚本
- `README.md` — 快速说明

### 借鉴来源

科研 Skill 的设计灵感来自 [AIASys](https://github.com/AIAsys/AIASys) 项目（Apache 2.0）。LuminOS 借鉴并精选了其中面向 AI4S 场景的 Skill，保留自包含的脚本与文档结构，适配 LuminOS 的 Skill 加载机制。

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [重构规格说明书](LuminOS-Refactor-Spec.md) | LuminOS 改名与 AI4S 强化的完整方案 |
| [DESIGN.md](DESIGN.md) | 视觉设计基线（颜色 / 排版 / 布局 / 组件） |
| `docs/guides/getting-started/` | 快速入门与部署 |
| `docs/guides/workspace/` | 工作区使用指南 |
| `docs/guides/agent/` | Agent 对话与配置 |
| `docs/guides/capabilities/` | MCP / Skill / 能力市场 |
| `docs/guides/development/` | 开发与扩展 |
| `docs/guides/operations/` | 运维与监控 |
| `docs/changelog/` | 更新日志 |

---

## 🗓️ 路线图

### ✅ 已完成 (v0.1.0-alpha)

- [x] 完成品牌统一改名
- [x] 移除 CE / EE 版本分支，合并为单一开源版
- [x] 字符串级改名（210 个代码文件）
- [x] 删除 CE/EE 环境变量 (`JX_EDITION` / `VITE_EDITION`)
- [x] DESIGN.md 品牌更新
- [x] 引入第一批科研 Skill（含 arxiv-search）

### 🚧 进行中

- [ ] 前端 CE/EE 判断清理（删除 `agentEdition.tsx` 等）
- [ ] 后端 edition 概念的"止血"处理（保留兼容性，移除显式分支）
- [ ] Skill frontmatter 适配（统一 ID 命名规则）

### 📋 规划中

- [ ] v0.2.0 — 完整清理后端 edition 概念
- [ ] v0.3.0 — 引入 mem0 / Milvus 记忆系统一键安装
- [ ] v0.4.0 — 工作区模板市场（论文精读 / 数据分析 / 实验记录）
- [ ] v1.0.0 — 第一个稳定版本

---

## 🤝 贡献

LuminOS 欢迎所有形式的贡献：

- 🐛 报告 Bug：[GitHub Issues](../../issues)
- 💡 提出新功能：[GitHub Discussions](../../discussions)
- 🔧 提交代码：[Pull Requests](../../pulls)
- 📚 改进文档：[Docs Repository](../../tree/main/docs)
- 🧪 分享 Skill：在 `skill_bundles/marketplace/` 提交你的 Skill 包

### 开发约定

- 后端遵循 PEP 8 + Black 100 字符行宽
- 前端遵循 ESLint + Prettier
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)
- Skill 包必须是自包含的（Markdown + 独立脚本）

---

## 🔒 许可证

LuminOS 基于 **Apache License 2.0** 开源，详见 [LICENSE](LICENSE)。

```
Copyright 2026 LuminOS Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

---

## 🙏 致谢

LuminOS 的诞生离不开以下开源项目：

- [AgentScope](https://github.com/modelscope/agentscope) — 多智能体编排框架
- [AIASys](https://github.com/AIAsys/AIASys) — 工作区与科研 Skill 设计灵感
- [Model Context Protocol](https://modelcontextprotocol.io/) — MCP 标准
- [FastAPI](https://fastapi.tiangolo.com/) · [React](https://react.dev/) · [Tauri](https://tauri.app/)
- 以及所有上游依赖的作者和贡献者

---

## 📮 联系方式

- GitHub Issues: [提交问题](../../issues)
- GitHub Discussions: [参与讨论](../../discussions)
- Email: `luminos@example.com`

---

<div align="center">

**如果 LuminOS 对你的科研工作有帮助，请给我们一个 ⭐️！**

</div>