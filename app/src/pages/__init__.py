from .instagram_search import InstagramSearch
from .file_upload import FileUpload
from .octosuite import Octosuite
from ..types import Page

from typing import Dict, Type


PAGE_MAP: Dict[str, Type[Page]] = {
    "Instagram Search": InstagramSearch,
    "File Upload": FileUpload,
    "Octosuite": Octosuite,
}

__all__ = ["PAGE_MAP"]
