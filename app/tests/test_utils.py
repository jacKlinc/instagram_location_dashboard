import os
from dotenv import load_dotenv

from ..src.utils import query_instagram

load_dotenv()


def test_query_instagram():
    """Tests if cookies work"""
    # NOTE why does this return values when 0,0  is in the middle of the atlantic?
    response_good = query_instagram(0, 0, os.getenv("INSTAGRAM_COOKIES"))
    response_bad = query_instagram(0, 0, "this is a bad cookie")
    assert (response_good is not None) & (response_bad is None)
