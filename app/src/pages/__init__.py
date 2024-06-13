from .instagram_search import InstagramSearch
from .file_upload import FileUpload
from .telegram_number_checker import TelegramNumberChecker
from ..types import Page

from typing import Dict, Type


PAGE_MAP: Dict[str, Type[Page]] = {
    "Instagram Search": InstagramSearch,
    "Telegram Number Checker": TelegramNumberChecker,
    "File Upload": FileUpload,
}

__all__ = ["PAGE_MAP"]
