import streamlit as st
import pandas as pd

from ..utils import query_instagram, plot_coords, calcualte_fuzzy_locations
from ..types import InstagramVenue, Page, HttpStatus


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
            fuzzy_locations = calcualte_fuzzy_locations(
                self.locations, self.latitude, self.longitude
            )
            fuzzy_locations_df = pd.DataFrame(fuzzy_locations)
            st.write(fuzzy_locations_df)

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
