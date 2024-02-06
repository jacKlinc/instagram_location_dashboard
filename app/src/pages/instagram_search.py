from typing import Tuple
from functools import reduce

import streamlit as st
import pandas as pd
import httpx
import asyncio

from ..utils import query_instagram, plot_coords, calcualte_fuzzy_coordinates
from ..types import InstagramVenue, Page, HttpStatus
from ..constants import INSTAGRAM_URL

fuzzy_results = []


class InstagramSearch(Page):
    latitude: float
    longitude: float
    cookies: str
    locations: list[InstagramVenue]

    # Sub-sections
    def location_section(self):
        response = query_instagram(self.latitude, self.longitude, self.cookies)
        if response:
            if response.status_code == HttpStatus.bad_request_400:
                st.text("Cookies invalid. Please check again")

            if response.status_code == HttpStatus.too_many_requests_429:
                st.text("Too many requests for 1 hour. Try again later")

            if response.status_code == HttpStatus.ok_200:
                self.locations = response.message.venues # type: ignore
                locations_df = pd.DataFrame(self.locations)
                st.write(locations_df)
                plot_coords(locations_df)

    def fuzzy_locations_section(self):
        st.write("## Fuzzy Locations")
        st.write("Fuzzy Locations find even more instagram posts in the area")
        if st.button("Calculate fuzzy locations?"):
            fuzzy_coordinates = calcualte_fuzzy_coordinates(
                self.locations, self.latitude, self.longitude
            )
            if len(fuzzy_coordinates) > 1:
                asyncio.run(self.query_fuzzy_locations(fuzzy_coordinates))
                # flattens list and creates dataframe
                fuzzy_df = pd.DataFrame(reduce(lambda xs, ys: xs + ys, fuzzy_results))
                st.write(fuzzy_df)
                plot_coords(fuzzy_df)
            else:
                st.write("Too few coordinates, no additional queries made.")

    def write(self):
        st.title("Instagram Search")
        st.text(
            "This section will use the existing Bellingcat repo to search for activity in an area"
        )

        # TODO: add regex to for check correct format
        self.cookies = st.text_input(
            "Please enter your Instagram cookies", type="password"
        )

        # NOTE we could get the cookies from a browser extension
        # TODO: add regex to for check correct format
        self.latitude = st.text_input("Please enter the latitude", placeholder=52.3676)  # type: ignore
        self.longitude = st.text_input("Please enter the longitude", placeholder=4.9041)  # type: ignore

        # Return sub-sections
        self.location_section()
        self.fuzzy_locations_section()

    async def query_instagram_async(
        self, client: httpx.AsyncClient, lat: float, lng: float
    ):
        """Async Instagram query

        Args:
            client (httpx.AsyncClient): async client
            lat (float): area latitude
            lng (float): area longitude
        """
        params = {"latitude": lat, "longitude": lng}
        HEADERS = {"Cookie": self.cookies, "Content-Type": "application/json"}
        r = await client.get(INSTAGRAM_URL, params=params, headers=HEADERS)

        fuzzy_results.append(r.json()["venues"])

    async def query_fuzzy_locations(self, locations: list[Tuple[float, float]]):
        """Loops over fuzzy locations and re-queries API

        Args:
            locations (list[Tuple[float, float]]): GPS coordinates
        """
        HEADERS = {"Cookie": self.cookies, "Content-Type": "application/json"}

        async with httpx.AsyncClient(headers=HEADERS) as client:
            tasks = [
                asyncio.create_task(self.query_instagram_async(client, k[0], k[1]))
                for k in locations
            ]
            await asyncio.gather(*tasks)
