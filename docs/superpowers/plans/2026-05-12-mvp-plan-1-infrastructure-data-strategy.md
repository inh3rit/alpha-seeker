# Alpha Seeker MVP 计划 1：基础设施 + 数据 + 策略引擎

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建 Alpha Seeker 项目基础设施，实现 A 股数据抓取与存储，构建可扩展的策略引擎（双均线、MACD、RSI），并通过命令行工具验证端到端数据流。

**Architecture:** 单体 Python 应用，使用 Docker Compose 编排 PostgreSQL + Redis，通过 AKShare 抓取 A 股数据存储到 PostgreSQL，使用策略模式（Strategy Pattern）实现可插拔的量化策略，通过 CLI 工具触发数据抓取和策略运行。

**Tech Stack:** Python 3.11, PostgreSQL 15, Redis 7, SQLAlchemy 2.0, AKShare, pandas, TA-Lib（或 pandas-ta）, pytest, Docker Compose, Typer (CLI 框架)

---

## File Structure

```
alpha-seeker/
├── docker-compose.yml              # 编排 PostgreSQL + Redis
├── .env.example                    # 环境变量模板
├── .gitignore
├── pyproject.toml                  # Python 依赖和项目配置
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py               # 应用配置（从环境变量加载）
│   │   ├── database.py             # 数据库连接和 Session
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── stock.py            # Stock 模型
│   │   │   ├── quote.py            # DailyQuote 模型
│   │   │   └── indicator.py        # Indicator 模型
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   ├── fetcher.py          # AKShare 数据抓取
│   │   │   └── storage.py          # 数据存储逻辑
│   │   ├── indicators/
│   │   │   ├── __init__.py
│   │   │   ├── ma.py               # 均线指标
│   │   │   ├── macd.py             # MACD 指标
│   │   │   └── rsi.py              # RSI 指标
│   │   ├── strategies/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # 策略基类和注册器
│   │   │   ├── dual_ma.py          # 双均线策略
│   │   │   ├── macd_strategy.py    # MACD 策略
│   │   │   └── rsi_strategy.py     # RSI 策略
│   │   └── cli.py                  # Typer CLI 入口
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # pytest fixtures
│       ├── test_config.py
│       ├── test_database.py
│       ├── test_models.py
│       ├── test_fetcher.py
│       ├── test_storage.py
│       ├── test_indicators/
│       │   ├── test_ma.py
│       │   ├── test_macd.py
│       │   └── test_rsi.py
│       ├── test_strategies/
│       │   ├── test_base.py
│       │   ├── test_dual_ma.py
│       │   ├── test_macd_strategy.py
│       │   └── test_rsi_strategy.py
│       └── test_cli.py
└── docs/
    └── superpowers/
        ├── specs/
        │   └── 2026-05-12-alpha-seeker-design.md
        └── plans/
            └── 2026-05-12-mvp-plan-1-infrastructure-data-strategy.md
```

---

## 阶段 1：项目初始化

### Task 1: 创建项目基础文件

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `README.md`
- Create: `pyproject.toml`

- [ ] **Step 1: 创建 `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Data
data/
*.db
*.sqlite
logs/

# Docker
.docker/
```

- [ ] **Step 2: 创建 `.env.example`**

```bash
# Database
POSTGRES_USER=alpha_seeker
POSTGRES_PASSWORD=alpha_seeker_password
POSTGRES_DB=alpha_seeker
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Application
LOG_LEVEL=INFO
ENVIRONMENT=development
```

- [ ] **Step 3: 创建 `pyproject.toml`**

```toml
[project]
name = "alpha-seeker"
version = "0.1.0"
description = "A股智能推荐系统"
requires-python = ">=3.11"
dependencies = [
    "sqlalchemy>=2.0.0",
    "psycopg2-binary>=2.9.0",
    "redis>=5.0.0",
    "akshare>=1.12.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "pandas-ta>=0.3.14b",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "loguru>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[project.scripts]
alpha-seeker = "app.cli:app"

[tool.pytest.ini_options]
testpaths = ["backend/tests"]
pythonpath = ["backend"]
python_files = "test_*.py"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "W", "N"]
```

- [ ] **Step 4: 创建 `README.md`**

```markdown
# Alpha Seeker

A股智能推荐系统 - MVP 第一阶段：基础设施 + 数据 + 策略引擎

## 快速开始

### 前置依赖

- Docker 和 Docker Compose
- Python 3.11+

### 初始化环境

\`\`\`bash
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
\`\`\`

## 文档

- 系统设计：`docs/superpowers/specs/2026-05-12-alpha-seeker-design.md`
- MVP 计划 1：`docs/superpowers/plans/2026-05-12-mvp-plan-1-infrastructure-data-strategy.md`
```

- [ ] **Step 5: Commit**

```bash
git add .gitignore .env.example pyproject.toml README.md
git commit -m "chore: initialize project structure and dependencies"
```

---

### Task 2: 创建 Docker Compose 基础服务

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: 编写 docker-compose.yml**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: alpha-seeker-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-alpha_seeker}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-alpha_seeker_password}
      POSTGRES_DB: ${POSTGRES_DB:-alpha_seeker}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-alpha_seeker}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: alpha-seeker-redis
    ports:
      - "${REDIS_PORT:-6379}:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

- [ ] **Step 2: 启动服务并验证**

Run:
```bash
cp .env.example .env
docker-compose up -d
docker-compose ps
```

Expected output:
```
NAME                      STATUS    PORTS
alpha-seeker-postgres     Up        0.0.0.0:5432->5432/tcp
alpha-seeker-redis        Up        0.0.0.0:6379->6379/tcp
```

- [ ] **Step 3: 测试 PostgreSQL 连接**

Run:
```bash
docker exec alpha-seeker-postgres psql -U alpha_seeker -d alpha_seeker -c "SELECT version();"
```

Expected: PostgreSQL 版本信息输出

- [ ] **Step 4: 测试 Redis 连接**

Run:
```bash
docker exec alpha-seeker-redis redis-cli ping
```

Expected: `PONG`

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml
git commit -m "chore: add docker-compose for PostgreSQL and Redis"
```

---

### Task 3: 创建 backend 目录结构和基础配置

**Files:**
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_config.py`

- [ ] **Step 1: 创建空的 `__init__.py` 文件**

```bash
mkdir -p backend/app backend/tests
touch backend/app/__init__.py backend/tests/__init__.py
```

- [ ] **Step 2: 编写失败测试 `backend/tests/test_config.py`**

```python
import os
from unittest.mock import patch

import pytest

from app.config import Settings


def test_settings_load_from_env():
    """配置应该从环境变量加载"""
    with patch.dict(os.environ, {
        "POSTGRES_USER": "test_user",
        "POSTGRES_PASSWORD": "test_pass",
        "POSTGRES_DB": "test_db",
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
    }, clear=True):
        settings = Settings()
        assert settings.postgres_user == "test_user"
        assert settings.postgres_db == "test_db"
        assert settings.redis_port == 6379


def test_database_url_is_constructed():
    """database_url 应该从组件构造"""
    with patch.dict(os.environ, {
        "POSTGRES_USER": "user",
        "POSTGRES_PASSWORD": "pass",
        "POSTGRES_DB": "db",
        "POSTGRES_HOST": "host",
        "POSTGRES_PORT": "5432",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
        "REDIS_DB": "0",
    }, clear=True):
        settings = Settings()
        assert settings.database_url == "postgresql+psycopg2://user:pass@host:5432/db"


def test_redis_url_is_constructed():
    """redis_url 应该从组件构造"""
    with patch.dict(os.environ, {
        "POSTGRES_USER": "u",
        "POSTGRES_PASSWORD": "p",
        "POSTGRES_DB": "d",
        "POSTGRES_HOST": "h",
        "POSTGRES_PORT": "5432",
        "REDIS_HOST": "redis-host",
        "REDIS_PORT": "6380",
        "REDIS_DB": "2",
    }, clear=True):
        settings = Settings()
        assert settings.redis_url == "redis://redis-host:6380/2"
```

- [ ] **Step 3: 运行测试验证失败**

Run: `pytest backend/tests/test_config.py -v`
Expected: FAIL（`app.config` 模块不存在）

- [ ] **Step 4: 实现 `backend/app/config.py`**

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置，从环境变量加载"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    postgres_user: str = Field(default="alpha_seeker")
    postgres_password: str = Field(default="alpha_seeker_password")
    postgres_db: str = Field(default="alpha_seeker")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    
    log_level: str = Field(default="INFO")
    environment: str = Field(default="development")
    
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
```

- [ ] **Step 5: 创建 `backend/tests/conftest.py`**

```python
import os
import sys
from pathlib import Path

# 确保 backend 在 Python 路径中
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
```

- [ ] **Step 6: 运行测试验证通过**

Run: `pytest backend/tests/test_config.py -v`
Expected: 3 passed

- [ ] **Step 7: Commit**

```bash
git add backend/app/__init__.py backend/app/config.py backend/tests/__init__.py backend/tests/conftest.py backend/tests/test_config.py
git commit -m "feat(config): add settings loaded from environment variables"
```

---

## 阶段 2：数据层基础

### Task 4: 创建数据库连接和 Session 管理

**Files:**
- Create: `backend/app/database.py`
- Create: `backend/tests/test_database.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_database.py`**

```python
from sqlalchemy import text

from app.database import Base, SessionLocal, engine, get_db


def test_engine_is_configured():
    """数据库引擎应该被正确配置"""
    assert engine is not None
    assert "postgresql" in str(engine.url)


def test_base_has_metadata():
    """Base 类应该有 metadata 属性"""
    assert Base.metadata is not None


def test_session_factory_creates_session():
    """SessionLocal 应该能创建 session"""
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT 1")).scalar()
        assert result == 1
    finally:
        session.close()


def test_get_db_yields_session_and_closes():
    """get_db 应该生成 session 并在结束时关闭"""
    gen = get_db()
    db = next(gen)
    assert db is not None
    result = db.execute(text("SELECT 1")).scalar()
    assert result == 1
    try:
        next(gen)
    except StopIteration:
        pass
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_database.py -v`
Expected: FAIL（`app.database` 模块不存在）

- [ ] **Step 3: 实现 `backend/app/database.py`**

```python
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    """所有数据模型的基类"""
    pass


engine = create_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """依赖注入：数据库 session 生成器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: 运行测试验证通过（需要 Docker 服务已启动）**

Run: `pytest backend/tests/test_database.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/database.py backend/tests/test_database.py
git commit -m "feat(database): add SQLAlchemy engine and session management"
```

---

### Task 5: 创建 Stock 数据模型

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/stock.py`
- Create: `backend/tests/test_models.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_models.py`**

```python
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.stock import Stock


@pytest.fixture
def in_memory_db():
    """使用内存 SQLite 数据库进行模型测试"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_stock_can_be_created_with_required_fields(in_memory_db):
    """Stock 应该能用必需字段创建"""
    stock = Stock(
        code="600519",
        name="贵州茅台",
        industry="食品饮料",
        sector="主板",
        list_date=date(2001, 8, 27),
    )
    in_memory_db.add(stock)
    in_memory_db.commit()
    
    result = in_memory_db.query(Stock).filter_by(code="600519").first()
    assert result is not None
    assert result.name == "贵州茅台"
    assert result.industry == "食品饮料"


