from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from enum import Enum


class HttpStatus(Enum):
    unknown = 0
    bad_request_400 = 400
    ok_200 = 200
    too_many_requests_429 = 429


class Page(ABC):
    @abstractmethod
    def write(self):
        pass


@dataclass
class InstagramVenue:
    external_id: int
    lat: float
    lng: float
    external_id_source: Optional[str] = None
    name: Optional[str] = None
    # this looks like distance from location (in miles)
    address: Optional[str] = None


@dataclass
class InstagramResponse:
    rank_token: str
    request_id: str
    venues: list[InstagramVenue]
    status: str


@dataclass
class APIResponse:
    status_code: HttpStatus
    message: InstagramResponse | dict
