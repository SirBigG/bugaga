import logging

import requests

logger = logging.getLogger(__name__)


class TelegramAPIError(RuntimeError):
    pass


class TelegramClient:
    def __init__(self, token, *, request_timeout=30, session=None):
        if not token:
            raise ValueError("TELEGRAM_TOKEN is required when the bot worker is enabled.")
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.request_timeout = request_timeout
        self.session = session or requests.Session()

    def _call(self, method, payload, *, timeout=None):
        response = self.session.post(
            f"{self.base_url}/{method}",
            json=payload,
            timeout=timeout or self.request_timeout,
        )
        response.raise_for_status()
        body = response.json()
        if not body.get("ok"):
            raise TelegramAPIError(f"Telegram {method} failed: {body.get('description', 'unknown error')}")
        return body.get("result")

    def get_updates(self, *, offset=None, timeout=30):
        payload = {"timeout": timeout, "allowed_updates": ["message"]}
        if offset is not None:
            payload["offset"] = offset
        return self._call("getUpdates", payload, timeout=timeout + 10)

    def send_text(self, chat_id, text, *, parse_mode="HTML"):
        return self._call(
            "sendMessage",
            {
                "chat_id": str(chat_id),
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            },
        )

    def close(self):
        self.session.close()