def test_stock_code_is_primary_key(in_memory_db):
    """相同 code 不能重复插入"""
    stock1 = Stock(code="600519", name="贵州茅台")
    in_memory_db.add(stock1)
    in_memory_db.commit()
    
    stock2 = Stock(code="600519", name="不同名称")
    in_memory_db.add(stock2)
    with pytest.raises(Exception):
        in_memory_db.commit()


def test_stock_repr(in_memory_db):
    """Stock 应该有可读的 repr"""
    stock = Stock(code="600519", name="贵州茅台")
    assert "600519" in repr(stock)
    assert "贵州茅台" in repr(stock)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_models.py -v`
Expected: FAIL（`app.models.stock` 不存在）

- [ ] **Step 3: 创建 `backend/app/models/__init__.py`**

```python
from app.models.stock import Stock

__all__ = ["Stock"]
```

- [ ] **Step 4: 实现 `backend/app/models/stock.py`**

```python
from datetime import date, datetime

from sqlalchemy import Date, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Stock(Base):
    """股票基本信息"""
    
    __tablename__ = "stocks"
    
    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sector: Mapped[str | None] = mapped_column(String(50), nullable=True)
    list_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Stock(code={self.code!r}, name={self.name!r})>"
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest backend/tests/test_models.py -v`
Expected: 3 passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/__init__.py backend/app/models/stock.py backend/tests/test_models.py
git commit -m "feat(models): add Stock model"
```

---

### Task 6: 创建 DailyQuote 数据模型

**Files:**
- Modify: `backend/app/models/__init__.py`
- Create: `backend/app/models/quote.py`
- Modify: `backend/tests/test_models.py`

- [ ] **Step 1: 追加失败测试到 `backend/tests/test_models.py`**

在文件末尾追加：

```python
from decimal import Decimal

from app.models.quote import DailyQuote


def test_daily_quote_can_be_created(in_memory_db):
    """DailyQuote 应该能被创建"""
    quote = DailyQuote(
        code="600519",
        trade_date=date(2026, 5, 12),
        open=Decimal("1800.00"),
        close=Decimal("1850.00"),
        high=Decimal("1860.00"),
        low=Decimal("1795.00"),
        volume=1000000,
        amount=Decimal("1850000000.00"),
    )
    in_memory_db.add(quote)
    in_memory_db.commit()
    
    result = in_memory_db.query(DailyQuote).filter_by(
        code="600519", trade_date=date(2026, 5, 12)
    ).first()
    assert result is not None
    assert result.close == Decimal("1850.00")


def test_daily_quote_unique_on_code_and_date(in_memory_db):
    """同一股票同一天只能有一条记录"""
    q1 = DailyQuote(
        code="600519",
        trade_date=date(2026, 5, 12),
        open=Decimal("1800.00"),
        close=Decimal("1850.00"),
        high=Decimal("1860.00"),
        low=Decimal("1795.00"),
        volume=1000000,
        amount=Decimal("1850000000.00"),
    )
    in_memory_db.add(q1)
    in_memory_db.commit()
    
    q2 = DailyQuote(
        code="600519",
        trade_date=date(2026, 5, 12),
        open=Decimal("1810.00"),
        close=Decimal("1860.00"),
        high=Decimal("1870.00"),
        low=Decimal("1800.00"),
        volume=2000000,
        amount=Decimal("3720000000.00"),
    )
    in_memory_db.add(q2)
    with pytest.raises(Exception):
        in_memory_db.commit()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_models.py -v`
Expected: FAIL（`app.models.quote` 不存在）

- [ ] **Step 3: 实现 `backend/app/models/quote.py`**

```python
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DailyQuote(Base):
    """日线行情数据"""
    
    __tablename__ = "daily_quotes"
    __table_args__ = (
        UniqueConstraint("code", "trade_date", name="uq_daily_quotes_code_date"),
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    open: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    
    def __repr__(self) -> str:
        return (
            f"<DailyQuote(code={self.code!r}, date={self.trade_date}, "
            f"close={self.close})>"
        )
```

- [ ] **Step 4: 更新 `backend/app/models/__init__.py`**

```python
from app.models.quote import DailyQuote
from app.models.stock import Stock

__all__ = ["Stock", "DailyQuote"]
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest backend/tests/test_models.py -v`
Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/__init__.py backend/app/models/quote.py backend/tests/test_models.py
git commit -m "feat(models): add DailyQuote model"
```

---

### Task 7: 创建 Indicator 数据模型

**Files:**
- Modify: `backend/app/models/__init__.py`
- Create: `backend/app/models/indicator.py`
- Modify: `backend/tests/test_models.py`

- [ ] **Step 1: 追加失败测试到 `backend/tests/test_models.py`**

在文件末尾追加：

```python
from app.models.indicator import Indicator


def test_indicator_can_be_created(in_memory_db):
    """Indicator 应该能被创建，value 为 JSON"""
    indicator = Indicator(
        code="600519",
        trade_date=date(2026, 5, 12),
        indicator_type="MA",
        indicator_value={"ma5": 1820.5, "ma20": 1780.3, "ma60": 1750.0},
    )
    in_memory_db.add(indicator)
    in_memory_db.commit()
    
    result = in_memory_db.query(Indicator).filter_by(
        code="600519", trade_date=date(2026, 5, 12), indicator_type="MA"
    ).first()
    assert result is not None
    assert result.indicator_value["ma5"] == 1820.5


def test_indicator_unique_on_code_date_type(in_memory_db):
    """同一股票同一天同一指标类型唯一"""
    i1 = Indicator(
        code="600519",
        trade_date=date(2026, 5, 12),
        indicator_type="MA",
        indicator_value={"ma5": 1820.5},
    )
    in_memory_db.add(i1)
    in_memory_db.commit()
    
    i2 = Indicator(
        code="600519",
        trade_date=date(2026, 5, 12),
        indicator_type="MA",
        indicator_value={"ma5": 9999.0},
    )
    in_memory_db.add(i2)
    with pytest.raises(Exception):
        in_memory_db.commit()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_models.py -v`
Expected: FAIL（`app.models.indicator` 不存在）

- [ ] **Step 3: 实现 `backend/app/models/indicator.py`**

```python
from datetime import date, datetime
from typing import Any

from sqlalchemy import BigInteger, Date, DateTime, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.database import Base


