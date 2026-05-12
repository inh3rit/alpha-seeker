# Alpha Seeker MVP Plan 2A：后端 API + 推荐引擎 + 通知系统

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Plan 1 的数据和策略基础上，构建 FastAPI 后端 API、每日推荐生成引擎、持仓管理、Celery 定时任务和企业微信/钉钉通知推送。

**Architecture:** FastAPI 提供 RESTful API，Celery + Redis 处理定时任务（每日数据抓取、策略运行、推荐生成、通知推送），推荐引擎综合多策略评分生成每日推荐清单，通知模块通过 Webhook 推送到企业微信/钉钉。

**Tech Stack:** FastAPI, Celery, Redis, SQLAlchemy 2.0, httpx (Webhook), APScheduler (备选), pytest, pytest-asyncio

---

## File Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app 实例和路由注册
│   │   ├── deps.py              # 依赖注入（db session 等）
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── market.py        # GET /api/market/overview
│   │   │   ├── recommendations.py  # GET /api/recommendations/daily, /:code
│   │   │   ├── rankings.py      # GET /api/rankings/:type
│   │   │   ├── positions.py     # CRUD /api/positions
│   │   │   └── stocks.py        # GET /api/stocks/:code/chart, /indicators
│   │   └── schemas.py           # Pydantic response/request schemas
│   ├── models/
│   │   ├── position.py          # UserPosition 模型 (NEW)
│   │   └── recommendation.py    # Recommendation 模型 (NEW)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recommendation.py    # 推荐引擎核心逻辑
│   │   └── notification.py      # 通知推送（Webhook）
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py        # Celery 实例配置
│   │   ├── daily.py             # 每日定时任务
│   │   └── schedule.py          # Celery Beat 调度配置
│   ├── cli.py                   # (MODIFY) 添加 api/worker 启动命令
│   ├── config.py                # (MODIFY) 添加通知相关配置
│   └── models/__init__.py       # (MODIFY) 注册新模型
├── tests/
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── conftest.py          # FastAPI TestClient fixture
│   │   ├── test_market.py
│   │   ├── test_recommendations.py
│   │   ├── test_rankings.py
│   │   ├── test_positions.py
│   │   └── test_stocks.py
│   ├── test_services/
│   │   ├── __init__.py
│   │   ├── test_recommendation.py
│   │   └── test_notification.py
│   └── test_tasks/
│       ├── __init__.py
│       └── test_daily.py
└── Dockerfile                   # (NEW) 后端容器化
```

---

## 阶段 1：新增数据模型

### Task 1: 创建 Recommendation 模型

**Files:**
- Create: `backend/app/models/recommendation.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/tests/test_models.py`

- [ ] **Step 1: 编写失败测试**

在 `backend/tests/test_models.py` 末尾追加：

```python
from app.models.recommendation import Recommendation


def test_recommendation_can_be_created(in_memory_db):
    rec = Recommendation(
        code="600519",
        recommend_date=date(2026, 5, 12),
        score=Decimal("85.50"),
        signals=["双均线金叉", "MACD金叉"],
        reason="技术面强势，多个买入信号共振",
        suggested_action="buy",
        risk_level="medium",
    )
    in_memory_db.add(rec)
    in_memory_db.commit()

    result = in_memory_db.query(Recommendation).filter_by(code="600519").first()
    assert result is not None
    assert result.score == Decimal("85.50")
    assert result.signals == ["双均线金叉", "MACD金叉"]
    assert result.suggested_action == "buy"
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_models.py::test_recommendation_can_be_created -v`
Expected: FAIL

- [ ] **Step 3: 实现 `backend/app/models/recommendation.py`**

```python
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Date, DateTime, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database import Base


