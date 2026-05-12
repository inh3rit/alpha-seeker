import httpx
from loguru import logger

from app.config import settings
from app.models.recommendation import Recommendation


class NotificationService:
    """通知服务：通过 Webhook 推送消息到企业微信/钉钉"""

    def __init__(self, webhook_url: str | None = None) -> None:
        self.webhook_url = webhook_url or settings.webhook_url

    def format_daily_report(self, recommendations: list[Recommendation], date_str: str) -> str:
        """格式化每日推荐为 Markdown"""
        if not recommendations:
            return f"【Alpha Seeker】{date_str}\n\n今日无推荐"

        lines = [f"【Alpha Seeker 每日推荐】{date_str}\n"]
        lines.append("**今日精选 Top 5：**\n")

        for i, rec in enumerate(recommendations[:5], 1):
            action_text = {"buy": "买入", "hold": "观察", "sell": "卖出"}.get(
                rec.suggested_action, rec.suggested_action
            )
            risk_text = {"low": "低", "medium": "中", "high": "高"}.get(
                rec.risk_level or "", rec.risk_level or ""
            )
            lines.append(
                f"{i}. **{rec.code}** 评分:{rec.score}\n"
                f"   建议：{action_text} | 风险：{risk_text}\n"
                f"   理由：{rec.reason or '综合评分较高'}\n"
            )

        return "\n".join(lines)

    def send_webhook(self, content: str) -> bool:
        """发送 Webhook 消息"""
        if not self.webhook_url:
            logger.warning("未配置 Webhook URL，跳过通知推送")
            return False

        # 企业微信格式
        payload = {
            "msgtype": "markdown",
            "markdown": {"content": content},
        }

        try:
            response = httpx.post(self.webhook_url, json=payload, timeout=10.0)
            if response.status_code == 200:
                logger.info("通知推送成功")
                return True
            else:
                logger.error(f"通知推送失败: {response.status_code} {response.text}")
                return False
        except httpx.RequestError as exc:
            logger.error(f"通知推送异常: {exc}")
            return False

    def send_daily_report(self, recommendations: list[Recommendation], date_str: str) -> bool:
        """发送每日推荐报告"""
        content = self.format_daily_report(recommendations, date_str)
        return self.send_webhook(content)