class Indicator(Base):
    """技术指标缓存表"""
    
    __tablename__ = "indicators"
    __table_args__ = (
        UniqueConstraint(
            "code", "trade_date", "indicator_type",
            name="uq_indicators_code_date_type",
        ),
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    indicator_type: Mapped[str] = mapped_column(String(20), nullable=False)
    indicator_value: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    def __repr__(self) -> str:
        return (
            f"<Indicator(code={self.code!r}, date={self.trade_date}, "
            f"type={self.indicator_type!r})>"
        )
```

- [ ] **Step 4: 更新 `backend/app/models/__init__.py`**

```python
from app.models.indicator import Indicator
from app.models.quote import DailyQuote
from app.models.stock import Stock

__all__ = ["Stock", "DailyQuote", "Indicator"]
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest backend/tests/test_models.py -v`
Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/models/__init__.py backend/app/models/indicator.py backend/tests/test_models.py
git commit -m "feat(models): add Indicator model with JSON value storage"
```

---

### Task 8: 创建数据库初始化 CLI 命令

**Files:**
- Create: `backend/app/cli.py`
- Create: `backend/tests/test_cli.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_cli.py`**

```python
from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_cli_has_version():
    """CLI 应该显示版本"""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_db_init_command_exists():
    """db init 命令应该存在"""
    result = runner.invoke(app, ["db", "init", "--help"])
    assert result.exit_code == 0
    assert "创建所有数据库表" in result.stdout


def test_db_drop_command_exists():
    """db drop 命令应该存在（需要确认）"""
    result = runner.invoke(app, ["db", "drop", "--help"])
    assert result.exit_code == 0
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_cli.py -v`
Expected: FAIL（`app.cli` 不存在）

- [ ] **Step 3: 实现 `backend/app/cli.py`**

```python
import typer
from loguru import logger
from rich.console import Console

from app.database import Base, engine
from app.models import DailyQuote, Indicator, Stock  # 注册模型  # noqa: F401

app = typer.Typer(help="Alpha Seeker CLI")
db_app = typer.Typer(help="数据库操作")
app.add_typer(db_app, name="db")

console = Console()

__version__ = "0.1.0"


def version_callback(value: bool) -> None:
    if value:
        console.print(f"Alpha Seeker v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v",
        callback=version_callback,
        help="显示版本信息",
    ),
) -> None:
    pass


@db_app.command("init")
def db_init() -> None:
    """创建所有数据库表"""
    logger.info("创建数据库表...")
    Base.metadata.create_all(engine)
    console.print("[green]✓[/green] 数据库表创建完成")


@db_app.command("drop")
def db_drop(
    confirm: bool = typer.Option(
        False, "--yes", "-y",
        help="跳过确认提示",
    ),
) -> None:
    """删除所有数据库表（危险操作）"""
    if not confirm:
        typer.confirm("确定要删除所有表吗？此操作不可逆！", abort=True)
    logger.warning("删除所有数据库表...")
    Base.metadata.drop_all(engine)
    console.print("[yellow]✓[/yellow] 所有表已删除")


if __name__ == "__main__":
    app()
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_cli.py -v`
Expected: 3 passed

- [ ] **Step 5: 手动验证数据库初始化**

Run:
```bash
pip install -e ".[dev]"
alpha-seeker db init
```

Expected: `✓ 数据库表创建完成`

验证表是否创建：
```bash
docker exec alpha-seeker-postgres psql -U alpha_seeker -d alpha_seeker -c "\dt"
```

Expected: 列出 `stocks`, `daily_quotes`, `indicators` 三张表

- [ ] **Step 6: Commit**

```bash
git add backend/app/cli.py backend/tests/test_cli.py
git commit -m "feat(cli): add db init/drop commands"
```

---

### Task 9: 实现 AKShare 股票列表抓取

**Files:**
- Create: `backend/app/data/__init__.py`
- Create: `backend/app/data/fetcher.py`
- Create: `backend/tests/test_fetcher.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_fetcher.py`**

```python
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from app.data.fetcher import AKShareFetcher, StockInfo, StockQuote


def test_stock_info_dataclass():
    """StockInfo 应该是一个带基础字段的数据类"""
    info = StockInfo(
        code="600519",
        name="贵州茅台",
        industry="食品饮料",
        sector="主板",
        list_date=date(2001, 8, 27),
    )
    assert info.code == "600519"
    assert info.name == "贵州茅台"


def test_stock_quote_dataclass():
    """StockQuote 应该是一个带 OHLCV 字段的数据类"""
    quote = StockQuote(
        code="600519",
        trade_date=date(2026, 5, 12),
        open=Decimal("1800.00"),
        close=Decimal("1850.00"),
        high=Decimal("1860.00"),
        low=Decimal("1795.00"),
        volume=1000000,
        amount=Decimal("1850000000.00"),
    )
    assert quote.close == Decimal("1850.00")


def test_fetch_stock_list_parses_dataframe():
    """fetch_stock_list 应该把 AKShare DataFrame 转为 StockInfo 列表"""
    fake_df = pd.DataFrame([
        {"code": "600519", "name": "贵州茅台"},
        {"code": "000001", "name": "平安银行"},
    ])
    with patch("app.data.fetcher.ak.stock_info_a_code_name", return_value=fake_df):
        fetcher = AKShareFetcher()
        stocks = fetcher.fetch_stock_list()
        assert len(stocks) == 2
        assert stocks[0].code == "600519"
        assert stocks[0].name == "贵州茅台"
        assert stocks[1].code == "000001"


def test_fetch_stock_list_handles_empty_response():
    """AKShare 返回空 DataFrame 时应返回空列表"""
    with patch("app.data.fetcher.ak.stock_info_a_code_name", return_value=pd.DataFrame()):
        fetcher = AKShareFetcher()
        stocks = fetcher.fetch_stock_list()
        assert stocks == []


def test_fetch_stock_list_retries_on_failure():
    """网络失败时应重试"""
    mock_fn = MagicMock(side_effect=[
        ConnectionError("network error"),
        pd.DataFrame([{"code": "600519", "name": "贵州茅台"}]),
    ])
    with patch("app.data.fetcher.ak.stock_info_a_code_name", mock_fn):
        fetcher = AKShareFetcher(max_retries=2, retry_delay=0)
        stocks = fetcher.fetch_stock_list()
        assert len(stocks) == 1
        assert mock_fn.call_count == 2


def test_fetch_stock_list_raises_after_max_retries():
    """重试次数耗尽后应抛出异常"""
    with patch(
        "app.data.fetcher.ak.stock_info_a_code_name",
        side_effect=ConnectionError("persistent error"),
    ):
        fetcher = AKShareFetcher(max_retries=2, retry_delay=0)
        with pytest.raises(ConnectionError):
            fetcher.fetch_stock_list()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_fetcher.py -v`
Expected: FAIL（`app.data.fetcher` 不存在）

- [ ] **Step 3: 实现 `backend/app/data/__init__.py`**

```python
```

（空文件即可）

- [ ] **Step 4: 实现 `backend/app/data/fetcher.py`**

```python
import time
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import akshare as ak
import pandas as pd
from loguru import logger


@dataclass
class StockInfo:
    """股票基本信息"""
    code: str
    name: str
    industry: str | None = None
    sector: str | None = None
    list_date: date | None = None


@dataclass
class StockQuote:
    """股票日线行情"""
    code: str
    trade_date: date
    open: Decimal
    close: Decimal
    high: Decimal
    low: Decimal
    volume: int
    amount: Decimal


class AKShareFetcher:
    """AKShare 数据抓取器"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _retry(self, func, *args, **kwargs):
        """带重试的调用"""
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    f"AKShare 调用失败（第 {attempt}/{self.max_retries} 次）: {exc}"
                )
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
        assert last_exc is not None
        raise last_exc
    
    def fetch_stock_list(self) -> list[StockInfo]:
        """抓取 A 股股票列表"""
        logger.info("抓取 A 股股票列表...")
        df: pd.DataFrame = self._retry(ak.stock_info_a_code_name)
        if df.empty:
            logger.warning("AKShare 返回空列表")
            return []
        
        stocks = [
            StockInfo(code=str(row["code"]), name=str(row["name"]))
            for _, row in df.iterrows()
        ]
        logger.info(f"抓取到 {len(stocks)} 只股票")
        return stocks
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest backend/tests/test_fetcher.py -v`
Expected: 6 passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/data/__init__.py backend/app/data/fetcher.py backend/tests/test_fetcher.py
git commit -m "feat(data): add AKShareFetcher with stock list fetch and retry"
```

---

### Task 10: 实现 AKShare 日线行情抓取

**Files:**
- Modify: `backend/app/data/fetcher.py`
- Modify: `backend/tests/test_fetcher.py`

- [ ] **Step 1: 追加失败测试到 `backend/tests/test_fetcher.py`**

在文件末尾追加：

```python
def test_fetch_daily_quotes_parses_dataframe():
    """fetch_daily_quotes 应该把 AKShare DataFrame 转为 StockQuote 列表"""
    fake_df = pd.DataFrame([
        {
            "日期": "2026-05-10",
            "开盘": 1800.00,
            "收盘": 1850.00,
            "最高": 1860.00,
            "最低": 1795.00,
            "成交量": 1000000,
            "成交额": 1850000000.00,
        },
        {
            "日期": "2026-05-11",
            "开盘": 1850.00,
            "收盘": 1880.00,
            "最高": 1890.00,
            "最低": 1840.00,
            "成交量": 1200000,
            "成交额": 2256000000.00,
        },
    ])
    with patch("app.data.fetcher.ak.stock_zh_a_hist", return_value=fake_df):
        fetcher = AKShareFetcher()
        quotes = fetcher.fetch_daily_quotes(
            code="600519",
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 11),
        )
        assert len(quotes) == 2
        assert quotes[0].code == "600519"
        assert quotes[0].trade_date == date(2026, 5, 10)
        assert quotes[0].close == Decimal("1850.00")
        assert quotes[1].volume == 1200000


def test_fetch_daily_quotes_empty_returns_empty_list():
    """无数据时返回空列表"""
    with patch("app.data.fetcher.ak.stock_zh_a_hist", return_value=pd.DataFrame()):
        fetcher = AKShareFetcher()
        quotes = fetcher.fetch_daily_quotes(
            code="600519",
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 11),
        )
        assert quotes == []


def test_fetch_daily_quotes_passes_formatted_dates():
    """调用 AKShare 时日期应格式化为 YYYYMMDD"""
    mock_fn = MagicMock(return_value=pd.DataFrame())
    with patch("app.data.fetcher.ak.stock_zh_a_hist", mock_fn):
        fetcher = AKShareFetcher()
        fetcher.fetch_daily_quotes(
            code="600519",
            start_date=date(2026, 5, 10),
            end_date=date(2026, 5, 11),
        )
        call_kwargs = mock_fn.call_args.kwargs
        assert call_kwargs["symbol"] == "600519"
        assert call_kwargs["start_date"] == "20260510"
        assert call_kwargs["end_date"] == "20260511"
        assert call_kwargs["adjust"] == "qfq"
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_fetcher.py::test_fetch_daily_quotes_parses_dataframe -v`
Expected: FAIL（`fetch_daily_quotes` 方法不存在）

- [ ] **Step 3: 扩展 `AKShareFetcher`，在类末尾追加方法**

在 `backend/app/data/fetcher.py` 的 `AKShareFetcher` 类末尾追加：

```python
    def fetch_daily_quotes(
        self,
        code: str,
        start_date: date,
        end_date: date,
    ) -> list[StockQuote]:
        """
        抓取指定股票在日期区间内的日线行情（前复权）
        
        Args:
            code: 股票代码（如 600519）
            start_date: 起始日期（包含）
            end_date: 结束日期（包含）
        """
        logger.info(
            f"抓取 {code} 日线行情: {start_date} ~ {end_date}"
        )
        df: pd.DataFrame = self._retry(
            ak.stock_zh_a_hist,
            symbol=code,
            period="daily",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust="qfq",
        )
        if df.empty:
            logger.warning(f"{code} 在 {start_date} ~ {end_date} 无数据")
            return []
        
        quotes: list[StockQuote] = []
        for _, row in df.iterrows():
            trade_date_str = str(row["日期"])
            quotes.append(
                StockQuote(
                    code=code,
                    trade_date=date.fromisoformat(trade_date_str[:10]),
                    open=Decimal(str(row["开盘"])),
                    close=Decimal(str(row["收盘"])),
                    high=Decimal(str(row["最高"])),
                    low=Decimal(str(row["最低"])),
                    volume=int(row["成交量"]),
                    amount=Decimal(str(row["成交额"])),
                )
            )
        logger.info(f"{code}: 抓取到 {len(quotes)} 条日线数据")
        return quotes
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_fetcher.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/data/fetcher.py backend/tests/test_fetcher.py
git commit -m "feat(data): add daily quotes fetch from AKShare"
```

---

### Task 11: 实现数据存储层（upsert 逻辑）

**Files:**
- Create: `backend/app/data/storage.py`
- Create: `backend/tests/test_storage.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_storage.py`**

```python
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.data.fetcher import StockInfo, StockQuote
from app.data.storage import DataStorage
from app.database import Base
from app.models import DailyQuote, Stock


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


def test_upsert_stocks_inserts_new_records(db_session):
    """新股票应该被插入"""
    storage = DataStorage(db_session)
    storage.upsert_stocks([
        StockInfo(code="600519", name="贵州茅台"),
        StockInfo(code="000001", name="平安银行"),
    ])
    
    count = db_session.query(Stock).count()
    assert count == 2


def test_upsert_stocks_updates_existing_records(db_session):
    """已存在股票应该被更新（name 变化）"""
    storage = DataStorage(db_session)
    storage.upsert_stocks([StockInfo(code="600519", name="旧名称")])
    storage.upsert_stocks([StockInfo(code="600519", name="贵州茅台")])
    
    stock = db_session.query(Stock).filter_by(code="600519").one()
    assert stock.name == "贵州茅台"
    assert db_session.query(Stock).count() == 1


def test_upsert_stocks_empty_list_is_noop(db_session):
    """空列表不应报错"""
    storage = DataStorage(db_session)
    storage.upsert_stocks([])
    assert db_session.query(Stock).count() == 0


def test_upsert_quotes_inserts_new_records(db_session):
    """新行情应该被插入"""
    storage = DataStorage(db_session)
    storage.upsert_quotes([
        StockQuote(
            code="600519",
            trade_date=date(2026, 5, 10),
            open=Decimal("1800.00"),
            close=Decimal("1850.00"),
            high=Decimal("1860.00"),
            low=Decimal("1795.00"),
            volume=1000000,
            amount=Decimal("1850000000.00"),
        ),
    ])
    assert db_session.query(DailyQuote).count() == 1


def test_upsert_quotes_updates_existing_records(db_session):
    """同 code+date 的行情应该被更新"""
    storage = DataStorage(db_session)
    q = StockQuote(
        code="600519",
        trade_date=date(2026, 5, 10),
        open=Decimal("1800.00"),
        close=Decimal("1850.00"),
        high=Decimal("1860.00"),
        low=Decimal("1795.00"),
        volume=1000000,
        amount=Decimal("1850000000.00"),
    )
    storage.upsert_quotes([q])
    
    q_updated = StockQuote(
        code="600519",
        trade_date=date(2026, 5, 10),
        open=Decimal("1800.00"),
        close=Decimal("9999.00"),
        high=Decimal("9999.00"),
        low=Decimal("1795.00"),
        volume=2000000,
        amount=Decimal("1850000000.00"),
    )
    storage.upsert_quotes([q_updated])
    
    records = db_session.query(DailyQuote).all()
    assert len(records) == 1
    assert records[0].close == Decimal("9999.00")
    assert records[0].volume == 2000000


