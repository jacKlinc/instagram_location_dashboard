from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import streamlit as st
import pandas as pd
import requests

from . import constants


# Classes
class Page(ABC):
    @abstractmethod
    def write(self):
        pass


@dataclass
class InstagramVenue:
    external_id: int
    external_id_source: str
    name: str
    address: str  # this looks like distance from location (in miles)
    lat: float
    lng: float


@dataclass
class InstagramResponse:
    rank_token: str
    request_id: str
    venues: list[InstagramVenue]
    status: str


# Functions
def plot_coords(df: pd.DataFrame):
    """Plots GPS coordinates on Streamlit map

    Args:
        df (pd.DataFrame): table of latitudes and longitudes
    Only works where columns named: "lat", "lng"
    """
    # TODO: exception handling
    lat_lng = df[["lat", "lng"]].dropna()
    st.map(lat_lng, longitude="lng")


def query_instagram(lat: float, lng: float, cookies: str) -> InstagramResponse | None:
    """Queries Instagram location API

    Args:
        lat (float): area latitude
        lng (float): area longitude
        cookies (str): personal Instagram cookies

    Returns:
        InstagramResponse | None:
    """
    params = {"latitude": lat, "longitude": lng}  # __a supports pagination
    headers = {"Cookie": cookies}
    try:
        response = requests.get(
            constants.INSTAGRAM_URL,
            params=params,
            headers=headers,
            timeout=constants.INSTAGRAM_TIMEOUT,
        )
        try:
            return InstagramResponse(**response.json())
        except (ValueError, TypeError) as e:
            print(f"No values returned for params: {params}: {e}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection failed for params: {params}: {e}")
    except requests.exceptions.Timeout:
        print(f"Connections timed out after {constants.INSTAGRAM_TIMEOUT} seconds")
