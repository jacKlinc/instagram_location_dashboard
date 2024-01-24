from abc import ABC, abstractmethod
from dataclasses import dataclass
from statistics import pstdev
from itertools import product
from typing import Tuple
from enum import Enum


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


class HttpStatus(Enum):
    unknown = 0
    bad_request_400 = 400
    ok_200 = 200
    too_many_requests_429 = 429


@dataclass
class APIResponse:
    status_code: HttpStatus
    message: InstagramResponse | dict


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


def query_instagram(lat: float, lng: float, cookies: str) -> APIResponse | None:
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
        print(response.status_code)
        if response.status_code == HttpStatus.ok_200.value:
            # if cookies are invalid the response code is still 200
            try:
                return APIResponse(
                    HttpStatus.ok_200, InstagramResponse(**response.json())
                )
            except (ValueError, TypeError) as e:
                print(f"No values returned for params: {params}: {e}")
                return APIResponse(HttpStatus.bad_request_400, {})
        if response.status_code == HttpStatus.too_many_requests_429.value:
            print("Too many requests for 1 hour. 200 per hour limit")
            return APIResponse(HttpStatus.too_many_requests_429, response.json())
    except requests.exceptions.ConnectionError as e:
        print(f"Connection failed for params: {params}: {e}")
    except requests.exceptions.Timeout:
        print(f"Connections timed out after {constants.INSTAGRAM_TIMEOUT} seconds")


def calculate_coordinate_delta(coordinate: float, delta: float, std: float) -> float:
    """Calculates additional coordinate based on delta"""
    return coordinate + delta * std


def calcualte_fuzzy_locations(
    venues: list[InstagramVenue], lat: float, lng: float
) -> list[Tuple[float, float]]:
    """Creates more nearby coordinates to query more local data

    Args:
        venues (list[InstagramVenue]): all locations received from previous query
        lat (float): latitude first sent to API
        lng (float): longitude first sent to API

    Returns:
        list[Tuple[float, float]]: list of augmented coordinates
    """
    # calculate distribution for all locations
    std_lat = pstdev([v.lat for v in venues])
    std_lng = pstdev([v.lng for v in venues])

    sigma_range = range(-constants.FUZZY_STD, constants.FUZZY_STD + 1)
    # finds cartesian product of range (-2, 3)
    coordinate_variance = list(product(sigma_range, repeat=2))
    # removes (0,0)
    coordinate_variance_non_zero = list(filter(lambda x: any(x), coordinate_variance))

    return list(
        (
            calculate_coordinate_delta(lat, delta_lat, std_lat),
            calculate_coordinate_delta(lng, delta_lng, std_lng),
        )
        for delta_lat, delta_lng in coordinate_variance_non_zero
    )