def test_get_quotes_returns_sorted_by_date(db_session):
    """get_quotes 应按日期升序返回"""
    storage = DataStorage(db_session)
    storage.upsert_quotes([
        StockQuote(
            code="600519", trade_date=date(2026, 5, 11),
            open=Decimal("1850.00"), close=Decimal("1880.00"),
            high=Decimal("1890.00"), low=Decimal("1840.00"),
            volume=1200000, amount=Decimal("2256000000.00"),
        ),
        StockQuote(
            code="600519", trade_date=date(2026, 5, 10),
            open=Decimal("1800.00"), close=Decimal("1850.00"),
            high=Decimal("1860.00"), low=Decimal("1795.00"),
            volume=1000000, amount=Decimal("1850000000.00"),
        ),
    ])
    
    quotes = storage.get_quotes("600519", date(2026, 5, 10), date(2026, 5, 11))
    assert len(quotes) == 2
    assert quotes[0].trade_date == date(2026, 5, 10)
    assert quotes[1].trade_date == date(2026, 5, 11)


def test_get_quotes_respects_date_range(db_session):
    """get_quotes 应过滤日期区间"""
    storage = DataStorage(db_session)
    storage.upsert_quotes([
        StockQuote(
            code="600519", trade_date=d,
            open=Decimal("1800.00"), close=Decimal("1850.00"),
            high=Decimal("1860.00"), low=Decimal("1795.00"),
            volume=1000000, amount=Decimal("1.00"),
        )
        for d in [date(2026, 5, 1), date(2026, 5, 5), date(2026, 5, 10)]
    ])
    
    quotes = storage.get_quotes("600519", date(2026, 5, 3), date(2026, 5, 7))
    assert len(quotes) == 1
    assert quotes[0].trade_date == date(2026, 5, 5)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_storage.py -v`
Expected: FAIL（`app.data.storage` 不存在）

- [ ] **Step 3: 实现 `backend/app/data/storage.py`**

```python
from datetime import date

from loguru import logger
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.data.fetcher import StockInfo, StockQuote
from app.models import DailyQuote, Stock


class DataStorage:
    """数据存储层，实现 upsert 和查询"""
    
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def upsert_stocks(self, stocks: list[StockInfo]) -> None:
        """插入或更新股票基本信息"""
        if not stocks:
            return
        
        for info in stocks:
            existing = self.session.get(Stock, info.code)
            if existing is None:
                self.session.add(Stock(
                    code=info.code,
                    name=info.name,
                    industry=info.industry,
                    sector=info.sector,
                    list_date=info.list_date,
                ))
            else:
                existing.name = info.name
                if info.industry is not None:
                    existing.industry = info.industry
                if info.sector is not None:
                    existing.sector = info.sector
                if info.list_date is not None:
                    existing.list_date = info.list_date
        
        self.session.commit()
        logger.info(f"upsert {len(stocks)} 只股票")
    
    def upsert_quotes(self, quotes: list[StockQuote]) -> None:
        """插入或更新日线行情"""
        if not quotes:
            return
        
        for q in quotes:
            existing = (
                self.session.query(DailyQuote)
                .filter_by(code=q.code, trade_date=q.trade_date)
                .one_or_none()
            )
            if existing is None:
                self.session.add(DailyQuote(
                    code=q.code,
                    trade_date=q.trade_date,
                    open=q.open,
                    close=q.close,
                    high=q.high,
                    low=q.low,
                    volume=q.volume,
                    amount=q.amount,
                ))
            else:
                existing.open = q.open
                existing.close = q.close
                existing.high = q.high
                existing.low = q.low
                existing.volume = q.volume
                existing.amount = q.amount
        
        self.session.commit()
        logger.info(f"upsert {len(quotes)} 条行情")
    
    def get_quotes(
        self, code: str, start_date: date, end_date: date
    ) -> list[DailyQuote]:
        """查询指定股票在日期区间内的日线行情（按日期升序）"""
        return (
            self.session.query(DailyQuote)
            .filter(
                DailyQuote.code == code,
                DailyQuote.trade_date >= start_date,
                DailyQuote.trade_date <= end_date,
            )
            .order_by(DailyQuote.trade_date.asc())
            .all()
        )
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_storage.py -v`
Expected: 7 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/data/storage.py backend/tests/test_storage.py
git commit -m "feat(data): add DataStorage with upsert and query methods"
```

---

### Task 12: 添加数据抓取 CLI 命令

**Files:**
- Modify: `backend/app/cli.py`
- Modify: `backend/tests/test_cli.py`

- [ ] **Step 1: 追加失败测试到 `backend/tests/test_cli.py`**

在文件末尾追加：

```python
from unittest.mock import patch

from app.data.fetcher import StockInfo


def test_data_fetch_stocks_command_exists():
    """data fetch-stocks 命令应该存在"""
    result = runner.invoke(app, ["data", "fetch-stocks", "--help"])
    assert result.exit_code == 0


def test_data_fetch_stocks_calls_fetcher_and_storage():
    """data fetch-stocks 应该调用 fetcher 抓取然后写入 storage"""
    fake_stocks = [
        StockInfo(code="600519", name="贵州茅台"),
        StockInfo(code="000001", name="平安银行"),
    ]
    with patch(
        "app.cli.AKShareFetcher.fetch_stock_list",
        return_value=fake_stocks,
    ) as mock_fetch, patch(
        "app.cli.DataStorage.upsert_stocks"
    ) as mock_upsert:
        result = runner.invoke(app, ["data", "fetch-stocks"])
        assert result.exit_code == 0
        mock_fetch.assert_called_once()
        mock_upsert.assert_called_once_with(fake_stocks)


def test_data_fetch_quotes_command_exists():
    """data fetch-quotes 命令应该存在"""
    result = runner.invoke(app, ["data", "fetch-quotes", "--help"])
    assert result.exit_code == 0


def test_data_fetch_quotes_requires_code():
    """data fetch-quotes 应要求股票代码"""
    result = runner.invoke(app, ["data", "fetch-quotes"])
    assert result.exit_code != 0
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_cli.py -v`
Expected: 新增测试 FAIL（`data` 子命令不存在）

- [ ] **Step 3: 扩展 `backend/app/cli.py`**

在现有 `backend/app/cli.py` 末尾（`if __name__ == "__main__":` 前）追加：

```python
from datetime import date, timedelta

from app.data.fetcher import AKShareFetcher
from app.data.storage import DataStorage
from app.database import SessionLocal

data_app = typer.Typer(help="数据管理")
app.add_typer(data_app, name="data")


@data_app.command("fetch-stocks")
def data_fetch_stocks() -> None:
    """抓取 A 股股票列表并写入数据库"""
    fetcher = AKShareFetcher()
    stocks = fetcher.fetch_stock_list()
    
    with SessionLocal() as session:
        storage = DataStorage(session)
        storage.upsert_stocks(stocks)
    
    console.print(f"[green]✓[/green] 抓取并保存 {len(stocks)} 只股票")


@data_app.command("fetch-quotes")
def data_fetch_quotes(
    code: str = typer.Option(..., "--code", "-c", help="股票代码"),
    days: int = typer.Option(60, "--days", "-d", help="抓取最近多少天"),
) -> None:
    """抓取指定股票的日线行情"""
    end = date.today()
    start = end - timedelta(days=days)
    
    fetcher = AKShareFetcher()
    quotes = fetcher.fetch_daily_quotes(code=code, start_date=start, end_date=end)
    
    with SessionLocal() as session:
        storage = DataStorage(session)
        storage.upsert_quotes(quotes)
    
    console.print(
        f"[green]✓[/green] {code}: 抓取 {len(quotes)} 条行情 "
        f"（{start} ~ {end}）"
    )
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_cli.py -v`
Expected: 7 passed

- [ ] **Step 5: 手动验证（端到端）**

Run:
```bash
alpha-seeker data fetch-stocks
alpha-seeker data fetch-quotes --code 600519 --days 30
```

验证数据库：
```bash
docker exec alpha-seeker-postgres psql -U alpha_seeker -d alpha_seeker -c \
  "SELECT COUNT(*) FROM stocks; SELECT COUNT(*) FROM daily_quotes WHERE code='600519';"
```

Expected: stocks 表有数千条记录，daily_quotes 有约 20-30 条记录

- [ ] **Step 6: Commit**

```bash
git add backend/app/cli.py backend/tests/test_cli.py
git commit -m "feat(cli): add data fetch-stocks and fetch-quotes commands"
```

---

## 阶段 3：技术指标

### Task 13: 实现均线指标（MA）

**Files:**
- Create: `backend/app/indicators/__init__.py`
- Create: `backend/app/indicators/ma.py`
- Create: `backend/tests/test_indicators/__init__.py`
- Create: `backend/tests/test_indicators/test_ma.py`

- [ ] **Step 1: 创建目录并创建空 `__init__.py`**

```bash
mkdir -p backend/app/indicators backend/tests/test_indicators
touch backend/app/indicators/__init__.py backend/tests/test_indicators/__init__.py
```

- [ ] **Step 2: 编写失败测试 `backend/tests/test_indicators/test_ma.py`**

```python
import pandas as pd
import pytest

from app.indicators.ma import calculate_ma


def test_calculate_ma_returns_series():
    """calculate_ma 应返回 pd.Series"""
    prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    ma3 = calculate_ma(prices, period=3)
    assert isinstance(ma3, pd.Series)
    assert len(ma3) == 5


def test_calculate_ma_correct_values():
    """均线值应正确"""
    prices = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    ma3 = calculate_ma(prices, period=3)
    # 前两个为 NaN；第三个为 (10+11+12)/3 = 11.0
    assert pd.isna(ma3.iloc[0])
    assert pd.isna(ma3.iloc[1])
    assert ma3.iloc[2] == pytest.approx(11.0)
    assert ma3.iloc[3] == pytest.approx(12.0)
    assert ma3.iloc[4] == pytest.approx(13.0)


def test_calculate_ma_raises_on_invalid_period():
    """period <= 0 应抛出 ValueError"""
    prices = pd.Series([10.0, 11.0, 12.0])
    with pytest.raises(ValueError):
        calculate_ma(prices, period=0)
    with pytest.raises(ValueError):
        calculate_ma(prices, period=-1)


def test_calculate_ma_on_empty_series():
    """空序列应返回空序列"""
    result = calculate_ma(pd.Series([], dtype=float), period=3)
    assert len(result) == 0
```

- [ ] **Step 3: 运行测试验证失败**

Run: `pytest backend/tests/test_indicators/test_ma.py -v`
Expected: FAIL

- [ ] **Step 4: 实现 `backend/app/indicators/ma.py`**

```python
import pandas as pd


def calculate_ma(prices: pd.Series, period: int) -> pd.Series:
    """
    计算简单移动平均（SMA）
    
    Args:
        prices: 收盘价序列
        period: 周期（如 5、20、60）
    
    Returns:
        与输入等长的均线序列，前 period-1 个值为 NaN
    """
    if period <= 0:
        raise ValueError(f"period 必须 > 0，当前 period={period}")
    return prices.rolling(window=period, min_periods=period).mean()
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest backend/tests/test_indicators/test_ma.py -v`
Expected: 4 passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/indicators/__init__.py backend/app/indicators/ma.py backend/tests/test_indicators/__init__.py backend/tests/test_indicators/test_ma.py
git commit -m "feat(indicators): add moving average (MA) calculation"
```

---

### Task 14: 实现 MACD 指标

**Files:**
- Create: `backend/app/indicators/macd.py`
- Create: `backend/tests/test_indicators/test_macd.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_indicators/test_macd.py`**

```python
import pandas as pd
import pytest

