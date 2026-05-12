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