class Recommendation(Base):
    """每日推荐记录"""

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    recommend_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    signals: Mapped[list[Any]] = mapped_column(JSON, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_action: Mapped[str] = mapped_column(String(20), nullable=False)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Recommendation(code={self.code!r}, date={self.recommend_date}, score={self.score})>"
```

- [ ] **Step 4: 更新 `backend/app/models/__init__.py`**

```python
from app.models.indicator import Indicator
from app.models.quote import DailyQuote
from app.models.recommendation import Recommendation
from app.models.stock import Stock

__all__ = ["Stock", "DailyQuote", "Indicator", "Recommendation"]
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest backend/tests/test_models.py -v`
Expected: All passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/recommendation.py backend/app/models/__init__.py backend/tests/test_models.py
git commit -m "feat(models): add Recommendation model"
```

---

### Task 2: 创建 UserPosition 模型

**Files:**
- Create: `backend/app/models/position.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/tests/test_models.py`

- [ ] **Step 1: 编写失败测试**

在 `backend/tests/test_models.py` 末尾追加：

```python
from app.models.position import UserPosition


def test_user_position_can_be_created(in_memory_db):
    pos = UserPosition(
        user_id="default",
        code="600519",
        buy_date=date(2026, 5, 1),
        buy_price=Decimal("1800.00"),
        quantity=100,
        status="holding",
    )
    in_memory_db.add(pos)
    in_memory_db.commit()

    result = in_memory_db.query(UserPosition).filter_by(code="600519").first()
    assert result is not None
    assert result.buy_price == Decimal("1800.00")
    assert result.quantity == 100
    assert result.status == "holding"


def test_user_position_default_user_id(in_memory_db):
    pos = UserPosition(
        code="000001",
        buy_date=date(2026, 5, 10),
        buy_price=Decimal("15.50"),
        quantity=1000,
    )
    in_memory_db.add(pos)
    in_memory_db.commit()

    result = in_memory_db.query(UserPosition).first()
    assert result.user_id == "default"
    assert result.status == "holding"
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_models.py::test_user_position_can_be_created -v`
Expected: FAIL

- [ ] **Step 3: 实现 `backend/app/models/position.py`**

```python
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserPosition(Base):
    """用户持仓"""

    __tablename__ = "user_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(50), default="default", nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    buy_date: Mapped[date] = mapped_column(Date, nullable=False)
    buy_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="holding", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<UserPosition(code={self.code!r}, qty={self.quantity}, status={self.status!r})>"
```

- [ ] **Step 4: 更新 `backend/app/models/__init__.py`**

```python
from app.models.indicator import Indicator
from app.models.position import UserPosition
from app.models.quote import DailyQuote
from app.models.recommendation import Recommendation
from app.models.stock import Stock

__all__ = ["Stock", "DailyQuote", "Indicator", "Recommendation", "UserPosition"]
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest backend/tests/test_models.py -v`
Expected: All passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/position.py backend/app/models/__init__.py backend/tests/test_models.py
git commit -m "feat(models): add UserPosition model"
```

---
<!-- PLACEHOLDER_PHASE2 -->

## 阶段 2：推荐引擎服务

### Task 3: 实现推荐引擎核心逻辑

**Files:**
- Create: `backend/app/services/__init__.py`
- Create: `backend/app/services/recommendation.py`
- Create: `backend/tests/test_services/__init__.py`
- Create: `backend/tests/test_services/test_recommendation.py`

核心逻辑：遍历所有有数据的股票，运行所有策略，综合评分，生成推荐清单并存入数据库。

---

### Task 4: 实现通知服务（Webhook）

**Files:**
- Create: `backend/app/services/notification.py`
- Create: `backend/tests/test_services/test_notification.py`
- Modify: `backend/app/config.py` (添加 WEBHOOK_URL 配置)

核心逻辑：格式化推荐结果为 Markdown，通过 httpx 发送到企业微信/钉钉 Webhook URL。

---

## 阶段 3：Celery 定时任务

### Task 5: 配置 Celery 实例

**Files:**
- Create: `backend/app/tasks/__init__.py`
- Create: `backend/app/tasks/celery_app.py`
- Create: `backend/app/tasks/schedule.py`

核心逻辑：创建 Celery 实例，配置 Redis 作为 broker，设置 Beat 调度（每日 15:30 触发）。

---

### Task 6: 实现每日定时任务链

**Files:**
- Create: `backend/app/tasks/daily.py`
- Create: `backend/tests/test_tasks/__init__.py`
- Create: `backend/tests/test_tasks/test_daily.py`

核心逻辑：daily_pipeline 任务链 = 数据抓取 → 策略运行 → 推荐生成 → 通知推送。

---

## 阶段 4：FastAPI 后端 API

### Task 7: 创建 FastAPI 应用和依赖注入

**Files:**
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/main.py`
- Create: `backend/app/api/deps.py`
- Create: `backend/app/api/schemas.py`
- Create: `backend/app/api/routes/__init__.py`

---

### Task 8: 实现推荐相关 API

**Files:**
- Create: `backend/app/api/routes/recommendations.py`
- Create: `backend/tests/test_api/__init__.py`
- Create: `backend/tests/test_api/conftest.py`
- Create: `backend/tests/test_api/test_recommendations.py`

API:
- `GET /api/recommendations/daily` - 获取今日推荐清单
- `GET /api/recommendations/daily?date=2026-05-12` - 获取指定日期推荐

---

### Task 9: 实现持仓管理 API

**Files:**
- Create: `backend/app/api/routes/positions.py`
- Create: `backend/tests/test_api/test_positions.py`

API:
- `GET /api/positions` - 持仓列表
- `POST /api/positions` - 添加持仓
- `PUT /api/positions/:id` - 更新持仓
- `DELETE /api/positions/:id` - 删除持仓

---

### Task 10: 实现排行榜和股票数据 API

**Files:**
- Create: `backend/app/api/routes/rankings.py`
- Create: `backend/app/api/routes/stocks.py`
- Create: `backend/tests/test_api/test_rankings.py`
- Create: `backend/tests/test_api/test_stocks.py`

API:
- `GET /api/rankings/score` - 综合评分排行
- `GET /api/stocks/:code/chart` - K线数据
- `GET /api/stocks/:code/indicators` - 技术指标数据

---

## 阶段 5：集成和部署

### Task 11: 更新 CLI 和 Docker 配置

**Files:**
- Modify: `backend/app/cli.py` (添加 api serve 和 worker 命令)
- Create: `backend/Dockerfile`
- Modify: `docker-compose.yml` (添加 backend, celery-worker, celery-beat 服务)

---

### Task 12: 更新配置和 README

**Files:**
- Modify: `backend/app/config.py` (添加 API 和通知配置)
- Modify: `.env.example` (添加新的环境变量)
- Modify: `README.md` (更新使用指南)

---

## 完成标准

- [ ] 所有测试通过
- [ ] `alpha-seeker api serve` 启动 FastAPI 服务
- [ ] `GET /api/recommendations/daily` 返回推荐清单
- [ ] `POST /api/positions` 可以添加持仓
- [ ] `GET /api/rankings/score` 返回排行榜
- [ ] Celery worker 可以执行每日任务链
- [ ] 通知推送到企业微信/钉钉（需要配置 Webhook URL）

---

**计划文档结束**