from app.indicators.macd import MACDResult, calculate_macd


def test_calculate_macd_returns_result():
    """calculate_macd 应返回 MACDResult"""
    prices = pd.Series([float(i) for i in range(1, 51)])
    result = calculate_macd(prices)
    assert isinstance(result, MACDResult)
    assert len(result.dif) == 50
    assert len(result.dea) == 50
    assert len(result.histogram) == 50


def test_macd_result_has_expected_columns():
    """MACDResult 应包含 dif, dea, histogram 三个 Series"""
    prices = pd.Series([float(i) for i in range(1, 51)])
    result = calculate_macd(prices, fast=12, slow=26, signal=9)
    assert result.dif is not None
    assert result.dea is not None
    assert result.histogram is not None


def test_macd_histogram_equals_2x_dif_minus_dea():
    """histogram = 2 * (dif - dea)，A 股约定"""
    prices = pd.Series([float(i) for i in range(1, 51)])
    result = calculate_macd(prices)
    
    # 取最后一个非 NaN 的值验证
    last_idx = len(prices) - 1
    expected_hist = 2 * (result.dif.iloc[last_idx] - result.dea.iloc[last_idx])
    assert result.histogram.iloc[last_idx] == pytest.approx(expected_hist)


def test_calculate_macd_invalid_periods():
    """非法周期应抛出 ValueError"""
    prices = pd.Series([float(i) for i in range(1, 51)])
    with pytest.raises(ValueError):
        calculate_macd(prices, fast=0, slow=26, signal=9)
    with pytest.raises(ValueError):
        calculate_macd(prices, fast=26, slow=12, signal=9)  # fast >= slow
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_indicators/test_macd.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 `backend/app/indicators/macd.py`**

```python
from dataclasses import dataclass

import pandas as pd


@dataclass
class MACDResult:
    """MACD 计算结果"""
    dif: pd.Series       # 快线 EMA - 慢线 EMA
    dea: pd.Series       # DIF 的 signal 周期 EMA
    histogram: pd.Series # 2 * (DIF - DEA)，A 股约定


def calculate_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> MACDResult:
    """
    计算 MACD 指标（A 股约定）
    
    Args:
        prices: 收盘价序列
        fast: 快线 EMA 周期（默认 12）
        slow: 慢线 EMA 周期（默认 26）
        signal: DEA 的 EMA 周期（默认 9）
    """
    if fast <= 0 or slow <= 0 or signal <= 0:
        raise ValueError(
            f"fast/slow/signal 必须 > 0，当前 fast={fast}, slow={slow}, signal={signal}"
        )
    if fast >= slow:
        raise ValueError(f"fast({fast}) 必须 < slow({slow})")
    
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    histogram = 2 * (dif - dea)
    
    return MACDResult(dif=dif, dea=dea, histogram=histogram)
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_indicators/test_macd.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/indicators/macd.py backend/tests/test_indicators/test_macd.py
git commit -m "feat(indicators): add MACD calculation"
```

---

### Task 15: 实现 RSI 指标

**Files:**
- Create: `backend/app/indicators/rsi.py`
- Create: `backend/tests/test_indicators/test_rsi.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_indicators/test_rsi.py`**

```python
import pandas as pd
import pytest

from app.indicators.rsi import calculate_rsi


def test_calculate_rsi_returns_series():
    """calculate_rsi 应返回 pd.Series"""
    prices = pd.Series([float(i) for i in range(1, 51)])
    rsi = calculate_rsi(prices, period=14)
    assert isinstance(rsi, pd.Series)
    assert len(rsi) == 50


def test_rsi_values_in_0_to_100_range():
    """RSI 值应在 [0, 100] 之间"""
    prices = pd.Series([100 + (i % 7) - 3 for i in range(100)], dtype=float)
    rsi = calculate_rsi(prices, period=14)
    valid = rsi.dropna()
    assert (valid >= 0).all()
    assert (valid <= 100).all()


def test_rsi_all_rising_prices_gives_high_rsi():
    """持续上涨的价格 RSI 应接近 100"""
    prices = pd.Series([float(i) for i in range(1, 51)])
    rsi = calculate_rsi(prices, period=14)
    assert rsi.iloc[-1] == pytest.approx(100.0, abs=0.1)


def test_rsi_all_falling_prices_gives_low_rsi():
    """持续下跌的价格 RSI 应接近 0"""
    prices = pd.Series([float(50 - i) for i in range(50)])
    rsi = calculate_rsi(prices, period=14)
    assert rsi.iloc[-1] == pytest.approx(0.0, abs=0.1)


def test_rsi_invalid_period():
    """period <= 0 应抛出 ValueError"""
    prices = pd.Series([float(i) for i in range(1, 20)])
    with pytest.raises(ValueError):
        calculate_rsi(prices, period=0)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_indicators/test_rsi.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 `backend/app/indicators/rsi.py`**

```python
import pandas as pd


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    计算相对强弱指数（RSI）- 使用 Wilder 平滑
    
    Args:
        prices: 收盘价序列
        period: 周期（默认 14）
    
    Returns:
        RSI 序列，前 period 个值为 NaN，取值范围 [0, 100]
    """
    if period <= 0:
        raise ValueError(f"period 必须 > 0，当前 period={period}")
    
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)
    
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    
    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    # 全涨（avg_loss=0）时 RSI = 100
    rsi = rsi.where(avg_loss != 0, 100.0)
    # 全跌（avg_gain=0）时 RSI = 0
    rsi = rsi.where(avg_gain != 0, 0.0)
    return rsi
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_indicators/test_rsi.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/indicators/rsi.py backend/tests/test_indicators/test_rsi.py
git commit -m "feat(indicators): add RSI calculation with Wilder smoothing"
```

---

## 阶段 4：策略引擎

### Task 16: 实现策略基类和注册器

**Files:**
- Create: `backend/app/strategies/__init__.py`
- Create: `backend/app/strategies/base.py`
- Create: `backend/tests/test_strategies/__init__.py`
- Create: `backend/tests/test_strategies/test_base.py`

- [ ] **Step 1: 创建目录和空 `__init__.py`**

```bash
mkdir -p backend/app/strategies backend/tests/test_strategies
touch backend/app/strategies/__init__.py backend/tests/test_strategies/__init__.py
```

- [ ] **Step 2: 编写失败测试 `backend/tests/test_strategies/test_base.py`**

```python
from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from app.strategies.base import (
    BaseStrategy,
    Signal,
    StockData,
    StrategyRegistry,
    StrategyResult,
)


@pytest.fixture(autouse=True)
def clear_registry():
    """每个测试后清空注册器"""
    yield
    StrategyRegistry._strategies.clear()


def test_signal_enum_values():
    """Signal 应有 BUY/SELL/HOLD 三个值"""
    assert Signal.BUY.value == "buy"
    assert Signal.SELL.value == "sell"
    assert Signal.HOLD.value == "hold"


def test_stock_data_wraps_dataframe():
    """StockData 应包含 code 和价格 DataFrame"""
    df = pd.DataFrame({
        "trade_date": [date(2026, 5, 10)],
        "open": [100.0],
        "close": [105.0],
        "high": [106.0],
        "low": [99.0],
        "volume": [1000],
    })
    sd = StockData(code="600519", prices=df)
    assert sd.code == "600519"
    assert len(sd.prices) == 1


def test_strategy_result_contains_fields():
    """StrategyResult 应包含 signal, score, reason"""
    r = StrategyResult(signal=Signal.BUY, score=80.0, reason="金叉")
    assert r.signal == Signal.BUY
    assert r.score == 80.0
    assert r.reason == "金叉"


def test_base_strategy_is_abstract():
    """BaseStrategy 应无法直接实例化"""
    with pytest.raises(TypeError):
        BaseStrategy()


def test_strategy_registry_register_and_get():
    """可以注册并按名称获取策略"""
    class FakeStrategy(BaseStrategy):
        name = "fake"
        
        def analyze(self, data: StockData) -> StrategyResult:
            return StrategyResult(signal=Signal.HOLD, score=50.0, reason="fake")
    
    StrategyRegistry.register(FakeStrategy())
    s = StrategyRegistry.get("fake")
    assert isinstance(s, FakeStrategy)


def test_strategy_registry_get_all():
    """get_all 应返回已注册的全部策略"""
    class A(BaseStrategy):
        name = "a"
        def analyze(self, data: StockData) -> StrategyResult:
            return StrategyResult(Signal.HOLD, 0, "")
    
    class B(BaseStrategy):
        name = "b"
        def analyze(self, data: StockData) -> StrategyResult:
            return StrategyResult(Signal.HOLD, 0, "")
    
    StrategyRegistry.register(A())
    StrategyRegistry.register(B())
    all_ = StrategyRegistry.get_all()
    assert len(all_) == 2


def test_strategy_registry_unknown_name_returns_none():
    """未注册的名称应返回 None"""
    assert StrategyRegistry.get("nonexistent") is None
```

- [ ] **Step 3: 运行测试验证失败**

Run: `pytest backend/tests/test_strategies/test_base.py -v`
Expected: FAIL

- [ ] **Step 4: 实现 `backend/app/strategies/base.py`**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar

import pandas as pd


class Signal(Enum):
    """买卖信号"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class StockData:
    """策略输入：股票的价量数据
    
    prices 应包含列：trade_date, open, close, high, low, volume
    按 trade_date 升序排列（最近的数据在最后）
    """
    code: str
    prices: pd.DataFrame


@dataclass
class StrategyResult:
    """策略输出：信号、评分、理由"""
    signal: Signal
    score: float  # 0-100
    reason: str


class BaseStrategy(ABC):
    """策略基类
    
    子类必须：
    - 设置 name 类属性（策略唯一标识）
    - 实现 analyze 方法
    """
    
    name: ClassVar[str] = ""
    
    @abstractmethod
    def analyze(self, data: StockData) -> StrategyResult:
        """分析股票数据，返回信号、评分和理由"""
        raise NotImplementedError


class StrategyRegistry:
    """策略注册和查找"""
    
    _strategies: ClassVar[dict[str, BaseStrategy]] = {}
    
    @classmethod
    def register(cls, strategy: BaseStrategy) -> None:
        if not strategy.name:
            raise ValueError("策略必须设置非空的 name")
        cls._strategies[strategy.name] = strategy
    
    @classmethod
    def get(cls, name: str) -> BaseStrategy | None:
        return cls._strategies.get(name)
    
    @classmethod
    def get_all(cls) -> list[BaseStrategy]:
        return list(cls._strategies.values())
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest backend/tests/test_strategies/test_base.py -v`
Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add backend/app/strategies/__init__.py backend/app/strategies/base.py backend/tests/test_strategies/__init__.py backend/tests/test_strategies/test_base.py
git commit -m "feat(strategies): add BaseStrategy, Signal, StockData and StrategyRegistry"
```

---

### Task 17: 实现双均线策略

**Files:**
- Create: `backend/app/strategies/dual_ma.py`
- Create: `backend/tests/test_strategies/test_dual_ma.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_strategies/test_dual_ma.py`**

