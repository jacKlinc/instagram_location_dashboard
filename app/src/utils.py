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
class InstagramVenues:
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
    venues: list[InstagramVenues]
    status: str


# Functions
def add_custom_css():
    st.markdown(
        """
        <style>
        </style>
        """,
        unsafe_allow_html=True,
    )


def plot_coords(df: pd.DataFrame):
    """Plots GPS coordinates on Streamlit map

    Args:
        df (pd.DataFrame): table of latitudes and longitudes
    Only works where columns named: "lat", "lng"
    """
    # TODO: exception handling
    lat_lng = df[["lat", "lng"]].dropna()
    st.map(lat_lng, longitude="lng")


def query_instagram(params: Any, headers: Any) -> InstagramResponse | None:
    """Queries Instagram location API

    Args:
        params (Any): latitude, longitude and __a
        headers (Any): request header

    Returns:
        InstagramResponse | None:
    """
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


def get_instagram_locations(
    lat: float, lng: float, cookies: str
) -> list[InstagramVenues] | None:
    """Queries Instagram and checks data

    Args:
        lat (float): area latitude
        lng (float): area longitude
        cookies (str): personal Instagram cookies

    Returns:
        list[InstagramVenues] | None: _description_
    """
    params = {"latitude": lat, "longitude": lng}  # __a supports pagination
    headers = {"Cookie": cookies}
    response = query_instagram(params, headers)

    if response:
        return response.venues

    print(f"Got invalid response for {lat}, {lng}")
