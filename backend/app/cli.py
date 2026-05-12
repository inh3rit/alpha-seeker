from datetime import date, timedelta

import typer
from loguru import logger
from rich.console import Console
from rich.table import Table

from app.data.fetcher import AKShareFetcher
from app.data.storage import DataStorage
from app.database import Base, SessionLocal, engine
from app.models import DailyQuote, Indicator, Stock  # noqa: F401
from app.strategies import register_builtin_strategies
from app.strategies.base import StrategyRegistry, StrategyResult

app = typer.Typer(help="Alpha Seeker CLI")
db_app = typer.Typer(help="数据库操作")
data_app = typer.Typer(help="数据管理")
strategy_app = typer.Typer(help="策略管理")
app.add_typer(db_app, name="db")
app.add_typer(data_app, name="data")
app.add_typer(strategy_app, name="strategy")

console = Console()

__version__ = "0.1.0"

register_builtin_strategies()


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


# --- DB commands ---

@db_app.command("init")
def db_init() -> None:
    """创建所有数据库表"""
    logger.info("创建数据库表...")
    Base.metadata.create_all(engine)
    console.print("[green]✓[/green] 数据库表创建完成")


@db_app.command("drop")
def db_drop(
    confirm: bool = typer.Option(False, "--yes", "-y", help="跳过确认提示"),
) -> None:
    """删除所有数据库表（危险操作）"""
    if not confirm:
        typer.confirm("确定要删除所有表吗？此操作不可逆！", abort=True)
    logger.warning("删除所有数据库表...")
    Base.metadata.drop_all(engine)
    console.print("[yellow]✓[/yellow] 所有表已删除")


# --- Data commands ---

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
        f"[green]✓[/green] {code}: 抓取 {len(quotes)} 条行情 （{start} ~ {end}）"
    )


# --- Strategy commands ---

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


@strategy_app.command("scan")
def strategy_scan(
    top: int = typer.Option(10, "--top", "-t", help="返回前 N 名"),
    days: int = typer.Option(90, "--days", "-d", help="使用最近多少天数据"),
    min_days: int = typer.Option(60, "--min-days", help="股票最少需要的数据条数"),
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
            str(rank), code, f"{avg:.1f}",
            f"{scores.get('dual_ma', 0):.1f}",
            f"{scores.get('macd', 0):.1f}",
            f"{scores.get('rsi', 0):.1f}",
        )

    console.print(table)


if __name__ == "__main__":
    app()