```python
from datetime import date, timedelta

import pandas as pd
import pytest

from app.strategies.base import Signal, StockData
from app.strategies.dual_ma import DualMAStrategy


def _make_stock_data(code: str, closes: list[float]) -> StockData:
    start = date(2026, 1, 1)
    df = pd.DataFrame({
        "trade_date": [start + timedelta(days=i) for i in range(len(closes))],
        "open": closes,
        "close": closes,
        "high": closes,
        "low": closes,
        "volume": [1000] * len(closes),
    })
    return StockData(code=code, prices=df)


def test_dual_ma_name():
    assert DualMAStrategy().name == "dual_ma"


def test_golden_cross_generates_buy_signal():
    """短均线上穿长均线 → BUY"""
    # 先下跌再上涨，制造金叉
    closes = [100 - i * 0.5 for i in range(30)] + [85 + i * 1.5 for i in range(30)]
    data = _make_stock_data("600519", closes)
    
    strategy = DualMAStrategy(short_period=5, long_period=20)
    result = strategy.analyze(data)
    
    assert result.signal == Signal.BUY
    assert "金叉" in result.reason
    assert 50 < result.score <= 100


def test_death_cross_generates_sell_signal():
    """短均线下穿长均线 → SELL"""
    closes = [100 + i * 1.5 for i in range(30)] + [145 - i * 2 for i in range(30)]
    data = _make_stock_data("600519", closes)
    
    strategy = DualMAStrategy(short_period=5, long_period=20)
    result = strategy.analyze(data)
    
    assert result.signal == Signal.SELL
    assert "死叉" in result.reason


def test_hold_signal_when_no_cross():
    """没有交叉时 → HOLD"""
    closes = [100.0] * 40
    data = _make_stock_data("600519", closes)
    
    strategy = DualMAStrategy(short_period=5, long_period=20)
    result = strategy.analyze(data)
    
    assert result.signal == Signal.HOLD


def test_insufficient_data_returns_hold():
    """数据少于长周期时返回 HOLD"""
    data = _make_stock_data("600519", [100.0] * 5)
    strategy = DualMAStrategy(short_period=5, long_period=20)
    result = strategy.analyze(data)
    assert result.signal == Signal.HOLD
    assert "数据不足" in result.reason


def test_invalid_periods():
    """short >= long 应抛出 ValueError"""
    with pytest.raises(ValueError):
        DualMAStrategy(short_period=20, long_period=5)
    with pytest.raises(ValueError):
        DualMAStrategy(short_period=0, long_period=20)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_strategies/test_dual_ma.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 `backend/app/strategies/dual_ma.py`**

```python
from app.indicators.ma import calculate_ma
from app.strategies.base import BaseStrategy, Signal, StockData, StrategyResult


class DualMAStrategy(BaseStrategy):
    """双均线策略
    
    - 短期均线上穿长期均线 → BUY
    - 短期均线下穿长期均线 → SELL
    - 其他情况 → HOLD
    """
    
    name = "dual_ma"
    
    def __init__(self, short_period: int = 5, long_period: int = 20) -> None:
        if short_period <= 0 or long_period <= 0:
            raise ValueError(
                f"周期必须 > 0，当前 short={short_period}, long={long_period}"
            )
        if short_period >= long_period:
            raise ValueError(
                f"short_period({short_period}) 必须 < long_period({long_period})"
            )
        self.short_period = short_period
        self.long_period = long_period
    
    def analyze(self, data: StockData) -> StrategyResult:
        closes = data.prices["close"].astype(float)
        
        if len(closes) < self.long_period + 1:
            return StrategyResult(
                signal=Signal.HOLD,
                score=50.0,
                reason=f"数据不足：需要至少 {self.long_period + 1} 条，当前 {len(closes)}",
            )
        
        ma_short = calculate_ma(closes, self.short_period)
        ma_long = calculate_ma(closes, self.long_period)
        
        prev_short = ma_short.iloc[-2]
        prev_long = ma_long.iloc[-2]
        curr_short = ma_short.iloc[-1]
        curr_long = ma_long.iloc[-1]
        
        # 金叉：昨日 short <= long 且 今日 short > long
        if prev_short <= prev_long and curr_short > curr_long:
            diff_pct = (curr_short - curr_long) / curr_long * 100
            return StrategyResult(
                signal=Signal.BUY,
                score=min(100.0, 60.0 + diff_pct * 10),
                reason=(
                    f"MA{self.short_period} 上穿 MA{self.long_period} "
                    f"金叉（差距 {diff_pct:.2f}%）"
                ),
            )
        
        # 死叉：昨日 short >= long 且 今日 short < long
        if prev_short >= prev_long and curr_short < curr_long:
            diff_pct = (curr_long - curr_short) / curr_long * 100
            return StrategyResult(
                signal=Signal.SELL,
                score=max(0.0, 40.0 - diff_pct * 10),
                reason=(
                    f"MA{self.short_period} 下穿 MA{self.long_period} "
                    f"死叉（差距 {diff_pct:.2f}%）"
                ),
            )
        
        # 无交叉，根据多空排列给分
        if curr_short > curr_long:
            score = 60.0
            reason = f"多头排列（MA{self.short_period} > MA{self.long_period}）"
        else:
            score = 40.0
            reason = f"空头排列（MA{self.short_period} < MA{self.long_period}）"
        
        return StrategyResult(signal=Signal.HOLD, score=score, reason=reason)
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_strategies/test_dual_ma.py -v`
Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/strategies/dual_ma.py backend/tests/test_strategies/test_dual_ma.py
git commit -m "feat(strategies): add dual moving average crossover strategy"
```

---

### Task 18: 实现 MACD 策略

**Files:**
- Create: `backend/app/strategies/macd_strategy.py`
- Create: `backend/tests/test_strategies/test_macd_strategy.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_strategies/test_macd_strategy.py`**

```python
from datetime import date, timedelta

import pandas as pd
import pytest

from app.strategies.base import Signal, StockData
from app.strategies.macd_strategy import MACDStrategy


def _make_data(closes: list[float]) -> StockData:
    start = date(2026, 1, 1)
    df = pd.DataFrame({
        "trade_date": [start + timedelta(days=i) for i in range(len(closes))],
        "open": closes,
        "close": closes,
        "high": closes,
        "low": closes,
        "volume": [1000] * len(closes),
    })
    return StockData(code="TEST", prices=df)


def test_macd_strategy_name():
    assert MACDStrategy().name == "macd"


def test_macd_golden_cross_buy():
    """DIF 上穿 DEA → BUY"""
    closes = [100 - i * 0.3 for i in range(40)] + [88 + i * 0.8 for i in range(30)]
    data = _make_data(closes)
    
    strategy = MACDStrategy()
    result = strategy.analyze(data)
    assert result.signal == Signal.BUY
    assert "金叉" in result.reason


def test_macd_death_cross_sell():
    """DIF 下穿 DEA → SELL"""
    closes = [100 + i * 0.8 for i in range(40)] + [132 - i * 0.6 for i in range(30)]
    data = _make_data(closes)
    
    strategy = MACDStrategy()
    result = strategy.analyze(data)
    assert result.signal == Signal.SELL
    assert "死叉" in result.reason


def test_macd_insufficient_data_returns_hold():
    """数据少于 slow + signal 时返回 HOLD"""
    data = _make_data([100.0] * 10)
    strategy = MACDStrategy()
    result = strategy.analyze(data)
    assert result.signal == Signal.HOLD
    assert "数据不足" in result.reason
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_strategies/test_macd_strategy.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 `backend/app/strategies/macd_strategy.py`**

```python
from app.indicators.macd import calculate_macd
from app.strategies.base import BaseStrategy, Signal, StockData, StrategyResult


class MACDStrategy(BaseStrategy):
    """MACD 策略
    
    - DIF 上穿 DEA（金叉）→ BUY
    - DIF 下穿 DEA（死叉）→ SELL
    - 其他 → HOLD
    """
    
    name = "macd"
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9) -> None:
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def analyze(self, data: StockData) -> StrategyResult:
        closes = data.prices["close"].astype(float)
        min_required = self.slow + self.signal + 1
        
        if len(closes) < min_required:
            return StrategyResult(
                signal=Signal.HOLD,
                score=50.0,
                reason=f"数据不足：需要至少 {min_required} 条，当前 {len(closes)}",
            )
        
        result = calculate_macd(closes, self.fast, self.slow, self.signal)
        prev_dif = result.dif.iloc[-2]
        prev_dea = result.dea.iloc[-2]
        curr_dif = result.dif.iloc[-1]
        curr_dea = result.dea.iloc[-1]
        curr_hist = result.histogram.iloc[-1]
        
        if prev_dif <= prev_dea and curr_dif > curr_dea:
            score = min(100.0, 65.0 + abs(curr_hist))
            return StrategyResult(
                signal=Signal.BUY,
                score=score,
                reason=f"MACD 金叉（DIF={curr_dif:.3f}, DEA={curr_dea:.3f}）",
            )
        
        if prev_dif >= prev_dea and curr_dif < curr_dea:
            score = max(0.0, 35.0 - abs(curr_hist))
            return StrategyResult(
                signal=Signal.SELL,
                score=score,
                reason=f"MACD 死叉（DIF={curr_dif:.3f}, DEA={curr_dea:.3f}）",
            )
        
        if curr_dif > curr_dea:
            return StrategyResult(
                signal=Signal.HOLD,
                score=60.0,
                reason=f"MACD 多头持续（柱={curr_hist:.3f}）",
            )
        
        return StrategyResult(
            signal=Signal.HOLD,
            score=40.0,
            reason=f"MACD 空头持续（柱={curr_hist:.3f}）",
        )
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_strategies/test_macd_strategy.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/strategies/macd_strategy.py backend/tests/test_strategies/test_macd_strategy.py
git commit -m "feat(strategies): add MACD crossover strategy"
```

---

### Task 19: 实现 RSI 超买超卖策略

**Files:**
- Create: `backend/app/strategies/rsi_strategy.py`
- Create: `backend/tests/test_strategies/test_rsi_strategy.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_strategies/test_rsi_strategy.py`**

```python
from datetime import date, timedelta

import pandas as pd

from app.strategies.base import Signal, StockData
from app.strategies.rsi_strategy import RSIStrategy


def _make_data(closes: list[float]) -> StockData:
    start = date(2026, 1, 1)
    df = pd.DataFrame({
        "trade_date": [start + timedelta(days=i) for i in range(len(closes))],
        "open": closes,
        "close": closes,
        "high": closes,
        "low": closes,
        "volume": [1000] * len(closes),
    })
    return StockData(code="TEST", prices=df)


def test_rsi_strategy_name():
    assert RSIStrategy().name == "rsi"


def test_rsi_oversold_buy():
    """RSI < 30 → 超卖，BUY"""
    # 持续下跌，RSI 会 → 0
    closes = [float(100 - i) for i in range(50)]
    data = _make_data(closes)
    
    strategy = RSIStrategy()
    result = strategy.analyze(data)
    assert result.signal == Signal.BUY
    assert "超卖" in result.reason


def test_rsi_overbought_sell():
    """RSI > 70 → 超买，SELL"""
    closes = [float(i) for i in range(1, 51)]
    data = _make_data(closes)
    
    strategy = RSIStrategy()
    result = strategy.analyze(data)
    assert result.signal == Signal.SELL
    assert "超买" in result.reason


