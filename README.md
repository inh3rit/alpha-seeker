# Alpha Seeker

A股智能推荐系统 - MVP 第一阶段：基础设施 + 数据 + 策略引擎

## 快速开始

### 前置依赖

- Docker 和 Docker Compose
- Python 3.11+

### 初始化环境

```bash
# 复制环境变量文件
cp .env.example .env

# 启动基础服务（PostgreSQL + Redis）
docker-compose up -d

# 安装 Python 依赖
pip install -e ".[dev]"

# 运行数据库迁移
alpha-seeker db init

# 抓取股票列表
alpha-seeker data fetch-stocks

# 运行策略
alpha-seeker strategy run --code 600519
```

## 文档

- 系统设计：`docs/superpowers/specs/2026-05-12-alpha-seeker-design.md`
- MVP 计划 1：`docs/superpowers/plans/2026-05-12-mvp-plan-1-infrastructure-data-strategy.md`
