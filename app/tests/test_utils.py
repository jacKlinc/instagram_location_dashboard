import os
from dotenv import load_dotenv

from ..src.utils import query_instagram

load_dotenv()

COOKIES = os.getenv("INSTAGRAM_COOKIES")


def test_query_instagram():
    assert True