def test_rsi_neutral_hold():
    """RSI 在 30-70 之间 → HOLD"""
    # 价格在窄幅震荡
    closes = [100 + (i % 4 - 1.5) for i in range(50)]
    data = _make_data(closes)
    
    strategy = RSIStrategy()
    result = strategy.analyze(data)
    assert result.signal == Signal.HOLD


def test_rsi_insufficient_data():
    """数据不足 → HOLD"""
    data = _make_data([100.0] * 5)
    strategy = RSIStrategy()
    result = strategy.analyze(data)
    assert result.signal == Signal.HOLD
    assert "数据不足" in result.reason
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_strategies/test_rsi_strategy.py -v`
Expected: FAIL

- [ ] **Step 3: 实现 `backend/app/strategies/rsi_strategy.py`**

```python
from app.indicators.rsi import calculate_rsi
from app.strategies.base import BaseStrategy, Signal, StockData, StrategyResult


class RSIStrategy(BaseStrategy):
    """RSI 超买超卖策略
    
    - RSI < oversold_threshold → 超卖，BUY
    - RSI > overbought_threshold → 超买，SELL
    - 其他 → HOLD
    """
    
    name = "rsi"
    
    def __init__(
        self,
        period: int = 14,
        oversold_threshold: float = 30.0,
        overbought_threshold: float = 70.0,
    ) -> None:
        if oversold_threshold >= overbought_threshold:
            raise ValueError(
                f"oversold({oversold_threshold}) 必须 < overbought({overbought_threshold})"
            )
        self.period = period
        self.oversold = oversold_threshold
        self.overbought = overbought_threshold
    
    def analyze(self, data: StockData) -> StrategyResult:
        closes = data.prices["close"].astype(float)
        min_required = self.period + 2
        
        if len(closes) < min_required:
            return StrategyResult(
                signal=Signal.HOLD,
                score=50.0,
                reason=f"数据不足：需要至少 {min_required} 条，当前 {len(closes)}",
            )
        
        rsi = calculate_rsi(closes, self.period)
        curr_rsi = float(rsi.iloc[-1])
        
        if curr_rsi < self.oversold:
            # 越低分越高（越应该买）
            score = min(100.0, 70.0 + (self.oversold - curr_rsi))
            return StrategyResult(
                signal=Signal.BUY,
                score=score,
                reason=f"RSI={curr_rsi:.2f} 超卖（< {self.oversold}）",
            )
        
        if curr_rsi > self.overbought:
            # 越高分越低（越应该卖）
            score = max(0.0, 30.0 - (curr_rsi - self.overbought))
            return StrategyResult(
                signal=Signal.SELL,
                score=score,
                reason=f"RSI={curr_rsi:.2f} 超买（> {self.overbought}）",
            )
        
        # 中性区域：50 分为基准，越接近超卖越高分
        score = 50.0 + (50.0 - curr_rsi) * 0.3
        return StrategyResult(
            signal=Signal.HOLD,
            score=max(0.0, min(100.0, score)),
            reason=f"RSI={curr_rsi:.2f} 中性",
        )
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_strategies/test_rsi_strategy.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/strategies/rsi_strategy.py backend/tests/test_strategies/test_rsi_strategy.py
git commit -m "feat(strategies): add RSI oversold/overbought strategy"
```

---

### Task 20: 在 strategies 包中注册所有策略

**Files:**
- Modify: `backend/app/strategies/__init__.py`
- Create: `backend/tests/test_strategies/test_registration.py`

- [ ] **Step 1: 编写失败测试 `backend/tests/test_strategies/test_registration.py`**

```python
from app.strategies import register_builtin_strategies
from app.strategies.base import StrategyRegistry


def test_all_builtin_strategies_are_registered():
    """三个内置策略应该都被注册"""
    StrategyRegistry._strategies.clear()
    register_builtin_strategies()
    
    names = {s.name for s in StrategyRegistry.get_all()}
    assert names == {"dual_ma", "macd", "rsi"}


def test_register_is_idempotent():
    """重复调用不应重复注册"""
    StrategyRegistry._strategies.clear()
    register_builtin_strategies()
    register_builtin_strategies()
    
    assert len(StrategyRegistry.get_all()) == 3
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_strategies/test_registration.py -v`
Expected: FAIL

- [ ] **Step 3: 更新 `backend/app/strategies/__init__.py`**

```python
from app.strategies.base import (
    BaseStrategy,
    Signal,
    StockData,
    StrategyRegistry,
    StrategyResult,
)
from app.strategies.dual_ma import DualMAStrategy
from app.strategies.macd_strategy import MACDStrategy
from app.strategies.rsi_strategy import RSIStrategy


def register_builtin_strategies() -> None:
    """注册所有内置策略（幂等）"""
    for strategy_cls in [DualMAStrategy, MACDStrategy, RSIStrategy]:
        instance = strategy_cls()
        if StrategyRegistry.get(instance.name) is None:
            StrategyRegistry.register(instance)


__all__ = [
    "BaseStrategy",
    "Signal",
    "StockData",
    "StrategyResult",
    "StrategyRegistry",
    "DualMAStrategy",
    "MACDStrategy",
    "RSIStrategy",
    "register_builtin_strategies",
]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_strategies/test_registration.py -v`
Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/strategies/__init__.py backend/tests/test_strategies/test_registration.py
git commit -m "feat(strategies): add builtin strategy registration"
```

---

## 阶段 5：策略运行 CLI 和端到端集成

### Task 21: 实现 StockData 加载器（从数据库）

**Files:**
- Modify: `backend/app/data/storage.py`
- Modify: `backend/tests/test_storage.py`

- [ ] **Step 1: 追加失败测试到 `backend/tests/test_storage.py`**

在文件末尾追加：

```python
from app.strategies.base import StockData


def test_load_stock_data_returns_stock_data_object(db_session):
    """load_stock_data 应返回 StockData 对象"""
    storage = DataStorage(db_session)
    storage.upsert_quotes([
        StockQuote(
            code="600519", trade_date=date(2026, 5, 10),
            open=Decimal("1800.00"), close=Decimal("1850.00"),
            high=Decimal("1860.00"), low=Decimal("1795.00"),
            volume=1000000, amount=Decimal("1.0"),
        ),
        StockQuote(
            code="600519", trade_date=date(2026, 5, 11),
            open=Decimal("1850.00"), close=Decimal("1880.00"),
            high=Decimal("1890.00"), low=Decimal("1840.00"),
            volume=1200000, amount=Decimal("1.0"),
        ),
    ])
    
    data = storage.load_stock_data("600519", date(2026, 5, 10), date(2026, 5, 11))
    assert isinstance(data, StockData)
    assert data.code == "600519"
    assert len(data.prices) == 2
    assert list(data.prices.columns) == [
        "trade_date", "open", "close", "high", "low", "volume"
    ]
    assert data.prices["close"].iloc[-1] == 1880.00


def test_load_stock_data_empty_when_no_quotes(db_session):
    """无数据时返回空 DataFrame 的 StockData"""
    storage = DataStorage(db_session)
    data = storage.load_stock_data("NONE", date(2026, 5, 1), date(2026, 5, 30))
    assert data.code == "NONE"
    assert len(data.prices) == 0
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_storage.py::test_load_stock_data_returns_stock_data_object -v`
Expected: FAIL（`load_stock_data` 方法不存在）

- [ ] **Step 3: 在 `DataStorage` 类末尾追加方法**

在 `backend/app/data/storage.py` 的 `DataStorage` 类末尾追加：

```python
    def load_stock_data(
        self, code: str, start_date: date, end_date: date
    ) -> "StockData":  # noqa: F821
        """从数据库加载并构造 StockData 供策略使用"""
        from app.strategies.base import StockData
        import pandas as pd
        
        quotes = self.get_quotes(code, start_date, end_date)
        
        df = pd.DataFrame([
            {
                "trade_date": q.trade_date,
                "open": float(q.open),
                "close": float(q.close),
                "high": float(q.high),
                "low": float(q.low),
                "volume": int(q.volume),
            }
            for q in quotes
        ], columns=["trade_date", "open", "close", "high", "low", "volume"])
        
        return StockData(code=code, prices=df)
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_storage.py -v`
Expected: 9 passed

- [ ] **Step 5: Commit**

```bash
git add backend/app/data/storage.py backend/tests/test_storage.py
git commit -m "feat(data): add load_stock_data for strategy consumption"
```

---

### Task 22: 实现 strategy run CLI 命令

**Files:**
- Modify: `backend/app/cli.py`
- Modify: `backend/tests/test_cli.py`

- [ ] **Step 1: 追加失败测试到 `backend/tests/test_cli.py`**

在文件末尾追加：

```python
from datetime import date as date_cls
from decimal import Decimal
from unittest.mock import MagicMock

import pandas as pd

from app.strategies.base import Signal, StockData, StrategyResult


def test_strategy_run_command_exists():
    """strategy run 命令应该存在"""
    result = runner.invoke(app, ["strategy", "run", "--help"])
    assert result.exit_code == 0


def test_strategy_run_single_stock_prints_results():
    """strategy run --code 应输出三个策略的结果"""
    fake_data = StockData(
        code="600519",
        prices=pd.DataFrame({
            "trade_date": [date_cls(2026, 5, 1) + pd.Timedelta(days=i) for i in range(60)],
            "open": [100.0 + i for i in range(60)],
            "close": [100.0 + i for i in range(60)],
            "high": [100.5 + i for i in range(60)],
            "low": [99.5 + i for i in range(60)],
            "volume": [1000] * 60,
        }),
    )
    
    with patch("app.cli.SessionLocal") as mock_session_ctx:
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = False
        mock_session_ctx.return_value = mock_session
        
        with patch(
            "app.cli.DataStorage.load_stock_data",
            return_value=fake_data,
        ):
            result = runner.invoke(app, ["strategy", "run", "--code", "600519"])
            assert result.exit_code == 0
            assert "600519" in result.stdout
            assert "dual_ma" in result.stdout
            assert "macd" in result.stdout
            assert "rsi" in result.stdout


def test_strategy_list_command():
    """strategy list 应列出所有已注册策略"""
    result = runner.invoke(app, ["strategy", "list"])
    assert result.exit_code == 0
    assert "dual_ma" in result.stdout
    assert "macd" in result.stdout
    assert "rsi" in result.stdout
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest backend/tests/test_cli.py -v`
Expected: FAIL（`strategy` 子命令不存在）

- [ ] **Step 3: 扩展 `backend/app/cli.py`**

在现有文件末尾（`if __name__ == "__main__":` 前）追加：

