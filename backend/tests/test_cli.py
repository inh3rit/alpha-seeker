from typer.testing import CliRunner

from app.cli import app

runner = CliRunner()


def test_cli_has_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_db_init_command_exists():
    result = runner.invoke(app, ["db", "init", "--help"])
    assert result.exit_code == 0
    assert "创建所有数据库表" in result.stdout


def test_db_drop_command_exists():
    result = runner.invoke(app, ["db", "drop", "--help"])
    assert result.exit_code == 0


def test_data_fetch_stocks_command_exists():
    result = runner.invoke(app, ["data", "fetch-stocks", "--help"])
    assert result.exit_code == 0


def test_data_fetch_quotes_command_exists():
    result = runner.invoke(app, ["data", "fetch-quotes", "--help"])
    assert result.exit_code == 0


def test_strategy_list_command():
    result = runner.invoke(app, ["strategy", "list"])
    assert result.exit_code == 0
    assert "dual_ma" in result.stdout
    assert "macd" in result.stdout
    assert "rsi" in result.stdout


def test_strategy_run_command_exists():
    result = runner.invoke(app, ["strategy", "run", "--help"])
    assert result.exit_code == 0


def test_strategy_scan_command_exists():
    result = runner.invoke(app, ["strategy", "scan", "--help"])
    assert result.exit_code == 0
