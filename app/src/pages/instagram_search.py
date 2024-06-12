from typing import Tuple
from functools import reduce
from re import search

import streamlit as st
import pandas as pd
import httpx
import asyncio

from ..utils import query_instagram, plot_coords, calcualte_fuzzy_coordinates
from ..types import InstagramVenue, Page, HttpStatus
from ..constants import INSTAGRAM_URL, INSTAGRAM_POST_URL, MAPS_TEST_URL

fuzzy_results = []


class InstagramSearch(Page):
    latitude: float
    longitude: float
    cookies: str
    locations: list[InstagramVenue]
    search_option: str

    # Sub-sections
    def location_section(self):
        response = query_instagram(self.latitude, self.longitude, self.cookies)
        if response:
            if response.status_code == HttpStatus.bad_request_400:
                st.text("Cookies invalid. Please check again")

            if response.status_code == HttpStatus.too_many_requests_429:
                st.text("Too many requests for 1 hour. Try again later")

            if response.status_code == HttpStatus.ok_200:
                self.locations = response.message.venues  # type: ignore
                locations_df = pd.DataFrame(self.locations)
                locations_df = self.format_location_table(locations_df)

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
                fuzzy_df = self.format_location_table(fuzzy_df)
                plot_coords(fuzzy_df)
            else:
                st.write("Too few coordinates, no additional queries made.")

    def sidebar(self):
        # TODO: add regex to for check correct format
        self.cookies = st.sidebar.text_input(
            "Please enter your Instagram cookies", type="password"
        )

        st.sidebar.markdown("### Coordinates")
        search_option = st.sidebar.radio("Use Google Maps or GPS?", ["Maps", "GPS"])
        if search_option == "Maps":
            google_maps_url = st.sidebar.text_input("Please enter Google Maps link")
            if google_maps_url == "":
                google_maps_url = MAPS_TEST_URL
            match = search(r"@([-\d.]+),([-\d.]+)", google_maps_url)
            if match:
                self.latitude = float(match.group(1))
                self.longitude = float(match.group(2))

        if search_option == "GPS":
            # NOTE we could get the cookies from a browser extension
            # TODO: add regex to for check correct format
            self.latitude = st.sidebar.text_input("Please enter the latitude", placeholder=52.3676)  # type: ignore
            self.longitude = st.sidebar.text_input("Please enter the longitude", placeholder=4.9041)  # type: ignore

    def write(self):
        self.sidebar()
        st.title("Instagram Search")
        st.text(
            "This section will use the existing Bellingcat repo to search for activity in an area"
        )

        # Return sub-sections
        self.location_section()
        self.fuzzy_locations_section()

    @staticmethod
    def format_location_table(df: pd.DataFrame):
        """Adds clickable Instagram link and rearranges columns

        Args:
            df (pd.DataFrame): locations table

        Returns:
            _type_: formatted table
        """
        # Appends id to root Instagram link
        df["link"] = INSTAGRAM_POST_URL + df["external_id"].astype(str)

        # Rearrange columns
        column_names = list(df.columns.values)
        column_names.insert(1, column_names[-1])
        column_names.pop()
        df = df[column_names]

        def make_df_columns_links(df: pd.DataFrame, col_name: str, link_name: str):
            return st.data_editor(
                df,
                column_config={
                    col_name: st.column_config.LinkColumn(
                        col_name, display_text=link_name
                    )
                },
                hide_index=True,
            )

        # Add link
        return make_df_columns_links(df, "link", "Open Instagram")

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