```python
from rich.table import Table

from app.strategies import register_builtin_strategies
from app.strategies.base import StrategyRegistry

# 在模块加载时注册所有内置策略
register_builtin_strategies()

strategy_app = typer.Typer(help="策略管理")
app.add_typer(strategy_app, name="strategy")


@strategy_app.command("list")
def strategy_list() -> None:
    """列出所有已注册的策略"""
    table = Table(title="已注册策略")
    table.add_column("名称", style="cyan")
    table.add_column("类名", style="green")
    
    for s in StrategyRegistry.get_all():
        table.add_row(s.name, s.__class__.__name__)
    
    console.print(table)


@strategy_app.command("run")
def strategy_run(
    code: str = typer.Option(..., "--code", "-c", help="股票代码"),
    days: int = typer.Option(90, "--days", "-d", help="使用最近多少天数据"),
) -> None:
    """对指定股票运行所有已注册策略"""
    end = date.today()
    start = end - timedelta(days=days)
    
    with SessionLocal() as session:
        storage = DataStorage(session)
        data = storage.load_stock_data(code, start, end)
    
    if len(data.prices) == 0:
        console.print(
            f"[red]✗[/red] {code}: 数据库中无数据，请先运行 "
            f"[cyan]alpha-seeker data fetch-quotes --code {code}[/cyan]"
        )
        raise typer.Exit(code=1)
    
    table = Table(title=f"{code} 策略分析结果 ({len(data.prices)} 条数据)")
    table.add_column("策略", style="cyan")
    table.add_column("信号", style="bold")
    table.add_column("评分", justify="right")
    table.add_column("理由")
    
    signal_color = {
        "buy": "[green]BUY[/green]",
        "sell": "[red]SELL[/red]",
        "hold": "[yellow]HOLD[/yellow]",
    }
    
    for strategy in StrategyRegistry.get_all():
        result: StrategyResult = strategy.analyze(data)
        table.add_row(
            strategy.name,
            signal_color[result.signal.value],
            f"{result.score:.1f}",
            result.reason,
        )
    
    console.print(table)


# 使 StrategyResult 在本模块可见，便于类型检查
from app.strategies.base import StrategyResult  # noqa: E402
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest backend/tests/test_cli.py -v`
Expected: 10 passed

- [ ] **Step 5: 手动端到端验证**

```bash
# 确保数据已抓取
alpha-seeker data fetch-quotes --code 600519 --days 90
alpha-seeker data fetch-quotes --code 000001 --days 90

# 列出所有策略
alpha-seeker strategy list

# 运行策略
alpha-seeker strategy run --code 600519
alpha-seeker strategy run --code 000001
```

Expected: 每个命令都输出格式化的策略分析表格，包含 dual_ma、macd、rsi 三行

- [ ] **Step 6: Commit**

```bash
git add backend/app/cli.py backend/tests/test_cli.py
git commit -m "feat(cli): add strategy list and run commands"
```

---

### Task 23: 实现批量策略运行（全市场排序）

**Files:**
- Modify: `backend/app/cli.py`
- Modify: `backend/tests/test_cli.py`

- [ ] **Step 1: 追加失败测试到 `backend/tests/test_cli.py`**

在文件末尾追加：

```python
def test_strategy_scan_command_exists():
    """strategy scan 命令应该存在"""
    result = runner.invoke(app, ["strategy", "scan", "--help"])
    assert result.exit_code == 0


def test_strategy_scan_ranks_by_avg_score():
    """strategy scan 应按多策略平均分排序并输出 top N"""
    fake_data_high = StockData(
        code="GOOD",
        prices=pd.DataFrame({
            "trade_date": [date_cls(2026, 1, 1) + pd.Timedelta(days=i) for i in range(70)],
            "open": [90 + i * 0.5 for i in range(70)],
            "close": [90 + i * 0.5 for i in range(70)],
            "high": [91 + i * 0.5 for i in range(70)],
            "low": [89 + i * 0.5 for i in range(70)],
            "volume": [1000] * 70,
        }),
    )
    fake_data_low = StockData(
        code="BAD",
        prices=pd.DataFrame({
            "trade_date": [date_cls(2026, 1, 1) + pd.Timedelta(days=i) for i in range(70)],
            "open": [150 - i * 0.5 for i in range(70)],
            "close": [150 - i * 0.5 for i in range(70)],
            "high": [151 - i * 0.5 for i in range(70)],
            "low": [149 - i * 0.5 for i in range(70)],
            "volume": [1000] * 70,
        }),
    )
    
    def fake_load(code, start, end):
        return fake_data_high if code == "GOOD" else fake_data_low
    
    with patch("app.cli.SessionLocal") as mock_session_ctx:
        mock_session = MagicMock()
        mock_session.__enter__.return_value = mock_session
        mock_session.__exit__.return_value = False
        mock_session_ctx.return_value = mock_session
        
        with patch(
            "app.cli.DataStorage.list_stock_codes",
            return_value=["GOOD", "BAD"],
        ), patch(
            "app.cli.DataStorage.load_stock_data",
            side_effect=fake_load,
        ):
            result = runner.invoke(app, ["strategy", "scan", "--top", "2"])
            assert result.exit_code == 0
            # GOOD 应排在 BAD 前面
            good_pos = result.stdout.find("GOOD")
            bad_pos = result.stdout.find("BAD")
            assert good_pos >= 0
            assert bad_pos >= 0
            assert good_pos < bad_pos
```

- [ ] **Step 2: 为 DataStorage 添加 list_stock_codes 方法**

在 `backend/app/data/storage.py` 的 `DataStorage` 类末尾追加：

```python
    def list_stock_codes(self) -> list[str]:
        """返回 stocks 表中所有股票代码"""
        return [s.code for s in self.session.query(Stock).order_by(Stock.code).all()]
```

追加测试到 `backend/tests/test_storage.py`：

```python
def test_list_stock_codes_returns_sorted_codes(db_session):
    storage = DataStorage(db_session)
    storage.upsert_stocks([
        StockInfo(code="000001", name="平安银行"),
        StockInfo(code="600519", name="贵州茅台"),
    ])
    codes = storage.list_stock_codes()
    assert codes == ["000001", "600519"]
```

Run: `pytest backend/tests/test_storage.py -v`
Expected: 10 passed

- [ ] **Step 3: 运行 CLI 测试验证失败**

Run: `pytest backend/tests/test_cli.py::test_strategy_scan_ranks_by_avg_score -v`
Expected: FAIL（`strategy scan` 命令不存在）

- [ ] **Step 4: 在 `backend/app/cli.py` 末尾追加**

```python
@strategy_app.command("scan")
def strategy_scan(
    top: int = typer.Option(10, "--top", "-t", help="返回前 N 名"),
    days: int = typer.Option(90, "--days", "-d", help="使用最近多少天数据"),
    min_days: int = typer.Option(
        60, "--min-days",
        help="股票最少需要的数据条数（少于该值跳过）",
    ),
) -> None:
    """扫描所有已抓取数据的股票，按多策略平均分排序"""
    end = date.today()
    start = end - timedelta(days=days)
    
    with SessionLocal() as session:
        storage = DataStorage(session)
        codes = storage.list_stock_codes()
        
        rows: list[tuple[str, float, dict[str, float]]] = []
        skipped = 0
        for code in codes:
            data = storage.load_stock_data(code, start, end)
            if len(data.prices) < min_days:
                skipped += 1
                continue
            
            scores: dict[str, float] = {}
            for strategy in StrategyRegistry.get_all():
                result = strategy.analyze(data)
                scores[strategy.name] = result.score
            
            avg = sum(scores.values()) / len(scores) if scores else 0.0
            rows.append((code, avg, scores))
    
    rows.sort(key=lambda r: r[1], reverse=True)
    top_rows = rows[:top]
    
    table = Table(title=f"全市场扫描 - Top {top} (跳过 {skipped} 只数据不足的股票)")
    table.add_column("排名", style="cyan", justify="right")
    table.add_column("代码", style="bold")
    table.add_column("平均分", justify="right")
    table.add_column("dual_ma", justify="right")
    table.add_column("macd", justify="right")
    table.add_column("rsi", justify="right")
    
    for rank, (code, avg, scores) in enumerate(top_rows, start=1):
        table.add_row(
            str(rank),
            code,
            f"{avg:.1f}",
            f"{scores.get('dual_ma', 0):.1f}",
            f"{scores.get('macd', 0):.1f}",
            f"{scores.get('rsi', 0):.1f}",
        )
    
    console.print(table)
```

- [ ] **Step 5: 运行测试验证通过**

Run: `pytest backend/tests/test_cli.py -v`
Expected: 12 passed

- [ ] **Step 6: 运行全量测试验证**

Run: `pytest backend/tests -v`
Expected: 全部通过

- [ ] **Step 7: Commit**

```bash
git add backend/app/cli.py backend/app/data/storage.py backend/tests/test_cli.py backend/tests/test_storage.py
git commit -m "feat(cli): add strategy scan for whole-market ranking"
```

---

### Task 24: 编写 README 使用指南

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 `README.md` 为完整使用指南**

```markdown
# Alpha Seeker

A 股智能推荐系统 - MVP 第一阶段

通过 AKShare 抓取 A 股数据，运行量化策略（双均线、MACD、RSI），输出推荐列表。

## 快速开始

### 1. 前置依赖

- Docker 和 Docker Compose
- Python 3.11+

### 2. 初始化

```bash
# 复制环境变量文件
cp .env.example .env

# 启动 PostgreSQL 和 Redis
docker-compose up -d

# 安装 Python 依赖
pip install -e ".[dev]"

# 初始化数据库表
alpha-seeker db init
```

### 3. 抓取数据

```bash
# 抓取 A 股股票列表（约 5000+ 只）
alpha-seeker data fetch-stocks

# 抓取指定股票的日线数据（默认最近 60 天）
alpha-seeker data fetch-quotes --code 600519 --days 90
alpha-seeker data fetch-quotes --code 000001 --days 90
```

### 4. 运行策略

```bash
# 列出所有已注册策略
alpha-seeker strategy list

# 对单只股票运行所有策略
alpha-seeker strategy run --code 600519

# 全市场扫描（需要先抓取多只股票的数据）
alpha-seeker strategy scan --top 10
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `alpha-seeker db init` | 创建数据库表 |
| `alpha-seeker db drop --yes` | 删除所有表（危险） |
| `alpha-seeker data fetch-stocks` | 抓取股票列表 |
| `alpha-seeker data fetch-quotes --code CODE --days N` | 抓取指定股票的日线 |
| `alpha-seeker strategy list` | 列出策略 |
| `alpha-seeker strategy run --code CODE` | 对单只股票运行策略 |
| `alpha-seeker strategy scan --top N` | 全市场扫描排名 |

## 开发

```bash
# 运行测试
pytest backend/tests -v

# 代码检查
ruff check backend/
```

## 文档

- 系统设计：`docs/superpowers/specs/2026-05-12-alpha-seeker-design.md`
- 本阶段计划：`docs/superpowers/plans/2026-05-12-mvp-plan-1-infrastructure-data-strategy.md`

## 下一阶段

第二阶段（MVP Plan 2）将实现：
- 每日推荐生成和存储
- 企业微信/钉钉推送
- FastAPI 后端 API
- Vue 3 前端界面
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README with CLI usage guide"
```

---

## 完成标准

执行完所有任务后，应满足以下条件：

- [ ] `pytest backend/tests -v` 全部通过（约 50+ 个测试）
- [ ] `alpha-seeker db init` 成功创建 3 张表
- [ ] `alpha-seeker data fetch-stocks` 成功抓取并存储数千只股票
- [ ] `alpha-seeker data fetch-quotes --code 600519 --days 90` 成功抓取数十条日线
- [ ] `alpha-seeker strategy run --code 600519` 输出 3 个策略的评分表格
- [ ] `alpha-seeker strategy scan --top 10` 输出全市场 Top 10
- [ ] `ruff check backend/` 无错误

完成本计划后，MVP 的核心数据和策略能力已就绪。进入 MVP Plan 2 实现推荐引擎、通知系统和 Web 界面。

---

**计划文档结束**







