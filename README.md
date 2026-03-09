# AI Opportunity Spider

每天自动从 **GitHub Trending**、**HackerNews**、**ProductHunt** 抓取 AI 相关项目与讨论，通过 **智谱 GLM（OpenAI 兼容接口）** 分析提炼出 **Top 3 创业机会信号**，生成结构化 Markdown 报告并自动提交到仓库。

## Features

- **多源数据采集** — 并发抓取 GitHub Trending / HackerNews / ProductHunt 三大平台
- **AI 关键词过滤** — 基于 30+ 关键词（LLM、Agent、RAG、MCP 等）自动筛选 AI 相关条目
- **GPT 深度分析** — 从增长速度、市场缺口、技术突破、社区热度四个维度评分
- **每日报告** — 自动生成 Markdown 格式的机会雷达报告，含信号强度星级评分
- **GitHub Actions 自动化** — 每天定时运行，报告自动 commit 到 `reports/` 目录

## How It Works

```
GitHub Trending ──┐
HackerNews ───────┼──▶ AI 关键词过滤 ──▶ 智谱 GLM 分析 ──▶ Markdown 报告
ProductHunt ──────┘
```

1. 三个爬虫并发抓取各平台当日热门内容
2. 基于关键词列表过滤出 AI 相关条目
3. 将过滤后的数据发送给智谱 GLM，从四个维度识别创业机会
4. 生成带星级评分的 Markdown 报告，保存到 `reports/YYYY-MM-DD.md`

## Project Structure

```
ai-opportunity-spider/
├── main.py                     # 入口，编排爬虫 → 分析 → 报告流程
├── config.py                   # 配置项（API Key、关键词、URL 等）
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
├── src/
│   ├── models.py               # 数据模型（RawItem / Opportunity / DailyReport）
│   ├── analyzer.py             # 智谱 GLM 分析模块
│   ├── reporter.py             # Markdown 报告生成器
│   └── spiders/
│       ├── base.py             # 爬虫基类（含 AI 关键词过滤）
│       ├── github_trending.py  # GitHub Trending 爬虫
│       ├── hackernews.py       # HackerNews 爬虫（Firebase API）
│       └── producthunt.py      # ProductHunt 爬虫
├── reports/                    # 生成的每日报告
│   └── 2026-03-06.md
├── tests/
└── .github/workflows/
    └── daily.yml               # GitHub Actions 定时任务
```

## Quick Start

### 1. 克隆仓库

```bash
git clone https://github.com/<your-username>/ai-opportunity-spider.git
cd ai-opportunity-spider
```

### 2. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的智谱 GLM API Key：

```env
ZHIPU_API_KEY=your-zhipu-api-key-here
ZHIPU_MODEL=glm-4
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
```

### 4. 运行

```bash
python main.py
```

报告将保存到 `reports/` 目录，文件名为当天日期（如 `reports/2026-03-07.md`）。

## Configuration

所有配置项在 `config.py` 中管理：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ZHIPU_API_KEY` | 智谱 GLM API 密钥 | 从 `.env` 读取 |
| `ZHIPU_MODEL` | 使用的模型 | `glm-4` |
| `ZHIPU_BASE_URL` | 智谱 OpenAI 兼容 API Base URL | `https://open.bigmodel.cn/api/paas/v4/` |
| `AI_KEYWORDS` | AI 关键词过滤列表 | 30+ 关键词 |
| `HN_TOP_STORIES_LIMIT` | HackerNews 抓取条数上限 | `80` |
| `TOP_OPPORTUNITIES_COUNT` | 每日输出的机会数量 | `3` |

## Data Sources

| Source | 抓取方式 | 采集指标 |
|--------|----------|----------|
| GitHub Trending | HTML 解析 | 今日 Star 数、总 Star 数、项目描述 |
| HackerNews | Firebase API | 评分、评论数、标题 |
| ProductHunt | HTML / JSON 解析 | 点赞数、标语、话题标签 |

## Report Example

每日报告包含两个部分：

**Top Opportunities** — AI 识别的创业机会，每条包含：
- 信号强度（1-5 星评分）
- 来源平台
- 机会分类（开发者工具 / AI 基础设施 / 消费级 AI 等）
- 为什么是强信号（2-3 句分析）
- 创业方向建议
- 相关链接

**Raw Data** — 当日各平台采集到的 AI 相关条目统计。

## Automation

项目通过 GitHub Actions 实现全自动运行：

- **定时执行**：每天 UTC 08:00（北京时间 16:00）自动触发
- **手动触发**：支持在 Actions 页面手动运行 (`workflow_dispatch`)
- **自动提交**：运行完毕后自动将报告 commit 并 push 到仓库

### 设置步骤

1. Fork 或 push 本仓库到你的 GitHub
2. 进入仓库 **Settings → Secrets and variables → Actions**
3. 添加 Repository Secret：`ZHIPU_API_KEY`（可选：`ZHIPU_MODEL`、`ZHIPU_BASE_URL`）
4. 前往 **Actions** 标签页确认 workflow 已启用

## Tech Stack

- **Python 3.12+**
- **httpx** — 异步 HTTP 客户端
- **BeautifulSoup4** — HTML 解析
- **OpenAI 兼容 SDK** — 调用智谱 GLM 分析
- **Pydantic** — 数据校验与模型定义
- **GitHub Actions** — CI/CD 自动化

## License

MIT
